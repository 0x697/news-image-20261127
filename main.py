"""Entry program for news-image-20261127.

The finished front page ships in this repository as entry.png. This
program checks it against the contest's gate (PNG, at most 1 MiB, at
most 1024 by 1024 pixels), copies it byte for byte into the directory
the grader names, and proves the copy landed intact by comparing
sha256 hashes. Standard library only; no network, no clock.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

IMAGE = "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def png_size(data: bytes) -> tuple[int, int]:
    """Read width and height out of a PNG's IHDR chunk."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main() -> int:
    source = Path(__file__).resolve().parent / IMAGE
    data = source.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the 1 MiB gate")
    width, height = png_size(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(f"entry.png is {width}x{height}, over the 1024x1024 gate")
    wanted = hashlib.sha256(data).hexdigest()

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / IMAGE
    target.write_bytes(data)
    got = hashlib.sha256(target.read_bytes()).hexdigest()
    if got != wanted:
        raise SystemExit("copy mismatch: entry.png did not land intact")
    print(f"wrote {target} ({len(data)} bytes, {width}x{height}, sha256:{wanted[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
