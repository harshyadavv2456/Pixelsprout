"""Adds static FAQPage JSON-LD to every games/*.html (idempotent). Q/A text matches the visible
'At a glance' FAQ rendered by assets/redesign/redesign.js, so markup and on-page content agree.
Run after generators: python3 add-faq-jsonld.py"""
import glob, html, json, os, re
R = os.path.dirname(os.path.abspath(__file__))
def faq(title, genre):
    return [(f"Is {title} free to play?", f"Yes. {title} is free on Pixelsprout and plays in your web browser with no download or sign-up."),
            (f"Can I play {title} on my phone?", "Yes, it runs in a modern mobile browser. Rotate to landscape or use full screen for the best view."),
            (f"What kind of game is {title}?", f"{title} is a {genre.lower()} game. Find more in the {genre} section."),
            ("Do I need to install anything?", "No. Pixelsprout games are HTML5 and load directly in the page.")]
n = 0
for f in glob.glob(os.path.join(R, "games", "*.html")):
    t = open(f, encoding="utf-8").read()
    if "FAQPage" in t or "</head>" not in t or 'class="game-page' not in t: continue
    m = re.search(r'class="game-bar__title"[^>]*>(.*?)<', t, re.S) or re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    if not m: continue
    title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    g = re.search(r'"@type":\s*"VideoGame".*?"genre":\s*"([^"]+)"', t, re.S)
    genre = g.group(1) if g else "Arcade"
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq(title, genre)]}
    tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    open(f, "w", encoding="utf-8").write(t.replace("</head>", tag + "</head>", 1)); n += 1
print(n, "pages updated")
