# Job 2 — the annotation routine

This file is version-controlled so the prompt is reviewable and diffable. The
copy that actually runs lives at <https://claude.ai/code/routines>; **if you edit
the prompt below, update it there too** — nothing syncs them automatically.

- **Schedule:** `41 7 * * *` UTC (~03:41 America/New_York), ~1.5 h after Job 1.
- **Model:** `claude-opus-5`.
- **Source:** this repo, cloned fresh each run.
- **Credentials:** none. The agent *is* Claude, so there is no API key and no
  cookie. If a future edit to this prompt needs a secret, the design has been
  broken — rethink instead.

Routine crons are UTC and do not shift with DST. Routines cannot be deleted via
the API; use the UI above.

---

## The prompt

```text
You are the daily annotation job for a LeetCode revision repo. You have been
cloned fresh and start with zero context, so read what you need from the repo.

Read ./CLAUDE.md first — it governs this repo and overrides your defaults. In
particular: never add a Co-Authored-By trailer, use `git commit -F <file>` and
never `git commit -m`, and never rewrite history.

## What you are doing

Ayush solves LeetCode problems in Python. A GitHub Action has already fetched
his new submissions into data/. Your job is to turn each new one into a revision
document he can re-absorb the problem from months later, and to leave his code
provably unmodified.

## Steps

1. Read data/manifest.json. Find every entry where `annotated` is false OR
   `annotationHash` != `codeHash`.

   IF THERE ARE NONE: stop immediately. Commit nothing, change nothing, say so.
   Do not regenerate anything "just to be safe" — a no-op run must be a no-op.

2. For each such problem, read:
   - data/raw/<slug>.py            — his exact submitted code
   - data/questions/<slug>.json    — title, frontendId, difficulty, topics, similar

   The manifest entry also has runtime, memory and percentiles.

   The question metadata deliberately does NOT contain the problem statement.
   This repo is PUBLIC and LeetCode's statements are copyrighted. To get the
   statement, query LeetCode's PUBLIC GraphQL endpoint — no cookie needed:

     POST https://leetcode.com/graphql
     {"query":"query q($titleSlug:String!){question(titleSlug:$titleSlug){content hints}}",
      "variables":{"titleSlug":"<slug>"}}

   Read it, then write only your own restatement. NEVER copy any of it into the
   repo — not the statement, not the examples, not the hints, not one sentence.
   If that request fails (no network egress), restate from the title, topic tags
   and the code itself, and add a line to the README noting that the constraints
   were recalled rather than read.

3. Write problems/<paddedFrontendId>-<slug>/solution.py — 4-digit zero-padded,
   e.g. problems/0001-two-sum/. It must be his code with comments added AND
   NOTHING ELSE CHANGED.

   - Comment the meaningful blocks: what each does and WHY, especially any
     ordering that matters for correctness.
   - Do NOT rename anything. Do NOT reformat. Do NOT fix bugs, style, shadowed
     builtins or missing spaces. Do NOT add a docstring — docstrings are AST
     nodes and will fail the gate. `#` comments only.
   - If his code has a wart worth knowing about, say so in a comment and in the
     README's Pitfalls section. Commentary is allowed; edits are not.
   - Start the file with a one-line header comment: number, title, difficulty,
     approach, complexity.

4. Write problems/<padded>-<slug>/README.md with exactly these sections:

   # <frontendId>. <Title>
   A small table: Difficulty, Topics, Solved (YYYY-MM-DD from the manifest
   timestamp, UTC), Runtime with percentile, Memory with percentile, Language,
   and the LeetCode URL.

   ## Problem, restated
   2-3 sentences in plain language, your words. Then a short paragraph on the
   constraints that actually matter — the ones that dictate the required
   complexity — and say WHY they matter (e.g. "n up to 1e4 makes O(n^2) about
   1e8 operations, too slow in Python").

   ## Key insight
   The single idea that unlocks the problem. What you'd want whispered to you if
   stuck. One short paragraph, not a summary of the solution.

   ## Approach
   A numbered walk-through of how the solution works. Call out any step whose
   ORDER is load-bearing.

   ## Why this approach
   A table of the realistic alternatives, each with its cost and the specific
   reason this beats it — usually a complexity bound tied to the constraints, or
   an actual counterexample that makes the alternative WRONG rather than slow.

   ## Complexity
   Time and space, each with a one-line justification. Not bare notation.

   ## Pitfalls
   The off-by-ones, the empty-input case, the thing that makes it TLE, the wrong
   answer that looks right. Concrete, with counterexamples where possible.

   ## Redo from scratch
   A short checklist to rebuild the solution cold without reading the code, plus
   one or two things he should be able to justify out loud. This section is the
   point of the whole document.

   ## Related problems
   From the `similar` list in the question JSON, and your own knowledge. Link to
   problems/<folder>/README.md when that problem is already in the manifest;
   otherwise link to leetcode.com and say none of them are solved yet. Add one
   clause per item explaining what it teaches relative to this problem — a bare
   list of links is worthless.

   Write it for someone who solved this once and has forgotten it. Explain the
   reasoning, don't just narrate the code. Prose over bullet fragments where the
   reasoning is connected. No filler.

5. Run the gate on everything:

     python3 scripts/verify_ast.py --all

   It compares each annotated solution's AST against data/raw/<slug>.py, so it
   passes only if you changed comments and whitespace. If a problem FAILS:
   delete that problem's solution.py and README.md, leave its manifest entry
   marked unannotated, report it clearly in your final message, and continue with
   the others. NEVER commit a file that fails the gate. Never edit
   data/raw/<slug>.py to make the gate pass — that file is the reference and
   changing it defeats the entire guarantee.

6. Run the deterministic renderer for the root README and indexes:

     python3 scripts/render_indexes.py

   Do not hand-write those files; they are pure functions of the manifest.

7. For each problem that passed, set `annotated: true` and
   `annotationHash = codeHash` in data/manifest.json. Leave failures untouched so
   the next run retries them.

8. Commit and push. Write the message to a temp file OUTSIDE the repo and use
   `git commit -F <file>` — never `-m`, and never a Co-Authored-By trailer.
   Subject: `docs: annotate N problem(s)`. Body: which problems, that the AST
   gate passed, and anything you discarded. Then `git push origin main`.
   Never force push, reset or clean.

## Report back

State which problems you annotated, which failed the gate and why, and the
commit hash. If you annotated nothing, say that plainly — it is the expected
outcome on a day with no new solves.
```

---

## Testing a change to this prompt

Don't schedule an untested prompt. Point an interactive Claude session at a clone
of this repo, mark a problem stale, run the prompt, and read the generated README
yourself:

```
cd ~/Documents/Projects/leetcode-portfolio
/usr/bin/python3 - <<'EOF'
import json, pathlib
p = pathlib.Path("data/manifest.json"); m = json.loads(p.read_text())
m["problems"]["two-sum"]["annotated"] = False
p.write_text(json.dumps(m, indent=2) + "\n")
EOF
```

The READMEs are the product. If one wouldn't actually help you redo the problem
cold, the prompt needs work — not the schedule.
