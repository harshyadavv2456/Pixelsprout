#!/usr/bin/env python3
"""
Fixes a real mismatch: the ribbon ad unit was deployed with
data-ad-format="horizontal", but your actual AdSense dashboard generated
this specific ad unit as data-ad-format="auto". Corrects every already-
pushed game page to match exactly what Google's dashboard gave you.

Safe to re-run — only touches lines that still say "horizontal".
"""

import glob

def main():
    files = glob.glob("games/*.html")
    fixed = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if 'data-ad-slot="1457517471"' in content and 'data-ad-format="horizontal"' in content:
            new_content = content.replace(
                'data-ad-slot="1457517471"\n           data-ad-format="horizontal"',
                'data-ad-slot="1457517471"\n           data-ad-format="auto"',
            )
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                fixed += 1
    print(f"Fixed ribbon ad-format on {fixed} pages.")

if __name__ == "__main__":
    main()
