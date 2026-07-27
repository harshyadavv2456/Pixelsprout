# Pixelsprout — Project Brief

**Owner:** Harsh
**Status as of:** July 27, 2026
**Purpose of this document:** single reference file for the project — vision, current build, next steps, and handoff instructions for whoever runs day-to-day operations while Harsh is in CA Final monk mode through November 2026.

---

## 1. What Pixelsprout Is

A free browser gaming platform (playpixelsprout.com). No installs, no accounts — click and play, instantly, in any browser. Positioned as a growing, all-genre library, not a small curated hobby site.

**Current catalog:** 8 original, self-built HTML5 games across 3 genres:
- **Puzzle:** 2048, Memory Match, Minesweeper
- **Arcade:** Snake, Flappy Hop, Stackblocks
- **Strategy:** Tic-Tac-Toe, Rally (Pong-style)

All 8 are original code, owned outright, no licensing risk.

---

## 2. The Honest Business Assessment

Two distinct business models are in play here, at two different stages:

### Model A — Embed Network Aggregator (what we're doing now)
Apply to GameDistribution, GamePix, and CrazyGames' publisher programs. Once approved, browse their game catalogs and embed selected titles via iframe. They host the games; you display them; ad revenue splits roughly 50/50.

**Honest ceiling:** No moat. Every small gaming site pulls from the same public catalogs. Realistic outcome after 6–12 months of consistent weekly additions: a decent, functional, modestly-earning gaming site — not a breakout platform. This model alone will not make Pixelsprout "the next Poki."

**Why do it anyway:** near-zero cost and effort relative to the payoff. Keeps the site alive, growing, and earning something while Harsh is unavailable.

### Model B — Direct Developer Upload Marketplace (the real differentiator, future)
Let indie developers upload their own HTML5 games directly to Pixelsprout's own hosting, with a 50/50 revenue split, owned and controlled entirely by Pixelsprout. This is closer to what Poki, GameDistribution, and CrazyGames themselves actually are — a real catalog with real relationships, not just an embed pass-through.

**Why this is not a "tonight" or "friend can handle it" task:** requires sandboxing untrusted third-party code, malware/security scanning on every upload, storage infrastructure, and a moderation pipeline. This is a deliberate, architected build — a **post-November project**, planned and executed by Harsh directly, not delegated.

**Decision:** Model A runs now, on autopilot, during monk mode. Model B is parked as a written idea until December 2026+.

---

## 3. Current Technical Setup

- **Hosting:** Vercel (Hobby/free tier) — auto-deploys on every GitHub push
- **Repo:** github.com/harshyadavv2456/Pixelsprout, linked to Vercel
- **Domain:** playpixelsprout.com — purchased via Namecheap (~₹675/year, no lock-in)
- **Stack:** Plain HTML/CSS/JS, no framework, no backend, no database
- **Design system:** Built around Harsh's AI-generated Pixelsprout mascot logo — deep space-navy palette (sprout green, star gold, heart pink, sky blue accents), Press Start 2P pixel-game font for headlines, Inter for body text
- **Site features:** Live search/filter bar, genre-sectioned game grid, custom SVG icons per game, animated marquee ticker, legal pages (Privacy, Terms), sitemap.xml, robots.txt

**Important open item — Vercel Hobby tier restriction:** the free Vercel tier is non-commercial only per Vercel's own terms. Before turning on AdSense or any monetization, either:
- Upgrade to Vercel Pro ($20/month), **or**
- Migrate the static files to Cloudflare Pages (free, explicitly allows commercial/ad-supported sites)
This has not been resolved yet — decide before flipping on ads, not after approval comes through.

---

## 4. The Three Embed Platforms — What Each Actually Does

All three are the same *category* of tool (HTML5 game embed networks with ad revenue share) but are **not interchangeable** — apply to all three, don't pick just one:

| Platform | What it gives you |
|---|---|
| **GameDistribution** | Largest, oldest, most beginner-friendly network. Publisher dashboard → browse catalog → copy iframe embed code → paste into your site. |
| **GamePix** | Similar mechanism, different (partially overlapping) catalog, own dashboard and payout system. |
| **CrazyGames Dev Portal** | Same mechanism again, its own catalog and terms. |

**How it actually works, mechanically:**
1. Apply as a publisher on each platform's site
2. Get approved (review takes days, no way to speed this up)
3. Browse their dashboard's game catalog, pick titles
4. Copy the `<iframe>` embed code they provide, paste into a new page on Pixelsprout
5. The game itself stays hosted on **their** servers — Pixelsprout just displays it in a window
6. Their ad network shows ads inside that iframe automatically
7. Ad revenue is split (~50/50, varies) and paid out through **their own separate payout dashboard** — not through Pixelsprout's AdSense account

**Two separate revenue streams, don't confuse them:**
- **Pixelsprout's own 8 games + general site traffic** → monetized via Pixelsprout's own AdSense account, 100% of that revenue is Harsh's
- **Embedded third-party games** → monetized via each platform's own ad system, paid out to Harsh via their separate payout system, at their revenue-share rate

**Reality check on what you actually get:** not household names like Subway Surfers or Temple Run — those are locked into exclusive direct deals with Poki specifically. What's actually available: the long tail of generic HTML5 titles — puzzle, io-games, casual arcade, hidden-object, cooking/dress-up games. Real, free, legally embeddable content — just not recognizable brand-name games.

---

## 5. Tonight's Checklist (in order)

1. ✅ Confirm Namecheap domain purchase — playpixelsprout.com
2. Connect domain to Vercel: Vercel project → Settings → Domains → add domain → update DNS records at Namecheap as instructed
3. Submit sitemap to Google Search Console
4. Apply to Google AdSense
5. Apply to GameDistribution Direct Game Integration (publisher signup)
6. Apply to GamePix Partner program
7. Apply to CrazyGames Developer Portal
8. Resolve Vercel Hobby-tier commercial restriction before ads go live (Vercel Pro or Cloudflare Pages migration)

---

## 6. Handoff Plan — For Whoever Runs This During Monk Mode (June/July–November 2026)

**Ownership stays with Harsh, execution is delegated:**
- All accounts (AdSense, GameDistribution, GamePix, CrazyGames, Namecheap domain, Vercel/hosting) remain under **Harsh's name, email, and payout details** — no exceptions
- The friend/operator gets **GitHub collaborator access to the code repository only** — not ownership of any revenue-bearing account

**Weekly scope for the operator, once platforms are approved:**
- Log into each embed platform's dashboard
- Pick 2–3 new games per week from the available catalog
- Copy the embed code, create a new page on the site, add the game card to the homepage grid
- That's the entire recurring task — no design changes, no new services, no new spending, no branding changes

**Guardrails:**
- No new sign-ups, subscriptions, or spending without Harsh's explicit approval
- No changes to branding, layout, or core site structure
- Anything outside the weekly scope above waits until Harsh is reachable again
- **No check-ins required or expected until December 2026** — the operator runs independently within this scope, doesn't need Harsh's sign-off for routine additions

**What is explicitly NOT in scope during this period:**
- The direct-developer-upload marketplace (Model B above) — parked until Harsh actively resumes
- Any hosting migration, domain changes, or new monetization experiments
- Any rebrand or redesign beyond what's already built

---

## 7. Post-November Revisit Checklist

When Harsh resumes active involvement (December 2026+):
- Review how many embedded games were added and check actual ad revenue from each platform's payout dashboard
- Decide whether to invest in Model B (direct developer upload marketplace) — this requires real technical planning: upload sandboxing, malware scanning, storage, moderation
- Reassess whether Vercel Pro / Cloudflare Pages migration happened and whether it's working as intended
- Decide whether the "generic embed aggregator" ceiling is acceptable long-term, or whether it's time to invest in real differentiation (direct developer relationships, original exclusive content, dedicated distribution strategy)

---

*This document is the single source of truth for Pixelsprout's status, plan, and handoff terms as of July 27, 2026. Update it directly rather than creating parallel notes.*
