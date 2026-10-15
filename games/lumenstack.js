(function(){
  var C, ctx, W, H, state = 'title', score = 0, best = 0, stack = [], moving, dir = 1, speed = 2.2, size = 120, yBase, perfect = 0;
  var colors = ['#00e5ff','#00ff9d','#a8ff00','#ffea00','#ff9d00','#ff5e9d'];
  function resize(){
    W = C.width = C.clientWidth * devicePixelRatio;
    H = C.height = C.clientHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
    W /= devicePixelRatio; H /= devicePixelRatio;
    yBase = H * 0.72;
  }
  function initStack(){
    stack = [{x: W/2 - size/2, w: size, c: 0}];
    moving = {x: 40, w: size, c: 1};
    dir = 1; speed = 2.2; score = 0; perfect = 0;
  }
  function drop(){
    if(state !== 'play') return;
    var top = stack[stack.length-1];
    var left = Math.max(moving.x, top.x);
    var right = Math.min(moving.x + moving.w, top.x + top.w);
    var overlap = right - left;
    if(overlap < 12){
      state = 'over';
      if(score > best){ best = score; try{localStorage.setItem('lumenstack-best', best)}catch(e){} }
      return;
    }
    var newW = overlap;
    var newX = left;
    if(Math.abs(moving.x - top.x) < 6 && Math.abs(moving.w - top.w) < 6){
      perfect++;
      score += 25 + perfect * 5;
      newW = top.w; newX = top.x;
    } else {
      perfect = 0;
      score += Math.floor(overlap / 4);
    }
    stack.push({x: newX, w: newW, c: moving.c});
    if(stack.length > 12) stack.shift();
    size = newW;
    moving = {x: dir > 0 ? 20 : W - size - 20, w: size, c: (moving.c + 1) % colors.length};
    speed = Math.min(5.5, 2.2 + score * 0.012);
    dir *= -1;
  }
  function update(){
    if(state === 'play'){
      moving.x += dir * speed;
      if(moving.x <= 10 || moving.x + moving.w >= W - 10) dir *= -1;
    }
  }
  function draw(){
    ctx.fillStyle = '#0a1220';
    ctx.fillRect(0,0,W,H);
    // ground glow
    var g = ctx.createLinearGradient(0, yBase, 0, H);
    g.addColorStop(0, 'rgba(0,229,255,0.15)');
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g;
    ctx.fillRect(0, yBase - 40, W, H - yBase + 40);
    // stack
    var sy = yBase;
    for(var i = stack.length - 1; i >= 0; i--){
      var b = stack[i];
      ctx.fillStyle = colors[b.c % colors.length];
      ctx.shadowColor = colors[b.c % colors.length];
      ctx.shadowBlur = 12;
      roundRect(b.x, sy - 28, b.w, 26, 8);
      ctx.shadowBlur = 0;
      sy -= 26;
    }
    // moving
    if(state === 'play' || state === 'title'){
      ctx.fillStyle = colors[moving.c % colors.length];
      ctx.shadowColor = colors[moving.c % colors.length];
      ctx.shadowBlur = 16;
      roundRect(moving.x, 80, moving.w, 26, 8);
      ctx.shadowBlur = 0;
    }
    // UI
    ctx.fillStyle = '#e8f4ff';
    ctx.font = '600 22px system-ui,sans-serif';
    ctx.textAlign = 'center';
    if(state === 'title'){
      ctx.font = '700 36px system-ui,sans-serif';
      ctx.fillText('LUMENSTACK', W/2, H*0.32);
      ctx.font = '400 16px system-ui,sans-serif';
      ctx.fillStyle = '#7ab0d0';
      ctx.fillText('Time the drop. Stack the light.', W/2, H*0.38);
      ctx.fillStyle = '#00e5ff';
      ctx.font = '600 18px system-ui,sans-serif';
      ctx.fillText('Tap or press Space to start', W/2, H*0.55);
      if(best > 0){ ctx.fillStyle = '#88aacc'; ctx.font = '400 14px system-ui,sans-serif'; ctx.fillText('Best ' + best, W/2, H*0.60); }
    } else if(state === 'play'){
      ctx.textAlign = 'left';
      ctx.fillText(score, 16, 36);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#88aacc';
      ctx.font = '400 14px system-ui,sans-serif';
      ctx.fillText('Best ' + best, W - 16, 34);
    } else if(state === 'over'){
      ctx.font = '700 32px system-ui,sans-serif';
      ctx.fillText('Stack fell', W/2, H*0.35);
      ctx.font = '600 28px system-ui,sans-serif';
      ctx.fillStyle = '#00e5ff';
      ctx.fillText(score, W/2, H*0.43);
      ctx.fillStyle = '#7ab0d0';
      ctx.font = '400 16px system-ui,sans-serif';
      ctx.fillText('Best ' + best, W/2, H*0.49);
      ctx.fillStyle = '#00e5ff';
      ctx.font = '600 18px system-ui,sans-serif';
      ctx.fillText('Tap to retry', W/2, H*0.58);
    }
  }
  function roundRect(x,y,w,h,r){
    ctx.beginPath();
    ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
    ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); ctx.fill();
  }
  function loop(){
    update(); draw();
    requestAnimationFrame(loop);
  }
  function start(){
    if(state === 'title' || state === 'over'){
      state = 'play';
      initStack();
    } else if(state === 'play') drop();
  }
  window.Lumenstack = {
    mount: function(canvas){
      C = canvas; ctx = C.getContext('2d');
      try{ best = parseInt(localStorage.getItem('lumenstack-best')||'0',10)||0 }catch(e){}
      resize();
      initStack();
      window.addEventListener('resize', resize);
      C.addEventListener('pointerdown', function(e){ e.preventDefault(); start(); });
      window.addEventListener('keydown', function(e){
        if(e.code === 'Space' || e.code === 'Enter' || e.code === 'ArrowDown'){ e.preventDefault(); start(); }
      });
      loop();
    }
  };
})();
