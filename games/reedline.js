(function(){
  function mount(canvas){
    var ctx = canvas.getContext("2d");
    var W=360,H=480,dpr=1;
    var state="title";
    var score=0,best=0,chain=0,msg="";
    var hook,next,ang,vel,t=0;
    var flyer=null, particles=[];
    try{ best = +localStorage.getItem("reedline-best")||0; }catch(e){}
    function resize(){
      var r = canvas.getBoundingClientRect();
      dpr = Math.min(2, window.devicePixelRatio||1);
      W = Math.max(280, r.width||360);
      H = Math.max(400, r.height||480);
      canvas.width = Math.floor(W*dpr);
      canvas.height = Math.floor(H*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0);
    }
    function makeHook(x){
      return {x:x, y: 92 + Math.random()*70};
    }
    function reset(){
      score=0; chain=0; msg=""; flyer=null; particles=[];
      hook = {x: W*0.32, y: 140};
      next = {x: W*0.72, y: 118 + Math.random()*80};
      ang = -0.9; vel = 1.7;
      state="play";
    }
    function saveBest(){
      if(score>best){ best=score; try{ localStorage.setItem("reedline-best", String(best)); }catch(e){} }
    }
    function burst(x,y,col){
      for(var i=0;i<8;i++) particles.push({x:x,y:y,vx:(Math.random()-0.5)*3,vy:-Math.random()*2.4,life:28,col:col});
    }
    function release(){
      if(state==="title" || state==="over"){ reset(); return; }
      if(state!=="play" || flyer) return;
      var L=168;
      var px = hook.x + Math.sin(ang)*L;
      var py = hook.y + Math.cos(ang)*L;
      var tx = Math.cos(ang)*vel*L*0.42;
      var ty = -Math.sin(ang)*vel*L*0.42;
      flyer = {x:px,y:py,vx:tx,vy:ty+0.4};
    }
    function step(){
      t += 1;
      if(state==="play" && !flyer){
        ang += vel*0.018;
        if(ang>1.15){ ang=1.15; vel=-Math.abs(vel); }
        if(ang<-1.15){ ang=-1.15; vel=Math.abs(vel); }
      }
      if(flyer){
        flyer.vy += 0.22;
        flyer.x += flyer.vx;
        flyer.y += flyer.vy;
        var dx = next.x - flyer.x, dy = next.y - flyer.y;
        var dist = Math.hypot(dx,dy);
        if(dist < 28 && flyer.vy > -1){
          var perfect = dist < 12;
          chain = perfect ? chain+1 : 0;
          var add = 10 + (perfect ? 8*chain : 0);
          score += add;
          msg = perfect ? ("PERFECT x"+chain) : "CAUGHT";
          burst(next.x, next.y, perfect ? "#ffe7a0" : "#9ad07a");
          hook = next;
          next = {x: hook.x + 150 + Math.random()*70, y: 100 + Math.random()*110};
          if(next.x > W-40){ hook.x -= next.x-(W-70); next.x = W-70; }
          ang = -0.7; vel = 1.55 + Math.min(1.2, score/180);
          flyer = null;
        } else if(flyer.y > H+30 || flyer.x < -40 || flyer.x > W+40){
          state="over"; saveBest(); flyer=null;
        }
      }
      for(var i=particles.length-1;i>=0;i--){
        var p=particles[i]; p.x+=p.vx; p.y+=p.vy; p.life--;
        if(p.life<=0) particles.splice(i,1);
      }
    }
    function reed(x,y){
      ctx.strokeStyle="#3f7a48"; ctx.lineWidth=5;
      ctx.beginPath(); ctx.moveTo(x,y); ctx.quadraticCurveTo(x+10,y+40,x-4,H); ctx.stroke();
    }
    function lantern(x,y,glow){
      ctx.save();
      ctx.translate(x,y);
      ctx.fillStyle = glow ? "#ffd27a" : "#e07a32";
      ctx.beginPath();
      ctx.moveTo(0,-18); ctx.lineTo(-12,-6); ctx.lineTo(-10,12); ctx.lineTo(10,12); ctx.lineTo(12,-6); ctx.closePath();
      ctx.fill();
      ctx.fillStyle="#fff1c2";
      ctx.fillRect(-6,-2,12,10);
      ctx.fillStyle="#6b3a22";
      ctx.fillRect(-5,12,10,4);
      ctx.restore();
    }
    function draw(){
      var g = ctx.createLinearGradient(0,0,0,H);
      g.addColorStop(0,"#14243c"); g.addColorStop(1,"#0c1c22");
      ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
      ctx.fillStyle="#f3e2b0"; ctx.beginPath(); ctx.arc(W*0.78,70,28,0,6.3); ctx.fill();
      ctx.fillStyle="#14243c"; ctx.beginPath(); ctx.arc(W*0.78+12,62,24,0,6.3); ctx.fill();
      ctx.fillStyle="#16343c"; ctx.fillRect(0,H-70,W,70);
      if(state!=="title"){
        reed(hook.x, hook.y);
        reed(next.x, next.y);
        ctx.strokeStyle="#d7b15a"; ctx.lineWidth=3;
        ctx.beginPath(); ctx.arc(hook.x, hook.y, 7, 0, 6.3); ctx.stroke();
        ctx.beginPath(); ctx.arc(next.x, next.y, 7, 0, 6.3); ctx.stroke();
        var lx, ly;
        if(flyer){ lx=flyer.x; ly=flyer.y; }
        else {
          lx = hook.x + Math.sin(ang)*168;
          ly = hook.y + Math.cos(ang)*168;
          ctx.strokeStyle="#7dba78"; ctx.lineWidth=3;
          ctx.beginPath(); ctx.moveTo(hook.x, hook.y); ctx.lineTo(lx, ly); ctx.stroke();
        }
        lantern(lx, ly, true);
        ctx.fillStyle="#e8f0dc"; ctx.font="600 18px sans-serif";
        ctx.fillText(""+score, 16, 32);
        ctx.font="14px sans-serif"; ctx.fillStyle="#b7c8aa";
        ctx.fillText("best "+best, 16, 52);
        if(msg){ ctx.fillStyle="#ffe7a0"; ctx.font="700 16px sans-serif"; ctx.fillText(msg, W/2-40, 36); }
      }
      particles.forEach(function(p){
        ctx.globalAlpha = Math.max(0,p.life/28);
        ctx.fillStyle=p.col; ctx.fillRect(p.x,p.y,3,3); ctx.globalAlpha=1;
      });
      if(state==="title"){
        ctx.fillStyle="#ffe8c0"; ctx.font="700 42px serif"; ctx.fillText("REEDLINE", 36, H*0.38);
        ctx.fillStyle="#c9d7bf"; ctx.font="16px sans-serif";
        ctx.fillText("Swing the lantern. Release to catch", 36, H*0.38+36);
        ctx.fillText("the next reed. Center hits chain.", 36, H*0.38+58);
        ctx.fillStyle="#ffd27a"; ctx.fillText("Tap or press Space", 36, H*0.38+100);
        lantern(W*0.72, H*0.62, true);
      }
      if(state==="over"){
        ctx.fillStyle="rgba(6,10,16,0.55)"; ctx.fillRect(0,0,W,H);
        ctx.fillStyle="#ffe8c0"; ctx.font="700 32px serif"; ctx.fillText("Missed the reed", 40, H*0.42);
        ctx.fillStyle="#d5e2cc"; ctx.font="18px sans-serif";
        ctx.fillText("Score "+score+"   Best "+best, 40, H*0.42+36);
        ctx.fillStyle="#ffd27a"; ctx.fillText("Tap to swing again", 40, H*0.42+72);
      }
    }
    function frame(){ resize(); step(); draw(); requestAnimationFrame(frame); }
    canvas.addEventListener("pointerdown", function(e){ e.preventDefault(); release(); });
    window.addEventListener("keydown", function(e){
      if(e.code==="Space" || e.code==="Enter"){ e.preventDefault(); release(); }
    });
    resize(); requestAnimationFrame(frame);
  }
  window.Reedline = { mount: mount };
})();
