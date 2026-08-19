# 75. Sort Colors

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Two Pointers, Sorting, Quicksort, Bubble Sort |
| **Solved** | 2026-08-18 |
| **Runtime** | 0 ms (100th percentile) |
| **Memory** | 19.2 MB (62.11th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/sort-colors/ |

## The problem

**Given** an array `nums` where every element is one of exactly three
values: `0`, `1`, or `2` (representing three "colors" — conventionally red,
white, blue).

**Return** nothing — sort `nums` **in place** so all the `0`s come first,
then all the `1`s, then all the `2`s. (The function's own declared return
type is `None`; the array is mutated directly.)

**Guaranteed**: every element is exactly `0`, `1`, or `2` — no other integer
values ever appear, which is the whole reason a specialized single-pass
partition (rather than a general comparison sort) is possible here.

```text
def sortColors(self, nums: List[int]) -> None
```

### Examples (mine, not LeetCode's)

| `nums` (before → after) | Why |
|---|---|
| `[2, 0, 1] → [0, 1, 2]` | The ordinary case: one of each color, out of order. |
| `[0] → [0]` | **Edge case:** length 1. Nothing to partition; the loop should do zero meaningful work and terminate immediately. |
| `[1, 1, 1] → [1, 1, 1]` | All the same color. No `0` region and no `2` region ever form — `left` never advances past index `0` and `right` never retreats, so the array is untouched, which is the correct output. |
| `[2, 2, 0, 0] → [0, 0, 2, 2]` | **Counterexample to a naive single-swap-and-advance approach:** when a `2` is swapped in from the right end (at `nums[right]`), the element that lands at the current position hasn't been examined yet and might itself be a `0` or another `2` — an approach that always advances `i` after any swap would misclassify it. |
| `[1, 0, 2, 1, 0] → [0, 0, 1, 1, 2]` | A mix that exercises all three branches — `0`-swap, `1`-skip, `2`-swap — in the same pass, including a `0` encountered *after* some `1`s, which must still get swapped correctly into the growing `0`-region left of them. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `n == nums.length` | Just naming: the input's own length defines `n`. |
| `1 <= n <= 300` | Small enough that literally any correct sort — even an O(n²) one, or calling `nums.sort()` — would run instantly; there's no performance pressure from the size alone. The real constraint that shapes the *algorithm* choice here is the value range below, not this bound: the intent of the problem (explicit in a well-known follow-up asking for one pass and constant space) is to avoid a general sort in favor of exploiting that there are only three distinct values. |

*Only two constraints were captured for this problem — `n` and its bound.
From memory — **recalled, not read**, so treat it as unverified — the
statement also restricts every element to `nums[i] ∈ {0, 1, 2}`, and poses a
well-known follow-up asking for a one-pass, constant-extra-space solution
without using a library sort. The solution here matches that follow-up; the
three-value restriction is what makes it possible.*

## Key insight

With only three possible values, sorting isn't really "sorting" in the
comparison sense — it's **partitioning into three regions** in a single
pass. Track two boundaries: everything before `left` is known to be `0`,
everything after `right` is known to be `2`, and a scanning pointer `i`
walks the unknown middle, growing whichever boundary applies as it goes.
This is the classic Dutch national flag partition.

## Approach

1. Initialize `i = 0`, `left = 0`, `right = len(nums) - 1`. `left` marks the
   next slot to fill with a `0`; `right` marks the next slot to fill with a
   `2`, from the far end; `i` is the scan position.
2. Loop while `i <= right` — the region from `i` to `right` inclusive is
   what's still unclassified; once `i` passes `right`, everything has been
   placed.
3. If `nums[i] == 0`: swap it with `nums[left]`, then advance **both** `left`
   and `i`. Advancing `i` here is safe because the element swapped in from
   `left` is guaranteed to be something already classified as `<= 1` (it was
   at or before the scan position previously), so it needs no re-examination.
4. If `nums[i] == 1`: it's already in the correct relative region — just
   advance `i`.
5. Otherwise (`nums[i] == 2`): swap it with `nums[right]`, then advance
   **only** `right`, leaving `i` unchanged. This is the one asymmetry in the
   whole function: the element just swapped into `nums[i]` from the far end
   has **not** been examined yet — it could be a `0`, `1`, or another `2` —
   so `i` must revisit the same position on the next iteration rather than
   advancing past it.

The asymmetry between the `0`-branch (advances `i`) and the `2`-branch
(does not) is the one detail that makes or breaks this algorithm; getting it
backwards produces a partially-sorted array on inputs like
`[2, 0, 2, 1]`.

### Why it's correct

**Invariant**, maintained before and after every iteration of the `while`
loop: `nums[0:left]` is all `0`s, `nums[left:i]` is all `1`s,
`nums[right+1:]` is all `2`s, and `nums[i:right+1]` is unclassified (could
be any of 0/1/2). Each branch preserves it: the `0`-branch swaps `nums[i]`
(a known `0`) into `nums[left]`, extending the `0`-region by one and pulling
whatever was at `left` — which by the invariant was either the very first
unclassified element or already part of the `1`-region — into position `i`,
which is why it's safe to also advance `i` past it: it lands squarely on the
boundary of the (now-extended) `1`-region, correctly classified either way.
The `1`-branch simply extends the `1`-region by advancing `i`, since
`nums[i] == 1` already belongs where it sits. The `2`-branch swaps `nums[i]`
(a known `2`) into `nums[right]`, extending the `2`-region on the right —
but the element pulled in from `nums[right]` is entirely unexamined (nothing
in the invariant says anything about it), which is exactly why `i` must
**not** advance here: the next iteration needs to classify that same
position from scratch.

**Termination**: the loop condition is `i <= right`, and every branch either
increments `i`, decrements `right`, or both — never neither — so the
quantity `right - i` strictly decreases (or, in the `0`-branch, `i`
increases while `right` stays fixed, still shrinking the gap) every single
iteration. Since `right - i` starts finite and strictly decreases each step,
the loop must terminate, and it does so exactly when `i > right`, meaning
the unclassified region `nums[i:right+1]` has become empty — consistent
with the invariant, since an empty range trivially satisfies "all
unclassified elements are unclassified." The one thing to notice about the
loop bound: it's `i <= right`, not `i < right` — using `<` would exit one
iteration early and leave `nums[right]` (a boundary element, not yet
classified into the `2`-region) unexamined whenever the array's last
still-unknown element is exactly at that position.

The step I'd flag as the one most worth re-deriving rather than trusting on
faith: *why* it's safe to advance `i` after a `0`-swap but not after a
`2`-swap. It comes down to which end of the array the incoming element was
pulled from — `left` only ever holds elements the scan has already visited
(so swapping one in and re-scanning it would be redundant, not incorrect,
but advancing past it is what makes the pass single-pass), while `right`
holds elements the scan has never visited (so re-scanning is mandatory,
not optional).

## Solution

```python
# 75. Sort Colors (Medium) - Dutch national flag: three pointers partitioning nums into 0s, 1s, 2s in one pass, in place. O(n) time, O(1) space.
class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """

        # i scans forward through the unexamined region; left/right are the
        # boundaries of the growing 0-region (before left) and 2-region
        # (after right). The 1-region is implicitly everything between
        # left and i that i has already passed over.
        i = 0
        left = 0
        right = len(nums) - 1

        while i <= right:

            if nums[i] == 0:
                # Swap the 0 into place at `left` and advance BOTH pointers:
                # the element now at nums[i] (previously at left) is known to
                # be <= 1 already-processed territory, safe to move past.
                nums[i], nums[left] = nums[left], nums[i]
                left += 1
                i += 1

            elif nums[i] == 1:
                # Already in its correct region relative to i; just advance.
                i+= 1

            else:
                # Swap the 2 into place at `right` and advance ONLY `right`,
                # NOT `i` - the element swapped in from the right end hasn't
                # been examined yet, so i must re-check nums[i] next iteration.
                nums[i], nums[right] = nums[right], nums[i]
                right -= 1
```

[solution.py](solution.py) · [raw submission](../../data/raw/sort-colors.py)

## Why this approach

| Alternative | Cost | Why the three-pointer partition beats it |
|---|---|---|
| `nums.sort()` (a general comparison sort) | O(n log n) time | Trivially correct and simple, but ignores that only three distinct values exist — the whole point of the well-known follow-up on this problem (one pass, constant space) is to do better than a general sort when the value range is this restricted. |
| Counting sort: count the 0s/1s/2s in one pass, then overwrite `nums` with that many of each in a second pass | O(n) time, O(1) extra space | Also linear and constant-space, and arguably simpler to reason about — but it's **two** passes over the array, where the Dutch flag partition does the same job in **one**. Equally valid; this solution is the tighter version of the same asymptotic idea. |
| Bubble sort / repeated adjacent swaps | O(n²) time | Correct, but does far more comparisons and swaps than necessary given only three distinct values — the constraint (`n <= 300`) would let it pass here regardless, but it doesn't scale and doesn't use the three-value structure at all. |
| Quicksort with a 3-way (Dutch flag) partition as the *whole* sort, not just this one problem | O(n log n) average | This problem's partition step **is** exactly quicksort's 3-way partition scheme, applied once instead of recursively — recognizing that connection is why this pattern is called "Dutch national flag" in the first place (it comes from Dijkstra's three-way partitioning). |

## Complexity

- **Time — O(n)**. Each of the three pointers moves monotonically
  (`left` and `i` only increase, `right` only decreases) and the loop
  terminates once `i` and `right` cross, so the total number of pointer
  advances across the whole run is bounded by `2n` — no element is ever
  re-examined more than a constant number of times.
- **Space — O(1)**. Only three integer pointers (`i`, `left`, `right`) are
  used beyond the input; the sort happens via in-place swaps on `nums`
  itself, with no auxiliary array.

## Pitfalls

- **Advancing `i` after a `2`-swap.** If the `else` branch also did
  `i += 1`, then `[2, 0, 2, 1]` would fail: at `i=0`, `nums[0]=2` swaps with
  `nums[right=3]=1`, giving `[1, 0, 2, 2]`; advancing `i` to 1 then skips
  re-examining the `1` that just landed at index 0, but the deeper failure
  shows up whenever the swapped-in element is itself a `0` or `2` — e.g.
  `[2, 2, 0]`: swapping `nums[0]` with `nums[right=2]` gives `[0, 2, 2]`,
  and if `i` incorrectly advanced to 1, the `0` now sitting at index 0 would
  never be moved into the `left`-region (it happens to already be
  correctly placed here by luck, but `[2, 0, 0]` with the same wrong
  advance would leave a `0` stranded to the right of where it belongs).
- **Using `i < right` instead of `i <= right`** as the loop condition drops
  the last element from consideration whenever it's still unclassified at
  the point the loop would otherwise exit, leaving one element unswapped.
- **Trying to solve this with a single `left`/`right` two-pointer pass (as
  in problems with only two distinct values)** doesn't directly generalize —
  three values need three regions, which is why this needs `i` as a
  *separate* scanning pointer in addition to the two region boundaries,
  not just `left`/`right` alone.

## Redo from scratch

1. Recognize "only three distinct values" as the signal for a Dutch
   national flag three-way partition, not a general sort.
2. Three pointers: `i = 0`, `left = 0`, `right = len(nums) - 1`.
3. Loop `while i <= right`. On `0`: swap to `left`, advance both `left` and
   `i`. On `1`: advance `i` only. On `2`: swap to `right`, advance `right`
   only — **not** `i`.
4. The one line to say out loud before writing any code: "after a 2-swap,
   `i` does not move, because the incoming element is unexamined."
5. Stress-test mentally on `[2, 0, 2, 1]` — the case that breaks if the `i`
   advance is applied to both swap branches instead of just the `0` one.

Be able to justify out loud: why `left` and `i` advance together on a
`0`-swap but `right` advances alone on a `2`-swap — it's about which
direction the incoming replacement element came from, and whether it's
already been classified.

## Related problems

- [Sort List](https://leetcode.com/problems/sort-list/) — not solved yet.
  Sorting with no value-range restriction, on a linked list rather than an
  array — none of this problem's three-way partition trick applies; it
  needs a general O(n log n) sort like merge sort instead, similar in
  spirit to [Sort an Array](../0912-sort-an-array/README.md).
- [Wiggle Sort](https://leetcode.com/problems/wiggle-sort/) — not solved
  yet. A different ordering target (alternating peaks and valleys, not
  ascending) but shares the "structural constraint replaces the need for a
  full comparison sort" theme — worth comparing how differently that
  constraint gets exploited.
- [Wiggle Sort II](https://leetcode.com/problems/wiggle-sort-ii/) — not
  solved yet. The strict version of Wiggle Sort, notably harder — a good
  test of whether the "read the exact constraint, then pick the minimal
  algorithm it permits" instinct this problem builds actually transfers to
  a case where the easy version's approach doesn't scale up.
