# 121. Best Time to Buy and Sell Stock

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Dynamic Programming |
| **Solved** | 2026-09-17 |
| **Runtime** | 18 ms (96.35th percentile) |
| **Memory** | 28.6 MB (76.57th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/best-time-to-buy-and-sell-stock/ |

## The problem

**Given** an array `prices` where `prices[i]` is the price of one share on day
`i`.

**Return** the largest profit obtainable from **one** buy followed by **one**
sell, where the buy day must come strictly before the sell day. You return the
profit as an integer, not the pair of days. If no pair of days yields a positive
profit, return `0` — you are permitted to decline to trade, and that is what the
`0` means.

Two things to be precise about. Exactly **one** transaction: you may not buy and
sell repeatedly (that is Stock II). And the **order is enforced** — you cannot
sell on day 2 and buy on day 5, which is why the answer is not simply
`max(prices) - min(prices)`.

**Guaranteed**: `prices` is non-empty, and every price is non-negative. The
non-negativity matters less than it looks; what actually matters is that a
zero-profit answer is always available, so the result is never negative.

```text
def maxProfit(self, prices: list[int]) -> int
```

### Examples (mine, not LeetCode's)

| `prices` | Returns | Why |
|---|---|---|
| `[2, 7, 1, 9]` | `8` | The best buy is *not* the global minimum-then-maximum in the obvious spot: buy at `1` (day 2), sell at `9` (day 3). Confirms the scan keeps improving the minimum as it goes rather than fixing it early. |
| `[5, 1, 4, 0, 3]` | `3` | **Counterexample to "take the global min and the global max".** The global min is `0` at day 3 and the global max is `5` at day 0, which are in the wrong order. The true answer is buy `1` sell `4`. A `max(prices) - min(prices)` solution returns `5`. Verified. |
| `[3, 2, 1]` | `0` | Prices only fall, so no profitable pair exists and the "don't trade" answer is returned. This is what the `max_price = 0` seed is for. |
| `[1]` | `0` | **Edge case:** a single day. There is no later day to sell on, the loop runs once and only updates `min_price`, and `0` comes back. |
| `[4, 4, 4]` | `0` | A flat series. The `elif` computes `4 - 4 = 0`, which is not `> 0`, so nothing is recorded. Selling at the price you bought at is not a profit. |
| `[0, 0, 10]` | `10` | Price `0` is legal and is a valid buy. Shows why `min_price` must be seeded at `float("inf")` and not at `0`. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= prices.length <= 10^5` | The upper bound rules out the obvious nested loop: **10⁵ days means an O(n²) pairwise scan is ~5 × 10⁹ comparisons, hopeless in Python**, so the solution must be a single pass (or at worst `n log n`). It also makes O(n) *extra* memory — a suffix-maximum array, say — technically affordable but wasteful, since a single scalar carries the same information. The lower bound of `1` rules in the empty-array question entirely: `prices` is never empty, so no guard is needed, and the `for` loop over one element is a well-defined base case that leaves `max_price` at its seed. |
| `0 <= prices[i] <= 10^4` | Prices are **non-negative**, which is exactly why `min_price = float("inf")` is the right sentinel and `min_price = 0` would be a bug — a seed of `0` is below every legal price, so it would never be replaced and every "profit" would be computed against a day that does not exist. The bound also caps the answer at 10⁴, comfortably inside a machine integer in any language, so nothing here needs overflow care. |

## Key insight

For each day, ask only one question: *if I sell today, what is the best I could
have done?* The answer depends on precisely one number — the cheapest price
**strictly before today** — and that number is trivially maintained as you sweep
left to right. So the two-dimensional search over (buy day, sell day) collapses
into a one-dimensional sweep carrying a single running minimum, and the
ordering constraint stops being something you check and becomes something the
sweep direction enforces for you.

## Approach

1. Seed `max_price = 0` — the profit of not trading, and the floor on the
   answer.
2. Seed `min_price = float("inf")` so that day 0 is unconditionally cheaper.
3. Sweep the array left to right. For each `current`:
   - if `current < min_price`, it is the new cheapest buy candidate for every
     later day;
   - otherwise, consider selling today against `min_price` and keep the profit
     if it improves on `max_price`.
4. Return `max_price`.

The load-bearing ordering is **the sweep direction**, not anything inside the
loop: because `min_price` is only ever drawn from days already visited, a sale
is never matched against a purchase in its own future. That is the entire
mechanism for "buy before sell", and it is invisible — there is no index
comparison anywhere in the code.

### Why it's correct

**Invariant**: before processing day `i`, `min_price` is the minimum of
`prices[0..i-1]` (or `+∞` when `i = 0`), and `max_price` is the best profit
achievable by any pair `(buy, sell)` with `buy < sell <= i - 1`.

Both halves are maintained by the body. The first branch restores the minimum
when day `i` beats it. The second branch considers the single best sale on day
`i`: over all valid buy days `b < i`, `prices[i] - prices[b]` is maximised by
taking the smallest `prices[b]`, which is exactly `min_price`. So the best pair
ending at `i` is examined, and combined with `max_price`'s existing value — the
best pair ending anywhere earlier — the invariant holds for `i + 1`. At the end
`i = n`, which is the answer over all pairs.

**Why the `elif` loses nothing.** The one place this could go wrong is the day
when both branches would have something to say. It cannot: if `current <
min_price` fires, then afterwards `min_price == current`, so the profit the
second branch would compute is `current - current = 0`, and `max_price` is
already `>= 0`. The skipped update is a no-op. (Note this depends on
`max_price` being seeded at `0` rather than at `-∞`, which is a mild coupling
between two lines that look independent.)

**Termination and the edge of the range.** The `for` visits each element exactly
once and ends; there are no indices and so no off-by-one to get wrong — a real
advantage of iterating over values rather than `range(len(prices))`. The one
boundary worth stating is the first iteration: `min_price` is `+∞`, so the first
branch always fires on day 0 and the second never does, which is right, since
there is no day before day 0 to have bought on. The last iteration is
unremarkable: day `n-1` can sell but its update to `min_price`, if it fires, is
never read again.

## Solution

```python
# 121. Best Time to Buy and Sell Stock (Easy) - one pass tracking the cheapest day seen so far and the best profit against it. O(n) time, O(1) space.
class Solution:
    def maxProfit(self, prices: list[int]) -> int:

        # NAMING WART worth knowing about: `max_price` does not hold a price.
        # It holds the best PROFIT found so far. `min_price` really is a price.
        # Seeding the profit at 0 is what encodes "you are allowed to not
        # trade at all" - on a strictly falling series nothing ever beats 0,
        # so 0 is returned rather than a negative loss.
        max_price = 0

        # float("inf") so that the very first day is unconditionally cheaper
        # and becomes the buy candidate. A sentinel of 0 would be wrong here
        # (prices can be 0, and nothing would ever go below it).
        min_price = float("inf")

        # Single left-to-right pass. The direction is the whole point: buying
        # must happen before selling, so by only ever comparing `current`
        # against a minimum drawn from STRICTLY EARLIER days, the ordering
        # constraint is enforced for free and never has to be checked.
        for current in prices:

            # Case 1: today is the cheapest day so far, so it becomes the new
            # buy candidate for every future day.
            if current < min_price:
                min_price = current

            # Case 2 (elif, not if): today is not a new minimum, so selling
            # today against the cheapest earlier day is worth checking.
            #
            # The `elif` is safe rather than merely tidy. If the first branch
            # fired then current == min_price afterwards, so the profit this
            # branch would compute is current - current = 0, which can never
            # beat max_price (already >= 0). Skipping it loses nothing.
            # Equally it is NOT an optimisation you may invert: swapping the
            # branches, so the profit check runs first, would let day i sell
            # against itself - still 0, so still harmless here, but only by
            # accident of the >= 0 seed.
            elif current - min_price > max_price:
                max_price = current - min_price

        # 0 if no profitable pair exists, which is the required answer for a
        # series that only ever falls.
        return max_price
```

[solution.py](solution.py) · [raw submission](../../data/raw/best-time-to-buy-and-sell-stock.py)

## Why this approach

| Alternative | Cost | Why the one-pass minimum beats it |
|---|---|---|
| Brute force: every pair `(i, j)` with `i < j` | O(n²) time, O(1) space | At `n = 10⁵` that is ~5 × 10⁹ pairs. TLE by three orders of magnitude. The waste is that for a fixed `j` it re-scans all of `prices[0..j-1]` to find a minimum it already computed for `j - 1`. |
| `max(prices) - min(prices)` | O(n) time and **wrong** | Ignores the ordering requirement entirely. On `[5, 1, 4, 0, 3]` it returns `5 - 0 = 5`; the true answer is `3`. Verified, not recalled. This is the tempting one-liner and it is wrong on any input whose cheapest day comes after its dearest. |
| Sort the prices, then take the two ends | O(n log n) and **wrong** | Same defect, more expensively: sorting is precisely the operation that destroys the day ordering the problem is about. Returns `4` on `[5, 1]` where the answer is `0`. |
| Suffix-maximum array: `best[i] = max(prices[i..])`, answer `max(best[i+1] - prices[i])` | O(n) time, **O(n) space** | Correct, and a perfectly reasonable way to see the problem (look *forwards* for the best sale instead of backwards for the best buy). It just spends an `n`-element array to store what the prefix-minimum version holds in one scalar, and needs a second pass. |
| Kadane's maximum subarray on the difference array `prices[i] - prices[i-1]` | O(n) time, O(1) space if computed on the fly | Genuinely equivalent — the profit of a trade is the sum of daily deltas over the holding period, so the best trade is the maximum-sum contiguous run. Same complexity, and worth knowing because it is the bridge to *Maximum Subarray*. It is only *presented* worse: you must remember to clamp at `0` and to handle the empty run, which is what `max_price = 0` does here for free. |
| DP with explicit state: `hold[i]` = best balance holding a share, `free[i]` = best balance holding none | O(n) time, O(1) space with rolling variables | Also correct, and it is the formulation that *generalises* — Stock II, III, IV and the cooldown variant are all this recurrence with more states. Overkill for a single transaction, where `hold` is just `-min_price` and `free` is just `max_price` under different names. Learn it when you get to Stock III; do not reach for it here. |

## Complexity

- **Time — O(n)**. One pass, doing a constant amount of arithmetic and at most
  two comparisons per element. Nothing is revisited, and there is no inner loop
  to amortise.
- **Space — O(1)**. Two scalars, `max_price` and `min_price`, neither of which
  grows with the input. The 28.6 MB reported is essentially the input array
  itself.

## Pitfalls

- **`max(prices) - min(prices)`.** Returns `5` on `[5, 1, 4, 0, 3]` instead of
  `3`. It is right on plenty of inputs — any input where the cheapest day
  precedes the dearest — which is what makes it survive a casual test.
- **Seeding `min_price = 0` instead of `float("inf")`.** Prices may be `0`, so
  `0` is not a safe "smaller than anything" sentinel. With that seed,
  `[0, 0, 10]` still works by luck but `[5, 3, 6]` reports `6` (selling against a
  phantom day priced at `0`) rather than `3`. Using `prices[0]` as the seed is
  the other safe choice and reads more clearly.
- **Seeding `max_price` at `-inf` or at `prices[1] - prices[0]`.** Then a falling
  series like `[3, 2, 1]` returns a negative number instead of `0`. The problem
  lets you decline to trade; a negative answer is never correct.
- **Allowing buy and sell on the same day.** Yields `0` rather than a wrong
  answer here, so it hides — but it is the bug that bites when the same code is
  adapted to a problem where prices can be negative.
- **Turning the `elif` into an `if` without thinking.** Harmless as written (the
  extra check computes `0`), and it is worth knowing *why* it is harmless rather
  than assuming it: if you also change the `max_price` seed to `-inf`, the two
  edits interact and the flat-series and falling-series cases both break.
- **The name `max_price` does not hold a price.** It holds the best profit. This
  is the thing most likely to confuse a cold reader of this file, and renaming it
  to `max_profit` would be an improvement that the AST gate deliberately forbids
  here — the annotation may only add comments.
- **Reading the array right to left** on the theory that it is symmetric. It is
  not: reversed, you would be tracking a running *maximum* as the sell candidate
  and subtracting the current price. Both work, but mixing the two halves up
  gives you the sign backwards.

## Redo from scratch

1. Say the reframing first: **fix the sell day, ask for the cheapest day before
   it.** The pair search collapses to a scan.
2. Seed `best_profit = 0` (declining to trade is legal) and
   `cheapest = float("inf")` (prices can be `0`).
3. One left-to-right pass. Update the cheapest price, or update the best profit
   against it.
4. Return `best_profit`.
5. Test `[5, 1, 4, 0, 3]` (global min and max in the wrong order), `[3, 2, 1]`
   (no profit), `[1]` (single day).

Be able to justify out loud: **where the "buy before sell" constraint is
enforced in the code.** The answer — that it is implicit in the sweep direction,
because `min_price` only ever summarises days already passed — is the whole
idea, and if you cannot point at it you will not be able to adapt this to
Stock II or to the suffix-maximum variant. Second: **why `elif` and not `if`**,
and what else in the function that answer depends on.

## Related problems

- [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) — not
  solved yet, and the one to do next. This problem *is* Maximum Subarray applied
  to the array of consecutive daily differences; solving both makes the running
  minimum and Kadane's running sum visibly the same trick seen from two ends.
- [Best Time to Buy and Sell Stock II](../0122-best-time-to-buy-and-sell-stock-ii/README.md)
  — solved. Unlimited transactions, which collapses to summing every positive
  daily delta. The instructive part is *why* the greedy is suddenly legal there
  and is not here: with one transaction you must commit to a single interval,
  and greed over intervals is not the same as greed over days. Read the two
  pages back to back — one keeps a running minimum, the other throws the
  minimum away entirely, and the difference is exactly the transaction cap.
- [Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)
  and [IV](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) —
  not solved yet. At most two, then at most `k`, transactions. This is where the
  explicit `hold`/`free` DP state stops being overkill and becomes the only
  tractable formulation. If you can restate *this* solution as that DP, those two
  become routine.
- [Best Time to Buy and Sell Stock with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/)
  — not solved yet. Adds a third state to the same machine. Good for checking
  that you understand the state graph rather than having memorised two variables.
- [Maximum Difference Between Increasing Elements](https://leetcode.com/problems/maximum-difference-between-increasing-elements/)
  — not solved yet. Literally this problem with the "return `0` if nothing
  qualifies" rule changed to "return `-1`", which is a neat test of whether you
  know what the `0` seed was doing.
