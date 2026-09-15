# 283. Move Zeroes

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Two Pointers |
| **Solved** | 2026-09-14 |
| **Runtime** | 3 ms (81.85th percentile) |
| **Memory** | 20.5 MB (25.35th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/move-zeroes/ |

## The problem

**Given** an integer array `nums`.

**Return** nothing. Modify `nums` **in place** so that every `0` is moved to
the end of the array, while the **relative order of the non-zero elements is
preserved**. The array's length does not change — zeros are relocated, not
removed.

That order-preservation clause is the whole problem. Without it, this is a
two-line swap-from-both-ends exercise; with it, you need a stable compaction.

**Guaranteed**: nothing beyond the constraints. In particular the array is
*not* sorted and may be all zeros, no zeros, or anything between.

```text
def moveZeroes(self, nums: List[int]) -> None
```

### Examples (mine, not LeetCode's)

| `nums` (before → after) | Why |
|---|---|
| `[4, 0, 7] → [4, 7, 0]` | The ordinary case: one zero migrates to the back, `4` and `7` keep their order. |
| `[6] → [6]` | **Edge case:** single non-zero element. Pass 1 writes `nums[0] = 6` (a self-assignment), `write` becomes `1`, and pass 2's `range(1, 1)` is empty. Nothing happens, correctly. |
| `[0, 0, 0] → [0, 0, 0]` | **Edge case:** all zeros. Pass 1 copies nothing and leaves `write` at `0`; pass 2 then rewrites every slot from index `0`. The array is overwritten with the same values it already had — wasteful but correct. |
| `[3, 0, 0, 5] → [3, 5, 0, 0]` | **Counterexample to the naive "swap each zero with the element after it" approach.** That method walks `[3, 0, 0, 5]`, swaps index 1 and 2 (both zeros, no change), then swaps index 2 and 3 to get `[3, 0, 5, 0]` — and the scan has moved past index 1, so the zero stranded there never advances again. Runs of consecutive zeros are what break single-swap approaches. |
| `[0, 1, 0, 2] → [1, 2, 0, 0]` | Leading zero plus interleaving. Non-zeros `1` and `2` must come out in that order, not `2, 1` — this is the case that fails if you "optimize" by swapping the zero with the last non-zero from the back. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 10^4` | The array is never empty, so neither pass needs an emptiness guard — `write` always ends up somewhere valid. At 10,000 elements, an O(n²) approach is about 10⁸ operations, which is too slow in Python and rules out the `pop`/`insert` family that shifts the array on every zero. Two linear passes are trivially fast here; the real pressure is the in-place requirement, not the size. |
| `-2^31 <= nums[i] <= 2^31 - 1` | Full signed 32-bit range, which matters mostly for what it **does not** let you do: you cannot pick a sentinel value to mark "this slot was a zero," because every representable 32-bit integer is a legitimate input value. Any solution that needs a marker has to find one outside the value domain, and there isn't one. It also means negative numbers are ordinary non-zero elements — a truthiness test like `if num:` works (only `0` is falsy among ints), but `if num > 0:` would silently drop every negative. |

## Key insight

Stop thinking about moving zeros. Think about **compacting the non-zeros
forward**, and then the zeros are simply whatever is left over. Once the
non-zeros are packed into the front in order, the count of remaining slots
*is* the number of zeros, so you never have to count them.

## Approach

1. `write = 0` — the next slot that will receive a non-zero value.
2. **Pass 1:** walk every element. When it is non-zero, write it to
   `nums[write]` and advance `write`. Zeros are skipped entirely.
3. After pass 1, `nums[0:write]` holds every non-zero value in its original
   order, and `nums[write:]` is stale leftover data — copies of values that
   were already relocated.
4. **Pass 2:** overwrite `nums[write]` through the end with `0`.

The order of the two passes is load-bearing in the obvious direction (you
cannot zero the tail before you know where the tail starts), but the subtler
point is that pass 1 *must not* also write zeros as it goes. Writing a zero at
the read cursor's position mid-pass is how the single-pass swap variants get
themselves into trouble.

### Why it's correct

**Invariant** for pass 1, true before and after every iteration:
`nums[0:write]` contains exactly the non-zero elements of the portion already
visited, in their original relative order. It holds vacuously at the start
(`write == 0`, nothing visited). Each iteration either appends the current
element to that prefix (when non-zero) or skips it (when zero); appending at
the end is what preserves relative order, since elements are visited
left to right.

**The in-place write is safe** — and this is the one thing genuinely worth
checking, because pass 1 iterates by value (`for num in nums`) over the very
list it is writing into. The guarantee is that `write` never exceeds the
implicit read position: both start at `0`, and `write` advances only on
iterations where the read cursor also advances, so `write <= read` always.
Every write therefore lands at or behind the element currently being read,
never ahead of it, so no unvisited element is ever clobbered. When
`write == read` (an array with no zeros yet) the assignment is a self-copy.

Worth being explicit that this is an argument about *Python's* `for num in
nums`, which reads `nums[i]` fresh on each step from the live list rather than
from a snapshot. The invariant is what makes that safe; it is not safe in
general to mutate a list while iterating it.

**Termination and the edge of the range**: both loops are over finite ranges,
so termination is not in question. The interesting bound is pass 2's
`range(write, len(nums))`. It starts at `write` — the first slot *not* claimed
by a non-zero — and runs to `len(nums)` exclusive, so it covers exactly the
`n - write` trailing slots. Starting at `write + 1` would leave one stale
value in place; starting at `write - 1` would destroy the last non-zero. The
count is never computed explicitly, which is why there is no off-by-one to get
wrong: the range is defined by the boundary, not by a tally of zeros.

## Solution

```python
# 283. Move Zeroes (Easy) - two passes: compact the non-zeros forward, then fill the tail with zeros. O(n) time, O(1) space.
class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # `write` is the next slot to receive a non-zero value. Everything
        # left of it is already final.
        write = 0

        # Pass 1: copy every non-zero forward, in the order encountered.
        # Iterating by VALUE (`for num in nums`) rather than by index is safe
        # here only because writes always land at or behind the read cursor -
        # write <= the implicit read position at all times, so a write can
        # never clobber an element this loop has not yet visited.
        for num in nums:

            if num != 0:
                nums[write] = num
                write += 1
            
        # Pass 2: everything from `write` to the end is stale leftover data,
        # so overwrite it with zeros. The count is implicit - however many
        # slots remain is exactly how many zeros were skipped in pass 1.
        for i in range(write, len(nums)):
            nums[i] = 0
        # WART: the signature says `-> None` and the docstring says do not
        # return anything. Returning nums is harmless (LeetCode ignores the
        # return value and the mutation is what is graded) but it contradicts
        # the declared contract. Do not rely on this return value.
        return nums
```

[solution.py](solution.py) · [raw submission](../../data/raw/move-zeroes.py)

## Why this approach

| Alternative | Cost | Why the two-pass compaction beats it |
|---|---|---|
| `nums[:] = [x for x in nums if x != 0] + [0] * nums.count(0)` | O(n) time, O(n) extra space | Correct, and arguably the clearest one-liner, but it builds two new lists. The `nums[:] =` slice assignment does mutate in place, so it satisfies the letter of "in place" while allocating O(n) — which is what the problem is actually trying to prevent. |
| Single pass swapping `nums[write]` and `nums[read]` whenever `nums[read]` is non-zero | O(n) time, O(1) space | **Also correct**, and strictly better in one respect: it touches each slot once instead of writing the tail twice, so it does fewer writes when the array is mostly zeros. The version here is easier to prove right (the tail is unconditionally zeroed rather than relying on the swap having deposited a zero in the right place), but the swap variant is the one to know for interviews, since it answers the "can you do it in one pass?" follow-up directly. |
| `nums.remove(0)` in a loop, appending a `0` each time | O(n²) time | `list.remove` scans for the value and then shifts every later element left, so an array of 10,000 zeros does ~10⁸ element moves. It also mutates length mid-iteration, which makes the loop bounds treacherous. |
| Sort with a key that pushes zeros last (`nums.sort(key=lambda x: x == 0)`) | O(n log n) time | Works, and Python's stable sort even preserves the relative order of non-zeros — a genuinely cute solution. But it is asymptotically worse for no reason, and it leans on sort stability in a way that is easy to state wrongly. |
| Swap each zero with the element to its right, scanning forward | O(n) time | **Wrong**, not just slow. Runs of consecutive zeros defeat it: on `[3, 0, 0, 5]` it yields `[3, 0, 5, 0]` because after swapping the zero at index 1 rightward, the scan has already advanced past the position that zero landed in. |

## Complexity

- **Time — O(n)**. Two independent passes, each visiting at most `n`
  positions, with constant work per position. The passes are sequential, not
  nested, so the total is `2n` element visits — still linear.
- **Space — O(1)**. One integer for `write` and one for the pass-2 loop
  variable. The array is rewritten in place and nothing is allocated whose
  size depends on `n`.

## Pitfalls

- **Returning early, or returning a new list.** The grader inspects the
  *mutated* `nums`. Building the right list and returning it — `return [x for
  x in nums if x] + [0] * ...` — scores zero, because the caller's array was
  never touched. This is the single most common way to fail this problem.
- **The `return nums` in this code is a contract violation, not a feature.**
  The signature says `-> None`. It passes because LeetCode ignores the return
  value, but if you redo this cold and *rely* on the return value, the same
  code used as a library function will surprise you: it returns the same list
  object that was mutated, not a copy, so `result = sol.moveZeroes(a)` leaves
  `result is a` — aliasing, not a fresh array.
- **Zeroing the tail before pass 1 finishes.** `write` is not final until the
  first loop ends; using it early truncates the answer.
- **Using `if num > 0` instead of `if num != 0`.** The value range includes
  negatives, so this silently deletes every negative number:
  `[-1, 0, 2]` becomes `[2, 0, 0]` instead of `[-1, 2, 0]`. (`if num:` is a
  correct shorthand, since `0` is the only falsy integer — but it is the kind
  of shorthand that stops being correct the moment the element type changes.)
- **Confusing this with [Remove Duplicates](../0026-remove-duplicates-from-sorted-array/README.md).**
  Both compact a prefix with a `write` pointer, but there the tail is
  explicitly ignored and returning the count is the answer; here the tail must
  be cleaned and there is no return value. Same skeleton, opposite endings.
- **All-zeros input does redundant work.** `[0, 0, 0]` rewrites three zeros
  over three zeros. Correct, but if asked to optimize, that is the case to
  mention — and it is exactly where the single-pass swap variant wins.

## Redo from scratch

1. Reframe it immediately: this is not "move the zeros back," it is
   **"compact the non-zeros forward."** The zeros take care of themselves.
2. `write = 0`. Walk the array; on a non-zero, `nums[write] = num` and
   `write += 1`.
3. Second loop: `for i in range(write, len(nums)): nums[i] = 0`.
4. No return. (Or at least, do not depend on one.)
5. Check `[3, 0, 0, 5]` mentally — the consecutive-zeros case that kills the
   naive swap-with-neighbour approach.
6. Then, as a follow-up to yourself, rewrite it as the single-pass swap
   version and convince yourself it produces the same output.

Be able to justify out loud: why it is safe to write into `nums` while
iterating over `nums` — specifically the `write <= read` argument — and why
relative order survives, which is the clause that rules out every
swap-from-both-ends approach.

## Related problems

- [Remove Element](../0027-remove-element/README.md) — already solved. The
  same compaction with a different predicate and no tail cleanup. If the
  skeleton here feels familiar, that is why.
- [Remove Duplicates from Sorted Array](../0026-remove-duplicates-from-sorted-array/README.md)
  — already solved. Third member of the same family; compare what each one
  does with the leftover tail, since that is the only real difference between
  the three.
- [Sort Colors](../0075-sort-colors/README.md) — already solved. The
  generalization: three regions instead of two, and it genuinely needs a
  single pass with two boundaries plus a scanner. Good next step once the
  one-boundary version here is automatic.
- [Apply Operations to an Array](https://leetcode.com/problems/apply-operations-to-an-array/)
  — not solved yet. Literally this problem with a merge step bolted on the
  front: transform adjacent equal pairs, then move zeroes. The second half is
  this exact loop, so it is the cheapest possible check that the pattern
  transferred.
