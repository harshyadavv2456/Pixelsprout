/*
 * Adsterra slot loader.
 * Banner units share one global (window.atOptions), so they are loaded
 * strictly one at a time: set atOptions, inject invoke.js into the slot,
 * wait until its iframe appears (or a timeout), then move to the next.
 * Slots load when they come within 200px of the viewport.
 */
(function () {
  'use strict';

  var BANNER_HOST = 'https://www.highperformanceformat.com/';
  var FILL_TIMEOUT = 4000;
  var EMPTY_AFTER = 12000;

  var queue = [];
  var busy = false;

  function hasIframe(el) {
    return !!el.querySelector('iframe');
  }

  function markEmptyLater(slot, host) {
    setTimeout(function () {
      if (!host.children.length || (!hasIframe(host) && !host.querySelector('a, img, div'))) {
        slot.classList.add('is-empty');
      }
    }, EMPTY_AFTER);
  }

  function pickSize(slot) {
    var minWidth = parseInt(slot.getAttribute('data-min-width') || '0', 10);
    if (!minWidth || window.matchMedia('(min-width: ' + minWidth + 'px)').matches) {
      return { key: slot.getAttribute('data-key'), w: +slot.getAttribute('data-w'), h: +slot.getAttribute('data-h') };
    }
    var altKey = slot.getAttribute('data-alt-key');
    if (altKey) {
      slot.classList.add('is-alt');
      return { key: altKey, w: +slot.getAttribute('data-alt-w'), h: +slot.getAttribute('data-alt-h') };
    }
    return null;
  }

  function loadBanner(slot, done) {
    var size = pickSize(slot);
    if (!size || !size.key) {
      slot.classList.add('is-skipped');
      done();
      return;
    }
    var host = slot.querySelector('.ad__slot') || slot;
    var finished = false;
    var observer;
    function finish() {
      if (finished) return;
      finished = true;
      if (observer) observer.disconnect();
      done();
    }

    window.atOptions = { key: size.key, format: 'iframe', height: size.h, width: size.w, params: {} };
    if ('MutationObserver' in window) {
      observer = new MutationObserver(function () {
        if (hasIframe(host)) setTimeout(finish, 150);
      });
      observer.observe(host, { childList: true, subtree: true });
    }
    var s = document.createElement('script');
    s.src = BANNER_HOST + size.key + '/invoke.js';
    s.onerror = finish;
    host.appendChild(s);
    setTimeout(finish, FILL_TIMEOUT);
    markEmptyLater(slot, host);
  }

  function pump() {
    if (busy || !queue.length) return;
    busy = true;
    var slot = queue.shift();
    loadBanner(slot, function () {
      busy = false;
      pump();
    });
  }

  function loadNative(slot) {
    var src = slot.getAttribute('data-src');
    if (!src) return;
    var s = document.createElement('script');
    s.async = true;
    s.setAttribute('data-cfasync', 'false');
    s.src = src;
    slot.insertBefore(s, slot.firstChild);
    var container = slot.querySelector('div[id^="container-"]');
    if (container) {
      setTimeout(function () {
        if (!container.children.length) slot.classList.add('is-empty');
      }, EMPTY_AFTER);
    }
  }

  function activate(slot) {
    if (slot.getAttribute('data-ad-state')) return;
    slot.setAttribute('data-ad-state', 'loading');
    var kind = slot.getAttribute('data-ad');
    if (kind === 'native') {
      loadNative(slot);
    } else if (kind === 'banner') {
      queue.push(slot);
      pump();
    }
  }

  function init() {
    var slots = Array.prototype.slice.call(document.querySelectorAll('.ad[data-ad]'));
    if (!slots.length) return;
    if (!('IntersectionObserver' in window)) {
      slots.forEach(activate);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          io.unobserve(entry.target);
          activate(entry.target);
        }
      });
    }, { rootMargin: '200px 0px' });
    slots.forEach(function (slot) { io.observe(slot); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* Pixel Sprout Originals: shelf + menu link, driven by /assets/originals.json */
(function () {
  function boot() {
    var labels = document.querySelectorAll('.rail__label');
    var label = null;
    for (var i = 0; i < labels.length; i++) {
      if (labels[i].textContent.replace(/\s+/g, ' ').trim() === 'Originals') label = labels[i];
    }
    if (label && !document.querySelector('a.rail__link[href="/originals/"]')) {
      var a = document.createElement('a');
      a.className = 'rail__link';
      a.href = '/originals/';
      a.setAttribute('aria-label', 'Pixel Sprout Originals');
      a.innerHTML = '<svg class="i" aria-hidden="true"><use href="/assets/icons.svg#sparkle"></use></svg><span class="rail__text">Pixel Sprout Originals</span>';
      label.insertAdjacentElement('afterend', a);
    }
    if (!document.body.classList.contains('home-page') || document.getElementById('pixel-sprout-originals')) return;
    fetch('/assets/originals.json').then(function (r) { return r.ok ? r.json() : []; }).then(function (games) {
      if (!games || !games.length || document.getElementById('pixel-sprout-originals')) return;
      var cards = games.map(function (g) {
        var title = String(g.title || '');
        var slug = String(g.slug || '');
        var cat = String(g.category || '');
        var thumb = String(g.thumbnail || '');
        return '<a class="card" href="/games/' + slug + '.html" data-name="' + title.toLowerCase() + '">' +
          '<span class="card__media"><img src="' + thumb + '" alt="' + title + '" width="320" height="320" loading="lazy" decoding="async"></span>' +
          '<span class="card__title">' + title + '</span>' +
          (cat ? '<span class="card__meta">' + cat + '</span>' : '') +
          '</a>';
      }).join('');
      var n = games.length;
      var section = document.createElement('section');
      section.className = 'shelf shelf--originals';
      section.id = 'pixel-sprout-originals';
      section.setAttribute('aria-labelledby', 'pixel-sprout-originals-title');
      section.innerHTML = '<div class="shelf__head"><h2 class="shelf__title" id="pixel-sprout-originals-title">Pixel Sprout Originals</h2>' +
        '<span class="shelf__count">' + n + (n === 1 ? ' game' : ' games') + '</span>' +
        '<span class="shelf__spacer"></span><a class="shelf__more" href="/originals/">See all</a></div>' +
        '<div class="shelf__track" data-shelf-track>' + cards + '</div>';
      var anchor = document.querySelector('.hero') || document.querySelector('.home-intro');
      if (anchor) anchor.insertAdjacentElement('afterend', section);
    }).catch(function () {});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
