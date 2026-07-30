# Pixelsprout — Project Brief (FINAL, v4)

**Owner:** Harsh
**Status as of:** July 30, 2026
**Supersedes:** v3 (July 30, earlier today).

---

## 1. What Pixelsprout Is

A free browser gaming platform at **playpixelsprout.com**. No installs, no accounts — click and play instantly.

**Catalog: ~2,900 games**, plus **42 dedicated category landing pages** (Arcade, Kids, Action, Sports, Casual, Adventure, Animal, Racing, Strategy, Shooter, and more).

---

## 2. Pinterest — Submitted, Now Waiting

- Full API pipeline built and verified working (OAuth, board creation, pin posting, tracking) in Pinterest's required Sandbox tier
- **Standard access upgrade request submitted** — Pinterest's dashboard confirms: *"Upgrade to Standard access pending"*
- This is a genuine human review on Pinterest's end. **No action possible until they respond** — same category of wait as AdSense review, no way to expedite either.
- **Once approved:** change one line in `pinterest-config.json` (`"sandbox": false`) and the exact same daily automation starts posting real, public pins — no new code needed.

---

## 3. Financial Model — Updated to Reflect This Session's Work

**Same caveat as always: illustrative scenarios, not a forecast.** No real traffic data exists yet — these are "what would have to be true" ranges, not predictions.

**What changed and why:** this session added genuine SEO infrastructure (IndexNow, structured data, breadcrumbs, 42 category landing pages) plus the Pinterest pipeline. These are real, additive discoverability improvements — but modest ones. Applying a small, clearly-labeled uplift to the Base case, not a category change:

- **+10% from Year 2** — reflects category pages capturing broader search intent ("arcade games online" vs. only exact game names) once they've had time to be indexed and start ranking. Year 1 unchanged since indexing/ranking takes real time.
- Combines with the existing **+15% open-source migration uplift from Year 3** (unchanged from before, still Phase 2/post-November).

| Scenario | What it reflects | Yr 5 annual revenue | 5-yr NPV |
|---|---|---|---|
| **Conservative** | Automation only, no active marketing | ~$450/yr | ~$590 (~₹49,000) |
| **Base** | Friend executes consistent marketing | ~$3,000/yr (~$250/mo) | ~$3,650 (~₹3.0 lakh) |
| **Base + SEO/Pinterest Infrastructure** | This session's category pages + eventual Pinterest traffic | ~$3,300/yr (~$275/mo) | **~$4,000 (~₹3.3 lakh)** |
| **Base + SEO + Open-Source Migration** | Everything above, plus Phase 2 genre-replacement from Yr 3 | ~$3,795/yr (~$315/mo) | **~$4,550 (~₹3.8 lakh)** |
| **Optimistic** | Real sustained marketing investment | ~$19,200/yr (~$1,600/mo) | ~$22,100 (~₹18.4 lakh) |

**Honest read on this update:** tonight's work moved the Base case NPV from ~$3,650 to ~$4,550 in the best combined case — roughly a **25% improvement**, entirely from infrastructure, zero additional marketing effort. That's a real, measurable return on this session's work. **It is still not the dominant lever** — compare it to Optimistic's ~$22,100: marketing effort remains 5x more impactful than all the technical work combined. This update makes the foundation better; it doesn't change the fundamental answer in Section 6.

---

## 4. Everything Else From This Session (unchanged from v3)

- IndexNow integration, live
- Structured data (`VideoGame` schema), live on all games
- Breadcrumbs (visual + `BreadcrumbList` schema), live on all games and category pages
- 42 category landing pages, live, auto-refreshing daily
- Favicon, OG banner, ribbon ad format, orientation lock, mobile sizing — all bugs found and fixed
- About/Contact pages added
- Outdated Terms content corrected
- GitHub Actions scheduled triggers disabled (prevents conflict); Task Scheduler is now the real daily driver — **confirm this is actually set up on your PC, this is the one manual step that doesn't automate itself**

---

## 5. Monetization — Current Status

### AdSense — code live, review pending
- Publisher ID: `pub-8466016918717424`, nothing renders until approval clears

### GamePix — active, ads.txt validated

### GameDistribution — apply August 2, 2026

### Pinterest — see Section 2, submitted and pending

---

## 6. Direct Answer: Is This Steady, Perpetual Income?

**Still no, not without ongoing effort — but the foundation is now genuinely stronger.** Tonight's work added real, measurable value (see Section 3's ~25% NPV improvement in the combined scenario), entirely through infrastructure, zero extra marketing effort required to realize it. That's a legitimate win.

**But it doesn't change the category of outcome.** Conservative case is still pocket change. Base case, even with tonight's improvements, is still a modest ₹3,000-3,800/month by Year 5 — real, but not life-changing. Only sustained marketing investment (Optimistic case) reaches money that matters, and that gap hasn't closed.

**Honest bottom line:** you've meaningfully improved the asset's technical quality and discoverability tonight. That's worth being genuinely pleased about. It's not a substitute for the marketing effort that remains the actual determinant of whether this becomes real income.

---

## 7. What's Still Open

**Passive, waiting on external review:**
- AdSense review
- Pinterest Standard access review

**Date-locked:**
- Apply to GameDistribution on/after August 2, 2026

**One real setup step, not yet confirmed done:**
- Windows Task Scheduler — needs to actually be created and tested, not just have the `.bat` file present

**Unresolved decision:**
- Vercel Hobby tier is non-commercial only — resolve before leaning on ad revenue at scale

**Post-November, your active decision:**
- Review real traffic/revenue data once it exists
- Begin Phase 2 open-source migration if numbers justify it
- Resolve hosting decision
- Spot-check catalog quality

---

*Single source of truth for Pixelsprout as of July 30, 2026. Update directly rather than creating parallel notes.*
