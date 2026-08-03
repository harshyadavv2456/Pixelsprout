# Content engine — guide pages, "games like X" collections, auto internal linking

## What this actually builds (and why it's not "4 random blogs per game")

Per your brief and the ChatGPT critique you pasted (which was right): thin,
near-duplicate pages hurt more than they help. So each of the 4 pages per
game targets a genuinely different search intent:

- `/guides/<slug>-tips/` — tips, strategy, how to score higher
- `/guides/<slug>-controls/` — keyboard/mouse/touch control scheme
- `/guides/<slug>-beginner-guide/` — what the game is, first steps, who it's for
- `/guides/games-like-<slug>/` — other catalog games in the same category

Plus a **separate, smaller, curated layer** — 18 `/games-like/<famous-title>/`
pages (Subway Surfers, Minecraft, GTA, Candy Crush, etc. — full list in
`content-engine/collections_data.py`, easy to add more). These are the
highest-value pages: they can rank for searches about games you don't
host, and convert that traffic into plays of similar games you do host.
Each one only publishes if it finds 4+ real matching games in your
catalog — it won't create an empty or thin page.

**Internal linking is automatic and bidirectional:**
- Every guide page links back to its game, to its 3 sibling guide pages,
  and to 8 similar catalog games (deterministic category/title matching,
  not AI-guessed).
- Every game page now links forward to its guide pages too (via
  `pixelsprout-features.js`, reading `guides-index.json` — no need to
  touch any of your 2,774 existing game HTML files by hand).
- Every collection page links out to 15-20 real catalog games.

## Groq, 5-key rotation, and the "run out of quota, use next key" logic

`content-engine/groq_client.py` reads `GROQ_API_KEY_1` through
`GROQ_API_KEY_5` from environment variables. On a 429 (rate limit/quota)
response, it marks that key dead for the rest of the run and moves to the
next one automatically — exactly the daily-replenishing-quota behavior you
described. If all 5 keys are exhausted mid-run, it falls back to
template-based placeholder content for whatever's left (see below) rather
than failing the whole run.

## Fallback mode — and why it's genuinely useful, not just a stopgap

Every script runs even with **zero API keys configured** — it uses
`content-engine/fallback_content.py` instead, producing structurally
complete, correctly-linked, correctly-schema'd pages with clearly generic
text. This is what let me build and test this entire pipeline end-to-end
against your real 2,774-game catalog without needing your Groq keys at
all — I ran it, confirmed the HTML balances, the internal links point to
real games, the sitemap updates correctly, before handing this to you.

It's also a safety net in production: if Groq has an outage or all 5 keys
hit quota on a given day, the daily run still completes instead of
failing outright — any fallback-generated pages get tagged in
`content-engine/manifest.json` (`"any_fallback": true`) so you can
re-run with `--retry-fallback` later to upgrade them to real AI content
once quota's available again.

## Setup

### 1. Get 5 Groq API keys

console.groq.com → API Keys. Free tier gives each key its own daily token
allowance — 5 separate accounts/keys is exactly what makes the rotation
worth doing.

### 2. Add them as GitHub Secrets

Your repo → **Settings → Secrets and variables → Actions** → **New
repository secret**, one at a time:

| Name | Value |
|---|---|
| `GROQ_API_KEY_1` | first key |
| `GROQ_API_KEY_2` | second key |
| `GROQ_API_KEY_3` | third key |
| `GROQ_API_KEY_4` | fourth key |
| `GROQ_API_KEY_5` | fifth key |

### 3. Copy the files onto your PC

At `E:\PixelSprout\Pixelsprout`:

| From this delivery | Action |
|---|---|
| `content-engine\` (whole folder) | **New** |
| `.github\workflows\generate-guides.yml` | **New** |
| `pixelsprout-features.js` | **Replace** (adds the game-page → guides links) |

### 4. Test locally first (no API cost, no keys needed)

```bash
python content-engine/generate_guides.py --dry-run --limit 3
python content-engine/generate_collections.py --dry-run
```

Open a couple of the generated files in `guides/` and `games-like/` in a
browser to see the real layout before spending any API quota. Delete the
test output when you're happy:

```bash
# Windows PowerShell
Remove-Item -Recurse -Force guides, games-like, content-engine\manifest.json, guides-index.json -ErrorAction SilentlyContinue
```

### 5. Run the real, AI-powered backfill (this is the big one)

With your keys set as **local** environment variables (not just GitHub
Secrets) for a one-time manual backfill:

```powershell
$env:GROQ_API_KEY_1="..."
$env:GROQ_API_KEY_2="..."
$env:GROQ_API_KEY_3="..."
$env:GROQ_API_KEY_4="..."
$env:GROQ_API_KEY_5="..."
python content-engine/generate_guides.py --limit 2774
python content-engine/generate_collections.py
```

**Realistic expectation:** 2,774 games × 4 pages = ~11,000 API calls. Even
spread across 5 keys' daily quotas, this will very likely take several
days of runs, not one sitting — that's fine, it's fully incremental and
resumable (re-run the exact same command daily; it always picks up where
`content-engine/manifest.json` left off).

**Or, simpler: skip the manual backfill entirely** and just let the
GitHub Actions workflow (§6) run daily on its default batch size (40
games/day) — the whole catalog backfills itself over about 70 days with
zero manual effort, at the same pace new games get added anyway.

### 6. Commit and push

```bash
git add .
git commit -m "Add content engine: guide pages, collections, auto internal linking"
git push
```

The `generate-guides.yml` workflow will then run automatically every day
at 6:30 UTC (30 min after your existing `auto-add-games.yml`), processing
new games and refreshing the 18 collection pages. You can also trigger it
manually any time from the Actions tab, optionally overriding the batch
size.

## Images (per your "2 pics per game" ask) — honest scope note

I did **not** wire in AI image generation for these pages. Two reasons:
generating genuinely useful, non-generic images per page at this scale is
a meaningfully bigger and more expensive piece of work than the text
pipeline, and — per the copyright/attribution concerns baked into how I
work — I'd rather flag that as a deliberate scope cut than ship something
low-quality. What's already there: every guide/collection page uses the
game's real GamePix thumbnail (`og:image`, and inline in the "similar
games" grids) — that's real, relevant, already-licensed imagery, not
padding. If you want actual custom illustrations per guide later, that's
a separate, well-scoped follow-up, not something to bolt onto this run.

## What's genuinely NOT done

- The manual backfill for all 2,774 games hasn't been run — that's the
  API-cost/time-cost step only you can kick off (§5).
- No image generation (see above).
- The 18 curated collections are a starting set — add more to
  `content-engine/collections_data.py` any time; the generator picks up
  new entries automatically on the next run.
- No de-duplication/quality scoring beyond "did Groq return valid JSON" —
  if you want a stricter quality gate (min word count, banned-phrase
  filter, etc.) before a page counts as "done" rather than needing a
  retry, that's a reasonable next iteration once you see real AI output
  quality.
