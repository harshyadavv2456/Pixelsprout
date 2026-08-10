# Popular Games — Daily Refresh Instead of Live Lag

## The problem
`index.html` was calling `/api/popular-games` on every single homepage load.
That serverless function hit Supabase live, every time, for every visitor —
the round-trip (cold start + DB query) is what you were feeling as lag before
the "Popular Picks" section settled.

## The fix
Same data, same UI, same fallback behavior — just decoupled from live traffic:

1. `refresh-popular-games.py` — queries Supabase once, writes the ranked
   list to a static `popular-games.json` file at the repo root.
2. `.github/workflows/refresh-popular-games.yml` — runs that script once a
   day (5:00 UTC, before your existing 6:00 UTC game-add workflow) and
   commits the updated JSON. Also runnable manually from the Actions tab.
3. `index.html` — the one line that mattered: `fetch('/api/popular-games')`
   is now `fetch('/popular-games.json')`. Everything else (the fallback to
   your curated static list, the slot-filling logic, Cold Read / Guess It
   Box staying pinned) is unchanged.

Since `popular-games.json` is a plain static file at the repo root, Vercel
serves it straight off the CDN — no function cold start, no per-visitor DB
call, effectively instant.

## What was NOT touched
- `api/popular-games.js` — left in place, just no longer called by the
  homepage. Harmless if you want it later.
- `api/_supabase.js`, your `game_views` table, view-counting logic — untouched.
- Everything else in `index.html` outside that one fetch block.

## Deploy steps
1. Copy `refresh-popular-games.py` and `popular-games.json` into your repo
   root.
2. Copy `.github/workflows/refresh-popular-games.yml` into your
   `.github/workflows/` folder.
3. Copy `index.html` over your existing one (only the popular-games fetch
   block changed — worth a quick `git diff` glance since it's a big file).
4. **Add two GitHub Actions secrets** (repo → Settings → Secrets and
   variables → Actions → New repository secret) — same values you already
   have set in Vercel → Settings → Environment Variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   These are required for the new workflow to reach Supabase — GitHub
   Actions and Vercel don't share env vars automatically.
5. `git add -A && git commit -m "Refresh popular games once daily instead of live per-visit" && git push`
6. Optional: trigger the workflow once manually from the Actions tab right
   after pushing, so `popular-games.json` gets its first real data instead
   of waiting for tomorrow's 5:00 UTC run. Until then it ships as
   `{"games": []}`, which safely falls back to your existing curated list —
   same as what visitors see today.

## Verified before handoff
- `refresh-popular-games.py` passes `python3 -m py_compile`.
- Workflow YAML validated with `yaml.safe_load`.
- Confirmed exactly one remaining reference to the popular-games fetch in
  `index.html`, correctly pointing at `/popular-games.json`, and zero
  remaining references to `/api/popular-games`.
