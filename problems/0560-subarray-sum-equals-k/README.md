# 560. Subarray Sum Equals K

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Hash Table, Prefix Sum |
| **Solved** | 2026-09-18 |
| **Runtime** | 35 ms (46.23th percentile) |
| **Memory** | 21.5 MB (99.32th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/subarray-sum-equals-k/ |

## The problem

**Given** an integer array `nums` (values may be negative or zero) and an
integer `k`.

**Return** the **number** of contiguous, non-empty subarrays whose elements sum
to exactly `k`. A count, not the subarrays themselves and not their indices.

Three things to be precise about:

- **Count, not existence.** The answer is how many, so overlapping subarrays all
  count separately. `[0, 0, 0]` with `k = 0` has six of them, not one.
- **Contiguous.** Adjacent elements only; this is not a subset-sum question.
- **Distinct by position, not by content.** Two subarrays at different index
  ranges are two answers even if they contain identical values.

**Guaranteed**: the array is non-empty. Nothing is guaranteed about signs —
`nums[i]` may be negative, zero or positive, and `k` may be negative. That
single missing guarantee is what makes this a Medium.

```text
def subarraySum(self, nums: List[int], k: int) -> int
```

### Examples (mine, not LeetCode's)

| `nums`, `k` | Returns | Why |
|---|---|---|
| `[1, 2, 3]`, `k = 3` | `2` | `[1, 2]` and `[3]`. The ordinary case: two answers, one of which starts at index 0 and can only be found via the empty-prefix seed. |
| `[3]`, `k = 3` | `1` | **Edge case, and the seed test.** The only answer is the whole array, which is the prefix minus the *empty* prefix. Drop `{0: 1}` from the map and this returns `0`. |
| `[1, -1, 0]`, `k = 0` | `3` | **Counterexample to the sliding window.** The answers are `[1, -1]`, `[1, -1, 0]` and `[0]`. A window that shrinks when the sum overshoots finds only one of them — negatives mean the running sum is not monotone, so there is no correct shrink rule. |
| `[0, 0, 0]`, `k = 0` | `6` | **Counterexample to `total += 1`.** Three singles, two pairs, one triple. The prefix `0` is hit repeatedly and its stored *count* is what makes this `6`; incrementing by one per index returns `3`. |
| `[5, -5, 5]`, `k = 5` | `3` | Both single `5`s, plus the whole array. Shows that an answer can contain a complete zero-sum stretch in its middle — there is no notion of a "minimal" answer to prefer. |
| `[1, 2, 3]`, `k = 7` | `0` | **Edge case:** no subarray qualifies. Nothing special happens; `total` is simply never incremented. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 2 * 10^4` | Two × 10⁴ is deliberately *small* — the O(n²) double loop is ~2 × 10⁸ operations, which is far too slow in Python but borderline-passable in C++. So the bound quietly permits the naive solution in a faster language while forcing the hash-map solution here; treat the O(n) method as the required one. It also rules **in** O(n) auxiliary space without a second thought: a map of at most 2 × 10⁴ prefix sums is nothing. The lower bound of `1` means the array is never empty. |
| `-1000 <= nums[i] <= 1000` | **The most important line in the problem.** Values may be negative, so prefix sums do not increase monotonically — which kills the sliding-window approach outright (see the examples table), and also kills binary search over prefix sums. Zeros are permitted too, which is what creates repeated prefix sums and therefore makes the map store *counts* rather than booleans. Had this read `1 <= nums[i]`, the intended solution would have been a two-pointer window and the problem would be Easy. |
| `-10^7 <= k <= 10^7` | `k` may be negative or zero, so nothing may assume the target is positive or that a qualifying subarray must be "long enough". The zero case is the sharp one: with `k = 0`, `counting - k` is `counting` itself, so the lookup would match the current prefix against itself if the insert happened first — which is exactly why the read-before-write order in the loop is load-bearing. The magnitude is a non-issue: `|sum| ≤ 2 × 10⁴ × 10³ = 2 × 10⁷`, so every reachable prefix sum fits comfortably and Python's integers make overflow irrelevant regardless. |

## Key insight

The sum of `nums[i..j]` is `prefix[j] - prefix[i-1]`. So asking "does this
subarray sum to `k`" is asking "do two prefix sums differ by exactly `k`" — and
for a fixed right end `j`, the qualifying left ends are precisely the earlier
prefixes equal to `prefix[j] - k`. Since you only need to *count* them, you
never need to know which ones they were: a hash map from prefix-sum value to how
many times it has occurred answers the whole question in one pass.

The thing to whisper if stuck: *stop looking for subarrays and start looking for
pairs of prefix sums.* It is the same inversion that turns Two Sum from a double
loop into a single pass — and it is exactly the same map, one index earlier.

## Approach

1. Keep `seen`, a map from prefix sum to the number of prefixes so far with that
   sum. Seed it with `{0: 1}`: the empty prefix, which has sum `0` and has
   "occurred" once before the scan begins.
2. Walk the array, maintaining `counting`, the running prefix sum including the
   current element.
3. At each element, **look up first**: add `seen[counting - k]` to `total` if
   that key exists. Each earlier prefix with that value marks a distinct start
   position for a subarray ending here and summing to `k`.
4. **Then record** the current prefix: increment `seen[counting]`.
5. Return `total`.

Two orderings are load-bearing:

- **Look up before inserting.** With `k = 0` the key being searched for *is*
  `counting`, so inserting first lets the current prefix match itself and counts
  the empty subarray once per index. On `[1, 2, 3]` with `k = 0` that returns
  `3` instead of `0`, and on `[1, -1, 0]` with `k = 0` it returns `6` instead of
  `3`. For any non-zero `k` the order happens not to matter — which is worse, not
  better, since it means the bug only shows on the one input most people forget
  to test.
- **Add the stored count, not one.** `total += seen[counting - k]`, never
  `total += 1`. See `[0, 0, 0]` above.

### Why it's correct

**Invariant**: just before the lookup for the element at index `j`, `counting`
equals `nums[0] + … + nums[j]`, and `seen` maps each value `v` to the exact
number of indices `i` in `{-1, 0, 1, …, j-1}` for which `nums[0] + … + nums[i]`
equals `v` — where `i = -1` denotes the empty prefix, contributed by the `{0: 1}`
seed. Meanwhile `total` is the exact count of qualifying subarrays that end at an
index strictly less than `j`.

**Why the count is exhaustive and non-duplicating.** Every non-empty subarray has
exactly one right endpoint, so summing over right endpoints partitions the answer
— no subarray is counted twice and none is missed, provided each iteration counts
*all* subarrays ending at `j`. A subarray ending at `j` is determined entirely by
its start `i+1`, and its sum is `counting - prefix[i]`. That equals `k` exactly
when `prefix[i] = counting - k`. By the invariant, `seen` holds the count of such
`i` over precisely the legal range (`-1` through `j-1`), so the single lookup
adds all of them and nothing else. The map holds counts rather than flags because
several distinct `i` can share a prefix value — which happens whenever the
elements between them sum to zero.

**Why the empty prefix has to be in the map.** A subarray starting at index `0`
has `i = -1`, and its sum is `counting` minus the empty prefix's `0`. Without the
seed, no start-at-zero subarray is ever counted: `[3]` with `k = 3` returns `0`,
and `[1, 2, 3]` with `k = 3` returns `1` instead of `2`, losing the `[1, 2]`. The
seed is not a defensive trick; it is the `i = -1` case of the invariant, and
writing it as a literal `{0 : 1}` is the same thing as saying the empty prefix is
a real prefix.

**Termination and the edge of the range.** The loop is a plain `for` over the
array with no early exit, so it runs exactly `n` times and stops. The edges are
where the ordering rules bite. The *first* iteration: `seen` contains only the
seed, so the lookup can only match the empty prefix — correct, since the only
subarray ending at index 0 is `nums[0]` itself. The *last* iteration: the final
insert into `seen` is dead work, as nothing is looked up afterwards — harmless,
and not worth special-casing. And note there is no post-loop pass: every subarray
was counted at its right endpoint as the scan passed over it.

I would not call any step here subtle in isolation, but the one I would re-derive
rather than trust is the claim that read-before-write only matters for `k = 0`.
It follows from `counting - k = counting` iff `k = 0`, which is immediate — yet
it is the step that makes the ordering rule feel arbitrary when you meet it cold,
and "it only breaks on one value of `k`" is exactly the kind of claim worth
re-checking rather than remembering.

## Solution

```python
# 560. Subarray Sum Equals K (Medium) - prefix sums in a hash map, counting how many earlier prefixes make the window hit k. O(n) time, O(n) space.
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:

        # Style wart, left alone because the AST gate forbids editing code:
        # `List` is used bare. LeetCode's preamble does the
        # `from typing import List` for you, so this runs there, but copying
        # this file into a plain script raises NameError on the annotation.
        # The rest of the repo uses the builtin `list[int]` form.

        # Maps a prefix sum to HOW MANY prefixes so far had that sum. The
        # count, not a boolean - several different prefixes can share a sum,
        # and each of them is a distinct subarray start.
        #
        # The {0: 1} seed is the empty prefix, and it is load-bearing: it is
        # what lets a subarray that starts at index 0 be counted. Without it,
        # nums = [3], k = 3 returns 0 instead of 1, because the only prefix
        # that makes the window work is the empty one.
        seen = {0 : 1}

        # `counting` is the running PREFIX SUM, despite the name - it counts
        # nothing. `total` is the actual count and the return value.
        counting = 0
        total = 0

        for num in nums:
            counting += num

            # Every subarray ending here is (prefix up to here) minus (some
            # earlier prefix). Its sum is k exactly when that earlier prefix
            # equals counting - k. So the number of subarrays ending at this
            # index with sum k is the number of earlier prefixes with that
            # value, which is precisely what `seen` stores.
            #
            # Add the STORED COUNT, not 1. On [0, 0, 0] with k = 0 the prefix
            # 0 is reached repeatedly, and `total += 1` returns 3 where the
            # answer is 6.
            if counting - k in seen:
                total += seen[counting - k]

            # ORDER IS LOAD-BEARING: the lookup above happens BEFORE this
            # index's own prefix is recorded. Recording first would let the
            # current prefix match itself whenever k == 0, counting the empty
            # subarray once per index - [1, 2, 3] with k = 0 would return 3
            # instead of 0. The read-then-write order is what keeps "earlier
            # prefix" strictly earlier.
            if counting not in seen:
                seen[counting] = 0
            seen[counting] += 1

        return total
```

[solution.py](solution.py) · [raw submission](../../data/raw/subarray-sum-equals-k.py)

## Why this approach

| Alternative | Cost | Why the prefix-sum map beats it |
|---|---|---|
| Brute force: every `(start, end)` pair, summing each from scratch | O(n³) time, O(1) space | Hopeless at `n = 2 × 10⁴`. Even the O(n²) version — fix `start`, extend `end` with a running sum — is ~2 × 10⁸ iterations of a Python loop, which is tens of seconds. In C++ it would squeak through, which is worth knowing when the same problem appears with the same bounds in a different language. |
| Materialise a `prefix` array, then double-loop over `(i, j)` pairs | O(n²) time, O(n) space | The same O(n²) with a nicer inner body. It is the useful *intermediate* step when deriving the solution — once the pairs are written as `prefix[j] - prefix[i]`, the hash map is the obvious next move — but it is not a solution to submit. |
| Sliding window that shrinks from the left when the sum exceeds `k` | O(n) time, O(1) space | **Wrong**, and it is the trap the problem is built around. Windows need monotonicity: growing must push the sum in one direction. Negative values break that, so "too big, shrink" is not a valid rule. On `[1, -1, 0]` with `k = 0` it finds `1` of the `3` answers. This approach *is* correct on the variant with all-positive values — which is precisely why the constraint line permitting negatives is the one to read first. |
| Sort the prefix sums and binary-search for `prefix[j] - k` | O(n log n) time, O(n) space | **Wrong as stated**, because sorting destroys the "earlier than `j`" requirement and would count prefixes from the future as valid starts. Patching it (an order-statistics tree, inserting as you go) gets you correctness at O(n log n) — strictly worse than the map for no benefit, since you never need the prefixes in sorted order, only counted by value. |
| Hash map storing a boolean "have I seen this prefix" | O(n) time, O(n) space | **Wrong**: undercounts whenever a prefix value repeats, which happens on any zero-sum stretch. `[0, 0, 0]` with `k = 0` returns `3` instead of `6`, and `[1, -1, 1, -1]` with `k = 0` returns `3` instead of `4`. The fix is one character — `+= seen[…]` rather than `+= 1` — but the failure is invisible on inputs with all-distinct prefixes. |

## Complexity

- **Time — O(n)**. One pass; each element does one addition, one dictionary
  lookup and one dictionary update, all O(1) on average. Hash collisions could
  in principle degrade this, but the keys are small integers and Python hashes
  them to themselves, so the average case is the case. The 35 ms is the cost of
  2 × 10⁴ Python-level dict operations.
- **Space — O(n)**. Worst case the map holds `n + 1` distinct prefix sums — one
  per index plus the seed — which happens whenever no prefix value repeats, e.g.
  an all-positive array. There is no way around this: the algorithm's whole
  mechanism is remembering every prefix seen. The 99th-percentile memory reading
  reflects that nothing else is allocated — no prefix array, no copy of the
  input.

## Pitfalls

- **Omitting the `{0: 1}` seed.** Every subarray starting at index 0 vanishes.
  `[3]` with `k = 3` returns `0`; `[1, 2, 3]` with `k = 3` returns `1` instead of
  `2`. Seeding with `{0: 0}` or `{}` are the same bug.
- **`total += 1` instead of `total += seen[counting - k]`.** Undercounts on any
  repeated prefix: `[0, 0, 0]`, `k = 0` gives `3` instead of `6`;
  `[1, -1, 1, -1]`, `k = 0` gives `3` instead of `4`. Passes every test whose
  prefix sums are distinct, which is most improvised tests.
- **Inserting the current prefix before the lookup.** Only wrong when `k = 0`,
  and then badly: `[1, 2, 3]` with `k = 0` returns `3` instead of `0`, and
  `[1, -1, 0]` with `k = 0` returns `6` instead of `3`. The narrowness of the
  failure is the danger — this order survives almost any test set that does not
  include `k = 0`.
- **Reaching for a sliding window.** The single most common wrong instinct here,
  because the problem statement reads like a window problem. It is correct only
  when every value is positive. Check the constraint line before writing a
  window, every time.
- **Searching for `counting + k` instead of `counting - k`.** Symmetric-looking
  and wrong. It asks for a *later* prefix, which is not in the map yet, so it
  silently undercounts — on `[1, 2, 3]` with `k = 3` it returns `0`. Derive the
  direction from `sum(i..j) = prefix[j] - prefix[i-1]` rather than recalling it.
- **Trying to return the subarrays rather than the count.** The count is
  computable in O(n) precisely *because* the identities of the matching prefixes
  are never needed. Listing them can require O(n²) output — `[0, 0, …, 0]` with
  `k = 0` has ~n²/2 answers — so no algorithm can enumerate them in linear time.
  That is a real distinction, not a quibble.
- **Assuming a zero-sum stretch should be skipped or merged.** `[5, -5, 5]` with
  `k = 5` has three answers, including the whole array. There is no preference
  for shorter or non-overlapping subarrays; every index range counts on its own.

## Redo from scratch

1. Write down `sum(nums[i..j]) = prefix[j] - prefix[i-1]`. Everything follows
   from this line.
2. Fix the right end `j` and ask how many earlier prefixes equal
   `prefix[j] - k`. That is a counting question, so use a map from prefix value
   to occurrence count.
3. Seed the map with `{0: 1}` — the empty prefix — or lose every subarray that
   starts at index 0.
4. In the loop: add the element, **look up, then insert**. Add the stored count,
   not one.
5. Test `[3]` with `k = 3` (the seed), `[0, 0, 0]` with `k = 0` (counts, and the
   insert order), `[1, -1, 0]` with `k = 0` (negatives — the window trap),
   `[1, 2, 3]` with `k = 7` (no answers).

Be able to justify out loud: **why the map stores counts rather than a set** —
that two distinct start positions can share a prefix sum whenever the elements
between them sum to zero, and each is a separate answer. And second: **why the
lookup must precede the insert** — that for `k = 0` the key sought is `counting`
itself, so inserting first lets the prefix match itself and counts the empty
subarray. If you can state both, you can also see immediately why the
all-positive variant of this problem is a two-pointer window and this one is not.

## Related problems

- [Two Sum](../0001-two-sum/README.md) — solved. The same hash map one step
  earlier: for each element, look up the complement you need *before* inserting
  the current one. Identical structure, identical ordering rule, and recognising
  that this problem is Two Sum over prefix sums is the fastest route back into it
  cold.
- [Maximum Subarray](../0053-maximum-subarray/README.md) — solved, in the same
  batch as this one. The instructive contrast: also about contiguous sums, but
  asking for the *best* one rather than *how many* equal a target, so a single
  running scalar suffices and no map is needed. Which question you are being
  asked determines which of the two machines applies.
- [Range Sum Query - Immutable](../0303-range-sum-query-immutable/README.md) —
  solved. The prefix-sum primitive in its plainest form, materialised as an array
  and queried directly. Read it if the `prefix[j] - prefix[i-1]` identity does
  not feel automatic.
- [Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/)
  — not solved yet, and the best next one. Identical algorithm with the map keyed
  on `prefix % k` instead of `prefix`, so it tests whether you learned the
  *technique* or the formula — plus a genuine trap in Python's handling of
  negative remainders.
- [Continuous Subarray Sum](https://leetcode.com/problems/continuous-subarray-sum/)
  — not solved yet. Same modular prefix idea, but it asks for existence with a
  minimum length of two, so the map stores the earliest *index* per remainder
  rather than a count. A good demonstration of how the question shape changes
  what the map's value should be.
- [Subarray Product Less Than K](https://leetcode.com/problems/subarray-product-less-than-k/)
  — not solved yet. The mirror image worth doing right after: products of
  strictly positive values *are* monotone, so the sliding window that is wrong
  here is exactly right there. Doing both fixes the window-versus-prefix instinct
  permanently.
- [Minimum Operations to Reduce X to Zero](https://leetcode.com/problems/minimum-operations-to-reduce-x-to-zero/)
  — not solved yet. A disguised version: removing a prefix and a suffix summing
  to `x` is the same as finding the longest middle subarray summing to
  `total - x`. Useful for learning to recognise this machine when the statement
  works hard to hide it.
