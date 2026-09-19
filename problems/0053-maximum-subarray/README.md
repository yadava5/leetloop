# 53. Maximum Subarray

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Divide and Conquer, Dynamic Programming |
| **Solved** | 2026-09-17 |
| **Runtime** | 19 ms (96.82th percentile) |
| **Memory** | 31.5 MB (45.38th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/maximum-subarray/ |

## The problem

**Given** an integer array `nums`, which may contain negative values.

**Return** the largest sum achievable by any **contiguous, non-empty**
subarray. The sum itself, not the subarray and not its indices.

Three things to be precise about, because each is a way to get this wrong:

- **Contiguous.** A subarray is a run of adjacent elements. You may not skip an
  element you dislike — that would be a *subsequence*, and the answer to that
  problem is just "sum of all the positives", which is a different and much
  easier question.
- **Non-empty.** You must take at least one element. This is the entire
  difficulty of the all-negative case: the answer to `[-5, -2, -9]` is `-2`, not
  `0`, because "take nothing" is not on the table.
- **The sum, not the span.** Nothing needs to be returned about *where* the best
  subarray sits, which is what permits the two-scalar solution below.

**Guaranteed**: the array has at least one element, so `nums[0]` can be read
without a guard, and an answer always exists.

```text
def maxSubArray(self, nums: list[int]) -> int
```

### Examples (mine, not LeetCode's)

| `nums` | Returns | Why |
|---|---|---|
| `[2, -1, 3]` | `4` | The whole array. The `-1` costs one but unlocks the `3`, so crossing it nets `+2` versus stopping at the `2`. This is the shape that makes the problem non-trivial: a negative element is not a wall. |
| `[4, -1, 4]` | `7` | **Counterexample to "restart whenever the element is negative."** That rule stops at the first `4` and answers `4`. What matters is whether the *running sum so far* has gone negative, not whether this one element did. |
| `[4, -6, 5]` | `5` | The mirror image, and why the rule above has to exist at all. Here the `-6` really does sink the prefix — `4 - 6 = -2` — so the best subarray starts fresh at the `5` and drops everything before it. Same element pattern as the row above, opposite decision, decided purely by the running total. |
| `[-5, -2, -9]` | `-2` | **Edge case, and the one that catches most rewrites:** every element is negative, so the answer is the *least bad* single element. Any solution that seeds its maximum at `0` returns `0` here. |
| `[7]` | `7` | **Edge case:** one element. The `for` loop never runs; the answer is entirely the seed values. |
| `[-3, 8, -2, 5, -9]` | `11` | `8 - 2 + 5`. Neither end of the array is in the answer, and the trailing `-9` is correctly refused even though `current` is positive when it arrives — `best` has already banked `11`. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 10^5` | The upper bound rules out the obvious double loop over every `(start, end)` pair: 10⁵ elements means ~5 × 10⁹ pairs, which is hopeless in Python, so an O(n) or O(n log n) method is required. It also means recursion is a liability — a divide-and-conquer written recursively goes ~17 levels deep, which is fine, but the iterative scan avoids the question entirely. The lower bound of `1` is the one the code actually leans on: it is what makes `nums[0]` safe to read as a seed with no emptiness check, and it is what makes "non-empty subarray" always satisfiable. |
| `-10^4 <= nums[i] <= 10^4` | Values can be negative, which is the entire problem — with non-negative values the answer would trivially be the sum of the whole array. The bound also settles the arithmetic: the extreme possible sum is 10⁵ × 10⁴ = 10⁹, comfortably inside a machine word and irrelevant in Python anyway, so no overflow guard is needed and no sentinel like `-inf` is required — `nums[0]` is a legitimate starting maximum. Finally, since values are bounded but *not* guaranteed to include a positive, the all-negative case is explicitly in scope rather than a curiosity. |

## Key insight

Don't ask "which subarray is best" — ask, for each index in turn, "what is the
best subarray that **ends right here**?" That question has a one-line answer
built from the previous index's answer: either extend what ended at `i-1`, or
start over at `i`. And you start over exactly when the previous total was
negative, because a negative prefix makes every sum it is glued onto *smaller*.
The global answer is then just the best of those `n` local answers.

The thing to whisper if stuck: *a negative element is not a reason to restart;
a negative running total is.*

## Approach

1. Seed both `best` and `current` with `nums[0]`. That handles index 0 and,
   crucially, means neither ever has to represent "nothing chosen yet".
2. Walk `i` from `1` to `n-1`. At each step:
   - If `current < 0`, the prefix ending at `i-1` is a liability — discard it
     and set `current = nums[i]`.
   - Otherwise extend: `current = current + nums[i]`.
3. Then, and only then, fold `current` into `best` if it is larger.
4. Return `best`.

Two orderings are load-bearing:

- **Update `current` before comparing to `best`.** Reversed, the comparison
  measures the window ending at `i-1` a second time and never sees the one
  ending at `i` — the last element of the array would be ignored entirely.
- **The loop starts at `1`, not `0`.** Index 0 is already inside both seeds;
  starting at `0` would run `current = nums[0] + nums[0]` on the first step and
  double-count it. On `[3, -10]` that returns `6`.

### Why it's correct

**Invariant**: at the end of the iteration that visits index `i`, `current`
holds the maximum sum over all non-empty subarrays that end exactly at `i`, and
`best` holds the maximum over all non-empty subarrays ending at any index `≤ i`.

The `best` half is maintained trivially — it is a running maximum over values
that are, by the `current` half, exactly the per-index optima. So everything
rests on the `current` half.

**Why the recurrence is exhaustive.** Any non-empty subarray ending at `i` is
either the single element `[nums[i]]`, or it is some longer run, and every
longer run ending at `i` is (a subarray ending at `i-1`) followed by `nums[i]`.
Those two cases cover all of them with no overlap, so

```text
current[i] = max(nums[i], current[i-1] + nums[i])
```

is a complete case split, not a heuristic. The code writes it as a branch
instead of a `max`, which is the same thing: `current[i-1] + nums[i] > nums[i]`
holds exactly when `current[i-1] > 0`. So "extend if the previous total is
positive, restart otherwise" is not a greedy guess — it is the arithmetic
comparison of the only two candidates, evaluated in closed form.

**The `current == 0` boundary is genuinely free.** When `current` is zero the
code takes the `else` branch and computes `0 + value == value`, which is exactly
what the `if` branch would have assigned. So `< 0` and `<= 0` give identical
output on every input; I checked this over several thousand random arrays and
found no divergence. Worth knowing so you don't waste time in review deciding
the boundary is a bug.

**Termination and the edge of the range.** `range(1, len(nums))` is finite and
the body does no jumping, so termination is immediate. The interesting edges are
the two ends. At the low end, `n == 1` makes the range empty: the loop body
never executes and the function returns `nums[0]`, which is correct because the
only non-empty subarray is the whole one-element array — this is why seeding
with `nums[0]` rather than `0` or `-inf` matters. At the high end, the last
iteration is `i == n-1`, so the subarray ending at the final element does get
its chance; an off-by-one that wrote `range(1, len(nums) - 1)` would silently
drop it, and on `[1, 2, 100]` would return `3`.

The step I would re-derive rather than trust, coming back to this cold, is the
equivalence between `current < 0` and `current + value < value`. It is obvious
once written down — subtract `value` from both sides — but it is the hinge that
turns the DP recurrence into this particular branch, and it is easy to
misremember as a test on `value`.

## Solution

```python
# 53. Maximum Subarray (Medium) - Kadane: one pass carrying the best sum ending at the current index. O(n) time, O(1) space.
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:

        # Two different quantities, and confusing them is the whole problem:
        #
        #   `best`    - the largest sum of ANY subarray seen so far. This is
        #               the answer.
        #   `current` - the largest sum of a subarray that ENDS EXACTLY at the
        #               index being visited. Not the answer, the state.
        #
        # Both start at nums[0] rather than at 0, and that is load-bearing.
        # Every subarray is non-empty, so on an all-negative input the answer
        # is negative; seeding `best` with 0 returns 0 on [-5, -2, -9] where
        # the answer is -2. nums[0] is safe to read because the constraints
        # promise 1 <= nums.length.
        best = nums[0]
        current = nums[0]

        # Index 0 is already folded into the two seeds above, so the scan
        # starts at 1. Starting at 0 would count nums[0] twice - `current`
        # would become nums[0] + nums[0] on the first step.
        for i in range(1, len(nums)):
            value = nums[i]

            # The single decision Kadane makes, once per element: does the
            # subarray ending here START here, or does it EXTEND the one that
            # ended at i-1?
            #
            # Note the test is on `current`, the running sum, NOT on `value`.
            # A negative element is no reason to restart - on [4, -1, 4] the
            # right answer crosses the -1 and totals 7, while a rule that
            # restarted on every negative element returns 4. What makes a
            # prefix worth dropping is that the prefix itself sums to
            # something negative, i.e. it would cost more than it contributes.
            if current < 0:
                current = value

            else:
                current = current + value

            # The boundary case current == 0 takes this else branch and gives
            # current + value == value, which is exactly what the if branch
            # would have produced. So `< 0` and `<= 0` behave identically here
            # and neither is a bug; nothing hinges on which was written.

            # Fold into the running maximum AFTER `current` has been updated
            # for this index. Comparing first would measure the window ending
            # at i-1 against itself and miss the one ending at i entirely.
            if current > best:
                best = current

        return best
```

[solution.py](solution.py) · [raw submission](../../data/raw/maximum-subarray.py)

## Why this approach

| Alternative | Cost | Why Kadane beats it |
|---|---|---|
| Brute force over every `(start, end)` pair, summing each | O(n³) time, O(1) space | At `n = 10⁵` this is astronomically over budget. Even the O(n²) refinement — extend `end` and keep a running sum — is ~5 × 10⁹ additions and still TLEs by a wide margin. |
| Prefix sums, then for each `end` find the smallest earlier prefix | O(n) time, O(1) space if you track the running minimum | **Correct and genuinely equivalent** — `best = max over end of (prefix[end] - min prefix before end)`, and tracking that minimum inline makes it a one-pass scan too. It is the same algorithm wearing different clothes, and it is worth knowing because it generalises where Kadane does not (see [Subarray Sum Equals K](../0560-subarray-sum-equals-k/README.md), where the prefix framing is mandatory and Kadane is useless). Kadane wins here only on directness: no second array, no separate "have I seen a prefix yet" bookkeeping. |
| Divide and conquer: best in the left half, best in the right half, best crossing the midpoint | O(n log n) time, O(log n) stack | Correct, and the reason "Divide and Conquer" is a topic tag — it is the intended *second* solution, and a classic interview follow-up. But it is strictly worse asymptotically, much fussier to write (the crossing case needs its own two scans outward from the midpoint), and the recursion adds stack depth for nothing. Know it exists, in case an interviewer asks for it by name. |
| Sliding window with a shrink step | — | **Wrong**, not just slow, and it is the tempting mistake because "contiguous subarray" smells like a window problem. Sliding windows need a monotone validity condition — growing the window must move some quantity in one direction. With negative numbers it does not: adding an element can raise *or* lower the sum, so there is no rule for when to shrink. On `[4, -6, 5]` there is no window discipline that lands on `[5]`. |
| Seed `best = 0` and skip the all-negative case | — | **Wrong** on `[-5, -2, -9]`, returning `0` instead of `-2`. It passes every test whose array contains at least one positive number, which is most hand-written tests — a silent failure that survives casual testing. |

## Complexity

- **Time — O(n)**. One pass, with a constant number of comparisons and one
  addition per element. There is no inner loop and nothing is revisited, which
  is why this lands at the 96th percentile: at 10⁵ elements the runtime is
  essentially the cost of the Python-level iteration itself.
- **Space — O(1)**. Two integers, `best` and `current`, plus the loop variables.
  Nothing scales with the input — notably, no prefix-sum array, which is where
  the memory advantage over the prefix-minimum formulation would show if that
  version materialised its array.

## Pitfalls

- **Seeding `best = 0` (or `current = 0`).** Returns `0` on `[-5, -2, -9]` where
  the answer is `-2`. This is *the* bug in this problem. It hides on any input
  containing a positive number, so it survives casual testing and dies on the
  official all-negative case.
- **Testing the element instead of the running sum.** Writing
  `if value < 0: current = value` returns `4` on `[4, -1, 4]` (answer `7`) and
  `5` on `[-3, 8, -2, 5, -9]` (answer `11`). It is a plausible-looking one-word
  slip that makes the algorithm merely "longest run of non-negatives".
- **Starting the loop at `0` after seeding with `nums[0]`.** The first iteration
  computes `nums[0] + nums[0]`. On `[3, -10]` you get `6` instead of `3` — and
  on an array whose first element is negative it may even look right, because
  doubling a negative makes `current` smaller and the seed still wins.
- **Comparing to `best` before updating `current`.** The subarray ending at the
  final index never gets measured. On `[1, 2, 100]` this returns `3`.
- **Returning `current` instead of `best`.** `current` is the best sum ending at
  the *last* index, which is a different question. On `[-3, 8, -2, 5, -9]` it
  returns `2` instead of `11`. The two variables existing separately is the
  point; collapsing them is the mistake.
- **Trying to also return the subarray without re-deriving the bounds.** The
  moment you need the start and end indices too, you must record the start each
  time `current` restarts and snapshot both ends each time `best` improves —
  snapshotting only at the improvement is not enough, because the restart
  happened earlier. This is a common interview follow-up and it is not a
  one-line change.
- **Worrying about the `< 0` versus `<= 0` boundary.** It is not a bug — see the
  correctness section. Time spent here is time not spent on the seed value,
  which is where the real bug lives.

## Redo from scratch

1. Ask the local question: *what is the best subarray ending exactly at `i`?*
2. Write the recurrence `current[i] = max(nums[i], current[i-1] + nums[i])`, then
   notice that the `max` resolves to "restart iff `current[i-1] < 0`".
3. Seed `best = current = nums[0]` — **never `0`** — and start the loop at `1`.
4. Update `current` first, then fold into `best`.
5. Test `[-5, -2, -9]` (all negative — the seed trap), `[4, -1, 4]` (crossing a
   negative element), `[4, -6, 5]` (dropping a sunk prefix), `[7]` (single
   element, empty loop).

Be able to justify out loud: **why the two-case recurrence is exhaustive** —
that every subarray ending at `i` either starts at `i` or extends one ending at
`i-1`, with no third possibility, which is what makes this a complete DP rather
than a greedy hunch. And second: **why `current < 0` is the right test** — that
it is algebraically identical to `current + value < value`, i.e. to asking which
of the two candidates is larger. If you can state both, the variants (maximum
product, best time to buy and sell stock, maximum circular subarray) are all the
same machine with a different fold.

## Related problems

- [Best Time to Buy and Sell Stock](../0121-best-time-to-buy-and-sell-stock/README.md)
  — solved. Literally this problem in disguise: run Kadane over the array of
  day-to-day *differences* and you get the best single trade. Seeing that
  equivalence is the fastest way to stop treating the two as separate memorised
  templates.
- [Subarray Sum Equals K](../0560-subarray-sum-equals-k/README.md) — solved, in
  the same batch as this one. The instructive contrast: it also asks about
  contiguous subarray sums, but *counting* them forces the prefix-sum-plus-hash
  framing, and no Kadane-style "best ending here" scalar can answer it. Read the
  two together to see which question shape each tool fits.
- [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/)
  — not solved yet, and the natural next one. Same skeleton, but you must carry
  **two** running values (the best and the worst product ending here), because a
  large negative times a negative becomes the new maximum. It is the problem that
  tests whether you understood *why* one scalar sufficed here.
- [Maximum Absolute Sum of Any Subarray](https://leetcode.com/problems/maximum-absolute-sum-of-any-subarray/)
  — not solved yet. Run this scan twice, once for the maximum and once for the
  minimum, and take the larger magnitude. A cheap, satisfying reuse that makes
  the "best ending here" state explicit.
- [Longest Turbulent Subarray](https://leetcode.com/problems/longest-turbulent-subarray/)
  — not solved yet. Same "best thing ending at `i`" pattern with a different
  local rule (alternating comparisons), and it drives home that Kadane is a
  *shape* of dynamic programming, not a formula about sums.
- [Range Sum Query - Immutable](../0303-range-sum-query-immutable/README.md) —
  solved. The prefix-sum primitive that the alternative formulation above is
  built on. Worth a glance to see the array this solution deliberately avoids
  materialising.
