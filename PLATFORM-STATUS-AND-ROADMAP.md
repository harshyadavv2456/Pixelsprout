# Pixelsprout — Cold Read & Guess It Box: complete platform status

One file, everything in it. If you read only one document, read this one.

Last updated: this build round (dynamic Popular Picks + view tracking added).

---

## 1. What actually exists right now

Two new tools, live at `/cold-read/` and `/gift-file/` (branded "Guess It
Box" on-page), fully integrated into the existing static Pixelsprout site
(2,890+ games, Vercel-hosted, GamePix + AdSense monetized).

**Cold Read** — Akinator-style yes/no guessing game. ~125 seeded
entries (people, fictional characters, animals, objects, food). Weighted
scoring, no AI/LLM calls, no per-play cost. Self-learns: every confirmed
guess and every "teach me" correction blends into the shared dataset stored
in Supabase, so the pool gets more accurate over time, for everyone.

**Guess It Box** (internally `gift-file/`) — 4-question gift finder
(recipient → occasion → budget → interests). ~45 seeded gift ideas, same
self-learning mechanism. Asks India-vs-elsewhere upfront and routes budget
labels (₹ vs $) and Amazon search links (`.in` vs `.com`, with your real
Associate tags) accordingly.

Both:
- Use your real page template (`.game-shell`) — same breadcrumb, ad
  placement, spacing, similar-games strip as every other game page. Not a
  stripped-down widget.
- Have working Fullscreen, Favorite, Share, and Recently-Played tracking —
  same mechanism as every other game.
- Carry your two new AI-generated logos as branding.
- Are pinned as the first two cards in the homepage's Popular Picks row.
- Have their own AdSense banner + ribbon ad slots (same slot IDs as
  everywhere else: `4936643192` banner, `1457517471` ribbon).
- Have full SEO metadata: canonical URL, OG tags, `WebApplication` +
  `BreadcrumbList` JSON-LD schema, entries in `sitemap.xml`.
- Are backed by Supabase (Postgres via REST, no SDK dependency) — two
  tables: `kv_store` (the tools' own datasets) and `game_views` (new, see
  §3).

---

## 2. Everything fixed this round (so you know what changed and why)

| Problem you reported | Root cause | Fix |
|---|---|---|
| Budget stuck in ₹ even choosing "elsewhere" | Budget list was hardcoded to INR, region only affected the Amazon link | Two budget lists (`BUDGETS_IN`/`BUDGETS_US`), picked by the region you already chose |
| Same question every single game | `decide()` always picked the single mathematically-best next question | Now picks randomly among the top few equally-informative questions |
| Voldemort / Captain America failed | Dataset only had 50 entries | Expanded to ~125 people/characters/animals/objects/food |
| **Kept guessing wrong names, never asked "what was it"** | Real bug: once every distinguishing question was used up, it just kept re-guessing its next-best candidate forever, never reaching the teach step | Hard cap: after 3 wrong guesses in one round, it now always asks you to teach it |
| Giant black box swallowing the page | `min-h-screen` (force full viewport height) was a leftover from the original standalone-artifact prototype | Removed from both tools' root containers |
| Opened as a small popup, not a real page | Pill buttons opened an iframe modal | Modal system removed entirely. Homepage cards and the new floating badge both do plain navigation to the real page |
| Fullscreen/Favorite/Share didn't work on the tool pages | The shared script only recognized `/games/*.html` URLs | Generalized to recognize tool pages via a `data-tool-slug` attribute; added a real fullscreen button |
| Tools only discoverable if you scroll to the homepage | No presence elsewhere on the site | Added a small dismissible floating badge (bottom-right, not a popup) that shows on every page once `pixelsprout-features.js` is loaded there — **you need to run `python add-features-to-site.py` once** so your 42 category pages (which never had the script at all) pick it up too |
| Popular Picks was a fixed, hand-picked list forever | No visit tracking existed | New: real view-count tracking (§3), Cold Read + Guess It Box pinned first, the other 8 slots now rank by actual traffic once there's enough of it |

---

## 3. New: popularity-ranked homepage

**What changed:** the 8 non-tool cards in "Popular Picks" used to be a
permanently fixed list. Now:

- **Cold Read and Guess It Box are permanently pinned first** — not
  ranked, always there, as you asked.
- The other 8 slots are filled by your actual most-viewed real games,
  recalculated on every homepage load from live data.
- **Cold-start safe:** until there's enough tracked traffic (fewer than 4
  ranked games with data), it silently falls back to the original curated
  list — nothing ever looks empty or broken.

**How it works technically:**
- Every real game page fires one small, non-blocking `POST
  /api/track-view` call on load (fire-and-forget — a failed call never
  affects the page).
- That hits a new Postgres function `increment_view()` in Supabase, which
  atomically increments a per-slug counter (atomic matters here — a plain
  "read, add one, write back" would lose counts when two visitors land on
  a page in the same second).
- The homepage calls `GET /api/popular-games` on load, gets the top 20
  slugs by view count, and rebuilds the 8 ranked cards from your existing
  on-page game cards (no extra fetch needed — the real card HTML for every
  game is already in the page).

**Setup required (new table, new function):** see §7 below — one more
SQL block to run in Supabase, same place as before.

---

## 4. Would these get smarter over time? Yes — mechanism, honestly stated

- **Cold Read / Guess It Box datasets**: every confirmed guess/match blends
  a small correction (weight 0.15) into that entry's attribute vector in
  Supabase; every "teach me" correction blends a bigger one (0.35) or adds
  a brand-new entry. This is real, persistent, shared across all visitors
  — not per-browser. It was working correctly the whole time; the reason
  it didn't *look* like it was learning is the wrong-guess-loop bug in §2,
  which is now fixed.
- **Popular Picks ranking**: literally recalculated from live traffic
  every load, so yes, it "gets smarter" in the sense of staying current —
  though this is closer to "reflects reality" than "learns," worth being
  precise about.
- Neither of these involves an AI/LLM model. Both are transparent, cheap,
  deterministic-given-the-data algorithms. That's a feature, not a
  limitation — zero per-play cost, and you can inspect exactly why any
  guess or recommendation happened.

---

## 5. SEO — current status

Done for both new pages:
- Canonical URLs, unique title/meta description
- OG tags (title, description, image using the new logos)
- `WebApplication` + `BreadcrumbList` JSON-LD schema
- Listed in `sitemap.xml`
- Real on-page content (the "how it works" paragraphs) — not thin/empty
  pages, which matters for both ranking and avoiding a low-quality-content
  flag
- No entry popups anywhere (avoids Google's intrusive-interstitial
  penalty) — the floating badge is deliberately small, corner-anchored,
  and dismissible

Still on you (can't be done from code):
- **Submit both URLs via IndexNow** the same way you already do for new
  games — you have the key file and presumably a script/process for this
  already; just add these two URLs to whatever you're already running.
- **Google Search Console** will pick up both pages on its own crawl
  schedule, or you can request indexing manually for a faster first crawl.
- Backlinks / external mentions — no code fixes this, only real promotion
  does (see §8).

---

## 6. Ads — current status

Both tool pages carry the same AdSense unit (`pub-8466016918717424`) in
the same two placements every game page uses: a banner slot
(`4936643192`) above the content, a ribbon slot (`1457517471`) below it.
Nothing else was changed about your AdSense setup — I don't have visibility
into your AdSense account's approval/review status, payment details, or
policy compliance beyond what's in the code; that's entirely on the
Google AdSense dashboard side.

---

## 7. Setup — everything you need to run, in order

### 7.1 If you haven't already (Supabase basics)

Project created, `kv_store` table created, `service_role` key wired into
Vercel as `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`, table privileges
granted. If you did all of this already (you have — the tools are live),
skip to 7.2.

### 7.2 New: `game_views` table + `increment_view()` function

Supabase → SQL Editor → New query → paste and run:

```sql
create table game_views (
  slug text primary key,
  views bigint not null default 0,
  updated_at timestamptz not null default now()
);

alter table game_views enable row level security;
grant select, insert, update on public.game_views to service_role;

create or replace function increment_view(p_slug text)
returns void
language sql
as $$
  insert into game_views (slug, views, updated_at)
  values (p_slug, 1, now())
  on conflict (slug) do update
    set views = game_views.views + 1,
        updated_at = now();
$$;

grant execute on function increment_view(text) to service_role;
```

No new env vars needed — reuses the same `SUPABASE_URL` /
`SUPABASE_SERVICE_ROLE_KEY` already configured.

### 7.3 Files to copy onto your PC

At `E:\PixelSprout\Pixelsprout`:

| File | Action |
|---|---|
| `api\track-view.js` | **New** |
| `api\popular-games.js` | **New** |
| `api\_supabase.js` | **Replace** (added generic REST/RPC helpers) |
| `index.html` | **Replace** (dynamic Popular Picks ranking script) |
| `pixelsprout-features.js` | **Replace** (view tracking, floating badge, modal removed, tool-page detection) |
| `cold-read\index.html` | **Replace** |
| `gift-file\index.html` | **Replace** |

### 7.4 Also run this once (propagates the floating badge site-wide)

```bash
python add-features-to-site.py
```

Already in your repo, safe to re-run, only touches files that don't yet
have the script tag (your 42 category pages).

### 7.5 Push

```bash
git add .
git commit -m "Dynamic popularity-ranked homepage, view tracking, bug fixes"
git push
```

### 7.6 Verify

```bash
curl -X POST https://playpixelsprout.com/api/track-view -H "Content-Type: application/json" -d "{\"slug\":\"tank-1990\"}"
curl https://playpixelsprout.com/api/popular-games
```

First command should return `{"ok":true}`. Second should eventually show
`tank-1990` with `views` incrementing each time you re-run the first.
Then reload the homepage a few times — once 4+ real games have tracked
views, the 8 non-pinned cards will start reflecting them instead of the
static fallback list.

---

## 8. Marketing — what actually moves the needle from here

Code changes don't create traffic by themselves. What you already have
running (per your own notes): Pinterest auto-posting pipeline, GitHub
Actions daily game additions, IndexNow instant indexing, GA4 tracking.
That's a solid discovery-automation base. What's realistically worth doing
next, roughly in order of effort-to-impact:

1. **Let the floating badge + pinned homepage cards do their job first.**
   Every one of your 2,890+ game pages is now a discovery surface for
   these two tools, for free, as of this deploy. This alone is probably
   your highest-leverage move and it's already done.
2. **Cross-promote inside Cold Read / Guess It Box themselves** — e.g. a
   "you might also like" strip pointing back to popular games, mirroring
   what game pages already do for each other. (Not built yet — small
   follow-up if you want it.)
3. **Content marketing around Guess It Box specifically** — "gift ideas
   for [X]" is a genuinely large, low-competition-for-you search category.
   The SEO landing paragraph already on the page is a start; a handful of
   real short articles (not AI-generated word-count-padding — actual
   useful guidance) would compound over months, not days.
4. **Pinterest** is already your strongest existing channel per your
   notes — a gift-finder tool is a very natural fit for Pinterest's
   audience intent (people search Pinterest specifically for gift ideas).
   Worth a dedicated board/pin series once Pinterest's Standard access
   upgrade comes through.
5. **Reddit** — relevant subreddits exist for both "guessing games" and
   "gift ideas," but this only works if you participate as a real person
   first and mention the tool naturally later; pure link-drops get
   removed and can get accounts banned. Slower, but durable if done right.
6. **Short-form video (TikTok/Reels/Shorts)** — Cold Read in particular is
   inherently demo-able in 15-30 seconds ("I made an AI-less guessing game
   that gets smarter every time it's played, watch it fail then learn").
   This is the one channel here with real viral upside, but it needs
   actual video content, which is effort I can't do for you.
7. **Amazon Associates compliance** — get the India account past its
   3-sales/180-day provisional requirement and finish the US W-8BEN before
   leaning on Guess It Box's affiliate links as a real revenue driver —
   without an active Associates account the links still work as plain
   Amazon search links, they just don't earn commission.

None of this is code I can ship for you tonight — it's ongoing
work/decisions on your side. Flagging it honestly rather than pretending a
deploy solves distribution.

---

## 9. Financial projections — read this section's caveats before the numbers

**I am not a financial advisor, and I don't have access to your live
analytics, AdSense earnings, or GamePix revenue share statements.** Every
number below is an illustrative order-of-magnitude scenario built from the
assumptions your own prior competitive-analysis modeling used (Year 1
~$6/month → Year 5 ~$316/month for Pixelsprout overall, per your notes),
extended with rough, clearly-stated assumptions about what these two new
tools plus the dynamic homepage might add on top. Treat every figure as a
"could plausibly land somewhere near this, if traffic grows roughly this
way" range, not a forecast, and not a promise. Actual results depend
almost entirely on traffic acquisition (§8), which nothing in this file
guarantees.

**Assumptions used (stated so you can disagree with any of them):**
- Blended AdSense RPM of $1.50–$4.00 per 1,000 pageviews (wide range
  because India-heavy traffic earns meaningfully less per pageview than
  US/UK-heavy traffic; your current audience mix is unknown to me)
- GamePix revenue share continues at whatever rate your existing
  agreement specifies (I don't have that figure — treated as already
  baked into your baseline site revenue, not modeled separately here)
- Amazon affiliate: 1–4% commission depending on category, applied only
  once both Associates accounts are active and past their
  provisional/compliance requirements
- Two new tools add engagement (more pages/session, longer sessions) more
  than they add net-new visitors on their own — most of their traffic
  value in the early months comes from better-retaining existing visitors
  and the free cross-promotion from your existing 2,890+ game pages, not
  from the tools independently ranking well in search (that takes months)
- No paid acquisition spend assumed in any scenario

| Horizon | Conservative | Base case | Optimistic |
|---|---|---|---|
| **3 months** | Tools mostly get seed traffic from existing site visitors via the badge/homepage cards. Datasets fill in nicely from play volume. Revenue impact: negligible, within existing site noise (~+$5–15/mo total site incremental) | Modest engagement lift (session length, pages/session) starts showing in GA4. +$15–40/mo incremental | Cold Read gets some organic sharing traction (it's inherently shareable). +$40–100/mo incremental |
| **6 months** | Amazon Associates compliance sorted, Pinterest gift-board traction beginning. +$30–70/mo | Guess It Box starts ranking for a handful of long-tail gift-idea searches. +$70–150/mo | One piece of content or short-form video gets real traction. +$150–350/mo |
| **12 months** | Steady incremental engagement value, Associates commissions trickling in. +$100–250/mo | Meaningful long-tail SEO traffic to Guess It Box, Cold Read has a returning-visitor base. +$250–600/mo | Genuine organic/viral moment on one channel materially shifts overall site traffic, not just these two tools. +$600–1,500/mo |
| **24 months** | Tools are a stable, minor supplementary revenue line. +$200–500/mo | Both tools are established site features with real recurring usage and a meaningfully larger combined dataset (more accurate = better retention). +$500–1,200/mo | Compounding SEO + social presence, tools become a recognizable part of the site's identity. +$1,200–3,000/mo |
| **36 months** | Same trajectory, larger base site traffic overall. +$400–900/mo | Datasets mature (thousands of taught entries), tools rank for a real portfolio of long-tail terms. +$900–2,200/mo | Genuinely differentiated feature vs. every other GamePix-clone site, contributes noticeably to overall site identity/retention, not just incremental ad revenue. +$2,200–5,000+/mo |

**The honest summary:** in every scenario, these two tools are a
**differentiation and retention play first, a direct revenue driver
second.** Their real value case — per your own reasoning when we scoped
this — was "stands out from thousands of identical GamePix-clone
competitors," not "this specific feature makes $X." The financial ranges
above are there because you asked for them, not because they're precise;
the true determinant of where you land in this table is entirely §8
(marketing), not anything in the code.

---

## 10. What's genuinely NOT done — full honesty

- AdSense approval status — outside my visibility, entirely on Google's
  side.
- Pinterest Standard access, Amazon US W-8BEN — both were already
  in-progress per your notes, unaffected by this work, still need your
  action.
- No content marketing / articles / video actually created — only the
  infrastructure and the one on-page SEO paragraph per tool.
- `gifts.playpixelsprout.com` subdomain — code is ready
  (`vercel.json`), DNS/domain attachment is a dashboard action only you
  can do.
- Cross-tool "you might also like" recommendations between Cold Read and
  Guess It Box — not built, flagged in §8 as a reasonable next step.
- No load-testing done on the new `/api/track-view` endpoint at real
  scale (2,890 games × real traffic) — Supabase's free tier has request
  limits; if the site's daily pageviews are large enough to approach them,
  that's worth monitoring in the Supabase dashboard before assuming this
  scales indefinitely for free.
