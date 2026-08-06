#!/usr/bin/env python3
"""Watchdog: has anything been waiting too long to be annotated?

The failure this exists to catch is the quiet one. Job 1 can succeed, Job 2 can
report a green run, and the work can still not be on `main` — because the routine
pushed to a branch and the `promote` workflow rejected it, or the routine never
fired at all. Nothing about that is visible unless something looks.

So: anything in the manifest still un-annotated more than MAX_PENDING_HOURS after
it was solved means a link in the chain is broken. The check is derived purely
from data already in the manifest, so there is no new state to keep correct.

Exit status:
    0  nothing is overdue (including "nothing is pending at all")
    1  something is overdue — the workflow turns this into a GitHub issue
    2  the manifest is missing or unreadable, which is itself a problem

Run: /usr/bin/python3 scripts/check_pending.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data" / "manifest.json"

# Job 1 runs at 17:00 UTC and Job 2 an hour later, so a problem solved just
# before a fetch should be annotated within ~1 hour and certainly within a day.
# 30 hours gives a full missed cycle plus GitHub's scheduling slack before this
# starts shouting.
MAX_PENDING_HOURS = 30


def main() -> int:
    if not MANIFEST.exists():
        print("manifest missing at %s" % MANIFEST)
        return 2
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("manifest unreadable: %s" % exc)
        return 2

    problems = manifest.get("problems", {})
    now = datetime.now(tz=timezone.utc)

    pending = []
    for slug, entry in problems.items():
        if entry.get("annotated") and entry.get("annotationHash") == entry.get("codeHash"):
            continue
        solved = datetime.fromtimestamp(entry.get("timestamp", 0), tz=timezone.utc)
        hours = (now - solved).total_seconds() / 3600
        pending.append((hours, slug, entry))

    if not pending:
        print("nothing pending annotation — %d problem(s) all current" % len(problems))
        return 0

    pending.sort(reverse=True)
    overdue = [p for p in pending if p[0] > MAX_PENDING_HOURS]

    for hours, slug, entry in pending:
        print(
            "%-28s %s  solved %.1f h ago%s"
            % (
                slug,
                "annotated" if entry.get("annotated") else "NOT annotated",
                hours,
                "   <-- OVERDUE" if hours > MAX_PENDING_HOURS else "",
            )
        )

    if not overdue:
        print(
            "\n%d pending, none older than %d h — the next run should pick them up"
            % (len(pending), MAX_PENDING_HOURS)
        )
        return 0

    print(
        "\n%d problem(s) pending for more than %d hours."
        % (len(overdue), MAX_PENDING_HOURS)
    )
    print("Something in the chain is not completing. Check, in order:")
    print("  1. the routine's own run log at https://claude.ai/code/routines")
    print("  2. the `promote` workflow — it refuses to merge output it can't verify")
    print("  3. `python3 scripts/verify_ast.py --all` on the routine's branch")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
