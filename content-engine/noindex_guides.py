"""
Persistent NOINDEX_GUIDES list: guide pages that stay noindex,follow and out of
sitemap.xml until someone rewrites them from real play.

The list lives in content-engine/noindex-guides.json ("urls": ["/guides/<x>/", ...]).
Who respects it:
  * seo_cleanup.py      - forces the noindex tag and drops these URLs from sitemap.xml
  * generate_guides.py  - never regenerates these pages, never adds them to the sitemap,
                          and hides games whose guides are all listed from the /guides/ hub list
  * apply_queue.py      - publishing a page from a played seo-queue file is the only thing
                          that takes its URL off the list (that is the proof the copy is real)

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
    """Take URLs off the list (only after they were republished from a played file)."""
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


# --- purchase-claim guard ---------------------------------------------------
# Matches "in-game purchases" with any hyphen (ASCII, non-breaking U+2011, en dash...) or a space.
PURCHASE_RE = re.compile(r"in[\s\-\u2010\u2011\u2012\u2013]?(game|app)\s+purchas|microtransaction|\bpurchas", re.I)
_SENT_RE = re.compile(r"[^.!?]*(?:[.!?]+|$)")


def strip_purchase_claims(text):
    """Drop every sentence that talks about purchases. Returns the cleaned text."""
    if not isinstance(text, str) or not PURCHASE_RE.search(text):
        return text
    kept = [s for s in _SENT_RE.findall(text) if s.strip() and not PURCHASE_RE.search(s)]
    return "".join(kept).strip()


def scrub_content(page_type, content):
    """Remove unverified purchase claims from generated guide content (any page type).
    FAQ pairs whose question is about purchases are dropped entirely."""
    if not isinstance(content, dict):
        return content
    out = {}
    for key, value in content.items():
        if key == "faqs" and isinstance(value, list):
            faqs = []
            for qa in value:
                if not isinstance(qa, dict) or PURCHASE_RE.search(str(qa.get("question", ""))):
                    continue
                answer = strip_purchase_claims(qa.get("answer", ""))
                if answer:
                    faqs.append({**qa, "answer": answer})
            out[key] = faqs
        elif isinstance(value, list):
            out[key] = [v for v in (strip_purchase_claims(x) for x in value) if v]
        else:
            out[key] = strip_purchase_claims(value)
    return out
