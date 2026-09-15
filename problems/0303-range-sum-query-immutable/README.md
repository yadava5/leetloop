# 303. Range Sum Query - Immutable

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Design, Prefix Sum |
| **Solved** | 2026-08-18 |
| **Runtime** | 0 ms (100th percentile) |
| **Memory** | 23 MB (17.32th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/range-sum-query-immutable/ |

## The problem

A **design** problem: implement a class, not a function.

**Given** an integer array `nums` passed once to the constructor. The array is
**immutable** — no update operation exists, and it never changes after
construction.

**Return**, from `sumRange(left, right)`, the sum of `nums[left] + nums[left+1]
+ ... + nums[right]` — **inclusive of both endpoints**. The method will be
called many times on the same array.

The shape of the problem is the point: one setup, many queries. That asymmetry
is what makes precomputation pay, and "immutable" is the promise that lets the
precomputed structure stay valid forever.

**Guaranteed**: `0 <= left <= right < nums.length`. Queries are always valid
and never inverted, so no bounds checking or argument swapping is needed.

```text
def __init__(self, nums: List[int])
def sumRange(self, left: int, right: int) -> int
```

### Examples (mine, not LeetCode's)

| Calls | Returns | Why |
|---|---|---|
| `NumArray([3, 1, 4])`, then `sumRange(0, 2)` | `8` | The whole array. `prefix` is `[0, 3, 4, 8]`, so the answer is `prefix[3] - prefix[0] = 8 - 0`. |
| same object, `sumRange(1, 1)` | `1` | **Edge case:** a single element, where `left == right`. Gives `prefix[2] - prefix[1] = 4 - 3 = 1`. The formula must not special-case this, and it does not. |
| same object, `sumRange(0, 0)` | `3` | **Edge case:** the very first element, where `left == 0`. This is the case the leading `prefix[0] = 0` exists for — `prefix[1] - prefix[0] = 3 - 0`. Without that sentinel, `left == 0` would need its own branch. |
| `NumArray([-5, 2, -5])`, then `sumRange(0, 2)` | `-8` | Negative values. Nothing about prefix sums assumes positivity — a common false instinct, since the *sliding window* techniques that also sum subarrays usually do require it. |
| `NumArray([9])`, then `sumRange(0, 0)` | `9` | Minimum-size array. `prefix` is `[0, 9]`; the only legal query reads both entries. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 10^4` | The array is never empty, so `prefix` always has at least two entries and the constructor's loop always runs at least once. Ten thousand elements is small enough that the prefix array itself is trivially affordable in memory — this bound is not what makes the problem interesting. |
| `-10^5 <= nums[i] <= 10^5` | **Values can be negative**, which rules out the entire family of two-pointer and sliding-window tricks that assume sums grow monotonically as a window widens. Prefix sums work regardless of sign, which is precisely why they are the right tool here. The magnitude also bounds the worst-case total: 10⁴ × 10⁵ = 10⁹, which fits in a signed 32-bit int with room to spare — so a C++ or Java version would not need 64-bit accumulators, and Python's arbitrary-precision ints make the question moot anyway. |
| `0 <= left <= right < nums.length` | **The reason there is no validation code.** `left <= right` means the range is never inverted, so no swap is needed; `right < nums.length` means `prefix[right + 1]` is always in bounds — the `+ 1` can never run off the end, which is the single most fragile-looking thing in the solution. `left >= 0` means the subtraction never picks up a negative index and silently reads from the far end. |
| `At most 10^4 calls will be made to sumRange.` | **The constraint that decides the whole design.** With up to 10⁴ queries on a 10⁴-element array, a naive `sum(nums[left:right+1])` per call is 10⁴ × 10⁴ = **10⁸ element additions**, far too slow in Python. Precomputing shifts the work to a single O(n) build and makes each query O(1), for 10⁴ + 10⁴ ≈ 2 × 10⁴ operations total. This line is what turns an obvious one-liner into a design problem. |

## Key insight

The sum of any contiguous range is the difference of two running totals. Store
the running total *before* each index, and every range query collapses to one
subtraction — no loop, no matter how wide the range. The one trick that makes
it painless is prepending a `0`, so that "the total before index `i`" is always
`prefix[i]` and the `left == 0` case needs no special handling.

## Approach

1. In the constructor, start `prefix = [0]`. That leading zero means "the sum
   of the first zero elements."
2. Walk `nums` once, appending `prefix[-1] + num` each time. Afterwards
   `prefix` has `n + 1` entries and `prefix[i]` is the sum of the first `i`
   elements of `nums` — i.e. of `nums[0:i]`, with the right endpoint exclusive.
3. For `sumRange(left, right)`, return `prefix[right + 1] - prefix[left]`.

The order is forced — the build must complete before any query — but there is
nothing subtle about it. The one detail that *is* subtle is the indexing
convention in step 2: `prefix` is indexed by **count**, not by position. Every
off-by-one in this problem comes from mixing those two up.

## Solution

```python
# 303. Range Sum Query - Immutable (Easy) - precompute a prefix-sum array once, answer each query by subtracting two entries. O(n) build, O(1) per query.
class NumArray:

    def __init__(self, nums: List[int]):

        # prefix[i] holds the sum of the first i elements, so prefix[0] = 0
        # for the empty prefix. That leading zero is what makes the query
        # formula below need no special case for left == 0.
        self.prefix = [0]

        # Each entry is the previous running total plus the current element,
        # so this builds all n + 1 prefix sums in a single pass.
        for num in nums:
            self.prefix.append(self.prefix[-1] + num)


    def sumRange(self, left: int, right: int) -> int:
        
        # sum(nums[left..right]) inclusive = (sum of first right+1 elements)
        # - (sum of first left elements). The +1 is because `right` is an
        # inclusive index but prefix is indexed by COUNT, so the element at
        # `right` must be included in the larger term.
        return (self.prefix[right + 1] - self.prefix[left])



# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# param_1 = obj.sumRange(left,right)
```

[solution.py](solution.py) · [raw submission](../../data/raw/range-sum-query-immutable.py)

## Why this approach

| Alternative | Cost | Why the prefix array beats it |
|---|---|---|
| Store `nums` and compute `sum(nums[left:right + 1])` per call | O(1) build, O(n) per query → up to 10⁸ total | The direct translation of the problem statement, and the thing the "at most 10⁴ calls" constraint exists to defeat. It also allocates a slice copy on every call, so the constant factor is worse than the asymptotics suggest. |
| `itertools.accumulate(nums, initial=0)` into a list | Identical — O(n) build, O(1) query | The same array, built by the standard library instead of by hand. Genuinely better Python (one call, C-speed loop), and worth knowing. The explicit loop is kept here because it makes the `prefix[0] = 0` convention visible, which is the part that has to be right. |
| Prefix array with **no** leading zero, so `prefix[i]` = sum of `nums[0..i]` | Identical complexity | Saves one array slot and costs a branch: the query becomes `prefix[right] - prefix[left - 1]`, which reads `prefix[-1]` — Python's *last* element — when `left == 0`, silently returning nonsense instead of raising. You then need `if left == 0` to patch it. The sentinel trades one integer for the removal of an entire error case. |
| Segment tree or Fenwick (BIT) | O(n) build, O(log n) query, O(n) space | Strictly worse here: more code, more memory, and slower queries, in exchange for update support the problem explicitly does not need. This is the right answer to [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/), and the difference between the two problems is exactly the word *immutable*. |
| Precompute every `(left, right)` pair into a lookup table | O(n²) build and space → 10⁸ entries | O(1) queries too, but 10⁸ integers is gigabytes. The prefix array gets the same query cost for O(n) space by storing the *differences* rather than the answers. |

## Complexity

- **Time — O(n) to construct, O(1) per query.** The constructor makes one pass
  appending `n` entries (amortized O(1) each, since Python list append is
  amortized constant). `sumRange` does two index lookups and one subtraction,
  with no dependence on the width of the range — a query spanning all 10,000
  elements costs exactly the same as one spanning a single element.
- **Space — O(n)**. One auxiliary list of `n + 1` integers, held for the
  object's lifetime. Note the original `nums` is deliberately *not* stored —
  the prefix array subsumes it entirely, since `nums[i]` could be recovered as
  `prefix[i + 1] - prefix[i]` if ever needed.

## Pitfalls

- **Writing `prefix[right] - prefix[left]`** (forgetting the `+ 1`). This
  silently returns the sum of `nums[left:right]` — the range with the **last
  element excluded**. On `[3, 1, 4]` with `sumRange(0, 2)` it gives `4`
  instead of `8`. It is off by exactly one element, so it looks nearly right
  on small inputs and is easy to talk yourself past.
- **Dropping the leading zero and not noticing.** With `prefix[i]` = sum of
  `nums[0..i]`, the query `prefix[right] - prefix[left - 1]` reads
  `prefix[-1]` when `left == 0`. Python does not raise — it returns the final
  element of the list, i.e. the total sum of the whole array. So
  `sumRange(0, 0)` on `[3, 1, 4]` returns `3 - 8 = -5`. A negative-index read
  masquerading as a valid lookup is the worst failure mode in this problem.
- **Summing inside the constructor with `sum(nums[:i])` per entry.** That is
  O(n²) at build time — 10⁸ operations for `n = 10⁴`, which times out during
  construction rather than during queries, making the cause harder to spot.
  The running total (`prefix[-1] + num`) is what keeps the build linear.
- **Assuming positivity.** Values can be negative, so `prefix` is **not
  monotonically increasing**. Any instinct to binary-search it, or to reason
  that a wider range has a larger sum, is wrong here.
- **Storing `nums` as well and letting the two drift.** Harmless in this
  immutable problem, but it is the seed of the bug that appears the moment
  someone adds an `update` method: the prefix array must be rebuilt or it
  becomes silently stale. The immutability guarantee is what makes caching
  safe at all.

## Redo from scratch

1. Notice the shape first: **one build, many queries.** That alone says
   precompute, before you know what to precompute.
2. `prefix = [0]`, then append the running total for each element. Say the
   convention out loud: **`prefix[i]` is the sum of the first `i` elements**,
   right endpoint exclusive.
3. Query: `prefix[right + 1] - prefix[left]`. Derive the `+ 1` from the
   convention rather than recalling it — `right` is inclusive, `prefix` is
   indexed by count, so the count that includes `right` is `right + 1`.
4. Sanity-check `sumRange(0, 0)` on a 3-element array. If it does not come out
   as `nums[0]`, the sentinel or the offset is wrong.
5. Do **not** write a special case for `left == 0`. Needing one is the signal
   that the leading zero is missing.

Be able to justify out loud: why the leading `0` removes a branch rather than
merely being a convention, and what specifically changes if the array becomes
mutable (answer: a point update invalidates every prefix entry from that index
onward, which is O(n) to repair — and that cost is what a Fenwick tree exists
to fix).

## Related problems

- [Range Sum Query 2D - Immutable](https://leetcode.com/problems/range-sum-query-2d-immutable/)
  — not solved yet. The same idea in two dimensions, where a rectangle sum
  becomes an inclusion–exclusion of **four** prefix entries instead of two.
  The natural next step, and the leading zero row/column pays off even more
  there.
- [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/)
  — not solved yet. Identical interface plus an `update`, which destroys the
  precompute-once assumption and forces a Fenwick tree or segment tree. The
  cleanest illustration anywhere of what a single word in the problem title
  buys you.
- [Maximum Size Subarray Sum Equals k](https://leetcode.com/problems/maximum-size-subarray-sum-equals-k/)
  — not solved yet. Prefix sums combined with a hash map, which is the real
  power move: instead of answering a given range, you search for ranges with a
  target sum by looking up `prefix[j] - k`. Same array, far more interesting
  use.
- [Two Sum](../0001-two-sum/README.md) — already solved. Worth pairing
  mentally with the problem above: "seen a complement before?" via a hash map
  is exactly the technique that turns prefix sums from a lookup table into a
  search structure.
- [Sum of Variable Length Subarrays](https://leetcode.com/problems/sum-of-variable-length-subarrays/)
  — not solved yet. A direct application where each query's left endpoint is
  derived from the data; good drill for the `right + 1` offset becoming
  automatic.
