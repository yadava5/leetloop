# Architecture

## Why two jobs

There is no Anthropic API key in this system and there must never be one. That
constraint, plus one security fact, produces the whole design.

The security fact: a Claude cloud routine **cannot read local files or
environment variables**, so the only channel for handing it a LeetCode cookie
would be its own prompt text — which stores a live credential as plaintext
config, visible in the routines UI and echoed into every run transcript. That is
a real downgrade from a proper secret store, so the work is split instead:

| | Job | Holds | Is | Schedule (UTC) |
|---|---|---|---|---|
| 1 | fetch | the LeetCode cookie, in GitHub's encrypted secret store | a plain TypeScript script, no model | `13 6 * * *` |
| 2 | annotate + render | no credentials at all | Claude — the agent *is* the model, so nothing is called | `41 7 * * *` |

Each job holds exactly one of the two sensitive things and never needs the
other's. Job 2 starts ~1.5 h after Job 1 so they cannot race.

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

## The guarantee: the code is provably unmodified

- `data/raw/<slug>.py` — the submitted code, verbatim. Written only by Job 1.
  Source of truth.
- `problems/<n>-<slug>/solution.py` — a derived artifact: the same code plus
  comments.
- `scripts/verify_ast.py` — parses both and compares
  `ast.dump(tree, annotate_fields=True, include_attributes=False)`.

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

- Job 1 **never persists** `content` or `hints`. `src/leetcode.ts` fetches only
  what it needs and `QuestionMeta` has no field for them.
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
