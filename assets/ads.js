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
