/* Vinehook — Pixel Sprout original. Swing a lantern, release, catch the next hook. */
(function () {
  var BEST_KEY = "vinehook-best";

  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 360, H = 640;
    var state = "title";
    var score = 0;
    var best = 0;
    try { best = +localStorage.getItem(BEST_KEY) || 0; } catch (e) { best = 0; }
    var combo = 0;
    var t = 0;
    var hooks = [];
    var cam = 0;
    var swinging = true;
    var anchor = { x: 180, y: 140 };
    var rope = 96;
    var amp = 1.05;
    var omega = 1.7;
    var flash = 0;
    var msg = "";
    var pod = { x: 180, y: 236, vx: 0, vy: 0 };
    var last = 0;
    var pointerBound = false;

    function saveBest() {
      if (score > best) {
        best = score;
        try { localStorage.setItem(BEST_KEY, String(best)); } catch (e) {}
      }
    }

    function addHook(i) {
      var y = 140 + i * 148;
      var base = (i % 2 === 0) ? 108 : 252;
      var jitter = ((i * 53) % 64) - 32;
      hooks.push({
        x: Math.max(64, Math.min(296, base + jitter)),
        y: y,
        got: i === 0
      });
    }

    function syncPod() {
      var a = Math.sin(t * omega) * amp;
      var w = Math.cos(t * omega) * omega * amp;
      pod.x = anchor.x + Math.sin(a) * rope;
      pod.y = anchor.y + Math.cos(a) * rope;
      pod.vx = Math.cos(a) * rope * w;
      pod.vy = -Math.sin(a) * rope * w;
    }

    function reset() {
      score = 0;
      combo = 0;
      cam = 0;
      t = 0.4;
      flash = 0;
      msg = "";
      swinging = true;
      amp = 1.02;
      omega = 1.65;
      anchor = { x: 180, y: 140 };
      hooks = [];
      for (var i = 0; i < 10; i++) addHook(i);
      syncPod();
    }

    function latch(h, perfect) {
      swinging = true;
      anchor = { x: h.x, y: h.y };
      h.got = true;
      combo = perfect ? combo + 1 : 1;
      score += 10 * combo;
      saveBest();
      flash = 0.55;
      msg = perfect ? "PERFECT x" + combo : "HOOKED";
      omega = Math.min(2.6, 1.65 + score * 0.004);
      amp = Math.min(1.25, 1.02 + score * 0.001);
      while (hooks[hooks.length - 1].y < anchor.y + 1100) addHook(hooks.length);
    }

    function release() {
      if (state !== "play") {
        state = "play";
        reset();
        return;
      }
      if (!swinging) return;
      syncPod();
      swinging = false;
    }

    function step(dt) {
      t += dt;
      if (flash > 0) flash -= dt;
      if (state !== "play") return;
      if (swinging) {
        syncPod();
      } else {
        pod.vy += 920 * dt;
        pod.x += pod.vx * dt;
        pod.y += pod.vy * dt;
        for (var i = 0; i < hooks.length; i++) {
          var h = hooks[i];
          if (h.got) continue;
          if (h.y < anchor.y + 30) continue;
          var dx = pod.x - h.x;
          var dy = pod.y - h.y;
          if (dx * dx + dy * dy < 34 * 34 && pod.vy > -20) {
            latch(h, Math.abs(dx) < 16);
            break;
          }
        }
        if (pod.y > cam + H + 80 || pod.x < -60 || pod.x > W + 60) state = "over";
      }
      var target = pod.y - 200;
      cam += (target - cam) * Math.min(1, dt * 5);
    }

    function roundRect(x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
    }

    function drawLantern(x, y) {
      ctx.fillStyle = "#ffb24a";
      ctx.beginPath();
      ctx.ellipse(x, y, 15, 19, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#fff1c4";
      ctx.beginPath();
      ctx.ellipse(x, y + 1, 7, 9, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#c48c3c";
      ctx.fillRect(x - 6, y - 22, 12, 5);
    }

    function draw() {
      var rect = canvas.getBoundingClientRect();
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      var cw = Math.max(2, rect.width);
      var ch = Math.max(2, rect.height);
      var pw = Math.floor(cw * dpr);
      var ph = Math.floor(ch * dpr);
      if (canvas.width !== pw || canvas.height !== ph) {
        canvas.width = pw;
        canvas.height = ph;
      }
      ctx.setTransform(canvas.width / W, 0, 0, canvas.height / H, 0, 0);
      var sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#1a1240");
      sky.addColorStop(1, "#102433");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#f4e7c3";
      ctx.beginPath();
      ctx.arc(286, 78, 26, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#1a1240";
      ctx.beginPath();
      ctx.arc(298, 72, 22, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "rgba(255,255,255,.75)";
      for (var s = 0; s < 28; s++) {
        var sx = (s * 97) % W;
        var sy = ((s * 53) - cam * 0.12) % 420;
        if (sy < 0) sy += 420;
        ctx.fillRect(sx, sy, 2, 2);
      }
      ctx.save();
      ctx.translate(0, -cam);
      for (var i = 0; i < hooks.length; i++) {
        var h = hooks[i];
        if (h.y < cam - 80 || h.y > cam + H + 80) continue;
        ctx.strokeStyle = "#3f6e50";
        ctx.lineWidth = 7;
        ctx.beginPath();
        ctx.moveTo(h.x, h.y - 90);
        ctx.lineTo(h.x, h.y);
        ctx.stroke();
        ctx.fillStyle = h.got ? "#f0c14a" : "#e7f3d8";
        ctx.beginPath();
        ctx.arc(h.x, h.y, 9, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#8a6840";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(h.x, h.y + 4, 13, 0.25, Math.PI - 0.25);
        ctx.stroke();
      }
      if (state === "play" || state === "over") {
        ctx.strokeStyle = "#7dcb86";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(anchor.x, anchor.y);
        ctx.quadraticCurveTo((anchor.x + pod.x) / 2 + 6, (anchor.y + pod.y) / 2, pod.x, pod.y - 18);
        ctx.stroke();
        drawLantern(pod.x, pod.y);
      }
      ctx.restore();
      ctx.fillStyle = "#fff";
      ctx.font = "600 22px Inter, sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(String(score), 16, 36);
      ctx.font = "14px Inter, sans-serif";
      ctx.fillStyle = "rgba(255,255,255,.72)";
      ctx.fillText("BEST " + best, 16, 56);
      if (flash > 0 && state === "play") {
        ctx.fillStyle = "#ffe08a";
        ctx.font = "700 18px Inter, sans-serif";
        ctx.fillText(msg, 16, 82);
      }
      if (state !== "play") {
        ctx.fillStyle = "rgba(8,10,18,.62)";
        ctx.fillRect(0, 180, W, 250);
        ctx.textAlign = "center";
        ctx.fillStyle = "#fff6df";
        ctx.font = "800 40px Inter, sans-serif";
        ctx.fillText("VINEHOOK", W / 2, 250);
        ctx.font = "16px Inter, sans-serif";
        ctx.fillStyle = "#d5ebcf";
        if (state === "over") {
          ctx.fillText("The lantern slipped. Score " + score, W / 2, 292);
          ctx.fillText("Tap or press Space to swing again", W / 2, 318);
        } else {
          ctx.fillText("The lantern swings. Tap to let go.", W / 2, 292);
          ctx.fillText("Catch the next hook. Center hits chain.", W / 2, 318);
        }
        ctx.textAlign = "left";
      }
    }

    function frame(now) {
      var dt = Math.min(0.033, (now - last) / 1000 || 0.016);
      last = now;
      step(dt);
      draw();
      requestAnimationFrame(frame);
    }

    function onKey(e) {
      if (e.code === "Space" || e.code === "Enter") {
        e.preventDefault();
        release();
      }
    }

    if (!pointerBound) {
      canvas.addEventListener("pointerdown", function (e) {
        e.preventDefault();
        release();
      });
      window.addEventListener("keydown", onKey);
      pointerBound = true;
    }
    reset();
    state = "title";
    requestAnimationFrame(frame);
  }

  window.Vinehook = { mount: mount };
})();
