# Deploying Pixelsprout to Vercel

This is a static site — no build step, no backend. That makes deployment simple.

## Option A: Deploy via Vercel's website (no terminal needed)

1. Go to https://vercel.com and sign up / log in (GitHub login is easiest).
2. Put this `pixelsprout` folder into a GitHub repo:
   - Create a new repo on github.com (e.g. `pixelsprout`).
   - Upload all the files in this folder (`index.html`, `styles.css`, `games/`) via GitHub's web upload, or `git push` if you're comfortable with git.
3. In Vercel, click **Add New → Project**, then **Import** your `pixelsprout` GitHub repo.
4. Framework preset: choose **Other** (it's plain HTML, no framework).
5. Leave build command and output directory blank — Vercel will serve the static files as-is.
6. Click **Deploy**. You'll get a live URL like `pixelsprout.vercel.app` in under a minute.

## Option B: Deploy via terminal (Vercel CLI)

```bash
npm install -g vercel
cd pixelsprout
vercel
```
Follow the prompts (link to a new project, accept defaults). It deploys instantly and gives you a URL.

## Connecting your domain

Once deployed, go to your Vercel project → **Settings → Domains**, add `pixelsprout.games` (or whichever you bought), and follow the DNS instructions Vercel shows you (usually just adding an A record or CNAME at your registrar).

## Important — read before turning on ads

Vercel's free **Hobby** tier is for non-commercial projects only. It's perfect for this build/testing phase. Once you're ready to add Google AdSense and actually monetize:

- Either upgrade this same project to **Vercel Pro** ($20/month), or
- Migrate the static files over to **Cloudflare Pages** (free, unlimited bandwidth, and explicitly allows commercial/ad-monetized sites) — since this is a plain static site with no framework lock-in, moving it is just re-uploading the same files to a new host.

Either path works from a pure hosting standpoint — the free-Vercel path is fine for now while you're building and sharing with friends, just don't flip on ads until you've upgraded or migrated.

## What's in this folder

```
pixelsprout/
├── index.html          — catalog / home page
├── styles.css           — shared design system
├── games/
│   ├── 2048.html
│   ├── snake.html
│   ├── memory.html
│   └── tictactoe.html
```

All four games are original code written for this project (not copied from any existing repo), using generic public-domain game concepts — safe to host, extend, and reskin however you like since you own them outright.
