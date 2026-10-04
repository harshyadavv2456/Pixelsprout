/* Lumen Dock — Pixel Sprout original. Timing stack on a night river. */
(function () {
  var KEY = "lumen-dock-best";
  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 360, H = 560;
    var state = "title";
    var score = 0, best = 0, combo = 0, cam = 0, t = 0, speed = 1.4;
    var mover, stack, particles, flash;
    try { best = +localStorage.getItem(KEY) || 0; } catch (e) {}
    function resize() {
      var r = canvas.parentElement.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(2, r.width) * dpr;
      canvas.height = Math.max(2, r.height) * dpr;
      ctx.setTransform(canvas.width / W, 0, 0, canvas.height / H, 0, 0);
    }
    function reset() {
      score = 0; combo = 0; cam = 0; speed = 1.45; flash = 0;
      stack = [{ x: 90, y: 470, w: 180, hue: 0 }];
      mover = { x: 20, y: 400, w: 180, dir: 1, hue: 1 };
      particles = [];
    }
    function drop() {
      if (state === "title") { state = "play"; reset(); return; }
      if (state === "over") { state = "play"; reset(); return; }
      var prev = stack[stack.length - 1];
      var left = Math.max(mover.x, prev.x);
      var right = Math.min(mover.x + mover.w, prev.x + prev.w);
      var w = right - left;
      if (w < 12) { state = "over"; save(); return; }
      var perfect = Math.abs(mover.x - prev.x) < 7;
      if (perfect) { w = prev.w; left = prev.x; combo += 1; flash = 8; burst(left + w / 2, mover.y); }
      else combo = 0;
      var gain = Math.round(w / 4) * (1 + combo);
      score += gain;
      stack.push({ x: left, y: prev.y - 28, w: w, hue: (prev.hue + 1) % 3 });
      mover.w = w;
      mover.y = prev.y - 56;
      mover.hue = (mover.hue + 1) % 3;
      speed = Math.min(4.2, speed + 0.06);
      if (score > best) best = score;
    }
    function save() { try { localStorage.setItem(KEY, String(best)); } catch (e) {} }
    function burst(x, y) {
      for (var i = 0; i < 10; i++) particles.push({ x: x, y: y, vx: (Math.random() - 0.5) * 3, vy: -Math.random() * 2.4, life: 24 });
    }
    function tick() {
      t += 1;
      if (state === "play") {
        mover.x += mover.dir * speed;
        if (mover.x < 8) { mover.x = 8; mover.dir = 1; }
        if (mover.x + mover.w > W - 8) { mover.x = W - 8 - mover.w; mover.dir = -1; }
        var target = Math.max(0, (stack.length - 4) * 28);
        cam += (target - cam) * 0.08;
      }
      if (flash > 0) flash -= 1;
      particles.forEach(function (p) { p.x += p.vx; p.y += p.vy; p.life -= 1; });
      particles = particles.filter(function (p) { return p.life > 0; });
    }
    function lantern(x, y, w, hue, sway) {
      var cols = ["#f2a23a", "#e36b62", "#f0d27a"];
      var body = cols[hue % 3];
      ctx.fillStyle = body;
      round(x, y - 22, w, 26, 8);
      ctx.fill();
      ctx.fillStyle = "rgba(255,236,190,0.85)";
      round(x + w * 0.22, y - 16, w * 0.56, 14, 5);
      ctx.fill();
      ctx.fillStyle = "#7a3a22";
      ctx.fillRect(x + w * 0.35, y - 30, w * 0.3, 8);
      ctx.strokeStyle = "#5a321c";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(x + w / 2, y - 30);
      ctx.lineTo(x + w / 2 + (sway || 0), y - 40);
      ctx.stroke();
    }
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
      ctx.fillStyle = "#12142a";
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#f6e2b4";
      for (var i = 0; i < 28; i++) {
        var sx = (i * 47) % W, sy = (i * 29) % 180;
        ctx.fillRect(sx, sy, 2, 2);
      }
      ctx.fillStyle = "#f3c98a";
      ctx.beginPath();
      ctx.arc(300, 54, 22, 0, 6.3);
      ctx.fill();
      ctx.fillStyle = "#0e2a44";
      ctx.fillRect(0, 500, W, 60);
      ctx.save();
      ctx.translate(0, cam);
      ctx.fillStyle = "#6a4328";
      ctx.fillRect(40, 498, 280, 16);
      stack.forEach(function (b, i) { lantern(b.x, b.y, b.w, b.hue, Math.sin(t / 12 + i) * 2); });
      if (state === "play") lantern(mover.x, mover.y, mover.w, mover.hue, Math.sin(t / 6) * 3);
      particles.forEach(function (p) { ctx.fillStyle = "rgba(255,220,140," + (p.life / 24) + ")"; ctx.fillRect(p.x, p.y, 3, 3); });
      ctx.restore();
      ctx.fillStyle = "#fff6e4";
      ctx.font = "700 18px Inter, sans-serif";
      ctx.fillText(String(score), 16, 28);
      ctx.font = "600 12px Inter, sans-serif";
      ctx.fillStyle = "#f0c98a";
      ctx.fillText("best " + best, 16, 46);
      if (combo > 1) { ctx.fillStyle = "#ffe08a"; ctx.fillText("steady x" + combo, 220, 28); }
      if (flash) { ctx.fillStyle = "rgba(255,220,150,0.18)"; ctx.fillRect(0, 0, W, H); }
      if (state !== "play") {
        ctx.fillStyle = "rgba(8,10,22,0.62)";
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = "#fff4dc";
        ctx.font = "800 32px Inter, sans-serif";
        ctx.fillText("Lumen Dock", 78, 230);
        ctx.font = "600 15px Inter, sans-serif";
        ctx.fillStyle = "#f0c98a";
        var line = state === "title" ? "Tap or press Space to drop" : "The stack tipped. Score " + score;
        ctx.fillText(line, 62, 268);
        ctx.fillStyle = "#f2a23a";
        round(108, 300, 144, 40, 12);
        ctx.fill();
        ctx.fillStyle = "#2a160c";
        ctx.font = "800 16px Inter, sans-serif";
        ctx.fillText(state === "title" ? "Play" : "Retry", 156, 326);
      }
    }
    function loop() { tick(); draw(); requestAnimationFrame(loop); }
    function press(e) { if (e && e.preventDefault) e.preventDefault(); drop(); }
    canvas.addEventListener("pointerdown", press);
    window.addEventListener("keydown", function (e) {
      if (e.code === "Space" || e.code === "Enter") { e.preventDefault(); drop(); }
      if (e.key === "r" || e.key === "R") { state = "play"; reset(); }
    });
    window.addEventListener("resize", resize);
    reset();
    state = "title";
    resize();
    loop();
  }
  window.LumenDock = { mount: mount };
})();
