# Pixelsprout — Project Brief (FINAL)

**Owner:** Harsh
**Status as of:** July 27, 2026 — built end-to-end in roughly 4 hours in one session
**Purpose:** single reference file — what this is, what's been built, what's automated, and exactly what's still open.

---

## 1. What Pixelsprout Is

A free browser gaming platform at **playpixelsprout.com**. No installs, no accounts — click and play instantly. Positioned as a large, growing, all-genre library.

**Catalog: ~2,897 games** across genres including Puzzle, Arcade, Strategy, Simulation, Hidden-Object, Match-3, 2048, Battle, Memory, and Kids. This includes:
- 8 original, self-built HTML5 games (2048, Memory Match, Minesweeper, Snake, Flappy Hop, Stackblocks, Tic-Tac-Toe, Rally) — owned outright, no licensing dependency
- ~2,889 embedded third-party games pulled from GamePix's catalog, quality-filtered (score ≥ 0.55), one-time bulk import

---

## 2. Technical Setup — Complete

- **Domain:** playpixelsprout.com, purchased via Namecheap (~₹675/year), DNS connected to Vercel, live
- **Hosting:** Vercel (free Hobby tier), auto-deploys on every GitHub push
- **Repo:** github.com/harshyadavv2456/Pixelsprout
- **Design:** Full identity built around Harsh's Pixelsprout logo — deep space-navy palette, Press Start 2P pixel-game headline font, Inter body text, custom SVG icons for the original 8 games, real thumbnail images for embedded games
- **Site features:** live search/filter bar, genre-sectioned grid, animated marquee ticker, favicon, legal pages (Privacy/Terms), sitemap.xml (~2,900 URLs), robots.txt, Vercel Web Analytics
- **AdSense code:** installed across all pages; consent banner (EEA/UK/Switzerland) configured

---

## 3. Automation — Built and Tested

**Daily auto-add script (`auto-add-games.py`):** pulls up to 3 new games/day from GamePix's feed, builds each page, adds the homepage card, updates the sitemap, commits and pushes. Shares a tracking file (`games-data.json`) with the bulk import, so nothing is ever added twice.

**One-time bulk import (`bulk-add-games.py`):** already run once — pulled the ~2,889 games currently on the site, quality-filtered, no artificial cap. Not meant to run again; the daily script takes over from here.

**Two possible daily triggers — pick one, not both, to avoid double-adding:**
- **GitHub Actions** (`.github/workflows/auto-add-games.yml`) — runs in the cloud daily, no PC required. Currently paused due to a GitHub billing/spending limit hit (from unrelated account activity); **resumes automatically on its own once the limit resets** (~4 days from when it was hit) — nothing needs to be re-enabled by hand for this to resume.
- **Windows Task Scheduler** — an alternative that runs the same script from Harsh's own PC. **Decision: not set up, in favor of letting GitHub Actions resume on its own.** Do not set up Task Scheduler alongside GitHub Actions — running both causes duplicate-day additions.

---

## 4. Monetization Status

### Google AdSense — Applied, pending review
- Publisher ID: pub-8466016918717424
- Site status: under Google's review (typically days to a few weeks — no way to speed this up)
- **One thing to know, not a problem to fix now:** the catalog includes a large "Kids" category (~218 games). AdSense has specific rules for child-directed content (ad personalization limits, sometimes a "child-directed treatment" tag). If review flags this section specifically, that's why — it's an AdSense settings adjustment, not a content removal issue. Address only if/when AdSense actually raises it.
- **Payout: $100 threshold**, monthly, once crossed.

### GamePix — Active and working
- Property created for playpixelsprout.com, payment set up via Tipalti (SBI bank transfer, €6 flat fee + up to 3% FX spread per payout)
- Feed access already functional (confirmed — both the manual test and the bulk import successfully pulled real games), so this is not gated behind a separate approval the way AdSense is.

### GameDistribution — Blocked until August 2, 2026
- New publisher sign-ups paused (team on leave) through August 1
- **Action needed: apply on or after August 2, 2026** at gamedistribution.com/publishers/embedded-links

### CrazyGames — Not applicable
- Confirmed: no self-serve publisher/embed program exists for this. Nothing to do here, ever, for this use case.

---

## 5. What's Still Open — The Honest List

**Passive, needs nothing from anyone:**
- AdSense review completing
- GitHub Actions resuming automatically once the billing limit resets

**One small technical task, not yet confirmed done:**
- Add `loading="lazy"` to the ~2,889 embedded game thumbnail images on the homepage, to reduce initial page-load weight (command already provided — run locally and push)

**One date-locked action item:**
- Apply to GameDistribution on/after August 2, 2026

**One unresolved decision, not urgent but real:**
- Vercel's free Hobby tier is non-commercial only per their terms. Before leaning on ad revenue at real scale, decide: upgrade to Vercel Pro ($20/month) or migrate to Cloudflare Pages (free, commercial-safe). Not urgent while AdSense review is still pending and no ads are live yet — but needs a decision before it matters.

**Post-November, Harsh's active decision, not delegated to anyone:**
- Review actual traffic and revenue data from AdSense and GamePix
- Decide whether to build the direct-developer-upload marketplace (Model B — the actual differentiator, requires real infrastructure work: sandboxing, security scanning, moderation)
- Resolve the Vercel/Cloudflare hosting decision
- Reassess catalog quality — with ~2,889 auto-pulled games now live, worth a human pass at some point to spot-check for anything broken, mislabeled, or low-quality that slipped through the quality filter

---

## 6. What This Means Right Now

Everything that can be automated, is automated. Everything that needed manual setup — domain, hosting, design, legal pages, monetization applications, the entire catalog — is done. The only things left are: one date in the future (Aug 2 for GameDistribution), one lazy-loading fix, one hosting decision to make eventually, and passive waiting on two reviews. Nothing here requires daily attention from Harsh or his friend between now and November.

---

*This is the final, current source of truth for Pixelsprout as of July 27, 2026. Supersedes all earlier versions of this brief.*
