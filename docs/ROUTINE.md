# Job 2 — the annotation routine

Job 2 is a **Claude scheduled cloud routine**. It holds no credentials and makes
no API call: the scheduled agent *is* Claude, which is the whole reason this
system needs no Anthropic API key.

**The prompt lives in [`routine-prompt.txt`](routine-prompt.txt)** — one file,
nothing but the prompt, so setting up the routine is a single copy-paste and
there is no second copy of the text to drift out of sync with this document.

| | |
|---|---|
| **Prompt** | [`docs/routine-prompt.txt`](routine-prompt.txt) |
| **Schedule** | `41 7 * * *` UTC (~03:41 America/New_York) |
| **Model** | `claude-opus-5` |
| **Source** | this repo, cloned fresh each run |
| **Credentials** | none |

`41 7` is ~1.5 h after Job 1's `13 6`, so the two can never race. Routine crons
are UTC and don't shift with DST, so the local time drifts an hour in winter —
irrelevant for an overnight job.

## Setting it up (one time, a couple of minutes)

1. Go to <https://claude.ai/code/routines> and create a new routine.
2. **Source:** `yadava5/leetcode-portfolio`, branch `main`.
3. **Schedule:** `41 7 * * *`, UTC. (If the UI asks for a friendly time instead
   of cron, that's 07:41 UTC daily.)
4. **Model:** `claude-opus-5` — the field may default to Sonnet; annotation
   quality is the product here, so change it.
5. **Prompt:** paste the entire contents of `docs/routine-prompt.txt`.
6. Save, then trigger one run immediately rather than waiting for the cron.

Copy the prompt to your clipboard without opening an editor:

```
/usr/bin/pbcopy < ~/Documents/Projects/leetcode-portfolio/docs/routine-prompt.txt
```

### Checking that first run

Everything is currently annotated, so a run right now should correctly do
**nothing**. Make it do real work first:

```
cd ~/Documents/Projects/leetcode-portfolio
/usr/bin/python3 - <<'EOF'
import json, pathlib
p = pathlib.Path("data/manifest.json"); m = json.loads(p.read_text())
m["problems"]["two-sum"]["annotated"] = False
p.write_text(json.dumps(m, indent=2) + "\n")
EOF
/usr/bin/git add data/manifest.json
/usr/bin/git commit -F /dev/stdin <<'EOF'
chore: mark two-sum for re-annotation

Giving the new cloud routine real work on its first run.
EOF
/usr/bin/git push origin main
```

Then trigger the routine and confirm four things:

1. It committed `docs: annotate 1 problem` — and **not** a
   `Co-Authored-By: Claude` trailer:
   `/usr/bin/git fetch origin && /usr/bin/git log origin/main --pretty=%B -1`
2. `/usr/bin/python3 scripts/verify_ast.py --all` still passes 4 checks.
3. The regenerated README doesn't contain LeetCode's prose. If the routine had no
   network egress it will have said so in the page itself.
4. A **second** immediate run does nothing at all and commits nothing.

If step 1 shows a trailer, the routine ignored `CLAUDE.md`; make the instruction
louder in `routine-prompt.txt` before trusting it unattended.

## Changing the prompt later

Edit `routine-prompt.txt`, commit it, **and paste the new version into the
routines UI** — nothing syncs them automatically. The file is version-controlled
precisely so that the diff is reviewable.

Then mark problems stale so they regenerate under the new prompt (recipe 1 in
`../CLAUDE.md`).

Don't schedule an untested prompt. Test by pointing an interactive Claude session
at this repo and having it follow `routine-prompt.txt`, then read the generated
README yourself. That is how the two problems currently in the repo were
produced. **The READMEs are the product** — if one wouldn't actually help you redo
the problem cold, the prompt needs work, not the schedule.

## Deleting a routine

The API can't; use <https://claude.ai/code/routines>.
