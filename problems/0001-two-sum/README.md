# 1. Two Sum

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table |
| **Solved** | 2026-08-05 |
| **Runtime** | 3 ms (53.83rd percentile) |
| **Memory** | 20.5 MB (17.52nd percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/two-sum/ |

## The problem

**Given** an integer array `nums` and an integer `target`. The array is not
sorted, may contain duplicates, and may contain negative numbers.

**Return** the two *indices* — not the values — of the two entries that add up
to `target`, as a list of two integers. Either order is accepted. You return
positions into the original array, so sorting the input destroys the very thing
you are asked to report.

**Guaranteed**: `Only one valid answer exists.` — that one is quoted from the
problem's own constraints, and the solution leans on it directly: it is what
makes returning on the first hit correct rather than greedy, and it is why the
fall-through `return []` can never fire. A second promise, that the same element
may not be used twice, is *recalled* rather than read — it is phrased as prose
in the statement and so is not in the fetched `constraints` array. It is what
the lookup-before-insert ordering enforces.

```text
def twoSum(self, nums: List[int], target: int) -> List[int]
```

### Examples (mine, not LeetCode's)

Every row below respects the guarantee: exactly one pair sums to the target.

| `nums` | `target` | Returns | Why |
|---|---|---|---|
| `[8, 2, 5, 1]` | `7` | `[1, 2]` | The ordinary case: the partner of `2` shows up later, at index 2. |
| `[4, 4]` | `8` | `[0, 1]` | Two *equal* values are a legal pair as long as the indices differ. A `set` instead of a dict loses the index; refusing to overwrite a repeated key loses nothing here, but see the duplicates pitfall. |
| `[5, 3, 7]` | `10` | `[1, 2]` | **Counterexample to insert-before-check.** `10 == 2 × 5`, so if index 0 were stored before its complement was looked up, the `5` would answer its own query and return `[0, 0]` — never even reaching the real pair at indices 1 and 2. |
| `[-4, 11, 1]` | `-3` | `[0, 2]` | Negatives work unchanged — the complement is arithmetic, not magnitude, so no `abs` or sign handling is needed. |
| `[6, 1]` | `7` | `[0, 1]` | **Edge case:** the minimum legal input size, `nums.length == 2`. The loop finds the answer on its second and final iteration. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `2 <= nums.length <= 10^4` | The lower bound means you never handle an empty or single-element array — no special-casing. The upper bound is the real signal: brute force is ~10^4 × 10^4 / 2 = 5×10^7 pair checks, which Python does in seconds rather than milliseconds. It would likely squeak past the judge, but it is the wrong answer to the question being asked; O(n) is expected. |
| `-10^9 <= nums[i] <= 10^9` | Values can be negative, so no counting-array or bucket trick indexed by value. Python ints are arbitrary precision, so `target - num` cannot overflow — a genuine hazard in C++/Java, where the difference reaches 2×10^9 and escapes a signed 32-bit int. Nothing here needs a wider type. |
| `-10^9 <= target <= 10^9` | Same story: the complement `target - num` ranges over ±2×10^9 and is safe in Python. It also rules out assuming a positive target and pruning by "this value already exceeds target". |
| `Only one valid answer exists.` | The most load-bearing line on the page. Because the answer is unique, the *first* pair the loop finds is *the* pair — no collecting candidates, no tie-break, no "best" pair to choose between. It also means there is no not-found case to design, which is why the trailing `return []` is dead code rather than a real branch. Drop this promise and the problem becomes [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/), where the bookkeeping this problem lets you skip is the entire exercise. |

## Key insight

You are not searching for *a pair*; you are, for each element, searching for
*one specific number* — `target - num`. That reframing turns an O(n²) search
over pairs into n O(1) lookups, because "is this exact value present, and where
was it?" is precisely what a hash map answers. Walk once, and for each element
ask whether the number that would complete it has already gone by.

## Approach

1. Create an empty dict `seen`, mapping value → the index it appeared at. Its
   invariant: it holds only elements strictly to the left of the current index.
2. Walk the array with `enumerate`, so you carry both the index and the value.
3. Compute `comp = target - num`, the one number that would complete this pair.
4. **Check `comp in seen` before inserting `num`.** This order is load-bearing.
   Insert first and an element can match itself whenever `target == 2 * num`,
   returning `[i, i]`. Checking first means everything in `seen` is at a strictly
   smaller index, so the two indices are distinct by construction — no `i != j`
   guard needed anywhere.
5. On a hit, return `[seen[comp], i]`: the earlier index first, then the current
   one. Returning immediately is correct because exactly one answer exists.
6. Otherwise record `seen[num] = i` and continue. Overwriting a duplicate value's
   older index is harmless — had that older index been part of the answer, step 5
   would already have fired.
7. Fall through to `return []`, unreachable on valid input.

## Solution

```python
# 1. Two Sum (Easy) - one pass hash map of value -> index. O(n) time, O(n) space.
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # seen maps a value we have already walked past -> the index it sat at.
        # Only values to the LEFT of the current index ever live in here, which
        # is what makes "found a partner" automatically mean "two distinct
        # indices" without any i != j check.
        seen = {}

        for i, num in enumerate(nums):
            # The exact other number that would complete the pair with num.
            # Searching for a known value in a dict is O(1); searching for
            # "some pair that sums to target" by scanning is O(n).
            comp = target - num

            # ORDER IS LOAD-BEARING: look up comp BEFORE inserting num.
            # If num were inserted first, an element would find itself whenever
            # target == 2 * num. On nums = [5, 3, 7], target = 10 the insert
            # first version returns [0, 0] at i = 0, because the 5 it just
            # stored answers its own lookup - and never reaches the real pair
            # 3 + 7 at indices 1 and 2. Checking first makes that impossible.
            if comp in seen:
                # seen[comp] is the earlier index, i is the current one, so the
                # pair comes back in ascending order. Returning here also means
                # the loop stops at the first valid pair, which the constraints
                # state is safe: "Only one valid answer exists."
                return[seen[comp], i]
            # Insert AFTER the check. A duplicate value overwrites the older
            # index; harmless, because if the older index were part of the
            # answer the loop would already have returned at that point.
            seen[num] = i
        # WART worth knowing: unreachable for any valid LeetCode input, since
        # the constraints guarantee an answer exists. It is here to satisfy the
        # declared -> List[int] return type on the fall-through path. If this
        # ever fires in your own testing, the input violated that guarantee.
        return []
```

[solution.py](solution.py) · [raw submission](../../data/raw/two-sum.py)

## Why this approach

| Alternative | Cost | Why the hash map beats it |
|---|---|---|
| Nested loops over every pair `(i, j)` | O(n²) time, O(1) space | At `n = 10^4` that is 5×10^7 comparisons — seconds in Python, versus milliseconds. It is not *wrong*, just the answer the problem is designed to move you off of. The hash map trades O(n) memory for the whole inner loop. |
| Sort, then two pointers from both ends | O(n log n) time, O(n) space | **Wrong as stated**, not merely slower. Sorting destroys the indices you were asked to return, so you must first pair each value with its original position and sort the pairs — at which point you have paid O(n log n), used O(n) space anyway, and written more code than the dict version. It is the right tool for [Two Sum II](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/), where the input arrives sorted and the O(1) space actually materialises. |
| Two passes: build the whole dict, then scan for complements | O(n) time, O(n) space | Same asymptotics, and it *is* correct — but only once you add an explicit `seen[comp] != i` guard, because every value is now in the map before you query it, so `target == 2 * num` matches an element with itself. Without the guard, `[-3, -4, -2]` with `target = -6` returns `[0, 0]` instead of `[1, 2]`. With the guard it is fine, including on duplicates like `[4, 4]`/`8` — the map keeps the *later* index, so scanning from the left finds `[1, 0]`, and either order is accepted. The one-pass version wins not on complexity but because it needs no guard at all: the ordering makes self-pairing unreachable rather than detected-and-rejected, and there is one traversal instead of two. |
| `collections.Counter` / frequency map | O(n) time, O(n) space | Counts tell you a complement *exists* but not *where*. You would have to scan again to recover the index, which is the two-pass approach with extra steps. |

## Complexity

- **Time — O(n).** One pass over `nums`; each iteration does a constant number
  of dict operations, and average-case dict lookup and insert are O(1).
  (Worst-case hashing is O(n) per probe under adversarial collisions, which is
  not a realistic concern for Python ints on LeetCode.) Early return only helps.
- **Space — O(n).** `seen` grows by at most one entry per element, so it holds
  up to `n` entries when the answer is at the very end. Nothing else scales with
  input size. The 17th-percentile memory reading is exactly this trade: the O(n²)
  scan would rank higher on memory and far worse on time.

## Pitfalls

- **Inserting before checking.** The single classic bug. `nums = [5, 3, 7]`,
  `target = 10`: insert `5` at index 0, then look up `10 - 5 == 5`, find the
  entry you just wrote, and return `[0, 0]` — one element used twice, and the
  genuine answer `[1, 2]` never reached. Always look up the complement first.
- **Returning values instead of indices.** `[3, 7]` instead of `[1, 2]`. The
  return type is the same shape, so it passes the type checker and fails the
  judge.
- **Adding a needless `i != j` guard.** Not wrong, but it signals you have not
  seen *why* the check-then-insert ordering already makes it impossible, and it
  hides the real bug if you also flip the order.
- **Assuming values are distinct.** `[4, 4]` with `target = 8` is legal input.
  Storing values in a set instead of a dict, or refusing to overwrite an existing
  key, breaks the duplicate case.
- **"Simplifying" the overwrite away.** `seen[num] = i` deliberately clobbers an
  earlier index for the same value, and that looks like a lost answer. It is not:
  if the earlier index had been half the answer, the loop would have returned
  before reaching this element. Guarding the write with `if num not in seen` is
  also correct, but only by accident — it is extra code defending against a case
  the ordering already rules out.
- **Breaking out of the loop and returning after it.** Works, but you then have
  to keep the two indices in variables and reason about the not-found case.
  Returning inside the loop is shorter and has fewer states.
- **Reaching for sorting because the array "looks" like a two-pointer problem.**
  It is unsorted *and* index-returning; both point away from that.

## Redo from scratch

1. Empty dict `seen`, mapping **value → index**. Say the direction out loud
   before you type it — reversing it is the fastest way to lose five minutes.
2. `for i, num in enumerate(nums):`.
3. `comp = target - num`.
4. **Look up `comp` first**, then insert `num`. If you write these in the other
   order, you have written the self-pairing bug.
5. On a hit return `[seen[comp], i]`; otherwise `seen[num] = i`.
6. `return []` after the loop to satisfy the return type.

Be able to justify out loud:

- **Why no `i != j` check is needed.** Because `seen` only ever contains indices
  strictly less than the current `i`, so a hit is always two different positions.
  Then give the concrete input that breaks if you insert first: `[5, 3, 7]`,
  `target = 10`.
- **Why sorting is disqualified rather than just slow.** The answer is indices
  into the original array, and sorting throws those away.

## Related problems

- [Two Sum II — Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) — not solved yet. The same question with the input pre-sorted, which unlocks the O(1)-space two-pointer walk. Solving it directly after this one is the cleanest way to internalise *why* sortedness is what buys you the space saving.
- [3Sum](https://leetcode.com/problems/3sum/) — not solved yet. The natural escalation: fix one element, then run a two-sum on the rest. It adds the duplicate-skipping problem, which this version dodges entirely because only one answer exists.
- [4Sum](https://leetcode.com/problems/4sum/) — not solved yet. Generalises 3Sum to k-sum recursion; teaches when the hash-map trick stops paying and sorting takes over.
- [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — not solved yet. The most valuable follow-up here. It is the same "store what I have seen, look up the complement" move, but over *prefix sums* rather than raw values — the step that turns this trick from a one-problem gimmick into a general technique.
- [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) — not solved yet. Drops the "Only one valid answer exists." guarantee and asks you to consume pairs greedily, so the count-and-decrement bookkeeping this problem lets you skip becomes the whole exercise.
- [Two Sum IV — Input Is a BST](https://leetcode.com/problems/two-sum-iv-input-is-a-bst/) — not solved yet. Same complement-lookup idea over a tree traversal; good for checking whether you learned the *pattern* or just memorised the array loop.
- [Two Sum III — Data Structure Design](https://leetcode.com/problems/two-sum-iii-data-structure-design/) — not solved yet. Reframes it as an API where adds and queries interleave, forcing you to decide which of the two operations should carry the cost.

*None of the related problems above are in this repo yet.*
