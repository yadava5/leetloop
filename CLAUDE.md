# leetcode-portfolio — project contract

Governed by `~/CLAUDE.md`. This file adds only what is specific to this repo.

## Mental model

This repo fills itself. Two scheduled jobs do the work, and they are split along
a secret boundary so that **neither one ever needs an Anthropic API key**:

| | Job | Holds | Runs as | When (UTC) |
|---|---|---|---|---|
| 1 | **fetch** — pull new submissions, commit raw data | the LeetCode cookie | GitHub Action, no model involved | `13 6 * * *` |
| 2 | **annotate** — write the revision docs | no credentials at all | Claude cloud routine (Claude *is* the runtime) | `41 7 * * *` |

Job 2 runs ~1.5 h after Job 1 so the two never race.

**There is no Anthropic API key anywhere in this system, and there must never be
one.** Job 2 needs no key because the scheduled agent is itself Claude. If you
ever find yourself reaching for `ANTHROPIC_API_KEY`, the design has been
misunderstood.

### What is source and what is generated

- **Source of truth**: `data/raw/<slug>.py` — your submitted code, verbatim, byte
  for byte. Written only by Job 1.
- **Generated, never hand-edited**: everything under `problems/`, everything
  under `indexes/`, and the root `README.md`. The next run overwrites them.
- **The guarantee**: `problems/<n>-<slug>/solution.py` is `data/raw/<slug>.py`
  plus comments — *provably*. `scripts/verify_ast.py` parses both and compares
  `ast.dump(...)`. Comments and blank lines are invisible to Python's AST, so
  equal dumps mean only comments and whitespace changed. A renamed variable, a
  reordered line, a "helpful" fix — each produces a different dump and the
  annotation is discarded rather than committed.

### The repo is public

LeetCode problem statements are copyrighted. Every word of prose in `problems/`
is a restatement in Ayush's own words plus a link to the original. Job 1 strips
`content` and `hints` from question metadata before writing it, and
`.githooks/pre-commit` blocks the commit if they reappear.

## Recipes

### 1. Re-annotate one problem

```
/usr/bin/python3 - <<'EOF'
import json, pathlib
p = pathlib.Path("data/manifest.json"); m = json.loads(p.read_text())
m["problems"]["<slug>"]["annotated"] = False
p.write_text(json.dumps(m, indent=2) + "\n")
EOF
```

Then run Job 2's prompt (`docs/routine-prompt.txt`) in a Claude session pointed
at this repo, or wait for the nightly routine.

### 2. Sync now, without waiting for the cron

```
/opt/homebrew/bin/gh workflow run fetch.yml          # remote, uses the stored secret
npm run build && node dist/cli.js --only <slug>      # local, uses ~/.leetcode.env
node dist/cli.js --dry-run                           # local, writes nothing
```

### 3. Refresh the cookie (every 1–2 weeks, when the issue lands)

See `docs/RUNBOOK.md`. Two `gh secret set` commands, under a minute.

### 4. Change what a problem README looks like

Edit the template section of `docs/routine-prompt.txt`, then mark problems
`annotated: false` (recipe 1) so they regenerate. That file is Job 2's entire
prompt, version-controlled so it is reviewable and diffable — and the copy
running in the cloud must be pasted over to match, at
`https://claude.ai/code/routines`. Nothing syncs them automatically.
`docs/ROUTINE.md` explains the setup around it.

### 5. Change the AST gate

`scripts/verify_ast.py`, then `npm run test:gate`. The test asserts both
directions and must keep doing so.

## Don'ts, each with its reason

- **Don't hand-edit `problems/`, `indexes/`, or root `README.md`.** The next
  scheduled run overwrites them and your edit vanishes silently.
- **Don't edit `data/raw/*.py`.** It is the gate's reference copy. Editing it
  doesn't change your LeetCode submission — it just makes the gate compare the
  annotation against something that isn't your code, which defeats the entire
  guarantee.
- **Don't commit with `git commit -m`.** Use `git commit -F <file>`.
  `~/.claude/hooks/block-destructive.sh` substring-matches raw command text, and
  these messages carry generated prose and problem titles; a message containing
  a dangerous-looking literal blocks the commit.
- **Don't add a `Co-Authored-By: Claude` trailer.** Commits are Ayush's. This
  applies to both jobs permanently, not just to interactive sessions.
- **Don't rewrite history.** `git push --force`, `git reset --hard` and
  `git clean -fdx` are on the global deny list. Both jobs are append-only by
  design; if a run produced something wrong, fix it forward with a new commit.
- **Don't use `--no-verify`.** The pre-commit hook is what stops a credential or
  a copyrighted problem statement from reaching a public repo.
- **Don't write LeetCode's problem text into the repo.** Restate it. The hook
  will block `content` and `hints` in `data/questions/*.json`, but it can't tell
  that a paragraph in a README was copy-pasted — that one is on you.
- **Don't introduce an Anthropic API call.** See the mental model above.
- **Use absolute paths in scripts and verification commands.** Interactive
  aliases shadow POSIX tools (`ls`→eza, `cat`→bat, `diff`→difftastic,
  `du`→dust); on macOS `ls`/`cat`/`rm`/`cp`/`mkdir`/`chmod` are in `/bin`.
