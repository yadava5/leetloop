# 27. Remove Element

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Two Pointers |
| **Solved** | 2026-08-17 |
| **Runtime** | 0 ms (100.00th percentile) |
| **Memory** | 19.3 MB (57.19th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/remove-element/ |

## The problem

**Given** an integer array `nums` and an integer `val`.

**Return** an integer `k`: how many elements of `nums` are *not* equal to `val`.

But the return value is only half the answer. The other half is a side effect:
`nums` must be **modified in place** so that its first `k` slots hold exactly
those surviving elements. You may not allocate a new list and hand it back —
the grader reads `k` from your return value and then reads `nums[0:k]` out of
the array you were passed.

What happens beyond index `k` is explicitly **not checked**. The old values can
stay there, be zeroed, be anything. There is no need to shrink the list, and no
credit for doing so.

The relative order of the survivors is likewise not checked: any permutation of
the correct multiset in the first `k` slots is accepted. This solution happens
to preserve the original order anyway, which costs nothing and makes it easier
to reason about.

**Guaranteed**: nothing useful. The array may be empty, `val` may not appear at
all, and every element may be `val`. All three cases must fall out of the code
rather than being special-cased.

```text
def removeElement(self, nums: List[int], val: int) -> int
```

### Examples (mine, not LeetCode's)

| `nums` (before) | `val` | Returns | `nums[:k]` (after) | Why |
|---|---|---|---|---|
| `[7, 2, 7, 9]` | `7` | `2` | `[2, 9]` | The ordinary case. Two survivors get slid down to indices 0 and 1; indices 2 and 3 keep whatever junk the loop left there, which is not read. |
| `[4, 4, 4]` | `4` | `0` | `[]` | **Edge case:** everything is removed. `write` never advances, no element is ever copied, and returning `0` tells the grader to read nothing. |
| `[8, 8, 8]` | `1` | `3` | `[8, 8, 8]` | **Edge case:** nothing is removed — `0 <= val <= 100` while `0 <= nums[i] <= 50`, so a `val` that cannot possibly occur is a legal input. Every iteration writes an element onto itself. Wasteful, still correct. |
| `[]` | `5` | `0` | `[]` | **Edge case:** the empty array is legal (`0 <= nums.length`). The loop body never runs and `write` is still `0`. Any solution that starts by touching `nums[0]` crashes here. |
| `[3, 6, 3, 6, 3]` | `3` | `2` | `[6, 6]` | **Counterexample to the naive approach.** Writing `for num in nums: if num == val: nums.remove(num)` returns a list still containing a `3`: `remove` shifts everything left while the loop's internal index keeps marching right, so the element that slides into the vacated slot is skipped entirely. Mutating a list's *length* under iteration is the bug; this solution only ever mutates its *contents*. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `0 <= nums.length <= 100` | The lower bound is the interesting one: **zero is allowed**, so the empty array is a legal input and any approach that reads `nums[0]`, or that initialises a pointer from the last index, has to defend itself. This code needs no guard — a `for` over an empty list simply does not execute. The upper bound of 100 is so small that it forces nothing at all on the time side: even an `O(n^2)` "find a `val`, shift the whole tail down one" would be ~10^4 operations and pass comfortably. So the constraint is not what rules out the quadratic solution — taste is. What the problem *does* insist on is O(1) extra space, and that requirement comes from the statement's in-place demand, not from this bound. |
| `0 <= nums[i] <= 50` | Values are small non-negative integers, which mostly matters for what it rules *in*: there is no sentinel worry, no overflow, and comparisons are plain `==`. It also means a counting-sort-flavoured rewrite (tally the 51 possible values, rewrite the array) is available — correct, but it would destroy the original order and use more code for no gain. |
| `0 <= val <= 100` | Deliberately a **wider** range than the elements. `val` can legally be 51–100, a value that cannot appear in `nums`, so "no element is removed" is a case the test set will actually exercise. The code must return `len(nums)` there, which it does by advancing `write` on every iteration. |

## Key insight

Stop thinking about *deleting* and start thinking about *rebuilding*. Deletion
from an array is expensive because every removal shifts the tail; but nothing
here requires deletion — it requires that the first `k` slots end up holding the
keepers. So sweep left to right and re-write the array from its own contents,
keeping one index for where you are reading and one for where the next keeper
goes. The keepers are never behind the reader, so you can overwrite as you go.

## Approach

1. Set `write = 0`. It counts survivors and simultaneously points at the next
   free slot at the front of the array.
2. Walk every element of `nums` once, left to right, as `num`. This is the read
   pointer, just spelled as a `for ... in` rather than an index.
3. If `num == val`, do nothing at all — no copy, no advance. The element is
   dropped by simply never being written anywhere.
4. Otherwise store it at `nums[write]` and advance `write` by one. **The order
   inside this branch matters**: write first, *then* increment. Incrementing
   first would place the element one slot too far right and leave index 0 with
   its original value forever.
5. Return `write`. No cleanup pass, no truncation.

### Why it's correct

The **invariant**, stated for the moment just before the loop body runs on read
index `i`:

> `nums[0:write]` contains, in their original relative order, exactly the
> elements of the original `nums[0:i]` that are not equal to `val`; and
> `write <= i`.

It holds trivially before the first iteration (`write = i = 0`, both slices
empty). Each iteration preserves it: if `nums[i] == val` neither `write` nor the
prefix changes while `i` grows, so both halves still hold; if not, the element is
appended at `nums[write]` and `write` grows by one, exactly matching the one new
qualifying element in `nums[0:i+1]`, and `write + 1 <= i + 1` follows from
`write <= i`.

That second clause — `write <= i` — is the part that is easy to skip and is the
only reason the whole thing is legal. Writing to `nums[write]` while iterating
over `nums` would be a catastrophe if `write` could ever exceed `i`, because the
loop would then read a slot the loop itself had already clobbered. It cannot:
`write` advances at most once per iteration and starts equal to `i`. So every
write lands on a slot already consumed, and the read stream is untouched.

**Termination** is unconditional — a bounded `for` over a finite list, with no
`break` and no mutation of the list's length (`nums[write] = num` replaces an
element, it never inserts or deletes, so the iterator's view of the length never
shifts). **At the edge**, after the final iteration `i = len(nums) - 1` and the
invariant reads: `nums[0:write]` is exactly the non-`val` elements of the whole
array, which is precisely what the problem asks to be in place, and `write` is
its length, which is precisely `k`. Nothing has to happen after the loop, which
is why there is no post-processing step to get wrong.

## Solution

```python
# 27. Remove Element (Easy) - in-place compaction with a write pointer. O(n) time, O(1) extra space.
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:

        # write carries two meanings at once, and that is the whole trick:
        #   - how many keepers have been placed so far, and
        #   - the index the NEXT keeper belongs at.
        # Because those are the same number, the counter that gets returned is
        # also the pointer that does the work. No second variable, no final
        # arithmetic to convert one into the other.
        write = 0

        # The read pointer is implicit: `num` walks the list left to right,
        # each element exactly once. write only advances on a keeper, so after
        # processing index i we have write <= i + 1, which means the slot being
        # written to has ALWAYS already been read. That is why mutating nums
        # while iterating over it is safe here even though it is normally a
        # trap - the writer can never overtake the reader.
        for num in nums:
            if num != val:
                # Copy the keeper down to the front of the array. Before the
                # first deletion write == the read index and this assigns an
                # element onto itself: wasted, never wrong. Guarding it with
                # `if write != <read index>` would need an explicit read index
                # and buys nothing.
                nums[write] = num
                # WART worth knowing: `write +=1` is missing the space before
                # the 1. Valid Python, and PEP 8 wants `write += 1`.
                write +=1
        # Everything from index write onward is stale leftovers from the
        # original array - the problem states outright that those slots are
        # ignored, so there is nothing to clear or pad. Returning write is
        # returning k, the number of surviving elements, and nums[:k] is
        # already exactly those elements in their original relative order.
        return write
```

[solution.py](solution.py) · [raw submission](../../data/raw/remove-element.py)

## Why this approach

| Alternative | Cost | Why the write pointer beats it |
|---|---|---|
| `nums[:] = [x for x in nums if x != val]; return len(nums)` | O(n) time, O(n) temporary space | Genuinely correct — the slice assignment mutates the caller's list, so it satisfies "in place" as the grader checks it. But it builds a whole second list first, which is the O(1)-space requirement dodged rather than met. Fine in Python, and an instant fail if the interviewer meant it. |
| `while val in nums: nums.remove(val)` | O(n^2) time, O(1) space | Correct, and at `n <= 100` fast enough to pass. Each `remove` is a linear scan plus a linear shift, so it is quadratic in the number of removals — and it is the "delete" framing the key insight argues against. |
| `for num in nums: if num == val: nums.remove(num)` | O(n^2) time | **Wrong, not slow.** On `[3, 6, 3, 6, 3]` with `val = 3` it leaves a `3` behind. `remove` shortens the list underneath an iterator that is advancing by index, so the element shifted into the vacated slot is never examined. The single most common way to get this problem wrong. |
| Swap-with-the-end two pointers (`i` from the left, `n` shrinking from the right; on a hit, copy `nums[n-1]` into `nums[i]` and shrink `n` without advancing `i`) | O(n) time, O(1) space | Also correct, and strictly fewer *writes* when removals are rare — it touches only the slots it has to, whereas this solution rewrites every keeper. That is the textbook answer when the array is huge and `val` is rare. The cost is that it scrambles the order, and it has a genuine trap: after the swap you must **not** advance `i`, because the element you just pulled in from the end has not been tested yet. More to get wrong for a win the constraints do not need. |
| Count the survivors first, then fill | O(n) time, two passes | Two passes to do what one pass does, and it still needs the same write pointer in the second pass. Strictly worse. |

## Complexity

- **Time — O(n)**, one pass over `nums` with O(1) work per element: one integer
  comparison, and for a keeper one store plus one increment. There is no inner
  loop and no shifting, which is exactly the difference from the `remove`-based
  solutions. The 0 ms / 100th-percentile runtime is unsurprising at `n <= 100`;
  it says the approach is not pathological, not that it is tuned.
- **Space — O(1) extra.** One integer, `write`. The array is rewritten inside
  its own storage, no list is allocated, and nothing grows with `n`. This is the
  actual requirement of the problem, and the only one of the alternatives above
  that fails it is the list-comprehension rebuild.

## Pitfalls

- **`for num in nums: if num == val: nums.remove(num)`** returns
  `[3, 6, 6]`-worth of nonsense on `[3, 6, 3, 6, 3]`, `val = 3` — one `3`
  survives. Deleting from a list while a `for` walks it by index skips the
  element that slides into the hole. If you must delete in a loop, iterate
  backwards.
- **Incrementing `write` before storing.** `write += 1; nums[write] = num`
  leaves `nums[0]` untouched forever and writes one slot too far right. On
  `[7, 2]` with `val = 7` it returns `1` with `nums[0]` still `7` — the answer
  the grader reads is the removed element itself.
- **Returning `nums` instead of `k`.** The signature says `-> int`. Returning a
  list, or returning `nums[:write]`, fails the type contract even though the
  data is right.
- **Truncating with `del nums[write:]` and then returning `len(nums)`.** Works,
  and is a reasonable habit, but it is extra O(n) work the grader ignores, and
  if you forget to also fix the return value you get the *pre*-truncation
  length.
- **Assuming `nums` is non-empty.** `0 <= nums.length` permits `[]`. Any variant
  that starts with `n = len(nums) - 1` and indexes `nums[n]` crashes there. The
  `for`-loop form dodges this without a guard, which is easy to mistake for luck
  — it is the reason to prefer it.
- **Worrying that writing into `nums` mid-iteration is unsafe.** It is safe
  *here*, non-obviously, because `write <= i` always and `nums[write] = num`
  does not change the list's length. This is exactly the kind of correct-but-
  surprising code that a later "cleanup" turns back into a bug by introducing a
  copy of the list to iterate over "for safety" — which quietly costs O(n)
  space.
- **Reading "in place" as "and the list must end up length k".** It must not.
  The trailing garbage is part of the accepted answer.

## Redo from scratch

1. Say the reframing out loud first: *this is not a deletion problem, it is a
   compaction problem.* Rebuild the array from its own contents.
2. `write = 0` — one variable, meaning both "survivors so far" and "next free
   slot".
3. `for num in nums:` — read every element once.
4. `if num != val:` → `nums[write] = num`, then `write += 1`. Store before
   incrementing.
5. `return write`. Resist the urge to truncate or to return a slice.
6. Sanity-check against `[]`, against "every element is `val`", and against "no
   element is `val`" before submitting. All three should work with no extra
   code; if any needs a special case, the loop is wrong.

Be able to justify out loud:

- **Why overwriting `nums` while iterating over it is safe.** Because `write`
  never exceeds the read index, so every write lands on a slot already read —
  and because assigning to an index does not change the list's length, unlike
  `remove` or `del`.
- **Why nothing needs to happen after the loop.** State the invariant at exit:
  `nums[0:write]` is exactly the non-`val` elements, so `write` *is* `k`. If you
  find yourself adding a cleanup pass, you have mis-stated the invariant.

## Related problems

- [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) — not solved yet. The same write pointer with a different keep-test: keep an element when it differs from the last one *written* rather than from a fixed `val`. The natural next problem, because it forces the predicate to depend on `nums[write - 1]`, which is where the `write == 0` edge case first bites.
- [Move Zeroes](https://leetcode.com/problems/move-zeroes/) — not solved yet. Literally this solution with `val = 0`, plus a second pass that fills `nums[write:]` with zeroes instead of leaving garbage. Good for internalising that "what happens after index k" is a *specification* choice, not an algorithmic one.
- [Remove Linked List Elements](https://leetcode.com/problems/remove-linked-list-elements/) — not solved yet. The same task where the tail-shifting cost that makes array deletion expensive simply does not exist, so the answer is genuine pointer surgery. Worth doing next to this one to see why "don't delete, compact" is advice about arrays specifically.
- [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) — not solved yet, and not in the similar list. Same pointer, keep-test relaxed to "at most twice", which is the version where people finally write the invariant down instead of guessing.
- [Sort Colors](https://leetcode.com/problems/sort-colors/) — not solved yet, and not in the similar list. Three write pointers into one array in one pass. The place the swap-with-the-end alternative from the table above becomes mandatory rather than optional.

*None of the related problems above are in this repo yet.*
