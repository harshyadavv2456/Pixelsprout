# Redesign plan (branch `redesign`, never merge without review)

Style reference: foundplay.io (dark base, single acid accent). Our own palette, copy and assets; nothing copied.

## Done (Days 1-2: foundation)
- `styles.css` tokens retuned: deep green-black base (`#0A0D0B`), surfaces `#121712/#192019`, lime accent `#B6F23F` with dark ink, soft lime top glow, 14px card radius. Legacy aliases kept, so tool pages and built-in games still read the same variables.
- Typography: display font for h1/h2/shelf titles with tight tracking; `.label` mono uppercase utility.
- Components: `.btn-lime`, `.btn-ghost`, `.topnav` header nav, game tile card with hover "Play" pill and "Original" badge (`card--original`).
- `site_shell.py`: header nav (Browse, Originals, Guides, Surprise me), Original badge from `assets/originals.json`, `originals_first()` helper.
- Untouched: ad slots/scripts (`ad_*`, `assets/ads.js`, AdSense/Adsterra), `<head>` (titles, descriptions, canonicals, robots), `sitemap.xml`, URLs.
- CSS changes apply to every page immediately (all pages load `/styles.css`). Header/badge markup appears on pages as they are re-rendered (`migrate-ui.py` / generators). A full re-render was intentionally NOT run yet (would touch ~19k files).

## Done (rough preview, compressed timeline)
- Homepage: hero with Surprise me, trending tabs (Trending/Originals/New), phone-friendly toggle (placeholder), collections rows. Injected by `assets/redesign/redesign.js` (loaded from `pixelsprout-features.js`), data from `build-redesign-data.py`.
- Game pages (all existing): trust line, Play next (1 original + 2 same genre), "At a glance" FAQ + FAQPage JSON-LD (added client-side).

## Next
- **Days 3-4 homepage:** trending tabs (24h/7d/all), working Surprise me (random game from games-index.json, JS on `[data-surprise]`), collections row, phone-friendly filter; originals first (`originals_first`).
- **Day 5 game page:** Play next list (3 games), FAQ block + FAQPage JSON-LD, link-checked trust line.
- **Days 6-7 QA:** phone + desktop, Lighthouse speed, SEO diff (titles/canonicals/robots/sitemap unchanged), ad render check, then bump `ASSET_VERSION` and re-render with `migrate-ui.py`.
