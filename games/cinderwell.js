/* loads Cinderwell source parts */
(function(){
  var files = ["/games/cinderwell.p0", "/games/cinderwell.p1", "/games/cinderwell.p2"];
  Promise.all(files.map(function(u){return fetch(u).then(function(r){if(!r.ok) throw new Error(u); return r.text();})})).then(function(chunks){
    (0, eval)(chunks.join(""));
  }).catch(function(e){ console.error(e); });
})();
