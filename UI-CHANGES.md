# UI rebuild — what changed

Branch `ui-premium`. Editorial, restrained dark design; one shell on every
page; ad slots rebuilt so every unit renders and fits.

## Design system

- `styles.css` — rewritten. Tokens live in `:root` (colors, type scale,
  spacing, radii, motion). Fonts: Bricolage Grotesque (display), Geist (UI),
  Geist Mono (meta). Press Start 2P is used only for the PIXELSPROUT wordmark
  (loaded with `&text=PIXELSPROUT`, so it costs a few hundred bytes).
- `assets/icons.svg` — one stroke-icon sprite (UI + genre icons). Emoji are
  gone from the UI.
- Legacy variable names (`--teal`, `--muted`, `--panel`…) are aliased to the
  new tokens so tool pages and built-in games keep working.

## Which script owns which page

| Pages | Owner |
|---|---|
| Shared head, top bar, rail, footer, cards, ad slots | `site_shell.py` |
| Page templates (game, guide, collection, legal, category, home, A–Z, guides hub) + extractors | `site_pages.py` |
| `index.html`, `all-games/index.html` | `generate-homepage.py` (never hand-edit) |
| `/{genre}/index.html` | `generate-category-pages.py` |
| `games/*.html` (new games) | `auto-add-*.py`, `bulk-add-*.py` via `site_pages.render_game_page` |
| `guides/*`, `guides/index.html` | `content-engine/generate_guides.py` via `page_renderer.py` |
| `games-like/*` | `content-engine/generate_collections.py` via `page_renderer.py` |
| Everything already on disk | `migrate-ui.py` (idempotent re-render) |
| Homepage hero picks | `featured.json` (one per day, in order — edit freely) |

The auto-add scripts no longer regex-patch `index.html`. They add the game
to `games-index.json`, render its page, then rebuild the homepage and A–Z
page. That removes the bug that pushed cards outside their grid.

## Daily run

GitHub Actions:
- `refresh-popular-games.yml` now also runs `generate-homepage.py` and
  commits `index.html` + `all-games/index.html`, so "Popular now" follows the
  real view ranking once `popular-games.json` has data (until then it uses
  the curated fallback list).
- `auto-add-games.yml` has a new step: `python generate-homepage.py`.

Windows Task Scheduler: `run-daily-automation.bat` now runs
`python generate-homepage.py` after the category pages
(`setup-task-scheduler.md` updated to match).

`content-engine/generate_guides.py` re-renders a game page after writing its
guides, so the game page links to them.

## Ads

- One component: `.ad` + `.ad--rect | --leader | --native | --adsense`,
  small "Advertisement"/"Sponsored" label, reserved height, never wider than
  its container.
- `assets/ads.js` loads Adsterra banners **one at a time** (they share the
  global `atOptions`), only when a slot is within 200px of the viewport. The
  728×90 is skipped below 768px (on home/category pages it swaps to the
  300×250). Unfilled Adsterra slots collapse after 12s.
- Adsterra's `invoke.js` places its iframe next to `document.currentScript`
  (no `document.write`), so dynamic injection works — no static fallback
  was needed.
- Native unit fixed: its container is full width, so the widget has room.
- Unfilled AdSense `<ins>` (and its wrapper) are hidden via CSS; the AdSense
  code is unchanged.
- Placements: game page — 300×250 in a right rail at ≥1280px (below the game
  on smaller screens), native below the description, 728×90 above "More like
  this" (desktop only), plus the two AdSense slots. Home and category pages —
  one native + one banner between shelves/rows. Guides — 3 units total (was
  5). Nothing sticky, no popunders, no interstitials.

## Data fixes done by the migration

- `games-index.json`: 63 duplicate slugs dropped, 108 game pages that were
  missing from it added (they were absent from every category page), missing
  thumbnails recovered from the old homepage, HTML entities in titles decoded.
- Game-page JSON-LD URLs of the form `/games/games\\slug.html` fixed to
  `/games/slug.html`. No page URL, canonical, `<title>` or JSON-LD `@type`
  changed. Sitemap gains only `/all-games/`.
- ~2,000 newer game pages were missing the AdSense loader, features script
  and manifest; every page now has the same head.

## Cleanup

- 31 one-off scripts that pattern-matched the old markup moved to
  `legacy-scripts/` (none were used by workflows or the `.bat`).
- `content-engine/__pycache__` untracked and git-ignored.

## Manual follow-ups

1. After deploy, open a game page on desktop and phone and confirm in the
   Adsterra dashboard that impressions keep coming for all three units.
2. Cold Read / Guess It Box still load Tailwind CDN + in-browser Babel.
   They now sit in the new shell, but precompiling them would cut ~1MB of JS
   from those two pages.
3. AdSense: this redesign helps (no giant card dump, lighter ad density), but
   "Low value content" is about thin pages. The ~13,800 templated guide
   pages are the likeliest cause — consider `noindex` or pruning the
   fallback-generated ones before requesting a review.
