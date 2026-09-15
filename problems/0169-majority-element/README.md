# 169. Majority Element

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table, Divide and Conquer, Sorting, Counting, Boyer–Moore Majority Vote Algorithm |
| **Solved** | 2026-09-14 |
| **Runtime** | 7 ms (58.42th percentile) |
| **Memory** | 21.6 MB (5.06th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/majority-element/ |

## The problem

**Given** an integer array `nums` of length `n`.

**Return** the *majority element* — the value that appears **strictly more
than `⌊n/2⌋` times**. Return the value itself, not its index or its count.

Note how strong "more than half" is. It is not "the most frequent element";
it is a value so dominant that it outnumbers *everything else combined*. That
strength is what the algorithm below exploits, and it is why the same approach
does not work for "most frequent."

**Guaranteed**: a majority element always exists. This is not a detail — the
solution below returns a wrong answer rather than an error when it is false,
and the standard algorithm normally requires a second verification pass that
this guarantee lets you delete.

```text
def majorityElement(self, nums: List[int]) -> int
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[7, 7, 3]` | `7` | The ordinary case: `7` appears twice out of three, which is more than `⌊3/2⌋ = 1`. |
| `[4]` | `4` | **Edge case:** a single element is trivially the majority (1 > `⌊1/2⌋ = 0`). The loop runs once, `count` goes to `1`, and the initial `candidate` is confirmed. |
| `[5, 5, 5, 5]` | `5` | No opposition at all. `count` climbs monotonically to `4` and never resets — the branch that matters most is the one that never fires. |
| `[2, 1, 2, 1, 2]` | `2` | **The counterexample that kills "just track the running most-frequent-so-far."** After two elements the counts are tied 1–1; after four they are tied 2–2. At no prefix shorter than the whole array is `2` unambiguously ahead, so any approach that commits to an answer early is wrong. Boyer–Moore survives because it tracks a *margin*, not a count. |
| `[6, 6, 8, 9, 6, 6]` | `6` | **The case that shows why the candidate is allowed to change and change back.** Walk it: `6`(c=6,n=1), `6`(n=2), `8`(n=1), `9`(n=0 — candidate now discarded), then `6` resets the candidate to `6`(n=1), `6`(n=2). The algorithm abandons the correct answer mid-scan and re-adopts it. That is not a bug; it is the mechanism. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `n == nums.length` | Just naming — the array's own length defines `n`, which is what `⌊n/2⌋` in the problem statement refers to. |
| `1 <= n <= 5 * 10^4` | The lower bound of `1` means the array is never empty, which is what makes `candidate = nums[0]` safe from an `IndexError` — on an empty array that line would raise. The upper bound of 50,000 is small: an O(n log n) sort (≈ 50,000 × 16 ≈ 8 × 10⁵ operations) passes easily, and even a hash-map count is fine. **So the size constraint does not force Boyer–Moore.** The reason to reach for it is the well-known follow-up asking for O(1) space, not the time limit. |
| `-10^9 <= nums[i] <= 10^9` | Two billion possible values, which is what rules out a counting array indexed by value — you cannot allocate 2 × 10⁹ slots. A hash map works (its size is bounded by `n`, not by the value range), but Boyer–Moore sidesteps the question entirely by storing exactly one value. Values comfortably fit in a machine int, so the counter arithmetic cannot overflow in any language, and in Python it could not anyway. |
| `The input is generated such that a majority element will exist in the array.` | **The load-bearing one.** Boyer–Moore's vote phase finds a candidate that *would be* the majority if one exists; on input with no majority it returns an arbitrary survivor. The textbook algorithm therefore has a second pass that counts the candidate's occurrences and reports failure if it is not above `⌊n/2⌋`. This guarantee is exactly the permission to omit that pass — and it is why the code below can `return candidate` directly with no verification. Remove this line from the problem and the code becomes wrong. |

## Key insight

Pair off and cancel. If you repeatedly delete two *different* elements from
the array, the majority element stays in the majority — because it was more
than half to begin with, so every cancelled pair removes at most one of its
occurrences and at least one of something else. Keep cancelling until only one
kind of element remains, and that survivor must be the majority. The candidate
and counter are just a way to do all that cancelling in one pass without
actually building anything.

## Approach

1. Hold two pieces of state: `candidate` (the value currently winning) and
   `count` (its *margin* over everything seen since the last reset — not its
   total frequency).
2. Walk the array once.
3. If `count == 0`, the prefix examined so far has cancelled out completely and
   there is no standing leader. Adopt the current element as the new
   `candidate`.
4. Then, separately, cast the current element's vote: `+1` if it equals the
   candidate, `-1` if it does not.
5. After the pass, return `candidate`.

Step 3 and step 4 are **two independent `if`s, not an `if`/`elif` chain**, and
that is the detail most worth pinning down. A freshly adopted candidate must
also vote for itself in the same iteration. If step 4 were an `elif` attached
to step 3, a new candidate would be installed with `count` still at `0`, and
the very next element would immediately depose it — the counter could never
climb above zero and the algorithm would just return the last element of the
array.

### Why it's correct

**Invariant**: at every point, `count` equals the number of occurrences of
`candidate` in the unprocessed-since-reset window minus the number of
non-`candidate` elements in it — i.e. the candidate's *net margin* over that
window. Equivalently, and more usefully: the elements consumed so far can be
partitioned into `count` copies of `candidate` plus some number of *cancelling
pairs*, where each pair holds two elements that are not equal to each other.

That framing is what makes the conclusion follow. Whenever `count` hits `0`,
the entire prefix processed so far has decomposed into cancelling pairs with
nothing left over. Since each pair removes at most one occurrence of the true
majority element `M`, and `M` had a strict majority overall, discarding a
fully-cancelled prefix leaves `M` still holding a strict majority of the
*remaining* suffix. So the algorithm may safely forget everything before a
reset — the problem it faces afterwards is the same problem on a smaller
array, with the same answer.

At the end, `count >= 1` necessarily (it cannot be negative — it is only
decremented when positive, because a zero count triggers the reset branch
first, which then increments). So there is a non-empty residue of
uncancelled copies of `candidate`, and by the argument above that residue must
consist of copies of `M`. Hence `candidate == M`.

**Termination and the edge of the range**: the loop is a plain `for` over the
whole array, so it runs exactly `n` times and terminates trivially — there is
no early exit and no index arithmetic to get wrong, which is part of why this
algorithm is nicer than it looks. The first iteration is the interesting edge:
`count` starts at `0`, so the reset branch fires immediately and sets
`candidate = nums[0]` — overwriting the identical value the code already
assigned before the loop. The last iteration does nothing special; the answer
is simply whatever `candidate` holds when the array runs out.

The step I would flag as worth re-deriving rather than trusting: the claim
that a fully-cancelled prefix can be discarded without changing the answer.
It is the crux, it is not obvious, and "the counter works out" is not a proof
of it.

## Solution

```python
# 169. Majority Element (Easy) - Boyer-Moore majority vote: one candidate, one counter, single pass. O(n) time, O(1) space.
class Solution:
    def majorityElement(self, nums: List[int]) -> int:
            
        # WART: this initial assignment is dead. On the very first iteration
        # count is 0, so `candidate = num` immediately overwrites it with the
        # same nums[0]. Harmless, and it does document the intent, but it is
        # not load-bearing - deleting it would not change the result.
        candidate = nums[0]

        count = 0
        for num in nums:
            # A count of 0 means every element seen so far has been cancelled
            # out in pairs, so the prefix examined up to this point has no
            # surviving leader. Restart the vote from the current element.
            if count == 0:
                candidate = num

            # ORDER MATTERS: this `if` is deliberately NOT an `elif` attached
            # to the count == 0 test above. When the counter has just been
            # reset, the current element must also cast its own vote (+1),
            # otherwise a fresh candidate would start at count 0 and be
            # replaced again on the very next element, and the counter could
            # never grow.
            if num == candidate:
                count += 1
            else:
                count -= 1

        # No verification pass is needed because the problem guarantees a
        # majority element exists. Without that guarantee this returns
        # garbage - see Pitfalls.
        return candidate
        
```

[solution.py](solution.py) · [raw submission](../../data/raw/majority-element.py)

## Why this approach

| Alternative | Cost | Why Boyer–Moore beats it |
|---|---|---|
| `collections.Counter(nums).most_common(1)[0][0]` | O(n) time, O(n) space | Correct, one line, and the right answer in real code. It loses only on the follow-up's terms: the hash map holds up to `n` distinct keys, where Boyer–Moore holds two integers. Given `n <= 5 × 10⁴` it would pass comfortably — this is a space-elegance win, not a necessity. |
| Sort, then return `nums[n // 2]` | O(n log n) time, O(1)–O(n) space | Clever and genuinely correct: an element occupying more than half the slots must cover the middle index no matter how the array is arranged. But it is asymptotically worse, and in Python `nums.sort()` also mutates the caller's array, which is a side effect the problem never asked for. |
| Divide and conquer: majority of the left half, majority of the right half, then count both across the whole range | O(n log n) time, O(log n) stack | The recurrence `T(n) = 2T(n/2) + O(n)` is strictly worse than one pass, and the merge step is fiddly (the answer can be the majority of neither half... no — it must be the majority of at least one half, which is the non-obvious lemma that makes it work at all). Instructive, but strictly harder to get right for a worse bound. |
| Randomized: pick an element at random, count it, repeat until one exceeds `⌊n/2⌋` | O(n) expected time, O(1) space | Each draw hits the majority with probability > 1/2, so the expected number of draws is < 2 — genuinely fast in expectation. But it has no worst-case bound, needs a verification count anyway, and is strictly worse than a deterministic single pass that does the same work. |
| Track the running most-frequent-so-far and commit early | O(n) time | **Wrong.** `[2, 1, 2, 1, 2]` is tied at every proper prefix of even length; nothing is "ahead" until the final element. Boyer–Moore works precisely because it never commits — it tracks a margin that is allowed to collapse to zero and restart. |

## Complexity

- **Time — O(n)**. Exactly one pass, with two comparisons and one arithmetic
  update per element. No sorting, no hashing, no second verification pass
  (which the existence guarantee lets us skip).
- **Space — O(1)**. Two scalars, `candidate` and `count`, regardless of `n` or
  of how many distinct values the array contains. This is the entire reason to
  prefer it over `Counter`.

## Pitfalls

- **Making the second `if` an `elif`.** This is the bug this algorithm is
  famous for. With `elif`, a candidate adopted at `count == 0` does not vote
  for itself, so `count` stays `0` and the next element replaces it
  immediately. On `[7, 7, 3]` you would get: `7` adopted with `count` still
  `0`; `7` adopted again, `count` still `0`; `3` adopted, `count` still `0` —
  returning `3`. The code reads almost identically and fails on almost
  everything.
- **Returning `count`, or treating `count` as a frequency.** It is a margin,
  not a tally. On `[5, 5, 5, 5]` it ends at `4`, but on `[6, 6, 8, 9, 6, 6]`
  it ends at `2` even though `6` occurs four times. The final value of `count`
  carries no useful information at all.
- **Relying on this when a majority might not exist.** Feed it `[1, 2, 3]` and
  it returns `3` with total confidence — the last element survives by
  accident. If you ever reuse this outside a problem that guarantees a
  majority, you **must** add the second pass: `if nums.count(candidate) >
  len(nums) // 2`. Forgetting that is how this algorithm turns into a silent
  data-corruption bug in production code.
- **`candidate = nums[0]` looks necessary and is not.** It is dead — the first
  loop iteration always overwrites it, because `count` starts at `0`. Worth
  knowing so that seeing it deleted in someone else's version does not read as
  a bug. What it *does* do is crash on an empty array, which the constraints
  forbid; if you generalize this, decide deliberately whether you want that
  crash or a `None`.
- **Confusing "majority" with "mode."** More than half is a far stronger
  condition than most-frequent. `[1, 1, 2, 2, 3]` has mode `1` (tied with `2`)
  and no majority at all. Boyer–Moore answers only the stronger question.

## Redo from scratch

1. Say the cancellation argument out loud before writing anything: **delete
   two unequal elements repeatedly; the majority survives.** The code is just
   bookkeeping for that.
2. Two variables: `candidate`, `count = 0`.
3. One pass. `if count == 0: candidate = num`. Then — as a **separate** `if`,
   not an `elif` — `count += 1` if `num == candidate` else `count -= 1`.
4. Return `candidate`. No second pass, because the problem guarantees a
   majority exists — say that guarantee out loud too, so you notice when a
   future problem lacks it.
5. Trace `[6, 6, 8, 9, 6, 6]` by hand and watch the candidate get abandoned at
   the `9` and re-adopted at the next `6`. If that sequence surprises you, the
   invariant has not landed yet.

Be able to justify out loud: why a fully-cancelled prefix can be thrown away
without changing the answer, and why the self-vote on the reset iteration is
mandatory rather than cosmetic.

## Related problems

- [Majority Element II](https://leetcode.com/problems/majority-element-ii/) —
  not solved yet. Find every element appearing more than `⌊n/3⌋` times, of
  which there can be at most two. Boyer–Moore generalizes: keep two candidates
  and two counters. Crucially, the `⌊n/3⌋` version **does** need the
  verification pass that this problem's guarantee let you skip — which makes
  it the best possible check that you understood why the pass exists.
- [Check If a Number Is Majority Element in a Sorted Array](https://leetcode.com/problems/check-if-a-number-is-majority-element-in-a-sorted-array/)
  — not solved yet. The verification half alone, made efficient with binary
  search on a sorted array. Complementary: this problem finds the candidate,
  that one confirms it.
- [Top K Frequent Elements](../0347-top-k-frequent-elements/README.md) —
  already solved. The general "most frequent" question, which genuinely needs
  a frequency map. Useful contrast: it shows exactly what the majority
  guarantee bought — the ability to answer without counting anything.
- [Sort Colors](../0075-sort-colors/README.md) — already solved. Another
  single-pass, O(1)-space array algorithm whose correctness rests entirely on
  a stated invariant rather than on anything visible in the code.
- [Most Frequent Even Element](https://leetcode.com/problems/most-frequent-even-element/)
  — not solved yet. A plain counting problem with a filter; included by
  LeetCode as similar, but it needs a hash map and teaches the opposite
  lesson — that most frequency questions do not collapse the way this one does.
