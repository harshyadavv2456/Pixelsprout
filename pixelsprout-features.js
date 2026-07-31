/*
 * Pixelsprout shared features: Recently Played, Favorites, Share button,
 * personalized homepage sections. Pure client-side (localStorage only) -
 * no accounts, no backend, no server changes needed. Works by detecting
 * page type at runtime and injecting UI where needed, so it can be added
 * to every page with a single <script> tag, no per-page template surgery.
 */

(function () {
  'use strict';

  const RECENT_KEY = 'pixelsprout_recent';
  const FAVORITES_KEY = 'pixelsprout_favorites';
  const MAX_RECENT = 12;

  // ---------- Pure logic (storage helpers) ----------

  function loadList(key) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveList(key, list) {
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch (e) {
      // localStorage unavailable (private browsing, quota, etc.) - fail silently,
      // the site works fine without these features, they're pure enhancement.
    }
  }

  function recordRecentlyPlayed(game) {
    let list = loadList(RECENT_KEY);
    list = list.filter(g => g.slug !== game.slug);
    list.unshift(game);
    list = list.slice(0, MAX_RECENT);
    saveList(RECENT_KEY, list);
  }

  function isFavorite(slug) {
    return loadList(FAVORITES_KEY).some(g => g.slug === slug);
  }

  function toggleFavorite(game) {
    let list = loadList(FAVORITES_KEY);
    const exists = list.some(g => g.slug === game.slug);
    if (exists) {
      list = list.filter(g => g.slug !== game.slug);
    } else {
      list.unshift(game);
    }
    saveList(FAVORITES_KEY, list);
    return !exists;
  }

  // ---------- Card rendering helper ----------

  function buildCardHTML(game, basePath) {
    const thumb = game.thumbnail || basePath + 'assets/logo-icon.png';
    return `<a class="card" href="${basePath}games/${game.slug}.html" data-name="${(game.title || '').toLowerCase()}">
      <span class="icon-tile gold" style="padding:0;overflow:hidden;">
        <img src="${thumb}" alt="" style="width:100%;height:100%;object-fit:cover;border-radius:9px;" loading="lazy">
      </span>
      <div class="card-body"><h3>${game.title}</h3></div>
    </a>`;
  }

  // ---------- Game page enhancements ----------

  function enhanceGamePage() {
    const titleEl = document.querySelector('.game-title');
    const metaEl = document.querySelector('.game-meta');
    if (!titleEl) return;

    const title = titleEl.textContent.trim();
    const category = metaEl ? metaEl.textContent.trim() : '';
    const slugMatch = window.location.pathname.match(/\/games\/([^/]+)\.html/);
    const slug = slugMatch ? slugMatch[1] : '';
    if (!slug) return;

    const thumbImg = document.querySelector('.similar-card img');
    const thumbnail = thumbImg ? thumbImg.src : '';

    const game = { slug, title, category, thumbnail };
    recordRecentlyPlayed(game);

    // Inject Favorite + Share buttons next to the fullscreen button
    const fullscreenBtn = document.querySelector('.fullscreen-btn');
    if (fullscreenBtn && !document.querySelector('.favorite-btn')) {
      const favBtn = document.createElement('button');
      favBtn.className = 'action favorite-btn';
      favBtn.style.marginLeft = '8px';
      const setFavLabel = () => {
        favBtn.textContent = isFavorite(slug) ? '💔 Remove Favorite' : '❤️ Favorite';
      };
      setFavLabel();
      favBtn.addEventListener('click', () => {
        toggleFavorite(game);
        setFavLabel();
      });

      const shareBtn = document.createElement('button');
      shareBtn.className = 'action share-btn';
      shareBtn.style.marginLeft = '8px';
      shareBtn.textContent = '🔗 Share';
      shareBtn.addEventListener('click', async () => {
        const url = window.location.href;
        if (navigator.share) {
          try { await navigator.share({ title: title, url: url }); } catch (e) {}
        } else {
          try {
            await navigator.clipboard.writeText(url);
            shareBtn.textContent = '✅ Link Copied';
            setTimeout(() => { shareBtn.textContent = '🔗 Share'; }, 2000);
          } catch (e) {}
        }
      });

      fullscreenBtn.insertAdjacentElement('afterend', shareBtn);
      fullscreenBtn.insertAdjacentElement('afterend', favBtn);
    }
  }

  // ---------- Homepage enhancements ----------

  function enhanceHomepage() {
    const main = document.querySelector('main') || document.querySelector('.wrap');
    if (!main) return;

    const recent = loadList(RECENT_KEY);
    const favorites = loadList(FAVORITES_KEY);
    if (recent.length === 0 && favorites.length === 0) return; // new visitor, nothing to show

    const sections = [];

    if (favorites.length > 0) {
      sections.push(`
        <div class="category gold" data-section>
          <span class="bar"></span><h2>Your Favorites</h2>
          <span class="count">${favorites.length} game${favorites.length === 1 ? '' : 's'}</span>
        </div>
        <div class="grid" data-grid>
          ${favorites.slice(0, 12).map(g => buildCardHTML(g, '')).join('\n')}
        </div>
      `);
    }

    if (recent.length > 0) {
      sections.push(`
        <div class="category teal" data-section>
          <span class="bar"></span><h2>Recently Played</h2>
          <span class="count">${recent.length} game${recent.length === 1 ? '' : 's'}</span>
        </div>
        <div class="grid" data-grid>
          ${recent.map(g => buildCardHTML(g, '')).join('\n')}
        </div>
      `);
    }

    const container = document.createElement('div');
    container.innerHTML = sections.join('\n');
    main.prepend(container);
  }

  // ---------- Run on page load ----------

  document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.game-shell')) {
      enhanceGamePage();
    } else {
      enhanceHomepage();
    }
  });
})();
