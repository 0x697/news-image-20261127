"""Hand the finished front page to the grader.

The entry image lives beside this file as entry.png. This program streams
it into the directory the grader names (MAKEFUN_OUTPUT_DIR, or /output),
then hashes the copy and compares it with the original, so a truncated
write is caught instead of silently graded. Only the standard library is
used, and nothing here touches the network or the clock.
"""

import hashlib
import os
import shutil
from pathlib import Path

IMAGE = "entry.png"


def main():
    root = Path(__file__).resolve().parent
    source = root / IMAGE
    wanted = hashlib.sha256(source.read_bytes()).hexdigest()
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / IMAGE
    with source.open("rb") as reader, target.open("wb") as writer:
        shutil.copyfileobj(reader, writer, length=1 << 16)
    got = hashlib.sha256(target.read_bytes()).hexdigest()
    if got != wanted:
        raise SystemExit("copy mismatch: entry.png did not land intact")
    print(f"wrote {target} ({target.stat().st_size} bytes, "
          f"sha256:{wanted[:12]})")


if __name__ == "__main__":
    main()
