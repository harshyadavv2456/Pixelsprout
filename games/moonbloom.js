/* loads Moonbloom source parts */
(function(){
  var files = ["/games/moonbloom.p0", "/games/moonbloom.p1", "/games/moonbloom.p2", "/games/moonbloom.p3", "/games/moonbloom.p4"];
  Promise.all(files.map(function(u){return fetch(u).then(function(r){if(!r.ok) throw new Error(u); return r.text();})})).then(function(chunks){
    (0, eval)(chunks.join(""));
  }).catch(function(e){ console.error(e); });
})();
