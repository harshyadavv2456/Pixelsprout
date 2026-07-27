from pathlib import Path

GAMES_DIR = Path("games")

LOADER = (
    '<script async '
    'src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8466016918717424" '
    'crossorigin="anonymous"></script>'
)

TARGET = '<link rel="stylesheet" href="../styles.css">'

patched = 0
skipped = 0

for html_file in GAMES_DIR.glob("*.html"):
    text = html_file.read_text(encoding="utf-8")

    # Already patched
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in text:
        skipped += 1
        continue

    # Insert immediately after stylesheet link
    if TARGET in text:
        text = text.replace(TARGET, TARGET + "\n" + LOADER, 1)
        html_file.write_text(text, encoding="utf-8")
        patched += 1
    else:
        print(f"WARNING: stylesheet link not found in {html_file.name}")

print(f"\n✅ Patched: {patched}")
print(f"⏭️  Skipped (already had loader): {skipped}")