"""news-image-20261119 entry: copy the pre-rendered front page to the
output directory. Standard library only; no network.

The grader runs this twice in a fresh container with the repository
mounted read-only; both runs must write the same bytes.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def main():
    # Fail loudly (non-zero exit) if the image is missing, instead of
    # writing a partial or empty output the gate would reject anyway.
    if not SOURCE.is_file():
        print(f"main.py: {SOURCE} not found", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_dir / "entry.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
