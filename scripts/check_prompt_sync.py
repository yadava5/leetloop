#!/usr/bin/env python3
"""Print a fingerprint of the routine prompt, so UI drift is detectable.

`docs/routine-prompt.txt` is version-controlled, but the copy that actually runs
lives in the routines UI and **nothing syncs them**. That is a documented risk and
it has already bitten once: an edit went into the UI and not the file, so the two
described different behaviour for several hours with no symptom.

There is no API to read the live prompt back, so this cannot compare them
automatically. What it can do is give you a short fingerprint to eyeball against
the UI, and a summary of the structure the prompt currently asks for — enough to
spot "these are not the same document" in a couple of seconds.

Run: /usr/bin/python3 scripts/check_prompt_sync.py
"""

import hashlib
import re
import sys
from pathlib import Path

PROMPT = Path(__file__).resolve().parent.parent / "docs" / "routine-prompt.txt"


def main() -> int:
    if not PROMPT.exists():
        print("missing %s" % PROMPT)
        return 2

    text = PROMPT.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    print("docs/routine-prompt.txt")
    print("  sha256      %s" % digest)
    print("  short       %s" % digest[:12])
    print("  lines       %d" % len(text.splitlines()))
    print("  characters  %d" % len(text))
    print()

    steps = re.findall(r"(?m)^(\d+)\. (.+)$", text)
    print("  numbered steps the routine must follow:")
    for number, title in steps:
        print("    %s. %s" % (number, title.strip()[:66]))
    print()

    sections = re.findall(r"(?m)^\s*(#{1,3}) ([A-Z].+)$", text)
    page = [name.strip() for level, name in sections if level in ("##", "###")]
    print("  sections it asks each problem page to contain:")
    for name in page:
        print("    %s" % name)
    print()

    print("  Compare the line/character counts against the prompt at")
    print("  https://claude.ai/code/routines — if they differ, the running copy")
    print("  is not this file. Paste this file over it:")
    print()
    print("    /usr/bin/pbcopy < %s" % PROMPT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
