/*
 * Pixelsprout site behaviour: search palette, menu sheet, favorites and
 * recently played (localStorage only), game page actions, shelves and the
 * category catalog controls. Loaded with `defer` on every page.
 */
(function () {
  'use strict';

  var RECENT_KEY = 'pixelsprout_recent_v2';
  var FAVORITES_KEY = 'pixelsprout_favorites_v2';
  var MAX_RECENT = 12;
  var ICONS = '/assets/icons.svg#';
  var TOOLS = [
    { slug: 'cold-read', title: 'Cold Read', category: 'Pixelsprout original', thumbnail: '/assets/cold-read-logo.jpg', href: '/cold-read/' },
    { slug: 'gift-file', title: 'Guess It Box', category: 'Pixelsprout original', thumbnail: '/assets/gift-file-logo.jpg', href: '/gift-file/' }
  ];

  // ---------- helpers ----------

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function escapeHTML(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function icon(name, cls) {
    return '<svg class="' + (cls || 'i') + '" aria-hidden="true"><use href="' + ICONS + name + '"></use></svg>';
  }

  function prettyGenre(c) {
    if (!c) return '';
    var map = { 'First-Person-Shooter': 'First-Person Shooter', 'Games-For-Girls': 'Games for Girls', 'Two-Player': 'Two Player', '2 Player': 'Two Player', 'Hyper-Casual': 'Hypercasual', 'Match-3': 'Match 3', 'Io': '.io', '.Io': '.io' };
    if (map[c]) return map[c];
    return c.split(/[-\s]+/).map(function (w, i) {
      if (i && /^(for|and|of|the)$/i.test(w)) return w.toLowerCase();
      if (w === w.toUpperCase() || /^\d/.test(w)) return w;
      return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
    }).join(' ');
  }

  function loadList(key) {
    try { var raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : []; } catch (e) { return []; }
  }
  function saveList(key, list) {
    try { localStorage.setItem(key, JSON.stringify(list)); } catch (e) { /* storage unavailable */ }
    updateCounts();
  }

  function hrefFor(game) {
    if (game.href) return game.href;
    if (game.slug === 'cold-read' || game.slug === 'gift-file') return '/' + game.slug + '/';
    return '/games/' + game.slug + '.html';
  }

  function cardHTML(game, showMeta) {
    var thumb = game.thumbnail && String(game.thumbnail).trim() ? game.thumbnail : '/assets/logo-icon.png';
    if (thumb.indexOf('../') === 0) thumb = thumb.slice(2);
    return '<a class="card" href="' + escapeHTML(hrefFor(game)) + '" data-name="' + escapeHTML((game.title || '').toLowerCase()) + '">' +
      '<span class="card__media"><img src="' + escapeHTML(thumb) + '" alt="' + escapeHTML(game.title) + '" width="320" height="320" loading="lazy" decoding="async"></span>' +
      '<span class="card__title">' + escapeHTML(game.title) + '</span>' +
      (showMeta !== false && game.category ? '<span class="card__meta">' + escapeHTML(prettyGenre(game.category)) + '</span>' : '') +
      '</a>';
  }

  function track(name, params) {
    if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
  }

  var catalogPromise = null;
  function loadCatalog() {
    if (!catalogPromise) {
      catalogPromise = fetch('/games-index.json')
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (list) {
          var seen = {};
          return list.filter(function (g) {
            if (!g || !g.slug || seen[g.slug]) return false;
            seen[g.slug] = true;
            return true;
          });
        })
        .catch(function () { catalogPromise = null; return []; });
    }
    return catalogPromise;
  }

  // ---------- toast ----------

  var toastEl, toastTimer;
  function toast(message) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      toastEl.setAttribute('role', 'status');
      toastEl.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastEl);
    }
    toastEl.innerHTML = icon('check', 'i i--sm') + '<span>' + escapeHTML(message) + '</span>';
    requestAnimationFrame(function () { toastEl.classList.add('is-visible'); });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-visible'); }, 2200);
  }

  // ---------- focus trap / dialogs ----------

  var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

  function trapFocus(container, onClose) {
    var previous = document.activeElement;
    function onKey(e) {
      if (e.key === 'Escape') { e.preventDefault(); close(); return; }
      if (e.key !== 'Tab') return;
      var items = $$(FOCUSABLE, container).filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
      if (!items.length) return;
      var first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    function close() {
      document.removeEventListener('keydown', onKey, true);
      onClose();
      if (previous && previous.focus) previous.focus();
    }
    document.addEventListener('keydown', onKey, true);
    return close;
  }

  function openDialog(opts) {
    var overlay = document.createElement('div');
    overlay.className = 'overlay';
    overlay.innerHTML =
      '<div class="dialog ' + (opts.wide ? 'dialog--wide' : '') + '" role="dialog" aria-modal="true" aria-labelledby="dlg-title">' +
      (opts.headHTML || ('<div class="dialog__head"><h2 class="dialog__title" id="dlg-title">' + escapeHTML(opts.title) + '</h2>' +
        (opts.actionsHTML || '') +
        '<button class="icon-btn" type="button" data-dialog-close aria-label="Close">' + icon('x') + '</button></div>')) +
      (opts.bodyHTML || '') +
      '</div>';
    document.body.appendChild(overlay);
    document.body.classList.add('is-locked');
    var dialog = overlay.firstChild;
    var close = trapFocus(dialog, function () {
      overlay.remove();
      if (!$('.overlay') && !$('.rail.is-open')) document.body.classList.remove('is-locked');
      if (opts.onClose) opts.onClose();
    });
    overlay.addEventListener('mousedown', function (e) { if (e.target === overlay) close(); });
    $$('[data-dialog-close]', overlay).forEach(function (b) { b.addEventListener('click', close); });
    var focusTarget = $(opts.focus || '[data-dialog-close]', overlay);
    if (focusTarget) focusTarget.focus();
    return { overlay: overlay, dialog: dialog, close: close };
  }

  // ---------- counts ----------

  function updateCounts() {
    var counts = { favorites: loadList(FAVORITES_KEY).length, recent: loadList(RECENT_KEY).length };
    $$('[data-count]').forEach(function (el) {
      var n = counts[el.getAttribute('data-count')] || 0;
      el.textContent = n ? String(n) : '';
      if (el.classList.contains('count-badge')) el.hidden = !n;
    });
  }

  // ---------- favorites / recent panels ----------

  function openLibrary(kind) {
    var isFav = kind === 'favorites';
    var key = isFav ? FAVORITES_KEY : RECENT_KEY;
    var list = loadList(key);
    var body = list.length
      ? '<div class="dialog__body"><div class="grid">' + list.map(function (g) { return cardHTML(g); }).join('') + '</div></div>'
      : '<div class="dialog__body"><p class="dialog__empty">' + (isFav
        ? 'No favorites yet. Tap the heart under any game to keep it here.'
        : 'Nothing here yet. Games you play will show up here so you can jump back in.') + '</p></div>';
    var actions = list.length ? '<button class="btn btn--quiet" type="button" data-clear>Clear</button>' : '';
    var d = openDialog({ title: isFav ? 'Favorites' : 'Recently played', bodyHTML: body, actionsHTML: actions, wide: true });
    var clear = $('[data-clear]', d.dialog);
    if (clear) clear.addEventListener('click', function () {
      saveList(key, []);
      d.close();
      toast(isFav ? 'Favorites cleared' : 'History cleared');
    });
  }

  // ---------- search palette ----------

  function normalize(s) {
    return String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function score(game, q, words) {
    var t = game._n;
    if (t === q) return 100;
    var s = 0;
    if (t.indexOf(q) === 0) s += 60;
    else if ((' ' + t).indexOf(' ' + q) >= 0) s += 40;
    else if (t.indexOf(q) >= 0) s += 25;
    else {
      for (var i = 0; i < words.length; i++) {
        if (t.indexOf(words[i]) < 0 && game._g.indexOf(words[i]) < 0) return 0;
      }
      s += 10;
    }
    if (game._g.indexOf(q) >= 0) s += 5;
    return s - Math.min(t.length, 40) / 10;
  }

  function highlight(title, q) {
    var safe = escapeHTML(title);
    if (!q) return safe;
    var idx = title.toLowerCase().indexOf(q);
    if (idx < 0) return safe;
    return escapeHTML(title.slice(0, idx)) + '<mark>' + escapeHTML(title.slice(idx, idx + q.length)) + '</mark>' + escapeHTML(title.slice(idx + q.length));
  }

  var paletteOpen = false;
  function openPalette(initial) {
    if (paletteOpen) return;
    paletteOpen = true;
    var head =
      '<div class="palette__field">' + icon('search') +
      '<input type="search" placeholder="Search games" aria-label="Search games" autocomplete="off" spellcheck="false" ' +
      'role="combobox" aria-expanded="true" aria-controls="palette-list" aria-autocomplete="list">' +
      '<button class="icon-btn icon-btn--sm" type="button" data-dialog-close aria-label="Close search">' + icon('x', 'i i--sm') + '</button></div>';
    var body =
      '<ul class="palette__list" id="palette-list" role="listbox" aria-label="Results"></ul>' +
      '<div class="palette__foot"><span><span class="kbd">↑</span> <span class="kbd">↓</span> to move</span><span><span class="kbd">↵</span> to open</span><span><span class="kbd">esc</span> to close</span></div>';
    var d = openDialog({ headHTML: head, bodyHTML: body, focus: '.palette__field input', onClose: function () { paletteOpen = false; } });
    d.dialog.classList.add('palette');
    d.dialog.setAttribute('aria-label', 'Search games');
    d.dialog.removeAttribute('aria-labelledby');
    var input = $('input', d.dialog);
    var listEl = $('.palette__list', d.dialog);
    var items = [];
    var active = -1;
    var catalog = null;
    var searchTimer;

    function setActive(i) {
      var opts = $$('.palette__item', listEl);
      if (!opts.length) { active = -1; input.removeAttribute('aria-activedescendant'); return; }
      active = (i + opts.length) % opts.length;
      opts.forEach(function (o, idx) { o.setAttribute('aria-selected', idx === active ? 'true' : 'false'); });
      input.setAttribute('aria-activedescendant', opts[active].id);
      opts[active].scrollIntoView({ block: 'nearest' });
    }

    function itemHTML(g, i, q) {
      var thumb = g.thumbnail && String(g.thumbnail).trim() ? g.thumbnail : '/assets/logo-icon.png';
      return '<li class="palette__item" role="option" id="pal-' + i + '" aria-selected="false">' +
        '<a href="' + escapeHTML(hrefFor(g)) + '" tabindex="-1"><img src="' + escapeHTML(thumb) + '" alt="" width="40" height="40" loading="lazy" decoding="async">' +
        '<span class="palette__text"><b>' + highlight(g.title, q) + '</b><small>' + escapeHTML(prettyGenre(g.category)) + '</small></span></a></li>';
    }

    function render() {
      var raw = input.value;
      var q = normalize(raw);
      var html = '';
      items = [];
      if (!q) {
        var recent = loadList(RECENT_KEY).slice(0, 6);
        if (recent.length) {
          html += '<li class="palette__group" role="presentation">Recently played</li>';
          recent.forEach(function (g) { items.push(g); html += itemHTML(g, items.length - 1, ''); });
        }
        html += '<li class="palette__group" role="presentation">Originals</li>';
        TOOLS.forEach(function (g) { items.push(g); html += itemHTML(g, items.length - 1, ''); });
        if (!catalog) html += '<li class="palette__status" role="presentation">Loading the catalog…</li>';
      } else if (!catalog) {
        html = '<li class="palette__status" role="presentation">Loading the catalog…</li>';
      } else {
        var words = q.split(' ');
        var results = [];
        var pool = TOOLS.map(function (t) { return Object.assign({ _n: normalize(t.title), _g: 'original' }, t); }).concat(catalog);
        for (var i = 0; i < pool.length; i++) {
          var sc = score(pool[i], q, words);
          if (sc > 0) results.push([sc, pool[i]]);
        }
        results.sort(function (a, b) { return b[0] - a[0]; });
        results = results.slice(0, 40);
        if (!results.length) {
          html = '<li class="palette__status" role="presentation">No games match “' + escapeHTML(raw.trim()) + '”.</li>';
        } else {
          html += '<li class="palette__group" role="presentation">' + results.length + (results.length === 40 ? '+' : '') + ' results</li>';
          var lower = raw.trim().toLowerCase();
          results.forEach(function (r) { items.push(r[1]); html += itemHTML(r[1], items.length - 1, lower); });
        }
      }
      listEl.innerHTML = html;
      setActive(0);
    }

    input.addEventListener('input', function () {
      render();
      clearTimeout(searchTimer);
      var v = input.value.trim();
      if (v.length > 2) searchTimer = setTimeout(function () { track('search_used', { search_term: v }); }, 1000);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Enter') {
        var opt = $$('.palette__item', listEl)[active];
        if (opt) { e.preventDefault(); window.location.href = $('a', opt).getAttribute('href'); }
      }
    });
    listEl.addEventListener('mousemove', function (e) {
      var li = e.target.closest && e.target.closest('.palette__item');
      if (!li) return;
      var idx = $$('.palette__item', listEl).indexOf(li);
      if (idx !== active) setActive(idx);
    });

    if (initial) input.value = initial;
    render();
    loadCatalog().then(function (list) {
      catalog = list.map(function (g) {
        return Object.assign({ _n: normalize(g.title), _g: normalize(g.category) }, g);
      });
      if (paletteOpen) render();
    });
  }

  // ---------- menu sheet (mobile rail) ----------

  function initMenu() {
    var rail = $('#rail');
    var scrim = $('[data-scrim]');
    var openBtn = $('[data-menu-open]');
    if (!rail || !openBtn) return;
    var release = null;
    var mq = window.matchMedia('(max-width: 767px)');

    function close() {
      if (!rail.classList.contains('is-open')) return;
      rail.classList.remove('is-open');
      if (scrim) scrim.classList.remove('is-open');
      openBtn.setAttribute('aria-expanded', 'false');
      if (!$('.overlay')) document.body.classList.remove('is-locked');
      rail.removeAttribute('role');
      rail.removeAttribute('aria-modal');
    }
    function open() {
      rail.classList.add('is-open');
      if (scrim) scrim.classList.add('is-open');
      openBtn.setAttribute('aria-expanded', 'true');
      document.body.classList.add('is-locked');
      rail.setAttribute('role', 'dialog');
      rail.setAttribute('aria-modal', 'true');
      release = trapFocus(rail, function () { release = null; close(); });
      var first = $('[data-menu-close]', rail);
      if (first) first.focus();
    }
    openBtn.addEventListener('click', open);
    $$('[data-menu-close]', rail).forEach(function (b) { b.addEventListener('click', function () { if (release) release(); else close(); }); });
    if (scrim) scrim.addEventListener('click', function () { if (release) release(); else close(); });
    $$('a', rail).forEach(function (a) { a.addEventListener('click', function () { if (release) release(); else close(); }); });
    $$('[data-open-panel]', rail).forEach(function (b) { b.addEventListener('click', function () { if (mq.matches && release) release(); }); });
    var onChange = function () { if (!mq.matches && release) release(); };
    if (mq.addEventListener) mq.addEventListener('change', onChange); else if (mq.addListener) mq.addListener(onChange);
  }

  // ---------- shelves ----------

  function initShelves() {
    $$('.shelf').forEach(function (shelf) {
      var track = $('[data-shelf-track]', shelf);
      var prev = $('[data-shelf-prev]', shelf);
      var next = $('[data-shelf-next]', shelf);
      if (!track || !prev || !next) return;
      function update() {
        var max = track.scrollWidth - track.clientWidth - 2;
        prev.disabled = track.scrollLeft <= 2;
        next.disabled = track.scrollLeft >= max;
        var nav = prev.parentNode;
        if (nav) nav.style.visibility = track.scrollWidth > track.clientWidth + 4 ? '' : 'hidden';
      }
      function go(dir) {
        track.scrollBy({ left: dir * Math.max(track.clientWidth * 0.85, 200), behavior: 'smooth' });
      }
      prev.addEventListener('click', function () { go(-1); });
      next.addEventListener('click', function () { go(1); });
      track.addEventListener('scroll', function () { window.requestAnimationFrame(update); }, { passive: true });
      window.addEventListener('resize', update);
      update();
    });
  }

  // ---------- homepage ----------

  function initHome() {
    var section = $('#continue-playing');
    var track = $('#continue-playing-track');
    if (!section || !track) return;
    var recent = loadList(RECENT_KEY);
    if (!recent.length) return;
    track.innerHTML = recent.slice(0, 12).map(function (g) { return cardHTML(g); }).join('');
    section.hidden = false;
    initShelfFor(section);
  }

  function initShelfFor(section) {
    var prev = $('[data-shelf-prev]', section);
    if (prev) prev.parentNode.style.visibility = '';
    var track = $('[data-shelf-track]', section);
    if (track) track.dispatchEvent(new Event('scroll'));
  }

  // ---------- game pages ----------

  function gameContext() {
    var body = document.body;
    if (body.getAttribute('data-page') === 'game') {
      return {
        slug: body.getAttribute('data-slug'),
        title: body.getAttribute('data-title'),
        category: body.getAttribute('data-genre') || '',
        thumbnail: body.getAttribute('data-thumbnail') || '',
        isTool: false
      };
    }
    var titleEl = $('.game-title');
    if (!titleEl) return null;
    var m = window.location.pathname.match(/\/games\/([^/]+)\.html/);
    var toolSlug = body.getAttribute('data-tool-slug') || '';
    var slug = m ? m[1] : toolSlug;
    if (!slug) return null;
    var shell = $('.game-shell');
    var metaEl = $('.game-meta');
    var thumb = shell ? shell.getAttribute('data-thumbnail') || '' : '';
    if (thumb.indexOf('../') === 0) thumb = thumb.slice(2);
    return {
      slug: slug,
      title: titleEl.textContent.trim(),
      category: toolSlug ? 'Pixelsprout original' : (metaEl ? metaEl.textContent.trim() : ''),
      thumbnail: thumb,
      isTool: !m
    };
  }

  function initGamePage() {
    var ctx = gameContext();
    if (!ctx) return;
    var game = { slug: ctx.slug, title: ctx.title, category: ctx.category, thumbnail: ctx.thumbnail };

    var recent = loadList(RECENT_KEY).filter(function (g) { return g.slug !== game.slug; });
    recent.unshift(game);
    saveList(RECENT_KEY, recent.slice(0, MAX_RECENT));

    if (!ctx.isTool) {
      fetch('/api/track-view', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: game.slug })
      }).catch(function () {});
    }

    var favBtn = $('[data-fav]');
    var shareBtn = $('[data-share]');
    if (!favBtn) {
      var legacyFs = $('.fullscreen-btn');
      if (legacyFs) {
        favBtn = document.createElement('button');
        favBtn.type = 'button';
        favBtn.className = 'action';
        favBtn.setAttribute('data-fav', '');
        shareBtn = document.createElement('button');
        shareBtn.type = 'button';
        shareBtn.className = 'action';
        shareBtn.setAttribute('data-share', '');
        shareBtn.innerHTML = icon('share', 'i i--sm') + '<span>Share</span>';
        var row = document.createElement('div');
        row.className = 'legacy-actions';
        legacyFs.parentNode.insertBefore(row, legacyFs);
        row.appendChild(legacyFs);
        row.appendChild(favBtn);
        row.appendChild(shareBtn);
      }
    }

    function isFav() { return loadList(FAVORITES_KEY).some(function (g) { return g.slug === game.slug; }); }
    function paintFav() {
      if (!favBtn) return;
      var on = isFav();
      favBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
      favBtn.setAttribute('aria-label', on ? 'Remove from favorites' : 'Add to favorites');
      favBtn.title = on ? 'Remove from favorites' : 'Add to favorites';
      if (favBtn.classList.contains('action')) {
        favBtn.innerHTML = icon('heart', 'i i--sm') + '<span>' + (on ? 'Saved' : 'Favorite') + '</span>';
      }
    }
    if (favBtn) {
      paintFav();
      favBtn.addEventListener('click', function () {
        var list = loadList(FAVORITES_KEY);
        var on = list.some(function (g) { return g.slug === game.slug; });
        list = on ? list.filter(function (g) { return g.slug !== game.slug; }) : [game].concat(list);
        saveList(FAVORITES_KEY, list);
        paintFav();
        toast(on ? 'Removed from favorites' : 'Saved to favorites');
        track(on ? 'favorite_remove' : 'favorite_add', { game_title: game.title });
      });
    }
    if (shareBtn) {
      shareBtn.addEventListener('click', function () {
        var url = window.location.href.split('#')[0];
        if (navigator.share && window.matchMedia('(pointer: coarse)').matches) {
          navigator.share({ title: game.title, url: url }).catch(function () {});
          track('share_click', { game_title: game.title, method: 'native' });
          return;
        }
        var done = function () { toast('Link copied'); track('share_click', { game_title: game.title, method: 'copy' }); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(done).catch(function () { fallbackCopy(url); done(); });
        } else {
          fallbackCopy(url);
          done();
        }
      });
    }

    if (document.body.getAttribute('data-page') !== 'game' && !ctx.isTool) {
      legacyGuides(game.slug);
    }
  }

  function fallbackCopy(value) {
    var ta = document.createElement('textarea');
    ta.value = value;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    ta.remove();
  }

  function legacyGuides(slug) {
    var frame = $('.game-board-frame');
    if (!frame) return;
    fetch('/guides-index.json')
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (idx) {
        var pages = idx[slug];
        if (!pages) return;
        var labels = { tips: 'Tips & strategy', controls: 'Controls', 'beginner-guide': "Beginner's guide", faq: 'FAQ', similar: 'Games like this' };
        var section = document.createElement('section');
        section.style.alignSelf = 'stretch';
        section.innerHTML = '<h2 class="block__title">Guides for this game</h2><ul class="link-list">' +
          Object.keys(pages).map(function (k) {
            return '<li><a href="' + escapeHTML(pages[k]) + '">' + icon('book') + '<span class="link-list__label">' + escapeHTML(labels[k] || k) + '</span></a></li>';
          }).join('') + '</ul>';
        frame.appendChild(section);
      })
      .catch(function () {});
  }

  // ---------- category catalog ----------

  function initCatalog() {
    var grid = $('[data-catalog]');
    if (!grid) return;
    var cards = $$('.card', grid);
    var pageSize = parseInt(grid.getAttribute('data-page-size') || '60', 10);
    var limit = pageSize;
    var filterInput = $('[data-catalog-filter]');
    var countEl = $('[data-catalog-count]');
    var emptyEl = $('[data-catalog-empty]');
    var moreWrap = $('.load-more');
    var moreBtn = $('[data-load-more]');
    var sortBtns = $$('[data-sort]');
    var total = cards.length;

    function apply() {
      var q = filterInput ? normalize(filterInput.value) : '';
      var shown = 0, matched = 0;
      cards.forEach(function (card) {
        var match = !q || normalize(card.getAttribute('data-name')).indexOf(q) >= 0;
        if (match) matched++;
        var visible = match && (q ? true : matched <= limit);
        card.classList.toggle('is-more', !visible);
        if (visible) shown++;
      });
      if (countEl) countEl.textContent = q ? matched + ' of ' + total + ' games' : total + ' games';
      if (emptyEl) emptyEl.hidden = matched !== 0;
      if (moreWrap) moreWrap.hidden = !!q || matched <= limit;
    }

    function sortBy(mode) {
      var sorted = cards.slice();
      if (mode === 'az') {
        sorted.sort(function (a, b) { return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name')); });
      } else if (mode === 'new') {
        sorted.sort(function (a, b) { return +(b.getAttribute('data-n') || b.getAttribute('data-i')) - +(a.getAttribute('data-n') || a.getAttribute('data-i')); });
      } else {
        sorted.sort(function (a, b) { return +a.getAttribute('data-i') - +b.getAttribute('data-i'); });
      }
      var frag = document.createDocumentFragment();
      sorted.forEach(function (c) { frag.appendChild(c); });
      grid.appendChild(frag);
      cards = sorted;
      sortBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-sort') === mode ? 'true' : 'false'); });
      limit = pageSize;
      apply();
    }

    if (filterInput) {
      var t;
      filterInput.addEventListener('input', function () { clearTimeout(t); t = setTimeout(apply, 60); });
    }
    if (moreBtn) moreBtn.addEventListener('click', function () {
      var firstNew = cards.filter(function (c) { return c.classList.contains('is-more'); })[0];
      limit += pageSize;
      apply();
      if (firstNew) { var a = firstNew; setTimeout(function () { a.focus({ preventScroll: true }); }, 0); }
    });
    sortBtns.forEach(function (b) { b.addEventListener('click', function () { sortBy(b.getAttribute('data-sort')); }); });
  }

  // ---------- global wiring ----------

  function isTyping(el) {
    if (!el) return false;
    var tag = el.tagName;
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable;
  }

  function init() {
    updateCounts();
    initMenu();
    initShelves();
    initHome();
    initGamePage();
    initCatalog();

    document.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target : null;
      if (!t) return;
      var searchBtn = t.closest('[data-search-open]');
      if (searchBtn) { e.preventDefault(); openPalette(); return; }
      var panelBtn = t.closest('[data-open-panel]');
      if (panelBtn) { e.preventDefault(); openLibrary(panelBtn.getAttribute('data-open-panel')); }
    });

    document.addEventListener('keydown', function (e) {
      if (e.defaultPrevented) return;
      var k = e.key;
      if ((k === 'k' || k === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); openPalette(); return; }
      if (k === '/' && !isTyping(document.activeElement) && !e.metaKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        openPalette();
      }
    });

    window.addEventListener('storage', function (e) {
      if (e.key === RECENT_KEY || e.key === FAVORITES_KEY) updateCounts();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
