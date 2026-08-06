# Architecture

## Why two jobs

There is no Anthropic API key in this system and there must never be one. That
constraint, plus one security fact, produces the whole design.

The security fact: a Claude cloud routine **cannot read local files or
environment variables**, so the only channel for handing it a LeetCode cookie
would be its own prompt text — which stores a live credential as plaintext
config, visible in the routines UI and echoed into every run transcript. That is
a real downgrade from a proper secret store, so the work is split instead:

| | Job | Holds | Is | Runs daily at |
|---|---|---|---|---|
| 1 | fetch | the LeetCode cookie, in GitHub's encrypted secret store | a plain TypeScript script, no model | `0 17 * * *` |
| 2 | annotate + render | no credentials at all | Claude — the agent *is* the model, so nothing is called | 2:00 PM ET |
| 3 | promote | nothing | a GitHub Action that re-verifies and fast-forwards `main` | on Job 2's push |
| 4 | watchdog | nothing | a GitHub Action that files an issue if anything is stuck | `0 20 * * *` |

Jobs 3 and 4 exist because Job 2 is the only part that can neither push to `main`
nor be trusted blindly. See [How Job 2's work reaches main](#how-job-2s-work-reaches-main).

Each job holds exactly one of the two sensitive things and never needs the
other's. Job 2 starts an hour after Job 1 so they cannot race — GitHub can
delay a scheduled workflow by tens of minutes under load, so the gap is margin
rather than decoration. If Job 1 were ever so late that Job 2 ran first, Job 2
would find nothing pending and stop; the annotation would simply land the next
day. Late, never wrong.

## Job 1 stages

All three are driven by `data/manifest.json`.

1. **fetch** — `submissionList(offset, limit: 20)`, paging while `hasNext`,
   stopping at `manifest.lastSyncedTimestamp`. Keeps the latest **accepted**
   submission per `titleSlug`. At 4–10 solves/day one page suffices; the loop
   pages anyway so a missed week catches up.
2. **hydrate** — `submissionDetails(id)` for code, runtime, memory and
   percentiles; `question(titleSlug)` for the frontend id, difficulty, topic tags
   and similar questions. Question metadata is cached to
   `data/questions/<slug>.json`, so re-solving a problem costs one call, not two.
3. **commit** — write `data/raw/<slug>.py` and `data/questions/<slug>.json`,
   update the manifest (new or changed entries get `annotated: false`), commit
   `chore: sync N new submission(s)`.

Throttle: **1 request/second**, with `3^n × 1000 ms` backoff and 5 retries on 429
and 5xx. LeetCode publishes no numeric rate limit and returns bare 429s, so this
is the community-standard safe cadence rather than a documented one.

Zero runtime dependencies — native `fetch`. The three query shapes were verified
against the live authenticated API before `src/leetcode.ts` was written, so a
wrapper library would add a dependency and a moving part without adding
certainty.

### Exit codes

`src/cli.ts` returns codes the workflow branches on:

| Code | Meaning | Workflow behaviour |
|---|---|---|
| 0 | success, including "nothing new" | normal |
| 2 | the session cookie is dead | files/updates the `LeetCode session expired` issue, run stays green |
| 1 | anything else | run fails |

An expired cookie is **never** allowed to look like a quiet day. It is detected
three ways: HTTP 401/403, `userStatus.isSignedIn` coming back false before any
fetching happens, and an authenticated field returning `null` or empty `code`
(unauthenticated callers get metadata with no code).

### How Job 2's work reaches main

Job 2 **cannot push to main.** A Claude cloud routine is pinned to a feature
branch by its own environment policy, so it commits there and stops. The missing
half is `.github/workflows/promote.yml`, which fires on a push to any branch
other than `main` and:

1. confirms the subject is `docs: annotate ...` and carries no `Co-Authored-By`
   trailer — a human branch pushed by accident is never silently merged, which is
   also why the trigger can safely be "every branch but main" rather than a
   branch-name pattern the routine never promised to keep;
2. confirms only `problems/`, `indexes/`, the root `README.md` and
   `data/manifest.json` changed, and that **`data/raw` is byte-identical** — if
   the gate's reference copy moved, the guarantee is void;
3. re-runs `test_verify_ast.py` and `verify_ast.py --all`;
4. re-runs `render_indexes.py` and fails if the committed README or indexes
   differ from what the script produces;
5. fast-forwards `main` (never `--force`) and deletes the branch.

This is better than a direct push, not a workaround for one. **The gate now runs
twice, in two places, and the second run is somewhere the annotator has no
influence over.** An annotation that modified Ayush's code would have to defeat
the gate inside the routine *and* again in a CI job it cannot touch.

The consequence to remember: a green routine run is not the same as work landing
on `main`. Check the `promote` workflow if a problem page doesn't appear.

### If a push loses a race

Both jobs commit and push to `main` an hour apart, so a collision is unlikely but
not impossible. Neither job pulls, rebases or merges — deliberately. If a push is
rejected the run fails loudly and **nothing is lost**, because the state that
matters (`lastSyncedTimestamp`, and `annotated` / `annotationHash`) only advances
on `origin` once a push succeeds. The next scheduled run starts from a fresh
clone and redoes exactly the work that didn't land. Self-healing beats clever git
logic running unattended with nobody watching.

## The guarantee: the code is provably unmodified

- `data/raw/<slug>.py` — the submitted code, verbatim. Written only by Job 1.
  Source of truth.
- `problems/<n>-<slug>/solution.py` — a derived artifact: the same code plus
  comments.
- `problems/<n>-<slug>/README.md` — shows the same annotated solution inline, so
  one page holds the problem and the code.
- `scripts/verify_ast.py` — parses each and compares
  `ast.dump(tree, annotate_fields=True, include_attributes=False)`.

The README's inline copy is gated too: any fenced `python` block containing
`class Solution` is treated as a claim to be the real submission and verified as
one. An ungated second copy would be free to drift, which would quietly turn the
guarantee into a half-guarantee. Code fragments quoted in prose therefore use
inline backticks or a fence tagged something other than `python`.

Python's parser discards comments and blank lines entirely, so they cannot appear
in an AST. Equal dumps therefore mean the two files describe the identical
program and every byte of difference is a comment or whitespace. A renamed
variable, a reordered statement, a changed literal, an added docstring
(docstrings **are** AST nodes) or a "helpful" bug fix each change the dump and
are rejected. `include_attributes` is deliberately `False`, because line and
column numbers move when comments are inserted.

Job 2 runs the gate itself before committing, so the guarantee holds even though
an agent produced the annotation. On mismatch it discards that problem's output,
writes nothing and reports the failure.

`scripts/test_verify_ast.py` asserts the gate in **both** directions — 3 cases
that must pass and 5 that must fail. A gate that only ever passes is not a gate,
so CI runs this self-test on every fetch.

### Extension point: other languages

AST equality is exact only because Python's grammar discards comments. Adding
Java or C++ later needs a different comparison: strip comments with a real lexer
for that language, normalise whitespace, then compare the remaining token
stream. That is weaker than AST equality (it cannot see that two token streams
mean the same thing) but it is the right shape. Do not try to reuse
`verify_ast.py` — it would silently pass anything it cannot parse as Python.
Ayush solves exclusively in Python, so this is a note, not a plan.

## Copyright

The repo is public and LeetCode's problem statements are copyrighted. Therefore:

- Job 1 fetches `content`, mines the **constraint bounds** out of it, and then
  discards it. The statement is never written to disk and `hints` are never even
  requested.
- The bounds *are* kept, in `data/questions/<slug>.json` as `constraints`:
  `"2 <= nums.length <= 10^4"` and the like. This is a deliberate line, and the
  reasoning is that a mathematical bound on an input is a **fact about the
  problem, not creative expression** — the same way "water boils at 100°C" isn't
  the copyright of the textbook it appears in. `extractConstraints` enforces the
  line mechanically: it keeps only list items that look like bounds, discards
  anything longer than 120 characters, and caps the list at 12. The pre-commit
  hook independently rejects any entry over that length, so a sentence that
  slipped through the extractor still cannot be committed.
- Why bother: Job 2's sandbox **cannot reach leetcode.com**, and the constraints
  are precisely what dictate the required complexity. Without this, every page
  would say "recalled, not read" and the bounds would come from a model's memory.
  Job 1 has network; Job 2 has judgement. Each does the part it can actually do.
- `.githooks/pre-commit` blocks any `data/questions/*.json` that contains
  `content`, `hints`, `mysqlSchemas` or `exampleTestcases`, so a regression is
  caught mechanically rather than noticed later.
- Job 2 restates each problem in Ayush's own words in 2–3 sentences and links to
  the original. It reads the statement from LeetCode's **public** GraphQL at
  annotate time — no cookie is needed for that — and writes only the
  restatement. If the routine has no network egress it falls back to restating
  from the title, topic tags and the code itself, and says so in the README.

Because history is append-only here (force push, hard reset and `clean -fdx` are
all on the global deny list), a copyrighted statement committed once could not be
removed by a later commit. Hence a guard rather than a convention.

## Manifest schema

```jsonc
{
  "version": 1,
  "lastSyncedTimestamp": 1785974009, // highest ingested submission time
  "lastSyncedAt": "2026-08-06T02:44:00.000Z",
  "problems": {
    "two-sum": {
      "frontendId": "1",
      "title": "Two Sum",
      "slug": "two-sum",
      "difficulty": "Easy",
      "topics": ["Array", "Hash Table"],
      "url": "https://leetcode.com/problems/two-sum/",
      "submissionId": "2095951203",
      "timestamp": 1785973514, // drives indexes/review-queue.md
      "lang": "Python3",
      "runtime": "3 ms",
      "runtimePercentile": 53.8,
      "memory": "20.5 MB",
      "memoryPercentile": 17.5,
      "similar": ["3sum", "4sum"],
      "codeHash": "ef54…", // sha256 of data/raw/two-sum.py
      "annotationHash": "ef54…", // codeHash the annotation was written against
      "annotated": true
    }
  }
}
```

`annotationHash != codeHash` is how re-solving a problem invalidates its
annotation without any extra state: Job 1 resets it, Job 2 notices, regenerates,
and sets it back. Identical code keeps the existing annotation, which is what
makes both jobs idempotent.

## What is generated

`problems/`, `indexes/` and the root `README.md` are generated in full on every
Job 2 run. Nothing there should ever be hand-edited; the next run overwrites it.
`data/` is written only by Job 1. `src/`, `scripts/`, `docs/` and the config
files are the only hand-written parts of the repo.
