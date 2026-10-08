/* loads Petalrack source parts */
(function(){
  var files = ["/games/petalrack.p0", "/games/petalrack.p1"];
  Promise.all(files.map(function(u){return fetch(u).then(function(r){if(!r.ok) throw new Error(u); return r.text();})})).then(function(chunks){
    (0, eval)(chunks.join(""));
  }).catch(function(e){ console.error(e); });
})();
