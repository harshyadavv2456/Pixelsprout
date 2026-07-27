# SOP — Adding a New Game to Pixelsprout (via GamePix)

This is the exact procedure, based on the first real game we added (Bus Driver Simulator 3D). Follow it step by step for every new game.

---

## Step 1 — Find a game

1. Go to **my.gamepix.com/dashboard**, log in
2. Left sidebar → **Games Catalog**
3. Browse the list (you can filter by Category or sort by Quality)
4. Click into any game that looks good

## Step 2 — Copy the game's details

On the game's detail page, copy these exact values (all shown as labeled fields):
- **TITLE** — the game's name
- **EMBED CODE** — the full `<iframe>` code block
- **DESCRIPTION** — the game's description text
- **CATEGORY** — what genre GamePix classifies it as
- **THUMBNAILURL** — the direct image link for the game's icon

## Step 3 — Create the game's own page

Create a new file in the `games/` folder. Name it using the game's title in lowercase with hyphens (e.g. `bus-driver-simulator-3d.html`).

Use this exact template — replace the bracketed parts with the game's real details:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="../assets/logo-icon.png">
<title>[GAME TITLE] — Pixelsprout</title>
<meta name="description" content="Play [GAME TITLE] free online. [SHORT DESCRIPTION], no download needed.">
<link rel="stylesheet" href="../styles.css">
<script defer src="/_vercel/insights/script.js"></script>
<style>
  .embed-frame-wrap {
    width: 100%;
    max-width: 480px;
    aspect-ratio: 480 / 320;
    border-radius: 8px;
    overflow: hidden;
    background: #000;
  }
  .embed-frame-wrap iframe {
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }
  .source-note {
    margin-top: 4px;
    font-size: 11px;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }
</style>
</head>
<body>
<div class="game-shell">
  <a class="back-link" href="../index.html">← back to Pixelsprout</a>
  <h1 class="game-title">[GAME TITLE]</h1>
  <div class="game-meta">[CATEGORY] · hosted via GamePix</div>

  <div class="game-board-frame">
    <div class="embed-frame-wrap">
      <iframe src="[THE URL FROM THE EMBED CODE]" scrolling="no" allowfullscreen title="[GAME TITLE]"></iframe>
    </div>
    <p class="how-to">[FULL DESCRIPTION FROM GAMEPIX]</p>
    <p class="source-note">Game provided via GamePix</p>
  </div>
</div>
</body>
</html>
```

**Note:** only the `src="..."` URL from the embed code is needed, not the whole `<iframe>` tag GamePix gives you — our page already has its own styled wrapper, so just pull the URL out of their code.

## Step 4 — Add the card to the homepage

Open `index.html`. If the game's category (genre) already has a section on the homepage, add the card inside that section's `<div class="grid" data-grid>`. If it's a brand-new genre, create a new section following this pattern (copy an existing one and edit):

```html
<div class="category gold" data-section>
  <span class="bar"></span>
  <h2>[GENRE NAME]</h2>
  <span class="count">[N] games</span>
</div>
<div class="grid" data-grid>
  <a class="card" href="games/[filename].html" data-name="[game title in lowercase]">
    <span class="icon-tile gold" style="padding:0; overflow:hidden;">
      <img src="[THUMBNAILURL]" alt="" style="width:100%; height:100%; object-fit:cover; border-radius:9px;">
    </span>
    <div class="card-body">
      <h3>[GAME TITLE]</h3>
      <p>[ONE-LINE SHORT DESCRIPTION]</p>
    </div>
  </a>
</div>
```

Use the color class `gold`, `teal`, or `signal` on both the `.category` div and the `.icon-tile` span — rotate through these three for visual variety across genres.

**Also update, in the same `index.html` file:**
- The `<strong id="game-count">` number in the hero stats — increase by 1
- The genres count next to it, if this was a new genre
- The `names` array inside the `<script>` at the bottom of the page (the marquee ticker) — add the new game's title in capitals

## Step 5 — Update the sitemap

Open `sitemap.xml`. Add one line for the new game, anywhere in the list before the closing `</urlset>`:

```xml
<url><loc>https://playpixelsprout.com/games/[filename].html</loc><priority>0.7</priority></url>
```

## Step 6 — Push and confirm

```bash
git add .
git commit -m "Add [game title]"
git push
```

Wait ~60 seconds for Vercel to redeploy, then check `playpixelsprout.com` to confirm the new game card appears and the game actually plays correctly in its embedded frame.

## Step 7 — Repeat

That's the entire loop. Realistic pace: 5-10 minutes per game once you've done it a couple of times. Doing 2-3 per week is a reasonable, sustainable cadence — no need to rush or batch a huge number at once.

---

*This SOP reflects the exact process used for the first embedded game (Bus Driver Simulator 3D, added July 27, 2026). If GamePix changes their dashboard layout later, the core steps (find game → copy embed URL + details → build page → add card → update sitemap → push) stay the same even if the exact screens look different.*
