#!/usr/bin/env python3
"""Watchdog: has anything been waiting too long to be annotated?

The failure this exists to catch is the quiet one. Job 1 can succeed, Job 2 can
report a green run, and the work can still not be on `main` — because the routine
pushed to a branch and the `promote` workflow rejected it, or the routine never
fired at all. Nothing about that is visible unless something looks.

So: anything in the manifest still un-annotated more than MAX_PENDING_HOURS after
it was solved means a link in the chain is broken. The check is derived purely
from data already in the manifest, so there is no new state to keep correct.

There is a second quiet failure, and it is the one that actually bit. On
2026-08-19 the LeetCode cookie expired. Job 1 handled it exactly as designed —
filed an issue, exited 0 — and then reported SUCCESS every day for 28 days.
Job 2 correctly found nothing to annotate and reported "no new solves, expected
outcome" every day. This watchdog stayed silent too, because its only question
was "is anything pending?" and the answer was honestly no: nothing was pending
because nothing was arriving. Four weeks of real solves sat unfetched while
every indicator in the system read green.

So this also asks whether Job 1 is still alive at all, by checking how long ago
`lastSyncedAt` was updated. A pipeline that has not ingested anything in days is
broken whether or not the queue is empty — an empty queue is only good news if
the thing that fills it still works.

Exit status:
    0  nothing is overdue (including "nothing is pending at all")
    1  something is overdue — the workflow turns this into a GitHub issue
    2  the manifest is missing or unreadable, which is itself a problem
    3  no successful fetch in MAX_SYNC_AGE_HOURS — Job 1 has stopped

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

# Job 1 runs daily and updates lastSyncedAt on every SUCCESSFUL sync, whether or
# not it found anything new. So this is not "days since Ayush last solved
# something" — taking a week off is fine and does not trip it. It is "days since
# the fetcher last completed a round trip to LeetCode", which only goes stale if
# the cookie is dead, the workflow is disabled, or the schedule stopped firing.
#
# 72 hours: three missed daily runs. Long enough that a single GitHub outage or
# a weekend of scheduler lag stays quiet, short enough that a dead cookie is
# named within days instead of within a month.
MAX_SYNC_AGE_HOURS = 72


def sync_age_hours(manifest, now):
    """Hours since Job 1 last completed a sync, or None if it cannot be told.

    Returns None rather than 0 for a manifest with no `lastSyncedAt` at all — a
    fresh fork has never synced, and shouting at it on day one would be noise.
    An unparseable value is treated the same way: this check exists to catch a
    stopped fetcher, not to police the manifest's schema.
    """
    raw = manifest.get("lastSyncedAt")
    if not raw:
        return None
    try:
        # Written by JavaScript's toISOString(), which always ends in "Z";
        # fromisoformat() before Python 3.11 does not accept that suffix.
        stamp = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return (now - stamp).total_seconds() / 3600


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

    # Check Job 1 first. If the fetcher is dead, an empty annotation queue is a
    # symptom rather than a clean bill of health, and reporting it as "all
    # current" is precisely the mistake that hid a 28-day outage.
    stale_hours = sync_age_hours(manifest, now)
    if stale_hours is not None and stale_hours > MAX_SYNC_AGE_HOURS:
        print(
            "No successful fetch in %.1f hours (last: %s).\n"
            % (stale_hours, manifest.get("lastSyncedAt", "never"))
        )
        print("Job 1 updates lastSyncedAt on every successful run, even a run that")
        print("finds nothing new — so this is not a quiet stretch of not solving.")
        print("It means the fetcher itself has stopped completing. Check, in order:")
        print("  1. open issues — an expired LeetCode cookie files one automatically")
        print("  2. the `fetch` workflow — note it exits 0 on an expired cookie,")
        print("     so a green run does NOT mean anything was ingested")
        print("  3. whether scheduled workflows are still enabled for this repo")
        print("\nFix: docs/RUNBOOK.md — refresh the cookie, two `gh secret set` commands.")
        print("Nothing is lost meanwhile; LeetCode keeps full submission history and")
        print("the next successful run resumes from lastSyncedTimestamp.")
        return 3

    pending = []
    for slug, entry in problems.items():
        if entry.get("annotated") and entry.get("annotationHash") == entry.get("codeHash"):
            continue
        solved = datetime.fromtimestamp(entry.get("timestamp", 0), tz=timezone.utc)
        hours = (now - solved).total_seconds() / 3600
        pending.append((hours, slug, entry))

    if not pending:
        print("nothing pending annotation — %d problem(s) all current" % len(problems))
        # Print the sync age even on the happy path, so "all current" is always
        # accompanied by the evidence that it means something.
        if stale_hours is not None:
            print("last successful fetch %.1f h ago (%s)"
                  % (stale_hours, manifest.get("lastSyncedAt")))
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
