(function(){
  function mount(canvas){
    var ctx = canvas.getContext('2d');
    var W = 480, H = 720;
    var state = 'title';
    var lane = 1;
    var score = 0;
    var best = 0;
    try { best = +(localStorage.getItem('dewlane-best') || 0); } catch (e) {}
    var speed = 180;
    var dist = 0;
    var obstacles = [];
    var drops = [];
    var spawn = 0;
    var t = 0;
    var last = 0;
    function reset(){
      lane = 1; score = 0; speed = 180; dist = 0; obstacles = []; drops = []; spawn = 0; t = 0;
      state = 'play';
    }
    function addRow(){
      var kind = Math.random();
      var safe = (Math.random() * 3) | 0;
      if (kind < 0.62) {
        for (var i = 0; i < 3; i++) if (i !== safe) obstacles.push({ lane: i, y: -40, h: 36 });
      } else if (kind < 0.82) {
        obstacles.push({ lane: safe, y: -40, h: 36 });
      }
      if (Math.random() < 0.7) drops.push({ lane: (Math.random() * 3) | 0, y: -90 });
    }
    function hit(px, py, ox, oy, hw, hh){
      return Math.abs(px - ox) < hw && Math.abs(py - oy) < hh;
    }
    function end(){
      state = 'over';
      if (score > best) { best = score; try { localStorage.setItem('dewlane-best', String(best)); } catch (e) {} }
    }
    function step(dt){
      if (state !== 'play') return;
      t += dt;
      speed = Math.min(420, 180 + dist * 0.04);
      dist += speed * dt;
      score += dt * 8;
      spawn -= dt;
      if (spawn <= 0) { addRow(); spawn = Math.max(0.45, 1.15 - dist / 8000); }
      var py = H - 150;
      var px = 80 + lane * 160;
      obstacles.forEach(function(o){ o.y += speed * dt; });
      drops.forEach(function(d){ d.y += speed * dt; });
      obstacles = obstacles.filter(function(o){
        if (o.y > H + 40) return false;
        if (hit(px, py, 80 + o.lane * 160, o.y, 46, 28)) end();
        return state === 'play';
      });
      drops = drops.filter(function(d){
        if (d.y > H + 20) return false;
        if (hit(px, py, 80 + d.lane * 160, d.y, 28, 22)) { score += 25; return false; }
        return true;
      });
    }
    function drawSprout(x, y){
      ctx.fillStyle = '#2f8f4c';
      ctx.fillRect(x - 6, y - 8, 12, 36);
      ctx.fillStyle = '#7ad35a';
      ctx.beginPath(); ctx.ellipse(x - 14, y - 10, 18, 12, -0.6, 0, 6.28); ctx.fill();
      ctx.fillStyle = '#b6ee78';
      ctx.beginPath(); ctx.ellipse(x + 12, y - 16, 16, 11, 0.5, 0, 6.28); ctx.fill();
      ctx.fillStyle = '#14301c';
      ctx.fillRect(x - 6, y - 6, 3, 3); ctx.fillRect(x + 3, y - 6, 3, 3);
    }
    function frame(now){
      if (!last) last = now;
      var dt = Math.min(0.033, (now - last) / 1000);
      last = now;
      step(dt);
      canvas.width = W; canvas.height = H;
      ctx.fillStyle = '#102028';
      ctx.fillRect(0, 0, W, H);
      for (var i = 0; i < 3; i++) {
        ctx.fillStyle = i === 1 ? '#1d6b62' : '#16564f';
        ctx.fillRect(40 + i * 160, 0, 120, H);
        ctx.fillStyle = 'rgba(210,245,230,0.15)';
        ctx.fillRect(70 + i * 160, 0, 18, H);
      }
      drops.forEach(function(d){
        ctx.fillStyle = '#d8fbff';
        ctx.beginPath(); ctx.arc(80 + d.lane * 160, d.y, 10, 0, 6.28); ctx.fill();
      });
      obstacles.forEach(function(o){
        ctx.fillStyle = '#6a4a32';
        ctx.fillRect(80 + o.lane * 160 - 40, o.y - 16, 80, 32);
        ctx.fillStyle = '#3d6b34';
        ctx.fillRect(80 + o.lane * 160 - 28, o.y - 28, 16, 16);
      });
      drawSprout(80 + lane * 160, H - 150);
      ctx.fillStyle = '#eaffd8';
      ctx.font = '600 22px Inter, sans-serif';
      ctx.fillText(String(Math.floor(score)), 24, 36);
      ctx.font = '14px Inter, sans-serif';
      ctx.fillText('best ' + Math.floor(best), 24, 58);
      if (state !== 'play') {
        ctx.fillStyle = 'rgba(6,16,22,0.72)';
        ctx.fillRect(40, 200, 400, 280);
        ctx.fillStyle = '#f4ffe8';
        ctx.font = '800 42px Inter, sans-serif';
        ctx.fillText('DEWLANE', 108, 270);
        ctx.font = '18px Inter, sans-serif';
        ctx.fillStyle = '#c6ebc8';
        var msg = state === 'title' ? 'Hop lanes. Catch dew. Dodge roots.' : 'The lane closed. Score ' + Math.floor(score);
        ctx.fillText(msg, 78, 318);
        ctx.fillStyle = '#7ad35a';
        ctx.fillRect(150, 360, 180, 52);
        ctx.fillStyle = '#102018';
        ctx.font = '700 20px Inter, sans-serif';
        ctx.fillText(state === 'title' ? 'Play' : 'Again', 206, 394);
      }
      requestAnimationFrame(frame);
    }
    function move(dir){
      if (state !== 'play') { reset(); return; }
      lane = Math.max(0, Math.min(2, lane + dir));
    }
    canvas.addEventListener('pointerdown', function(e){
      var r = canvas.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width;
      if (state !== 'play') { reset(); return; }
      if (x < 0.4) move(-1); else if (x > 0.6) move(1);
    });
    window.addEventListener('keydown', function(e){
      if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') { move(-1); e.preventDefault(); }
      else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') { move(1); e.preventDefault(); }
      else if (e.key === ' ' || e.key === 'Enter') { if (state !== 'play') reset(); e.preventDefault(); }
    });
    requestAnimationFrame(frame);
  }
  window.Dewlane = { mount: mount };
})();
