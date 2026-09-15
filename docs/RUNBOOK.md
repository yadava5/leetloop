# Runbook

## The cookie expired (you got an issue email)

`LEETCODE_SESSION` lasts one to two weeks and cannot be refreshed
programmatically — no token-refresh flow exists. This is the one part of the
system that is not fully unattended, so it is made loud and cheap instead of
pretended away.

**The fix, about a minute:**

1. Open <https://leetcode.com> in the browser profile you keep permanently
   logged in (your notes say "Personal", Profile 6).
2. DevTools → **Application** → **Cookies** → `https://leetcode.com`.
3. Copy the value of **`LEETCODE_SESSION`** (long) and **`csrftoken`** (32
   chars).
4. Run these two, pasting when prompted — the value never appears in your shell
   history this way:

```
/opt/homebrew/bin/gh secret set LEETCODE_SESSION --repo yadava5/leetloop
/opt/homebrew/bin/gh secret set LEETCODE_CSRF_TOKEN --repo yadava5/leetloop
```

5. Confirm it works, then close the issue:

```
/opt/homebrew/bin/gh workflow run fetch.yml --repo yadava5/leetloop
/opt/homebrew/bin/gh run watch --repo yadava5/leetloop
```

For local runs, update `~/.leetcode.env` too (same two keys). That file lives
outside the repo deliberately: this repo is public, and a credential that
physically cannot be committed beats one protected only by `.gitignore`.

**Nothing is lost while the cookie is dead.** LeetCode retains full submission
history, and the next successful run resumes from `lastSyncedTimestamp`. A week
of downtime costs recency, not data.

**Don't log out of that browser profile.** Logging out invalidates the session
immediately, which is the one way to turn a fortnightly annoyance into a daily
one.

## Sync now instead of waiting for 17:00 UTC

```
/opt/homebrew/bin/gh workflow run fetch.yml --repo yadava5/leetloop
```

Locally:

```
cd ~/Documents/Projects/leetloop
npm install --include=dev     # NODE_ENV=production is exported in your shell,
                              # so plain `npm install` skips typescript
npm run build
node dist/cli.js --dry-run    # reads only
node dist/cli.js              # commits and pushes
node dist/cli.js --only two-sum
```

## Re-annotate a problem

Mark it stale, then let tonight's routine pick it up (or run the prompt in
`docs/routine-prompt.txt` in a Claude session pointed at this repo):

```
cd ~/Documents/Projects/leetloop
/usr/bin/python3 - <<'EOF'
import json, pathlib
p = pathlib.Path("data/manifest.json")
m = json.loads(p.read_text())
m["problems"]["two-sum"]["annotated"] = False
p.write_text(json.dumps(m, indent=2) + "\n")
EOF
```

## The annotation looks wrong / modified my code

It cannot have modified your code silently — but verify rather than trust:

```
/usr/bin/python3 scripts/verify_ast.py --all
/usr/bin/python3 scripts/test_verify_ast.py    # is the gate itself still honest?
```

If `--all` fails, the annotation is the thing that is wrong.
`data/raw/<slug>.py` is your submission and is never touched by Job 2; delete the
offending `problems/<n>-<slug>/` directory, mark the problem `annotated: false`,
and let it regenerate.

## An issue appeared saying "Annotation is not completing"

The watchdog files that when something was fetched but never annotated on `main`
more than 30 hours later. Job 1 and Job 2 can both look green while this is true,
because the routine pushes to a branch and `promote` refuses to merge output it
cannot verify.

Look in this order:

1. **the routine's run log** at <https://claude.ai/code/routines> — did it run at
   all, and did it push a branch?
2. **the `promote` workflow** — if it rejected the branch it will have filed its
   own issue saying which check failed.
3. `/usr/bin/python3 scripts/verify_ast.py --all` on that branch locally.

Nothing is lost while this is open: the manifest on `origin` still says
un-annotated, so each run retries. The issue means the retries aren't working.
The watchdog closes it by itself once everything is current again.

```
/usr/bin/python3 scripts/check_pending.py     # the same check, locally
```

## An issue appeared saying "Fetch has stopped bringing in submissions"

No successful fetch in over 72 hours. Job 1 updates `lastSyncedAt` on every
successful run — including a run that finds nothing new — so this is **not**
triggered by a quiet stretch of not solving. Take a week off and it stays silent.
It fires only when the fetcher itself stops completing.

Almost always this means the cookie expired and the expired-cookie issue went
unread. Treat this one as the escalation and follow the first section of this
runbook.

**Why it exists.** On 2026-08-19 the cookie expired. Job 1 filed its issue and
then reported success every day for 28 days, because an expired cookie is exit
code 2 and the workflow deliberately exits 0 on it. Job 2 correctly found nothing
to annotate and reported "no new solves — expected outcome" every day. The
watchdog stayed quiet too, because the only question it asked was "is anything
pending?" and nothing was pending — nothing was pending because nothing was
arriving. Every indicator in the system read green for four weeks while real
solves went unfetched.

An empty queue is only good news if the thing that fills it still works. That is
now checked:

```
/usr/bin/python3 scripts/check_pending.py     # exit 3 == fetch has stalled
```

Exit codes: `0` all current, `1` annotations overdue, `2` manifest unreadable,
`3` no successful fetch in 72 h. The annotate routine runs this before calling a
no-op run healthy, so a stalled fetcher is now named by both Job 2 and Job 4
rather than by neither.

## Where the jobs live

| Job | Where | Schedule (UTC) | Holds |
|---|---|---|---|
| 1 — fetch | `.github/workflows/fetch.yml` | `0 17 * * *` (1 pm ET) | the LeetCode cookie |
| 2 — annotate | <https://claude.ai/code/routines> | 2:00 PM ET (local, DST-aware) | nothing |
| 3 — promote | `.github/workflows/promote.yml` | when Job 2 pushes a branch | nothing |
| 4 — watchdog | `.github/workflows/watchdog.yml` | `0 20 * * *` (4 pm ET) | nothing |

Both crons are UTC and do not follow daylight saving, so from November to March
they fire an hour earlier in Eastern terms — noon and 1 pm instead of 1 pm and
2 pm. Harmless; bump both by an hour if it bothers you. Routines cannot be
deleted via the API — manage them at the URL above.
