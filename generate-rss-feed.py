#!/usr/bin/env python3
"""
Generates rss.xml — a real RSS feed (proper titles, descriptions, links,
images per game), which dlvr.it (or any RSS reader) can actually parse,
unlike a plain XML sitemap.

Builds the feed from your most recently added games (using games-index.json,
which lists games in the order they were added). Keeps the most recent 60
entries — recent enough for dlvr.it to pick up newly added games daily,
without the feed file growing unbounded as your catalog grows.

Run this once now for the initial backlog. auto-add-games.py and
bulk-add-games.py have been updated to keep this file current automatically
going forward, using real timestamps at the moment each game is added.
"""

import json
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

DOMAIN = "https://playpixelsprout.com"
MAX_ITEMS = 60


def load_games():
    with open("games-index.json", encoding="utf-8") as f:
        return json.load(f)


def build_rss(games):
    recent = games[-MAX_ITEMS:]
    recent.reverse()  # most recently added first

    now = datetime.now(timezone.utc)
    items_xml = []
    for i, g in enumerate(recent):
        # Real timestamps aren't tracked for the historical backlog, so
        # spacing them a day apart (newest = now) is a reasonable stand-in —
        # going forward, auto-add-games.py uses the real add-time instead.
        pub_date = (now - timedelta(days=i)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        title = escape(g["title"])
        link = f"{DOMAIN}/games/{g['slug']}.html"
        description = escape(f"Play {g['title']} free online at Pixelsprout — no download needed.")
        thumbnail = g.get("thumbnail", "")

        enclosure = f'<enclosure url="{escape(thumbnail)}" type="image/jpeg"/>' if thumbnail else ""

        items_xml.append(f"""  <item>
    <title>{title}</title>
    <link>{link}</link>
    <guid>{link}</guid>
    <description>{description}</description>
    <pubDate>{pub_date}</pubDate>
    {enclosure}
  </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Pixelsprout - New Games</title>
  <link>{DOMAIN}/</link>
  <description>Newest games added to Pixelsprout, a free browser gaming library.</description>
{chr(10).join(items_xml)}
</channel>
</rss>
"""
    return rss


def main():
    games = load_games()
    rss = build_rss(games)
    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"Wrote rss.xml with {min(len(games), MAX_ITEMS)} items.")


if __name__ == "__main__":
    main()
