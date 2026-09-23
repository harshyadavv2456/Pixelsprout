#!/usr/bin/env python3
"""Generates /{category}/index.html for every category with 15+ games.

Rendering lives in site_pages.build_category_pages so the daily run and
migrate-ui.py produce identical pages. Safe to re-run; it only overwrites
its own generated pages.
"""

import site_pages as P
import site_shell as S


def main():
    catalog = S.load_catalog()
    pages = P.build_category_pages(catalog)
    for path in sorted(pages):
        print("Generated", path.replace(S.ROOT, "").replace("\\", "/"))
    print(f"{len(pages)} category pages written.")


if __name__ == "__main__":
    main()
