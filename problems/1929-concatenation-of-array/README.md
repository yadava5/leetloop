# 1929. Concatenation of Array

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Simulation |
| **Solved** | 2026-08-17 |
| **Runtime** | 3 ms (18.21th percentile) |
| **Memory** | 19.4 MB (41.28th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/concatenation-of-array/ |

## The problem

**Given** an integer array `nums` of length `n`.

**Return** a new array `ans` of length `2n`, where `ans` is `nums` followed by
another copy of `nums` — `ans[i] == ans[i + n] == nums[i]` for every valid `i`.
It is a brand-new array; `nums` itself is not modified.

**Guaranteed**: nothing beyond the length and value bounds — no sortedness, no
uniqueness. The two halves are simply the same sequence twice, in the same
order both times.

```text
def getConcatenation(self, nums: List[int]) -> List[int]
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[4, 9, 2]` | `[4, 9, 2, 4, 9, 2]` | The ordinary case: the whole array repeated once. |
| `[7]` | `[7, 7]` | **Edge case:** the smallest legal length. One element, doubled. |
| `[5, 5, 5]` | `[5, 5, 5, 5, 5, 5]` | Repeated values are not special — nothing here compares or dedupes elements, so identical values pass straight through. |
| `[1, 2, 3]` | `[1, 2, 3, 1, 2, 3]` | **Counterexample to a naive approach:** the halves are `nums` twice, *not* `nums` followed by its reverse (`[1,2,3,3,2,1]`) and not `nums` sorted. It is a literal repeat, order preserved exactly. |
| `[10, 1, 1000]` | `[10, 1, 1000, 10, 1, 1000]` | Values at the extremes of the constraint range (`1` and `1000`) round-trip with no special handling — there is nothing about the value itself that the code inspects. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `n == nums.length` | Just naming: the input's own length defines `n`, so there is no separate length parameter to reconcile with `len(nums)`. |
| `1 <= n <= 1000` | Small enough that any O(n) approach is instant — at most 2000 writes — so there is no performance pressure pushing toward anything cleverer than the obvious loop or slice. The lower bound of 1 also means `nums` is never empty, so `ans` is never a zero-length array either. |
| `1 <= nums[i] <= 1000` | Values are positive and bounded, but nothing in the solution reads a value to make a decision — every element is only ever copied — so this bound has no effect on the code's logic, only a reassurance that there's no need to worry about negatives or overflow. |

## Key insight

There is no algorithm here — the problem statement *is* the algorithm. The
only decision is how to build the double-length array: write into two
preallocated halves, or let a language builtin do the copy (`nums + nums`,
`nums * 2`). This solution picks the first.

## Approach

1. Compute `n = len(nums)`.
2. Allocate `ans` as a list of `2n` zeros up front.
3. Walk `nums` once with `enumerate`; for each `(i, num)`, write `num` into
   both `ans[i]` (the first copy) and `ans[i + n]` (the second copy) in the
   same assignment.
4. Return `ans`.

There is no ordering constraint between iterations — each index pair
`(i, i + n)` is written independently of every other, so the loop could run
in any order, including in parallel, without changing the result.

## Solution

```python
# 1929. Concatenation of Array (Easy) - preallocate a 2n array, write each element to its two mirrored slots. O(n) time, O(n) extra space.
class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:

        n = len(nums)
        # Preallocating the full 2n-length answer up front avoids ever growing
        # a list with individual appends, which is why this beats `nums + nums`
        # only in principle - see Why this approach below.
        ans = [0] * 2 * n

        # Each element is written to BOTH halves in the same pass: ans[i] is
        # the first copy, ans[i + n] is the second. One loop instead of two,
        # relying on index arithmetic instead of slicing.
        for i, num in enumerate(nums):
            ans[i] = ans[i + n] = num
        return ans
```

[solution.py](solution.py) · [raw submission](../../data/raw/concatenation-of-array.py)

## Why this approach

| Alternative | Cost | Why the manual loop doesn't clearly beat it |
|---|---|---|
| `return nums + nums` | O(n) time, O(n) space | Simpler, and at `n <= 1000` no slower in any way that matters — Python's list concatenation is a single C-level memcpy of both operands. The explicit loop exists here as a `for`-loop exercise, not because it's faster; if anything the interpreted Python loop has more per-element overhead than the builtin. |
| `return nums * 2` | O(n) time, O(n) space | Same story as `+`: idiomatic, equally fast at this size, and arguably the clearest one-liner for "this sequence, twice". |
| Two separate loops, one per half | O(n) time, O(n) space | Functionally identical to writing both slots in one pass; just twice as many loop iterations for no benefit, since `ans[i]` and `ans[i+n]` are independent. |
| Preallocate and write both slots per iteration (this solution) | O(n) time, O(n) space | Chosen here specifically to make the doubling explicit — the code visibly states "index `i` and index `i+n` hold the same value" rather than leaning on a builtin to imply it. Worth knowing `nums + nums` is the version to reach for outside a learning exercise. |

## Complexity

- **Time — O(n)**. One pass over `nums`, two constant-time writes per
  element.
- **Space — O(n)** beyond the input, for the `2n`-length `ans` array — the
  minimum possible, since the output itself has `2n` elements.

## Pitfalls

- **None of the usual off-by-ones apply here** — `ans[i + n]` for `i` in
  `range(n)` reaches exactly indices `n` through `2n - 1`, filling `ans`
  completely with no gap and no out-of-bounds write. There's little room for
  a subtle bug in a problem this direct.
- The one thing to *not* do is reach for `nums[:]` or `list(nums)` for one
  half and `nums` itself for the other — that copies correctly but invites
  confusing which one is the "original" if the function were ever extended
  to mutate `nums` afterward. Not a bug in the code as written, just a trap
  for a modified version of it.

## Redo from scratch

1. Notice the problem *is* the definition: build the length-`2n` array
   `[nums[0..n-1], nums[0..n-1]]`.
2. Preallocate `ans = [0] * 2 * n` (or just return `nums + nums`).
3. Loop `i` over `range(n)` (or use `enumerate`), setting both
   `ans[i]` and `ans[i + n]` to `nums[i]`.
4. Sanity check on `[7]`: expect `[7, 7]`, and `ans[0 + 1] = ans[1]` is indeed
   the second half.

Be able to say out loud: why `nums + nums` is the version worth writing in
practice, and why the manual index version doesn't need any special-casing
for the smallest input (`n = 1`) — the loop runs once, filling both of the
array's two slots.

## Related problems

No `similar` entries were provided for this problem. By topic, the closest
match in spirit is any "build a derived array by direct index arithmetic"
problem — none of those are in this repo yet, and this page is short enough
that a related-problems section would mostly be padding for an Easy this
direct.
