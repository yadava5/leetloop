# 219. Contains Duplicate II

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table, Sliding Window |
| **Solved** | 2026-09-16 |
| **Runtime** | 41 ms (80.20th percentile) |
| **Memory** | 39.3 MB (26.51th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/contains-duplicate-ii/ |

## The problem

**Given** an integer array `nums` and an integer `k`.

**Return** `True` if there exist two **distinct** indices `i` and `j` such that
`nums[i] == nums[j]` and `abs(i - j) <= k`; `False` otherwise. A boolean only —
you are not asked which pair, or how many.

Two readings to get right. `i` and `j` must be **different indices**, so an
element is never its own duplicate; this is what makes `k = 0` always answer
`False`. And the bound is on the **distance between positions**, not on the
values — the values must be exactly equal, and how large they are is irrelevant.

**Guaranteed**: `nums` is non-empty and `k` is non-negative. Neither promise is
leaned on hard: a single-element array simply finds no pair, and a negative `k`
would still behave sensibly because the stored distance is always `>= 1`.

```text
def containsNearbyDuplicate(self, nums: list[int], k: int) -> bool
```

### Examples (mine, not LeetCode's)

| `nums` | `k` | Returns | Why |
|---|---|---|---|
| `[1, 2, 3, 1]` | `3` | `True` | The pair of `1`s is exactly `3` apart, so `<=` rather than `<` is what makes this pass. The boundary case for the comparison operator. |
| `[1, 2, 3, 1]` | `2` | `False` | Same array, one smaller `k`. **Counterexample to ignoring `k` and just looking for duplicates** — a plain "does this array contain a duplicate" check returns `True` here and is wrong. |
| `[1, 0, 1, 1]` | `1` | `True` | The `1`s at indices 0 and 2 are too far apart, but the ones at 2 and 3 are not. Only returns `True` because index 2 **overwrote** index 0 in the map. The example that justifies keeping the latest index rather than the first. |
| `[1, 2, 1]` | `0` | `False` | **Edge case:** `k = 0`. Distinct indices are always at least `1` apart, so no `k = 0` input can ever be `True`. Worth confirming rather than special-casing. |
| `[1, 2, 3, 1, 2, 3]` | `2` | `False` | Every value repeats, and every repeat is exactly `3` apart. Kills any solution that answers "are there duplicates at all". |
| `[99]` | `5` | `False` | **Edge case:** one element, generous `k`. There is no second index, so the loop finds nothing and the fall-through `return False` is what answers. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 10^5` | The upper bound is what rules out the direct reading of the problem. Checking each `i` against the next `k` positions is **O(n · k), and with both at 10⁵ that is 10¹⁰ comparisons — TLE by a wide margin**, even though it looks linear-ish when `k` is small. So the solution must be O(n) (or `n log n`) independent of `k`, which is what forces a hash map keyed on the *value*. The lower bound of `1` means `nums` is never empty, so no guard is needed — though the code would return `False` correctly if it were. |
| `-10^9 <= nums[i] <= 10^9` | The values span 2 × 10⁹ possibilities and go **negative**, which rules out the other tempting trick: you cannot use the value as a direct index into an array of counters (that would be a 2 × 10⁹-slot table, ~16 GB), and you cannot offset-and-bucket it cheaply either. Hashing is the only practical keying. The magnitude is otherwise irrelevant — nothing here does arithmetic on the values, only equality, so there is no overflow question. |
| `0 <= k <= 10^5` | `k` may be **`0`**, and the answer must then always be `False`; the code gets this from `i - seen[num] >= 1 > 0` without a special case. `k` may also **exceed the array length**, in which case the distance test is vacuously true and the problem degenerates into plain *Contains Duplicate*. Both extremes have to work without branching, and they do, which is a small argument for the map-of-indices formulation over an explicit window of size `k` that would need clamping. |

## Key insight

Sweep once, and at each index ask only: *have I seen this exact value recently
enough?* The answer needs just one number per value — the **most recent** index
at which it occurred — because for a fixed right-hand index `j`, the closest
possible partner is by definition the latest earlier occurrence. Every older
occurrence is strictly further away and can never rescue a pair the latest one
fails. So the map holds one index per value, not a list, and it is overwritten
unconditionally.

## Approach

1. Create an empty dict `seen`, mapping value → last index seen.
2. Walk the array with `enumerate`, so both the index `i` and the value `num`
   are in hand.
3. If `num` is already in `seen`, test `i - seen[num] <= k` and return `True`
   immediately if it holds.
4. **Whether or not the test passed**, set `seen[num] = i`.
5. If the loop completes, return `False`.

Two orderings are load-bearing. **The lookup must precede the write** — if
`seen[num] = i` ran first, every element would find itself at distance `0` and
the function would return `True` for any non-empty input with `k >= 0`. And
**step 4 must not be in an `else`**: a failed distance test is not a verdict on
the value, only on that one pair, and the current index must still be recorded
so that a *later* occurrence can be measured against it. `[1, 0, 1, 1]` with
`k = 1` is the input that proves it — moving the write into an `else` makes the
final `1` compare against index 0, distance 3, and the answer flips to `False`.

### Why it's correct

**Invariant**: before processing index `i`, `seen` maps every value in
`nums[0..i-1]` to the largest index `< i` at which it occurs, and no qualifying
pair exists within `nums[0..i-1]`. The second half is justified by the early
`return True` — if one had existed, the function would already have returned.

The body maintains both. The unconditional write restores the first half. For
the second: any qualifying pair whose right end is `i` has a left end
`b < i` with `nums[b] == nums[i]` and `i - b <= k`. Among all such `b`, the
largest is `seen[nums[i]]`, and `i - seen[nums[i]]` is therefore the *smallest*
distance available — so if any `b` satisfies the bound, the stored one does, and
the test catches it. Conversely the test never fires falsely, because
`seen[nums[i]]` is a real earlier index holding an equal value. This is exactly
why discarding older indices is lossless rather than merely convenient.

**Termination and the edges.** The loop is a bounded `for` over `n` elements
with an early exit; it always ends. `i - seen[num]` is always `>= 1` because
`seen[num]` was written on a strictly earlier iteration — that is the whole
mechanism behind `k = 0` returning `False`, and it is also why `<=` is right
and `<` would be wrong (it would reject the exactly-`k` pair that
`[1, 2, 3, 1]` with `k = 3` depends on). The first iteration finds an empty
map and does nothing but write. The last iteration, at `i = n - 1`, performs a
test whose write is then never read; harmless.

## Solution

```python
# 219. Contains Duplicate II (Easy) - hash map from value to its MOST RECENT index; a repeat within k of that index answers yes. O(n) time, O(n) space.
class Solution:
    def containsNearbyDuplicate(self, nums: list[int], k: int) -> bool:

        # value -> the last index at which that value was seen. Only the last
        # one is kept, and that is sufficient, not a shortcut: for a fixed j,
        # the nearest earlier twin is the one that minimises j - i, so if any
        # earlier occurrence satisfies the distance test, the most recent one
        # does too. Storing a list of all past indices would cost more memory
        # and answer exactly the same question.
        seen = {}

        for i, num in enumerate(nums):

            if num in seen:
                # seen[num] is strictly less than i, so the difference is
                # always positive - which is exactly why k = 0 can never
                # return True, matching the problem's requirement that the
                # two indices be distinct.
                if i - seen[num] <= k:
                    return True
            # NOT an else. A failed distance test must fall through to the
            # update, because a later occurrence may still be close enough to
            # THIS one even though it was too far from the older one.
            # Example: nums = [1, 0, 0, 0, 1], k = 1. At i = 4 the pair of 1s
            # is 4 apart and fails, but the pair of 0s at i = 2 already
            # returned True - and had the array been [1, 2, 1, 1] with k = 1,
            # the i = 2 test fails while i = 3 succeeds only because i = 2
            # overwrote the stored index.
            #
            # The ORDER here is load-bearing: the lookup must happen before
            # the write. Writing first would make `seen[num] == i` and every
            # element would report a distance of 0 <= k.
            seen[num] = i

        # No qualifying pair anywhere in the array.
        return False
```

[solution.py](solution.py) · [raw submission](../../data/raw/contains-duplicate-ii.py)

## Why this approach

| Alternative | Cost | Why the index map beats it |
|---|---|---|
| Brute force: for each `i`, scan `j` in `(i, min(i+k, n))` | O(n · k) time, O(1) space | Direct transcription of the problem statement, and the **memory-cheapest** option — but at `n = k = 10⁵` it is 10¹⁰ comparisons. TLE. Worth knowing as the answer when `k` is guaranteed tiny; here it is not. |
| Plain *Contains Duplicate*: build a set, answer "any repeat at all" | O(n) time and **wrong** | Drops `k` entirely. Returns `True` on `[1, 2, 3, 1]` with `k = 2`, where the answer is `False`. Verified. The instructive failure: it answers a strictly easier question and gets the easy inputs right. |
| Keep a **list** of every index per value, scan it on each hit | O(n) space, but O(n²) time in the worst case | Correct, and the version people write first. On `[7] * 10⁵` each new `7` rescans a list of up to 10⁵ prior indices — 5 × 10⁹ operations. The whole point of storing one index is that the rest are provably useless. |
| Sort `(value, index)` pairs, compare adjacent entries with equal values | O(n log n) time, O(n) space | Correct, and it needs no hashing, which makes it the fallback in a language without a good map. Strictly slower, and the adjacent-pair reasoning (you must compare *all* adjacent equal-value entries, not just the first) is easier to get subtly wrong than the one-line map test. |
| Sliding window of exactly `k` elements held in a **set**, evicting `nums[i-k-1]` as `i` advances | O(n) time, **O(min(n, k)) space** | The one alternative that genuinely beats this solution, and on the axis where this submission is weakest — the 26.51th percentile memory. The map here grows to one entry per *distinct value* in the whole array; the window set holds at most `k + 1`. When `k` is small and `n` is large, that is a large saving. It costs an eviction line and an `i > k` guard, and it answers a slightly different question internally ("is the value present in the window") rather than ("how far back was it"). |

## Complexity

- **Time — O(n)**. One pass, with a dict lookup, a comparison and a dict write
  per element, each O(1) on average. There is no inner loop, so the bound does
  not depend on `k` at all — which is exactly what the `n · k = 10¹⁰` brute force
  is paying for.
- **Space — O(n)** in the worst case: one dict entry per *distinct* value. On an
  all-distinct array that is `n` entries, which is where the 39.3 MB and the
  unremarkable memory percentile come from. Note this is O(n) and **not**
  O(min(n, k)) — a `k`-sized sliding window would do better when `k` is small.

## Pitfalls

- **Ignoring `k` and answering "does a duplicate exist".** Returns `True` on
  `[1, 2, 3, 1]` with `k = 2`; the answer is `False`.
- **Putting `seen[num] = i` in an `else`.** Breaks `[1, 0, 1, 1]` with `k = 1`:
  the final `1` at index 3 is then compared against index 0, distance 3, and the
  answer comes back `False` instead of `True`. The first occurrence is not the
  useful one; the latest is.
- **Writing to the map before testing.** `seen[num] = i` then `i - seen[num]`
  gives `0 <= k` for every element, so the function returns `True` on any
  non-empty input. Catastrophic and completely silent on the sample tests, which
  mostly expect `True`.
- **`return False` inside the loop when the distance test fails.** Tempting
  symmetry with the `return True`, and wrong for the same reason as the `else`
  above: one failed pair is a verdict on that pair, not on the array. On
  `[1, 9, 1, 1]` with `k = 1` it bails out at index 2 (distance `2 > 1`) and
  returns `False`, never reaching the genuine pair at indices 2 and 3. The true
  answer is `True`.
- **Using `<` instead of `<=`.** Off by one at exactly the boundary: rejects
  `[1, 2, 3, 1]` with `k = 3`, which should be `True`. The statement says
  `abs(i - j) <= k`.
- **Computing `abs(i - seen[num])`.** Not wrong, just noise — `seen[num] < i`
  always, so the difference is already positive. Harmless here, but reaching for
  `abs` usually signals that you have not noticed the map only ever holds
  *earlier* indices, and that observation is what the correctness argument rests
  on.
- **Special-casing `k = 0`.** Unnecessary; the `>= 1` distance handles it. Adding
  the branch is not a bug, but it suggests the invariant is not clear, and the
  same misunderstanding produces a real bug in the `k > n` direction, where
  people sometimes clamp `k` and get the window boundaries wrong.

## Redo from scratch

1. Name the question you are answering at each index: **"was this exact value
   seen within the last `k` positions?"** Everything follows from that phrasing.
2. Reach for a dict of value → **last** index. Be able to say why the last one
   and not the first, and why a list of all of them is wasted work.
3. Test before writing; write unconditionally, outside any `else`.
4. `i - seen[num] <= k`, with `<=`.
5. `return False` after the loop, never inside it.
6. Test `[1, 2, 3, 1]` at `k = 3` and `k = 2` (the boundary), `[1, 0, 1, 1]` at
   `k = 1` (why the overwrite matters), and any array at `k = 0`.

Be able to justify out loud: **why keeping only the most recent index loses no
answers.** The exchange argument — for a fixed right end, the nearest left end
is the latest one, so if any partner qualifies the stored one does — is the
entire proof, and it is what separates this from the O(n²) list-of-indices
version. Second: **where the `k = 0` case is handled**, and why there is no
branch for it.

## Related problems

- [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) — not
  solved yet, and the strictly easier parent: drop `k` and a plain set answers
  it. Doing it right after this one is a good way to see exactly which line the
  index bookkeeping buys you.
- [Contains Duplicate III](https://leetcode.com/problems/contains-duplicate-iii/)
  — not solved yet, and a much harder child. The values need only be *within* a
  tolerance rather than equal, which destroys hashing (you cannot hash an
  approximate match) and forces bucketing by value range or an ordered structure
  over the sliding window. The best illustration of how much this problem was
  getting from exact equality.
- [Longest Substring Without Repeating Characters](../0003-longest-substring-without-repeating-characters/README.md)
  — already solved, and the same data structure used for the opposite purpose:
  there the map of value → last index is consulted to *move a window's left
  edge*, here only to measure a distance. Worth reading side by side; they make
  "dict of last-seen index" feel like one tool rather than two tricks.
- [Longest Nice Subarray](https://leetcode.com/problems/longest-nice-subarray/)
  — not solved yet. A genuine sliding window with an incrementally maintained
  invariant, which is the direction the "window of size `k` as a set" alternative
  above points in.
- [Minimum Consecutive Cards to Pick Up](https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up/)
  — not solved yet, and almost the same code: instead of testing the gap between
  equal values against `k`, you minimise it. If you can write this solution you
  can write that one by changing the comparison into a `min`.
