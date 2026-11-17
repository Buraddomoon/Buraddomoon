#!/usr/bin/env python3
"""Give the header a content-versioned filename to avoid stale image caches."""
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "header-fabio.svg"


def main():
    data = SOURCE.read_bytes()
    version = sha256(data).hexdigest()[:12]
    target = SOURCE.with_name(f"header-fabio-{version}.svg")
    readme = ROOT / "README.md"
    text = readme.read_text()
    pattern = r'(<img src=")\./assets/header-fabio(?:-[0-9a-f]{12})?\.svg(?:\?[^"\s]*)?("\s)'
    updated, count = re.subn(pattern, lambda m: f'{m[1]}./assets/{target.name}{m[2]}', text)
    if count != 1:
        raise ValueError("Expected exactly one profile header reference in README.md")
    if target.exists() and target.read_bytes() != data:
        raise ValueError("The existing versioned header has different content")
    if not target.exists():
        target.write_bytes(data)
    if updated != text:
        readme.write_text(updated)
    print(f"Header image: assets/{target.name}")


if __name__ == "__main__":
    main()
