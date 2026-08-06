# Running your own leetloop

This repo is a working system, not a demo, and it's built so a fork needs **no
code edits** — only your own credentials and a scheduled agent. Budget about ten
minutes.

Before you start, the honest prerequisites:

| You need | Why | Substitute? |
|---|---|---|
| A GitHub account | Job 1 runs as a GitHub Action on the free tier | no |
| A LeetCode account you stay logged into | the fetch needs your session cookie | no |
| You solve in **Python** | the AST gate that proves your code was not modified is exact only for Python | see [Other languages](#other-languages) |
| A Claude plan that includes **scheduled routines** | Job 2 is a scheduled agent, which is how the system avoids ever needing an Anthropic API key | see [Without routines](#without-scheduled-routines) |

---

## 1. Fork, and clear out my data

Fork on GitHub, clone your fork, then delete my problems. Everything except
`data/` is generic; `data/` is my submission history and is meaningless to you.

```
git clone git@github.com:<you>/leetloop.git
cd leetloop

/bin/rm -r data problems indexes
/bin/mkdir -p data
/usr/bin/python3 - <<'EOF'
import json, pathlib
pathlib.Path("data/manifest.json").write_text(
    json.dumps({"version": 1, "lastSyncedTimestamp": 0,
                "lastSyncedAt": None, "problems": {}}, indent=2) + "\n")
EOF
/usr/bin/python3 scripts/render_indexes.py
```

That last command regenerates an empty `README.md` and `indexes/` from the empty
manifest, so the front page reflects your repo rather than mine.

Commit it. Note `-F`, not `-m`: commit messages here routinely contain code
snippets and problem titles, and some shell hooks pattern-match raw command text.

```
git add -A
git commit -F - <<'EOF'
chore: reset fork to an empty manifest

Cleared the upstream author's submission data so the pipeline starts from zero.
EOF
git push origin main
```

`lastSyncedTimestamp: 0` means the first run pulls **everything** your session
cookie can page through, not just today. If you have hundreds of solved problems
that first run will take a while and will annotate a large batch — see
[Large histories](#large-histories).

## 2. Add your two secrets

Open <https://leetcode.com> while logged in → DevTools → **Application** →
**Cookies** → `https://leetcode.com`. Copy `LEETCODE_SESSION` (long) and
`csrftoken` (32 characters).

```
gh secret set LEETCODE_SESSION --repo <you>/leetloop
gh secret set LEETCODE_CSRF_TOKEN --repo <you>/leetloop
```

Paste when prompted so the values never enter your shell history. These are the
only credentials in the entire system, they live in GitHub's encrypted secret
store, and the half of the system that talks to a model never sees them.

For local runs, put the same two keys in `~/.leetcode.env` — **outside** the repo
on purpose, because the repo is public and a credential that physically cannot be
committed beats one protected only by `.gitignore`:

```
LEETCODE_SESSION=...
LEETCODE_CSRF_TOKEN=...
```

## 3. Enable Actions on your fork

**This is the step people miss.** GitHub disables scheduled workflows in forked
repositories, and a disabled cron looks exactly like a working system that never
finds anything.

Go to your fork's **Actions** tab, enable workflows if prompted, then confirm the
schedule is live:

```
gh workflow list --repo <you>/leetloop        # fetch should be "active"
gh workflow run fetch.yml --repo <you>/leetloop
gh run watch --repo <you>/leetloop
```

Two related GitHub behaviours worth knowing now rather than in six weeks:

- **Scheduled workflows are disabled after 60 days with no repository activity.**
  If you stop solving for two months the cron switches off and GitHub emails you.
  A single commit re-arms it.
- Scheduled runs can be **delayed by tens of minutes** under load. That's why Job
  2 is an hour behind Job 1 rather than a few minutes.

If you want a different time, there are two places, and they behave differently:

- `.github/workflows/fetch.yml` → `cron: "0 17 * * *"`. **UTC, ignores daylight
  saving**, so its local time shifts by an hour twice a year.
- your routine's schedule, set in the routines UI. **Local time, follows daylight
  saving.**

Keep Job 2 after Job 1. If they ever invert, Job 2 finds nothing pending and
stops, so the annotation just lands a day late — late, never wrong.

## 4. Set your committer name (optional)

By default commits are authored as your GitHub username at
`<username>@users.noreply.github.com`, which always works and leaks nothing. To
use a real name:

```
gh variable set COMMITTER_NAME --repo <you>/leetloop --body "Your Name"
gh variable set COMMITTER_EMAIL --repo <you>/leetloop --body "you@example.com"
```

## 5. Create the annotation routine

Job 2 is a scheduled Claude routine. It holds **no** credentials — the scheduled
agent *is* the model, which is the entire reason this system needs no API key.

```
/usr/bin/pbcopy < docs/routine-prompt.txt
```

At <https://claude.ai/code/routines>, create a routine with:

| Field | Value |
|---|---|
| Source | your fork, branch `main` |
| Schedule | daily, an hour after Job 1 (local time in the UI) |
| Model | an Opus-class model — annotation quality *is* the product |
| Prompt | paste `docs/routine-prompt.txt` |

Two things about this that cost me a run each, so they're worth doing up front:

**Install Anthropic's Claude GitHub App and scope it to this repo**, at
<https://github.com/apps/claude/installations/new>. Without it the routine clones
happily — your fork is public — and then fails `git push` with a bare `403` after
doing all the work. Choose "Only select repositories" so an unattended agent
can't write to anything else you own.

**Remove every connector from the routine.** The form pre-attaches whatever your
account has connected — Gmail, Drive, Supabase, Vercel. This job needs none of
them. They reappear when you save, so remove them again via Edit and save twice.

The routine will push to a feature branch rather than `main`; that's expected, and
`.github/workflows/promote.yml` handles the last mile. See
[docs/ROUTINE.md](ROUTINE.md) for the first-run checklist.

## 6. Solve something, then wait

Solve any problem in Python. At the next 17:00 UTC the Action commits your code
verbatim to `data/raw/`. An hour later the routine writes
`problems/<id>-<slug>/README.md` and `solution.py`, runs the gate, and commits to
a feature branch. The `promote` workflow then re-runs the gate on CI and
fast-forwards `main`.

Impatient? `gh workflow run fetch.yml` and then trigger the routine by hand.

**Three runs, three places to look** if a page doesn't appear: the `fetch` Action,
the routine's own run log, and the `promote` Action. A green routine run alone
does not mean the work landed.

---

## What you're expected to maintain

Exactly one thing: **the LeetCode session cookie expires every 1–2 weeks and
cannot be refreshed programmatically.** No token-refresh flow exists — this is a
LeetCode limitation, not a design shortcut.

The pipeline makes that cheap rather than pretending otherwise. Job 1 exits with
code `2`, the workflow **stays green** and files a GitHub issue titled
`LeetCode session expired`, and GitHub emails you on issue creation. Repeat
failures comment on the same issue instead of opening new ones. The fix is the
two `gh secret set` commands from step 2 — see
[docs/RUNBOOK.md](RUNBOOK.md).

Nothing is lost while the cookie is dead. LeetCode keeps your full submission
history and the next good run resumes from `lastSyncedTimestamp`. Downtime costs
recency, not data.

An expired cookie is never allowed to look like a quiet day. It's detected three
ways: HTTP 401/403, an authenticated `userStatus` query returning
`isSignedIn: false` before any fetching happens, and an authenticated field
returning `null` or empty `code` — unauthenticated callers get metadata with no
code, so empty code means the cookie was ignored.

## Other languages

`scripts/verify_ast.py` proves the annotation only added comments by comparing
Python ASTs. That proof is exact **because Python's parser discards comments and
blank lines entirely**, so equal trees mean every byte of difference is a comment
or whitespace.

That reasoning does not transfer. If you solve in Java, C++ or Go you need a
different check: strip comments with a real lexer for that language, normalise
whitespace, then compare the remaining token stream. It's weaker than AST
equality — it can't see that two token streams mean the same thing — but it's the
right shape.

**Do not just point the existing gate at another language.** It would refuse to
parse the file and fail, which is safe, but the failure would look like a bug
rather than a design boundary. `docs/ARCHITECTURE.md` marks the extension point.

If you don't want the guarantee at all, you can delete the gate — but then
"the annotation never modified my code" becomes a promise instead of a fact, and
that promise is the most interesting property this repo has.

## Without scheduled routines

The two-job split exists so that no Anthropic API key is ever needed: Job 1 holds
the cookie and calls no model, Job 2 *is* a model and holds no secrets.

If you can't schedule a routine, your options, worst to best:

- **Run Job 2 by hand.** Point any Claude session at your clone and have it follow
  `docs/routine-prompt.txt`. Fully supported — that's how the two problems in the
  upstream repo were written, and how you should test prompt changes anyway.
- **A local scheduler** (cron, launchd) driving your coding agent. Works, but your
  machine has to be awake, which is the thing the cloud routine buys you.
- **A second GitHub Action calling an LLM API with a key.** This works and is what
  most similar projects do. Understand the trade: you reintroduce a paid
  credential, and the job that holds an API key is a job that can be abused if the
  secret leaks. Job 2's "no credentials at all" property is deliberate.

Job 1 is independent of all of this. Skip Job 2 entirely and you still get a
repo that mirrors your submissions verbatim, every day, with no notes.

## Large histories

If you've solved hundreds of problems, the first run differs from the steady
state this repo is tuned for:

- Job 1 pages `submissionList` 20 at a time at **1 request/second** with
  exponential backoff. Hundreds of problems means hundreds of seconds and two
  extra calls per problem to hydrate. Well within a job timeout, but not instant.
- **The real constraint is that your session cookie may die mid-backfill.** If it
  does, the run exits 2 and files the issue; everything already committed stays,
  and the next run resumes. Backfill is naturally resumable.
- Job 2 annotating hundreds of problems in one run is the part I'd actually
  worry about — long runs, and a lot of output to review at once. Consider seeding
  `lastSyncedTimestamp` to a recent date so you start from now and let history
  fill in only if you re-solve. The upstream repo was built forward-only from two
  problems for exactly this reason.

## Copyright, if you make your fork public

LeetCode's problem statements are theirs. This pipeline never persists them:
`hydrate` drops `content` and `hints`, Job 2 reads the statement at annotate time
and writes only its own restatement with invented examples, and
`.githooks/pre-commit` blocks that prose from reappearing in
`data/questions/*.json`.

Enable the hook — it isn't inherited by a clone, because hook path is local git
config:

```
git config core.hooksPath .githooks
```

The Action sets this itself for the same reason. History here is append-only, so
prose committed once could not be taken back by a later commit — which is why
there's a mechanical guard and not just a convention.

## Layout, so you know what's safe to change

```
src/                    Job 1 — TypeScript ESM, zero runtime dependencies
scripts/verify_ast.py   the gate — plain Python, no dependencies
scripts/render_indexes.py  root README + indexes/, deterministic
docs/routine-prompt.txt Job 2's entire prompt — edit this to change the notes
.github/workflows/      Job 1's schedule and the expired-cookie issue
data/                   written only by Job 1; data/raw/*.py is the gate's reference
problems/ indexes/ README.md   GENERATED — rewritten every run, never hand-edit
```

Want different notes? Edit `docs/routine-prompt.txt`, then mark problems
`annotated: false` so they regenerate, **and paste the new prompt into the
routines UI** — nothing syncs those automatically.

Questions worth opening an issue for: anything where this guide told you something
that turned out not to be true.
