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

**Return** the two positions in the array whose values add up to `target` — the
**indices**, not the values. Any order.

**Guaranteed** by the problem: exactly one pair works, and you may not use the
same element twice (so `nums[i] + nums[i]` doesn't count).

**Signature:** `def twoSum(self, nums: List[int], target: int) -> List[int]`

### Examples (mine, not LeetCode's)

| `nums` | `target` | Answer | Why |
|---|---|---|---|
| `[4, 11, 2, 7]` | `9` | `[2, 3]` | `nums[2] + nums[3]` = `2 + 7` = `9` |
| `[3, 3]` | `6` | `[0, 1]` | the two equal values are different elements, which is allowed |
| `[-8, 5, 1]` | `-7` | `[0, 2]` | negatives are in range, so don't assume positives |

### Constraints, and what each one forces

| Constraint | Consequence |
|---|---|
| `2 <= len(nums) <= 10^4` | Checking all pairs is ~10⁸ operations at the top end — too slow in Python. LeetCode's own follow-up asks for better than O(n²), so the quadratic answer is explicitly not the intended one. |
| `-10^9 <= nums[i] <= 10^9` | The value range is astronomically wider than the array. Any "index a bucket array by value" idea is dead; the lookup structure has to be a hash map. |
| `-10^9 <= target <= 10^9` | `target - num` can't overflow anything in Python, so no defensive arithmetic is needed. |
| Exactly one valid answer | You may return the instant you find a pair — no need to compare candidates or handle ties. |

## Key insight

Flip the question around. Brute force asks *"which later element pairs with this
one?"*, which is a search. Instead ask *"have I already walked past the number
this element needs?"* — which is a lookup.

Keep a dict of `value -> index` as you go, and each element only ever looks
**backwards** at what's already recorded. One pass is enough.

## Approach

1. `seen = {}` maps each value to the index where it appeared.
2. Walk the array once with `enumerate`, so the index comes along for free.
3. For each `num`, compute `comp = target - num` — the exact partner it needs.
4. If `comp` is already in `seen`, the pair is complete: return
   `[seen[comp], i]`, earlier index first.
5. Otherwise record `seen[num] = i` and continue.

The order of steps 4 and 5 *is* the correctness argument: the lookup only ever
sees elements strictly before `i`, so an element can never pair with itself.

## Solution

My exact submission, with comments added and nothing else changed — the AST gate
proves it. Also at [`solution.py`](solution.py); raw at
[`../../data/raw/two-sum.py`](../../data/raw/two-sum.py).

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # value -> index, for every element walked so far. The whole trick is
        # storing values as keys: the question "is the partner I need already
        # behind me?" becomes a dict lookup instead of a scan.
        seen = {}

        for i, num in enumerate(nums):
            # The exact value that would complete the pair with `num`.
            comp = target - num

            # Look BEFORE inserting. If this ran after the insert below, an
            # element would find itself whenever target == 2 * num.
            if comp in seen:
                # seen[comp] is the earlier index, i is the current one.
                return[seen[comp], i]

            # Not a match, so remember this element for later elements to find.
            # A duplicate value overwrites the older index, which is safe here:
            # the problem guarantees exactly one valid answer.
            seen[num] = i

        # Unreachable given that guarantee, but it keeps the declared
        # List[int] return type honest.
        return []
```

`return[seen[comp], i]` has no space after `return`. It parses identically —
`return [...]` and `return[...]` are the same AST — and annotation is not allowed
to touch code, only comment on it.

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Nested loops over all pairs | O(n²) time, O(1) space | At n = 10⁴ that's ~10⁸ comparisons — TLE territory in Python, and the follow-up rules it out by name. |
| Sort, then two pointers inward | O(n log n) time | Sorting destroys the original indices, which are exactly what the answer asks for. You'd have to sort `(value, index)` pairs and carry indices along — more code, more to get wrong, still slower than O(n). |
| Bucket array indexed by value | O(1) lookup | Values span ±10⁹, so the array would be absurd. This constraint is precisely what forces a hash map. |

## Complexity

- **Time — O(n).** One pass; each iteration does a constant number of dict
  operations, which are O(1) on average.
- **Space — O(n).** Worst case (pair at the very end) the dict holds n − 1
  entries before the answer is found.

## Pitfalls

- **Inserting before looking up.** The classic wrong version writes
  `seen[num] = i` first, then checks. On `nums = [3, 5]`, `target = 6`, the 3
  finds itself and you return `[0, 0]`.
- **Returning values instead of indices.** `[num, comp]` looks right and even
  reads correctly on `[2, 7]`; the judge wants `[0, 1]`.
- **Duplicate values.** `seen[num] = i` overwrites the older index. Safe here —
  and if the answer *is* a duplicate pair like `[3, 3]` with target 6, the second
  3 finds the first via the lookup before any overwrite matters.
- **Assuming sorted input.** It isn't, so two pointers can't be applied directly.
- **Reaching for `nums.index(comp)`** instead of a dict. That's an O(n) scan
  inside the loop, which quietly rebuilds the O(n²) solution.

## Redo from scratch

Rebuild it cold, without reading the code:

1. Empty dict, mapping **value → index**.
2. `for i, num in enumerate(nums)`.
3. `comp = target - num`.
4. **Look up first:** if `comp in seen`, return `[seen[comp], i]`.
5. **Then insert:** `seen[num] = i`.
6. Fall through to `return []`.

Be able to justify out loud: why step 4 must precede step 5, and why a hash map
rather than sorting. If you can do both, you have the problem; if not, you've
memorised the code.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Two Sum II – Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) — the sorted version, where two pointers *do* beat a hash map, on space.
- [3Sum](https://leetcode.com/problems/3sum/) — fix one element, then run this problem on the rest.
- [Two Sum IV – Input is a BST](https://leetcode.com/problems/two-sum-iv-input-is-a-bst/) — the same lookup trick layered over a tree traversal.
- [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — "have I seen what I need?" applied to prefix sums. This is the one that makes the pattern generalise; do it next.
- [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) — counting variant, where the map holds multiplicities instead of indices.
