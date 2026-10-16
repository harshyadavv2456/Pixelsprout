"""Builds small JSON chunks for the redesign JS (homepage trending/collections, game-page Play next).
Run: python3 build-redesign-data.py  (reads games-index.json, popular-games.json, assets/originals.json)"""
import json, os, re
R = os.path.dirname(os.path.abspath(__file__))
L = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))
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
