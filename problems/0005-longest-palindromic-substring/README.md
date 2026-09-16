# 5. Longest Palindromic Substring

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Two Pointers, String, Dynamic Programming, Manacher |
| **Solved** | 2026-09-15 |
| **Runtime** | 215 ms (91.64th percentile) |
| **Memory** | 19.2 MB (70.02th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/longest-palindromic-substring/ |

## The problem

**Given** a string `s`.

**Return** the longest **contiguous substring** of `s` that reads the same
forwards and backwards. You return the substring itself, not its length and not
its indices. If several substrings tie for longest, any one of them is accepted.

Two things this is *not*. It is a **substring**, so the characters must be
contiguous in `s` — this is not the longest palindromic *subsequence*, which is
a genuinely different (and harder) problem solved by an O(n²) DP. And a
palindrome here is defined by plain character equality: no case folding, no
skipping punctuation.

**Guaranteed**: `s` is non-empty. That single promise is worth noticing,
because it means an answer always exists — every one-character substring is a
palindrome, so the result is never the empty string, and the `if not s` guard
at the top of the solution can never fire.

```text
def longestPalindrome(self, s: str) -> str
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `"q"` | `"q"` | **Edge case:** one character. Handled entirely by the initialisation `best_start = 0, best_length = 1` — the loop runs once and improves on nothing. |
| `"abcde"` | `"a"` | No palindrome longer than one character exists. The strict `>` in `if length > best_length` never fires, so the pre-loop default is returned, and that default is the leftmost single character. |
| `"xyzzyx"` | `"xyzzyx"` | **Counterexample to expanding from characters only.** The whole string is an even-length palindrome centred on the gap between the two `z`s. An odd-centres-only version returns `"x"` — verified, not assumed. This is why each pass of the loop runs the expansion twice. |
| `"bananas"` | `"anana"` | The answer touches neither end of the string and starts at an odd index. Kills any instinct to anchor the search at index `0` or to only grow a window from the left. |
| `"aaaa"` | `"aaaa"` | The worst case for running time as well as a correctness check: every centre expands as far as it can go, so this is the shape that makes the O(n²) bound tight. Also the case where several centres produce the same maximal length and the strict `>` quietly picks the first. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length <= 1000` | The lower bound of **`1` makes `if not s: return ""` dead code** — pleasant to have, but it is never exercised by the judge, so it proves nothing about the solution and should not be mistaken for the base case. The upper bound is the real design input: **n = 1000 makes O(n²) ≈ 10⁶ character comparisons, which Python does comfortably**, while a brute force over all ~5 × 10⁵ substrings that re-checks each one in O(n) is ~10⁹ operations and times out. Equally, 1000 is small enough that **Manacher's O(n) algorithm buys nothing** — the whole reason this problem is usually solved by centre expansion rather than by the asymptotically better method. The bound also makes the O(n²) *memory* of a DP table (10⁶ booleans) affordable but pointless next to this solution's O(1). |

One honesty note: the fetched constraints list contains only that one bound. The
real statement also restricts the alphabet, but that line was not captured, and
nothing here depends on it — the expansion compares characters with `==` and
works for any alphabet at all.

## Key insight

Stop thinking about *substrings* and start thinking about *centres*. A
palindrome is completely determined by where its middle is and how far it
reaches, and there are only `2n - 1` possible middles: each of the `n`
characters (odd lengths) and each of the `n - 1` gaps between adjacent
characters (even lengths). Walk outwards from each one while the two ends
match, and you have enumerated every palindrome in the string in O(n²) total,
never once re-checking a substring from the inside out.

The thing that makes this cheap is that a palindrome's interior is itself a
palindrome, so growing outwards reuses everything already verified. That is
also the licence to stop at the first mismatch.

## Approach

1. Return `""` if `s` is empty. (Dead under the constraints.)
2. Seed the answer as `best_start = 0, best_length = 1` — the leftmost single
   character, which is always a valid palindrome. This is what makes a string
   with no longer palindrome return something sensible.
3. For each index `centre`, run the expansion **twice**:
   - **odd**: `left = right = centre`, so the window starts as one character;
   - **even**: `left = centre, right = centre + 1`, so the window starts as two.
4. In each expansion, while `left >= 0 and right < len(s) and s[left] == s[right]`,
   step `left` down and `right` up.
5. After the loop, compute `length = right - left - 1`.
6. If `length > best_length`, record `best_length = length` and
   `best_start = left + 1`.
7. Return `s[best_start : best_length + best_start]`.

Two ordering details are load-bearing. **The three clauses of the `while` must
be in that order**: `left >= 0` and `right < len(s)` have to be checked *before*
`s[left] == s[right]`, because Python's negative indexing means `s[-1]` does not
raise — it silently reads the last character. Python's `and` short-circuits, so
writing them in this order is what prevents the bug rather than merely detecting
it. And **step 5 must happen after the loop exits, not inside it**: the loop
always leaves `left` and `right` one step *outside* the palindrome, and
`right - left - 1` is the formula that corrects for exactly that overshoot.

### Why it's correct

**Invariant of a single expansion**: *whenever the loop body executes, the
window `s[left .. right]` is a palindrome.* The condition has just established
that its two ends are equal, and its interior `s[left+1 .. right-1]` is either
the window accepted by the previous iteration — a palindrome by this same
invariant — or, on the first iteration, a single character (odd case) or the
empty string (even case), both trivially palindromes. Equal ends plus a
palindromic interior is exactly the definition, so the invariant carries
forward. Every window the loop accepts is therefore a genuine palindrome, and
the last one it accepts is the widest at that centre.

**Why stopping at the first mismatch loses nothing**: suppose the expansion
halts at `left, right`. Any *wider* palindrome at this same centre would contain
`s[left .. right]` as its middle — and every centred sub-window of a palindrome
is itself a palindrome. Since `s[left .. right]` is not one (the ends differ, or
one of them has fallen off the string), no wider window at this centre can be a
palindrome either. Nothing is skipped by breaking early.

**Why all palindromes are covered**: a palindrome occupying `s[i .. j]` has
`i + j` either even (centre character at `(i+j)/2`, reached by the odd pass) or
odd (centre gap between `(i+j-1)/2` and `(i+j+1)/2`, reached by the even pass at
`centre = (i+j-1)/2`). Both indices are in `range(len(s))`, so the outer `for`
visits that centre, and by the previous paragraph the expansion from it reaches
at least as far as `s[i .. j]`. So the maximum over all expansions is the true
maximum.

**Termination and the edge of the range.** Each iteration strictly decreases
`left` and strictly increases `right`, and both are bounded (`left >= 0`,
`right < len(s)`), so every expansion ends after at most `n` steps. The odd
expansion always runs at least once, because `s[centre] == s[centre]`, so
`length >= 1` there. The even expansion may run **zero** times — and that case
is the one worth checking by hand: `left = centre`, `right = centre + 1`, so
`length = (centre + 1) - centre - 1 = 0`, which loses to `best_length >= 1` and
correctly contributes nothing. The bound `right < len(s)` rather than `<=` is
what stops `right = len(s)` from being indexed; it also means that at
`centre = len(s) - 1` the even pass fails immediately, which is right, since
there is no gap to the right of the last character.

The off-by-one to stare at is `best_start = left + 1`. After the loop, `left`
sits one position *left of* the palindrome, so the palindrome starts at
`left + 1`. The same overshoot on both sides is what makes the length
`right - left - 1` and not `right - left + 1`; a quick sanity check on a
one-character expansion (`left = -1, right = 1`) gives `1 - (-1) - 1 = 1`,
which is correct.

Of everything above, the step I would flag as least likely to be reconstructed
correctly under pressure is the mapping from `(i, j)` back to a centre index in
the even case — `centre = (i + j - 1) / 2`, not `(i + j) / 2`. It is easy to
believe the coverage argument without being able to produce that formula, and
producing it is what actually establishes there are `2n - 1` centres and not
some other number.

## Solution

```python
# 5. Longest Palindromic Substring (Medium) - expand around each of the 2n-1 centres, remember the widest. O(n^2) time, O(1) extra space.
class Solution:
    def longestPalindrome(self, s: str) -> str:
        # Unreachable on LeetCode: the constraints promise 1 <= s.length, so s
        # is never empty. Kept because it costs nothing and makes the function
        # total if it is ever called from elsewhere.
        if not s:
            return ""

        # The answer is carried as (start, length), not as a string. Slicing
        # inside the loop would copy up to n characters every time a better
        # palindrome turned up; slicing once at the end copies exactly once.
        best_start = 0
        best_length = 1 # every single character is a palindrome itself!


        # Every palindrome is pinned by its CENTRE plus a radius, and there are
        # 2n-1 centres: n characters (which generate the odd lengths) and n-1
        # gaps between adjacent characters (the even lengths). Each pass of
        # this loop tries both kinds of centre anchored at index `centre`, so
        # over the whole loop all 2n-1 are covered.
        for centre in range(len(s)):

            # --- odd lengths. The window starts as the single character
            # s[centre], which is trivially a palindrome, so the while below
            # always runs at least once and `length` ends up at least 1.
            left = centre
            right = centre

            # `left >= 0` is load-bearing, not defensive: once left reaches -1
            # Python wraps it to the END of the string and starts comparing
            # characters that are nowhere near each other.
            # Stopping at the first mismatch is safe because any wider window
            # at this centre CONTAINS this one as its middle, so if this one is
            # not a palindrome no wider one can be either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            # The loop always exits one step PAST the palindrome on both sides
            # (either a mismatch or a fallen-off end), so the real window is
            # s[left+1 .. right-1] and its length is
            # (right - 1) - (left + 1) + 1 = right - left - 1.
            length = right - left - 1

            # Strict `>` keeps the FIRST palindrome of a given length, i.e. the
            # leftmost. LeetCode accepts any longest one; this just makes the
            # output deterministic.
            if length > best_length:
                best_length = length
                # left overshot by one, so the window begins at left + 1.
                # Writing `best_start = left` is the classic off-by-one here.
                best_start = left + 1

            # --- even lengths. The centre is now the GAP between s[centre] and
            # s[centre+1]. If those two differ, or centre is the last index,
            # the while body never runs and length comes out as
            # (centre + 1) - centre - 1 = 0, which loses every comparison
            # below - exactly right, since there is no even palindrome here.
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1

            if length > best_length:
                best_length = length
                best_start = left + 1

        # Same thing as s[best_start : best_start + best_length]; the two
        # operands of the sum are simply written the other way round.
        return s[best_start : best_length + best_start]
```

[solution.py](solution.py) · [raw submission](../../data/raw/longest-palindromic-substring.py)

## Why this approach

| Alternative | Cost | Why centre expansion beats it |
|---|---|---|
| Brute force: try every substring, check each for palindromicity | O(n³) time, O(1) space | There are `n(n+1)/2 ≈ 5 × 10⁵` substrings at `n = 1000` and checking one costs up to 1000 comparisons: ~10⁹ operations, a guaranteed TLE in Python. The waste is structural — each check restarts from the ends of a substring whose interior was already examined as part of another substring. |
| DP over a table: `dp[i][j] = (s[i] == s[j] and dp[i+1][j-1])`, filled by increasing length | O(n²) time, **O(n²) space** | Same time bound as this solution, so it is not *slower* — it just costs 10⁶ table entries to store facts the expansion derives on the fly, needs care over the fill order (by length, or bottom-up over `i`), and has two awkward base cases (length 1 and length 2). It is the tagged "Dynamic Programming" answer and it is strictly dominated here. Its one real advantage — answering arbitrary "is `s[i..j]` a palindrome?" queries later — is not something this problem asks for. |
| Manacher's algorithm | **O(n)** time, O(n) space | Genuinely better asymptotically, and it is in the topic tags. But at `n = 1000` the O(n²) solution does ~10⁶ comparisons and finishes in the 200 ms range, so the theoretical win is invisible while the implementation risk is real — the transformed string, the mirror index, the right-boundary bookkeeping. Correct trade only when `n` reaches 10⁵ or more. |
| Longest common substring between `s` and `reversed(s)` | O(n²) and **wrong** | The tempting reduction, and it does not work. On `s = "abacdfgdcaba"` the longest common substring with the reverse is `"abacd"` (length 5), which is not a palindrome at all; the true answer is `"aba"`. Verified, not recalled. It fails because a substring can coincide with the reverse of a *different* part of the string; repairing it means also checking that the two occurrences correspond to the same index range, which is more bookkeeping than the expansion it was meant to replace. |
| Binary search on the answer length + rolling hashes | O(n log n) time, O(n) space | Workable — palindromic lengths are monotone within a parity class, so you can binary search odd and even lengths separately and test each candidate length with hashed comparisons. Far more machinery, a hash-collision caveat, and no benefit at `n = 1000`. |

## Complexity

- **Time — O(n²)**. The outer loop runs `n` times and each pass does two
  expansions, each of which takes at most `O(n)` steps before it runs off an
  end. The bound is tight: on `"aaaa...a"` every expansion runs to the edge, for
  roughly `n²/2` character comparisons — about 5 × 10⁵ at the maximum `n`, which
  is where the 215 ms comes from.
- **Space — O(1)** auxiliary. Four integers (`best_start`, `best_length`,
  `left`, `right`) and nothing that grows with the input. The returned slice is
  O(n), but that is the answer itself, not working memory — and crucially the
  slice is taken **once at the end**, not on every improvement, which would turn
  the copying into an O(n²)-time cost of its own.

## Pitfalls

- **Forgetting the even-length centres.** Returns `"x"` on `"xyzzyx"` instead of
  the whole string, and `"a"` on `"abba"`. This is the single most common way to
  get this problem wrong, and it passes any test whose answer happens to be
  odd-length.
- **Dropping `left >= 0` from the loop condition.** No exception is raised —
  Python wraps `s[-1]` to the last character. On `"aa"` the odd expansion at
  `centre = 0` then matches `s[-1]` against `s[1]`, reports `best_length = 3`
  (longer than the string), and the final slice returns `"a"`. Verified. A crash
  would be kinder than this.
- **Reordering the `while` clauses** so that `s[left] == s[right]` is tested
  before the bounds. `right < len(s)` genuinely protects an `IndexError`, and
  `and` short-circuits left to right, so the order is the guard.
- **`best_start = left` instead of `left + 1`.** Returns a string shifted one
  character left, which on many inputs is still *nearly* right and so survives
  casual eyeballing: on `"bananas"` it gives `"nanan"` rather than `"anana"`.
- **Computing `length` inside the `while` loop** rather than after it. Inside,
  `left` and `right` have not yet overshot, so `right - left - 1` measures the
  wrong window and the final answer comes out too short.
- **`length = right - left + 1`.** The `-1` is there because *both* pointers
  overshot by one. Check it against the smallest case: a single character ends
  with `left = -1, right = 1`, and `1 - (-1) - 1 = 1`.
- **Slicing inside the loop** — `best = s[left+1:right]` on every improvement is
  correct but copies up to `n` characters each time; the `(start, length)`
  representation exists to avoid that.
- **Misreading the final slice.** `s[best_start : best_length + best_start]` is
  the usual `s[start : start + length]` with the addition written backwards. It
  is *not* `s[best_start : best_length]`, which would be the classic bug and is
  right only when `best_start == 0`.
- **The `if not s` guard looks like the base case but is not reachable** — the
  constraints promise a non-empty string. The thing actually doing the work for
  a length-1 input is `best_length = 1`. Delete that initialisation "because the
  loop will set it" and `"abcde"` returns `""`.

## Redo from scratch

1. Say the reframing out loud first: **enumerate centres, not substrings.**
   `2n - 1` of them — `n` characters and `n - 1` gaps.
2. Seed `best_start = 0, best_length = 1`, and be clear why: every single
   character is a palindrome, so this is a valid answer for any non-empty input.
3. Write one expansion, twice: `(centre, centre)` for odd, `(centre, centre+1)`
   for even. Bounds checks *first* in the `while`.
4. After the loop: `length = right - left - 1`, `best_start = left + 1`. Derive
   both from the overshoot rather than recalling them.
5. Return `s[best_start : best_start + best_length]`.
6. Test `"xyzzyx"` (even centre), `"bananas"` (answer in the middle), `"abcde"`
   (nothing longer than 1) and `"q"` (single character).

Be able to justify out loud: **why breaking at the first mismatch cannot miss a
longer palindrome at the same centre** — because any wider window has this one
as its exact middle, and the middle of a palindrome is a palindrome. And the
`2n - 1` count: which centre an even-length palindrome `s[i..j]` belongs to. If
you can only recite the expansion code, the even-centre half will be the part
that goes missing.

## Related problems

- [Palindromic Substrings](../0647-palindromic-substrings/README.md) — already
  solved, and the same code with one line changed: instead of tracking the
  widest expansion, count every expansion. Read the two together; they make it
  concrete that the expansion *enumerates* palindromes, and that what you do
  with each one is a separate question.
- [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/)
  — not solved yet. One word different in the title and a completely different
  algorithm: dropping contiguity destroys the centre argument, and you are back
  to an interval DP. The best possible check on whether "substring" and
  "subsequence" mean distinct things to you.
- [Shortest Palindrome](https://leetcode.com/problems/shortest-palindrome/) —
  not solved yet. Asks for the shortest prefix-extension that makes `s` a
  palindrome, which reduces to finding the longest palindromic *prefix* — the
  same centre machinery constrained to `left` reaching `0`, or a slicker KMP
  failure-function trick.
- [Palindrome Permutation](https://leetcode.com/problems/palindrome-permutation/)
  — not solved yet. Palindromes viewed through character *counts* instead of
  positions (at most one odd count). A useful reminder that "palindrome" admits
  a counting characterisation as well as a two-pointer one.
- [Palindrome Pairs](https://leetcode.com/problems/palindrome-pairs/) — not
  solved yet. Palindromicity across *pairs* of words, solved with a trie plus
  the observation that one word must be the reverse of a prefix of another.
  Uses "is this slice a palindrome?" as a subroutine, which is exactly what this
  problem teaches you to answer cheaply.
- [Maximum Number of Non-overlapping Palindrome Substrings](https://leetcode.com/problems/maximum-number-of-non-overlapping-palindrome-substrings/)
  — not solved yet. Centre expansion feeding a greedy/DP selection on top.
  The natural next step: this problem finds the best palindrome, that one has to
  choose a whole set of them.
