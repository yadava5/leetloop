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

## Where the two jobs live

| Job | Where | Schedule (UTC) | Holds |
|---|---|---|---|
| 1 — fetch | `.github/workflows/fetch.yml` | `0 17 * * *` (1 pm ET) | the LeetCode cookie |
| 2 — annotate | <https://claude.ai/code/routines> | `0 18 * * *` (2 pm ET) | nothing |

Both crons are UTC and do not follow daylight saving, so from November to March
they fire an hour earlier in Eastern terms — noon and 1 pm instead of 1 pm and
2 pm. Harmless; bump both by an hour if it bothers you. Routines cannot be
deleted via the API — manage them at the URL above.
