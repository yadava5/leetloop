# 167. Two Sum II - Input Array Is Sorted

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Two Pointers, Binary Search |
| **Solved** | 2026-09-16 |
| **Runtime** | 11 ms (5.50th percentile) |
| **Memory** | 22.3 MB (8.20th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/ |

## The problem

**Given** an array `numbers` sorted in **non-decreasing** order and an integer
`target`.

**Return** the positions of the two elements that sum to `target`, as a
two-element list `[index1, index2]` with `index1 < index2` — and crucially the
positions are **1-indexed**, not 0-indexed. You return indices, not the values.

**Guaranteed**, and all three promises are leaned on hard:

1. **`numbers` is sorted.** Without this the elimination argument below collapses
   entirely and the two-pointer sweep is simply wrong.
2. **Exactly one solution exists.** This is what licenses the function to have no
   `return` after the loop — the loop cannot finish without finding it.
3. **The same element may not be used twice.** Hence `left < right` rather than
   `left <= right`.

The extra follow-up that makes this a Medium rather than a repeat of *Two Sum*:
solve it in **constant extra space**. A hash map answers the question in O(n)
time but O(n) space, and the sortedness is the resource you are meant to spend
instead.

```text
def twoSum(self, numbers: list[int], target: int) -> list[int]
```

### Examples (mine, not LeetCode's)

| `numbers` | `target` | Returns | Why |
|---|---|---|---|
| `[1, 2, 3, 4]` | `5` | `[1, 4]` | The plain case, and the one that demonstrates the 1-indexing: `numbers[0] + numbers[3] = 5`, but the answer is `[1, 4]`. Returning `[0, 3]` is the single most common wrong answer. |
| `[-5, -2, 0, 3]` | `1` | `[2, 4]` | **Counterexample to any approach that assumes positive values** — for instance "shrink `right` while `numbers[right] > target`", which would immediately discard the `3` that the answer needs. Negatives are legal and the target may be smaller than an element in the pair. |
| `[2, 3, 4]` | `6` | `[1, 3]` | The pair straddles a middle element that is *itself* half the target. Confirms the sweep does not stop at the middle or accidentally pair `3` with itself. |
| `[1, 1]` | `2` | `[1, 2]` | **Edge case:** the minimum legal length, and two equal values. They are distinct *elements*, so this is valid — the rule forbids reusing one index, not using two equal values. The loop runs exactly once. |
| `[0, 0, 3, 4]` | `0` | `[1, 2]` | A zero target with duplicates. Also the shape that shows why the sweep converges from both ends rather than scanning: `right` walks all the way down from `3` to `1`. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `2 <= numbers.length <= 3 * 10^4` | The lower bound of **`2` means the array is never too short to contain a pair**, so `right = len(numbers) - 1` is always a valid index and `left < right` is satisfiable — no empty-or-singleton guard is needed. The upper bound is softer than it looks: **3 × 10⁴ makes O(n²) about 4.5 × 10⁸ pair sums, which is too slow in Python but not absurdly so**, and it makes O(n log n) binary search entirely comfortable. So the constraint alone does not force two pointers — what forces it is the problem's **O(1) extra space** follow-up, which rules out the hash map that would otherwise be the obvious O(n) answer. |
| `-1000 <= numbers[i] <= 1000` | Values may be **negative**, which rules out pruning heuristics that treat the array as positive (e.g. discarding any element greater than `target`). The range is also *tiny* — only 2001 distinct values against up to 3 × 10⁴ elements — so by pigeonhole the array is full of duplicates, which is why the duplicate-handling cases above are the realistic ones rather than the exotic ones. The magnitude also means `numbers[left] + numbers[right]` is bounded by 2000 in absolute value: no overflow concern in any language. |
| `-1000 <= target <= 1000` | The target is in the same small range and may be **negative or zero**, so nothing may assume `target > 0`. Combined with the value bound, a pair summing to `target` is always *representable*, but note the constraint says nothing about a solution existing — that promise comes from the problem statement, not from this list, and it is the promise the missing final `return` depends on. |

One honesty note about this table: the fetched `constraints` array contains only
these three bounds. Two further promises in the statement — that `numbers` is
sorted in non-decreasing order, and that exactly one solution exists — are not
in the list but are the two facts this solution most depends on. They are stated
under **Guaranteed** above rather than quoted here, because they were not
captured as constraints.

## Key insight

Start with the two extremes, and treat each comparison as an **elimination
proof** rather than a step of a search. If `numbers[left] + numbers[right]` is
below the target, then `numbers[left]` — the smallest value still in play — has
just been paired with the largest partner available to it and still fallen
short; every other partner is smaller, so `numbers[left]` cannot appear in *any*
solution and can be discarded forever. The symmetric argument discards
`numbers[right]` when the sum is too big. Each comparison therefore retires one
element permanently, so the whole search finishes in one pass.

Sortedness is what makes "the largest partner available" a fact you get for free
from an index rather than something you would have to compute.

## Approach

1. Put `left` at the first index and `right` at the last.
2. While `left < right`, compute `current = numbers[left] + numbers[right]`.
3. If `current == target`, return `[left + 1, right + 1]` — converting to
   1-indexed here and only here.
4. If `current < target`, advance `left`; the current `numbers[left]` is proved
   useless.
5. Otherwise retreat `right`; the current `numbers[right]` is proved useless.

Nothing in the loop body is order-sensitive, which is unusual and worth noticing
— the three cases are mutually exclusive. What *is* load-bearing is the
**starting positions**: the sweep must begin at the two extremes. Starting both
pointers in the middle, or at the same end, destroys the elimination argument,
because it is only at the extremes that "already paired with the largest/smallest
available partner" is true.

### Why it's correct

**Invariant**: if a solution exists at all, then at the top of every iteration
both of its indices lie inside `[left, right]`.

It holds initially, since `[left, right]` is the whole array. Suppose it holds
and the loop advances `left` because `current < target`. Let the solution be
`(a, b)` with `left <= a < b <= right`. Could `a == left`? Then
`numbers[left] + numbers[b] = target`, but `b <= right` and the array is sorted,
so `numbers[b] <= numbers[right]`, giving
`numbers[left] + numbers[b] <= current < target` — a contradiction. So
`a > left`, and the solution survives in `[left + 1, right]`. The `right`
branch is the mirror image, using `numbers[a] >= numbers[left]`. Therefore no
step can discard the solution, and since the loop only ends by returning or by
the pointers meeting, and the problem promises a solution exists, it must be
found.

Note where **sortedness** entered: in the inequality `numbers[b] <=
numbers[right]`. That single step is the entire dependence, and it is why the
same code on an unsorted array is not merely slower but wrong.

**Termination and the edge of the range.** Every iteration either returns or
moves exactly one pointer exactly one step towards the other, so `right - left`
strictly decreases and the loop runs at most `n - 1` times. The bound is
`left < right` and **not** `left <= right` because equality would mean pairing
an element with itself, which the problem forbids; it also means the last
iteration considers the pair `(left, left + 1)` and then, whichever branch it
takes, the pointers collide and the loop ends. Under the "exactly one solution"
guarantee the loop never reaches that exit — which is precisely why the function
has no `return` afterwards, and why it returns `None` if that guarantee is ever
violated.

The step I would flag as least likely to be reproduced correctly under pressure
is not the code but the contradiction above. It is easy to assert "the smallest
element can't be in any pair" and hard to notice that the proof needs
`numbers[b] <= numbers[right]` — that is, it needs the *other* pointer's
position, not just sortedness in the abstract.

## Solution

```python
# 167. Two Sum II - Input Array Is Sorted (Medium) - converge two pointers from the ends, moving whichever one the comparison proves useless. O(n) time, O(1) space.
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:

        # The pointers start at the two extremes, so the first sum considered
        # is the largest possible and the last is the smallest. Every move
        # shrinks the range by exactly one element.
        left = 0
        right = len(numbers) - 1

        # `left < right` and not `<=`: an element may not be paired with
        # itself, and at left == right that is the only pair left. The loop
        # therefore runs at most len(numbers) - 1 times, since each pass moves
        # one pointer one step towards the other.
        while left < right:
            current = numbers[left] + numbers[right]

            # The answer is 1-INDEXED, which is the difference from Two Sum I
            # that costs people a wrong answer. Hence the + 1 on both.
            if current == target:
                return [left + 1, right + 1]
            # Sum is short. numbers[left] is the smallest value still in play,
            # and it is already being paired with the LARGEST one available;
            # every remaining partner is <= numbers[right], so no pair using
            # numbers[left] can ever reach the target. Discarding it loses
            # nothing. This elimination argument is the whole proof, and it
            # depends entirely on the array being sorted.
            elif current < target:
                left += 1
            # Symmetrically: the sum is too big, numbers[right] is already
            # paired with the smallest available value, so it cannot appear in
            # any solution either.
            else:
                right -= 1

        # WART worth knowing about: there is no return after the loop, so this
        # function falls off the end and returns None if no pair exists. That
        # is unreachable on LeetCode - the problem guarantees exactly one
        # solution, which is found before the pointers meet - but it means the
        # function is not total, and copying it into code without that
        # guarantee will hand the caller a None to unpack.
```

[solution.py](solution.py) · [raw submission](../../data/raw/two-sum-ii-input-array-is-sorted.py)

## Why this approach

| Alternative | Cost | Why the converging pointers beat it |
|---|---|---|
| Brute force: every pair `(i, j)` with `i < j` | O(n²) time, O(1) space | ~4.5 × 10⁸ pair sums at `n = 3 × 10⁴`. Slow enough to TLE in Python, and it ignores the sortedness entirely — the one hint the problem title puts in capital letters. |
| Hash map from value to index, exactly as in *Two Sum I* | O(n) time, **O(n) space** | Correct, and the reflex if you have just done Two Sum. It is disqualified not by speed but by the problem's constant-space follow-up, and it is instructive that it is the *only* approach here that does not need the array sorted. The sortedness is precisely what lets you drop the map. |
| Binary search for `target - numbers[i]` for each `i` | O(n log n) time, O(1) space | Correct and comfortably fast at this size, so it is a legitimate answer rather than a straw man. It is just strictly more code — you must exclude `i` itself from the search range, and handle the duplicate values the tiny value range guarantees you will meet. Two pointers is O(n) with none of that. |
| Two pointers, but starting both in the middle and expanding | O(n) and **wrong** | Worth naming because it is a real instinct from palindrome problems. The elimination argument needs "paired with the most extreme partner available", which is false in the middle: a middle pair summing below the target tells you nothing, since a larger partner still exists on both sides. |
| Discard any element greater than `target` before starting | O(n) and **wrong** | A plausible-looking prune that the negative values kill. On `[-5, -2, 0, 3]` with `target = 1`, the `3` exceeds the target and would be thrown away — but it is half the answer, `[2, 4]`. Verified. |
| Sort first, then two pointers | O(n log n) and **wrong for this problem** | Not a complexity objection: sorting destroys the original positions, and the answer is a pair of *indices* into the given array. You would have to carry `(value, index)` pairs, at which point the space is no longer O(1). The array arriving pre-sorted is exactly what makes the index-returning version possible. |

## Complexity

- **Time — O(n)**. Each iteration retires one element, so there are at most
  `n - 1` iterations, each doing one addition and up to two comparisons. The
  11 ms is near the floor for reading the input; the 5.50th percentile is not a
  sign of a bad algorithm but of measurement noise at this scale, where faster
  submissions are mostly winning on interpreter start-up.
- **Space — O(1)**. Three integers — `left`, `right`, `current` — plus the
  two-element list that is the answer itself. This is the point of the problem;
  the hash-map solution is the same time bound at O(n) space.

## Pitfalls

- **Returning `[left, right]` instead of `[left + 1, right + 1]`.** The answer is
  1-indexed, and this is the difference from *Two Sum I* that the problem is
  really checking. `[1, 2, 3, 4]` with `target = 5` must give `[1, 4]`, not
  `[0, 3]`.
- **`while left <= right`.** Admits `left == right`, which pairs an element with
  itself. On `[3, 5]` with `target = 6` it would return `[1, 1]` — a pair that
  does not exist — rather than continuing. The problem forbids reusing an index.
- **Returning the values rather than the indices.** `[numbers[left],
  numbers[right]]` is a natural slip when the values are what you have been
  comparing.
- **Moving both pointers on a mismatch.** Each comparison proves exactly *one*
  element useless; moving the other discards an element you have no proof about.
  On `[1, 2, 3, 4, 5]` with `target = 9` the pointers go `(0,4) → (1,3) → ` meet,
  and the function falls out of the loop returning `None`, never having looked at
  the answer `[4, 5]`. Verified.
- **Applying this to an unsorted array.** Not slow — wrong. The proof uses
  `numbers[b] <= numbers[right]`, which is false without sortedness. This is the
  reason *Two Sum I* needs a hash map and this one does not.
- **The missing `return` after the loop.** If no pair exists the function returns
  `None`, and the caller gets a `TypeError` on unpacking rather than a clean
  "not found". Unreachable on LeetCode thanks to the exactly-one-solution
  promise, but this is a wart to know about before pasting the function anywhere
  that promise does not hold. It is also the kind of thing a linter will flag as
  an inconsistent-return warning.
- **Pruning on `numbers[i] > target`.** Breaks on negative values:
  `[-5, -2, 0, 3]` with `target = 1`.
- **Assuming distinct values.** With only 2001 possible values and up to 3 × 10⁴
  elements, duplicates are the norm. `[1, 1]` with `target = 2` is a valid input
  and its answer is `[1, 2]`.

## Redo from scratch

1. Say what the sortedness buys before writing anything: **at the extremes, each
   element is already paired with its best possible partner.**
2. `left = 0`, `right = len(numbers) - 1`. Extremes, not the middle.
3. `while left < right` — strict, because an element may not pair with itself.
4. Three-way compare: equal → return, too small → `left += 1`, too big →
   `right -= 1`.
5. **Add one to both indices on the way out.** Write the `+ 1`s at the same
   moment you write the `return`, not afterwards.
6. Test `[1, 1]` with `target = 2` (minimum length, duplicates), `[-5, -2, 0, 3]`
   with `target = 1` (negatives), and check the 1-indexing on anything.

Be able to justify out loud: **why advancing `left` cannot discard the answer** —
the contradiction argument, including the step that actually uses sortedness
(`numbers[b] <= numbers[right]`). If you can only say "because the array is
sorted", you have the slogan and not the proof, and the slogan will not tell you
whether the middle-out variant works. Second: **why `left < right` and not
`<=`**, in terms of the problem's rule rather than in terms of avoiding an
infinite loop.

## Related problems

- [Two Sum](../0001-two-sum/README.md) — already solved, and the direct
  comparison this problem exists to provoke: unsorted input, so the hash map is
  mandatory and costs O(n) space. Read the two pages together and be able to say
  which line of each proof the sortedness replaces.
- [3Sum](https://leetcode.com/problems/3sum/) — not solved yet, and the most
  valuable follow-up: sort, fix one element, then run *exactly this* two-pointer
  sweep on the remainder. This solution is a subroutine of that one, so the
  invariant above is worth over-learning.
- [Two Sum IV - Input is a BST](https://leetcode.com/problems/two-sum-iv-input-is-a-bst/)
  — not solved yet. The same converging sweep where "sorted order" is the in-order
  traversal of a tree, reached with two iterators instead of two indices. Good for
  seeing that the algorithm depends on *ordered access*, not on arrays.
- [Two Sum Less Than K](https://leetcode.com/problems/two-sum-less-than-k/) — not
  solved yet. Same setup, but you maximise a sum under a bound instead of hitting
  it exactly, so the `==` branch disappears and the `<` branch records a
  candidate before advancing. A one-line variation that tests whether you
  understood the elimination or memorised the shape.
- [Container With Most Water](https://leetcode.com/problems/container-with-most-water/)
  — not solved yet. The other canonical converging-pointer problem, and the one
  whose elimination argument (always move the *shorter* wall) is genuinely
  harder to justify than this one's. The natural next step once this proof feels
  routine.
- [Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/)
  — not solved yet. Two pointers from the ends of a sorted array again, but
  merging outwards rather than searching inwards. Cheap reinforcement that "sorted
  plus two pointers" is a family, not a single trick.
