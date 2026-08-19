# 912. Sort an Array

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Divide and Conquer, Sorting, Heap (Priority Queue), Merge Sort, Bucket Sort, Radix Sort, Counting Sort |
| **Solved** | 2026-08-17 |
| **Runtime** | 643 ms (48.5th percentile) |
| **Memory** | 27.3 MB (60.71th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/sort-an-array/ |

## The problem

**Given** an array of integers `nums`.

**Return** a **new** array containing the same elements in non-decreasing
order. (The reference solution returns a freshly built list rather than
sorting `nums` in place, though the problem itself doesn't require the input
untouched — see Pitfalls.)

**Guaranteed**: nothing beyond the length and value bounds — no bound on how
many duplicates may appear, and values may be negative.

```text
def sortArray(self, nums: List[int]) -> List[int]
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[8, 3, 5, 1]` | `[1, 3, 5, 8]` | The ordinary case: an unsorted array with no duplicates or negatives. |
| `[4]` | `[4]` | **Edge case:** length 1. Already "sorted"; the base case must return it unchanged rather than looping forever trying to split further. |
| `[2, 2, 2]` | `[2, 2, 2]` | **Edge case:** all duplicates. A merge that compares with `<=` instead of `<` still produces the right *values* here, but this is the case that would silently flip a stability bug into invisibility — worth testing even though it "looks trivial." |
| `[-3, 0, -1, 2]` | `[-3, -1, 0, 2]` | Negative values sort like any other integer — nothing in a comparison-based sort special-cases sign, unlike counting sort, which needs an offset to handle negative indices. |
| `[5, 4, 3, 2, 1]` | `[1, 2, 3, 4, 5]` | **Counterexample to a naive approach:** completely reverse-sorted input is the worst case for a naive insertion-sort-style approach (O(n²)) but costs merge sort nothing extra — every split and merge does the same fixed amount of work regardless of the input's initial order. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 5 * 10^4` | The lower bound rules out an empty-array edge case entirely. The upper bound (50,000) is what rules out any O(n²) sort — bubble sort or naive insertion sort would be on the order of 2.5×10^9 operations, far too slow in Python — and pushes toward an O(n log n) algorithm, which at this size is roughly 50,000 × 17 ≈ 8.5×10^5 comparisons, comfortably fast. |
| `-5 * 10^4 <= nums[i] <= 5 * 10^4` | A bounded integer range of exactly 10^5 possible values. This is what makes **counting sort** (bucket per distinct value) a legitimate O(n + k) alternative here, with `k = 10^5` — worth knowing as an alternative even though this solution doesn't take it (see Why this approach). The negative lower bound specifically rules out any scheme that uses a raw value directly as an array index without an offset. |

## Key insight

Sorting is trivial for size 0 or 1, and if you can **merge** two
already-sorted lists into one sorted list in linear time, then splitting an
array in half, sorting each half recursively, and merging the results
sorts the whole thing — the merge step is the only place actual comparison
work happens; the split just creates smaller subproblems for free.

## Approach

1. If `arr` has length 0 or 1, it's already sorted — return it as-is (base
   case, and the only place recursion stops).
2. Otherwise, split `arr` at its midpoint into `left` and `right` — two
   slices, each roughly half the size.
3. Recursively sort `left` and recursively sort `right`. This step **must
   happen before merging** — the merge step below only produces a correct
   result when both of its inputs are already individually sorted; merging
   unsorted halves would silently produce garbage that still happens to be
   the same *length*.
4. Merge the two sorted halves: walk both with pointers `i` (into `left`)
   and `j` (into `right`), repeatedly appending whichever front element is
   smaller and advancing that pointer, until one side is exhausted.
5. Append whatever remains of the non-exhausted side in bulk — exactly one
   of the two trailing `while` loops in step 5 will ever run any iterations,
   since the main loop above stops the instant *either* side empties.
6. Return the merged `result`; this becomes the sorted form of `arr` one
   level up the recursion.

## Solution

```python
# 912. Sort an Array (Medium) - classic top-down merge sort, implemented with fresh list slices at every split. O(n log n) time, O(n) space per merge level.
class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:

        def mergeSort(arr):

            # Base case: 0 or 1 element is trivially sorted already, and
            # splitting further would either loop forever (empty slices
            # can't shrink) or be pointless.
            if len(arr) <= 1:
                return arr

            # Split into two halves. Slicing here copies, so `left`/`right`
            # are independent lists - arr itself is never mutated.
            mid = len(arr) // 2
            left = arr[:mid]
            right = arr[mid:]

            # Sort each half FIRST, recursively, before attempting to merge -
            # merging only produces a sorted result if its two inputs are
            # already individually sorted. This ordering (sort, then merge)
            # is the entire algorithm.
            left = mergeSort(left)
            right = mergeSort(right)

            # Merge the two now-sorted halves by repeatedly taking the
            # smaller of the two current fronts. `<` (strict) rather than
            # `<=` means on a tie the LEFT half's element is taken first -
            # this is what keeps the sort stable.
            i = 0
            j = 0
            result = []

            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

            # One of the two halves may still have leftover elements once the
            # other is exhausted - both loops are needed since exactly one of
            # them (never both) will actually execute any iterations.
            while i < len(left):
                result.append(left[i])
                i += 1

            while j < len(right):
                result.append(right[j])
                j += 1

            return result
        return mergeSort(nums)
```

[solution.py](solution.py) · [raw submission](../../data/raw/sort-an-array.py)

### Why it's correct

**Invariant** (by strong induction on subarray length): `mergeSort(arr)`
returns a list containing exactly the elements of `arr`, in non-decreasing
order. Base case (length `<= 1`): trivially true, an array of 0 or 1
elements is already sorted. Inductive step: assuming the invariant holds for
any array shorter than `len(arr)` — which `left` and `right` both are, since
each is strictly smaller than `arr` for `len(arr) >= 2` — `left` and `right`
are correctly sorted after their recursive calls. The merge loop then
repeatedly moves the smaller of the two current fronts into `result`; since
both `left` and `right` are individually sorted, the smaller of their two
current fronts is guaranteed to be `<=` every remaining element in *both*
lists, so it's safe to commit it to `result` immediately — no future element
from either side could ever need to be placed before it. Once one side is
exhausted, everything left in the other side is by definition `>=`
everything already placed, so appending the remainder in order preserves
sortedness.

**Termination**: recursion terminates because each call operates on a
strictly shorter array than its caller (`mid = len(arr) // 2` splits any
array of length `>= 2` into two non-empty pieces, each shorter than the
original), bottoming out at the length-`<=1` base case — this is standard
divide-and-conquer termination, no off-by-one risk in the split itself. The
merge loop's `i < len(left) and j < len(right)` guard means it stops the
moment *either* index reaches its list's length, which is exactly why the
two follow-up `while` loops are separate rather than combined — at most one
of them has any remaining work, but which one isn't known in advance, so
both must be present to drain whichever side is left over.

The step I'm least certain a first-time reader would find obvious: the
strict `<` in `if left[i] < right[j]`. Using `<=` instead would still
produce a value-correct sort (the numbers end up in the same non-decreasing
order either way), but it changes *which* physical element is taken first
on a tie — with `<`, a tie takes from `left` first, preserving the relative
order of equal elements from the original array (stability). This solution
doesn't rely on that stability anywhere the problem can observe (LeetCode
only checks the final values), but it's the detail to know if this code
were ever reused somewhere stability mattered.

## Why this approach

| Alternative | Cost | Why merge sort is the reasonable choice here |
|---|---|---|
| Python's built-in `sorted()` / `list.sort()` (disqualified in spirit — this is a "sort from scratch" exercise) | O(n log n) time, highly optimized C (Timsort) | Would trivially pass and be faster in practice. The point of this problem is implementing a sort, so a from-scratch algorithm is the intended answer even though it's slower than the builtin. |
| Quicksort (in-place, e.g. Lomuto or Hoare partition) | O(n log n) average, O(n^2) worst case | Uses O(log n) space instead of merge sort's O(n) (better), but has an adversarial worst case (e.g. certain already-sorted or specially crafted inputs against a naive pivot choice) that merge sort's guaranteed O(n log n) avoids entirely. Merge sort trades memory for a worst-case guarantee. |
| Counting sort, using an offset for the negative range (`-5*10^4` to `5*10^4`, `k = 10^5` buckets) | O(n + k) time, O(k) space | Asymptotically better here since `k = 10^5` is comparable to `n`'s upper bound of `5*10^4` — a real contender at these specific constraints. It's a narrower tool though: it only works because the value range is small and known; merge sort makes no assumption about the values at all, only that they're comparable, so it still works if the constraint allowed arbitrarily large integers. |
| Heap sort (build a heap, pop repeatedly) | O(n log n) time, O(1) extra space (in-place variant) | Better space complexity than this merge sort (which allocates new lists at every merge level), at the cost of being harder to implement correctly from scratch and, in practice, worse cache behavior than merge sort's sequential access pattern. |
| Insertion sort / bubble sort | O(n^2) time | **The reason the constraint (`n` up to 5×10^4) exists.** At that size, O(n^2) is on the order of 2.5×10^9 operations — far too slow in Python within typical time limits. |

## Complexity

- **Time — O(n log n)**. The array is split in half at each of `O(log n)`
  levels of recursion, and every level does `O(n)` total work across all the
  merges at that level (each element is compared and copied into `result`
  exactly once per level) — `O(log n)` levels × `O(n)` work per level.
- **Space — O(n)**. Beyond the input, every call to `mergeSort` allocates
  new lists for `left`, `right`, and `result` — at the top level these sum
  to `O(n)`, and although recursive calls allocate further lists, the total
  live memory at any one time (accounting for lists that go out of scope
  once merged) is `O(n)`, plus `O(log n)` for the recursion call stack
  itself.

## Pitfalls

- **This solution does not sort in place** — it returns a new list built up
  through `result.append(...)` calls, and `nums` itself is untouched by the
  merge (only read from, via the slices `arr[:mid]` / `arr[mid:]`, which
  copy). If a caller expected `nums` itself to end up sorted (as some
  in-place sort problems require), this returns the right *value* but
  leaves the original argument unsorted — worth knowing since the problem
  name suggests "sort an array" without specifying in-place vs. new.
- **Comparing with `<=` instead of `<`** in the merge step doesn't produce a
  wrong *answer* (the values still end up correctly ordered) but silently
  breaks stability — on `[(1,'a'), (1,'b')]`-style tie-breaking scenarios
  (not applicable to plain integers, but relevant if this were adapted to
  sort objects by key), it would let ties from the right list jump ahead of
  ties from the left list.
- **Off-by-one in the base case.** `if len(arr) == 0` instead of
  `if len(arr) <= 1` misses the length-1 case: a length-1 array would then
  fall through to `mid = 0`, `left = []`, `right = arr` — an infinite
  recursion, since `right` is identical in length to the original `arr` and
  never shrinks.

## Redo from scratch

1. Base case: length `<= 1` returns as-is.
2. Split at `mid = len(arr) // 2` into `left`, `right` — both strictly
   shorter than `arr` whenever `len(arr) >= 2`, which is what guarantees the
   recursion terminates.
3. Recursively sort both halves *before* merging — merging unsorted input
   silently produces nonsense that still happens to be the right length.
4. Merge with two pointers, comparing fronts and appending the smaller,
   advancing that pointer; use `<` rather than `<=` for stability if it
   matters.
5. Drain whichever side has leftovers with a simple trailing loop (or,
   equivalently, `result.extend(left[i:])` then `result.extend(right[j:])`).
6. Sanity check on `[2, 2, 2]` (all-duplicate) and `[5, 4, 3, 2, 1]`
   (reverse-sorted, the case a naive insertion sort chokes on).

Be able to justify out loud: why the merge step requires its two inputs to
already be sorted (it's not "sort as you go" — the correctness argument
above depends on it), and why splitting always terminates (each half is
strictly shorter, down to the length-`<=1` base case).

## Related problems

No `similar` entries were provided for this problem. By technique:

- [Sort Colors](../0075-sort-colors/README.md) — solved. A much more
  constrained sort (only three distinct values) that a comparison-based
  merge sort would badly over-solve — that page's single-pass, O(1)-space
  Dutch national flag partition is the technique to reach for once the
  value range collapses to a handful of distinct values, in contrast to
  this page's general-purpose approach for arbitrary integers.
