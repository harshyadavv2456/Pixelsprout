#!/usr/bin/env python3
"""Builds index.html and all-games/index.html from games-index.json.

Run after anything changes the catalog (auto-add, bulk-add). The homepage is
fully generated - never hand-edit index.html.
"""

import site_pages as P
import site_shell as S


def main():
    catalog = S.load_catalog()
    P.build_home(catalog)
    print(f"Wrote index.html and all-games/index.html ({len(catalog)} games).")


if __name__ == "__main__":
    main()
