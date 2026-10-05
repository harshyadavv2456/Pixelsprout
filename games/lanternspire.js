/* Lanternspire — Pixel Sprout original. Timing stack. */
(function () {
  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var W = 360, H = 640;
    var state = "title";
    var best = 0;
    try { best = parseInt(localStorage.getItem("lanternspire-best") || "0", 10) || 0; } catch (e) {}
    var stack = [{ x: 180, w: 168, y: 520, hue: 8 }];
    var piece = { x: 180, w: 148, dir: 1, hue: 22 };
    var speed = 2.2, score = 0, combo = 0, perfects = 0, shake = 0, particles = [], overReason = "";

    function reset() {
      stack = [{ x: 180, w: 168, y: 520, hue: 8 }];
      piece = makePiece(168);
      speed = 2.2;
      score = 0;
      combo = 0;
      perfects = 0;
      shake = 0;
      particles = [];
      overReason = "";
      state = "play";
    }
    function makePiece(w) {
      var dir = Math.random() < 0.5 ? 1 : -1;
      return { x: dir < 0 ? 40 + w / 2 : 320 - w / 2, w: w, dir: dir, hue: 8 + stack.length * 14 };
    }
    function drop() {
      if (state !== "play") return;
      var top = stack[stack.length - 1];
      var left = Math.max(piece.x - piece.w / 2, top.x - top.w / 2);
      var right = Math.min(piece.x + piece.w / 2, top.x + top.w / 2);
      var overlap = right - left;
      if (overlap < 16) {
        overReason = "The lantern missed the spire.";
        end();
        return;
      }
      var perfect = Math.abs(piece.x - top.x) < 6;
      var nw = perfect ? top.w : overlap;
      var nx = perfect ? top.x : (left + right) / 2;
      if (perfect) {
        combo += 1;
        perfects += 1;
        score += 25 + combo * 5;
        burst(nx, top.y - 18, 14);
      } else {
        combo = 0;
        score += 10;
        var cut = piece.w - overlap;
        burst(piece.x > top.x ? right : left, top.y - 10, 6);
        if (cut > 0) shake = 4;
      }
      stack.push({ x: nx, w: nw, y: top.y - 46, hue: piece.hue });
      if (stack.length > 8) {
        for (var i = 0; i < stack.length; i++) stack[i].y += 46;
        stack.shift();
      }
      speed = Math.min(7.4, 2.2 + stack.length * 0.18 + perfects * 0.05);
      piece = makePiece(nw);
      score += stack.length;
      if (nw < 22) {
        overReason = "The spire got too narrow.";
        end();
      }
    }
    function end() {
      state = "over";
      if (score > best) {
        best = score;
        try { localStorage.setItem("lanternspire-best", String(best)); } catch (e) {}
      }
    }
    function burst(x, y, n) {
      for (var i = 0; i < n; i++) {
        particles.push({
          x: x, y: y,
          vx: (Math.random() - 0.5) * 3.2,
          vy: -Math.random() * 2.4 - 0.4,
          life: 28 + Math.random() * 16
        });
      }
    }
    function pointer(clientX) {
      var r = canvas.getBoundingClientRect();
      var x = ((clientX - r.left) / r.width) * W;
      if (state === "title" || state === "over") { reset(); return; }
      piece.x = Math.max(piece.w / 2 + 4, Math.min(W - piece.w / 2 - 4, x));
      drop();
    }
    canvas.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      pointer(e.clientX);
    });
    window.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") {
        if (state === "play") piece.x = Math.max(piece.w / 2 + 4, piece.x - 18);
      } else if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") {
        if (state === "play") piece.x = Math.min(W - piece.w / 2 - 4, piece.x + 18);
      } else if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        if (state === "play") drop();
        else reset();
      } else if (e.key === "r" || e.key === "R") {
        reset();
      }
    });

    function lantern(x, y, w, hue, hanging) {
      var h = 40;
      ctx.save();
      ctx.translate(x, y);
      if (hanging) {
        ctx.strokeStyle = "#d4a85c";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, -28);
        ctx.lineTo(0, -18);
        ctx.stroke();
      }
      ctx.fillStyle = "hsl(" + hue + ",72%,46%)";
      roundRect(-w / 2, -18, w, h, 10);
      ctx.fill();
      ctx.fillStyle = "hsla(" + (hue + 30) + ",90%,72%,0.85)";
      roundRect(-w * 0.28, -8, w * 0.56, 18, 6);
      ctx.fill();
      ctx.fillStyle = "#3a2418";
      roundRect(-w * 0.22, 18, w * 0.44, 6, 2);
      ctx.fill();
      ctx.strokeStyle = "#d4a85c";
      ctx.beginPath();
      ctx.moveTo(0, 24);
      ctx.lineTo(0, 32);
      ctx.stroke();
      ctx.restore();
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
    function frame() {
      if (canvas.width !== W) { canvas.width = W; canvas.height = H; }
      if (state === "play") {
        piece.x += speed * piece.dir;
        if (piece.x > W - piece.w / 2 - 6) piece.dir = -1;
        if (piece.x < piece.w / 2 + 6) piece.dir = 1;
      }
      if (shake > 0) shake *= 0.8;
      ctx.setTransform(1, 0, 0, 1, (Math.random() - 0.5) * shake, 0);
      var g = ctx.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "#14182e");
      g.addColorStop(1, "#2a1a28");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#f4e2b0";
      for (var s = 0; s < 28; s++) {
        var sx = (s * 97) % W, sy = (s * 53) % 220;
        ctx.fillRect(sx, sy, 2, 2);
      }
      ctx.fillStyle = "#e8d2a4";
      ctx.beginPath();
      ctx.arc(300, 70, 22, 0, 6.3);
      ctx.fill();
      ctx.fillStyle = "#14182e";
      ctx.beginPath();
      ctx.arc(312, 64, 18, 0, 6.3);
      ctx.fill();
      ctx.fillStyle = "#5a3a24";
      ctx.fillRect(70, 568, 220, 14);
      ctx.fillStyle = "#3a2418";
      ctx.fillRect(56, 580, 248, 12);
      for (var i = 0; i < stack.length; i++) {
        var b = stack[i];
        lantern(b.x, b.y, b.w, b.hue, false);
      }
      if (state === "play") lantern(piece.x, 92, piece.w, piece.hue, true);
      for (var p = particles.length - 1; p >= 0; p--) {
        var q = particles[p];
        q.x += q.vx; q.y += q.vy; q.life -= 1;
        ctx.globalAlpha = Math.max(0, q.life / 30);
        ctx.fillStyle = "#ffd28a";
        ctx.fillRect(q.x, q.y, 3, 3);
        if (q.life <= 0) particles.splice(p, 1);
      }
      ctx.globalAlpha = 1;
      ctx.fillStyle = "#f6e7c4";
      ctx.font = "600 18px sans-serif";
      ctx.fillText("Score " + score, 16, 32);
      ctx.font = "14px sans-serif";
      ctx.fillText("Best " + best, 16, 52);
      if (combo > 1) {
        ctx.fillStyle = "#ffd28a";
        ctx.font = "700 16px sans-serif";
        ctx.fillText("Spark x" + combo, 240, 32);
      }
      if (state === "title") {
        veil();
        ctx.fillStyle = "#ffd68a";
        ctx.font = "700 32px serif";
        ctx.textAlign = "center";
        ctx.fillText("LANTERNSPIRE", 180, 250);
        ctx.fillStyle = "#f6e7c4";
        ctx.font = "16px sans-serif";
        ctx.fillText("Stack the festival lanterns.", 180, 290);
        ctx.fillText("Tap or Space to drop.", 180, 316);
        ctx.fillText("Left and Right nudge the swing.", 180, 340);
        ctx.fillText("Tap to start", 180, 390);
        ctx.textAlign = "left";
      } else if (state === "over") {
        veil();
        ctx.fillStyle = "#ffd68a";
        ctx.font = "700 28px serif";
        ctx.textAlign = "center";
        ctx.fillText("Spire fell", 180, 250);
        ctx.fillStyle = "#f6e7c4";
        ctx.font = "16px sans-serif";
        ctx.fillText(overReason, 180, 286);
        ctx.fillText("Score " + score + "   Best " + best, 180, 316);
        ctx.fillText("Tap or Enter to stack again", 180, 360);
        ctx.textAlign = "left";
      }
      requestAnimationFrame(frame);
    }
    function veil() {
      ctx.fillStyle = "rgba(10,12,24,0.55)";
      ctx.fillRect(0, 0, W, H);
    }
    requestAnimationFrame(frame);
  }
  window.Lanternspire = { mount: mount };
})();
