#!/usr/bin/env python3
"""
Daily Pinterest posting script. Reads games-index.json, finds games not yet
pinned (tracked in pinterest-posted.json), posts a capped batch to your
Pinterest board via the official API, and commits the updated tracking file.

Never fails the deployment/run if Pinterest errors — logs and continues,
so a Pinterest outage or rate limit never blocks your game-adding pipeline.

Requires three environment variables (set as GitHub Actions secrets):
  PINTEREST_APP_ID
  PINTEREST_APP_SECRET
  PINTEREST_REFRESH_TOKEN
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DOMAIN = "https://playpixelsprout.com"
BOARD_NAME = "Pixelsprout Games"
POSTS_PER_RUN = 5
TRACKING_FILE = "pinterest-posted.json"
GAMES_INDEX_FILE = "games-index.json"

APP_ID = os.environ.get("PINTEREST_APP_ID", "")
APP_SECRET = os.environ.get("PINTEREST_APP_SECRET", "")
REFRESH_TOKEN = os.environ.get("PINTEREST_REFRESH_TOKEN", "")


def api_request(method, path, access_token, body=None):
    url = f"https://api.pinterest.com/v5{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def refresh_access_token():
    credentials = base64.b64encode(f"{APP_ID}:{APP_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }).encode()
    req = urllib.request.Request(
        "https://api.pinterest.com/v5/oauth/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
    return result["access_token"]


def find_board_id(access_token):
    result = api_request("GET", "/boards", access_token)
    for board in result.get("items", []):
        if board.get("name") == BOARD_NAME:
            return board["id"]
    raise RuntimeError(f"Board '{BOARD_NAME}' not found in your Pinterest account.")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_pin(access_token, board_id, game):
    thumbnail = game.get("thumbnail") or f"{DOMAIN}/assets/logo-icon.png"
    link = f"{DOMAIN}/games/{game['slug']}.html"
    body = {
        "board_id": board_id,
        "title": game["title"][:100],
        "description": f"Play {game['title']} free online at Pixelsprout — no download needed. #{game['category'].replace(' ', '')} #browsergames #freegames",
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": thumbnail,
        },
    }
    return api_request("POST", "/pins", access_token, body)


def main():
    if not (APP_ID and APP_SECRET and REFRESH_TOKEN):
        print("ERROR: missing PINTEREST_APP_ID, PINTEREST_APP_SECRET, or PINTEREST_REFRESH_TOKEN env vars.")
        sys.exit(1)

    games = load_json(GAMES_INDEX_FILE, [])
    posted = load_json(TRACKING_FILE, {"posted_slugs": []})
    posted_slugs = set(posted["posted_slugs"])

    to_post = [g for g in games if g["slug"] not in posted_slugs][:POSTS_PER_RUN]

    if not to_post:
        print("No new games to post to Pinterest.")
        return

    try:
        access_token = refresh_access_token()
        board_id = find_board_id(access_token)
    except Exception as e:
        print(f"Pinterest auth/board lookup failed (non-critical, skipping this run): {e}")
        return

    posted_count = 0
    for game in to_post:
        try:
            create_pin(access_token, board_id, game)
            posted["posted_slugs"].append(game["slug"])
            posted_count += 1
            print(f"Pinned: {game['title']}")
        except urllib.error.HTTPError as e:
            print(f"Failed to pin '{game['title']}' (HTTP {e.code}): {e.read().decode()[:200]} — skipping, will retry next run.")
        except Exception as e:
            print(f"Failed to pin '{game['title']}': {e} — skipping, will retry next run.")

    if posted_count:
        save_json(TRACKING_FILE, posted)
        print(f"Posted {posted_count} new pin(s). Tracking file updated.")
    else:
        print("No pins succeeded this run.")


if __name__ == "__main__":
    main()
