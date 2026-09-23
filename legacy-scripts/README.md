# Legacy scripts — do not run

One-off repair and rebuild scripts from before the shared page shell
(`site_shell.py` / `site_pages.py`). They pattern-match the old markup and
would corrupt the current pages if run again. Kept only for history.

Use instead:

- `generate-homepage.py` — homepage and `/all-games/`
- `generate-category-pages.py` — genre pages
- `migrate-ui.py` — re-render any existing page onto the current shell
