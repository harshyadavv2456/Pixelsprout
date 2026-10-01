# SEO Bot queue — how bot-written guide pages get published

The SEO Bot (Grok Bot) writes guide pages for games it has **actually played**.
It never edits HTML and never pushes to `main`.

```
SEO Bot ──commits JSON──▶ branch: seo-queue / folder: seo-queue/<game-slug>.json
                                   │
Daily workflow (.github/workflows/daily.yml, 6:00 UTC)
  └─ content-engine/apply_queue.py  validate → escape → render → lock pages
  └─ content-engine/seo_cleanup.py  template pages noindex, real pages in sitemap
  └─ one commit to main → Vercel deploys
                                   │
Result for the bot ◀── content-engine/queue-report.json on main (published / rejected + reasons)
```

## File rules

- One file per game, named exactly `<game-slug>.json` (slug = the part after `/games/` in the game URL, without `.html`).
- `"played": true` is required. Only write about what you saw while playing.
- Include any of the 5 page types. Missing types keep their current page.
- Plain text only: no HTML, no `<` or `>`, no links (internal links are added automatically), no placeholder text.
- Page types you publish are **locked**: the automatic Groq pipeline will never overwrite them. To improve a page, push a new version of the same file — changed files are re-published.
- Max 30 files are processed per day.

## Format and limits

```json
{
  "slug": "getting-over-it",
  "played": true,
  "pages": {
    "tips": {
      "intro": "40–500 chars",
      "tips": ["5–10 items, each 30–350 chars"],
      "conclusion": "20–350 chars"
    },
    "controls": {
      "intro": "20–350 chars",
      "desktop": "30–600 chars, the real keys/mouse actions you used",
      "mobile": "30–600 chars, the real touch controls",
      "tips": ["2–6 items, each 20–300 chars"]
    },
    "beginner-guide": {
      "intro": "20–450 chars",
      "what_it_is": "80–900 chars",
      "first_steps": ["3–8 items, each 20–300 chars"],
      "who_its_for": "20–350 chars"
    },
    "similar": {
      "intro": "120–900 chars on why fans of this game will like similar games"
    },
    "faq": {
      "faqs": [{"question": "10–160 chars, ends with ?", "answer": "30–450 chars"}]
    }
  }
}
```
`faqs` needs 5–10 pairs. FAQ pages also get FAQ rich-result schema automatically.

Any page can add deeper sections (this is what makes a page a "super page"):
```json
"extra_sections": [
  {"heading": "5–90 chars", "paragraphs": ["1–4 paragraphs, each 60–800 chars"]}
]
```
Max 4 sections per page.

## "Games like X" collection pages

The 26 pages under `/games-like/` (Minecraft, Roblox, Subway Surfers, Candy Crush…) can rank for
searches about games we don't host. Their intro is written once and reused every day.
To write or replace one, push `seo-queue/collection-<slug>.json`:

```json
{"collection": "minecraft", "played": true, "intro": "150–900 chars, plain text"}
```
Allowed slugs are the folder names under `/games-like/`. Play several of the games listed on
that page first, and say what they actually have in common with the famous game.

## Checking results

`content-engine/queue-report.json` on `main` → `runs[0]` is the latest run:
- `published`: file, pages and live URLs (plus `rejected_pages` if only some pages failed)
- `rejected`: file and the exact reasons — fix them and push the file again
