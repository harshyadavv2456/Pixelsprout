# Pixelsprout — Project Brief (FINAL, v3)

**Owner:** Harsh
**Status as of:** July 30, 2026
**Supersedes:** v2 (July 28).

---

## 1. What Pixelsprout Is

A free browser gaming platform at **playpixelsprout.com**. No installs, no accounts — click and play instantly.

**Catalog: ~2,900 games**, plus **42 dedicated category landing pages** (Arcade, Kids, Action, Sports, Casual, Adventure, Animal, Racing, Strategy, Shooter, and more — every category with 15+ games gets its own page; smaller categories intentionally don't, to avoid thin-content SEO risk).

---

## 2. What's New Since v2 — Everything Built This Session

### SEO & Discoverability
- **IndexNow integration** — every new game instantly notifies Bing/Yandex on publish, instead of waiting for their own crawl schedule
- **Structured data (schema.org)** — every game page carries `VideoGame` schema (name, genre, image, price) for richer search listings
- **Breadcrumb navigation** — every game page and every category page now shows visual breadcrumbs (Home / Category / Game) *and* `BreadcrumbList` JSON-LD schema
- **42 category landing pages** — `/arcade/`, `/kids/`, `/racing/`, etc., each with unique intro copy, real game grids, canonical URLs, OG tags, and breadcrumb schema. Regenerates automatically as part of the daily automation, so game counts and listings never go stale.

### Site fixes (bugs found and corrected)
- Favicon fixed (was showing a generic fallback icon)
- Open Graph share preview fixed (WhatsApp/social links now show your real banner)
- Ribbon ad format corrected to match what AdSense actually generated
- Orientation lock bug fixed (was forcing landscape on all games, breaking portrait ones)
- Mobile embed sizing fixed
- Outdated Terms content corrected (no longer falsely claims all games are original builds)
- About/Contact pages added (AdSense's own review checklist specifically asked for these)

### Monetization
- Two AdSense ad units live on every game page (banner + ribbon), correctly wired, awaiting AdSense approval to render
- ads.txt fixed and validated
- GamePix confirmed active

### Pinterest — genuinely working, one step from fully public
- Full API pipeline built and tested end-to-end: OAuth, board auto-creation, image fallback handling, tracking to prevent duplicate posts
- **Currently posting successfully in Sandbox mode** (visible only to you) — this is Pinterest's required testing tier for a new app, not a limitation of the code
- **One action needed from you:** submit for Pinterest's "Standard access" upgrade (button on your app's dashboard), including a screen recording of the sandbox run succeeding as your demo video. Once approved, flip one setting (`"sandbox": false`) and it posts real public pins automatically, daily, forever.

### Automation reliability — real problem found and fixed
- **Problem:** GitHub Actions' free monthly minutes ran out mid-month, causing 3+ consecutive failed daily runs — an unreliable single point of failure
- **Fix:** Windows Task Scheduler on your own PC is now the actual daily driver for everything (new games, Pinterest posting, category page refresh) — zero minute limits, runs entirely locally
- GitHub Actions scheduled triggers have been **intentionally disabled** (kept available for manual testing only) to prevent both systems running the same job on the same day and causing a rejected git push

### ChatGPT's 22-point "production audit" — evaluated, not blindly followed
- **Rejected:** repository restructuring, "single source of truth" rewrites, security header hardening, Lighthouse-100 perfectionism, fuzzy search — real risk or effort for near-zero traffic benefit, explicitly against your instruction not to touch what's working
- **Implemented:** IndexNow, category landing pages, breadcrumbs (both visual and schema), richer structured data — the handful of ideas that directly serve reach/discoverability with low risk, since they're purely additive

---

## 3. Monetization — Current Status (unchanged from v2 unless noted)

### AdSense — code live, review pending
- Publisher ID: `pub-8466016918717424`
- Nothing renders until AdSense approval clears

### GamePix — active, ads.txt validated
- Property status: **ACTIVE**, ads.txt: **VALID**

### GameDistribution — apply August 2, 2026
- Sign-ups paused until then

### Pinterest — see above, sandbox-verified, Standard access pending your submission

---

## 4. Open-Source / Indie Migration Strategy (Phase 2 — Post-November)

*(Unchanged from v2 — still correctly a post-November decision, still targets genres/mechanics rather than exact GamePix titles, still requires real play data that doesn't exist yet.)*

---

## 5. Financial Model — Illustrative Scenarios, Not a Forecast

*(Unchanged from v2 — see prior brief for full assumptions and NPV table. No new traffic data exists yet to revise these numbers.)*

| Scenario | Yr 5 annual revenue | 5-yr NPV |
|---|---|---|
| Conservative | ~$450/yr | ~$590 (~₹49,000) |
| Base | ~$3,000/yr | ~$3,650 (~₹3.0 lakh) |
| Base + Open-Source Migration | ~$3,450/yr | ~$4,140 (~₹3.4 lakh) |
| Optimistic | ~$19,200/yr | ~$22,100 (~₹18.4 lakh) |

---

## 6. What's Still Open

**Passive:**
- AdSense review
- Pinterest Standard access review (after you submit)

**One real action from you:**
- Submit Pinterest Standard access request with the sandbox demo recording

**Date-locked:**
- Apply to GameDistribution on/after August 2, 2026

**Unresolved decision:**
- Vercel Hobby tier is non-commercial only — resolve before leaning on ad revenue at scale

**Setup task, instructions ready:**
- Task Scheduler — guide provided, needs to actually be set up on your PC to become the real daily driver

**Minor, not urgent:**
- Sidebar genre list still doesn't reflect every category (cosmetic only — category *pages* now exist independent of the sidebar)

**Post-November, your active decision:**
- Review real traffic/revenue data
- Begin Phase 2 open-source migration if justified
- Resolve hosting decision
- Spot-check catalog quality

---

## 7. Marketing — Unchanged, Still the Real Lever

Per the financial model, marketing effort remains the single biggest lever between "irrelevant" and "meaningful" income. Nothing built this session changes that — IndexNow, schema, category pages, and Pinterest all help the same base traffic get discovered slightly better; none of them replace the need for your friend's consistent posting.

---

## 8. Direct Answer: Is This Steady, Perpetual Income?

Unchanged from v2: **no, not without ongoing effort.** Everything added this session strengthens the foundation (better SEO, working Pinterest pipeline, reliable automation) but doesn't change the fundamental answer — income scales with actual marketing effort, not with more automation layered on top of an already-automated system.

**Honest bottom line:** a more technically solid, more discoverable, more reliably-running asset than it was two days ago. Genuinely good progress. Still requires the same human effort (marketing) to turn into real money.

---

*Single source of truth for Pixelsprout as of July 30, 2026. Update directly rather than creating parallel notes.*
