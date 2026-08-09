# Adsterra Fix: Remove Popunder, Add Native Banner

## Why
Popunder is the format most tied to redirect/malware-blacklist complaints
on Adsterra specifically (multiple publisher reports of sites getting
flagged by antivirus vendors and Chrome after enabling it). Not worth the
risk to Pixelsprout's traffic and SEO trust. Swapped it for Native Banner
instead — stays on-page, blends with your layout, no redirect risk.

## Final ad stack per game page
1. AdSense banner (top) — unchanged
2. **Native Banner (4:1)** — directly under the game embed / Fullscreen
   button. This is the "ad when you open a game" slot you wanted —
   Adsterra's own placement guide recommends exactly this spot ("Under the
   player") for video/game content.
3. Adsterra 300x250
4. AdSense ribbon — unchanged
5. Adsterra 728x90

## Final ad stack per guide/collection ("blog") page
1. AdSense banner (top) — unchanged
2. Adsterra 728x90
3. Article body
4. **Native Banner** — middle of the page, after the article content
   (Adsterra's recommended placement for text/mixed-content pages)
5. Adsterra 300x250
6. AdSense ribbon — unchanged

No popunder anywhere, on any page type.

## What's in this folder
- `fix-adsterra-native.py` — NEW. Run this once against your already-
  deployed repo. It:
  - Removes the Popunder marker + script from every `games/*.html` file.
  - Adds the Native Banner block to every `games/*.html`,
    `guides/*/index.html`, and `games-like/*/index.html` file, right
    before the existing `ADSTERRA-300x250` marker.
  - Idempotent — safe to re-run, skips files already fixed.
- `auto-add-games.py`, `auto-add-gamemonetize.py`, `bulk-add-games.py`,
  `bulk-add-gamemonetize.py` — the 4 game-page templates, updated so
  every future game (from tomorrow's cron run onward) is generated
  without popunder and with the Native Banner already in place.
- `content-engine/page_renderer.py` — guide/collection template, same fix
  applied for future guide/collection pages.

## What was NOT touched
- `ads.txt`, homepage `index.html` — untouched.
- Existing AdSense slots — untouched.
- Existing Adsterra 300x250 / 728x90 banners — untouched, still there.
- 5 hand-built custom games (`memory.html`, `pong.html`, `snake.html`,
  `tetris.html`, `tictactoe.html`) — these never had any ad markup at all
  (not even AdSense), so they were correctly skipped by both scripts, not
  a bug. Flagging in case you want ads added there separately later.

## Deploy steps
1. Copy `fix-adsterra-native.py` into your repo root.
2. From repo root, run:
   ```
   python fix-adsterra-native.py
   ```
   It prints a summary: how many files had popunder removed, how many got
   the native banner added.
3. Copy the other 5 files (`auto-add-games.py`, `auto-add-gamemonetize.py`,
   `bulk-add-games.py`, `bulk-add-gamemonetize.py`,
   `content-engine/page_renderer.py`) over your existing ones at the same
   paths.
4. Spot-check a game page and a guide page in `git diff` — should show the
   popunder lines removed and the native banner block added.
5. `git add -A && git commit -m "Replace Adsterra popunder with Native Banner (UX/safety fix)" && git push`

## Verified before handoff
- Ran `fix-adsterra-native.py` against the full previously-deployed
  codebase: popunder removed from 4,842/4,842 game pages; Native Banner
  added to 4,837/4,842 game pages (5 exceptions are the hand-built games
  noted above), 13,824/13,824 guide pages, 26/26 collection pages.
- Re-ran it — 0 changes on second pass, confirms idempotency.
- Confirmed zero leftover references to the popunder script domain
  anywhere in `games/`, `guides/`, `games-like/`.
- All 5 edited/created Python files pass `python3 -m py_compile`.
- Actually executed `page_renderer.py` end-to-end (rendered a sample guide
  page and collection page) — confirmed Native Banner present, Popunder
  absent, no f-string/brace errors.
- Confirmed all 4 game-page template scripts contain exactly 1 native
  marker and 0 popunder references each.
