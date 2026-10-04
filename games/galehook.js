(function () {
  var KEY = "pixelsprout-galehook-best";
  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 360, H = 640, dpr = 1;
    var mode = "title";
    var score = 0, best = 0, combo = 0, hooks = 0;
    var angle = -0.9, swing = 1.15, dir = 1, wind = 0, windT = 4;
    var ax = 180, ay = 150, arm = 118;
    var flying = null;
    var posts = [];
    var flash = 0, t = 0, perfect = 0;
    try { best = +localStorage.getItem(KEY) || 0; } catch (e) {}

    function resize() {
      var r = canvas.parentElement.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(280, r.width);
      H = Math.max(420, r.height);
      canvas.width = Math.floor(W * dpr);
      canvas.height = Math.floor(H * dpr);
      canvas.style.width = W + "px";
      canvas.style.height = H + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function makePosts() {
      posts = [];
      var x = W * 0.34;
      for (var i = 0; i < 8; i++) {
        x += 92 + (i % 3) * 18;
        posts.push({ x: x, y: 168 + (i % 4) * 22, hit: false });
      }
    }

    function reset() {
      score = 0; combo = 0; hooks = 0; perfect = 0; flash = 0;
      angle = -0.95; dir = 1; wind = 0; windT = 3.2; flying = null;
      makePosts();
      ax = W * 0.28; ay = 150; arm = Math.min(130, W * 0.34);
      mode = "play";
    }

    function mothPos() {
      return { x: ax + Math.sin(angle) * arm, y: ay + Math.cos(angle) * arm };
    }

    function release() {
      if (mode === "title" || mode === "over") { reset(); return; }
      if (flying) return;
      var p = mothPos();
      var speed = 260 + combo * 8;
      flying = {
        x: p.x, y: p.y,
        vx: Math.cos(angle) * dir * speed * 0.55 + wind * 40,
        vy: -Math.abs(Math.sin(angle)) * speed * 0.15 - 40
      };
      var center = Math.abs(angle) < 0.22;
      perfect = center ? 1 : 0;
    }

    function nextHook() {
      for (var i = 0; i < posts.length; i++) if (!posts[i].hit) return posts[i];
      return null;
    }

    function latch(post, good) {
      post.hit = true;
      hooks += 1;
      combo = good ? combo + 1 : 1;
      score += 10 * combo + (good ? 15 : 0);
      flash = good ? 1 : 0.35;
      ax = post.x; ay = post.y; angle = -0.85; dir = 1;
      flying = null;
      if (hooks % 4 === 0) wind = (Math.random() * 2 - 1) * (0.6 + hooks * 0.04);
      if (!nextHook()) {
        makePosts();
        posts.forEach(function (p) { p.x += ax - W * 0.2; });
      }
    }

    function fail() {
      mode = "over";
      flying = null;
      if (score > best) {
        best = score;
        try { localStorage.setItem(KEY, String(best)); } catch (e) {}
      }
    }

    function step(dt) {
      t += dt;
      windT -= dt;
      if (windT <= 0) {
        wind = (Math.random() * 2 - 1) * (0.35 + hooks * 0.03);
        windT = 2.4 + Math.random() * 2;
      }
      if (flash > 0) flash -= dt;
      if (mode !== "play") return;
      if (!flying) {
        angle += dir * swing * dt * (1 + wind * 0.25);
        if (angle > 1.15) { angle = 1.15; dir = -1; }
        if (angle < -1.15) { angle = -1.15; dir = 1; }
        return;
      }
      flying.vy += 520 * dt;
      flying.vx += wind * 30 * dt;
      flying.x += flying.vx * dt;
      flying.y += flying.vy * dt;
      var post = nextHook();
      if (post) {
        var dx = flying.x - post.x, dy = flying.y - post.y;
        if (dx * dx + dy * dy < 34 * 34 && flying.vy > -20) latch(post, perfect);
      }
      if (flying && (flying.y > H - 40 || flying.x < -40 || flying.x > W + 80)) fail();
    }

    function drawMoth(x, y) {
      ctx.save();
      ctx.translate(x, y);
      ctx.fillStyle = "#d7b06a";
      ctx.beginPath(); ctx.moveTo(-22, 0); ctx.lineTo(-4, -6); ctx.lineTo(-4, 6); ctx.fill();
      ctx.beginPath(); ctx.moveTo(22, 0); ctx.lineTo(4, -6); ctx.lineTo(4, 6); ctx.fill();
      ctx.fillStyle = "#5c3a28";
      ctx.beginPath(); ctx.arc(0, 0, 5, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }

    function draw() {
      var g = ctx.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "#142033");
      g.addColorStop(1, "#1c2a22");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#e8d7a8";
      ctx.beginPath(); ctx.arc(W - 70, 64, 28, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#142033";
      ctx.beginPath(); ctx.arc(W - 56, 56, 24, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#243028";
      ctx.fillRect(0, H - 70, W, 70);
      posts.forEach(function (p) {
        if (p.x < -20 || p.x > W + 20) return;
        ctx.strokeStyle = "#6b4a32";
        ctx.lineWidth = 5;
        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x, H - 70); ctx.stroke();
        ctx.fillStyle = p.hit ? "#6a5030" : "#e08a3c";
        ctx.beginPath(); ctx.arc(p.x, p.y, 12, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ffd98a";
        ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, Math.PI * 2); ctx.fill();
      });
      if (mode === "play" && !flying) {
        var p = mothPos();
        ctx.strokeStyle = perfectWindow() ? "#b7e38a" : "#6d9a62";
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(p.x, p.y); ctx.stroke();
        drawMoth(p.x, p.y);
      } else if (flying) drawMoth(flying.x, flying.y);
      ctx.fillStyle = "#f4e7c4";
      ctx.font = "600 20px sans-serif";
      ctx.fillText(String(score), 16, 32);
      ctx.font = "14px sans-serif";
      ctx.fillStyle = "#cbb892";
      ctx.fillText("best " + best + (combo > 1 ? "   x" + combo : "") + (wind ? "   wind" : ""), 16, 52);
      if (flash > 0) {
        ctx.fillStyle = "rgba(255,220,140," + flash + ")";
        ctx.fillRect(0, 0, W, H);
      }
      if (mode !== "play") {
        ctx.fillStyle = "rgba(8,10,16,0.72)";
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = "#ffd978";
        ctx.font = "700 36px sans-serif";
        ctx.fillText("GALEHOOK", W / 2 - 108, H / 2 - 36);
        ctx.fillStyle = "#f4e7c4";
        ctx.font = "16px sans-serif";
        var msg = mode === "title" ? "Tap or press Space to swing off" : "Score " + score + "   Best " + best;
        ctx.fillText(msg, W / 2 - ctx.measureText(msg).width / 2, H / 2 + 4);
        ctx.fillText("Release near the bottom of the arc", W / 2 - 118, H / 2 + 32);
      }
    }

    function perfectWindow() { return Math.abs(angle) < 0.22; }

    var last = 0;
    function frame(now) {
      if (!last) last = now;
      var dt = Math.min(0.033, (now - last) / 1000);
      last = now;
      step(dt);
      draw();
      requestAnimationFrame(frame);
    }

    canvas.addEventListener("pointerdown", function (e) { e.preventDefault(); release(); });
    window.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter" || e.key === "ArrowUp") { e.preventDefault(); release(); }
    });
    window.addEventListener("resize", resize);
    resize();
    requestAnimationFrame(frame);
  }
  window.Galehook = { mount: mount };
})();
