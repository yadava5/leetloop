# 122. Best Time to Buy and Sell Stock II

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Dynamic Programming, Greedy |
| **Solved** | 2026-09-17 |
| **Runtime** | 0 ms (100.00th percentile) |
| **Memory** | 20.1 MB (99.71th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/ |

## The problem

**Given** an array `prices` where `prices[i]` is the price of one share on day
`i`.

**Return** the maximum total profit obtainable, as an integer, when you may buy
and sell **as many times as you like**. The two rules that shape everything:
you may hold **at most one share at a time** — so you must sell before you buy
again — but you **may sell and re-buy on the same day**. You return the profit
only, not the list of trades.

That second rule is the one that makes this problem different in kind from
Stock I rather than merely harder. Because a sale and a purchase can share a
day, holding a share from day `i` to day `j` is worth exactly the same as doing
`j - i` separate one-day trades. Nothing is lost by chopping a long hold into
its individual days, and that is the hinge the whole solution turns on.

**Guaranteed**: `prices` is non-empty and every price is non-negative. There is
no transaction fee and no cooldown — both of those exist as separate problems
precisely because either one destroys the argument below.

```text
def maxProfit(self, prices: list[int]) -> int
```

### Examples (mine, not LeetCode's)

| `prices` | Returns | Why |
|---|---|---|
| `[4, 9]` | `5` | The minimal interesting case: one up move, banked whole. |
| `[3, 8, 2, 6]` | `9` | **Counterexample to "buy the global low, sell the global high".** That approach picks `2 → 6` for `4`. Taking both rises, `5` and `4`, gives `9`. Unlimited transactions means you want *every* climb, not the biggest one. |
| `[1, 5, 3, 9]` | `10` | **Counterexample to "just hold from start to end".** Holding `1 → 9` yields `8`; stepping out over the `5 → 3` dip and back in yields `4 + 6 = 10`. The dip is what a buy-and-hold strategy pays for and the greedy does not. |
| `[7, 5, 4, 1]` | `0` | A monotonically falling series. No `rise` is ever positive, `total` stays at its seed, and declining to trade is the right answer. |
| `[6]` | `0` | **Edge case:** one day. `range(1, 1)` is empty, the loop body never runs, `0` comes back. This is why the `range` starting at `1` needs no length guard in front of it. |
| `[2, 2, 2]` | `0` | Flat. `rise` is `0` each time and `0 > 0` is false, so nothing accumulates — a flat move is not a profit, and using `>=` here would still give `0` but for the wrong reason. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= prices.length <= 3 * 10^4` | The lower bound of `1` rules out the empty array, so the single-element case is the smallest input and `range(1, len(prices))` handles it by being empty — no explicit guard is needed. The upper bound of 3 × 10⁴ is the interesting half: it is small enough that an O(n²) interval search (~9 × 10⁸ operations) is clearly out in Python, but also small enough that a full `O(n)`-space DP table would pass comfortably. So the bound rules out brute force over intervals while *not* forcing the O(1)-space form — that one is chosen because it is simpler, not because the limit demands it. |
| `0 <= prices[i] <= 10^4` | Prices are bounded and non-negative, so the total profit is at most about 3 × 10⁴ × 10⁴ = 3 × 10⁸ — inside a 32-bit integer, so no overflow care is needed even in a language that would care. Non-negativity also means the answer is never forced negative: a zero-profit "make no trades" answer is always legal, which is what the `total = 0` seed encodes. Note what this constraint does *not* say: nothing forbids equal adjacent prices, so the flat case is real input and the strict `> 0` test is what handles it. |

## Key insight

With unlimited same-day transactions, a trade held across several days is worth
exactly the sum of its daily price changes — so there is no reason to think in
terms of intervals at all. Decompose every possible strategy into single-day
holds, and the question becomes: for each adjacent pair of days, do I want to be
holding a share overnight? The answer is independently "yes" whenever the price
rises and "no" otherwise, with no interaction between days. **The profit is the
sum of the positive daily deltas**, and there is nothing left to optimise.

## Approach

1. Seed `total = 0` — the profit of making no trades, and the answer's floor.
2. Walk `index` from `1` to `len(prices) - 1`.
3. At each step compute `rise = prices[index] - prices[index - 1]`, the
   overnight change into today.
4. If `rise > 0`, add it to `total`. Otherwise ignore the day entirely.
5. Return `total`.

Two details are load-bearing, and neither is about the loop's *order* — the
terms are a sum, so they could be accumulated in any order at all:

- **The range starts at `1`.** Each iteration reads `prices[index - 1]`, so
  `index = 0` has no predecessor. In Python starting at `0` does not raise; it
  reads `prices[-1]`, the final element, and quietly adds a bogus term.
- **The subtraction points forwards in time** (`prices[index] - prices[index - 1]`,
  today minus yesterday). Written the other way, every sign flips and the
  function returns `0` on every rising series — an answer that looks plausible
  because it is the same answer a falling series legitimately gets.

### Why it's correct

The state a strategy can be in on any given day is binary — holding a share or
not — so the **invariant** is best stated over the sum rather than over a loop
variable: after processing index `i`, `total` equals the maximum profit
obtainable by trading only within `prices[0..i]`. The step from `i - 1` to `i`
adds `max(0, prices[i] - prices[i-1])`, which is exactly the value of the choice
"hold overnight from `i-1` into `i`, or don't".

What licenses treating that choice as independent is the **exchange argument**,
and it runs both directions:

- *The greedy is achievable.* Summing positive deltas describes a real, legal
  strategy: buy at the start of every maximal rising run and sell at its end.
  Consecutive positive deltas telescope — `(p₂ - p₁) + (p₃ - p₂) = p₃ - p₁` — so
  a run of up days is one ordinary buy-and-hold trade, not a stack of overlapping
  ones. At no point is more than one share held.
- *Nothing can beat it.* Take any optimal strategy. Its profit is a sum of
  `prices[sell] - prices[buy]` terms, and each such term telescopes into the sum
  of the daily deltas from `buy` to `sell`. So any strategy's profit is a sum of
  a subset of the daily deltas, with each delta used at most once (the holds do
  not overlap). The greatest such subset sum is obtained by taking every positive
  delta and no negative one — which is precisely what this code computes. Hence
  no strategy exceeds it.

This is the step to be suspicious of when you redo the problem, because it is
the step that **stops being true** the moment a cost is attached to trading. Add
a transaction fee and chopping a hold into daily pieces multiplies the fee;
add a cooldown and the pieces are no longer schedulable. Both variants exist as
separate LeetCode problems, and neither can be solved by this five-line loop.
The greedy here is not "greedy usually works" — it is licensed by the specific
absence of any per-transaction cost.

**Termination and the edge of the range.** `range(1, len(prices))` is finite and
the body does not touch `index`, so the loop ends after `n - 1` iterations. The
bounds are right at both ends: the first iteration is `index = 1`, pairing days
0 and 1, which is the earliest pair that exists; the last is
`index = n - 1`, pairing the final two days, and `range`'s exclusive upper bound
is what stops `index` from reaching `n` and reading off the end. When `n = 1`
the range is empty and the seed is returned. There is no off-by-one available
here except the two named above — starting at `0`, or writing `range(len(prices))`
and indexing `index + 1`, which needs the upper bound dropped to `n - 1` to stay
in range.

## Solution

```python
# 122. Best Time to Buy and Sell Stock II (Medium) - greedy: bank every upward day-to-day move. O(n) time, O(1) space.
class Solution:
    def maxProfit(self, prices: list[int]) -> int:

        # The running answer. Seeded at 0, which is also the correct answer for
        # a single-day array and for any series that never rises - you are
        # allowed to make no trades at all, so the result is never negative.
        total = 0

        # Start at 1, not 0. Every iteration looks BACKWARDS at index - 1, so
        # index 0 has no partner and must be skipped. Starting at 0 would read
        # prices[-1], which in Python is the LAST element rather than an error:
        # a silent wrong answer, not a crash. That is the load-bearing detail
        # in this line.
        for index in range(1, len(prices)):

            # The change in price from yesterday to today. Note the direction:
            # today minus yesterday. Reversing it flips the sign of every term
            # and the function returns 0 on every rising series.
            rise = prices[index] - prices[index - 1]

            # Keep only the up days. A day where the price falls or stays flat
            # contributes nothing, because you simply hold no shares over it.
            #
            # Why this is allowed to be this crude: buying and selling on the
            # same day is permitted, so a real trade held from day i to day j
            # can be split into j - i one-day trades with the identical total
            # profit. Summing the positive one-day moves therefore reaches the
            # optimum, and no bookkeeping of "am I currently holding?" is
            # needed. That equivalence is the entire proof.
            if rise > 0:
                total += rise

        return total
```

[solution.py](solution.py) · [raw submission](../../data/raw/best-time-to-buy-and-sell-stock-ii.py)

## Why this approach

| Alternative | Cost | Why the delta sum beats it |
|---|---|---|
| Buy at the global minimum, sell at the global maximum | O(n) time and **wrong** | It solves Stock I's problem, not this one. On `[3, 8, 2, 6]` it returns `4` where the answer is `9`. The whole point of unlimited transactions is that you collect every climb, not the largest one. |
| Buy on day 0, sell on day `n - 1` | O(n) time and **wrong** | On `[1, 5, 3, 9]` it returns `8` where the answer is `10`. Holding through the `5 → 3` dip pays for that dip; the greedy sits it out. |
| Find maximal rising runs explicitly — track a `buy` index, sell when the price turns down | O(n) time, O(1) space | **Correct, and genuinely equivalent** — it produces exactly the same number, because a run's endpoints telescope into its deltas. It is just more code and more state (a buy price, a "currently holding" flag) and its edge case — a run still open when the array ends — is a classic place to drop the final trade. Worth being able to write, since it is the version that survives adding a transaction fee. |
| Explicit DP over states: `hold[i]` = best balance while holding, `free[i]` = best while not | O(n) time, O(1) space with rolling scalars | Correct and the *generalising* formulation: `free = max(free, hold + p)`, `hold = max(hold, free - p)`. This is the one to reach for in Stock III/IV, with a fee, or with a cooldown. Here it computes the same answer with four comparisons per day instead of one, and its correctness is no more obvious than the exchange argument above. |
| Try every set of non-overlapping intervals | Exponential | Complete and hopeless. Even restricting to single intervals is O(n²) ≈ 9 × 10⁸ at `n = 3 × 10⁴`, already too slow in Python, and single intervals are the wrong search space anyway. |

## Complexity

- **Time — O(n)**. One pass over `n - 1` adjacent pairs, doing one subtraction,
  one comparison and at most one addition each. No inner loop, nothing revisited.
  The reported 0 ms is the whole story: this is about as little work as an array
  problem can be.
- **Space — O(1)**. Two scalars, `total` and `rise`, plus the loop index. Nothing
  allocated that scales with the input; the 20.1 MB reported is essentially the
  interpreter plus the input array itself.

## Pitfalls

- **Solving Stock I by mistake.** Tracking a running minimum and one best profit
  returns `5` on `[3, 8, 2, 6]` instead of `9`. The two problems have near-identical
  statements and *opposite* right answers, so read the transaction cap first,
  every time.
- **`range(0, len(prices))` instead of `range(1, ...)`.** No exception is raised.
  `prices[-1]` is the last element, so on `[1, 5, 3, 9]` the first iteration adds
  `max(0, 1 - 9) = 0` — harmless by luck. But on `[9, 1, 5]` it adds
  `max(0, 9 - 5) = 4` to the true answer of `4` and returns `8`. A wrong answer
  with no crash, which is the worst kind.
- **`prices[index - 1] - prices[index]`.** Sign inverted. Returns `0` on every
  rising series, which reads as a plausible "no profit available" rather than as
  an obvious bug.
- **`if rise >= 0` instead of `> 0`.** Harmless here — adding zeros changes
  nothing — but it signals a misunderstanding that bites elsewhere: it suggests
  you think flat days are trades worth taking, and with a transaction fee
  attached, taking them loses money.
- **Assuming this greedy transfers.** It does not survive a transaction fee or
  a cooldown. On `[1, 3, 1, 3]` with a fee of `2` per transaction, this code's
  strategy nets `4 - 4 = 0` while holding nothing at all nets `0` and a single
  `1 → 3` nets `0` too; push the fee to `3` and the greedy is strictly negative
  while the right answer is `0`. Recognise what the absence of a fee bought you.
- **Overlapping holds.** Reading "sum every positive delta" as "buy on every up
  day" sounds like it could hold two shares at once across a rising run. It does
  not — consecutive deltas telescope into one buy-and-hold — but the code makes
  that invisible, and a reader trying to "fix" the phantom overlap will end up
  reintroducing the explicit-runs version for no gain.

## Redo from scratch

1. Check the transaction cap first. Unlimited transactions **and** same-day
   re-entry — that pair is the whole problem.
2. Say the decomposition out loud: a multi-day hold equals the sum of its daily
   moves, so only adjacent pairs matter.
3. Loop `index` from `1`; compute today minus yesterday; add it when positive.
4. Return the total, seeded at `0`.
5. Test `[1, 5, 3, 9]` (must beat buy-and-hold), `[3, 8, 2, 6]` (must beat global
   min-to-max), `[7, 5, 4, 1]` (falling, expect `0`), `[6]` (single day).

Be able to justify out loud: **the exchange argument** — why no strategy can
beat the sum of positive deltas, in both directions (the greedy is realisable as
legal trades; every legal strategy is a subset of the deltas). A greedy you can
only assert is a guess that happened to pass. And second: **what specifically
breaks the argument when a transaction fee is added**, since that is the exact
line between this problem and the fee variant.

## Related problems

- [Best Time to Buy and Sell Stock](../0121-best-time-to-buy-and-sell-stock/README.md)
  — solved. The one-transaction version, and the direct contrast: there you must
  commit to a single interval, so a running minimum is unavoidable; here the cap
  is gone and the minimum becomes irrelevant. Re-read the two together — the
  difference in the code is far larger than the difference in the statements.
- [Best Time to Buy and Sell Stock with Transaction Fee](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/)
  — not solved yet, and the most instructive next step from here. It is this
  problem with a fee per trade, which is exactly the assumption the exchange
  argument above leans on. The greedy dies and the `hold`/`free` DP takes over,
  which makes the DP's value concrete rather than academic.
- [Best Time to Buy and Sell Stock with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/)
  — not solved yet. Breaks the same assumption from the other side: the daily
  pieces can no longer all be scheduled. Adds a third state to the machine.
- [Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)
  and [IV](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) —
  not solved yet. At most two, then at most `k`, transactions. Between Stock I
  (`k = 1`) and this one (`k = ∞`) they are the general case, and they are where
  the DP formulation stops being optional.
- [Maximum Profit From Trading Stocks](https://leetcode.com/problems/maximum-profit-from-trading-stocks/)
  — not solved yet. Despite the name it is a knapsack with a budget, not a
  sequence-of-days problem. Useful mainly as a reminder that a similar title in
  LeetCode's "similar questions" list does not imply a similar technique.
