#!/usr/bin/env python3
"""
Adds two AdSense ad placements to every existing embedded game page:
- A banner ad ABOVE the game (before it even loads)
- A ribbon ad BELOW the game (after the description, before similar games)

Neither touches the iframe/game area itself — GamePix's own in-game ads
(required to stay per their revenue-share terms) are completely separate
and untouched.

IMPORTANT: fill in your real ad slot IDs below before running this. These
come from YOUR AdSense dashboard (Ads -> By ad unit -> Create new ad unit),
not something that can be invented — each one is unique to your account.
"""

import glob
import re

# ---- FILL THESE IN before running ----
BANNER_SLOT_ID = "4936643192"
RIBBON_SLOT_ID = "1457517471"

BANNER_BLOCK = f"""  <div class="ad-slot ad-slot-banner">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-8466016918717424"
         data-ad-slot="{BANNER_SLOT_ID}"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

"""

RIBBON_BLOCK = f"""    <div class="ad-slot ad-slot-ribbon">
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="ca-pub-8466016918717424"
           data-ad-slot="{RIBBON_SLOT_ID}"
           data-ad-format="horizontal"
           data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>

"""


def main():
    if "REPLACE_WITH" in BANNER_SLOT_ID or "REPLACE_WITH" in RIBBON_SLOT_ID:
        print("ERROR: fill in BANNER_SLOT_ID and RIBBON_SLOT_ID at the top of this script first.")
        print("Get these from your AdSense dashboard: Ads -> By ad unit -> Create new ad unit.")
        return

    files = glob.glob("games/*.html")
    patched = 0
    skipped_not_embed = 0
    skipped_already_done = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if "embed-frame-wrap" not in content:
            skipped_not_embed += 1
            continue

        if "ad-slot-banner" in content:
            skipped_already_done += 1
            continue

        # Insert banner right after the game-meta div, before game-board-frame
        content = re.sub(
            r'(<div class="game-meta">[^<]*</div>\n)',
            r'\1\n' + BANNER_BLOCK.replace("\\", "\\\\"),
            content,
            count=1,
        )

        # Insert ribbon right before the similar-games block
        marker = '    <div class="similar-games">'
        if marker in content:
            content = content.replace(marker, RIBBON_BLOCK + marker, 1)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        patched += 1

    print(f"Patched: {patched}")
    print(f"Skipped (not an embed page, e.g. your 8 original games): {skipped_not_embed}")
    print(f"Skipped (already had ad slots): {skipped_already_done}")


if __name__ == "__main__":
    main()
