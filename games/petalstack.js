/* Petalstack - Pixelsprout original */
(function(){
  var Petalstack = window.Petalstack = {};
  Petalstack.mount = function(canvas){
    var ctx = canvas.getContext("2d");
    var W = canvas.width = 480, H = canvas.height = 640;
    var state = "title", score = 0, best = +(localStorage.getItem("petalstack-best")||0);
    var petals = [], moving = null, speed = 1.6, dir = 1, baseW = 180;
    var colors = ["#FF8A9A","#FFB366","#7DDE92","#B59CE6","#FFD166"];
    var anim = 0;

    function reset(){
      petals = [{x:W/2, y:H-80, w:baseW, h:28, c:colors[0]}];
      spawn();
      score = 0;
      speed = 1.6;
      state = "play";
    }
    function spawn(){
      var last = petals[petals.length-1];
      moving = {x: 40 + Math.random()* (W-80), y: last.y - 70, w: last.w, h: 28, c: colors[petals.length % colors.length], vx: speed * (Math.random()<0.5?1:-1)};
    }
    function drop(){
      if(state!=="play" || !moving) return;
      var last = petals[petals.length-1];
      var overlap = Math.min(moving.x + moving.w/2, last.x + last.w/2) - Math.max(moving.x - moving.w/2, last.x - last.w/2);
      if(overlap <= 8){ state = "over"; return; }
      var perfect = Math.abs(moving.x - last.x) < 6;
      moving.w = perfect ? last.w : Math.max(40, overlap);
      moving.x = perfect ? last.x : (moving.x + last.x)/2;
      moving.y = last.y - 32;
      petals.push(moving);
      score += perfect ? 25 : 10;
      if(score > best){ best = score; localStorage.setItem("petalstack-best", best); }
      speed = Math.min(4.2, 1.6 + petals.length * 0.08);
      // camera follow
      if(moving.y < H*0.35){
        var shift = H*0.35 - moving.y;
        petals.forEach(function(p){ p.y += shift; });
      }
      spawn();
    }
    function draw(){
      ctx.fillStyle = "#12182A"; ctx.fillRect(0,0,W,H);
      // sky gradient
      var g = ctx.createLinearGradient(0,0,0,H);
      g.addColorStop(0,"#1A2744"); g.addColorStop(1,"#0D1220");
      ctx.fillStyle = g; ctx.fillRect(0,0,W,H);
      // petals
      petals.forEach(function(p,i){
        ctx.fillStyle = p.c;
        roundRect(ctx, p.x-p.w/2, p.y-p.h/2, p.w, p.h, 14);
        ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.4)"; ctx.lineWidth=2; ctx.stroke();
      });
      if(moving && state==="play"){
        ctx.fillStyle = moving.c;
        roundRect(ctx, moving.x-moving.w/2, moving.y-moving.h/2, moving.w, moving.h, 14);
        ctx.fill();
        ctx.strokeStyle = "#fff"; ctx.lineWidth=2; ctx.stroke();
      }
      // UI
      ctx.fillStyle = "#fff"; ctx.font = "bold 28px system-ui,sans-serif";
      ctx.textAlign = "left"; ctx.fillText(score, 20, 40);
      ctx.font = "14px system-ui"; ctx.fillStyle = "#AAB";
      ctx.fillText("BEST "+best, 20, 62);
      if(state==="title"){
        ctx.fillStyle = "rgba(0,0,0,0.55)"; ctx.fillRect(0,0,W,H);
        ctx.fillStyle = "#fff"; ctx.textAlign="center"; ctx.font="bold 48px system-ui";
        ctx.fillText("PETALSTACK", W/2, H/2-40);
        ctx.font="18px system-ui"; ctx.fillText("Tap or Space to stack petals", W/2, H/2+10);
        ctx.fillText("Grow the tallest bloom", W/2, H/2+40);
        ctx.font="bold 22px system-ui"; ctx.fillStyle="#FFB366";
        ctx.fillText("TAP TO START", W/2, H/2+100);
      }
      if(state==="over"){
        ctx.fillStyle = "rgba(0,0,0,0.65)"; ctx.fillRect(0,0,W,H);
        ctx.fillStyle="#fff"; ctx.textAlign="center"; ctx.font="bold 36px system-ui";
        ctx.fillText("Tower Fell", W/2, H/2-30);
        ctx.font="22px system-ui"; ctx.fillText("Score "+score, W/2, H/2+10);
        ctx.font="bold 20px system-ui"; ctx.fillStyle="#FFB366";
        ctx.fillText("TAP TO RESTART", W/2, H/2+70);
      }
    }
    function roundRect(ctx,x,y,w,h,r){
      ctx.beginPath(); ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r); ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath();
    }
    function loop(){
      if(state==="play" && moving){
        moving.x += moving.vx;
        if(moving.x - moving.w/2 < 20 || moving.x + moving.w/2 > W-20) moving.vx *= -1;
      }
      draw();
      requestAnimationFrame(loop);
    }
    function onAction(e){
      if(e) e.preventDefault();
      if(state==="title") reset();
      else if(state==="over") reset();
      else drop();
    }
    canvas.addEventListener("pointerdown", onAction);
    window.addEventListener("keydown", function(e){
      if(e.code==="Space" || e.code==="Enter") onAction(e);
    });
    loop();
  };
})();
