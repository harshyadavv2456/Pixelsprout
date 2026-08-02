/*
 * Pixelsprout shared features: Recently Played, Favorites, Share button,
 * personalized homepage sections. Pure client-side (localStorage only) -
 * no accounts, no backend, no server changes needed. Works by detecting
 * page type at runtime and injecting UI where needed, so it can be added
 * to every page with a single <script> tag, no per-page template surgery.
 */

(function () {
  'use strict';

  const RECENT_KEY = 'pixelsprout_recent_v2';
  const FAVORITES_KEY = 'pixelsprout_favorites_v2';
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

    const gameShell = document.querySelector('.game-shell');
    let thumbnail = gameShell ? gameShell.dataset.thumbnail || '' : '';

    const game = { slug, title, category, thumbnail };

    if (!thumbnail) {
      // Fallback: the page wasn't patched with the data attribute yet -
      // look it up directly instead of silently falling back to the logo.
      fetch('../games-index.json')
        .then(r => r.json())
        .then(games => {
          const match = games.find(g => g.slug === slug);
          if (match && match.thumbnail) {
            game.thumbnail = match.thumbnail;
            recordRecentlyPlayed(game);
          }
        })
        .catch(() => {});
    }

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

  // ---------- Homepage enhancements: compact popup, not full sections ----------

  function buildModal(title, games) {
    const overlay = document.createElement('div');
    overlay.className = 'ps-modal-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;';

    const panel = document.createElement('div');
    panel.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);border-radius:12px;max-width:640px;width:100%;max-height:80vh;overflow-y:auto;padding:20px;';

    const header = document.createElement('div');
    header.style.cssText = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;';
    header.innerHTML = `<h3 style="font-family:'Press Start 2P',monospace;font-size:14px;color:var(--paper,#fff);margin:0;">${title}</h3>`;
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.textContent = '✕';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.style.cssText = 'background:none;border:none;color:var(--muted,#8a93b8);font-size:20px;cursor:pointer;padding:8px 12px;line-height:1;min-width:36px;min-height:36px;';
    const closeModal = () => { overlay.remove(); document.removeEventListener('keydown', escHandler); };
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeModal();
    });
    const escHandler = (e) => { if (e.key === 'Escape') closeModal(); };
    document.addEventListener('keydown', escHandler);
    header.appendChild(closeBtn);
    panel.appendChild(header);

    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = `Search ${title.toLowerCase()}...`;
    searchInput.style.cssText = 'width:100%;padding:8px 14px;border-radius:999px;border:1px solid var(--border,#2a3050);background:var(--bg,#0B0E1A);color:var(--paper,#fff);font-size:13px;margin-bottom:14px;';
    panel.appendChild(searchInput);

    const grid = document.createElement('div');
    grid.className = 'grid';
    grid.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;';
    grid.innerHTML = games.map(g => buildCardHTML(g, '')).join('\n');
    panel.appendChild(grid);

    // Self-healing: always re-check against current, correct data instead
    // of trusting whatever was cached whenever this entry was originally
    // saved. Fixes any stale/wrong thumbnails permanently, no matter when
    // they were recorded.
    fetch('games-index.json')
      .then(r => r.json())
      .then(freshGames => {
        const freshBySlug = {};
        freshGames.forEach(g => { freshBySlug[g.slug] = g; });
        let changed = false;
        games.forEach(g => {
          const fresh = freshBySlug[g.slug];
          if (fresh && fresh.thumbnail && fresh.thumbnail !== g.thumbnail) {
            g.thumbnail = fresh.thumbnail;
            changed = true;
          }
        });
        if (changed) {
          grid.innerHTML = games.map(g => buildCardHTML(g, '')).join('\n');
          // Persist the correction so it's fixed for next time too
          const key = title === 'Your Favorites' ? FAVORITES_KEY : RECENT_KEY;
          saveList(key, games);
        }
      })
      .catch(() => {});

    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim().toLowerCase();
      Array.from(grid.querySelectorAll('.card')).forEach(card => {
        const match = !q || (card.dataset.name && card.dataset.name.includes(q));
        card.style.display = match ? '' : 'none';
      });
    });

    overlay.appendChild(panel);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();
    });
    return overlay;
  }

  // ---------- Tool launcher popup (Cold Read / Gift File) ----------
  // Same overlay chrome as buildModal, but the body is an iframe pointing
  // at the standalone tool page instead of a game grid - these are
  // separate mini React apps (own dataset, own persistence), not part of
  // the game catalog.

  function buildToolModal(title, src) {
    const overlay = document.createElement('div');
    overlay.className = 'ps-modal-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;';

    const panel = document.createElement('div');
    panel.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);border-radius:12px;max-width:560px;width:100%;max-height:88vh;padding:0;display:flex;flex-direction:column;overflow:hidden;';

    const header = document.createElement('div');
    header.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:14px 18px;border-bottom:1px solid var(--border,#2a3050);flex-shrink:0;';
    header.innerHTML = `<h3 style="font-family:'Press Start 2P',monospace;font-size:13px;color:var(--paper,#fff);margin:0;">${title}</h3>`;
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.textContent = '✕';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.style.cssText = 'background:none;border:none;color:var(--muted,#8a93b8);font-size:20px;cursor:pointer;padding:8px 12px;line-height:1;min-width:36px;min-height:36px;';
    const closeModal = () => { overlay.remove(); document.removeEventListener('keydown', escHandler); };
    closeBtn.addEventListener('click', (e) => { e.stopPropagation(); closeModal(); });
    const escHandler = (e) => { if (e.key === 'Escape') closeModal(); };
    document.addEventListener('keydown', escHandler);
    header.appendChild(closeBtn);
    panel.appendChild(header);

    const iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.title = title;
    iframe.loading = 'lazy';
    iframe.style.cssText = 'border:0;width:100%;flex:1;min-height:70vh;background:#0B0B0F;';
    panel.appendChild(iframe);

    overlay.appendChild(panel);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
    return overlay;
  }

  function addToolLaunchers(bar) {
    // User-initiated only - small pill buttons, never an entry popup shown
    // on load (that pattern draws Google's intrusive-interstitial penalty).
    const giftBtn = document.createElement('button');
    giftBtn.textContent = '🎁 Stuck on a Gift?';
    giftBtn.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);color:var(--paper,#fff);padding:6px 14px;border-radius:999px;font-size:12px;cursor:pointer;';
    giftBtn.addEventListener('click', () => {
      document.body.appendChild(buildToolModal('Gift File', 'gift-file/'));
    });
    bar.appendChild(giftBtn);

    const coldReadBtn = document.createElement('button');
    coldReadBtn.textContent = '🕵️ Guess It';
    coldReadBtn.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);color:var(--paper,#fff);padding:6px 14px;border-radius:999px;font-size:12px;cursor:pointer;';
    coldReadBtn.addEventListener('click', () => {
      document.body.appendChild(buildToolModal('Cold Read', 'cold-read/'));
    });
    bar.appendChild(coldReadBtn);
  }

  function enhanceHomepage() {
    const recent = loadList(RECENT_KEY);
    const favorites = loadList(FAVORITES_KEY);

    // Small, unobtrusive buttons - don't push the catalog down, don't
    // dilute the "browse everything" homepage experience.
    const bar = document.createElement('div');
    bar.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;padding:8px 20px;flex-wrap:wrap;';

    // Tool launchers always show, independent of returning-visitor history.
    addToolLaunchers(bar);

    if (favorites.length > 0) {
      const favBtn = document.createElement('button');
      favBtn.textContent = `❤️ Favorites (${favorites.length})`;
      favBtn.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);color:var(--paper,#fff);padding:6px 14px;border-radius:999px;font-size:12px;cursor:pointer;';
      favBtn.addEventListener('click', () => {
        document.body.appendChild(buildModal('Your Favorites', loadList(FAVORITES_KEY)));
      });
      bar.appendChild(favBtn);
    }

    if (recent.length > 0) {
      const recentBtn = document.createElement('button');
      recentBtn.textContent = `🕐 Recently Played (${recent.length})`;
      recentBtn.style.cssText = 'background:var(--panel,#151a2e);border:1px solid var(--border,#2a3050);color:var(--paper,#fff);padding:6px 14px;border-radius:999px;font-size:12px;cursor:pointer;';
      recentBtn.addEventListener('click', () => {
        document.body.appendChild(buildModal('Recently Played', loadList(RECENT_KEY)));
      });
      bar.appendChild(recentBtn);
    }

    const header = document.querySelector('.site-header');
    if (header) {
      header.insertAdjacentElement('afterend', bar);
    } else {
      document.body.prepend(bar);
    }
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
