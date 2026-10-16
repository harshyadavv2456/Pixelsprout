"""Builds small JSON chunks for the redesign JS (homepage trending/collections, game-page Play next).
Run: python3 build-redesign-data.py  (reads games-index.json, popular-games.json, assets/originals.json)"""
import json, os, re
R = os.path.dirname(os.path.abspath(__file__))
L = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))
try:  # snapshot before this run overwrites home.json (keeps the last baked Games of the week)
    _PREV_HOME = L("assets/redesign/home.json")
except (OSError, ValueError):
    _PREV_HOME = {}
idx = L("games-index.json"); pop = L("popular-games.json")["games"]; orig = L("assets/originals.json")
by = {g["slug"]: g for g in idx}
KB = re.compile(r"\b(arrow keys|wasd|keyboard|space ?bar|press [a-z] key|mouse wheel|right[- ]click)\b", re.I)
TOUCH = re.compile(r"\b(tap|touch|swipe|mobile|phone|tablet)\b", re.I)
_pf = {}
def phone_ok(slug):
    """Phone-friendly heuristic: game page text mentions touch controls, or does not rely on keyboard-only controls."""
    if by.get(slug, {}).get("phone") is False: return 0  # explicit desktop-only flag in games-index.json
    if slug not in _pf:
        try: t = open(os.path.join(R, "games", slug + ".html"), encoding="utf-8").read()
        except OSError: t = ""
        m = re.search(r"<!--ps:desc-->(.*?)<!--/ps:desc-->", t, re.S); t2 = (m.group(1) if m else "") + " " + " ".join(re.findall(r'class="how-to"[^>]*>(.*?)</', t, re.S))
        _pf[slug] = 1 if (TOUCH.search(t2) or not KB.search(t2)) else 0
    return _pf[slug]
slim = lambda g: {"s": g["slug"], "t": g["title"], "c": g.get("category", ""), "i": g.get("thumbnail", ""), "m": phone_ok(g["slug"])}
osl = [o["slug"] for o in orig]
for o in orig: by.setdefault(o["slug"], o)
out = os.path.join(R, "assets", "redesign"); os.makedirs(os.path.join(out, "cat"), exist_ok=True)
originals = [slim(by[s]) for s in osl if s in by]
trending = [dict(slim(by[p["slug"]]), v=p.get("views", 0)) for p in pop if p["slug"] in by]
newest = [slim(g) for g in idx[:24]]
cats = {}
for g in idx: cats.setdefault(g.get("category") or "Other", []).append(slim(g))
for o in originals: cats.setdefault(o["c"] or "Other", []).insert(0, o)
slug = lambda c: re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
top = sorted(cats, key=lambda c: -len(cats[c]))[:6]
home = {"originals": originals, "trending": trending[:24], "newest": newest,
        "collections": [{"name": c, "slug": slug(c), "games": cats[c][:12]} for c in top],
        "all": [g["slug"] for g in idx]}

json.dump(home, open(os.path.join(out, "home.json"), "w"), separators=(",", ":"))
for c, gs in cats.items():
    json.dump(gs[:40], open(os.path.join(out, "cat", slug(c) + ".json"), "w"), separators=(",", ":"))
print(len(idx), "games;", len(cats), "categories")
# ---- Top picks (large cards on homepage + category pages) ----
# Only games with a real gameplay/creator thumbnail qualify. Generated title cards and logo fallbacks are skipped.
PLACEHOLDER_THUMBS = {"raveswords", "wildbrush", "get-in-the-shelter", "spellwright", "sojourner"}
try:  # generated title cards are registered here by the add-game tooling
    PLACEHOLDER_THUMBS |= set(L("assets/thumbs/placeholders.json"))
except (OSError, ValueError):
    pass
FOUNDPLAY_LIVE = ["surfd", "flowline-snowboarding", "billiards", "hollowlands", "gravecrawl", "graveyard-pinball",
                  "apex-formula-2026", "infinite-powder", "lantern-valley", "polygolf", "garage-to-gigawatt"]
ALWAYS = ["getting-over-it"]
def real_thumb(g):
    t = g.get("thumbnail") or ""
    if not t or "logo-icon" in t or g["slug"] in PLACEHOLDER_THUMBS:
        return False
    if t.startswith("/assets/thumbs/") or "playpixelsprout.com/assets/thumbs/" in t:
        f = os.path.join(R, "assets", "thumbs", g["slug"] + ".webp")
        if not os.path.exists(f):
            return False
        try:  # generated title cards are a flat two-tone gradient: very few distinct colours
            from PIL import Image
            if len(Image.open(f).convert("RGB").resize((32, 16)).getcolors(512) or range(512)) < 40:
                return False
        except ImportError:
            pass
    return True
def pick(g, tag):
    d = slim(g); d["tag"] = tag; return d
popular = [p["slug"] for p in pop if p["slug"] in by]
chosen, picks = set(), []
def take(slugs, tag, limit):
    n = 0
    for s in slugs:
        g = by.get(s)
        if g and s not in chosen and real_thumb(g) and n < limit and len(picks) < 12:
            picks.append(pick(g, tag(g))); chosen.add(s); n += 1
take(ALWAYS, lambda g: "Classic", 1)
take(FOUNDPLAY_LIVE, lambda g: "New on Pixelsprout", 7)
take(popular, lambda g: "Most played", 12)
home["picks"] = picks

# ---- Hero collage: crime/city action games with real art ----
COLLAGE = ["gangster-crimes-online-6-mafia-city", "gta-vi-beat-em-up", "the-boss-of-mong-kok", "grand-crime-auto-6",
           "blocky-dude-gangster-auto-city", "crime-theft-gangster-paradise", "grand-city-driving-2"]
def big(d):
    d["i"] = re.sub(r"([?&]w=)\d+", r"\g<1>400", d["i"]); return d
home["collage"] = [big(slim(by[s])) for s in COLLAGE if s in by and real_thumb(by[s])][:5]
# ---- Games of the week: top pageviews (7d) from a report file passed via PS_ANALYTICS_REPORT.
# The report URL/key never live in the repo; without a report we keep the last baked list, else fall back to Top picks.
def _week():
    rp = os.environ.get("PS_ANALYTICS_REPORT")
    if rp:
        try:
            tg = json.load(open(rp)).get("topGames") or []
            sl = [re.sub(r"^/games/|\.html$", "", x.get("path", "")) for x in sorted(tg, key=lambda x: -x.get("pageviews", 0))]
            l = [slim(by[s]) for s in sl if s in by and real_thumb(by[s])][:8]
            if l:
                return l, "analytics-7d"
        except (OSError, ValueError) as e:
            print("analytics report unreadable:", e)
    try:
        prev = _PREV_HOME
        if prev.get("weekSrc") == "analytics-7d" and prev.get("week"):
            return [slim(by[g["s"]]) for g in prev["week"] if g["s"] in by and real_thumb(by[g["s"]])], "analytics-7d"
    except (OSError, ValueError):
        pass
    return [dict(p) for p in picks[:8]], "top-picks-fallback"
home["week"], home["weekSrc"] = _week()
print("games of the week (%s): %s" % (home["weekSrc"], ", ".join(g["s"] for g in home["week"])))
print("collage:", ", ".join(g["s"] for g in home["collage"]))
json.dump(home, open(os.path.join(out, "home.json"), "w"), separators=(",", ":"))
os.makedirs(os.path.join(out, "picks"), exist_ok=True)
rank = {s: i for i, s in enumerate(ALWAYS + FOUNDPLAY_LIVE + popular)}
for c, gs in cats.items():
    pool = [by[g["s"]] for g in gs if g["s"] in by]
    pool = sorted(pool, key=lambda g: (0 if g["slug"] in osl else 1, rank.get(g["slug"], 10**6)))
    cp = [pick(g, "Original" if g["slug"] in osl else ("Popular" if g["slug"] in rank else c)) for g in pool if real_thumb(g)][:8]
    json.dump(cp, open(os.path.join(out, "picks", slug(c) + ".json"), "w"), separators=(",", ":"))
print("top picks:", ", ".join(p["s"] for p in picks))


# ---- Just added / Game of the day / stats (homepage hero) + /new-games/ page ----
# Added date = first git commit that created games/<slug>.html (games-index.json has no date field).
import subprocess, time, datetime, html as _html
def _added_dates():
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=@%ct", "--name-only", "--", "games/"],
                         cwd=R, capture_output=True, text=True).stdout
    dates, ts = {}, None
    for line in out.splitlines():
        if line.startswith("@"): ts = int(line[1:])
        elif line.startswith("games/") and line.endswith(".html"):
            dates[line[6:-5]] = ts  # log is newest-first, so the last hit is the first add
    return dates
added = _added_dates()
now = int(time.time())
WINDOW_DAYS = 30
recent = sorted((g for g in idx if added.get(g["slug"], 0) >= now - WINDOW_DAYS * 86400),
                key=lambda g: -added[g["slug"]])
# Interim (Studio): until older add-dates are verified, "new" = only the games that went live tonight.
INTERIM_NEW_TONIGHT = ["surfd", "flowline-snowboarding", "billiards", "hollowlands", "gravecrawl", "graveyard-pinball",
               "apex-formula-2026", "infinite-powder", "lantern-valley", "polygolf", "garage-to-gigawatt"]
INTERIM_NEW = []  # dates verified 16 Oct: every game is from a dated auto-add or launch commit, never deleted, live 200
if INTERIM_NEW:
    recent = [g for g in recent if g["slug"] in INTERIM_NEW]
def _new(g):
    d = slim(g); d["a"] = added[g["slug"]]; d["ok"] = 1 if real_thumb(g) else 0; return d
home["recent"] = [_new(g) for g in recent]
home["new7"] = sum(1 for g in recent if added[g["slug"]] >= now - 7 * 86400)
home["stats"] = {"games": len(idx), "genres": len(cats)}
home["built"] = now
json.dump(home, open(os.path.join(out, "home.json"), "w"), separators=(",", ":"))

import sys as _sys
_sys.path.insert(0, R)
import site_shell as _S
_rows = "".join(
    _S.card(g).replace('<span class="card__meta">',
        f'<span class="card__meta">Added {datetime.datetime.fromtimestamp(added[g["slug"]]).strftime("%-d %b")} · ', 1)
    for g in recent)
_main = (_S.crumbs([("Home", "/"), ("New games", None)]) +
         '<header class="page-head"><p class="eyebrow">New</p><h1>New games</h1>' +
         (f'<p>The {len(recent)} games that went live on Pixelsprout on 16 October 2026.</p></header>' if INTERIM_NEW else f'<p>Every game added to Pixelsprout in the last {WINDOW_DAYS} days, newest first. {len(recent)} games.</p></header>') +
         f'<div class="grid">{_rows}</div>')
_head = _S.head("New games — Pixelsprout", _html.escape(f"Free browser games added to Pixelsprout in the last {WINDOW_DAYS} days, newest first."),
                canonical="https://playpixelsprout.com/new-games/")
os.makedirs(os.path.join(R, "new-games"), exist_ok=True)
open(os.path.join(R, "new-games", "index.html"), "w", encoding="utf-8", newline="\n").write(
    _S.page(_head, _main, body_attrs='class="category-page" data-page="new-games"', total_games=len(idx)))
_sm = os.path.join(R, "sitemap.xml"); _t = open(_sm, encoding="utf-8").read()
if "/new-games/<" not in _t:
    open(_sm, "w", encoding="utf-8").write(_t.replace("</urlset>", "  <url><loc>https://playpixelsprout.com/new-games/</loc><priority>0.8</priority></url>\n</urlset>"))
print("new in 7 days:", home["new7"], "| recent (30d):", len(recent))
