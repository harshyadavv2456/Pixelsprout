(function(){
  var BEST_KEY = "pixelsprout-dewdash-best";
  function mount(canvas){
    var ctx = canvas.getContext("2d");
    var W = 480, H = 720;
    var state = "title";
    var score = 0, best = 0, dew = 0, dist = 0, speed = 220, lane = 1, yOff = 0;
    var jumping = 0, ducking = 0, alive = true, tick = 0;
    var obstacles = [], orbs = [];
    try { best = parseInt(localStorage.getItem(BEST_KEY) || "0", 10) || 0; } catch (e) {}
    function resize(){
      var r = canvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(r.width * dpr));
      canvas.height = Math.max(1, Math.floor(r.height * dpr));
    }
    resize();
    window.addEventListener("resize", resize);
    function laneX(i){ return 90 + i * 150; }
    function reset(){
      score = 0; dew = 0; dist = 0; speed = 220; lane = 1; jumping = 0; ducking = 0; alive = true; tick = 0;
      obstacles = []; orbs = [];
      state = "play";
    }
    function spawn(){
      var kind = Math.random() < 0.55 ? "rock" : (Math.random() < 0.5 ? "root" : "branch");
      obstacles.push({ lane: (Math.random()*3)|0, y: -40, kind: kind });
      if (Math.random() < 0.7) orbs.push({ lane: (Math.random()*3)|0, y: -90 });
    }
    function hop(){ if (state === "title" || state === "over") { reset(); return; } if (jumping <= 0 && ducking <= 0) jumping = 0.55; }
    function duck(){ if (state !== "play") return; if (jumping <= 0) ducking = 0.45; }
    function move(dir){ if (state !== "play") return; lane = Math.max(0, Math.min(2, lane + dir)); }
    function key(e){
      var k = e.key;
      if (k === "ArrowLeft" || k === "a") { move(-1); e.preventDefault(); }
      else if (k === "ArrowRight" || k === "d") { move(1); e.preventDefault(); }
      else if (k === "ArrowUp" || k === "w" || k === " ") { hop(); e.preventDefault(); }
      else if (k === "ArrowDown" || k === "s") { duck(); e.preventDefault(); }
      else if (k === "Enter") { hop(); e.preventDefault(); }
    }
    window.addEventListener("keydown", key);
    var tx = 0, ty = 0;
    canvas.addEventListener("pointerdown", function(e){ tx = e.clientX; ty = e.clientY; });
    canvas.addEventListener("pointerup", function(e){
      var dx = e.clientX - tx, dy = e.clientY - ty;
      if (Math.abs(dx) < 24 && Math.abs(dy) < 24) { hop(); return; }
      if (Math.abs(dx) > Math.abs(dy)) move(dx > 0 ? 1 : -1);
      else if (dy > 0) duck(); else hop();
    });
    function hit(o){
      if (o.lane !== lane || o.y < 500 || o.y > 590) return false;
      if (o.kind === "root" && jumping > 0.08) return false;
      if (o.kind === "branch" && ducking > 0.05) return false;
      return true;
    }
    function step(dt){
      if (state !== "play") return;
      tick += dt;
      dist += speed * dt;
      score = Math.floor(dist / 12) + dew * 25;
      speed = Math.min(460, 220 + dist / 80);
      if (jumping > 0) jumping -= dt;
      if (ducking > 0) ducking -= dt;
      yOff = jumping > 0 ? -Math.sin((0.55 - jumping) / 0.55 * Math.PI) * 70 : (ducking > 0 ? 18 : 0);
      var i;
      for (i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].y += speed * dt;
        if (hit(obstacles[i])) { alive = false; state = "over"; if (score > best) { best = score; try { localStorage.setItem(BEST_KEY, String(best)); } catch (e) {} } }
        if (obstacles[i].y > 780) obstacles.splice(i, 1);
      }
      for (i = orbs.length - 1; i >= 0; i--) {
        orbs[i].y += speed * dt;
        if (orbs[i].lane === lane && orbs[i].y > 500 && orbs[i].y < 580 && jumping < 0.2) { dew++; orbs.splice(i, 1); continue; }
        if (orbs[i].y > 780) orbs.splice(i, 1);
      }
      if (obstacles.length === 0 || obstacles[obstacles.length - 1].y > 180) spawn();
    }
    var last = performance.now();
    function frame(now){
      var dt = Math.min(0.033, (now - last) / 1000); last = now;
      step(dt);
      var rw = canvas.width, rh = canvas.height;
      ctx.setTransform(rw / W, 0, 0, rh / H, 0, 0);
      ctx.fillStyle = "#12343c";
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#f6e7a8";
      ctx.beginPath(); ctx.arc(400, 90, 36, 0, 7); ctx.fill();
      for (var L = 0; L < 3; L++) {
        ctx.fillStyle = L === lane ? "#2f6d52" : "#1d4a3c";
        ctx.fillRect(40 + L * 150, 0, 130, H);
      }
      orbs.forEach(function(o){
        ctx.fillStyle = "#b7f3ff";
        ctx.beginPath(); ctx.arc(laneX(o.lane), o.y, 10, 0, 7); ctx.fill();
      });
      obstacles.forEach(function(o){
        var x = laneX(o.lane) - 28;
        if (o.kind === "rock") { ctx.fillStyle = "#6d5a48"; ctx.fillRect(x, o.y, 56, 36); }
        else if (o.kind === "root") { ctx.fillStyle = "#8a5a32"; ctx.fillRect(x, o.y + 16, 56, 18); }
        else { ctx.fillStyle = "#245c38"; ctx.fillRect(x - 6, o.y, 70, 16); }
      });
      var py = 540 + yOff, px = laneX(lane);
      ctx.fillStyle = "#5ecf6a";
      ctx.beginPath(); ctx.ellipse(px, py + (ducking > 0 ? 10 : 0), 22, ducking > 0 ? 14 : 26, 0, 0, 7); ctx.fill();
      ctx.fillStyle = "#2f9a4a";
      ctx.beginPath(); ctx.moveTo(px, py - 20); ctx.lineTo(px + 28, py - 42); ctx.lineTo(px + 6, py - 8); ctx.fill();
      ctx.fillStyle = "#102018";
      ctx.fillRect(px + 6, py - 6, 5, 5);
      ctx.fillStyle = "#f4f1e4";
      ctx.font = "24px sans-serif";
      ctx.fillText("Dew " + dew + "   " + score, 24, 40);
      if (state === "title") {
        ctx.fillStyle = "rgba(8,18,22,0.72)"; ctx.fillRect(40, 220, 400, 240);
        ctx.fillStyle = "#ffd56a"; ctx.font = "54px sans-serif"; ctx.fillText("DEWDASH", 92, 300);
        ctx.fillStyle = "#e8f6ea"; ctx.font = "20px sans-serif";
        ctx.fillText("Swipe lanes. Tap to hop.", 110, 350);
        ctx.fillText("Duck branches. Grab dew.", 108, 382);
        ctx.fillText("Best " + best + "  ·  tap to start", 108, 424);
      }
      if (state === "over") {
        ctx.fillStyle = "rgba(8,18,22,0.75)"; ctx.fillRect(50, 250, 380, 200);
        ctx.fillStyle = "#ffd56a"; ctx.font = "40px sans-serif"; ctx.fillText("Sprout stopped", 90, 320);
        ctx.fillStyle = "#fff"; ctx.font = "22px sans-serif";
        ctx.fillText("Score " + score + "   Best " + best, 110, 368);
        ctx.fillText("Tap or Enter to run again", 96, 408);
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  window.Dewdash = { mount: mount };
})();
