"""Adds static FAQPage JSON-LD to every games/*.html (idempotent). Q/A text matches the visible
'At a glance' FAQ rendered by assets/redesign/redesign.js, so markup and on-page content agree.
Run after generators: python3 add-faq-jsonld.py"""
import glob, html, json, os, re
R = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, R)
from site_pages import FAQ_FREE_ANSWER, FAQ_MOBILE_ANSWER  # per-game override of the "free to play" answer (also drives the visible FAQ)
FAQ_RE = re.compile(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>\n?', re.S)
def faq(title, genre, slug=""):
    return [(f"Is {title} free to play?", FAQ_FREE_ANSWER.get(slug) or f"Yes. {title} is free on Pixelsprout and plays in your web browser with no download or sign-up."),
            (f"Can I play {title} on my phone?", FAQ_MOBILE_ANSWER.get(slug) or "Yes, it runs in a modern mobile browser. Rotate to landscape or use full screen for the best view."),
            (f"What kind of game is {title}?", f"{title} is a {genre.lower()} game. Find more in the {genre} section."),
            ("Do I need to install anything?", "No. Pixelsprout games are HTML5 and load directly in the page.")]
n = 0
for f in glob.glob(os.path.join(R, "games", "*.html")):
    t = open(f, encoding="utf-8").read()
    slug = os.path.basename(f)[:-5]
    if slug in FAQ_FREE_ANSWER or slug in FAQ_MOBILE_ANSWER:  # overridden answers are re-applied, so an older baked FAQ gets corrected
        t = FAQ_RE.sub("", t)
    if "FAQPage" in t or "</head>" not in t or 'class="game-page' not in t: continue
    m = re.search(r'class="game-bar__title"[^>]*>(.*?)<', t, re.S) or re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    if not m: continue
    title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    g = re.search(r'"@type":\s*"VideoGame".*?"genre":\s*"([^"]+)"', t, re.S)
    genre = g.group(1) if g else "Arcade"
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq(title, genre, slug)]}
    tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    new = t.replace("</head>", tag + "</head>", 1)
    if new != open(f, encoding="utf-8").read():
        open(f, "w", encoding="utf-8").write(new); n += 1
print(n, "pages updated")
