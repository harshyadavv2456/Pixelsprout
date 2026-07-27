# Pixelsprout — Project Brief (Final, Updated)

**Owner:** Harsh
**Status as of:** July 27, 2026, ~2-3 hours of setup completed tonight
**Purpose of this document:** single reference file for the project — vision, current build, exact current status, and handoff instructions for whoever runs day-to-day operations while Harsh is in CA Final monk mode through November 2026.

---

## 1. What Pixelsprout Is

A free browser gaming platform at **playpixelsprout.com**. No installs, no accounts — click and play, instantly, in any browser. Positioned as a growing, all-genre library.

**Current catalog:** 8 original, self-built HTML5 games across 3 genres:
- **Puzzle:** 2048, Memory Match, Minesweeper
- **Arcade:** Snake, Flappy Hop, Stackblocks
- **Strategy:** Tic-Tac-Toe, Rally (Pong-style)

All 8 are original code, owned outright, no licensing risk.

---

## 2. The Honest Business Assessment

Two distinct business models are in play, at two different stages:

### Model A — Embed Network Aggregator (in progress now)
Apply to third-party game networks (GameDistribution, GamePix), then browse their catalogs and embed selected games via iframe. They host the games; ad revenue splits roughly 50/50.

**Honest ceiling:** No moat — every small gaming site pulls from the same public catalogs. Realistic outcome after 6–12 months of consistent weekly additions: a decent, modestly-earning gaming site, not a breakout platform. Worth doing anyway because the cost/effort is near zero.

### Model B — Direct Developer Upload Marketplace (future, not started)
Let indie developers upload their own games directly to Pixelsprout's own hosting, 50/50 split, owned and controlled by Pixelsprout — a real differentiated catalog, not a pass-through. This is the only path that could realistically approach something like Poki's scale.

**Not a delegation task.** Requires sandboxing untrusted code, security scanning, storage infrastructure, and moderation — a deliberate build for **Harsh personally, post-November 2026.** Parked as an idea, not started.

---

## 3. Current Technical Setup

- **Domain:** playpixelsprout.com — purchased via Namecheap (~₹675/year, no lock-in), DNS connected to Vercel, **live and confirmed working**
- **Hosting:** Vercel (Hobby/free tier) — auto-deploys on every GitHub push
- **Repo:** github.com/harshyadavv2456/Pixelsprout, linked to Vercel
- **Stack:** Plain HTML/CSS/JS, no framework, no backend, no database
- **Design system:** Built around Harsh's Pixelsprout mascot logo — deep space-navy palette (sprout green, star gold, heart pink, sky blue), Press Start 2P pixel-game font for headlines, Inter for body text
- **Site features:** Live search/filter bar, genre-sectioned game grid, custom SVG icons per game, animated marquee ticker, legal pages (Privacy, Terms), sitemap.xml, robots.txt — all pointing to the real domain

**Still-open item — Vercel Hobby tier restriction:** the free Vercel tier is non-commercial only per Vercel's terms. Before ads can properly run long-term, either upgrade to Vercel Pro ($20/month) or migrate to Cloudflare Pages (free, explicitly allows commercial/ad-supported sites). **Not yet resolved — decide on this before relying on ad revenue at scale.**

---

## 4. Monetization Status — Exactly Where Things Stand

### Google AdSense — ✅ Applied, code installed, awaiting review
- Publisher ID: pub-8466016918717424
- AdSense verification script added to `<head>` of all 9 pages (homepage + 8 games)
- Payment profile: name, address verified; bank/tax info submitted
- EEA/UK/Switzerland consent banner (Google's CMP, 3-choice version) set up
- **Site status: "Getting ready" / under review.** Review typically takes a few days to a few weeks. No ads will show and no revenue accrues until this clears — this is normal, not a problem.
- **Payout threshold: $100.** Below that, earnings just accumulate in the dashboard; paid out monthly once crossed.

### GamePix — ✅ Registered, property created, payment set up
- Property "Pixelsprout" created for playpixelsprout.com, traffic estimate 0–50k
- Payment method set up via Tipalti (bank transfer, SBI account) — **note: €6 flat fee + up to 3% FX spread per payout**
- **Zero games embedded yet** — dashboard correctly shows €0.00 revenue, no data. This is expected for a freshly created property.
- **Next action required (ongoing, not tonight):** browse GamePix's Games Catalog dashboard, pick games, embed them on new pages on the site. This is the recurring weekly task for whoever operates the site — see Section 6.

### GameDistribution — ⏸️ Blocked, retry August 2nd
- New publisher sign-ups are paused (team on annual leave) from July 15 – August 1, 2026
- **Action needed: revisit gamedistribution.com/publishers/embedded-links on or after August 2, 2026 and complete the publisher registration then.**

### CrazyGames — ❌ Not applicable, remove from plan
- Corrected understanding: CrazyGames does **not** offer a self-serve publisher/embed program like GameDistribution or GamePix. Their "Developer Portal" is only for people submitting their *own* built games for CrazyGames to host — not for embedding CrazyGames' existing catalog on a third-party site.
- **No action needed or possible here. This was mistakenly included earlier as a parallel option — it isn't one.**

### Google Search Console — ✅ Fully done
- Domain property verified via DNS TXT record (**do not remove that TXT record from Namecheap, ever** — removing it drops verification)
- Sitemap submitted, 11 URLs discovered and indexed successfully

---

## 5. How the Money Actually Works (Plain English)

1. **AdSense (your own 8 games + general site traffic):** once approved, Google shows ads automatically. Revenue accumulates in your AdSense balance. Paid out monthly, only once balance crosses $100.
2. **GamePix (embedded third-party games, once added):** ads run inside those embedded games via GamePix's own system, separate from AdSense. Revenue accumulates in a separate GamePix balance, paid out via Tipalti once their payout minimum is reached.
3. **Nothing pays out today or this week** — both are pending either approval (AdSense) or actual content being added (GamePix). This is expected, not a failure of tonight's work.

---

## 6. Handoff Plan — For Whoever Runs This During Monk Mode (through November 2026)

**Ownership stays with Harsh, execution is delegated:**
- All accounts (AdSense, GamePix, GameDistribution once applied, Namecheap domain, Vercel/hosting) remain under **Harsh's name, email, and payout details** — no exceptions
- The friend/operator gets **GitHub collaborator access to the code repository only** — not ownership of any revenue-bearing account

**Weekly scope for the operator:**
- **On or after August 2:** complete the GameDistribution publisher application (paused until then)
- Log into GamePix's dashboard (and GameDistribution's, once approved) → Games Catalog
- Pick 2–3 new games per week from the available catalog
- Copy the embed code, create a new page on the site, add the game card to the homepage grid following the existing pattern
- That's the entire recurring task — no design changes, no new services, no new spending, no branding changes

**Guardrails:**
- No new sign-ups, subscriptions, or spending without Harsh's explicit approval
- No changes to branding, layout, or core site structure
- Anything outside the weekly scope above waits until Harsh is reachable again
- **No check-ins required or expected until December 2026**

**Explicitly NOT in scope during this period:**
- The direct-developer-upload marketplace (Model B) — parked until Harsh actively resumes
- Any hosting migration (Vercel Pro / Cloudflare Pages) or new monetization experiments
- Any rebrand or redesign beyond what's already built

---

## 7. What's Actually Left To Do (Next Steps From Tonight)

**Passive — no action needed, just waiting:**
- AdSense review (days to weeks)
- GamePix property review

**Active — needs someone to do it:**
- August 2, 2026 or later: apply to GameDistribution
- Ongoing, weekly: browse GamePix catalog, embed 2-3 games, repeat
- At some point before scaling: decide Vercel Pro vs. Cloudflare Pages migration

**Post-November, Harsh's active decision, not delegated:**
- Review actual revenue/traffic data from both platforms
- Decide whether to invest in Model B (direct developer marketplace)
- Reassess hosting migration
- Decide whether the "generic embed aggregator" ceiling is acceptable long-term or whether real differentiation is worth pursuing

---

*This document is the single source of truth for Pixelsprout's status, plan, and handoff terms as of July 27, 2026. Supersedes any earlier version of this brief. Update it directly rather than creating parallel notes.*
