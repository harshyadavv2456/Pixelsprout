(function () {
  var SIZES = [11, 17, 25, 35, 47, 60];
  var COLORS = ["#b7e7ff", "#7fd0f2", "#3aa7d8", "#1f7ea8", "#f2d27a", "#f7f1c8"];
  var NAMES = ["Bead", "Pearl", "Orb", "Lantern", "Moon", "Tide"];

  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 480, H = 640;
    var state = "title";
    var rack = 240;
    var drops = [];
    var score = 0;
    var best = 0;
    var lives = 3;
    var combo = 1;
    var spawn = 0;
    var flash = 0;
    var pointer = false;
    var keys = {};
    try { best = +localStorage.getItem("dewrack-best") || 0; } catch (e) {}

    function saveBest() {
      if (score > best) {
        best = score;
        try { localStorage.setItem("dewrack-best", String(best)); } catch (e) {}
      }
    }
    function reset() {
      drops = [];
      score = 0;
      lives = 3;
      combo = 1;
      spawn = 0.35;
      rack = 240;
      flash = 0;
      state = "play";
    }
    function addDrop(x, y, s, v) {
      drops.push({ x: x, y: y, vx: (Math.random() - 0.5) * 20, vy: v, s: s, settled: false });
    }
    function merge() {
      var hit = false;
      for (var i = 0; i < drops.length; i++) {
        for (var j = i + 1; j < drops.length; j++) {
          var a = drops[i], b = drops[j];
          if (a.s !== b.s || a.s >= 5) continue;
          var dx = a.x - b.x, dy = a.y - b.y;
          var need = SIZES[a.s] + SIZES[b.s] - 2;
          if (dx * dx + dy * dy < need * need) {
            var ns = a.s + 1;
            var nx = (a.x + b.x) / 2;
            var ny = (a.y + b.y) / 2;
            drops.splice(j, 1);
            drops.splice(i, 1);
            addDrop(nx, ny, ns, -40);
            drops[drops.length - 1].settled = ny > 470;
            score += (ns + 1) * 25 * combo;
            combo = Math.min(8, combo + 1);
            flash = 0.25;
            hit = true;
            return true;
          }
        }
      }
      return hit;
    }
    function step(dt) {
      var speed = keys.left || keys.a ? -280 : keys.right || keys.d ? 280 : 0;
      if (pointerX !== null) rack += (pointerX - rack) * Math.min(1, dt * 8);
      rack = Math.max(78, Math.min(402, rack + speed * dt));
      spawn -= dt;
      if (spawn <= 0) {
        addDrop(50 + Math.random() * 380, -16, Math.random() < 0.78 ? 0 : 1, 110 + Math.random() * 50);
        spawn = Math.max(0.55, 1.35 - score / 4000);
      }
      var rackTop = 548;
      for (var i = drops.length - 1; i >= 0; i--) {
        var d = drops[i];
        d.vy += 420 * dt;
        d.x += d.vx * dt;
        d.y += d.vy * dt;
        d.vx *= 0.99;
        if (d.x < SIZES[d.s]) { d.x = SIZES[d.s]; d.vx *= -0.4; }
        if (d.x > W - SIZES[d.s]) { d.x = W - SIZES[d.s]; d.vx *= -0.4; }
        var onRack = d.y + SIZES[d.s] >= rackTop && d.y < rackTop + 28 && Math.abs(d.x - rack) < 92;
        if (!d.settled && onRack && d.vy > 0) {
          d.settled = true;
          d.y = rackTop - SIZES[d.s];
          d.vy = 0;
          score += 2;
        }
        if (d.settled) {
          d.y = rackTop - SIZES[d.s];
          d.vy = 0;
          var pull = (rack - d.x) * 0.4;
          d.vx += pull * dt;
          if (Math.abs(d.x - rack) > 96) {
            d.settled = false;
            d.vy = 40;
          }
        }
        if (d.y > H + 20) {
          drops.splice(i, 1);
          lives -= 1;
          combo = 1;
          if (lives <= 0) { state = "over"; saveBest(); }
        }
      }
      for (var n = 0; n < 4 && merge(); n++) {}
      if (combo > 1) combo = Math.max(1, combo - dt * 0.35);
      flash = Math.max(0, flash - dt);
    }
    var pointerX = null;
    function drawDrop(d) {
      var r = SIZES[d.s];
      var g = ctx.createRadialGradient(d.x - r * 0.3, d.y - r * 0.35, r * 0.1, d.x, d.y, r);
      g.addColorStop(0, "#ffffff");
      g.addColorStop(0.35, COLORS[d.s]);
      g.addColorStop(1, "#12384c");
      ctx.beginPath();
      ctx.fillStyle = g;
      ctx.ellipse(d.x, d.y + r * 0.12, r * 0.82, r, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(d.x, d.y - r * 1.15);
      ctx.quadraticCurveTo(d.x + r * 0.7, d.y - r * 0.1, d.x, d.y + r * 0.1);
      ctx.quadraticCurveTo(d.x - r * 0.7, d.y - r * 0.1, d.x, d.y - r * 1.15);
      ctx.fill();
    }
    function frame(ts) {
      if (!frame.last) frame.last = ts;
      var dt = Math.min(0.033, (ts - frame.last) / 1000);
      frame.last = ts;
      if (state === "play") step(dt);
      ctx.clearRect(0, 0, W, H);
      var sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#16324a");
      sky.addColorStop(1, "#0c1c16");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "rgba(230,240,255,0.85)";
      ctx.beginPath();
      ctx.arc(390, 78, 28, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#2f6b45";
      ctx.beginPath();
      ctx.ellipse(rack, 568, 108, 26, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#8a5a34";
      ctx.fillRect(rack - 96, 558, 192, 18);
      ctx.fillStyle = "#c9894e";
      ctx.fillRect(rack - 88, 562, 176, 8);
      drops.forEach(drawDrop);
      ctx.fillStyle = "#e8f7ff";
      ctx.font = "600 18px system-ui, sans-serif";
      ctx.fillText("Score " + score, 18, 32);
      ctx.fillText("Best " + best, 18, 54);
      ctx.fillText("Lives " + lives, 360, 32);
      if (flash > 0) {
        ctx.fillStyle = "rgba(255,255,255," + (flash * 0.35) + ")";
        ctx.fillRect(0, 0, W, H);
      }
      if (state !== "play") {
        ctx.fillStyle = "rgba(6,12,18,0.62)";
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = "#f4fbff";
        ctx.textAlign = "center";
        ctx.font = "700 42px system-ui, sans-serif";
        ctx.fillText(state === "title" ? "Dewrack" : "Rack overflow", W / 2, 250);
        ctx.font = "18px system-ui, sans-serif";
        ctx.fillStyle = "#c9e7f5";
        var line = state === "title"
          ? "Catch dew. Same sizes fuse. Do not let a drop fall."
          : "Score " + score + "  ·  Best " + best;
        ctx.fillText(line, W / 2, 292);
        ctx.fillStyle = "#f2d27a";
        ctx.font = "600 20px system-ui, sans-serif";
        ctx.fillText("Tap, click, or press Space", W / 2, 350);
        ctx.textAlign = "left";
      }
      requestAnimationFrame(frame);
    }
    function aim(e) {
      var rect = canvas.getBoundingClientRect();
      pointerX = (e.clientX - rect.left) / rect.width * W;
    }
    canvas.addEventListener("pointerdown", function (e) {
      pointer = true;
      aim(e);
      if (state !== "play") reset();
    });
    canvas.addEventListener("pointermove", function (e) { if (pointer) aim(e); });
    canvas.addEventListener("pointerup", function () { pointer = false; pointerX = null; });
    canvas.addEventListener("pointerleave", function () { pointer = false; pointerX = null; });
    window.addEventListener("keydown", function (e) {
      var k = e.key.toLowerCase();
      if (k === "arrowleft" || k === "a") keys.left = keys.a = true;
      if (k === "arrowright" || k === "d") keys.right = keys.d = true;
      if (k === " " || k === "enter") {
        e.preventDefault();
        if (state !== "play") reset();
      }
    });
    window.addEventListener("keyup", function (e) {
      var k = e.key.toLowerCase();
      if (k === "arrowleft" || k === "a") keys.left = keys.a = false;
      if (k === "arrowright" || k === "d") keys.right = keys.d = false;
    });
    canvas.width = W;
    canvas.height = H;
    requestAnimationFrame(frame);
  }
  window.Dewrack = { mount: mount };
})();
