#!/usr/bin/env python3
"""
Refresh the static popular-games.json snapshot from Supabase.

Run once a day via GitHub Actions (see .github/workflows/refresh-popular-games.yml).
Replaces the old per-visitor pattern (index.html calling /api/popular-games,
which hit Supabase live on every single page load - the source of the
homepage lag). Now the homepage fetches this static, CDN-served JSON file
instead, and it only gets regenerated once a day.

Requires two env vars (same ones already used by api/_supabase.js in Vercel -
these need to be added as GitHub Actions repo secrets too, see the workflow
file for the exact names):
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
"""

import json
import os
import sys
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OUTPUT_PATH = "popular-games.json"


def fetch_popular_games():
    url = f"{SUPABASE_URL}/rest/v1/game_views?select=slug,views&order=views.desc&limit=20"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Supabase REST GET failed: {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def main():
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set - skipping, leaving existing file as-is.")
        sys.exit(0)

    try:
        games = fetch_popular_games()
    except Exception as e:
        print(f"Fetch failed: {e} - leaving existing popular-games.json untouched.")
        sys.exit(0)  # don't fail the whole workflow over a transient Supabase hiccup

    payload = {"games": games}
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(games)} ranked games to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
