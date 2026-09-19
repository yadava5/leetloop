# 5. Longest Palindromic Substring

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Two Pointers, String, Dynamic Programming, Manacher |
| **Solved** | 2026-09-18 |
| **Runtime** | 297 ms (46.32th percentile) |
| **Memory** | 19.2 MB (70.19th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/longest-palindromic-substring/ |

## The problem

**Given** a string `s`.

**Return** the longest **contiguous substring** of `s` that reads the same
forwards and backwards. The substring itself, not its length and not its indices.

Three things to be precise about:

- **Substring, not subsequence.** Characters must be adjacent in the original.
  The longest palindromic *subsequence* of `"abcba"` and of `"abccba"` are
  different questions with different (and harder) answers.
- **Any longest one will do.** If several share the maximum length, LeetCode
  accepts any of them. This solution returns the leftmost, by using a strict `>`
  when comparing lengths — a deliberate choice for determinism, not a
  requirement.
- **Length 1 counts.** Every single character is a palindrome, so the answer is
  never empty for a non-empty input. On `"abc"` the answer is `"a"`.

**Guaranteed**: `1 <= s.length`, so the string is never empty and an answer
always exists. Characters may be letters or digits; nothing here depends on the
alphabet.

```text
def longestPalindrome(self, s: str) -> str
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `"aba"` | `"aba"` | The odd case: a palindrome centred on a character, radius 1. |
| `"abba"` | `"abba"` | **The even case, and the reason the loop runs twice per position.** This palindrome is centred on the *gap* between the two `b`s. A solution that only expands around characters answers `"bb"` — plausible-looking and wrong. |
| `"abc"` | `"a"` | **Edge case:** no palindrome longer than one character. The answer comes from the seed `(best_start=0, best_string=1)` rather than from any comparison inside the loop, because `1 > 1` is false. |
| `"bananas"` | `"anana"` | A longer odd palindrome that is neither a prefix nor a suffix, sitting at index 1. Good for catching an off-by-one in the start index: `best_start = left` instead of `left + 1` returns `"banan"` here — same length, wrong window, and it *looks* like a palindrome at a glance. |
| `"xabay"` | `"aba"` | The answer is strictly interior, with junk on both sides. The expansion from centre `2` must stop at the mismatched `x`/`y`, not run past them. |
| `"abacdfgdcaba"` | `"aba"` | **Counterexample to "reverse the string and take the longest common substring."** That method returns `"abacd"` (length 5) here, because `"abacd"` also appears in the reversed string — but it is not a palindrome. The true answer is a mere `"aba"`. |
| `"z"` | `"z"` | **Edge case:** one character. Both `while` loops at the single centre stop immediately or run once trivially; the seed supplies the answer. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length <= 1000` | The upper bound is the whole story: at `n = 1000`, an O(n²) method is ~10⁶ character comparisons, which is comfortable in Python, while the O(n³) "check every substring for palindromicity" is ~10⁹ and will TLE. So the bound rules **in** expand-around-centre and the O(n²) DP table, and rules **out** brute force — while making Manacher's O(n) algorithm entirely unnecessary. That is worth saying plainly: the constraint is small on purpose, and reaching for Manacher here is over-engineering, not optimisation. The bound also rules in O(n²) *space* if you want the DP table (10⁶ booleans), though this solution needs none. The lower bound of `1` means the string is never empty, so the `if not s` guard is dead code and the seed of `best_string = 1` is always a valid standing answer. |

## Key insight

Every palindrome is determined by its **centre** plus how far it extends, so
instead of hunting for palindromes, enumerate the centres and grow each one
outward until the characters stop matching. There are `2n - 1` centres — `n`
characters for the odd-length palindromes and `n - 1` gaps between adjacent
characters for the even-length ones — and each expansion is cheap, which turns an
apparently O(n³) search into O(n²).

The thing to whisper if stuck: *don't search for palindromes, grow them.* And
immediately after: *there are two kinds of centre, and forgetting the gaps is the
bug.*

## Approach

1. Carry the answer as `(best_start, best_string)` — a start index and a
   **length** — and slice exactly once at the end. Slicing inside the loop would
   copy up to `n` characters on every improvement.
2. Seed with `best_start = 0`, `best_string = 1`: the first character, which is
   always a valid answer.
3. For each index `centre`:
   - **Odd:** set `left = right = centre` and expand while the ends match.
   - **Even:** set `left = centre`, `right = centre + 1` and expand the same way.
4. Inside each expansion step, after moving both pointers, compute the width as
   `right - left - 1` and record it if it beats the best.
5. Return `s[best_start : best_start + best_string]`.

Two details are load-bearing:

- **`left >= 0` in the `while` guard.** This is not defensive coding. Python
  wraps a negative index to the *end* of the string, so without the test the
  expansion keeps comparing `s[-1]` against characters near the front and can
  "succeed" on nonsense. Concretely, dropping it makes `"aa"` return `"a"` and
  `"aab"` return `"b"`.
- **`best_start = left + 1`, not `left`.** When the loop exits — or, here, after
  each step — `left` and `right` sit one past the palindrome on both sides. The
  window is `s[left+1 .. right-1]`, whose length is
  `(right - 1) - (left + 1) + 1 = right - left - 1`. The two off-by-ones have to
  agree with each other.

**A note on where the measurement lives.** This submission recomputes the width
and compares *inside* the `while` body, after every successful expansion, rather
than once after the loop ends. Both are correct: expansions at a given centre
grow monotonically, so the last one recorded is the widest, and any earlier
recording is simply superseded. The in-loop version does a little more work — a
subtraction and a comparison per expansion step rather than per centre — which is
the most likely source of the 297 ms. It is also the version that *must* measure
inside the body for the even case to behave: when an even centre fails
immediately the body never runs, and nothing is recorded at all, which is right
because the width there would be `0`.

### Why it's correct

**Invariant**: after the `centre = c` iteration completes, `(best_start,
best_string)` describes a genuine palindromic substring of `s`, and its length is
the maximum over all palindromes whose centre is at index `≤ c` — counting both
the character-centres and the gap-centres up to that point.

That the recorded window is always a genuine palindrome follows from the
expansion itself: the `while` only steps when `s[left] == s[right]`, and it
starts from a trivially palindromic core (a single character, or an empty gap
that is only stepped past if the two neighbours match). By induction, each
successful step wraps a matching pair around a known palindrome, which is a
palindrome.

**Why stopping at the first mismatch loses nothing.** When the expansion at a
centre halts, no *wider* window at that same centre can be a palindrome either,
because any wider window contains the current, failed one as its middle — and a
palindrome's middle is always a palindrome. So there is no reason to keep
expanding past a mismatch, and no palindrome is skipped by stopping.

**Why enumerating centres is exhaustive.** A palindrome of odd length `2r+1` has
a unique middle character; one of even length `2r` has a unique middle gap. Every
palindromic substring therefore has exactly one of the `2n - 1` centres, and the
loop visits all of them: the `centre` variable supplies the `n` character-centres
directly, and the `(centre, centre + 1)` pairing supplies the `n - 1` gaps (the
final iteration's gap has `right = n`, which fails the `right < len(s)` test
immediately, so it contributes nothing — correct, as there is no gap after the
last character).

**Termination and the edge of the range.** Each `while` iteration strictly
decreases `left` and increases `right`, and both are bounded by the guard
(`left >= 0` below, `right < len(s)` above), so each loop runs at most `n/2`
times and halts. The `for` is a finite range. The guards short-circuit left to
right, so `left >= 0 and right < len(s)` is fully checked before `s[left]` is
evaluated — swapping the comparison to the front would index out of range. At the
low end of the range, `centre = 0`'s odd expansion immediately steps to
`left = -1`, and it is precisely the `left >= 0` test that stops the next
iteration from wrapping around.

The subtlety I am least sure of when reconstructing this cold is the seed
interacting with the strict `>`. The seed says "length 1 starting at 0", and the
odd loop *does* compute a width of `1` at every centre — but `1 > 1` is false, so
those never overwrite the seed. The consequence is that on a string with no
palindrome longer than one character, the answer is always `s[0]` specifically,
supplied by the seed rather than by the loop. That is correct, and it is also the
kind of interaction that makes "just initialise it to 0 instead" feel like a free
change — it happens to also be correct here, since the first odd expansion
records a `1`, but the two facts are worth separating rather than conflating.

## Solution

```python
# 5. Longest Palindromic Substring (Medium) - expand around all 2n-1 centres, recording the widest window as it grows. O(n^2) time, O(1) extra space.
class Solution:
    def longestPalindrome(self, s: str) -> str:

        # Unreachable on LeetCode: the constraints promise 1 <= s.length, so
        # s is never empty. Costs nothing and makes the function total if it
        # is ever called from elsewhere.
        if not s:
            return ""

        # The answer is carried as (start, length), never as a string.
        # Slicing inside the loop would copy up to n characters every time a
        # wider palindrome turned up; slicing once at the end copies once.
        #
        # `best_string` holds a LENGTH, not a string - the name is a wart.
        # Seeding it at 1 with best_start 0 means "the first character" is the
        # standing answer: every single character is a palindrome, so on a
        # string with no palindrome longer than 1 ("abc") the loop below never
        # improves on this and s[0] is returned. Note the loop does compute a
        # length of 1 at every odd centre, but `1 > 1` is false, so it is the
        # seed and not the loop that supplies that case.
        best_string = 1
        best_start = 0

        # Every palindrome is pinned by a CENTRE plus a radius, and there are
        # 2n-1 centres: n characters (odd lengths) and n-1 gaps between
        # adjacent characters (even lengths). Each pass handles both kinds
        # anchored at `centre`, so all 2n-1 are covered.
        for centre in range(len(s)):

            # --- odd lengths. The window starts as the single character
            # s[centre], which is trivially a palindrome, so this while always
            # runs at least once.
            left = centre
            right = centre

            # `left >= 0` is load-bearing, not defensive. Once left reaches -1
            # Python wraps it to the END of the string and starts comparing
            # characters nowhere near each other: without this test, "aa"
            # returns "a" and "aab" returns "b".
            #
            # Stopping at the first mismatch is safe because any wider window
            # at this centre CONTAINS this one as its middle, so if this one
            # is not a palindrome no wider one can be either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1

                # Measured INSIDE the loop, after each successful step. left
                # and right have already moved one past the palindrome on both
                # sides, so the real window is s[left+1 .. right-1] and its
                # length is (right - 1) - (left + 1) + 1 = right - left - 1.
                current_string = right - left - 1

                # Strict `>` keeps the FIRST palindrome of a given length,
                # i.e. the leftmost. LeetCode accepts any longest one; this
                # just makes the output deterministic.
                if current_string > best_string:
                    best_string = current_string

                    # left overshot by one, so the window begins at left + 1.
                    # Writing `best_start = left` is the classic off-by-one:
                    # it turns "abba" into "" and "bananas" into "banan".
                    best_start = left + 1


            # --- even lengths. The centre is now the GAP between s[centre]
            # and s[centre+1]. If those differ, or centre is the last index,
            # the body never runs and nothing is recorded for this centre -
            # correct, since there is no even palindrome here. (Unlike the odd
            # case, this loop can record nothing at all, which is why the
            # measurement lives inside the body rather than after it.)
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1

                current_string = right - left - 1

                if current_string > best_string:
                    best_string = current_string

                    best_start = left + 1

        return s[best_start : best_start + best_string]
```

[solution.py](solution.py) · [raw submission](../../data/raw/longest-palindromic-substring.py)

## Why this approach

| Alternative | Cost | Why expand-around-centre beats it |
|---|---|---|
| Brute force: every substring, check each for palindromicity | O(n³) time, O(1) space | ~10⁹ character operations at `n = 1000` — a certain TLE in Python. The waste is that checking `s[i..j]` learns nothing that helps with `s[i..j+1]`, whereas expanding from a centre reuses the entire previous check. |
| DP table: `dp[i][j]` is true iff `s[i..j]` is a palindrome, built from `dp[i+1][j-1]` | O(n²) time, O(n²) space | **Correct and the same asymptotic time**, and it is why "Dynamic Programming" is a topic tag. But it pays 10⁶ booleans of memory for the identical bound, needs careful iteration order (by increasing substring length, or the recurrence reads unfilled cells), and has two base cases to get right. The centre expansion is the same algorithm with the table thrown away. Worth being able to write if asked for "the DP solution" by name. |
| Reverse the string, take the longest common substring | O(n²) time, O(n²) space | **Wrong**, and a genuinely popular suggestion. A substring shared with the reverse need not be a palindrome — it may match a *different* part of the reversed string. On `"abacdfgdcaba"` it returns `"abacd"` (length 5) where the answer is `"aba"`. It can be repaired by checking that the match's positions correspond, at which point it is strictly more machinery than the centre expansion for the same bound. |
| Manacher's algorithm | O(n) time, O(n) space | Correct, and the reason "Manacher" is tagged. At `n = 1000` it saves nothing measurable — O(n²) here is ~10⁶ operations, already fast — while costing a transformed string, a radius array, and a mirror-and-rightmost-boundary argument that is hard to reproduce correctly under pressure. Reach for it only if the constraint grows by orders of magnitude. |
| Expanding around character centres only | — | **Wrong**: misses every even-length palindrome. `"abba"` returns `"bb"` instead of `"abba"`. It passes any test whose answer happens to be odd-length, which is easy to arrange accidentally. |

## Complexity

- **Time — O(n²)**. There are `2n - 1` centres, and each expands at most `n/2`
  steps before hitting a mismatch or a boundary, giving ~n²/2 character
  comparisons — about 5 × 10⁵ at `n = 1000`. The worst case is a string of
  identical characters like `"aaaa…"`, where every centre expands all the way to
  the boundaries and nothing ever short-circuits. The 297 ms reflects both that
  and the per-step subtract-and-compare this version does inside the loop rather
  than after it.
- **Space — O(1)** auxiliary. Four integers and two loop pointers; no table, no
  transformed string, no recursion. The returned slice is O(n), but that is the
  required output rather than working space — which is what the solid 70th
  percentile memory reading reflects.

## Pitfalls

- **Handling only odd-length palindromes.** `"abba"` returns `"bb"`. This is the
  single most common failure, because the odd case is the one that comes to mind
  first and it produces a *plausible* answer rather than a crash.
- **`best_start = left` instead of `left + 1`.** Both pointers overshoot by one,
  so the recorded window is shifted left by one and no longer a palindrome:
  `"abba"` returns `""` (an empty string, because the shifted slice runs off the
  front), `"xabay"` returns `"xab"`, `"bananas"` returns `"banan"`. The length is
  right, which is what makes it survive any test that only checks lengths.
- **Dropping the `left >= 0` guard.** Python's negative indexing turns the
  overshoot into a silent wrap to the end of the string, so the expansion can
  match characters from opposite ends. `"aa"` returns `"a"`; `"aab"` returns
  `"b"`. There is no exception — it is simply wrong.
- **Getting the width formula wrong.** After the pointers move, the width is
  `right - left - 1`, not `right - left` or `right - left + 1`. The `-1` is
  because *both* ends overshot. Check it against a known case:
  expanding `"aba"` from centre 1 ends with `left = -1`, `right = 3`, and
  `3 - (-1) - 1 = 3`. ✓
- **Returning the length instead of the substring.** The problem asks for the
  string. `best_string` holds a length despite its name, and the final slice is
  what converts it — the naming makes this easy to trip over months later.
- **Reaching for Manacher.** At `n ≤ 1000` it buys nothing and costs a great deal
  of correctness risk. Knowing *when* an O(n²) solution is already sufficient is
  part of the answer here.
- **Slicing inside the loop to track the best.** Correct but wasteful: each
  improvement copies up to `n` characters, and on `"aaaa…"` improvements happen
  ~n²/2 times, which turns an O(n²) algorithm into O(n³) work. Carrying
  `(start, length)` is why this version stays within budget.

## Redo from scratch

1. Every palindrome has a centre; there are `2n - 1` of them, `n` characters and
   `n - 1` gaps. Enumerate centres, don't search substrings.
2. Carry `(best_start, best_length)`, **not** a string — slice once at the end.
3. For each centre, run the expansion twice: `(c, c)` for odd and `(c, c + 1)`
   for even.
4. Guard with `left >= 0 and right < len(s)` **before** comparing characters, and
   remember both pointers overshoot by one: the width is `right - left - 1` and
   the start is `left + 1`.
5. Test `"abba"` (even centre), `"abc"` (no palindrome longer than 1), `"aa"`
   (the negative-index wrap), `"bananas"` (interior answer, catches the start
   off-by-one), `"z"` (single character).

Be able to justify out loud: **why there are exactly `2n - 1` centres and why
that makes the enumeration exhaustive** — that every palindrome has a unique
middle, a character if its length is odd and a gap if it is even. And second:
**why stopping at the first mismatch is safe** — that any wider window at the
same centre contains the failed one as its middle, and a palindrome's middle is
always a palindrome, so nothing is lost by halting. If you can state both, the
DP table and Manacher both become optimisations of a machine you already
understand rather than separate things to memorise.

## Related problems

- [Palindromic Substrings](../0647-palindromic-substrings/README.md) — solved,
  and the closest relative by far. It is *this exact loop* with the body changed
  from "record if longest" to "add one to a counter", since every successful
  expansion step is itself a distinct palindrome. Reading the two together is the
  fastest way to see the centre expansion as a technique rather than a solution.
- [Valid Palindrome](../0125-valid-palindrome/README.md) — solved. The
  primitive: two pointers walking inward to test *one* window. This problem is
  that check run outward from every centre instead of inward from the ends.
- [Palindrome Number](../0009-palindrome-number/README.md) — solved. The same
  symmetry idea on digits with no string at all. Unrelated mechanically, but it
  is where the "compare from both ends" reflex comes from.
- [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/)
  — not solved yet, and the instructive contrast. Dropping the contiguity
  requirement breaks the centre argument entirely: a subsequence has no centre to
  expand from, so it needs a genuine interval DP. Doing it right after this one
  makes clear exactly which property the expansion was exploiting.
- [Shortest Palindrome](https://leetcode.com/problems/shortest-palindrome/) — not
  solved yet. Asks for the shortest prefix-extension that makes the whole string
  a palindrome, which reduces to finding the longest palindromic *prefix* — a
  restricted version of this problem, usually solved with KMP. Good for seeing
  the same question under a different constraint.
- [Palindrome Pairs](https://leetcode.com/problems/palindrome-pairs/) — not
  solved yet. The hard end of the family: palindromes formed by concatenating
  pairs of words, which needs a trie plus this palindrome test as a subroutine.
  Worth knowing it exists, not worth attempting until the above are automatic.
