# 169. Majority Element

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table, Divide and Conquer, Sorting, Counting, Boyer–Moore Majority Vote Algorithm |
| **Solved** | 2026-08-17 |
| **Runtime** | 2 ms (86.71th percentile) |
| **Memory** | 21.3 MB (18.53th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/majority-element/ |

## The problem

**Given** an integer array `nums` of length `n`.

**Return** the *majority element* — the value that occurs **strictly more than
`n / 2`** times. Not "the most frequent value": a value that occurs 4 times out
of 10 may well be the most frequent and is still not a majority. The threshold
is more than half, which is why at most one such value can exist.

Return the value itself, not its index or its count. The array is not modified
and nothing is printed.

**Guaranteed**, and this promise is doing an enormous amount of work: *a
majority element always exists*. That is what licenses returning the survivor of
a single pass without ever verifying it. The array is also non-empty
(`1 <= n`), so there is always something to return.

```text
def majorityElement(self, nums: List[int]) -> int
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[8, 8, 8]` | `8` | The trivial case: one value, never cancelled, `count` climbs to 3. |
| `[4, 4, 1, 1, 4]` | `4` | 3 of 5 — the ordinary case. Trace: `4` (count 1), `4` (2), `1` (1), `1` (0), `4` → count is 0 so `4` is re-adopted and count returns to 1. The candidate survives by being re-elected, not by never being challenged. |
| `[2, 5, 2, 5, 2]` | `2` | **The candidate is dethroned twice and still wins.** Trace: `2` (1), `5` (0), `2` → re-adopt `2` (1), `5` (0), `2` → re-adopt `2` (1). Watching this run is the fastest way to believe that "count hits zero" is not a failure state. |
| `[3, 3, 1, 1, 1, 3, 3]` | `3` | **Counterexample to the naive approach.** `3` occurs 4 times of 7 and is the answer, but the longest *run* belongs to `1` (three consecutive). Any "track the longest streak" heuristic returns `1`. Majority is about totals, not adjacency. |
| `[-10 ** 9, -10 ** 9, 7]` | `-10 ** 9` | **Edge case:** values are unbounded in sign and magnitude (`-10^9 <= nums[i]`), so nothing may be used as an array index or as a sentinel. Equality is the only operation the algorithm performs on the values. |
| `[6]` | `6` | **Edge case:** `n = 1`, and 1 > 0.5, so the single element is trivially the majority. `count` starts at 0, the element is adopted, and it is returned. |
| `[1, 2, 3]` | `3` — **and this input is illegal** | There is no majority here, so the guarantee is violated and the returned value is meaningless: it is simply whoever held the floor last. Worth writing down because it is the exact shape of the bug you ship if you reuse this code somewhere the guarantee does not hold. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `n == nums.length` | Just names the length so the other bounds and the "more than `n / 2`" threshold can refer to it. Nothing algorithmic. |
| `1 <= n <= 5 * 10^4` | The lower bound removes the empty array, so the initial `candidate = None` can never be what gets returned — the loop always runs at least once and always adopts a real value. The upper bound is the one that shapes the solution space: at 5×10^4, an `O(n log n)` sort is ~8×10^5 comparisons and passes easily, and even an `O(n)` hash-count passes; but `O(n^2)` — for each element, count its occurrences — is 2.5×10^9 operations and TLEs in Python by orders of magnitude. So the bound rules out the brute force while leaving sorting, counting and voting all viable. Choosing the vote is about the O(1) space, which this constraint does *not* force — the problem's own follow-up does. |
| `-10^9 <= nums[i] <= 10^9` | Values are signed and span 2×10^9 possibilities, so they cannot be used as indices into a counting array — a bucket-per-value table would need 2×10^9 slots for at most 5×10^4 distinct values. That rules out counting sort and forces any counting approach through a hash map. Boyer–Moore sidesteps the question entirely by never storing more than one value. In Python the magnitudes raise no overflow concern; in a language with 32-bit ints they would not either, since nothing is summed or multiplied. |
| `The input is generated such that a majority element will exist in the array.` | **The load-bearing constraint.** Boyer–Moore's single pass produces a *candidate*, and only this promise upgrades that candidate to an answer. Without it, the algorithm needs a second pass to count the candidate's occurrences and compare against `n // 2`, returning a sentinel on failure — see Majority Element II, where exactly that verification is mandatory. It also means "no majority" is not an edge case to handle: it is an input that cannot occur. |

## Key insight

Pair off every element with a *different* element and throw both away. Deleting
two unequal values can never destroy a strict majority — at most one of the two
was the majority element, so it loses at most one copy while the opposition
loses one too, and a lead of more than half survives every such trade. Keep
doing that and whatever is left standing at the end must be the majority
element. `count` is just the size of the unpaired remainder, and `candidate` is
what it consists of.

## Approach

1. Start with `count = 0` and no candidate. `count` means "how many unpaired
   copies of `candidate` are left", not "how many times I have seen it".
2. Walk the array once. For each `num`:
3. If `count == 0`, everything before this point has cancelled exactly, so the
   prefix carries no information — adopt `num` as the new candidate and start
   over from here. **This step must come before the vote, not after.** Adopting
   first means `num` is then compared against itself, matches, and drives
   `count` from 0 to 1. Reorder it and `num` is compared against the stale
   candidate, `count` goes negative, and the state stops meaning anything.
4. If `num == candidate`, increment `count` — another unpaired copy.
5. Otherwise decrement it — `num` and one copy of `candidate` annihilate each
   other. `count` can never go below zero because the zero case was already
   intercepted in step 3 and converted into a match.
6. Return `candidate`. No verification pass, because the problem promises the
   majority exists.

### Why it's correct

The **invariant**, stated after processing any prefix `nums[0:i]`:

> The prefix can be partitioned into `count` copies of `candidate`, plus
> `(i - count) / 2` disjoint pairs, where the two members of each pair are
> unequal to each other.

Check that it survives one step. If `count == 0` the prefix is entirely pairs;
adopting `num` and incrementing gives one unpaired copy of the new candidate and
the same pairs — holds. If `num == candidate`, the copies go from `count` to
`count + 1` and the pairs are untouched — holds. If `num != candidate` (and
`count > 0`), pair `num` with one of the unpaired copies of `candidate`; they
are unequal, so it is a legal pair, and `count` drops by one — holds. It is
vacuously true for the empty prefix.

Now the payoff, at the end of the array. Suppose `m` is the majority element, so
it occurs more than `n / 2` times, and suppose for contradiction that
`candidate != m`. Every pair contains two *unequal* values, so a pair contains
**at most one** `m`. There are `(n - count) / 2` pairs, and the `count` unpaired
copies are all `candidate`, which is not `m`. So the total number of `m`s is at
most `(n - count) / 2`, which is at most `n / 2`. That contradicts `m` occurring
strictly more than `n / 2` times. Therefore `candidate == m`.

Notice what that argument does *not* claim: it never says the candidate is
correct at every intermediate point, and it is not — on `[2, 5, 2, 5, 2]` the
candidate is `5` after two elements. Only the final state is meaningful. It also
never claims `count` is the majority element's frequency; it is a lead, not a
tally, and on `[4, 4, 1, 1, 4]` it ends at 1 while `4` occurs 3 times. Both
misreadings are the usual source of "improvements" that break the algorithm.

**Termination** is a bounded single pass with no early exit — every element must
be consumed, because an early exit at some comfortable-looking `count` would be
exactly the intermediate-state fallacy above. **At the edges**: `count` never
goes negative, so the `count == 0` test is a true restart rather than a
threshold to tune; and with `n = 1` the loop runs once, adopts, increments to 1,
and returns that element, so the smallest legal input needs no special case. The
only reachable path where `candidate` is still `None` at the return is an empty
array, which `1 <= n` forbids.

The step I would re-derive rather than trust from memory is the pairing bound
`(n - count) / 2` — it is right because the `count` unpaired copies are excluded
from the pairs by construction, but it is the line where an off-by-a-factor-of-2
would hide, and the whole contradiction rests on it.

## Solution

```python
# 169. Majority Element (Easy) - Boyer-Moore majority vote, one pass, no counting table. O(n) time, O(1) space.
class Solution:
    def majorityElement(self, nums: List[int]) -> int:

        # count is NOT "how many times candidate has been seen". It is the size
        # of candidate's surviving lead: how many copies of candidate are left
        # over after every element seen so far has been paired off against a
        # DIFFERENT element and both thrown away. That reading is the whole
        # algorithm, and it is why a single integer can stand in for a frequency
        # table of up to 5 * 10^4 distinct values.
        count = 0
        # None is a safe initial candidate precisely because it can never equal
        # an int, so the first iteration is forced through the count == 0 branch
        # below. It is also what would be returned for an empty array - not a
        # case the constraints allow (1 <= n), and not a case this code defends.
        candidate = None

        for num in nums:
            # Lead exhausted: everything seen so far has cancelled out exactly,
            # so the prefix is irrelevant and the election restarts from here.
            # ORDER IS LOAD-BEARING - this reassignment must happen BEFORE the
            # comparison below, not after. Adopting num as the candidate first
            # means the very same num then votes for itself and count goes
            # 0 -> 1. Move this block after the vote and num would be compared
            # against the OLD candidate, count would go to -1, and the state
            # stops meaning anything.
            if count == 0:
                candidate = num

            # A matching element reinforces the lead...
            if num == candidate:
                count += 1

            # ...and a differing one cancels one copy of it. Note this is the
            # only place count decreases, and it never goes below zero, because
            # count == 0 was intercepted above and turned into a match.
            else:
                count -= 1

        # Whatever is holding the floor at the end. This is correct ONLY because
        # the problem guarantees a majority element exists: the survivor of the
        # cancellation is the majority element if there is one, but on input
        # with no majority it is an arbitrary element rather than a signal.
        # Without that guarantee this needs a second pass counting occurrences
        # of candidate and checking > n // 2.
        return candidate
```

[solution.py](solution.py) · [raw submission](../../data/raw/majority-element.py)

## Why this approach

| Alternative | Cost | Why the vote beats it |
|---|---|---|
| `return Counter(nums).most_common(1)[0][0]` | O(n) time, O(k) space | Correct, one line, and in Python often *faster* in wall-clock because `Counter` counts in C while this loop runs in the interpreter. What it gives up is the space bound: a dict entry per distinct value, up to 5×10^4 of them. If the follow-up "solve it in O(1) space" is asked — and this problem asks it — this row is the answer being rejected. |
| `nums.sort(); return nums[len(nums) // 2]` | O(n log n) time, O(1) or O(n) space | Correct, and delightfully short: a value occupying more than half the array must cover the midpoint no matter how the rest is arranged. Slower asymptotically, and it mutates the caller's array. Worth keeping in your pocket as the answer you can prove in one sentence when the vote's proof deserts you. |
| For each element, count its occurrences and test `> n // 2` | O(n^2) time, O(1) space | Correct but 2.5×10^9 operations at the upper bound — a guaranteed TLE in Python. The constraint `n <= 5 * 10^4` exists to rule this out. |
| Divide and conquer: majority of the left half, majority of the right half, then count both across the whole range | O(n log n) time, O(log n) stack | The reason "Divide and Conquer" is a topic tag. Correct, and genuinely instructive — the merge step relies on the fact that a global majority must be a majority of at least one half — but it is far more code and strictly slower than the single pass. |
| Randomised: pick an index at random, count its occurrences, repeat until one exceeds `n // 2` | O(n) expected time, O(1) space | Each draw hits the majority element with probability > 1/2, so the expected number of rounds is under 2. Cute, and genuinely O(1) space, but it is a Las Vegas algorithm with no worst-case bound, and it needs the verification pass Boyer–Moore avoids. |
| Bit-by-bit: for each of the 32 bit positions, take the majority bit across all elements and reassemble | O(32n) time, O(1) space | Correct and a good interview flex, but it must be done carefully for negative values (`-10^9` is in range), and it reads the array 32 times. Slower for no benefit the vote does not already provide. |

## Complexity

- **Time — O(n)**, a single pass with two integer comparisons and one increment
  per element, no inner loop, no early exit. The 2 ms / 87th-percentile runtime
  is respectable but not top of the chart, and the reason is instructive: the
  faster submissions are almost all `Counter`-based, because their counting
  happens in C while this loop is interpreted. Same asymptotics, different
  constant.
- **Space — O(1)**, exactly two variables regardless of `n` or of how many
  distinct values appear. This is the entire reason to prefer this solution, and
  it is what the problem's own follow-up asks for. The 21.3 MB / 19th-percentile
  memory figure is *not* evidence against that — it is dominated by the
  interpreter and the input array itself, which every submission pays.

## Pitfalls

- **Adopting the candidate after the vote instead of before.** If the
  `if count == 0: candidate = num` block is moved below the comparison, then on
  `[1, 2, 2]` the element `2` at index 1 is compared against candidate `1`,
  `count` drops to `-1`, and the state is nonsense from there on. The reassign
  must precede the vote so that the adopting element casts the first ballot for
  itself.
- **Reading `count` as a frequency.** On `[4, 4, 1, 1, 4]` the loop ends with
  `count == 1` while `4` occurs three times. Anyone who adds
  `if count > len(nums) // 2: return candidate` as an early exit has misread
  this, and the early exit will fire late or never.
- **Trusting the candidate mid-loop.** On `[2, 5, 2, 5, 2]` the candidate is
  `5` after two elements and `2` at the end. There is no prefix property to
  exploit; the array must be consumed to the last element.
- **Reusing this where no majority is guaranteed.** `[1, 2, 3]` returns `3`,
  which is a majority of nothing. The single pass produces a candidate, not a
  verdict. If the guarantee is absent, add a second pass:
  `return candidate if nums.count(candidate) > len(nums) // 2 else -1`.
- **Confusing "majority" with "mode".** In `[7, 7, 1, 2, 3]` the value `7` is
  the most frequent and is *not* a majority (2 of 5). This algorithm would
  return `7` and be wrong about the question actually asked. The threshold is
  strictly greater than half.
- **`> n // 2` versus `>= n // 2` in the verification variant.** With `n = 4`,
  `n // 2` is 2, and a value occurring exactly twice is not a majority — `>=`
  accepts it wrongly. With odd `n` the two happen to agree, so a test set of odd
  lengths hides the bug.
- **Initialising `candidate = nums[0]` with `count = 1` instead.** Also correct,
  and arguably cleaner, but it requires a non-empty array — fine here under
  `1 <= n`, and a crash the moment the function is reused somewhere it is not.
  The `None` / `0` start is the version that degrades gracefully.

## Redo from scratch

1. Say the cancellation argument out loud before writing anything: *deleting two
   unequal elements cannot destroy a strict majority.* If you cannot say that,
   write the sort-and-take-the-middle solution instead — it is correct and you
   can prove it.
2. `count = 0`, `candidate = None`.
3. One loop over `nums`. First: `if count == 0: candidate = num`. Before the
   vote, always.
4. Then `if num == candidate: count += 1 else: count -= 1`.
5. `return candidate`, with no verification — but only because the constraints
   guarantee the majority exists. Note that dependency explicitly; it is the
   difference between this and Majority Element II.
6. Trace `[2, 5, 2, 5, 2]` by hand. If your trace does not have the candidate
   being re-adopted twice, the ordering in step 3 is wrong.

Be able to justify out loud:

- **Why the survivor must be the majority element.** The full contradiction, not
  a hand-wave: each pair holds at most one copy of `m`, there are
  `(n - count) / 2` pairs, the `count` leftovers are not `m`, so `m` occurs at
  most `n / 2` times — contradicting majority.
- **Exactly which line depends on the existence guarantee, and what you would
  add without it.** The bare `return candidate`; you would add a counting pass.

## Related problems

- [Majority Element II](https://leetcode.com/problems/majority-element-ii/) — not solved yet. Everything occurring more than `n / 3` times, so up to two answers, tracked with two candidates and two counters. The essential follow-up, because the existence guarantee disappears and the verification pass this solution skips becomes mandatory — it is the problem that shows you which half of the algorithm you actually understood.
- [Check If a Number Is Majority Element in a Sorted Array](https://leetcode.com/problems/check-if-a-number-is-majority-element-in-a-sorted-array/) — not solved yet. Sorted input turns the question into two binary searches for the value's first and last position, in O(log n). Good for seeing that the input's structure, not the question, is what picks the algorithm.
- [Boyer–Moore Voting on a stream](https://leetcode.com/problems/most-frequent-even-element/) — not solved yet; LeetCode lists Most Frequent Even Element as similar, though it is really a plain counting problem with a tie-break rule. Useful only as a reminder that "most frequent" and "majority" are different questions, which is the distinction in the Pitfalls above.
- [Minimum Index of a Valid Split](https://leetcode.com/problems/minimum-index-of-a-valid-split/) — not solved yet. Uses the guaranteed dominant element and asks where the array can be cut so both halves keep it. Builds directly on the counting intuition here, with a prefix-count sweep on top.
- [Valid Anagram](../0242-valid-anagram/README.md) — solved, and not in the similar list. The counterpoint: there, the right move is to build the full frequency table; here, the whole point is refusing to. Comparing them is the cleanest way to see when a `Counter` is the answer and when it is the lazy answer.

*Of the related problems above, only Valid Anagram is in this repo so far.*
