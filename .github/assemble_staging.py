#!/usr/bin/env python3
"""Unpack .github/publish-staging/<batch>/part-* (base64 of a repo-root tarball).

The daily publisher uploads text chunks because some credentials can commit
text but not raw binaries in one shot. This script turns those chunks back
into the real files, then deletes the staging directory.
"""
import base64
import io
import shutil
import tarfile
from pathlib import Path

ROOT = Path(".github/publish-staging")


def main():
    if not ROOT.is_dir():
        print("no staging directory")
        return
    batches = sorted(p for p in ROOT.iterdir() if p.is_dir())
    # Only the batch named in READY, so leftover parts cannot abort the job.
    ready = ROOT / "READY"
    only = ready.read_text(encoding="utf-8").strip() if ready.is_file() else ""
    if only:
        batches = [p for p in batches if p.name == only]
    if not batches:
        print("no batches")
        return
    for batch in batches:
        parts = sorted(batch.glob("part-*"))
        if not parts:
            print("skip", batch.name)
            continue
        blob = "".join(part.read_text(encoding="utf-8") for part in parts)
        raw = base64.b64decode("".join(blob.split()))
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            tar.extractall(path=".")
        print(f"extracted {batch.name}: {len(parts)} parts, {len(raw)} bytes")
    shutil.rmtree(ROOT, ignore_errors=True)


if __name__ == "main":
    main()
