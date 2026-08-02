# Cold Read & Gift File — exact setup steps (Supabase)

Everything below assumes your repo is at `E:\PixelSprout\Pixelsprout` and
you already deploy it to Vercel from GitHub, the way `DEPLOY.md` describes.

---

## PART A — Copy the files onto your PC

Unzip `pixelsprout-cold-read-gift-file.zip`. You'll see this:

```
api/
  _supabase.js
  cold-read-dataset.js
  gift-file-dataset.js
cold-read/
  index.html
gift-file/
  index.html
package.json
vercel.json
pixelsprout-features.js
sitemap.xml
```

Copy each one into `E:\PixelSprout\Pixelsprout`, matching the same folder
structure:

| From the zip | Goes to (on your PC) | Action |
|---|---|---|
| `api\_supabase.js` | `E:\PixelSprout\Pixelsprout\api\_supabase.js` | **New** — create the `api` folder if it doesn't exist, paste in |
| `api\cold-read-dataset.js` | `E:\PixelSprout\Pixelsprout\api\cold-read-dataset.js` | **New** |
| `api\gift-file-dataset.js` | `E:\PixelSprout\Pixelsprout\api\gift-file-dataset.js` | **New** |
| `cold-read\index.html` | `E:\PixelSprout\Pixelsprout\cold-read\index.html` | **New** — create the `cold-read` folder, paste in |
| `gift-file\index.html` | `E:\PixelSprout\Pixelsprout\gift-file\index.html` | **New** — create the `gift-file` folder, paste in |
| `package.json` | `E:\PixelSprout\Pixelsprout\package.json` | **New** — you don't have one yet, just drop it in |
| `vercel.json` | `E:\PixelSprout\Pixelsprout\vercel.json` | **New** — you don't have one yet, just drop it in |
| `pixelsprout-features.js` | `E:\PixelSprout\Pixelsprout\pixelsprout-features.js` | **Replace** — this overwrites your existing file (same file, just with two new pill buttons added, nothing else changed) |
| `sitemap.xml` | `E:\PixelSprout\Pixelsprout\sitemap.xml` | **Replace** — same file with 2 new `<url>` lines added at the top |

Nothing else in your repo needs to change. Don't touch `games-data.json`,
`games-index.json`, any `.py` scripts, or any existing game folder — none
of that was touched.

---

## PART B — Create the Supabase project

1. Go to **https://supabase.com** → sign in (GitHub login is fine) → **New project**.
2. Give it any name, e.g. `pixelsprout`. Pick any region. Set a database
   password (save it somewhere — you won't need it for this setup, but
   Supabase requires one to be set).
3. Wait ~1–2 minutes for it to finish provisioning.

### Create the one table you need

4. In the left sidebar, click **SQL Editor** → **New query**.
5. Paste this exactly, then click **Run**:

```sql
create table kv_store (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

alter table kv_store enable row level security;
```

That's it — one table, two columns of actual data (`key`, `value`), no other
setup. `enable row level security` with **no policies** means only requests
using the `service_role` key can touch this table (which is exactly what our
API functions use) — nothing is publicly readable or writable.

### Get your two credentials

6. Left sidebar → **Project Settings** (gear icon) → **API**.
7. You'll see:
   - **Project URL** — looks like `https://abcxyzcompany.supabase.co`
   - **Project API keys** → copy the one labeled **`service_role`** (⚠️ **not** the `anon`/`public` one — the service_role key is meant to stay secret and server-side, which is exactly what it'll be here)

Keep this browser tab open, you'll paste both into Vercel next.

---

## PART C — Add the credentials to Vercel

1. Go to your Vercel dashboard → your Pixelsprout project → **Settings → Environment Variables**.
2. Add these two, one at a time:

| Key (type exactly) | Value |
|---|---|
| `SUPABASE_URL` | the Project URL from step B.6, e.g. `https://abcxyzcompany.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | the `service_role` key from step B.7 |

3. For both, leave all three environments checked (**Production, Preview,
   Development**), then **Save**.

---

## PART D — Push and deploy

Open a terminal in `E:\PixelSprout\Pixelsprout` and run:

```bash
git add api cold-read gift-file package.json vercel.json pixelsprout-features.js sitemap.xml
git commit -m "Add Cold Read and Gift File tools, Supabase-backed"
git push
```

Vercel will pick up the push automatically (same as every deploy so far) and
this time it'll also detect the new `api/` folder and deploy those two
functions alongside your static site — no framework migration, no build
step, nothing else changes about how the site deploys.

---

## PART E — Verify it actually works

Once the deploy finishes (check the Vercel dashboard for the green
"Ready"), open a terminal and run:

```bash
curl https://playpixelsprout.com/api/cold-read-dataset
curl https://playpixelsprout.com/api/gift-file-dataset
```

- First time you run these, you should get back `{"entities":null,"gamesPlayed":0}`
  (or `matchesMade` for the gift one) — that's correct, no row exists yet.
- Then open **https://playpixelsprout.com/cold-read/** and
  **https://playpixelsprout.com/gift-file/** in a browser and actually play
  through one round of each. That first play writes the seed dataset into
  Supabase.
- Run the same two `curl` commands again — this time you should see real
  data back (a big JSON array of entities/gifts). That confirms the whole
  chain (page → API → Supabase) is working end to end.
- You can also check it visually: Supabase dashboard → **Table Editor** →
  `kv_store` → you should see two rows, `coldread:dataset` and
  `giftfile:dataset`.

If you get a `500` error with `"Storage not configured"` — the env vars in
Part C weren't picked up. Double check the names are typed exactly right
(`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) and that you redeployed after
adding them (Vercel → Deployments → ⋯ → **Redeploy** on the latest one, if
it deployed before you saved the env vars).

---

## PART F — (Optional) gifts.playpixelsprout.com subdomain

`vercel.json` already contains the rewrite rule. To actually make the
subdomain live:

1. Vercel project → **Settings → Domains** → **Add** → type
   `gifts.playpixelsprout.com` → **Add**.
2. Vercel will show you a DNS record (usually a CNAME) to add. Go to
   wherever you manage DNS for `playpixelsprout.com` (your domain registrar)
   and add exactly what Vercel shows you.
3. Wait for DNS to propagate (Vercel will show a green checkmark once it
   verifies, usually within minutes to a couple hours).

Once verified, `gifts.playpixelsprout.com` serves the Gift File page
directly. `playpixelsprout.com/gift-file/` keeps working too — same
codebase, both URLs. If you'd rather skip this for now, everything else
works fine without it.

---

## PART G — Ping IndexNow / update Search Console

Same pattern you already use for new game/category pages: submit the two
new URLs (`https://playpixelsprout.com/cold-read/` and
`https://playpixelsprout.com/gift-file/`) through whichever IndexNow script
or endpoint you're already using for the rest of the site, using the same
key file you already have (`09266bfbb51ba867175e9483e9d5fa6d.txt`). Both
URLs are already in `sitemap.xml`, so nothing else needs updating there.

---

## What to do if something looks wrong

- **Buttons don't show up on the homepage** — hard refresh
  (`Ctrl+Shift+R`) to bypass cache on `pixelsprout-features.js`.
- **Tool opens but says "Opening the file…" forever** — open browser dev
  tools (F12) → Console/Network tab on the `/cold-read/` or `/gift-file/`
  page directly (not inside the popup) and see what `/api/...` returns.
  99% of the time this is the env vars from Part C.
- **`curl` returns actual data but the page still won't load it** — check
  that `SUPABASE_URL` doesn't have a trailing slash, and that you copied the
  `service_role` key in full (it's long — easy to accidentally cut off the
  end when copying).
