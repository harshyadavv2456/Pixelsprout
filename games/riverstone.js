(function(){
"use strict";
var COLS=6, ROWS=8, COLORS=["#e7c27a","#5ec8c0","#e07a62","#8d7ad6","#f4f0e6"];
var NAMES=["pebble","cobble","riverstone","boulder","moonstone"];
function bestGet(){try{return +localStorage.getItem("riverstone-best")||0}catch(e){return 0}}
function bestSet(n){try{localStorage.setItem("riverstone-best", String(n))}catch(e){}}
function mount(canvas){
  var ctx=canvas.getContext("2d");
  var dpr=1, W=480, H=640;
  var state="title", grid, score, best=bestGet(), col=2, next=0, chain=0, falling=null, msg="", lock=0;
  function resize(){
    var r=canvas.getBoundingClientRect();
    dpr=Math.min(window.devicePixelRatio||1, 2);
    canvas.width=Math.max(1, r.width)*dpr;
    canvas.height=Math.max(1, r.height)*dpr;
  }
  function empty(){grid=[]; for(var r=0;r<ROWS;r++){grid[r]=[]; for(var c=0;c<COLS;c++) grid[r][c]=null;}}
  function start(){empty(); score=0; chain=0; col=2; next=Math.random()<0.78?0:1; state="play"; msg=""; falling=null;}
  function cell(r,c){return r>=0&&r<ROWS&&c>=0&&c<COLS;}
  function gravity(){
    for(var c=0;c<COLS;c++){
      var stack=[];
      for(var r=ROWS-1;r>=0;r--) if(grid[r][c]!=null) stack.push(grid[r][c]);
      for(var r=0;r<ROWS;r++) grid[r][c]=null;
      for(var i=0;i<stack.length;i++) grid[ROWS-1-i][c]=stack[i];
    }
  }
  function groups(){
    var seen={}, out=[];
    function key(r,c){return r+","+c}
    for(var r=0;r<ROWS;r++) for(var c=0;c<COLS;c++){
      if(grid[r][c]==null||seen[key(r,c)]) continue;
      var t=grid[r][c], q=[[r,c]], g=[]; seen[key(r,c)]=1;
      while(q.length){
        var p=q.pop(); g.push(p);
        var dirs=[[1,0],[-1,0],[0,1],[0,-1]];
        for(var i=0;i<4;i++){
          var nr=p[0]+dirs[i][0], nc=p[1]+dirs[i][1];
          if(cell(nr,nc)&&grid[nr][nc]===t&&!seen[key(nr,nc)]){seen[key(nr,nc)]=1; q.push([nr,nc]);}
        }
      }
      if(g.length>=2) out.push({tier:t, cells:g});
    }
    return out;
  }
  function resolve(){
    var popped=false;
    for(var r=0;r<ROWS;r++) for(var c=0;c<COLS;c++){
      if(grid[r][c]===4){grid[r][c]=null; score+=250; popped=true; msg="Moonstone splash";}
    }
    if(popped){gravity(); return true;}
    var gs=groups();
    if(!gs.length) return false;
    chain++;
    for(var i=0;i<gs.length;i++){
      var g=gs[i];
      var keep=g.cells[0];
      for(var k=1;k<g.cells.length;k++) if(g.cells[k][0]>keep[0]) keep=g.cells[k];
      for(var k=0;k<g.cells.length;k++) grid[g.cells[k][0]][g.cells[k][1]]=null;
      var nt=Math.min(4, g.tier+1);
      grid[keep[0]][keep[1]]=nt;
      score+= (g.tier+1)*g.cells.length*12*chain;
      msg=NAMES[nt]+" x"+chain;
    }
    gravity();
    return true;
  }
  function drop(){
    if(state!=="play"||falling) return;
    var land=-1;
    for(var r=0;r<ROWS;r++) if(grid[r][col]==null) land=r;
    if(land<0){end(); return;}
    falling={c:col, tier:next, y:-0.6, to:land};
    next=Math.random()<0.7?0:(Math.random()<0.85?1:2);
  }
  function end(){
    state="over";
    if(score>best){best=score; bestSet(best);}
  }
  function tick(){
    if(falling){
      falling.y+=0.18;
      if(falling.y>=falling.to){
        grid[falling.to][falling.c]=falling.tier;
        falling=null; chain=0;
        var guard=0;
        while(resolve()&&guard++<12){}
        for(var c=0;c<COLS;c++) if(grid[0][c]!=null) end();
      }
    }
  }
  function drawStone(x,y,s,tier){
    ctx.save();
    ctx.translate(x,y);
    ctx.fillStyle="rgba(0,0,0,.28)";
    ctx.beginPath(); ctx.ellipse(0, s*0.28, s*0.42, s*0.16, 0, 0, 6.28); ctx.fill();
    ctx.fillStyle=COLORS[tier];
    ctx.beginPath(); ctx.ellipse(0, 0, s*0.4, s*0.3, 0, 0, 6.28); ctx.fill();
    ctx.fillStyle="rgba(255,255,255,.35)";
    ctx.beginPath(); ctx.ellipse(-s*0.1, -s*0.08, s*0.14, s*0.08, -0.4, 0, 6.28); ctx.fill();
    if(tier===4){ctx.strokeStyle="#fff6c8"; ctx.lineWidth=2; ctx.beginPath(); ctx.ellipse(0,0,s*0.46,s*0.34,0,0,6.28); ctx.stroke();}
    ctx.restore();
  }
  function draw(){
    var w=canvas.width, h=canvas.height;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    var cw=w/dpr, ch=h/dpr;
    var g=ctx.createLinearGradient(0,0,0,ch);
    g.addColorStop(0,"#102033"); g.addColorStop(1,"#1b3a3a");
    ctx.fillStyle=g; ctx.fillRect(0,0,cw,ch);
    ctx.fillStyle="#f3e6c4"; ctx.font="700 28px Georgia, serif"; ctx.fillText("RIVERSTONE", 18, 36);
    ctx.fillStyle="#d7eee8"; ctx.font="14px sans-serif";
    ctx.fillText("Score "+score, 18, 58);
    ctx.fillText("Best "+best, 140, 58);
    ctx.fillText("Next", cw-110, 36);
    drawStone(cw-48, 58, 46, next);
    var top=92, left=24, bw=cw-48, bh=ch-160;
    var cs=Math.min(bw/COLS, bh/ROWS);
    var ox=left+(bw-cs*COLS)/2, oy=top+(bh-cs*ROWS)/2;
    ctx.fillStyle="rgba(8,20,28,.45)";
    round(ox-8, oy-8, cs*COLS+16, cs*ROWS+16, 16); ctx.fill();
    ctx.strokeStyle="rgba(255,220,160,.35)"; ctx.stroke();
    ctx.strokeStyle="rgba(255,120,100,.55)"; ctx.setLineDash([6,6]);
    ctx.beginPath(); ctx.moveTo(ox, oy+cs*0.35); ctx.lineTo(ox+cs*COLS, oy+cs*0.35); ctx.stroke();
    ctx.setLineDash([]);
    for(var r=0;r<ROWS;r++) for(var c=0;c<COLS;c++){
      if(grid[r][c]==null) continue;
      drawStone(ox+c*cs+cs/2, oy+r*cs+cs/2, cs, grid[r][c]);
    }
    if(falling) drawStone(ox+falling.c*cs+cs/2, oy+falling.y*cs+cs/2, cs, falling.tier);
    if(state==="play"){
      ctx.strokeStyle="rgba(255,236,190,.7)"; ctx.lineWidth=2;
      ctx.strokeRect(ox+col*cs+4, oy+4, cs-8, cs*ROWS-8);
    }
    if(state!=="play"){
      ctx.fillStyle="rgba(6,12,18,.62)"; ctx.fillRect(0,0,cw,ch);
      ctx.fillStyle="#f6edd4"; ctx.font="700 36px Georgia, serif";
      ctx.textAlign="center";
      ctx.fillText(state==="title"?"Riverstone":"Basin full", cw/2, ch/2-40);
      ctx.font="16px sans-serif"; ctx.fillStyle="#d7eee8";
      ctx.fillText(state==="title"?"Drop stones. Two of a kind fuse.":"Score "+score+"   Best "+best, cw/2, ch/2);
      ctx.fillText("Tap, or press Enter, to play", cw/2, ch/2+32);
      ctx.textAlign="left";
    } else if(msg){
      ctx.fillStyle="#f6edd4"; ctx.font="14px sans-serif"; ctx.fillText(msg, 18, ch-28);
    }
    ctx.fillStyle="#9ec8c0"; ctx.font="12px sans-serif";
    ctx.fillText("Arrows move  Enter drops  R restarts", 18, ch-12);
  }
  function round(x,y,w,h,r){
    ctx.beginPath();
    ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
    ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath();
  }
  function pointer(e){
    var b=canvas.getBoundingClientRect();
    var x=(e.clientX-b.left)/b.width;
    if(state!=="play"){start(); return;}
    col=Math.max(0, Math.min(COLS-1, Math.floor(x*COLS)));
    drop();
  }
  function key(e){
    var k=e.key;
    if(k==="ArrowLeft"||k==="a"||k==="A"){col=Math.max(0,col-1); e.preventDefault();}
    else if(k==="ArrowRight"||k==="d"||k==="D"){col=Math.min(COLS-1,col+1); e.preventDefault();}
    else if(k==="Enter"||k===" "||k==="ArrowDown"){e.preventDefault(); if(state!=="play") start(); else drop();}
    else if(k==="r"||k==="R"){start();}
  }
  window.addEventListener("resize", resize);
  canvas.addEventListener("pointerdown", pointer);
  window.addEventListener("keydown", key);
  empty(); score=0; next=0;
  resize();
  (function loop(){tick(); draw(); requestAnimationFrame(loop);})();
}
window.Riverstone={mount:mount};
})();
