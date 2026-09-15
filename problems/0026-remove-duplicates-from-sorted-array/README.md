# 26. Remove Duplicates from Sorted Array

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Two Pointers |
| **Solved** | 2026-09-14 |
| **Runtime** | 0 ms (100th percentile) |
| **Memory** | 20.5 MB (79.35th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/remove-duplicates-from-sorted-array/ |

## The problem

**Given** an integer array `nums` already sorted in non-decreasing order.

**Return** an integer `k` — the number of distinct values in `nums` — and, as
a side effect, rearrange `nums` **in place** so that its first `k` slots hold
those distinct values in their original (ascending) order. Whatever sits at
index `k` and beyond does not matter; the grader reads only `nums[0:k]`.

So this is a problem with two outputs: the returned count, and the mutated
prefix. Returning the right number while leaving the array untouched fails,
and so does compacting the array correctly but returning the wrong count.

**Guaranteed**: the array is **sorted**. This is the entire basis of the
approach — it means every group of equal values is contiguous, so a duplicate
can only ever appear immediately after the value it duplicates. On unsorted
input this solution is simply wrong.

```text
def removeDuplicates(self, nums: List[int]) -> int
```

### Examples (mine, not LeetCode's)

| `nums` (before) | Returns | `nums[0:k]` after | Why |
|---|---|---|---|
| `[4, 4, 9]` | `2` | `[4, 9]` | The ordinary case: one duplicated value, one unique. |
| `[7]` | `1` | `[7]` | **Edge case:** a single element. The `for` loop over `range(1, 1)` never executes, and `write` stays at its initial `1` — the answer falls straight out of the initialization. |
| `[5, 5, 5, 5]` | `1` | `[5]` | All identical. No copy ever happens; `write` never leaves `1`. Checks that the "keep the first one for free" initialization is right. |
| `[-3, -3, 0, 0, 0, 8]` | `3` | `[-3, 0, 8]` | Runs of length > 2. **Counterexample to comparing `nums[read]` against `nums[read - 1]`... which actually still works here** — see the next row for where the naive variant genuinely differs. |
| `[1, 2, 2, 3]` | `3` | `[1, 2, 3]` | **The instructive one.** At `read = 3` (value `3`), `write` is `2`, so the code compares `nums[3] != nums[1]`, i.e. `3 != 2`. A version that compared against `nums[read - 1]` would compare `3 != 2` too and agree here — the two rules coincide on *sorted* input, which is exactly why it is easy to write either one and never notice. They diverge the moment the input is not sorted, which is why "sorted" belongs in the Guaranteed list rather than being treated as decoration. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 3 * 10^4` | The lower bound of `1` means the array is **never empty**, which makes the `if not nums: return 0` guard in the code dead — and makes the `write = 1` initialization safe, since there is always at least one element to keep. The upper bound of 30,000 is tiny: even an O(n²) approach would be roughly 9 × 10⁸ operations and too slow in Python, but anything O(n log n) or better passes comfortably, so the size alone does not force the linear two-pointer scan — the in-place, O(1)-extra-space requirement does. |
| `-100 <= nums[i] <= 100` | A startlingly narrow value range: **at most 201 distinct values can ever exist**, so `k <= 201` no matter how long the array is. This rules the problem *open* to a counting-array approach (a 201-slot bucket table indexed by `nums[i] + 100`) that would be impossible with unbounded values. It is worth noticing precisely because the two-pointer solution does **not** need it — the scan works for any value range, and leaning on this bound would produce a solution that silently breaks on the otherwise-identical follow-up problems. |

## Key insight

Because the array is sorted, duplicates are adjacent — so you never need to
remember *all* the values seen before, only **the last one you decided to
keep**. That collapses the problem from "deduplicate a collection" (which
sounds like it wants a set) to "compare each element against one previous
value," which needs no extra memory at all.

## Approach

1. If the array is empty, return `0`. (Dead under the stated constraints, but
   it is what stops `write = 1` from claiming a one-element prefix that does
   not exist.)
2. Set `write = 1`. Index `0` is settled before the loop starts: the first
   element of a sorted array is always the first element of the answer, since
   there is nothing before it that it could duplicate. `write` now points at
   the next free slot in the answer prefix.
3. Scan `read` from `1` to the end.
4. Compare `nums[read]` against `nums[write - 1]` — the **last value kept**,
   not the previous value seen. If they differ, `nums[read]` starts a new run:
   copy it to `nums[write]` and advance `write`. If they match, do nothing and
   let `read` move on.
5. Return `write`, which is simultaneously "the next free index" and "how many
   distinct values were written."

The load-bearing detail is step 4's choice of `nums[write - 1]` as the
comparison target. It is the only expression in the function that refers to
the answer being built rather than to the input being read.

### Why it's correct

**Invariant**, true before and after every iteration: `nums[0:write]` contains
exactly the distinct values of `nums[0:read]`, in ascending order, and
`nums[write - 1]` is the largest value kept so far. It holds trivially before
the loop (`nums[0:1]` is the distinct values of `nums[0:1]`). Each iteration
preserves it: if `nums[read] != nums[write - 1]` then — because the input is
sorted and `nums[write - 1]` is the maximum kept — `nums[read]` must be
strictly *greater* than every kept value, so it is genuinely new and appending
it keeps the prefix distinct and ascending. If instead they are equal,
`nums[read]` is a duplicate of something already kept and skipping it leaves
the invariant untouched.

**The in-place write is safe** because `write <= read` always: both start at
`1`, and `write` only advances on iterations where `read` also advances. So
`nums[write] = nums[read]` never overwrites an element the scan has not yet
read. When `write == read` the copy is a harmless self-assignment.

**Termination and the edge of the range**: `range(1, len(nums))` is a finite
sequence, so the loop ends after exactly `n - 1` iterations. The range starts
at `1` rather than `0` because index `0` was pre-settled; starting at `0`
would compare `nums[0]` against `nums[write - 1] == nums[0]`, find them equal,
skip — harmless by luck, but it would make the initialization and the loop
tell contradictory stories about who owns index `0`. The range ends at
`len(nums)` exclusive, so the last element examined is `nums[n - 1]`; nothing
after the loop touches the array, so the final `write` is the answer.

## Solution

```python
# 26. Remove Duplicates from Sorted Array (Easy) - two pointers: `read` scans, `write` marks the next slot in the deduplicated prefix. O(n) time, O(1) space.
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        
        # Dead branch given the constraints (1 <= nums.length), but harmless.
        # It matters only if this were ever called on an empty list, where
        # `write = 1` below would otherwise claim a prefix of length 1 that
        # does not exist.
        if not nums:
            return 0

        # Start at 1, not 0: nums[0] is always the first element of the answer
        # (a single element cannot be a duplicate of anything before it), so
        # the deduplicated prefix begins life as nums[0:1] and `write` points
        # at the next free slot.
        write = 1

        # `read` starts at 1 for the same reason - index 0 is already settled.
        for read in range(1, len(nums)):

            # Compare against nums[write - 1], the LAST VALUE KEPT, not
            # against nums[read - 1], the previous value seen. On a run of
            # duplicates these two diverge: after [1,1,2] copies nothing for
            # the second 1, nums[write-1] is still 1 while nums[read-1] is
            # also 1 - equal here, but once a copy has happened the written
            # prefix is the only reliable record of what was kept. Since the
            # input is sorted, equal values are adjacent, so one comparison
            # against the last kept value is enough to detect any duplicate.
            if nums[read] != nums[write - 1]:
                nums[write] = nums[read]
                write += 1

        # write is both the next free index and the count of distinct values,
        # which is exactly what the problem asks to return.
        return write
```

[solution.py](solution.py) · [raw submission](../../data/raw/remove-duplicates-from-sorted-array.py)

## Why this approach

| Alternative | Cost | Why the two-pointer scan beats it |
|---|---|---|
| `nums[:] = sorted(set(nums))` then return the length | O(n log n) time, O(n) extra space | Correct and one line, but allocates a whole set and a whole new list, which is precisely what "in place, O(1) extra memory" forbids. It also sorts input that is already sorted. |
| Build a new list of distinct values, then copy it back into `nums` | O(n) time, O(n) extra space | Linear like the real answer and easier to write, but the extra list defeats the only interesting requirement in the problem. The two-pointer version is this idea with the output list overlaid onto the input array. |
| `del nums[i]` / `nums.pop(i)` whenever a duplicate is found | O(n²) time | **Not just slow — easy to get outright wrong.** Deleting from a list shifts every later element left, so the loop index must *not* advance after a deletion; forgetting that skips elements. On `[1, 1, 1]` a naive forward loop with `pop` returns `[1, 1]`. The two-pointer scan never mutates length, so this class of bug cannot occur. |
| A 201-slot counting array indexed by `nums[i] + 100` | O(n + 201) time, O(201) space | Would work, since `-100 <= nums[i] <= 100`. But it is O(1) space only by the grace of a constraint this problem happens to have, and it throws away the sortedness that makes the problem easy. It would not survive the value range widening. |

## Complexity

- **Time — O(n)**. One pass; `read` visits each index exactly once and every
  iteration does a constant amount of work (one comparison, at most one
  assignment).
- **Space — O(1)**. Two integer indices. The input array is modified in place
  and nothing else is allocated, regardless of `n`.

## Pitfalls

- **Initializing `write = 0` instead of `1`.** Then the first iteration
  evaluates `nums[write - 1]` as `nums[-1]` — Python's *last* element, not an
  error. On `[1, 2, 3]` that compares `nums[1] != nums[-1]`, i.e. `2 != 3`,
  and happens to work; on `[1, 2, 2]` it compares `nums[1] != nums[-1]`, i.e.
  `2 != 2`, and wrongly skips the `2`, returning `1` with `nums[0:1] == [1]`.
  A negative index silently reading from the far end instead of raising is the
  nastiest failure mode here, because it produces plausible answers on small
  test cases.
- **Returning `write - 1`, or `len(set(nums))` computed separately.** `write`
  is already the count; the off-by-one temptation comes from thinking of it as
  an index. It is both, which is the point.
- **Comparing against `nums[read - 1]`.** On sorted input this is equivalent
  and passes — so this is a bug you cannot detect on this problem, only on the
  next one. The habit to build is comparing against the *written* prefix,
  because that is what generalizes to
  [Remove Duplicates II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/),
  where the rule becomes `nums[read] != nums[write - 2]`.
- **Assuming the tail must be cleaned up.** It does not: values at index `k`
  and beyond are explicitly ignored. Zeroing them out is wasted work (and is
  the *opposite* of what [Move Zeroes](../0283-move-zeroes/README.md) asks
  for, which is a genuinely easy pair to confuse).
- **Handling the empty array.** The constraints forbid it, so the guard is
  dead here — but if you redo this cold and drop the guard on a problem that
  *does* allow `n == 0`, `write = 1` immediately claims a nonexistent element.

## Redo from scratch

1. Say the enabling fact out loud first: **the array is sorted, so duplicates
   are adjacent.** Everything else follows.
2. Two indices. `write = 1`, because `nums[0]` is free — it cannot duplicate
   anything.
3. `for read in range(1, len(nums))`.
4. Keep `nums[read]` only if it differs from `nums[write - 1]`, the last value
   kept. Copy and advance `write`; otherwise do nothing.
5. Return `write`.
6. Check against `[5, 5, 5, 5]` (nothing copied, answer `1`) and `[7]` (loop
   body never runs, answer `1`) — both should fall out of the initialization
   without a special case.

Be able to justify out loud: why the comparison target is `nums[write - 1]`
and not `nums[read - 1]`, and why `write <= read` is what makes overwriting
the input array safe rather than destructive.

## Related problems

- [Remove Element](../0027-remove-element/README.md) — already solved. The
  same two-pointer compaction with a simpler predicate: keep `nums[read]` if
  it does not equal a given target, instead of if it differs from the last
  kept value. Worth re-reading back to back with this one, because they share
  a skeleton and differ only in the `if`.
- [Move Zeroes](../0283-move-zeroes/README.md) — already solved. Third
  variation on the same compaction: keep the non-zeros, then *do* clean up the
  tail. The contrast with this problem — where the tail is explicitly garbage —
  is the thing to notice.
- [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/)
  — not solved yet. Allows each value to appear at most twice. The fix is a
  one-character change to the comparison target (`nums[write - 2]`), which is
  the clearest possible demonstration of why comparing against the written
  prefix rather than the read prefix was the right instinct here.
- [Sum of Distances](https://leetcode.com/problems/sum-of-distances/) — not
  solved yet. Listed as similar by LeetCode, but it is a grouping-by-value
  prefix-sum problem rather than a compaction one; the shared ground is only
  "runs of equal values in an array."
- [Apply Operations to an Array](https://leetcode.com/problems/apply-operations-to-an-array/)
  — not solved yet. A transform pass followed by a compaction pass, where the
  compaction half is exactly the loop above.
