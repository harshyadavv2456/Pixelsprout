/* Nectarjar — Pixelsprout original. Drop matching nectar orbs. Same sizes fuse. */
(function () {
  var TIERS = [
    { n: "Dew", c: "#7ad7ff", r: 16 },
    { n: "Petal", c: "#ff8ec4", r: 22 },
    { n: "Berry", c: "#ff6a4a", r: 29 },
    { n: "Blossom", c: "#c9a0ff", r: 37 },
    { n: "Hive", c: "#ffc14a", r: 46 },
    { n: "Lantern", c: "#7dffa0", r: 56 },
    { n: "Moonpear", c: "#ffe7a0", r: 68 }
  ];
  var W = 420, H = 640, LINE = 148, LEFT = 78, RIGHT = 342, FLOOR = 586;

  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    function fit() {
      var r = canvas.getBoundingClientRect();
      canvas.width = Math.max(2, r.width) * dpr;
      canvas.height = Math.max(2, r.height) * dpr;
    }
    fit();
    window.addEventListener("resize", fit);
    var st = "title", score = 0, best = +(localStorage.getItem("nectarjar-best") || 0);
    var orbs = [], aim = 210, held = 0, next = 0, dropCd = 0, overT = 0, pops = [];
    function roll() { return Math.random() < 0.72 ? 0 : Math.random() < 0.7 ? 1 : 2; }
    function reset() {
      orbs = []; score = 0; held = roll(); next = roll(); aim = 210; dropCd = 0; overT = 0; pops = []; st = "play";
    }
    function drop() {
      if (st !== "play" || dropCd > 0) return;
      var t = held, r = TIERS[t].r;
      var x = Math.max(LEFT + r + 4, Math.min(RIGHT - r - 4, aim));
      orbs.push({ x: x, y: 96, vx: 0, vy: 0.4, t: t, lock: 12 });
      held = next; next = roll(); dropCd = 28;
    }
    function step() {
      if (st !== "play") return;
      dropCd = Math.max(0, dropCd - 1);
      var g = 0.28;
      for (var i = 0; i < orbs.length; i++) {
        var o = orbs[i];
        o.vy += g; o.vx *= 0.992; o.vy *= 0.998;
        o.x += o.vx; o.y += o.vy;
        if (o.lock) o.lock--;
        var rad = TIERS[o.t].r;
        if (o.x - rad < LEFT) { o.x = LEFT + rad; o.vx = Math.abs(o.vx) * 0.35; }
        if (o.x + rad > RIGHT) { o.x = RIGHT - rad; o.vx = -Math.abs(o.vx) * 0.35; }
        if (o.y + rad > FLOOR) { o.y = FLOOR - rad; o.vy = -Math.abs(o.vy) * 0.22; o.vx *= 0.8; }
      }
      for (var a = 0; a < orbs.length; a++) {
        for (var b = a + 1; b < orbs.length; b++) {
          var A = orbs[a], B = orbs[b];
          var ra = TIERS[A.t].r, rb = TIERS[B.t].r;
          var dx = B.x - A.x, dy = B.y - A.y;
          var d = Math.hypot(dx, dy) || 0.01;
          var min = ra + rb;
          if (d < min) {
            var nx = dx / d, ny = dy / d, overlap = min - d;
            A.x -= nx * overlap * 0.5; A.y -= ny * overlap * 0.5;
            B.x += nx * overlap * 0.5; B.y += ny * overlap * 0.5;
            var rel = (A.vx - B.vx) * nx + (A.vy - B.vy) * ny;
            if (rel > 0) {
              var imp = rel * 0.55;
              A.vx -= imp * nx; A.vy -= imp * ny;
              B.vx += imp * nx; B.vy += imp * ny;
            }
            if (A.t === B.t && A.t < 6 && !A.lock && !B.lock && d < min * 0.96) {
              var nt = A.t + 1;
              var mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
              orbs.splice(b, 1); orbs.splice(a, 1);
              orbs.push({ x: mx, y: my, vx: (A.vx + B.vx) * 0.3, vy: -1.4, t: nt, lock: 10 });
              score += (nt + 1) * (nt + 1) * 12;
              pops.push({ x: mx, y: my, t: 24, n: TIERS[nt].n });
              if (score > best) { best = score; localStorage.setItem("nectarjar-best", String(best)); }
              a = orbs.length; break;
            }
          }
        }
      }
      var danger = false;
      for (i = 0; i < orbs.length; i++) {
        o = orbs[i];
        if (!o.lock && o.y - TIERS[o.t].r < LINE && Math.abs(o.vy) < 1.2) danger = true;
      }
      overT = danger ? overT + 1 : 0;
      if (overT > 70) st = "over";
      for (i = pops.length - 1; i >= 0; i--) { pops[i].t--; pops[i].y -= 0.6; if (pops[i].t <= 0) pops.splice(i, 1); }
    }
    function orb(x, y, t) {
      var spec = TIERS[t], r = spec.r;
      var grd = ctx.createRadialGradient(x - r * 0.3, y - r * 0.35, r * 0.1, x, y, r);
      grd.addColorStop(0, "#fff");
      grd.addColorStop(0.25, spec.c);
      grd.addColorStop(1, "#1a2030");
      ctx.beginPath(); ctx.arc(x, y, r, 0, 6.3); ctx.fillStyle = grd; ctx.fill();
      ctx.beginPath(); ctx.arc(x - r * 0.32, y - r * 0.36, r * 0.22, 0, 6.3);
      ctx.fillStyle = "rgba(255,255,255,.75)"; ctx.fill();
    }
    function draw() {
      var s = canvas.width / W;
      ctx.setTransform(s, 0, 0, s * (canvas.height / H) / (canvas.width / W) * (canvas.width / W) / s, 0, 0);
      ctx.setTransform(canvas.width / W, 0, 0, canvas.height / H, 0, 0);
      var bg = ctx.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, "#14182c"); bg.addColorStop(1, "#2a1c34");
      ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
      ctx.strokeStyle = "rgba(255,255,255,.18)"; ctx.setLineDash([6, 6]);
      ctx.beginPath(); ctx.moveTo(LEFT, LINE); ctx.lineTo(RIGHT, LINE); ctx.stroke(); ctx.setLineDash([]);
      ctx.strokeStyle = "rgba(220,245,255,.8)"; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(LEFT, 120); ctx.lineTo(LEFT, FLOOR - 20);
      ctx.quadraticCurveTo(LEFT, FLOOR + 16, 140, FLOOR + 8);
      ctx.lineTo(280, FLOOR + 8);
      ctx.quadraticCurveTo(RIGHT, FLOOR + 16, RIGHT, FLOOR - 20);
      ctx.lineTo(RIGHT, 120); ctx.stroke();
      ctx.strokeStyle = "rgba(255,255,255,.35)"; ctx.strokeRect(150, 78, 120, 22);
      for (var i = 0; i < orbs.length; i++) orb(orbs[i].x, orbs[i].y, orbs[i].t);
      if (st === "play") {
        ctx.globalAlpha = 0.45; orb(aim, 96, held); ctx.globalAlpha = 1;
        ctx.fillStyle = "#d7e7ff"; ctx.font = "14px sans-serif"; ctx.fillText("Next", 338, 36);
        orb(378, 70, next);
      }
      for (i = 0; i < pops.length; i++) {
        ctx.fillStyle = "#ffe7a8"; ctx.font = "bold 14px sans-serif";
        ctx.fillText(pops[i].n, pops[i].x - 20, pops[i].y);
      }
      ctx.fillStyle = "#fff6d2"; ctx.font = "bold 18px sans-serif";
      ctx.fillText("Score " + score, 16, 32);
      ctx.fillStyle = "#c9d4ea"; ctx.font = "13px sans-serif";
      ctx.fillText("Best " + best, 16, 52);
      if (st !== "play") {
        ctx.fillStyle = "rgba(8,10,18,.72)"; ctx.fillRect(36, 200, 348, 230);
        ctx.fillStyle = "#ffe7a8"; ctx.font = "bold 32px sans-serif";
        ctx.fillText(st === "title" ? "Nectarjar" : "Jar spilled", 78, 268);
        ctx.fillStyle = "#e7eefc"; ctx.font = "16px sans-serif";
        var msg = st === "title" ? "Drop matching orbs. They fuse." : "Score " + score + "   Best " + best;
        ctx.fillText(msg, 78, 304);
        ctx.fillText("Tap, click, or Space to start", 78, 344);
        ctx.fillStyle = "#9eb0d0"; ctx.font = "13px sans-serif";
        ctx.fillText("Arrows move   Space drops   R restarts", 78, 380);
      }
    }
    function pointer(e) {
      var rect = canvas.getBoundingClientRect();
      var x = ((e.clientX - rect.left) / rect.width) * W;
      aim = x;
      if (st !== "play") { reset(); return; }
      drop();
    }
    canvas.addEventListener("pointerdown", pointer);
    canvas.addEventListener("pointermove", function (e) {
      if (st !== "play") return;
      var rect = canvas.getBoundingClientRect();
      aim = ((e.clientX - rect.left) / rect.width) * W;
    });
    window.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") aim -= 16;
      if (e.key === "ArrowRight") aim += 16;
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); if (st !== "play") reset(); else drop(); }
      if (e.key === "r" || e.key === "R") reset();
      aim = Math.max(LEFT + 20, Math.min(RIGHT - 20, aim));
    });
    function loop() { step(); draw(); requestAnimationFrame(loop); }
    loop();
  }
  window.Nectarjar = { mount: mount };
})();
