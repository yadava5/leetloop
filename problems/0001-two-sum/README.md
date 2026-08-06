<!-- GENERATED. Problem restated in my own words; never LeetCode's text. -->

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

## Problem, restated

Given an array of integers and a target value, find the two entries that add up
to the target and return **their indices** — not the values. Exactly one such
pair exists, and a single element can't be used twice.

**Constraints that actually matter.** The array holds up to 10⁴ elements, so a
nested double loop is ~10⁸ operations — too slow in Python, and LeetCode's own
follow-up asks explicitly for better than O(n²). Values and the target range
over ±10⁹, which kills any idea of indexing into an array by value; the lookup
structure has to be a hash map, not a bucket array.

## Key insight

Flip the question around. The brute-force version asks *"which later element
pairs with this one?"*, which is a search. Instead ask *"have I already walked
past the number this element needs?"* — which is a lookup.

Keep a dict of `value -> index` as you go, and every element only ever needs to
look **backwards**, at things already in the dict. One pass is enough.

## Approach

1. `seen = {}` maps each value to the index it appeared at.
2. Walk the array once with `enumerate`, so the index comes along for free.
3. For each `num`, compute `comp = target - num` — the exact partner it needs.
4. If `comp` is already in `seen`, the pair is complete: return
   `[seen[comp], i]`, earlier index first.
5. Otherwise record `seen[num] = i` and keep going.

The ordering in steps 4 and 5 is the whole correctness argument: the lookup
happens against elements *strictly before* `i`, so an element can never pair
with itself.

*(Kept exactly as submitted, including `return[seen[comp], i]` with no space
after `return` — it parses identically and the annotation is not allowed to
touch code, only comment on it.)*

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Nested loops over all pairs | O(n²) time, O(1) space | At n = 10⁴ that's 10⁸ comparisons — TLE territory in Python, and the problem's follow-up rules it out by name. |
| Sort, then two pointers inward | O(n log n) time | Sorting destroys the original indices, which are what the answer asks for. You'd have to sort `(value, index)` pairs and carry the index along — more code, more to get wrong, and still slower than O(n). |
| Bucket array indexed by value | O(1) lookup | Values span ±10⁹. The array would be astronomically large. This is exactly the constraint that forces a hash map. |

## Complexity

- **Time — O(n).** One pass over the array; each iteration does a constant
  number of dict operations, which are O(1) on average.
- **Space — O(n).** In the worst case (the pair is at the very end) the dict
  holds n − 1 entries before the answer is found.

## Pitfalls

- **Inserting before looking up.** The classic wrong version writes
  `seen[num] = i` first, then checks. With `nums = [3, 5]` and `target = 6`,
  the 3 finds itself and you return `[0, 0]`.
- **Returning values instead of indices.** `[num, comp]` looks right and passes
  a mental test on `[2, 7]`; the judge wants `[0, 1]`.
- **Duplicate values.** `seen[num] = i` overwrites the older index. That's fine
  because only one valid answer exists — and if the answer *is* a duplicate pair
  (e.g. `[3, 3]`, target 6), the second 3 finds the first via the lookup before
  any overwrite matters.
- **Assuming the array is sorted.** It isn't, so two pointers can't be applied
  directly.

## Redo from scratch

Rebuild it cold, without reading the code:

1. Empty dict, mapping **value → index**.
2. `for i, num in enumerate(nums)`.
3. `comp = target - num`.
4. **Look up first:** if `comp in seen`, return `[seen[comp], i]`.
5. **Then insert:** `seen[num] = i`.
6. Fall through to `return []`.

Say out loud why step 4 must precede step 5. If you can explain that, you have
the problem; if you can't, you've memorised the code instead.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Two Sum II – Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) — the sorted version, where two pointers *do* beat a hash map on space.
- [3Sum](https://leetcode.com/problems/3sum/) — fix one element, then this problem on the rest.
- [Two Sum IV – Input is a BST](https://leetcode.com/problems/two-sum-iv-input-is-a-bst/) — same lookup trick over a tree traversal.
- [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — the same "have I seen what I need?" idea applied to prefix sums. This is the one that makes the pattern generalise.
- [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) — counting version with a multiset.
