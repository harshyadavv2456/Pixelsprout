#!/usr/bin/env python3
"""
Patches every embedded-game page (games/*.html files that use the GamePix
iframe embed template) to:
1. Make the game screen significantly bigger (was capped at 480px wide
   regardless of your actual screen size — now scales up to 960px)
2. Add a real Fullscreen button, which also gives mobile browsers their
   best shot at properly using landscape/rotated screen space for games
   that need it — this can't force a game to support rotation if the game
   itself doesn't, but it fixes the "no fullscreen option at all" gap.

Only touches files matching the known embed template signature — does NOT
touch your 8 original custom-built games (2048, Snake, etc.), which use
their own canvas/DOM logic, not this iframe pattern.

Safe to re-run: skips any file that's already been patched.
"""

import glob
import os

OLD_CSS = """  .embed-frame-wrap {
    width: 100%;
    max-width: 480px;
    aspect-ratio: 480 / 320;
    border-radius: 8px;
    overflow: hidden;
    background: #000;
  }
  .embed-frame-wrap iframe {
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }"""

NEW_CSS = """  .embed-frame-wrap {
    width: 100%;
    max-width: 960px;
    aspect-ratio: 16 / 10;
    border-radius: 8px;
    overflow: hidden;
    background: #000;
  }
  .embed-frame-wrap iframe {
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }
  .fullscreen-btn {
    margin-top: 4px;
  }"""

FULLSCREEN_BUTTON = """    <button class="action fullscreen-btn" onclick="
      const f = document.querySelector('.embed-frame-wrap iframe');
      const req = f.requestFullscreen || f.webkitRequestFullscreen || f.msRequestFullscreen;
      if (req) req.call(f);
      if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock('landscape').catch(() => {});
      }
    ">⛶ Fullscreen</button>
"""


def main():
    files = glob.glob("games/*.html")
    patched = 0
    skipped_no_match = 0
    already_done = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if OLD_CSS not in content:
            if "fullscreen-btn" in content:
                already_done += 1
            else:
                skipped_no_match += 1
            continue

        content = content.replace(OLD_CSS, NEW_CSS, 1)

        # Insert the fullscreen button right after the embed-frame-wrap's
        # closing </div>, before the description paragraph.
        marker = "    </div>\n    <p class=\"how-to\">"
        if marker in content:
            content = content.replace(marker, "    </div>\n" + FULLSCREEN_BUTTON + "    <p class=\"how-to\">", 1)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        patched += 1

    print(f"Patched: {patched}")
    print(f"Already done (skipped): {already_done}")
    print(f"Not a matching embed page (skipped, expected for your 8 original games): {skipped_no_match}")


if __name__ == "__main__":
    main()
