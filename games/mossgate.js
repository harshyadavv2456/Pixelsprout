(function () {
  var KEY = "pixelsprout-mossgate-best";
  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 480, H = 720, mode = "title", lane = 1, size = 2, bonus = 0, dist = 0, speed = 3.2;
    var best = Number(localStorage.getItem(KEY) || 0);
    var gates = [], spawn = 0, flash = "";
    function resize() {
      var r = canvas.getBoundingClientRect();
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      W = canvas.width = Math.max(280, Math.floor(r.width * dpr));
      H = canvas.height = Math.max(420, Math.floor(r.height * dpr));
    }
    resize();
    window.addEventListener("resize", resize);
    function score() { return Math.floor(dist) + bonus; }
    function save() { if (score() > best) { best = score(); localStorage.setItem(KEY, String(best)); } }
    function reset() {
      lane = 1; size = 2; bonus = 0; dist = 0; speed = 3.2; gates = []; spawn = 36; flash = ""; mode = "play";
    }
    function spawnGate() {
      var roll = Math.random(), type, val;
      if (roll < 0.32) { type = "add"; val = 1 + Math.floor(Math.random() * 3); }
      else if (roll < 0.48) { type = "mul"; val = 2; }
      else if (roll < 0.74) { type = "dew"; val = Math.max(1, size - 1 + Math.floor(Math.random() * 3)); }
      else { type = "thorn"; val = size + Math.floor(Math.random() * 3); }
      gates.push({ lane: Math.floor(Math.random() * 3), y: -70, type: type, val: val, hit: false });
    }
    function end() { mode = "over"; save(); }
    function take(g) {
      if (g.hit) return;
      g.hit = true;
      if (g.type === "thorn") {
        if (g.val > size) { flash = "Thorn too tall"; end(); return; }
        size += 1; bonus += g.val * 8; flash = "Smashed " + g.val;
      } else if (g.type === "dew") {
        if (g.val > size) { flash = "Dew too heavy"; end(); return; }
        size += 1; bonus += g.val * 12; flash = "Drank " + g.val;
      } else if (g.type === "mul") {
        size = Math.min(99, size * g.val); bonus += 30; flash = "x" + g.val;
      } else {
        size = Math.min(99, size + g.val); bonus += g.val * 10; flash = "+" + g.val;
      }
    }
    function step() {
      if (mode !== "play") return;
      dist += speed * 0.18;
      speed = Math.min(9, 3.2 + dist / 380);
      spawn -= 1;
      if (spawn <= 0) { spawnGate(); spawn = Math.max(26, 78 - dist / 28); }
      var py = H * 0.74;
      for (var i = 0; i < gates.length; i++) {
        var g = gates[i];
        g.y += speed * (H / 280);
        if (!g.hit && g.lane === lane && Math.abs(g.y - py) < H * 0.045) take(g);
      }
      gates = gates.filter(function (g) { return g.y < H + 90; });
    }
    function laneX(i) { return W * (0.22 + i * 0.28); }
    function round(x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
    }
    function draw() {
      ctx.fillStyle = "#10241c";
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#1c4630";
      ctx.fillRect(0, H * 0.82, W, H);
      for (var i = 0; i < 3; i++) {
        ctx.strokeStyle = i === lane ? "#b6e37a" : "#2f6b42";
        ctx.lineWidth = i === lane ? 8 : 4;
        ctx.beginPath();
        ctx.moveTo(laneX(i), 0);
        ctx.lineTo(laneX(i), H);
        ctx.stroke();
      }
      gates.forEach(function (g) {
        var x = laneX(g.lane);
        ctx.fillStyle = g.type === "thorn" ? "#c4553a" : g.type === "mul" ? "#e6c15a" : g.type === "add" ? "#7dce6a" : "#7ec8e3";
        round(x - W * 0.09, g.y - 26, W * 0.18, 52, 12);
        ctx.fill();
        ctx.fillStyle = "#10241c";
        ctx.font = "bold " + Math.floor(W * 0.055) + "px sans-serif";
        ctx.textAlign = "center";
        var label = g.type === "add" ? "+" + g.val : g.type === "mul" ? "x" + g.val : String(g.val);
        ctx.fillText(label, x, g.y + 8);
      });
      var px = laneX(lane), py = H * 0.74;
      ctx.fillStyle = "#3c2a1c";
      round(px - 32, py + 6, 64, 26, 8);
      ctx.fill();
      ctx.fillStyle = "#5aaa48";
      ctx.beginPath();
      ctx.ellipse(px, py - 16, 26, 34, 0, 0, 6.3);
      ctx.fill();
      ctx.fillStyle = "#d8f0a0";
      ctx.beginPath();
      ctx.ellipse(px + 16, py - 34, 16, 22, 0.4, 0, 6.3);
      ctx.fill();
      ctx.fillStyle = "#f2e6b0";
      ctx.font = "bold " + Math.floor(W * 0.04) + "px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(String(size), px, py + 26);
      ctx.fillStyle = "#e8f6c8";
      ctx.font = "bold " + Math.floor(W * 0.05) + "px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText("Score " + score(), 16, 40);
      ctx.textAlign = "right";
      ctx.fillText("Best " + best, W - 16, 40);
      ctx.textAlign = "center";
      ctx.font = Math.floor(W * 0.04) + "px sans-serif";
      ctx.fillText(flash, W / 2, 78);
      if (mode !== "play") {
        ctx.fillStyle = "rgba(8,18,14,0.66)";
        ctx.fillRect(0, H * 0.3, W, H * 0.34);
        ctx.fillStyle = "#e7f6b8";
        ctx.font = "bold " + Math.floor(W * 0.09) + "px sans-serif";
        ctx.fillText(mode === "title" ? "MOSSGATE" : "Run over", W / 2, H * 0.42);
        ctx.fillStyle = "#d5e8c4";
        ctx.font = Math.floor(W * 0.04) + "px sans-serif";
        ctx.fillText(mode === "title" ? "Grow through gates. Dodge tall thorns." : "Score " + score(), W / 2, H * 0.49);
        ctx.fillText(mode === "title" ? "Tap a side, or press Enter" : "Tap or Enter to grow again", W / 2, H * 0.55);
      }
    }
    function steer(dir) {
      if (mode !== "play") { reset(); return; }
      lane = Math.max(0, Math.min(2, lane + dir));
    }
    canvas.addEventListener("pointerdown", function (e) {
      var r = canvas.getBoundingClientRect();
      if (mode !== "play") { reset(); return; }
      steer((e.clientX - r.left) < r.width / 2 ? -1 : 1);
    });
    window.addEventListener("keydown", function (e) {
      var k = e.key;
      if (k === "ArrowLeft" || k === "a" || k === "A") { e.preventDefault(); steer(-1); }
      else if (k === "ArrowRight" || k === "d" || k === "D") { e.preventDefault(); steer(1); }
      else if (k === "Enter" || k === " ") { e.preventDefault(); if (mode !== "play") reset(); }
    });
    function loop() { step(); draw(); requestAnimationFrame(loop); }
    loop();
  }
  window.Mossgate = { mount: mount };
})();
