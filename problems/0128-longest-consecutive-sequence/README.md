# 128. Longest Consecutive Sequence

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Hash Table, Union-Find |
| **Solved** | 2026-09-14 |
| **Runtime** | 48 ms (62.66th percentile) |
| **Memory** | 36.6 MB (66.93th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/longest-consecutive-sequence/ |

## The problem

**Given** an unsorted integer array `nums`.

**Return** the length of the longest run of **consecutive integers** that can
be assembled from its values — that is, the largest `L` for which some value
`v` has `v, v+1, v+2, ..., v+L-1` all present in `nums`.

Two things this is *not*. The run does **not** have to be contiguous in the
array, or in any particular order there — position is irrelevant, only
membership matters. And you return the **length**, not the sequence itself.

**Guaranteed**: nothing helpful. The array may be empty, may contain
duplicates, and spans the full range of 32-bit-ish integers. The real
difficulty is a requirement that lives in the problem's famous follow-up
rather than in its constraints: solve it in **O(n)**, which forbids sorting.

```text
def longestConsecutive(self, nums: List[int]) -> int
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[8, 3, 9, 7]` | `3` | The run `7, 8, 9` — scattered across the array, and `3` is isolated. Shows that array order is irrelevant. |
| `[]` | `0` | **Edge case:** empty input. Handled by the explicit guard; without it the function would still return `0` via the untouched `longest_streak`, so the guard is defensive rather than necessary. |
| `[5, 5, 5]` | `1` | **Edge case: duplicates.** The answer is `1`, not `3` — three copies of `5` do not make a run of three. The `set()` is what collapses them; on a list-based version this is the input that returns the wrong answer. |
| `[100, 4, 200, 1, 3, 2]` | `4` | The run `1, 2, 3, 4`, with two decoys far away. Also shows the answer can sit entirely in the array's *middle* positions. |
| `[1, 2, 3, 10, 11, 12, 13]` | `4` | **Counterexample to stopping at the first run found.** The scan order over a set is arbitrary, so `1` may well be visited before `10`; a version that returned as soon as it completed a run would answer `3`. The `max()` is what makes the traversal order not matter. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `0 <= nums.length <= 10^5` | **The lower bound is `0` — the array can genuinely be empty**, which is unusual for LeetCode and is why the `if not nums` guard earns its place here (contrast the dead guard in [Remove Duplicates](../0026-remove-duplicates-from-sorted-array/README.md), where `n >= 1`). The upper bound of 100,000 is what makes the O(n²) trap fatal: a naive "walk outward from every element" is up to 10¹⁰ steps. It also makes an O(n log n) sort *pass* comfortably — sorting is the answer that works and is still considered wrong, because the intended follow-up demands linear time. |
| `-10^9 <= nums[i] <= 10^9` | Two billion possible values, which **rules out a boolean presence array** indexed by value — you cannot allocate 2 × 10⁹ slots. A hash set works because its size is bounded by the number of distinct elements (≤ 10⁵), not by the value range. The magnitude also means `current_num + 1` can reach 10⁹ + 1, which is fine in Python's arbitrary-precision integers but would be worth an overflow thought in a fixed-width language. Negative values are ordinary members; nothing here assumes positivity. |

## Key insight

A run should be counted **once, from its smallest element**. The test for
"am I the smallest?" is one hash lookup: `num - 1` is not in the set. Every
other member of a run fails that test immediately and costs nothing. Without
this filter you would walk the same run once per member — with it, the total
work across all runs is bounded by the total number of elements.

That single `if` is the difference between O(n) and O(n²). Everything else in
the solution is bookkeeping.

## Approach

1. Return `0` on empty input.
2. Build `num_set = set(nums)`. This does two jobs at once: it gives O(1)
   membership tests, and it **deduplicates**, which is what makes repeated
   values count once.
3. Iterate over **`num_set`, not `nums`** — see below.
4. For each value, check whether `num - 1` is absent from the set. If it is
   present, this value is in the middle of some run; skip it entirely.
5. If `num - 1` is absent, `num` starts a run. Walk upward with a `while`,
   incrementing `current_num` and `current_streak` for as long as
   `current_num + 1` is in the set.
6. Fold the finished run's length into `longest_streak` with `max()`.
7. Return `longest_streak`.

Two ordering details are load-bearing. **Step 4 must come before step 5** —
that is the whole optimization. And **step 3's choice of `num_set` over
`nums`** matters for the same reason at a different scale: iterating the
original list would re-examine every duplicate, so an input of 100,000
identical values would do 100,000 start-checks instead of one. The membership
filter would still keep each of those checks O(1), so it remains linear either
way, but it is gratuitous work the set has already paid to eliminate.

### Why it's correct

**Invariant** for the outer loop: after processing any subset of the values,
`longest_streak` equals the length of the longest consecutive run whose
**smallest element** has already been visited. It starts true vacuously
(`longest_streak = 0`, nothing visited). Each iteration either skips a value
that is not a run-minimum — which cannot change the quantity, since the
invariant only concerns run-minimums — or fully measures the run beginning at
a run-minimum and folds it in with `max`.

At the end, every value has been visited, so in particular every run's minimum
has been visited, so `longest_streak` is the length of the longest run overall.
That is the answer. Note how this argument makes the traversal order of the
set irrelevant, which matters because set iteration order is not something to
rely on.

**Why the inner `while` measures the run correctly**: it starts at a value with
no predecessor in the set and advances only while the successor is present, so
it stops exactly at the largest element of that run. `current_streak` counts
elements, starting at `1` for the start value itself — not at `0`, which is the
off-by-one to watch. Because it began at the minimum, it traverses the whole
run and not a suffix of it.

**Why two nested loops are still O(n)** — this is the part worth being able to
reconstruct. The inner loop's iterations are not bounded per outer iteration;
they are bounded **in aggregate**. Each inner step moves from one element of a
run to the next element of the *same* run, and the outer guard ensures each run
is entered exactly once (only from its minimum). Since runs are disjoint — an
element belongs to exactly one maximal run — the total number of inner steps
across the entire execution is at most the number of distinct elements. So the
cost is O(n) hash lookups overall, not O(n) per outer iteration. This is an
amortization argument, and it is the only reason the solution is fast.

**Termination and the edge of the range**: the outer `for` is over a finite set.
The inner `while` terminates because `current_num` strictly increases each step
and the set is finite, so `current_num + 1` must eventually be absent — and the
condition is `in`, not `<=` some bound, so there is no comparison boundary to
get backwards. The empty-array case never reaches either loop. Notice that the
`max()` sits *outside* the `while` but *inside* the `if`: putting it inside the
`while` would also be correct but would do redundant work; putting it outside
the `if` would fold in stale values from skipped elements.

The step I would flag as least obvious on a cold re-read, and worth
re-deriving rather than recalling: the amortization. "Two nested loops" looks
quadratic, and the reason it is not depends entirely on the outer guard, which
is four tokens long and easy to dismiss as an optimization rather than the
algorithm.

## Solution

```python
# 128. Longest Consecutive Sequence (Medium) - hash set, walk each run only from its smallest element. O(n) time, O(n) space.
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        
        # nums.length may be 0, and max() over no streaks would never run,
        # leaving longest_streak at 0 anyway - but the guard also protects
        # against nothing else here, so it is really just an early exit.
        if not nums:
            return 0

        longest_streak = 0

        # The set does two jobs: O(1) membership tests, and deduplication.
        # Deduplication is what makes the outer loop touch each DISTINCT value
        # once rather than once per copy.
        num_set = set(nums)

        # ORDER MATTERS: iterate over num_set, not nums. Iterating the raw
        # list would redo the same walk once per duplicate copy of a run's
        # start value.
        for num in num_set:

            # This is the whole algorithm. Only start counting from a value
            # that has no left neighbour - i.e. the SMALLEST element of its
            # run. Every other member of the run fails this test and costs
            # O(1). Without it, a run of length L would be walked from all L
            # of its members, making the whole thing O(n^2) on input like
            # [1..100000].
            if (num - 1) not in num_set:

                current_num = num
                current_streak = 1

                # Walk right until the run breaks. Each iteration consumes one
                # element of THIS run, and runs are disjoint, so across the
                # entire outer loop this inner loop runs at most n times in
                # total - that is why two nested loops still add up to O(n).
                while (current_num + 1) in num_set:

                    current_num += 1
                    current_streak += 1
                
                # Only reached at the end of a complete run, so current_streak
                # is that run's full length.
                longest_streak = max(longest_streak, current_streak)    
        
        return longest_streak
```

[solution.py](solution.py) · [raw submission](../../data/raw/longest-consecutive-sequence.py)

## Why this approach

| Alternative | Cost | Why the set-with-start-check beats it |
|---|---|---|
| Sort, then scan counting runs (skipping equal neighbours) | O(n log n) time, O(1)–O(n) space | **Correct, simpler, and about as fast in practice** at `n = 10⁵` — Python's Timsort is brutally efficient and this solution's hash lookups are not free (48 ms here is not a dominant win). It loses only on the follow-up's explicit terms: the problem asks for O(n), and sorting is the thing that requirement exists to forbid. Worth being honest that this is a theoretical win, not an empirical one at this input size. |
| For each element, walk outward without the `num - 1` guard | **O(n²)** time | The same code with four tokens deleted. On `[1, 2, ..., 100000]` every element starts a full walk: 10⁵ walks averaging 5 × 10⁴ steps ≈ 5 × 10⁹ operations. This is the trap the problem is built around, and it is the single most instructive thing here — the guard is not a micro-optimization, it is the algorithm. |
| Union-Find: union each value with `value + 1` when present, then take the largest component | O(n α(n)) ≈ O(n) time, O(n) space | Genuinely linear and a legitimate answer (it is in the topic tags). But it needs a disjoint-set structure with path compression plus a value→index map, which is far more code and more memory for the same bound. Reach for it when the problem also needs incremental updates; here it is over-engineering. |
| A boolean presence array indexed by value, then scan for the longest true-run | O(range) time and space | Would be beautifully simple — and is impossible: the range is 2 × 10⁹. This is exactly the constraint that forces a hash set instead of an array, and it is worth naming, because on a problem with `0 <= nums[i] <= 1000` this *would* be the best answer. |
| `set` plus checking `num + 1` (walking left instead of right) | O(n) time | Symmetric and equally correct, provided the guard flips to `num + 1 not in num_set` — i.e. start only from each run's **maximum**. Mixing the two up (guarding on `num - 1` but walking down) yields `1` for every run, which is the kind of bug that passes the single-element test case. |

## Complexity

- **Time — O(n)**. Building the set is O(n) expected. The outer loop runs once
  per distinct value, and each iteration does one hash lookup for the guard.
  The inner loops sum to at most one step per distinct value *in total*, by the
  disjointness argument above. So the whole thing is a constant number of
  expected-O(1) hash operations per element. Worst case degrades to O(n²) only
  under adversarial hash collisions, which is not a practical concern for
  Python's integer hashing here.
- **Space — O(n)**. The set holds every distinct value — up to 100,000
  entries, which at roughly 32 bytes of overhead apiece explains the 36.6 MB
  reading. Everything else is three scalars.

## Pitfalls

- **Dropping the `if (num - 1) not in num_set` guard.** The code still returns
  the *right answer*, just in O(n²) — so it passes every small test and times
  out only on the large hidden cases. A wrong answer announces itself; this
  does not.
- **Iterating `nums` instead of `num_set` while keeping everything else.**
  Still correct and still linear (the guard holds the line), but it does
  redundant work proportional to the duplicate count. The genuinely *wrong*
  version is dropping the `set()` entirely and testing membership against the
  list — `in` on a list is O(n), which makes the whole thing O(n²) or worse
  while looking identical.
- **Initializing `current_streak = 0` instead of `1`.** Returns one less than
  the true answer for every input. On `[1, 2, 3]` it gives `2`. The start value
  is itself a member of the run and must be counted before any walking.
- **Returning `current_streak` instead of `longest_streak`.** Returns the
  length of whichever run happened to be visited last — and since set
  iteration order is arbitrary, the failure is non-deterministic across runs
  and across Python versions. On `[1, 2, 3, 10, 11, 12, 13]` it might return
  `3` or `4` depending on nothing you control.
- **Forgetting that duplicates do not extend a run.** `[5, 5, 5]` is `1`, not
  `3`. The `set()` handles it silently, which means a hand-rolled version that
  skips the set will get this wrong without any obvious symptom.
- **Putting the `max()` in the wrong place.** Inside the `while` it is correct
  but wasteful; outside the `if` it folds in `current_streak` values left over
  from a previous iteration, which is a stale-variable bug rather than an
  algorithmic one — and it produces answers that are too *large*, which is
  harder to spot than answers that are too small.

## Redo from scratch

1. State the trap before writing code: the obvious solution is O(n²), and
   sorting is banned by the follow-up. The target is O(n).
2. `num_set = set(nums)` — say both of its jobs out loud, membership **and**
   deduplication.
3. The guard, which is the whole idea: **only start a walk from a value whose
   predecessor is absent**, because that value is the minimum of its run.
4. Inner `while (current_num + 1) in num_set`, counting from `1`.
5. `longest_streak = max(longest_streak, current_streak)` after the walk
   completes — inside the `if`, outside the `while`.
6. Check `[5, 5, 5]` → `1` (duplicates) and `[1, 2, 3, 10, 11, 12, 13]` → `4`
   (the `max` doing real work). Then check the empty array.

Be able to justify out loud: **why two nested loops are O(n) and not O(n²)** —
the disjointness/amortization argument, that each inner step consumes one
element of one run and each run is entered exactly once. If you cannot
reconstruct that, you have memorized the code rather than the algorithm, and
it will not survive a variant.

## Related problems

- [Two Sum](../0001-two-sum/README.md) — already solved. The foundational
  "trade O(n) memory for O(1) lookup" move. This problem is the same trade
  applied to *presence* rather than to complements.
- [Group Anagrams](../0049-group-anagrams/README.md) — already solved. Hashing
  as a way to make scattered items findable — same instinct, different key.
- [Design HashSet](../0705-design-hashset/README.md) — already solved. The
  data structure this solution's entire complexity argument rests on. Worth
  re-reading together: knowing *why* membership is O(1) is what licenses the
  claim that the outer guard is free.
- [Binary Tree Longest Consecutive Sequence](https://leetcode.com/problems/binary-tree-longest-consecutive-sequence/)
  — not solved yet. The same "longest consecutive run" question where adjacency
  is defined by tree edges rather than set membership, so it becomes a DFS
  carrying a running streak. Good test of whether the *idea* transferred or
  just the code.
- [Maximum Consecutive Floors Without Special Floors](https://leetcode.com/problems/maximum-consecutive-floors-without-special-floors/)
  — not solved yet. The inverse: longest run of values *missing* from the set.
  Sorting is genuinely the right answer there, which is a useful corrective to
  over-applying this problem's reflex.
- [Find the Maximum Number of Elements in Subset](https://leetcode.com/problems/find-the-maximum-number-of-elements-in-subset/)
  — not solved yet. Same count-and-walk-from-an-anchor shape over a frequency
  map, but the runs are geometric rather than consecutive.
