"""
Persistent NOINDEX_GUIDES list: guide pages that stay noindex,follow and out of
sitemap.xml until someone rewrites them from real play.

The list lives in content-engine/noindex-guides.json ("urls": ["/guides/<x>/", ...]).
Who respects it:
  * seo_cleanup.py      - forces the noindex tag and drops these URLs from sitemap.xml
  * generate_guides.py  - never regenerates these pages, never adds them to the sitemap,
                          and hides games whose guides are all listed from the /guides/ hub list
  * apply_queue.py      - still publishes played rewrites for listed pages, but keeps them
                          noindex; it never takes URLs off the list
  * lift_noindex.py     - the only way off the list: Studio checks the rewrite, then runs
                          `python content-engine/lift_noindex.py <slug> [...]`

Also home of the purchase-claim guard: nobody has verified in-game purchases for any
game, so generated copy must never claim them.
"""

import json
import os
import re

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noindex-guides.json")


def _load_doc():
    if not os.path.exists(PATH):
        return {"urls": []}
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def load_urls():
    """The NOINDEX_GUIDES set of guide paths, e.g. '/guides/angry-sharks-tips/'."""
    return set(_load_doc().get("urls", []))


NOINDEX_GUIDES = load_urls()


def remove_urls(urls):
    """Take URLs off the list. Only lift_noindex.py calls this (after Studio has checked them)."""
    urls = set(urls)
    doc = _load_doc()
    before = doc.get("urls", [])
    after = [u for u in before if u not in urls]
    if len(after) != len(before):
        doc["urls"] = after
        with open(PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")
        NOINDEX_GUIDES.difference_update(urls)
    return [u for u in before if u in urls]


def hidden_hub_slugs(guides_index, urls=None):
    """Games whose guide pages are all on the list: left out of the /guides/ hub list."""
    urls = load_urls() if urls is None else urls
    return sorted(slug for slug, pages in guides_index.items()
                  if pages and all(u in urls for u in pages.values()))


# --- purchase / download claim guard -----------------------------------------
# Nobody has verified purchases, paid "full versions" or app-store downloads for any
# game. Every game on Pixelsprout runs free in the web browser with no download.
_H = r"[\s\-\u2010\u2011\u2012\u2013]?"
PURCHASE_RE = re.compile(r"in" + _H + r"(game|app)\s+purchas|micro" + _H + r"transaction|\bpurchas", re.I)
CLAIM_RE = re.compile(PURCHASE_RE.pattern + r"|limited content|full version|download and (start )?play"
                      r"|free" + _H + r"to" + _H + r"download|app store|google play"
                      r"|(free|paid|premium|full|lite)\s*version|paid game|can be bought|in" + _H + r"(game|app)\s+store", re.I)
# Questions about cost: the only verified answer is the browser line.
COST_Q_RE = re.compile(r"\bpurchas|\bpaid\b|\bcost\b|\bprice", re.I)
_SENT_RE = re.compile(r"[^.!?]*(?:[.!?]+|$)")


def browser_line(title, yes=False):
    return f"{'Yes. ' if yes else ''}{title} is free to play in your web browser on Pixelsprout, with no download."


def clean_text(text, title=None, regex=None):
    """Replace every sentence with a purchase/download claim. With a title, the first one
    becomes the true browser line; without a title (or after the first) it is dropped."""
    regex = regex or CLAIM_RE
    if not isinstance(text, str) or not regex.search(text):
        return text
    out, used = [], False
    for sent in _SENT_RE.findall(text):
        if not sent.strip():
            continue
        if regex.search(sent):
            if title and not used:
                lead = sent[:len(sent) - len(sent.lstrip())]
                out.append(lead + browser_line(title, sent.strip().lower().startswith("yes")))
                used = True
            continue
        out.append(sent)
    return "".join(out).strip()


def strip_purchase_claims(text):
    """Drop every sentence with a purchase/download claim. Returns the cleaned text."""
    return clean_text(text)


def scrub_content(page_type, content, title=None):
    """Remove unverified purchase/download claims from generated guide content.
    FAQ pairs asking about in-game/in-app purchases are dropped; questions about cost get
    the true browser line; in answers each claim becomes that line (title given) or is dropped."""
    if not isinstance(content, dict):
        return content
    out = {}
    for key, value in content.items():
        if key == "faqs" and isinstance(value, list):
            faqs = []
            for qa in value:
                q = str(qa.get("question", "")) if isinstance(qa, dict) else ""
                if not q or re.search(r"in" + _H + r"(game|app)\s+purchas|micro" + _H + r"transaction", q, re.I):
                    continue
                if title and COST_Q_RE.search(q):
                    answer = browser_line(title)
                else:
                    answer = clean_text(qa.get("answer", ""), title)
                if answer:
                    faqs.append({**qa, "answer": answer})
            out[key] = faqs
        elif isinstance(value, list):
            out[key] = [v for v in (clean_text(x) for x in value) if v]
        else:
            out[key] = clean_text(value)
    return out
