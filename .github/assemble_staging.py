#!/usr/bin/env python3
"""Unpack .github/publish-staging/<batch>/part-* (base64 of a repo-root tarball).

The daily publisher uploads text chunks because some credentials can commit
text but not raw binaries in one shot. READY must contain the batch name.
Only that batch is extracted. A cover.jpg that is not a JPEG fails the job
so a game card is never left pointing at a missing image.
"""
import base64
import io
import sys
import tarfile
from pathlib import Path

ROOT = Path(".github/publish-staging")


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main():
    if not ROOT.is_dir():
        print("no staging directory")
        return
    ready = ROOT / "READY"
    if not ready.is_file():
        fail("READY is missing; refusing to unpack every batch")
    only = ready.read_text(encoding="utf-8").strip()
    if not only or "/" in only or only.startswith("."):
        fail("READY must be a single batch name")
    batch = ROOT / only
    if not batch.is_dir():
        fail(f"batch not found: {only}")
    parts = sorted(batch.glob("part-*"))
    if not parts:
        fail(f"no parts in {only}")
    blob = "".join(part.read_text(encoding="utf-8") for part in parts)
    try:
        raw = base64.b64decode("".join(blob.split()), validate=False)
    except Exception as exc:
        fail(f"base64 decode failed: {exc}")
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            tar.extractall(path=".")
            names = tar.getnames()
    except Exception as exc:
        fail(f"tar extract failed: {exc}")
    covers = [n for n in names if n.endswith("/cover.jpg") or n.endswith("cover.jpg")]
    if not covers:
        fail("batch extracted no cover.jpg")
    for name in covers:
        path = Path(name)
        head = path.read_bytes()[:3]
        if head != b"\xff\xd8\xff":
            fail(f"{name} is not a JPEG")
        if path.stat().st_size < 4000:
            fail(f"{name} is too small to be a finished logo")
    for part in parts:
        part.unlink()
    ready.unlink(missing_ok=True)
    try:
        batch.rmdir()
    except OSError:
        pass
    print(f"extracted {only}: {len(parts)} parts, {len(raw)} bytes, covers={covers}")


if __name__ == "__main__":
    main()
