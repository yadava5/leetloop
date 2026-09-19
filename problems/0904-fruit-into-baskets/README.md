# 904. Fruit Into Baskets

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Hash Table, Sliding Window |
| **Solved** | 2026-09-18 |
| **Runtime** | 192 ms (39.24th percentile) |
| **Memory** | 26.1 MB (14.26th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/fruit-into-baskets/ |

## The problem

A row of fruit trees. `fruits[i]` is an integer naming the **type** of fruit on
tree `i` — the number is a label, not a quantity. You carry **two baskets**, each
of which may hold only a single type of fruit but any number of pieces. You pick
a starting tree, then walk **right, tree by tree, taking exactly one fruit from
every tree you pass**, and you must stop the moment a tree's fruit fits in
neither basket. You may not skip a tree and you may not restart.

**Given** the array `fruits`.

**Return** the maximum number of fruits you can collect — an integer count.

Strip the story away and the question is: **what is the length of the longest
contiguous subarray containing at most 2 distinct values?** Since exactly one
fruit comes from each tree in the run, the count of fruits *is* the length of
the run. Two details the story hides:

- The two types need not be adjacent or interleaved in any particular way —
  `[2, 3, 2, 2]` is a legal run of four.
- You may use only one basket if you like ("at most 2", not "exactly 2"), so a
  uniform array is a legal answer of full length.

**Guaranteed**: the array is non-empty, so an answer of at least `1` always
exists, and every fruit type is a small non-negative integer.

```text
def totalFruit(self, fruits: list[int]) -> int
```

### Examples (mine, not LeetCode's)

| `fruits` | Returns | Why |
|---|---|---|
| `[1, 1, 1]` | `3` | **"At most two", not "exactly two".** One type fills one basket and the second stays empty; the whole array is legal. Any solution that insists on two distinct types answers `0` or `2` here. |
| `[1, 2, 3, 2, 2]` | `4` | **Counterexample to "add the two longest adjacent runs".** The runs are `1 \| 2 \| 3 \| 2,2`, and no two *adjacent* runs total more than `3`. The answer `[2, 3, 2, 2]` spans **three** runs — but only two distinct types, because the type `2` reappears after the `3`. Run-pairing is the most natural wrong idea here. |
| `[1, 2, 1, 2, 3]` | `4` | The window `[1, 2, 1, 2]` — two types alternating arbitrarily often. Also the input that catches measuring the window before shrinking it, which reports `5`. |
| `[0, 1, 2, 2, 2, 2]` | `5` | The answer `[1, 2, 2, 2, 2]` starts one past the left edge. Nothing about the best window is anchored to either end of the array. |
| `[0, 1, 0, 1, 0]` | `5` | **Edge-ish case:** the whole array qualifies because it only ever uses two types, however scrambled. Useful for checking that `left` never moves when it shouldn't. |
| `[5]` | `1` | **Edge case:** one tree. The `while` never runs, the window is `[0, 0]`, and the answer is the seed length of `1`. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= fruits.length <= 10^5` | The upper bound rules out checking every `(start, end)` pair: ~5 × 10⁹ windows, and counting distinct types inside each makes it worse. It demands an amortised linear scan — each of `left` and `right` crossing the array once. The lower bound of `1` is what makes the `not fruits` guard dead code and what guarantees a non-zero answer, so seeding `best_total = 0` is safe: the first iteration always measures a window of length at least `1`. |
| `0 <= fruits[i] < fruits.length` | Types are non-negative and bounded by `n`, so they are usable as **array indices**, not just hash keys — the dictionary could be a plain `[0] * len(fruits)` counter array with a separate distinct-count variable, which is a legitimate constant-factor win in Python and probably where the 192 ms could be improved. It also means types are opaque labels with no ordering worth exploiting: nothing is gained by sorting or comparing them, only by testing equality. Note the bound does *not* limit the number of distinct types to two — the input may contain many. |

## Key insight

The problem is not about baskets, it is about a window holding at most two
distinct values — and the crucial structural fact is **monotonicity**: if a
window is legal, every sub-window of it is legal too, and widening a window can
only add types, never remove them. That is exactly the condition a sliding window
needs. So walk the right edge forward one tree at a time and, whenever the window
becomes illegal, advance the left edge just far enough to make it legal again.
`left` never needs to move backwards, which is why one pass suffices.

The thing to whisper if stuck: *for each right end, find the smallest legal left
end — and it never moves back.*

## Approach

1. Keep `basket`, a map from fruit type to how many of that type are inside the
   window. Because zero-count keys are deleted, `len(basket)` **is** the number
   of distinct types in the window — that equality is the thing the loop tests.
2. Move `right` forward over every tree, adding its fruit to `basket` first. The
   window is momentarily illegal here, and that is fine.
3. While `len(basket) > k`, drop the tree at `left`: decrement its count, delete
   the key if it hits zero, and advance `left`. One tree at a time, re-testing
   each round.
4. Measure `right - left + 1` and keep the best.
5. Return the best.

Three things are load-bearing, in descending order of how badly they break:

- **Delete the key at zero.** `len(basket)` is only the distinct count if empty
  types are removed. Decrement without deleting and the `while` can never exit —
  `left` marches past the end of the array and the code raises `IndexError` on
  `[1, 2, 3, 3, 3]`.
- **Measure after shrinking, never before.** Measuring between the insert and the
  `while` scores an illegal window: `[1, 2, 1, 2, 3]` reports `5` where the
  answer is `4`.
- **Shrink one tree at a time, re-testing the condition.** Jumping `left`
  straight past the whole run of the evicted type would be a different (and
  fiddlier) algorithm; the one-step loop is what makes `left` land on the
  *smallest* legal position rather than merely a legal one.

### Why it's correct

**Invariant**: at the point where `current_length` is computed, `basket` holds
exactly the fruit types present in `fruits[left..right]` with their exact counts
and no zero entries, `len(basket) <= k`, and `left` is the **smallest** index for
which `fruits[left..right]` has at most `k` distinct types.

The first two clauses are maintained by construction: every entry into the window
increments a count (creating the key if needed) and every exit decrements one,
deleting at zero, so the map is a faithful multiset of the window and its size is
the distinct count.

The minimality clause is the one that makes the answer right, and it holds
because `left` only ever advances while the window is **illegal**, and stops the
instant it becomes legal. So at the moment of measurement the window is legal,
but the window one step wider on the left — `fruits[left-1..right]` — was illegal
when we passed it, if `left` moved at all this iteration. And illegality is
permanent in this direction: since the right edge only grows, a window that had
more than `k` types can never have fewer later. Hence no legal window ending at
`right` starts earlier than `left`, and `right - left + 1` is the longest one
ending at `right`.

**Why taking the best over right endpoints is exhaustive.** Every window has
exactly one right endpoint, and for each `right` the algorithm measures the
longest legal window ending there. The maximum over all right endpoints is
therefore the maximum over all legal windows — no case is missed and none is
double-counted.

**Termination and the edge of the range.** The outer `for` runs `n` times. The
inner `while` terminates because each pass increments `left`, and `left` is
bounded above by `right` — once the window shrinks to the single tree `right`,
`len(basket)` is `1`, which is `≤ k = 2`, so the loop must exit before `left` can
pass `right`. That bound is exactly what the key-deletion guarantees; without it
the argument collapses and so does the program. Across the whole run `left`
advances at most `n` times in total, which is why the nested loop is O(n) rather
than O(n²). At the range edges: the first iteration has a one-tree window that is
trivially legal, so the `while` body never runs and `best_total` becomes `1`; the
last iteration measures the window ending at `n-1`, so a window running to the
end of the array is not missed.

The step I would re-derive rather than trust, coming back to this cold, is the
minimality clause — specifically the claim that illegality is permanent as the
right edge grows. It is true because types are only ever *added* by moving
`right` forward, but it is the hinge that turns "a legal window" into "the
longest legal window", and it is what separates this from a heuristic.

## Solution

```python
# 904. Fruit Into Baskets (Medium) - longest window holding at most 2 distinct values, via a sliding window with a count map. O(n) time, O(1) space.
class Solution:
    def totalFruit(self, fruits: list[int]) -> int:

        # Two baskets, one fruit type each. The problem is "longest subarray
        # with at most k distinct values" with k pinned to 2; the general
        # version is left in as a named constant rather than a literal, which
        # is why the code reads like the k-distinct template.
        k = 2

        # Both halves of this guard are dead on LeetCode: k is literally 2, so
        # `k == 0` is never true, and the constraints promise
        # 1 <= fruits.length, so `not fruits` is never true either. It is the
        # generic template's guard, harmless, and kept as written.
        if k == 0 or not fruits:
            return 0

        # fruit type -> how many of it are inside the current window. Only
        # types actually present are keys, so len(basket) IS the number of
        # distinct types in the window. That equality is what the while loop
        # below tests, and it is maintained by the `del` further down.
        basket = {}

        best_total = 0
        left = 0

        # `right` is the inclusive right end of the window. It only ever moves
        # forward, and so does `left` - which is why the nested while does not
        # make this quadratic.
        for right, fruit in enumerate(fruits):

            # Admit the new tree first. The window is briefly INVALID here
            # (it may now hold 3 types); the while loop immediately repairs it
            # before anything is measured.
            if fruit not in basket:
                basket[fruit] = 0
            basket[fruit] += 1

            # Shrink from the left until at most k types remain. One tree at a
            # time, re-testing each round, so it stops at the very first
            # position that makes the window legal again - giving the LONGEST
            # valid window ending at `right`, not merely a valid one.
            while len(basket) > k:
                basket[fruits[left]] -= 1

                # Deleting the key at zero is what keeps len(basket) equal to
                # the distinct count. Decrementing without deleting leaves a
                # dead key behind, len(basket) never falls back to k, and the
                # loop keeps advancing `left` past the end of the array: on
                # [1, 2, 3, 3, 3] it walks off and raises IndexError rather
                # than returning a wrong answer.
                if basket[fruits[left]] == 0:
                    del basket[fruits[left]]
                left += 1

            # Measured only AFTER the repair, never before. Measuring between
            # the insert and the while loop scores an illegal 3-type window:
            # on [1, 2, 1, 2, 3] that reports 5 where the answer is 4.
            current_length = right - left + 1

            if best_total < current_length:
                # Style wart: the guard has already established that
                # current_length is the larger of the two, so max() here is
                # redundant - `best_total = current_length` does the same
                # thing. Harmless, and not mine to edit.
                best_total = max(best_total, current_length)

        return best_total
```

[solution.py](solution.py) · [raw submission](../../data/raw/fruit-into-baskets.py)

## Why this approach

| Alternative | Cost | Why the sliding window beats it |
|---|---|---|
| Brute force: every `(start, end)` pair, counting distinct types in each | O(n³) or O(n²) with an incremental set | At `n = 10⁵`, ~5 × 10⁹ windows is hopeless in Python. The waste is structural: the scan from `start + 1` re-walks everything the scan from `start` already established. |
| Pair adjacent runs: compress into runs of equal type, then take the best sum of two consecutive runs | O(n) time, O(n) space | **Wrong**, and worth burning in because it is the most seductive idea here. On `[1, 2, 3, 2, 2]` the runs are `1 \| 2 \| 3 \| 2,2` and the best adjacent pair totals `3`, but the answer is `4` — `[2, 3, 2, 2]` spans *three* runs while using only two types. Fixing it means merging non-adjacent runs of the same type, at which point you have reinvented the window, badly. |
| Track just the last two types and their most recent start positions, with no map | O(n) time, O(1) space | **Correct** and genuinely faster — the classic "two variables instead of a dict" version, which is where the 192 ms would go if you wanted it. It is much easier to get wrong (the bookkeeping for "where does the current run of the surviving type begin" is fiddly), and it is welded to `k = 2`, so it teaches nothing reusable. The map version generalises to "at most k distinct" by changing one constant. |
| Counter **array** of size `n` plus a distinct-count integer, instead of a dict | O(n) time, O(n) space | Correct, and the constraint `0 <= fruits[i] < fruits.length` is what licenses it. Trades a little memory for a meaningfully smaller constant factor in Python — the best easy speedup available here. It changes nothing about the algorithm, only its bookkeeping. |
| Binary search on the answer length, checking each candidate | O(n log n) time | Correct but pointless: the check for "is there a legal window of length L" is itself a linear scan, so you pay a log factor to avoid an insight you already have. Sliding windows are what you use when the answer is monotone *and* you can maintain it incrementally; here you can, so binary search is the strictly worse tool. |
| Decrement counts without deleting zero keys | — | **Wrong, and it crashes rather than mis-answers.** `len(basket)` stops tracking the distinct count, so the `while` cannot exit; `left` runs past the end of the array and `fruits[left]` raises `IndexError` on `[1, 2, 3, 3, 3]`. Listed because it is a one-line omission that reads as harmless. |

## Complexity

- **Time — O(n)**. The `for` advances `right` exactly `n` times; the inner
  `while` advances `left`, which also moves at most `n` times across the entire
  run because it never decreases. So the total work is at most `2n` window
  operations plus O(1) dictionary work each — amortised O(1) per tree, despite
  the nested loop. The 192 ms is Python's dictionary constant factor on 10⁵
  elements, not a complexity problem; the counter-array variant above is the fix
  if it ever mattered.
- **Space — O(1)**. `basket` holds at most `k + 1 = 3` entries — `k` legal types
  plus the one that momentarily broke the window before the `while` repairs it.
  That is a constant, independent of `n`, and it is the whole auxiliary cost.

## Pitfalls

- **Forgetting `del` when a count reaches zero.** The window never shrinks back
  to legal, `left` overruns the array, and `[1, 2, 3, 3, 3]` raises `IndexError`.
  Loud rather than silent, which is fortunate — but it is the error that follows
  most naturally from "just decrement the counter".
- **Measuring the window before shrinking it.** `[1, 2, 1, 2, 3]` returns `5`
  instead of `4`. The result is always too *large*, never too small, so it
  survives any test whose answer happens to be the whole array — including
  `[1, 1, 1]` and `[0, 1, 0, 1, 0]` above.
- **Pairing adjacent runs.** Returns `3` on `[1, 2, 3, 2, 2]` where the answer is
  `4`. See the table above; this is the wrong *idea*, not a slip, and it looks
  convincing until you construct the counterexample.
- **Requiring exactly two distinct types.** `[1, 1, 1]` answers `3`, not `0` or
  `2`. Both baskets do not have to be used.
- **Returning the number of types rather than the number of fruits.** The
  answer is a window *length*. `len(basket)` is never the answer; it is only the
  loop's test.
- **Putting `left += 1` inside the `if` that deletes the key.** Then `left` only
  advances when a type is fully evicted, so the window stops shrinking mid-run
  and the `while` spins forever on any window whose leftmost type has count
  greater than one. In the code above the increment is deliberately outside the
  `if`, at the bottom of the `while` body — that placement is easy to "tidy" back
  into a bug.
- **Assuming the answer is a run of one type plus a run of another.** It can
  interleave arbitrarily: `[0, 1, 0, 1, 0]` is a single legal window of length
  `5` with the types alternating five times.
- **Reading the `k == 0 or not fruits` guard as meaningful.** It is dead code
  under these constraints (`k` is the literal `2`; the array is non-empty). It is
  a leftover from the general k-distinct template. Don't spend review time on it,
  and don't conclude from it that empty input needs handling.

## Redo from scratch

1. Translate the story first: **longest contiguous subarray with at most 2
   distinct values.** The baskets are a costume.
2. Check the window is applicable: widening can only add types, so legality is
   monotone and `left` never has to move backwards.
3. Keep a count map so that `len(map)` is the distinct count — which requires
   **deleting keys at zero**, not just decrementing.
4. Per tree: add on the right, `while len(map) > 2` evict on the left one tree at
   a time, **then** measure.
5. Test `[1, 1, 1]` (one type only), `[1, 2, 3, 2, 2]` (the run-pairing
   counterexample), `[1, 2, 1, 2, 3]` (measure-after-shrink), `[5]` (single
   tree).

Be able to justify out loud: **why `left` never moves backwards** — that types
are only added as `right` advances, so a window that was already illegal can
never become legal again, which is what makes the two pointers a single pass
rather than a nested search. And second: **why `len(basket)` is the distinct
count** — that it holds only because zero-count keys are deleted, and that this
one line is simultaneously the correctness argument and the termination argument.
If you can state both, "at most k distinct" in any of its costumes is the same
machine with a different constant.

## Related problems

- [Longest Substring Without Repeating Characters](../0003-longest-substring-without-repeating-characters/README.md)
  — solved. The same window with the rule "at most 1 of each" instead of "at most
  2 distinct". Read them side by side: the skeleton is identical and only the
  shrink condition changes, which is the clearest way to see that the window is a
  template rather than a trick.
- [Fruits Into Baskets II](https://leetcode.com/problems/fruits-into-baskets-ii/)
  — not solved yet. A near-namesake that is **not** this problem: it is a
  different assignment question about capacities, and its shared title makes it a
  useful reminder to read the statement rather than the name.
- [Longest Nice Subarray](https://leetcode.com/problems/longest-nice-subarray/) —
  not solved yet. Same sliding-window skeleton with a bitwise legality condition
  (the AND of the window must stay zero), and the monotonicity argument is the
  same shape. Good for testing whether you internalised *why* the window works or
  only *when*.
- [Longest Substring with At Most K Distinct Characters](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/)
  — not solved yet, and the direct generalisation. This solution already solves
  it: delete the `k = 2` line and take `k` as a parameter. Worth doing once, to
  confirm the `k` in the code is genuinely a parameter and not a coincidence.
- [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)
  — not solved yet. The hard end of the family and the instructive inversion:
  there the window shrinks while it is *valid* (chasing the smallest) instead of
  while it is *invalid* (chasing the largest). Doing it after this one makes the
  shrink-condition choice conscious rather than copied.
- [Contains Duplicate II](../0219-contains-duplicate-ii/README.md) — solved. A
  fixed-width window rather than a variable one, which is worth a glance for the
  contrast: when the width is given, no shrink loop is needed at all.
