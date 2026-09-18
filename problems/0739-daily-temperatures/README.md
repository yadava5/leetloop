# 739. Daily Temperatures

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Stack, Monotonic Stack |
| **Solved** | 2026-09-17 |
| **Runtime** | 94 ms (57.38th percentile) |
| **Memory** | 28.6 MB (57.31th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/daily-temperatures/ |

## The problem

**Given** an array `temperatures` where `temperatures[i]` is that day's
temperature.

**Return** a new array `answer` of the same length, where `answer[i]` is the
number of days you must wait after day `i` to get a **strictly warmer**
temperature. If no later day is warmer, `answer[i]` is `0`.

Three things to be precise about, because each one is a place to go wrong:

- The result is a **distance in days**, not an index and not a temperature. For
  day `i` resolved by day `j`, the value is `j - i`.
- **Strictly** warmer. An equal temperature does not count, which matters far
  more here than it usually would — see the constraints.
- It is the **first** warmer day, not the warmest, and not the last.

**Guaranteed**: the array is non-empty, and every temperature is an integer in a
small fixed range. The answer array is a new array; nothing is modified in
place.

```text
def dailyTemperatures(self, temperatures: list[int]) -> list[int]
```

### Examples (mine, not LeetCode's)

| `temperatures` | Returns | Why |
|---|---|---|
| `[65, 70, 68, 90]` | `[1, 2, 1, 0]` | The general shape. Day 1 (`70`) is not resolved by day 2 (`68`, colder) and waits for day 3. The last day has no future at all, so `0`. |
| `[70, 70, 75]` | `[2, 1, 0]` | **The tie case, and the counterexample to using `<=` in the while test.** Day 0 is *not* resolved by day 1 — equal is not warmer — so it waits two days. A `<=` comparison returns `[1, 1, 0]`, which looks perfectly reasonable and is wrong. |
| `[90, 80, 70, 60]` | `[0, 0, 0, 0]` | **Counterexample to the intuition that the stack always empties.** A strictly falling series never pops anything; all four indices are still on the stack when the loop ends, and the prefilled `0`s are their final answers. This is the case that proves no drain pass is needed. |
| `[40, 100, 43, 42, 41]` | `[1, 0, 0, 0, 0]` | Day 1 spikes to `100` and nothing after it ever climbs again, so days 1–4 all answer `0` while day 0 — sitting below the spike — resolves immediately. Being warmer than *your own future* is what matters, not being warm: day 2's `43` is high in absolute terms and still gets nothing. Change the tail to `41, 42, 43` and the answer becomes `[1, 0, 1, 1, 0]`, because those days now resolve each other. |
| `[50]` | `[0]` | **Edge case:** one day. The while loop never runs (the stack is empty), the index is pushed, and the prefilled `[0]` is returned unchanged. |
| `[30, 31, 30, 31, 32]` | `[1, 3, 1, 1, 0]` | Day 1's `31` is not resolved by day 3's `31` — equal again — and waits for `32` at day 4, a distance of `3`. Worth tracing by hand: it is the example where an off-by-one in `index - settled` shows up as `2` instead of `3`. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= temperatures.length <= 10^5` | The upper bound rules out the obvious nested loop. 10⁵ days means the naive "for each day, scan forward until warmer" is ~5 × 10⁹ comparisons on a descending input, hopeless in Python, so an amortised linear method is required. The bound also rules **in** O(n) auxiliary space: a 10⁵-element stack of indices is trivially affordable, so there is no reason to contort the solution to save it. The lower bound of `1` means the array is never empty, so `[0] * len(...)` is never an empty array and no guard is needed in front of the loop. |
| `30 <= temperatures[i] <= 100` | This is the sleeper constraint. The range holds only **71 distinct values**, so across 10⁵ days ties are not an edge case — they are everywhere, and the strict-versus-non-strict comparison in the while loop is the single most consequential character in the solution. The small range also rules *in* a completely different O(71n) approach (for each day, look up the next occurrence of each of the 71 possible warmer temperatures and take the minimum), which is a legitimate alternative rather than a curiosity — see the table below. And since all values are positive and bounded, no sentinel value trick is needed to terminate the stack. |

## Key insight

Walk the days forward and keep a stack of the days still waiting for an answer.
The moment a warmer day arrives, it is the answer for **every** waiting day it
beats — and those are exactly the days sitting at the top of the stack, because
the stack's temperatures are non-increasing from bottom to top. A day that
gets popped is finished forever: the day that popped it is the first warmer one
by construction. Each index is pushed once and popped at most once, which is
where the linear time comes from despite the nested loop.

The thing to whisper if stuck: *don't ask "when will day `i` be resolved" —
ask "which pending days does today resolve".* Inverting the question is the
whole trick, and it is the same inversion that makes Stock I a one-pass scan.

## Approach

1. Prefill `answer` with `0`s, one per day. For any day never resolved, this is
   already the final value.
2. Keep `waiting`, a stack of **indices** whose answers are not yet known.
3. For each `(index, value)` in order:
   - While the stack is non-empty and the temperature at its top index is
     **strictly less** than `value`, pop that index and set its answer to
     `index - settled`.
   - Then push `index`.
4. Return `answer`. Whatever is still on the stack keeps its `0`.

Two orderings are load-bearing:

- **Pop before push.** The `waiting.append(index)` comes *after* the while loop.
  Reversing them would put today on the stack before testing it, and the loop
  would then compare `value` against itself.
- **Indices on the stack, not temperatures.** The pop needs both the temperature
  (to compare) and the position (to subtract). Storing the index gives both,
  since the temperature is one array lookup away; storing the temperature gives
  only one and loses the distance.

### Why it's correct

**Invariant**: at the top of every iteration, `waiting` holds, from bottom to
top, a strictly increasing sequence of indices whose temperatures are
**non-increasing**, and those are exactly the days seen so far whose warmer day
has not yet appeared. Every other day already has its final answer written.

The non-increasing part is maintained by construction: before `index` is pushed,
the while loop has removed every top entry strictly colder than `value`, so
whatever remains at the top is `>= value` and the order holds. The "exactly the
unresolved days" part is maintained because a day leaves the stack only when its
answer is written, and every day is pushed exactly once.

**Why a popped element can never be needed again.** When `settled` is popped at
`index`, day `index` is warmer than it. Could some day between `settled` and
`index` have been a better (earlier) answer? No: any day `k` with
`settled < k < index` was itself pushed onto the stack above `settled`, and the
only way `settled` reaches the top by the time we get to `index` is if every
such `k` was already popped — which means `temperatures[k] < temperatures[index]`
and, since `k` did not pop `settled`, also `temperatures[k] <= temperatures[settled]`.
So no day in between was strictly warmer than `settled`, and `index` really is
the first. The answer written is final, which is why a single pass with no
revisiting suffices.

**The strict `<` is what makes "strictly warmer" true.** With `<=`, a day of
equal temperature would pop `settled` and claim to be its warmer day. On
`[70, 70, 75]` that yields `[1, 1, 0]` instead of `[2, 1, 0]`. Note the
direction of the error: `<=` produces an answer that is too *small*, never too
large, so it passes any test whose data has distinct temperatures — and with
only 71 possible values, real test data will not be distinct.

**Termination and the edge of the range.** The outer `for` visits each index
once. The inner `while` terminates because each iteration removes an element,
and across the whole run it can pop at most `n` times in total — one per push —
so the nested loop is amortised O(1) per day, not O(n). The range edges: the
first iteration finds an empty stack, so the while guard short-circuits on
`waiting` before ever indexing into it (the order of the `and` matters — swapping
it would evaluate `waiting[-1]` on an empty list and raise `IndexError`). The
last iteration pushes `n - 1` and then the loop ends with at least that one index
still pending; its `0` is already in place. **There is deliberately no drain
loop after the main pass**, and that absence is correct rather than an oversight
— the prefill did the work.

The part of this I am least certain of when reconstructing it cold is the
"never needed again" argument above — specifically the second half, that an
intermediate `k` must satisfy `temperatures[k] <= temperatures[settled]`. It
follows from `k` not having popped `settled`, but it is the step worth
re-deriving rather than trusting, because the whole linearity claim rests on it.

## Solution

```python
# 739. Daily Temperatures (Medium) - monotonic stack of indices still waiting for a warmer day. O(n) time, O(n) space.
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:

        # Prefill with 0, which is the answer for every day that never finds a
        # warmer one. That is not a placeholder to be overwritten later - it is
        # the FINAL answer for whatever is left on the stack at the end, and it
        # is why the code needs no drain loop after the main pass.
        #
        # (Style wart, left alone: `[0] *len(...)` is missing a space after the
        # star. Harmless, and the AST gate forbids fixing it here.)
        answer = [0] *len(temperatures)

        # Indices - NOT temperatures - of days that have not yet found a warmer
        # day. Storing indices is what makes the distance subtraction possible
        # at the moment of resolution; storing values would lose the position.
        # The temperatures at these indices are non-increasing from bottom to
        # top, which is the invariant the while loop maintains.
        waiting = []

        for index, value in enumerate(temperatures):

            # Today resolves every pending day that is strictly colder. Each
            # such day's first warmer day is today, because it survived every
            # day in between - had one of those been warmer, it would have
            # popped this index then.
            #
            # STRICT `<` is load-bearing. With `<=`, an equal temperature would
            # resolve the pending day, but "warmer" means strictly greater:
            # on [70, 70, 75] day 0's answer is 2, not 1.
            while waiting and temperatures[waiting[-1]] < value:

                # Pop from the top: the most recent pending day, which is also
                # the coldest on the stack. Once popped, this index is finished
                # and can never be needed again - its answer is now known.
                settled = waiting.pop()

                # Distance in days, not a temperature and not an index. The
                # subtraction is the whole reason indices were stacked.
                answer[settled] = index - settled

            # Push AFTER the while loop, never before. Pushing first would put
            # today's index on the stack and then immediately test it against
            # itself; `value < value` is false so it would not pop, but the
            # ordering here is what keeps the stack's non-increasing property
            # true at the top of every iteration.
            waiting.append(index)

        # Anything still in `waiting` never found a warmer day and keeps its
        # prefilled 0. No cleanup pass is needed.
        return answer
```

[solution.py](solution.py) · [raw submission](../../data/raw/daily-temperatures.py)

## Why this approach

| Alternative | Cost | Why the monotonic stack beats it |
|---|---|---|
| Brute force: for each day, scan forward until a warmer day | O(n²) time, O(1) extra space | At `n = 10⁵` a descending input forces ~5 × 10⁹ comparisons — TLE by orders of magnitude. The waste is structural: the forward scan from day `i` re-walks ground that the scan from day `i - 1` already covered and learned nothing from. |
| Right-to-left with jumps: walk backwards, and from day `i` hop via `answer[i+1]` to skip runs already resolved | O(n) amortised, O(1) extra space | **Correct and genuinely competitive** — it uses the answer array itself as the skip structure and needs no stack, so it wins on space. It is harder to get right (the jump loop has two exit conditions and a `0` sentinel meaning "no warmer day ever", which must break the hop rather than continue it), and the amortisation argument is less obvious than "each index is pushed and popped once". Know it exists; reach for the stack first. |
| Next-occurrence table over the 71 possible temperatures: keep `next_seen[t]`, and for day `i` take `min(next_seen[t] for t > value)` | O(71n) ≈ 7 × 10⁶ operations, O(71) space | Correct, and viable *only* because of the `30 <= temperatures[i] <= 100` bound — it is the constraint-exploiting answer. Slower than the stack by a constant of ~71 and it does not generalise to unbounded values, which is exactly what makes it a worse thing to have memorised: the stack is the technique, this is a trick that happens to fit this input range. |
| Sort the days by temperature and process in order | O(n log n) time, O(n) space | Correct if done carefully with a sorted structure over indices, but strictly worse: an extra log factor to rediscover an ordering the array already had. Sorting destroys the adjacency that the problem is actually about. |
| Store temperatures on the stack instead of indices | — | **Wrong**, not merely different. The answer is a *distance*, and a stack of temperatures has thrown away the positions needed to compute it. You would need a parallel stack of indices, at which point you have the solution above with extra steps. |

## Complexity

- **Time — O(n)**. The `for` runs `n` times; the inner `while` looks like it
  makes this quadratic but does not, because every index is pushed exactly once
  and popped at most once, so the total number of pop operations across the
  entire run is at most `n`. Amortised, each day costs O(1). The 94 ms reported
  is Python's constant factor on 10⁵ elements, not a complexity problem.
- **Space — O(n)**. The `answer` array is required output, so it does not count
  against the auxiliary bound; `waiting` is the real cost and reaches `n` in the
  worst case — a strictly decreasing series, where nothing is ever popped and
  every index piles up. The constraints make that comfortable.

## Pitfalls

- **`<=` instead of `<` in the while test.** On `[70, 70, 75]` it returns
  `[1, 1, 0]` where the answer is `[2, 1, 0]`. Given that temperatures span only
  71 values, ties are dense in any realistic input — this is the bug that
  actually happens, not a theoretical one. It fails *quietly*: the answers come
  out too small, never too large, so the shape of the output still looks right.
- **Writing `answer[settled] = index` instead of `index - settled`.** Returns an
  index where a distance was wanted. On `[65, 70]` you get `[1, 0]` by
  coincidence, because day 0 resolved at index 1 and `1 - 0 = 1`. Every test that
  starts with a day-0 resolution at day 1 hides it.
- **Appending before the while loop.** Then day `index` is compared against
  itself. `value < value` is false, so nothing breaks *today* — but the stack no
  longer satisfies the non-increasing invariant when you reason about it, and the
  same misordering in the sibling problems (Next Greater Element, Online Stock
  Span, Largest Rectangle) does produce wrong answers.
- **Adding a drain loop after the main pass.** A natural-looking "cleanup" that
  writes something to every index still on the stack. Those indices already hold
  their correct `0` from the prefill; any drain that writes a distance instead
  turns `[90, 80, 70]` into nonzero answers for days with no warmer day at all.
  The code handles this case correctly and *invisibly* — there is nothing to see,
  which is exactly why someone redoing it cold adds the loop back.
- **Swapping the `and` operands** to `temperatures[waiting[-1]] < value and waiting`.
  Raises `IndexError` on the very first day. Python's `and` short-circuits left to
  right, and the emptiness check must come first.
- **Assuming the stack empties by the end.** It does not, in general. On a
  strictly falling series every index is still pending when the loop exits. Any
  logic that reads `waiting` after the loop and expects it empty is wrong.
- **Fearing the nested loop.** The `while` inside the `for` reads as O(n²) at a
  glance and gets "optimised" away by people who have not counted the pops. The
  amortisation argument is the thing to be able to state, not to feel.

## Redo from scratch

1. Invert the question: not "when is day `i` resolved" but "which pending days
   does today resolve".
2. Prefill the answer array with `0` — that is the final value for unresolved
   days, and it removes the need for any post-loop cleanup.
3. Stack **indices**, not temperatures, because the answer is a distance.
4. For each day: while the stack is non-empty **and** its top is strictly colder,
   pop and write `index - settled`. Then push.
5. Test `[70, 70, 75]` (ties — the `<` vs `<=` trap), `[90, 80, 70, 60]` (nothing
   ever pops, stack non-empty at the end), `[50]` (single day).

Be able to justify out loud: **why a popped index can never be needed again** —
that the day popping it is provably its *first* warmer day, because everything in
between was popped earlier and was therefore no warmer. That argument is what
makes one pass sufficient. And second: **why the nested loop is O(n), not O(n²)**
— each index is pushed once and popped once, so pops total at most `n` across the
whole run. If you can state both, every other monotonic-stack problem is the same
machine with a different comparison.

## Related problems

- [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/)
  — not solved yet, and the natural next one. It is this exact stack returning
  the *value* of the next greater element instead of the distance, with an added
  hash-map indirection between two arrays. Doing it right after this one makes
  clear that the stack is the technique and the "distance" was incidental.
- [Online Stock Span](https://leetcode.com/problems/online-stock-span/) — not
  solved yet. The same monotonic stack run *backwards in time* and incrementally:
  you are asked for the span of preceding days, one query at a time, with no
  array to prefill. It is the test of whether you understand the stack or have
  memorised this loop, because the prefill-with-zero trick is unavailable.
- [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/)
  — not solved yet. The hard end of the same family: the popped element's answer
  needs *both* the resolving index and the new stack top, so the arithmetic at
  the pop is where the difficulty lives rather than in the stack discipline.
- [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) — not
  solved yet. Solvable with this identical stack, and also with two pointers,
  which makes it the best problem for seeing what a monotonic stack *is* — a way
  to defer a decision until the element that resolves it arrives.
- [Best Time to Buy and Sell Stock](../0121-best-time-to-buy-and-sell-stock/README.md)
  — solved. Unrelated in mechanism but the same mental move: stop searching over
  pairs and let a single forward pass carry just enough state to answer for the
  current element.
