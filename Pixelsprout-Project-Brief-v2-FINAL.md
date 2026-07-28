# Pixelsprout — Project Brief (FINAL, v2)

**Owner:** Harsh
**Status as of:** July 28, 2026
**Supersedes:** all earlier versions of this brief, including the July 27 "COMPLETE" version.

---

## 1. What Pixelsprout Is

A free browser gaming platform at **playpixelsprout.com**. No installs, no accounts — click and play instantly.

**Catalog: ~2,900 games** across genres including Puzzle, Arcade, Strategy, Simulation, Hidden-Object, Match-3, 2048, Battle, Memory, Kids, and others that appear dynamically as GamePix's catalog grows (e.g. "Escape").
- **8 original, self-built HTML5 games** — 2048, Memory Match, Minesweeper, Snake, Flappy Hop, Stackblocks, Tic-Tac-Toe, Rally. Owned outright, zero revenue split, zero licensing dependency.
- **~2,889 embedded third-party games** via GamePix, quality-filtered, revenue-shared with GamePix.

---

## 2. Technical Setup — Complete

- **Domain:** playpixelsprout.com, DNS on Vercel, live
- **Hosting:** Vercel free Hobby tier — **still an open decision, see Section 6**
- **Design:** space-navy palette, pixel-game typography, custom SVG icons for originals, real thumbnails for embedded games, sidebar genre nav, search, hero engagement widget, similar-games recommendations, marquee ticker
- **Legal:** Privacy, Terms, ads.txt (validated), sitemap.xml, robots.txt

---

## 3. Monetization — Current Status

### AdSense — code live, review pending
- Publisher ID: `pub-8466016918717424`
- **Two ad units live on every game page**, both correctly matched to what AdSense actually generated:
  - **Game Banner** — slot `4936643192`, format `auto`, placed above the game
  - **Game Ribbon** — slot `1457517471`, format `auto`, placed below the game
- Neither touches the game iframe itself — fully separate from GamePix's in-game ads
- **Nothing renders until AdSense approval clears** — code is correctly wired and waiting

### GamePix — active, ads.txt validated
- Property status: **ACTIVE**, ads.txt: **VALID**
- Daily automation (`auto-add-games.py`) pulls 3 new games/day, fully automatic
- Revenue split with GamePix on all ~2,889 embedded games (approximate industry-typical range: you and the game's developer share roughly 90% of ad revenue between you, GamePix keeps roughly 10% — your exact effective take after any developer share is not separately confirmed in writing, treat the modeling below as an approximation, not a contractual figure)

### GameDistribution — apply August 2, 2026
- Sign-ups paused until then, no action possible before that date

---

## 4. Open-Source / Indie Migration Strategy (Phase 2 — Post-November)

**The idea:** once real play data exists, identify which genres/mechanics drive the most plays on GamePix-embedded games, and build or adopt **open-source, self-hosted equivalents** for those specific genres — the same pattern already proven with your 8 original games. Self-hosted games keep ~100% of ad revenue instead of splitting with GamePix.

**Why this can't start yet, honestly:** you have zero real traffic data today. "Most lucrative games" is not answerable until GamePix's Reports tab has weeks-to-months of real play data to look at. This is correctly a Phase 2 initiative, not a today-action.

**Why this targets genres, not exact titles:** most high-performing GamePix games are third-party branded content (specific art, specific IP) with no direct open-source equivalent. What's realistic is identifying which *mechanics* perform well (e.g. runner games, merge games, solitaire-style games) and building **original** games in that mechanic — exactly how your 8 originals were built — not literally cloning a specific branded title.

**Realistic pace:** 1-3 new original games per quarter, built by you (or a hired dev) post-November, once you know what's actually worth building. This is deliberate, effortful work — not something automation can do.

**Financial effect of this (modeled in Section 5):** modest but real — roughly a 10-15% uplift to Base-case revenue from Year 3 onward, once a handful of high-performing genres have been replaced with self-hosted originals. Not a platform-transforming move by itself; a genuine, worthwhile compounding improvement on top of the existing model.

---

## 5. Financial Model — Illustrative Scenarios, Not a Forecast

**Read this caveat first:** the single biggest unknown — how much traffic a new, largely-automated site actually gets — cannot be known in advance. This is a range of "what would have to be true," not a prediction. Costs are near-zero (~$10/year domain, free hosting) and don't materially affect the outcome — revenue assumptions drive everything.

**Assumptions:**
- Revenue = (monthly sessions × 12) × blended RPM per 1,000 sessions (AdSense + GamePix combined)
- Discounted at 15%/year, reflecting genuine uncertainty
- Open-source uplift applied only to the Base case, starting Year 3, once Phase 2 becomes realistic

| Scenario | What it assumes | RPM | Yr 5 monthly sessions | Yr 5 annual revenue | 5-yr NPV |
|---|---|---|---|---|---|
| **Conservative** | Automation only, no active marketing | $0.75/1k | ~50,000 | ~$450/yr | **~$590** (~₹49,000) |
| **Base** | Friend executes consistent content/marketing | $1.25/1k | ~200,000 | ~$3,000/yr (~$250/mo) | **~$3,650** (~₹3.0 lakh) |
| **Base + Open-Source Migration** | Base case, plus Phase 2 genre-replacement from Yr 3 | $1.25/1k (+15% Yr3-5) | ~200,000 | ~$3,450/yr (~$290/mo) | **~$4,140** (~₹3.4 lakh) |
| **Optimistic** | Real sustained marketing investment | $2.00/1k | ~800,000 | ~$19,200/yr (~$1,600/mo) | **~$22,100** (~₹18.4 lakh) |

**What the open-source migration actually buys you:** about a 13% NPV improvement over plain Base case — real, but modest at realistic execution pace. It is not the lever that changes the outcome category; marketing/traffic effort is.

---

## 6. What's Still Open

**Passive:**
- AdSense review
- Daily automation continuing on its own

**Date-locked:**
- Apply to GameDistribution on/after August 2, 2026

**Unresolved decision:**
- Vercel Hobby tier is non-commercial only. Resolve (Vercel Pro or Cloudflare Pages migration) before leaning on ad revenue at real scale.

**Minor, not urgent:**
- Sidebar genre list doesn't yet include every category the feed can produce (e.g. "Escape") — cosmetic, not functional

**Post-November, Harsh's active decision:**
- Review real traffic/revenue data
- Begin Phase 2 open-source migration if the numbers justify it
- Resolve hosting decision
- Spot-check catalog quality

---

## 7. Marketing — What Actually Moves the Needle

Per the financial model, marketing effort is the single biggest lever between "irrelevant" and "meaningful" income:
- Friend posts short gameplay clips **consistently** (3-4x/week minimum) — this is the actual difference between Conservative and Base case
- Target "unblocked games" and specific game-name search intent in captions
- Submit to 2-3 small game-directory sites for backlinks (one-time)
- SEO from ~2,900 indexed pages is already compounding passively — no action needed there

---

## 8. Direct Answer: Is This Steady, Perpetual Income?

**No, not without ongoing effort** — and the model above shows exactly why. Conservative case (automation only) is pocket change. Base case (friend actually executes marketing consistently) becomes a real but modest ₹2,000-3,000/month by Year 5. Open-source migration adds a further modest bump on top of that. Only the Optimistic case — real sustained marketing investment beyond what's currently planned — reaches money that matters, and that requires effort this plan doesn't currently include.

**Honest bottom line:** a legitimate, near-zero-cost asset worth letting run. It becomes meaningful income in direct proportion to ongoing human effort — not by itself, and not "perpetually" without that effort continuing.

---

*Single source of truth for Pixelsprout as of July 28, 2026. Update directly rather than creating parallel notes.*
