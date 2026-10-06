(function(){
  var BEST = "cairnfall-best";
  function mount(canvas){
    var ctx = canvas.getContext("2d");
    var W = 360, H = 640;
    var state = "title";
    var stones = [];
    var mover, score, best, t, cam, msg;
    best = +(localStorage.getItem(BEST) || 0);
    function reset(){
      stones = [{x:180, y:560, w:168, h:28, perfect:false}];
      mover = {x:180, w:148, h:26, dir:1, speed:2.2};
      score = 0; t = 0; cam = 0; msg = "";
    }
    reset();
    function drop(){
      var top = stones[stones.length-1];
      var left = Math.max(mover.x - mover.w/2, top.x - top.w/2);
      var right = Math.min(mover.x + mover.w/2, top.x + top.w/2);
      var overlap = right - left;
      if (overlap < 14){ end(); return; }
      var perfect = Math.abs(mover.x - top.x) < 6;
      var w = perfect ? top.w : overlap;
      var x = perfect ? top.x : (left+right)/2;
      var y = top.y - 28;
      stones.push({x:x, y:y, w:w, h:26, perfect:perfect});
      score += perfect ? 2 : 1;
      if (score > best){ best = score; localStorage.setItem(BEST, String(best)); }
      mover.w = Math.max(36, w - (perfect ? 0 : 4));
      mover.speed = Math.min(6.4, 2.2 + stones.length * 0.12);
      mover.x = 40 + Math.random()*280;
      if (y < 280) cam = 280 - y;
    }
    function end(){ state = "over"; msg = "The stack slipped"; }
    function start(){ reset(); state = "play"; }
    function key(e){
      if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A"){ if(state==="play") mover.x -= 18; }
      else if (e.key === "ArrowRight" || e.key === "d" || e.key === "D"){ if(state==="play") mover.x += 18; }
      else if (e.key === " " || e.key === "Enter"){ act(); e.preventDefault(); }
      else if (e.key === "r" || e.key === "R"){ if(state!=="title") start(); }
    }
    function act(){
      if (state === "title" || state === "over") start();
      else drop();
    }
    canvas.addEventListener("pointerdown", function(e){ e.preventDefault(); act(); });
    window.addEventListener("keydown", key);
    function frame(now){
      var rect = canvas.getBoundingClientRect();
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      var cw = Math.max(240, rect.width), ch = Math.max(320, rect.height);
      if (canvas.width !== Math.floor(cw*dpr) || canvas.height !== Math.floor(ch*dpr)){
        canvas.width = Math.floor(cw*dpr); canvas.height = Math.floor(ch*dpr);
      }
      ctx.setTransform(canvas.width/W, 0, 0, canvas.height/H, 0, 0);
      t += 1;
      if (state === "play"){
        mover.x += mover.dir * mover.speed;
        if (mover.x < 30 + mover.w/2){ mover.x = 30 + mover.w/2; mover.dir = 1; }
        if (mover.x > 330 - mover.w/2){ mover.x = 330 - mover.w/2; mover.dir = -1; }
      }
      var g = ctx.createLinearGradient(0,0,0,H);
      g.addColorStop(0, "#1a2340"); g.addColorStop(1, "#243028");
      ctx.fillStyle = g; ctx.fillRect(0,0,W,H);
      ctx.fillStyle = "#f4e6c2"; ctx.beginPath(); ctx.arc(290, 70, 28, 0, 6.3); ctx.fill();
      ctx.fillStyle = "rgba(255,244,210,.8)";
      for (var i=0;i<12;i++){ ctx.fillRect(20+(i*47)%320, 18+(i*29)%120, 2, 2); }
      ctx.save(); ctx.translate(0, cam);
      ctx.fillStyle = "#2c382c"; ctx.fillRect(0, 590, W, 80);
      stones.forEach(function(s, i){
        var hue = i%2 ? "#8a7560" : "#6e7c78";
        if (s.perfect) hue = "#d8b56a";
        round(s.x-s.w/2, s.y, s.w, s.h, 12, hue);
        ctx.fillStyle = "rgba(90,130,70,.55)";
        ctx.beginPath(); ctx.ellipse(s.x, s.y+4, s.w*0.28, 6, 0, 0, 6.3); ctx.fill();
      });
      if (state === "play"){
        var my = stones[stones.length-1].y - 28;
        round(mover.x-mover.w/2, my, mover.w, mover.h, 12, "#c4a078");
      }
      ctx.restore();
      ctx.fillStyle = "#f6edd8"; ctx.font = "600 18px Inter, sans-serif";
      ctx.fillText("Score "+score, 16, 28);
      ctx.fillText("Best "+best, 16, 50);
      if (state !== "play"){
        ctx.fillStyle = "rgba(10,12,18,.62)"; ctx.fillRect(30, 200, 300, 200);
        ctx.fillStyle = "#f4d69c"; ctx.font = "700 32px Inter, sans-serif";
        ctx.fillText("Cairnfall", 86, 258);
        ctx.fillStyle = "#efe6d4"; ctx.font = "16px Inter, sans-serif";
        var line = state === "title" ? "Tap or press Space to drop" : msg;
        ctx.fillText(line, 62, 300);
        ctx.fillText(state === "title" ? "Build the night cairn" : "Tap to stack again", 92, 328);
        ctx.fillText("Arrows nudge · R restarts", 84, 360);
      }
      requestAnimationFrame(frame);
    }
    function round(x,y,w,h,r,fill){
      ctx.fillStyle = fill; ctx.beginPath();
      ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
      ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  window.Cairnfall = { mount: mount };
})();
