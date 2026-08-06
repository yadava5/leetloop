<!-- GENERATED. Problem restated in my own words with my own examples; never
     LeetCode's text. The ```python block below is gated by
     scripts/verify_ast.py against data/raw/two-sum.py. -->

# 1. Two Sum

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table |
| **Solved** | 2026-08-05 |
| **Runtime** | 3 ms — beats 53.8% |
| **Memory** | 20.5 MB — beats 17.5% |
| **Language** | Python3 |
| **Problem** | <https://leetcode.com/problems/two-sum/> |

## The problem

**Given** an array of integers `nums` and an integer `target`.

**Return** the **indices** of the two elements that add up to `target` — the
positions, not the values — as a list of two integers. Either order is accepted.

**Guaranteed:**

- exactly one pair works, so there is never a tie to break and never a "no
  answer" case to report;
- the two indices must be **different**; a single element cannot be doubled to
  reach the target, even when `target == 2 * nums[i]`.

The array is **not** sorted, and nothing is promised about duplicates — the same
value may appear more than once.

**Signature:** `def twoSum(self, nums: List[int], target: int) -> List[int]`

### Examples (mine, not LeetCode's)

| `nums` | `target` | Answer | Why |
|---|---|---|---|
| `[8, 1, 5]` | `13` | `[0, 2]` | The pair isn't adjacent. The map has to remember `8` across an element that turns out to be irrelevant. |
| `[4, 1, 7]` | `8` | `[1, 2]` | **The counterexample.** At `i = 0` the complement of `4` is `4` itself. Record before you look up and this wrongly answers `[0, 0]`. |
| `[4, 4]` | `8` | `[0, 1]` | Equal values at *distinct* indices — legal, and the opposite of the case above. The two must not be confused. |
| `[6, -2, 9]` | `4` | `[0, 1]` | Negatives need no special handling; subtraction gets the sign right on its own. |
| `[-3, -5]` | `-8` | `[0, 1]` | The shortest legal input, with a negative target. Edge case: the loop must still find a pair on its second iteration. |

### Constraints, and what each one forces

*Recalled, not read: this environment has no network egress to leetcode.com, so
the constraints below are from memory rather than fetched from the problem page.
The consequences hold for the stated bounds; re-check the exact numbers against
the live page if a decision turns on them.*

| Constraint | Consequence |
|---|---|
| `2 <= len(nums) <= 10^4` | Never empty and never a single element, so there is no degenerate case to guard. At n = 10⁴ the brute-force double loop is ~5×10⁷ pair checks — seconds in pure Python, not milliseconds. That gap is what buys the hash map its O(n) space. |
| `-10^9 <= nums[i] <= 10^9` | Values are signed and wide. Python's arbitrary-precision ints mean `target - num` cannot overflow, but the range rules out any "index a bucket array by value" trick — the table has to be a hash map, not an array. |
| `-10^9 <= target <= 10^9` | The complement may be any integer at all, including one that never appears. The membership test therefore has to be a real lookup, not an assumption. |
| **Exactly one valid answer exists** | The constraint the code leans on hardest. It licenses returning on the very first hit, licenses letting a duplicate value overwrite its own earlier index in `seen`, and makes the trailing `return []` unreachable. |
| The same element may not be used twice | Forces the lookup to happen *before* the insert. This single ordering is the difference between correct and wrong. |
| Follow-up: do better than O(n²) | The problem is explicitly asking for this solution, not merely permitting it. |

## Key insight

Stop looking for *a pair*. Fix one element and ask a question about a single
value instead: "is `target - num` something I have already walked past?" That
converts a two-dimensional search into a one-dimensional membership test, and a
hash map answers membership in O(1). The second half of the insight is quieter
but does just as much work: because the map only ever holds elements strictly to
the left of the cursor, the requirement that the two indices differ is satisfied
for free — there is no `i != j` check anywhere in the code, and none is needed.

## Approach

1. `seen` is a dict mapping **value → index**, holding every element already
   passed. Values are the keys because the value is what you search by; the
   index is what you have to return.
2. Walk the array once with `enumerate`, so each step has both `i` and `num`.
3. Compute `comp = target - num`: the exact partner this element needs.
4. **Look up `comp` first.** If it is present, its stored index is strictly less
   than `i`, so `[seen[comp], i]` is a valid answer — return immediately.
5. **Only then insert `seen[num] = i`.** Steps 4 and 5 are the load-bearing
   ordering. Swapping them lets an element match itself whenever
   `target == 2 * num`, silently returning `[i, i]`.
6. If the loop finishes, return an empty list. Under this problem's guarantee
   that line never runs.

Note what step 5 does *not* do: it does not check whether `num` is already a key.
Overwriting is fine here — a later index is just as good a partner as an earlier
one, and the uniqueness guarantee means the discarded index was never going to be
part of the answer.

## Solution

My exact submission, with comments added and nothing else changed — the AST gate
proves it. Also at [`solution.py`](solution.py); raw at
[`../../data/raw/two-sum.py`](../../data/raw/two-sum.py).

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # value -> the index it was last seen at, covering only elements
        # strictly to the LEFT of the current one. That invariant is the whole
        # correctness argument: anything found in here is a different element,
        # never i itself.
        seen = {}

        for i, num in enumerate(nums):
            # The partner nums[i] would need. Computing it turns "search for a
            # pair" into "have I already passed this exact value?" - a question
            # a dict answers in O(1) instead of an inner loop.
            comp = target - num

            if comp in seen:
                # seen[comp] is strictly less than i, so the two indices are
                # distinct, which the problem requires. (No space after
                # `return`: this is `return [a, b]`, a list literal, not an
                # index expression. Preserved exactly as submitted.)
                return[seen[comp], i]
            # ORDER IS LOAD-BEARING: record num only AFTER the lookup above.
            # Insert first and nums = [4, 1, 7] with target 8 matches the 4
            # against itself and answers [0, 0].
            seen[num] = i
        # Unreachable given the problem's promise that exactly one pair exists;
        # a defensive fallback so every path returns a list.
        return []
```

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Brute force: nested loops over every `i < j` | O(n²) time, O(1) space | Correct, but ~5×10⁷ iterations at n = 10⁴ in interpreted Python. The follow-up rules it out by name; trading O(n) space for that factor is the entire point of the problem. |
| Sort, then converge two pointers from both ends | O(n log n) time, O(n) space | **Wrong as written**, not merely slower: sorting destroys the indices, and indices are what you must return. Fixing it means sorting `(value, index)` pairs and reading the index back out — more code, more space, and still worse than O(n). |
| Two passes: build the complete dict first, then rescan for complements | O(n) time, O(n) space | Correct only with an extra `seen[comp] != i` guard, because the dict now contains the current element too. And that guard alone still breaks on `[4, 4]` with target `8`: the dict maps `4 → 1` only, so the check rejects the sole valid pair. Same asymptotics, two more ways to be wrong. |
| A `set` of seen values instead of a dict | O(n) time, O(n) space | Tells you the complement exists but not *where*. The answer is positions, so the index has to be stored, and once you store it you have a dict. |
| Sort and binary-search each complement | O(n log n) time | Strictly dominated: slower than the hash map and it still has the index-destruction problem. |

## Complexity

- **Time — O(n).** One pass; each iteration does one subtraction, one dict
  membership test and one dict insert, all O(1) on average. A pathological hash
  collision cascade would be the only way to degrade this, and Python's dict
  makes that a non-concern for integer keys.
- **Space — O(n).** `seen` grows by one entry per element examined. The worst
  case is the answer being the last two elements, leaving n − 2 entries in the
  map before the return fires.

## Pitfalls

- **Inserting before looking up.** The one bug that matters. `[4, 1, 7]` with
  target `8`: at `i = 0`, `comp = 4`; if `seen[4] = 0` already happened, the
  lookup succeeds against the element itself and returns `[0, 0]`. The correct
  answer is `[1, 2]`. Note this fails *silently* — no exception, just a wrong
  pair.
- **Confusing "same element twice" with "same value twice".** `[4, 4]` with
  target `8` is a perfectly legal input and the answer is `[0, 1]`. Only reusing
  one *index* is forbidden. A fix for the previous pitfall that tests values
  instead of indices breaks this case.
- **Returning the values instead of the indices.** `[4, 4]` for the case above
  is a plausible-looking wrong answer that a quick eyeball check will not catch.
- **Assuming the array is sorted.** It isn't. Any two-pointer instinct has to be
  suppressed or paid for with a sort.
- **`List` is never imported.** LeetCode injects `from typing import List` into
  its own harness; this file doesn't have it, so running `solution.py`
  standalone raises `NameError` while evaluating the annotations at class
  definition time. That is a property of the submitted code, preserved
  deliberately — the AST gate parses rather than executes, so it is unaffected.
- **`return[...]` with no space** is legal Python and parses as a list literal,
  but it reads like an index expression at a glance. Kept exactly as submitted;
  `return [seen[comp], i]` is the better habit.
- **The trailing `return []` is a silent failure mode in any variant** where a
  pair might genuinely not exist. Here the guarantee makes it dead code, but
  copied into a looser problem it answers "no pair" instead of surfacing a bug.

## Redo from scratch

Rebuild it cold, without reading the code:

1. `seen = {}` — a dict of **value → index**, not index → value.
2. `for i, num in enumerate(nums):`.
3. `comp = target - num`.
4. If `comp in seen`: `return [seen[comp], i]`.
5. **Then** `seen[num] = i`. Never before step 4.
6. `return []` after the loop.

Be able to justify out loud: why steps 4 and 5 cannot be swapped, and what
concrete input punishes you if they are; why no `i != j` check is needed anywhere
despite the problem explicitly forbidding index reuse; and why overwriting a
duplicate key in `seen` is safe here but would not be if the problem asked for
*all* pairs.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Two Sum II — Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) — the direct contrast: sortedness replaces the hash map with two pointers and drops space to O(1). Doing both back to back shows exactly what the map was buying.
- [3Sum](https://leetcode.com/problems/3sum/) — fix one element, run Two Sum on the remainder. The new difficulty isn't the search, it's deduplicating the results.
- [4Sum](https://leetcode.com/problems/4sum/) — generalizes the same peeling into k-Sum, recursing down to a two-pointer base case.
- [Two Sum III — Data Structure Design](https://leetcode.com/problems/two-sum-iii-data-structure-design/) — the same trick amortized over many queries, which forces a real decision about whether `add` or `find` should carry the cost.
- [Two Sum IV — Input is a BST](https://leetcode.com/problems/two-sum-iv-input-is-a-bst/) — a set of seen values over a traversal, proving the technique was never about arrays.
- [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — the best follow-up here. Same complement idea, but applied to *prefix sums* rather than raw values; internalizing that jump is what makes "store what you've already seen" a reusable tool instead of a memorized trick.
- [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) — counting pairs greedily with a multiset instead of returning one, so the overwrite shortcut used above stops being safe.
- [Count Pairs Whose Sum is Less Than Target](https://leetcode.com/problems/count-pairs-whose-sum-is-less-than-target/) — an inequality instead of an equality, which kills hashing outright and hands the problem back to sorting.
