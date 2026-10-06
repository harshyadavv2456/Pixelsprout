(function () {
  "use strict";
  var BEST_KEY = "kilnstack-best";
  var COL = {
    sky0: "#1a1020",
    sky1: "#3a1c18",
    brick: "#e07038",
    hot: "#ffb45a",
    ember: "#ff5a28",
    ash: "#c9b6a4",
    text: "#ffe6c4"
  };

  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var state = "title";
    var score = 0;
    var best = 0;
    var combo = 0;
    var bricks = [];
    var mover = null;
    var cam = 0;
    var t = 0;
    var msg = "";
    var msgT = 0;
    try { best = parseInt(localStorage.getItem(BEST_KEY) || "0", 10) || 0; } catch (e) { best = 0; }

    function resize() {
      var r = canvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(280, Math.floor(r.width * dpr));
      canvas.height = Math.max(360, Math.floor(r.height * dpr));
    }

    function saveBest() {
      if (score > best) {
        best = score;
        try { localStorage.setItem(BEST_KEY, String(best)); } catch (e) {}
      }
    }

    function reset() {
      score = 0;
      combo = 0;
      msg = "";
      cam = 0;
      bricks = [{ x: 0, y: 0, w: 168, perfect: false }];
      spawn();
      state = "play";
    }

    function spawn() {
      var prev = bricks[bricks.length - 1];
      var w = Math.max(46, prev.w);
      mover = {
        w: w,
        y: prev.y + 28,
        phase: Math.random() * Math.PI * 2,
        speed: 1.35 + Math.min(2.4, bricks.length * 0.06),
        amp: 118 + Math.min(70, bricks.length * 3)
      };
    }

    function place() {
      if (state !== "play" || !mover) return;
      var prev = bricks[bricks.length - 1];
      var x = Math.sin(mover.phase) * mover.amp;
      var left = Math.max(x - mover.w / 2, prev.x - prev.w / 2);
      var right = Math.min(x + mover.w / 2, prev.x + prev.w / 2);
      var w = right - left;
      if (w < 18) {
        state = "over";
        saveBest();
        return;
      }
      var cx = (left + right) / 2;
      var perfect = Math.abs(x - prev.x) < 7;
      if (perfect) {
        cx = prev.x;
        w = prev.w;
        combo += 1;
        score += 2 + combo;
        msg = combo > 1 ? "Perfect x" + combo : "Perfect";
        msgT = 0.8;
      } else {
        combo = 0;
        score += 1;
        msg = "";
      }
      bricks.push({ x: cx, y: prev.y + 28, w: w, perfect: perfect });
      if (bricks.length > 18) bricks.shift();
      spawn();
    }

    function tap() {
      if (state === "title" || state === "over") reset();
      else place();
    }

    function loop(now) {
      var dt = Math.min(0.033, (now - (loop.last || now)) / 1000);
      loop.last = now;
      t += dt;
      if (msgT > 0) msgT -= dt;
      if (state === "play" && mover) mover.phase += mover.speed * dt;
      var target = bricks.length ? bricks[bricks.length - 1].y : 0;
      cam += (target - cam) * 0.08;
      draw();
      requestAnimationFrame(loop);
    }

    function draw() {
      var w = canvas.width;
      var h = canvas.height;
      var g = ctx.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, COL.sky0);
      g.addColorStop(1, COL.sky1);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
      var s = Math.min(w / 420, h / 640);
      ctx.save();
      ctx.translate(w / 2, h * 0.72);
      ctx.scale(s, s);
      ctx.translate(0, cam);
      var glow = ctx.createRadialGradient(0, -cam * 0.2, 10, 0, 40, 260);
      glow.addColorStop(0, "rgba(255,120,40,0.35)");
      glow.addColorStop(1, "rgba(255,80,20,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(0, 40, 260, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#3c241c";
      ctx.fillRect(-190, -cam - 200, 16, 520);
      ctx.fillRect(174, -cam - 200, 16, 520);
      bricks.forEach(function (b, i) {
        var hot = i === bricks.length - 1;
        roundRect(b.x - b.w / 2, -b.y, b.w, 24, 6, hot ? COL.hot : COL.brick);
        ctx.fillStyle = hot ? "rgba(255,220,160,0.55)" : "rgba(80,30,18,0.25)";
        ctx.fillRect(b.x - b.w / 2 + 6, -b.y + 5, b.w - 12, 4);
      });
      if (state === "play" && mover) {
        var x = Math.sin(mover.phase) * mover.amp;
        ctx.strokeStyle = "rgba(255,210,150,0.7)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, -mover.y - 70);
        ctx.lineTo(x, -mover.y);
        ctx.stroke();
        roundRect(x - mover.w / 2, -mover.y, mover.w, 24, 6, COL.ember);
      }
      ctx.restore();
      ctx.fillStyle = COL.text;
      ctx.font = "600 " + Math.floor(22 * (w / 480)) + "px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText("Score " + score, 18, 36);
      ctx.textAlign = "right";
      ctx.fillText("Best " + best, w - 18, 36);
      if (msg && msgT > 0) {
        ctx.textAlign = "center";
        ctx.fillStyle = COL.hot;
        ctx.font = "700 " + Math.floor(28 * (w / 480)) + "px sans-serif";
        ctx.fillText(msg, w / 2, h * 0.28);
      }
      if (state !== "play") {
        ctx.fillStyle = "rgba(10,6,8,0.55)";
        ctx.fillRect(0, 0, w, h);
        ctx.textAlign = "center";
        ctx.fillStyle = COL.hot;
        ctx.font = "800 " + Math.floor(42 * (w / 480)) + "px sans-serif";
        ctx.fillText("KILNSTACK", w / 2, h * 0.4);
        ctx.fillStyle = COL.text;
        ctx.font = "500 " + Math.floor(18 * (w / 480)) + "px sans-serif";
        var line = state === "title"
          ? "Tap or press Space to set the brick"
          : "The stack slipped. Score " + score;
        ctx.fillText(line, w / 2, h * 0.48);
        ctx.fillText(state === "title" ? "Best " + best : "Tap to fire the kiln again", w / 2, h * 0.54);
      }
    }

    function roundRect(x, y, w, h, r, fill) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
      ctx.fillStyle = fill;
      ctx.fill();
    }

    canvas.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      tap();
    });
    window.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        tap();
      } else if (e.key === "r" || e.key === "R") {
        reset();
      }
    });
    window.addEventListener("resize", resize);
    resize();
    requestAnimationFrame(loop);
  }

  window.Kilnstack = { mount: mount };
})();
