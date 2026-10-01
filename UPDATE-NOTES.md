# Pixelsprout update: one daily job + SEO Bot pipeline + template pages noindexed

## Install (one time, ~10 minutes)
1. Copy everything in this folder into the repo root (same paths, overwrite).
2. DELETE these old workflow files (the new daily.yml replaces all four):
   - .github/workflows/auto-add-games.yml
   - .github/workflows/generate-guides.yml
   - .github/workflows/post-to-pinterest.yml
   - .github/workflows/refresh-popular-games.yml
3. Commit and push to main.
4. On GitHub: branch dropdown → type `seo-queue` → "Create branch seo-queue from main".
5. Actions tab → "Daily site automation" → Run workflow (first run noindexes ~12,000 template pages).
6. Google Search Console → Sitemaps → resubmit sitemap.xml.
7. If the Windows Task Scheduler job (run-daily-automation.bat) is still enabled, disable it - it would run the same scripts twice and cause push conflicts.

No new secrets are needed - the workflow uses the same ones as before.

## What changed
- daily.yml: one checkout instead of four, 45-minute hard cap per day, each step continues if another fails,
  one commit (= one Vercel deploy) per day, push retries on conflict.
- seo_cleanup.py: 12,146 of 13,850 guide pages are the generic fallback template. They now get
  `noindex,follow` and leave sitemap.xml. When a page gets real content (Groq or SEO Bot), it comes back automatically.
- apply_queue.py + SEO-BOT-QUEUE.md: SEO Bot pages (JSON on the `seo-queue` branch) are validated,
  HTML-escaped, rendered and locked so Groq never overwrites them. Results: content-engine/queue-report.json.
- generate_guides.py: `--max-minutes` time budget, saves progress after every game, skips locked pages.
- generate_collections.py: collection intros are written once and reused (was 26 Groq calls/day, and a failed
  Groq day replaced intros with the generic line - all 26 are currently the generic line).
- page_renderer.py: optional "extra_sections" for deeper pages.

Tested on a copy of the repo: full pipeline run, queue accept/reject/escape cases, locked pages survive
regeneration, sitemap stays valid XML (18,953 -> ~6,800 URLs).
