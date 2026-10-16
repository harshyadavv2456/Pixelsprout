/* Pixelsprout redesign layer: Surprise me, homepage trending/collections, game-page Play next + FAQ + trust line.
   Loaded by pixelsprout-features.js on every page. Ad slots are never moved or removed. */
(function () {
  'use strict';
  var D = '/assets/redesign/';
  var esc = function (s) { return String(s || '').replace(/[&<>"']/g, function (c) { return '&#' + c.charCodeAt(0) + ';'; }); };
  var getJSON = function (u) { return fetch(u, { credentials: 'same-origin' }).then(function (r) { if (!r.ok) throw r.status; return r.json(); }); };
  var slugify = function (s) { return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
  var homeP; var home = function () { return homeP || (homeP = getJSON(D + 'home.json').then(function (h) {
    /* keep the header search label exact: same live count as the hero stats line */
    var sp = h.stats && document.querySelector('.search-trigger span');
    if (sp && /^Search [0-9,]+\+? games$/.test(sp.textContent)) sp.textContent = 'Search ' + Number(h.stats.games).toLocaleString('en-US') + ' games';
    return h; })); };
  var origSet = null;

  function card(g, opts) {
    var orig = origSet && origSet[g.s];
    return '<a class="card' + (orig ? ' card--original' : '') + '" href="/games/' + esc(g.s) + '.html">' +
      '<span class="card__media"><img src="' + esc(g.i || '/assets/logo-icon.png') + '" alt="' + esc(g.t) + '" width="320" height="320" loading="lazy" decoding="async">' +
      (orig ? '<span class="card__badge">Original</span>' : '') + (g.v ? '<span class="card__badge card__badge--hot">Hot</span>' : '') + (g.m === 0 ? '<span class="card__kb" title="Best with a keyboard">⌨</span>' : '') + '<span class="card__play" aria-hidden="true">Play</span></span>' +
      '<span class="card__title">' + esc(g.t) + '</span>' + (g.c ? '<span class="card__meta">' + esc(g.c) + '</span>' : '') + '</a>';
  }

  /* ---- Surprise me ---- */
  function surprise(e) {
    if (e) e.preventDefault();
    home().then(function (h) { var a = h.all; location.href = '/games/' + a[Math.floor(Math.random() * a.length)] + '.html'; })
      .catch(function () { location.href = '/all-games/'; });
  }
  var GENRES = ['Action','Puzzle','Arcade','Racing','Sports','Shooter','Adventure','Strategy','Girls','Two Player','Multiplayer','Casual'];
  function genreNav() {
    var top = document.querySelector('.topbar'); if (!top || document.querySelector('.rd-genres')) return;
    var n = document.createElement('nav'); n.className = 'rd-genres'; n.setAttribute('aria-label', 'Genres');
    n.innerHTML = GENRES.map(function (g) { var u = '/' + slugify(g) + '/'; return '<a href="' + u + '"' + (location.pathname === u ? ' aria-current="page"' : '') + '>' + esc(g) + '</a>'; }).join('');
    top.insertAdjacentElement('afterend', n);
  }
  function ensureHeader() {
    genreNav();
    var inner = document.querySelector('.topbar__inner');
    if (inner && !inner.querySelector('.topnav')) {
      var nav = document.createElement('nav'); nav.className = 'topnav'; nav.setAttribute('aria-label', 'Primary');
      nav.innerHTML = '<a href="/all-games/">Browse</a><a href="/originals/">Originals</a><a href="/guides/">Guides</a><a class="btn-ghost" href="/all-games/" data-surprise>Surprise me</a>';
      var act = inner.querySelector('.topbar__actions'); inner.insertBefore(nav, act || null);
    }
    var actions = document.querySelector('.topbar__actions');
    if (actions && !actions.querySelector('.surprise-mini')) {
      var b = document.createElement('a'); b.href = '/all-games/'; b.className = 'icon-btn surprise-mini'; b.setAttribute('data-surprise', '');
      b.setAttribute('aria-label', 'Surprise me: random game'); b.textContent = '🎲'; actions.insertBefore(b, actions.firstChild);
    }
  }
  document.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('[data-surprise]'); if (t) surprise(e); });


  /* ---- Top picks: large cards (homepage top + category pages). Data from build-redesign-data.py ---- */
  function picksHTML(list, title, id) {
    if (!list || !list.length) return ''; id = id || 'tp-title';
    return '<section class="tp" aria-labelledby="' + id + '"><div class="rd-head"><h2 id="' + id + '">' + esc(title) + '</h2></div><div class="tp__grid">' +
      list.slice(0, 12).map(function (g) {
        return '<a class="tp-card" href="/games/' + esc(g.s) + '.html">' +
          '<span class="tp-card__media"><img src="' + esc(g.i) + '" alt="' + esc(g.t) + '" width="400" height="250" loading="lazy" decoding="async"></span>' +
          '<span class="tp-card__body"><span class="tp-card__tag">' + esc(g.tag || g.c) + '</span><span class="tp-card__title">' + esc(g.t) + '</span>' +
          '<span class="btn-lime tp-card__play">▶ Play</span></span></a>'; }).join('') + '</div></section>';
  }
  function categoryPicks() {
    var main = document.querySelector('#main'); var head = main && main.querySelector('.page-head'); if (!head) return;
    var seg = location.pathname.split('/').filter(Boolean)[0]; if (!seg) return;
    getJSON(D + 'picks/' + encodeURIComponent(seg) + '.json').then(function (l) {
      if (!l.length) return; var d = document.createElement('div'); d.innerHTML = picksHTML(l, 'Top picks');
      head.parentNode.insertBefore(d.firstChild, head.nextSibling);
    }).catch(function () {});
  }


  /* ---- Hero extras: Just added, Game of the day, stats (data: home.json from build-redesign-data.py) ---- */
  function heroExtras(h) {
    var now = Date.now() / 1000, wk = (h.recent || []).filter(function (g) { return g.a >= now - 7 * 86400; });
    var n = wk.length || h.new7 || 0;
    var real = wk.filter(function (g) { return g.ok; });
    var ja = !n ? '' : '<section class="ja" aria-labelledby="ja-title"><p class="ja__label">Just added</p>' +
      '<h2 class="ja__title" id="ja-title">' + n + ' new game' + (n === 1 ? '' : 's') + ' just added</h2>' +
      '<div class="ja__grid">' + real.slice(0, 6).map(function (g) {
        return '<a class="ja__item" href="/games/' + esc(g.s) + '.html"><span class="ja__media"><img src="' + esc(g.i) + '" alt="" width="200" height="125" loading="lazy" decoding="async"></span><span class="ja__name">' + esc(g.t) + '</span></a>'; }).join('') +
      '</div><a class="btn-lime ja__cta" href="/new-games/">Play the new games →</a></section>';
    var pool = real.length ? real : (h.recent || []).filter(function (g) { return g.ok; });
    var gotd = '';
    if (pool.length) {
      var d = new Date(), day = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);
      var g = pool[day % pool.length];
      gotd = '<section class="gotd" aria-labelledby="gotd-title"><a class="gotd__media" href="/games/' + esc(g.s) + '.html" tabindex="-1" aria-hidden="true"><img src="' + esc(g.i) + '" alt="" width="640" height="400" decoding="async"></a>' +
        '<div class="gotd__body"><p class="label">Game of the day</p><h2 class="gotd__title" id="gotd-title">' + esc(g.t) + '</h2>' +
        '<p class="gotd__desc">A free ' + esc((g.c || 'browser').toLowerCase()) + ' game that plays right in your browser.</p>' +
        '<a class="btn-lime" href="/games/' + esc(g.s) + '.html">▶ Play ' + esc(g.t) + '</a></div></section>';
    }
    var st = h.stats ? '<p class="rd-stats">' + Number(h.stats.games).toLocaleString('en-US') + ' free games · ' + n + ' added this week · ' + h.stats.genres + ' genres</p>' : '';
    return { ja: ja, gotd: gotd, stats: st };
  }

  /* ---- Homepage ---- */
  function homepage() {
    var main = document.querySelector('#main, main'); if (!main) return;
    return home().then(function (h) {
      origSet = {}; h.originals.forEach(function (g) { origSet[g.s] = 1; });
      var hero = '<section class="rd-hero"><p class="label">Free · No download · Plays on phone</p>' +
        '<p class="rd-hero__title h1">Pick a game.<br><span class="accent-text">Start playing.</span></p>' +
        '<div class="rd-hero__cta"><button class="btn-lime" type="button" data-surprise>🎲 Surprise me</button>' +
        '<a class="btn-ghost" href="/all-games/">Browse all games</a><a class="btn-ghost" href="/originals/">Pixelsprout Originals</a></div></section>';
      var tabs = [['trending', 'Trending'], ['originals', 'Originals'], ['newest', 'New']];
      var tr = '<section class="rd-block"><div class="rd-head"><h2>What people are playing</h2>' +
        '<label class="rd-phone"><input type="checkbox" data-rd-phone> Phone-friendly</label></div>' +
        '<div class="rd-tabs" role="tablist">' + tabs.map(function (t, i) {
          return '<button role="tab" type="button" class="rd-tab" data-tab="' + t[0] + '" aria-selected="' + (i ? 'false' : 'true') + '">' + t[1] + '</button>'; }).join('') +
        '</div><div class="grid rd-grid" data-rd-grid></div></section>';
      var cols = '<section class="rd-block"><h2>Collections</h2>' + h.collections.map(function (c) {
        return '<div class="rd-row"><div class="rd-head"><h3>' + esc(c.name) + '</h3><a class="shelf__more" href="/' + esc(c.slug) + '/">See all</a></div>' +
          '<div class="shelf__track rd-track">' + c.games.map(card).join('') + '</div></div>'; }).join('') + '</section>';
      var wrap = document.createElement('div'); wrap.className = 'rd-home'; var hx = heroExtras(h); var col = (h.collage || []).length >= 3 ? '<div class="rd-collage" aria-label="City action games">' + h.collage.slice(0, 5).map(function (g, i) { return '<a class="rd-collage__c rd-collage__c' + i + '" href="/games/' + esc(g.s) + '.html"><img src="' + esc(g.i) + '" alt="' + esc(g.t) + '" width="400" height="250" decoding="async"' + (i ? ' loading="lazy"' : '') + '></a>'; }).join('') + '</div>' : '';
      hero = hero.replace('<section class="rd-hero">', '<section class="rd-hero">' + col).replace('</section>', hx.stats + hx.ja + '</section>');
      wrap.innerHTML = hero + hx.gotd + picksHTML(h.week, 'Games of the week', 'gow-title') + picksHTML(h.picks, 'Top picks') + tr + cols;
      main.insertBefore(wrap, main.firstChild);
      var grid = wrap.querySelector('[data-rd-grid]');
      var cur = 'trending', phoneOnly = false;
      var show = function (k) { cur = k; var l = (h[k] || []).filter(function (g) { return !phoneOnly || g.m !== 0; }); grid.innerHTML = l.slice(0, 12).map(card).join('') || '<p class="rd-empty">No phone-friendly games in this list yet.</p>'; };
      show('trending');
      wrap.querySelectorAll('.rd-tab').forEach(function (b) { b.addEventListener('click', function () {
        wrap.querySelectorAll('.rd-tab').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); }); show(b.dataset.tab); }); });
      /* Phone-friendly: g.m from build-redesign-data.py (0 = keyboard-only controls in the game description). */
      wrap.querySelector('[data-rd-phone]').addEventListener('change', function () { phoneOnly = this.checked; try { localStorage.setItem('rdPhone', phoneOnly ? '1' : ''); } catch (e) {} show(cur); });
      try { if (localStorage.getItem('rdPhone')) { wrap.querySelector('[data-rd-phone]').checked = true; phoneOnly = true; show(cur); } } catch (e) {}
    }).catch(function () {});
  }

  /* ---- Game page ---- */
  function gamepage() {
    var page = document.querySelector('.game-page'); if (!page) return;
    var slug = location.pathname.replace(/^.*\/games\//, '').replace(/\.html$/, '');
    var title = (document.querySelector('.game-bar__title') || document.querySelector('h1') || {}).textContent || document.title;
    title = title.trim();
    var genre = 'Arcade';
    document.querySelectorAll('script[type="application/ld+json"]').forEach(function (s) {
      try { var j = JSON.parse(s.textContent); if (j['@type'] === 'VideoGame' && j.genre) genre = j.genre; } catch (e) {}
    });
    var bar = document.querySelector('.game-bar');
    if (bar && !document.querySelector('.rd-trust')) {
      var t = document.createElement('p'); t.className = 'rd-trust';
      t.innerHTML = '✓ Plays right here in your browser: free, no download, no account. Game link checked by Pixelsprout.';
      bar.parentNode.insertBefore(t, bar.nextSibling);
    }
    var faq = [
      ['Is ' + title + ' free to play?', 'Yes. ' + title + ' is free on Pixelsprout and plays in your web browser with no download or sign-up.'],
      ['Can I play ' + title + ' on my phone?', document.querySelector('.desktop-only') ? 'No. ' + title + ' is desktop only: it needs a mouse and keyboard.' : 'Yes, it runs in a modern mobile browser. Rotate to landscape or use full screen for the best view.'],
      ['What kind of game is ' + title + '?', title + ' is a ' + genre.toLowerCase() + ' game. Find more in the ' + genre + ' section.'],
      ['Do I need to install anything?', 'No. Pixelsprout games are HTML5 and load directly in the page.']
    ];
    var about = document.querySelector('.game-about') || page;
    if (!document.querySelector('.rd-howto')) {
      var ht = document.createElement('section'); ht.className = 'rd-howto';
      ht.innerHTML = '<h2>How to play</h2><ol><li>Press Play in the game frame above; it loads right in the page.</li><li>Use your mouse, keyboard or touch, following the in-game prompts.</li><li>Tap full screen on phones and turn to landscape for the best view.</li></ol>';
      about.parentNode.insertBefore(ht, about.nextSibling); about = ht;
    }
    var hasFaq = Array.prototype.some.call(document.querySelectorAll('script[type="application/ld+json"]'), function (s) { return /FAQPage/.test(s.textContent); });
    var sec = document.createElement('section'); sec.className = 'rd-faq';
    sec.innerHTML = '<h2>At a glance</h2>' + faq.map(function (q) { return '<details><summary>' + esc(q[0]) + '</summary><p>' + esc(q[1]) + '</p></details>'; }).join('');
    about.parentNode.insertBefore(sec, about.nextSibling);
    if (!hasFaq) {
      var ld = document.createElement('script'); ld.type = 'application/ld+json';
      ld.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faq.map(function (q) {
        return { '@type': 'Question', name: q[0], acceptedAnswer: { '@type': 'Answer', text: q[1] } }; }) });
      document.head.appendChild(ld);
    }
    Promise.all([getJSON(D + 'cat/' + slugify(genre) + '.json').catch(function () { return []; }), home().catch(function () { return { originals: [] }; })]).then(function (r) {
      origSet = {}; r[1].originals.forEach(function (g) { origSet[g.s] = 1; });
      var pool = r[0].filter(function (g) { return g.s !== slug; });
      var o = r[1].originals.filter(function (g) { return g.s !== slug; });
      var picks = [o[Math.floor(Math.random() * o.length)]].concat(pool.sort(function () { return Math.random() - .5; }).slice(0, 2)).filter(Boolean);
      if (!picks.length) return;
      var pn = document.createElement('section'); pn.className = 'rd-next';
      pn.innerHTML = '<div class="rd-head"><h2>Play next</h2><button class="btn-ghost" type="button" data-surprise>🎲 Surprise me</button></div><div class="rd-next__list">' + picks.map(card).join('') + '</div>';
      (document.querySelector('.rd-trust') || bar || page).insertAdjacentElement('afterend', pn);
      var more = pool.filter(function (g) { return picks.indexOf(g) < 0; }).slice(0, 12);
      if (more.length) { var ml = document.createElement('section'); ml.className = 'rd-more';
        ml.innerHTML = '<div class="rd-head"><h2>More like this</h2><a class="shelf__more" href="/' + slugify(genre) + '/">All ' + esc(genre) + '</a></div><div class="rd-track">' + more.map(card).join('') + '</div>';
        (document.querySelector('.rd-faq') || page).insertAdjacentElement('afterend', ml); }
    });
  }

  function init() {
    ensureHeader();
    var p = location.pathname;
    var ready = function () { document.documentElement.classList.add('rd-ready'); };
    if (p === '/' || p === '/index.html') { try { Promise.resolve(homepage()).then(ready, ready); } catch (e) { ready(); } }
    else { ready(); if (document.body && document.body.getAttribute('data-page') === 'category') categoryPicks(); if (/^\/games\/[^/]+\.html$/.test(p) || /^\/games\/[^/.]+$/.test(p)) gamepage(); }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
