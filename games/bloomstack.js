/* Bloomstack */
(function(){
  const canvas = document.getElementById('bloomstack');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let score = 0, best = +(localStorage.getItem('bloomstackBest')||0);
  let state = 'title', stacks = [], moving = {x:100, w:160, dir:1, speed:2};
  function draw(){
    ctx.fillStyle='#0D0E10'; ctx.fillRect(0,0,canvas.width,canvas.height);
    if (state==='title'){
      ctx.fillStyle='#F8B500'; ctx.font='bold 32px sans-serif'; ctx.textAlign='center';
      ctx.fillText('BLOOMSTACK', canvas.width/2, 200);
      ctx.fillStyle='#fff'; ctx.font='18px sans-serif';
      ctx.fillText('Tap or Space to start', canvas.width/2, 260);
    } else {
      ctx.fillStyle='#fff'; ctx.fillText('Score: '+score, 20, 30);
    }
    requestAnimationFrame(draw);
  }
  function input(){ if (state!=='play'){ state='play'; score=0; } }
  canvas.addEventListener('pointerdown', input);
  window.addEventListener('keydown', e => { if (e.code==='Space') input(); });
  draw();
})();
