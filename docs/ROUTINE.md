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
| **Schedule** | daily at **2:00 PM** America/New_York |
| **Model** | **Opus 5** |
| **Source** | this repo, cloned fresh each run |
| **Credentials** | none |

2:00 PM is an hour after Job 1's 17:00 UTC (1:00 PM Eastern in summer), so the
two cannot race.

Note the asymmetry: the routines UI schedules in **local time and follows
daylight saving**, while a GitHub cron is **UTC and does not**. So in winter Job 1
slides to noon Eastern while Job 2 stays at 2 PM — the gap widens to two hours,
which is harmless. The ordering, which is the only thing that matters, never
inverts.

## Setting it up (one time, a couple of minutes)

1. Go to <https://claude.ai/code/routines> and create a new routine.
2. **Source:** `yadava5/leetloop`, branch `main`.
3. **Trigger:** Schedule → **Daily**, at **02:00 PM**. The UI schedules in your
   local timezone and follows daylight saving.
4. **Model:** **Opus 5** — the field defaults to Opus 4.5; annotation quality is
   the product here, so change it.
   **Remove every connector.** The form pre-attaches whatever you have connected
   (Gmail, Drive, Supabase, Vercel…). This routine needs none of them, and an
   unattended agent should not hold your inbox and database. They come back on
   save — remove them again via Edit and save a second time.
5. **Prompt:** paste the entire contents of `docs/routine-prompt.txt`.
6. Save, then trigger one run immediately rather than waiting for the cron.

Copy the prompt to your clipboard without opening an editor:

```
/usr/bin/pbcopy < ~/Documents/Projects/leetloop/docs/routine-prompt.txt
```

### Checking that first run

Everything is currently annotated, so a run right now should correctly do
**nothing**. Make it do real work first:

```
cd ~/Documents/Projects/leetloop
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

### Two things the first real run taught us

Both are now handled, but they explain why the setup looks the way it does.

**It needs Anthropic's Claude GitHub App installed, with write access.** Without
it the routine clones fine (public repo) and then fails `git push` with a bare
`403`, having done all the work. Install at
<https://github.com/apps/claude/installations/new> and scope it to this
repository only. Symptom to recognise: the run reports success on the annotation
and then hands you a patch file.

**It pushes to a feature branch, never to `main`.** The routine's environment
pins it to a branch, so `.github/workflows/promote.yml` does the last mile —
re-running the gate on CI and fast-forwarding `main`. A green run therefore does
**not** mean the work landed; check the `promote` workflow if a page is missing.

**LeetCode is unreachable from the routine.** The sandbox refuses `CONNECT
leetcode.com:443`. Every page carries a "recalled, not read" note under
Constraints. Honest, but it means the exact bounds come from memory.

Then trigger the routine and confirm five things:

1. The `promote` workflow ran and `main` moved — and the commit carries no
   `Co-Authored-By: Claude` trailer:
   `/opt/homebrew/bin/gh run list --workflow promote.yml --repo yadava5/leetloop`
   then `/usr/bin/git fetch origin && /usr/bin/git log origin/main --pretty='%an %s' -1`
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
