#!/usr/bin/env python3
"""
Upgrades every embedded game page's iframe with the 'allow' permissions
attribute needed for fullscreen and orientation-lock to work properly
inside a nested iframe on mobile browsers (many browsers silently block
these features for cross-origin iframes unless explicitly granted here).

Also retargets the fullscreen button to fullscreen the WRAPPER element
instead of the iframe directly — more consistently supported across mobile
browsers than fullscreening a cross-origin iframe element itself.

HONEST LIMIT: this is a real improvement, but it cannot force a specific
third-party game to support fullscreen or rotation if that game's own code
doesn't. Some GamePix titles may still show their own "rotate device"
prompt regardless — that's the game's own logic, not something patchable
from our side.
"""

import glob
import re

OLD_BUTTON_SNIPPET = "const f = document.querySelector('.embed-frame-wrap iframe');"
NEW_BUTTON_ONCLICK = """
      const f = document.querySelector('.embed-frame-wrap');
      const req = f.requestFullscreen || f.webkitRequestFullscreen || f.msRequestFullscreen;
      if (req) req.call(f);
      if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock('landscape').catch(() => {});
      }
    """


def main():
    files = glob.glob("games/*.html")
    iframe_patched = 0
    button_patched = 0
    no_button = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        changed = False

        # Add allow="" to iframe tags that don't already have one
        if "<iframe" in content and 'allow="' not in content:
            content = re.sub(
                r'(<iframe\s+src="[^"]*")',
                r'\1 allow="fullscreen; autoplay; screen-orientation;"',
                content,
                count=1,
            )
            iframe_patched += 1
            changed = True

        # Retarget the fullscreen button from iframe to wrapper
        if OLD_BUTTON_SNIPPET in content:
            content = re.sub(
                r"const f = document\.querySelector\('\.embed-frame-wrap iframe'\);.*?\}\s*\">",
                NEW_BUTTON_ONCLICK + '">',
                content,
                count=1,
                flags=re.DOTALL,
            )
            button_patched += 1
            changed = True
        elif "fullscreen-btn" not in content:
            no_button += 1

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"Iframe 'allow' attribute added: {iframe_patched}")
    print(f"Fullscreen button retargeted: {button_patched}")
    print(f"Skipped (no fullscreen button found, e.g. your 8 original games): {no_button}")


if __name__ == "__main__":
    main()
