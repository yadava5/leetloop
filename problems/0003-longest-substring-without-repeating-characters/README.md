# 3. Longest Substring Without Repeating Characters

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Hash Table, String, Sliding Window |
| **Solved** | 2026-09-15 |
| **Runtime** | 172 ms (76.58th percentile) |
| **Memory** | 19.8 MB (77.91th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/longest-substring-without-repeating-characters/ |

## The problem

**Given** a string `s`.

**Return** the **length** of the longest contiguous substring of `s` in which no
character appears twice. The length as an integer — not the substring itself,
and not its position. If `s` is empty the answer is `0`.

The word doing the work is **substring**: the characters must be contiguous in
`s`. This is not the longest subsequence with distinct characters, which would
be a trivially different problem (just count the distinct characters). And
"repeating" means *any* repeat anywhere inside the window, not just adjacent
repeats — `"abca"` has no adjacent repeat but its longest valid window is still
only `"abc"`.

**Guaranteed**: nothing useful. `s` may be empty, and the alphabet is wide
(letters, digits, symbols, spaces), so no assumption that it fits in 26 slots is
safe.

```text
def lengthOfLongestSubstring(self, s: str) -> int
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `"au"` | `2` | The whole string is already valid. The simplest shape: the window never has to shrink, and the answer is the final `current_length`. |
| `"abba"` | `2` | **Counterexample to the naive "jump to `seen[c] + 1`" window.** At index 3 the stored index of `'a'` is `0`, which is *behind* the current left edge at `2`. Jumping there would move the window backwards to `"bba"` and report `3`. The `seen[character] >= start` guard is the only thing stopping it. Verified. |
| `"tmmzuxt"` | `5` | The sharper version of the same trap, because here the wrong answer is not merely too big by one — the naive jump reports `6` (the whole string bar one character) where the truth is `5` (`"mzuxt"`). The stale `'t'` at index 0 is what does the damage. Verified. |
| `"zzzz"` | `1` | Every character repeats immediately, so the window is dragged forward on every step and never exceeds one character. Confirms the left edge can move every single iteration. |
| `""` | `0` | **Edge case:** the empty string, which the constraints explicitly permit. Caught by the `if not s` guard — though the loop would also produce `0` on its own. |
| `"dvdf"` | `3` | A favourite because the answer (`"vdf"`) is a suffix and the repeat is *not* adjacent. The window must jump from `0` to `1` at index 2 and then keep growing to the end. Anything that resets the window to empty on a repeat returns `2` here. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `0 <= s.length <= 10^5` | The **lower bound of `0` makes the empty string a real input**, so `if not s: return 0` is one of the rare guards in this repo that the judge actually exercises — unlike, say, the identical-looking guard in *Longest Palindromic Substring*, where the constraint starts at `1`. The upper bound is the design input: **10⁵ characters means an O(n²) scan over all start positions is ~5 × 10⁹ character operations and will TLE in Python**, and the brute force that re-checks each substring for uniqueness is O(n³) and worse. That forces a single pass in which the left edge only ever moves *forward* — the amortisation argument below. |
| `s consists of English letters, digits, symbols and spaces.` | The alphabet is **not** just lowercase letters, so **a fixed 26-slot array is wrong** and the natural container is a dict (or a 128-slot array if you are willing to bet on ASCII). This is the constraint most often skimmed, and skimming it produces an `IndexError` or a silent wrong answer on an input containing a space or a digit. It also caps the dict at the alphabet size rather than at `n`, which is where the O(min(n, |Σ|)) space bound comes from. |

## Key insight

Maintain a window that is *always* free of repeats, and never move its left edge
backwards. When the character at the right edge has been seen before **inside
the current window**, the left edge must move to one past that previous
occurrence — not by crawling, but in a single jump, because every position it
skips over would still contain the duplicate pair. Storing the last index of
each character is what makes the jump a lookup rather than a search.

The subtlety that makes this a Medium rather than an Easy is the phrase *inside
the current window*. The map remembers characters forever; the window does not.
A hit in the map is not by itself evidence of a repeat in the window, and
treating it as one is the bug.

## Approach

1. Return `0` for the empty string.
2. Keep `seen`: character → the last index at which it appeared (ever, not just
   within the window).
3. Keep `start`: the inclusive left edge of the current window. The window is
   `s[start .. index]`.
4. For each `index, character`:
   - if `character in seen` **and** `seen[character] >= start`, the previous
     occurrence lies inside the window, so set `start = seen[character] + 1`;
   - record `seen[character] = index`;
   - the window length is `index - start + 1`; keep the running maximum.
5. Return `max_length`.

Two orderings are load-bearing. **The staleness test must precede the write** —
if `seen[character] = index` ran first, the condition `seen[character] >= start`
would be trivially true for every character and `start` would be dragged to
`index + 1` on every step, collapsing the answer to `1`. And **`start` must only
be assigned, never decremented or reset**: the correctness of the amortised O(n)
bound and of the window invariant both rest on `start` being monotonically
non-decreasing, which the `>= start` guard is precisely what enforces.

### Why it's correct

**Invariant**: before processing index `i`, (a) `s[start .. i-1]` contains no
repeated character, (b) `seen` maps every character of `s[0 .. i-1]` to the last
index `< i` at which it occurs, and (c) `max_length` is the length of the longest
repeat-free substring ending at or before `i - 1`.

The body restores all three. For (a): let `c = s[i]`. If `c` does not occur in
`s[start .. i-1]` then appending it keeps the window repeat-free and `start` is
correctly left alone — and the test detects exactly this case, because the only
possible earlier occurrence of `c` inside the window would be the *last* one,
which is `seen[c]`; if `seen[c] < start` it is outside the window, and any older
occurrence is further left still. If `c` does occur in the window, then it occurs
at `seen[c] >= start`, and the new window must start after it; setting
`start = seen[c] + 1` removes that occurrence and nothing else, so the window is
repeat-free again and is the **longest** such window ending at `i`. (b) is
restored by the unconditional write, and (c) by the `max`.

**Why the longest window ending at `i` is enough.** Every repeat-free substring
ends at some index, so the maximum over all `i` of "the longest repeat-free
window ending at `i`" is the answer. The invariant establishes that the window
the loop holds at step `i` *is* that longest one — it cannot be extended left
without re-admitting the duplicate the jump just removed.

**Termination, and the edge of the range.** The `for` is bounded and always
ends. The interesting bound is `start`: it is only ever assigned
`seen[character] + 1` where `seen[character] >= start`, so it never decreases,
and it never exceeds `index + 1`. That monotonicity is also the running-time
argument — `start` advances at most `n` times over the whole run, so the total
work is O(n) despite the window appearing to move twice per step.
`current_length = index - start + 1` is inclusive on both ends, hence the `+ 1`;
the degenerate case to check by hand is a character repeating immediately
(`"zz"`), where at `index = 1` the jump sets `start = 1` and the length comes out
`1 - 1 + 1 = 1`, which is right. The length can never drop to `0`, because the
only assignment to `start` is `seen[character] + 1`, and `seen[character]` is
always a strictly earlier index, so `start <= index` at every step.

The step I would flag as least certain if reconstructing this cold is not the
algorithm but the *sufficiency* of storing only the last index. The argument
above — that an older occurrence of `c` inside the window would imply the latest
one is also inside it, since the latest is further right — is easy to wave at
and slightly fiddly to state. It is worth saying out loud rather than assuming.

## Solution

```python
# 3. Longest Substring Without Repeating Characters (Medium) - sliding window whose left edge jumps past the previous copy of a repeated character. O(n) time, O(min(n, alphabet)) space.
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # Reachable, unlike most such guards: the constraints allow
        # s.length == 0. Strictly it is redundant anyway - the loop body would
        # never run and max_length would already be 0 - but it is honest here.
        if not s:
            return 0

        # character -> the LAST index at which it appeared. Not a set and not
        # a count: the index is what allows the left edge to jump straight to
        # the right place instead of crawling one step at a time.
        seen = {}

        # Left edge of the window, inclusive. The window is s[start .. index].
        start = 0

        max_length = 0

        for index, character in enumerate(s):

            # THE line that makes this correct. `character in seen` alone is
            # not enough - `seen` is never pruned, so it still remembers
            # characters that have already fallen out of the window to the
            # left of `start`. Acting on those would drag `start` BACKWARDS
            # and produce a window containing a duplicate.
            #
            # Concretely on "abba": at index 3 the stored index of 'a' is 0,
            # but start is already 2. Without `seen[character] >= start` the
            # left edge would be reset to 1, the window would become "bba",
            # and the answer would come back 3 instead of 2.
            #
            # Because start only ever moves right, the window is always
            # duplicate-free, and this is the step that guarantees it.
            if character in seen and seen[character] >= start:
                start = seen[character] + 1
            # Must come AFTER the test above, otherwise the character would be
            # found at its own index and the window would collapse every step.
            seen[character] = index

            # Inclusive on both ends, hence the + 1.
            current_length = index - start + 1

            # Measured on every iteration rather than only when the window
            # shrinks, because the longest window may well be the final one.
            max_length = max(max_length, current_length)

        return max_length
```

[solution.py](solution.py) · [raw submission](../../data/raw/longest-substring-without-repeating-characters.py)

## Why this approach

| Alternative | Cost | Why the jumping window beats it |
|---|---|---|
| Brute force: every substring, check each for distinctness | O(n³) time (or O(n²) with an incremental set), O(n) space | There are ~5 × 10⁹ substrings at `n = 10⁵`. Not merely slow — it cannot finish. Even the O(n²) refinement, which extends each start position until it hits a repeat, is 5 × 10⁹ operations at the limit. |
| Sliding window with a **set**, shrinking one character at a time: on a repeat, `remove(s[start]); start += 1` until the duplicate is gone | **O(n)** time, O(min(n, \|Σ\|)) space | Genuinely equivalent in complexity — each character is added and removed at most once, so the inner `while` amortises to O(1). Arguably *easier to get right*, because there is no staleness question: the set contains exactly the window, so membership and "in the window" are the same thing. The cost is an inner loop and the discipline of removing before advancing. This version trades that for a single jump and the `>= start` guard. Pick either; know that the guard is the price of not having the inner loop. |
| Jump to `seen[c] + 1` **without** the `>= start` check | O(n) time and **wrong** | The defining trap. `start` can move backwards to a stale index, re-admitting a duplicate. On `"tmmzuxt"` it returns `6` where the answer is `5`; on `"abba"` it returns `3` where the answer is `2`. Both verified by running it. It passes `"abcabcbb"` and most hand-written tests, which is what makes it so durable a bug. |
| Same idea but a fixed `[-1] * 128` array instead of a dict | O(n) time, O(1) space | Faster by a constant and perfectly sound *if* the input really is ASCII. The constraint says "English letters, digits, symbols and spaces", which is ASCII in practice but is not stated as a code-point bound — the dict costs nothing and needs no bet. |
| Reset the window to empty on any repeat (`start = index`) | O(n) and **wrong** | The over-correction. Throws away the valid suffix that did not contain the duplicate. On `"dvdf"` it returns `2` instead of `3`, because at index 2 the whole prefix is discarded rather than just the leading `"d"`. |
| DP: `dp[i]` = length of the longest repeat-free substring ending at `i`, with `dp[i] = min(dp[i-1] + 1, i - seen[c])` | O(n) time, O(1) space with a rolling scalar | Correct, and a nice reframing — the `min` is doing precisely the job of the `>= start` guard, clamping the extension so it cannot reach back past the previous occurrence. Same algorithm wearing different clothes. Mentioned because if the guard ever feels arbitrary, this formulation shows it is not. |

## Complexity

- **Time — O(n)**. One pass; each iteration does a dict lookup, at most one dict
  write, a comparison and a `max`, all O(1) on average. Note that `start` jumping
  does **not** add work — it is an assignment, not a scan — so unlike the
  set-based window there is nothing to amortise here at all. 172 ms at `n = 10⁵`
  is essentially Python's per-character interpreter overhead.
- **Space — O(min(n, |Σ|))**. The dict holds one entry per *distinct* character
  ever seen, which is bounded by the alphabet as well as by the string length.
  For the stated alphabet that is a small constant in practice — hence 19.8 MB,
  most of which is the input string.

## Pitfalls

- **Dropping the `seen[character] >= start` guard.** Returns `6` on `"tmmzuxt"`
  (correct: `5`) and `3` on `"abba"` (correct: `2`). The single most likely way
  to get this problem wrong, and it survives `"abcabcbb"`, `"bbbbb"` and
  `"pwwkew"` — all three of LeetCode's own examples. If you test only against
  those you will ship it.
- **Never pruning `seen`, and forgetting that you never prune it.** These are the
  same fact seen from two sides: the map is deliberately allowed to hold stale
  entries (pruning would cost time), and the guard is what makes that safe. If
  you decide to prune instead, the guard becomes unnecessary — but a half-done
  version with neither is broken.
- **Writing `seen[character] = index` before the test.** Then
  `seen[character] >= start` is true for every character, `start` becomes
  `index + 1` every step, and every answer is `1`.
- **`start = index` on a repeat** instead of `seen[character] + 1`. Discards the
  valid tail of the window: `"dvdf"` returns `2` rather than `3`.
- **`current_length = index - start`,** without the `+ 1`. Every answer comes out
  one too small, including `0` for a single-character string. The window is
  inclusive at both ends.
- **Returning the substring instead of its length.** The problem asks for the
  length; carrying `(start, length)` and slicing would be the change, and it is
  not asked for.
- **Assuming a 26-letter alphabet** and indexing `ord(c) - ord('a')`. The
  constraint explicitly admits digits, symbols and spaces; a space gives a
  negative index, which in Python silently reads from the end of the array rather
  than raising.
- **Taking the `max` only when the window shrinks.** The longest window is very
  often the final one (`"au"`, `"dvdf"`), and it never triggers a shrink. The
  `max` belongs on every iteration.

## Redo from scratch

1. State the frame: **a window that is always repeat-free, whose left edge only
   moves right.** Everything else is bookkeeping.
2. Decide what the map holds — character → **last index seen, ever** — and accept
   that it is never pruned.
3. Write the guard before the write: `if c in seen and seen[c] >= start`. Say out
   loud what the second clause is for before you write it.
4. `start = seen[c] + 1`; then `seen[c] = index`; then
   `length = index - start + 1`; then `max`.
5. Test `"tmmzuxt"` (stale index, expect `5`), `"abba"` (expect `2`), `"dvdf"`
   (expect `3`), `""` and `"zzzz"`.

Be able to justify out loud: **why `start` may never move backwards**, and what
concretely goes wrong when it does — name `"tmmzuxt"` and the answer `6`. And
**why storing only the most recent index of each character is sufficient**: an
older occurrence inside the window would imply the newest one is inside it too.
If you can only recite the four lines of the loop, the guard is the clause that
will quietly go missing, and the code will still look right.

## Related problems

- [Contains Duplicate II](../0219-contains-duplicate-ii/README.md) — already
  solved, and the same dict of character/value → last index, used only to measure
  a distance rather than to move a window. The cheapest way to see that "map of
  last-seen index" is one idea with two uses.
- [Longest Substring with At Most K Distinct Characters](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/)
  — not solved yet, and the natural generalisation: the window condition becomes
  "at most `k` distinct" instead of "no repeats", which needs **counts** rather
  than indices, and therefore a shrinking inner loop rather than a jump. Doing it
  shows exactly which problems the jump trick applies to and which it does not.
- [Longest Substring with At Most Two Distinct Characters](https://leetcode.com/problems/longest-substring-with-at-most-two-distinct-characters/)
  — not solved yet. The `k = 2` special case of the above; a gentler entry to the
  count-based window.
- [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)
  — not solved yet. A window whose validity condition (`length - maxCount <= k`)
  is *not* monotone in the obvious way, which is the best available lesson in
  when a sliding window is and is not legitimate.
- [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)
  — not solved yet. The same two-pointer skeleton aimed at a *minimum* instead of
  a maximum, which flips where you record the answer. The standard hard follow-up.
- [Subarrays with K Different Integers](https://leetcode.com/problems/subarrays-with-k-different-integers/)
  — not solved yet. Counting windows rather than measuring the longest, solved by
  "at most `k`" minus "at most `k-1`". Worth it for that trick alone.
- [Minimum Consecutive Cards to Pick Up](https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up/)
  — not solved yet, and close to trivial once this page is understood: the
  smallest gap between two equal characters, which is the same map read for a
  different statistic.
