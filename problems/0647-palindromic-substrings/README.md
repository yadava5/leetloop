# 647. Palindromic Substrings

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Two Pointers, String, Dynamic Programming |
| **Solved** | 2026-09-15 |
| **Runtime** | 117 ms (73.57th percentile) |
| **Memory** | 19.2 MB (68.61th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/palindromic-substrings/ |

## The problem

**Given** a string `s`.

**Return** how many of its contiguous substrings are palindromes — an integer,
not the substrings themselves.

The word that decides this problem is **occurrences, not distinct strings**. A
substring is identified by its start and end positions, so two separate
occurrences of the same text count twice. On `"aaa"` the answer is `6`
(`s[0..0]`, `s[1..1]`, `s[2..2]`, `s[0..1]`, `s[1..2]`, `s[0..2]`) and not `3`.
Single characters count: each is a one-character palindrome. Substrings must be
contiguous — subsequences are not in scope.

**Guaranteed**: `s` is non-empty and consists of lowercase English letters. So
the answer is always at least `len(s)`, and the `if not s` guard in the solution
can never fire.

```text
def countSubstrings(self, s: str) -> int
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `"a"` | `1` | **Edge case:** one character, which is itself a palindrome. Comes entirely from the odd expansion's first iteration, since `s[0] == s[0]` always holds. |
| `"abc"` | `3` | No two characters are equal, so both expansions stop instantly at every centre and only the `n` single characters are counted. This is the floor: the answer can never be less than `len(s)`. |
| `"aaa"` | `6` | **Counterexample to counting distinct substrings.** The distinct palindromic strings here are only `"a"`, `"aa"`, `"aaa"` — three. The answer is six, because the two occurrences of `"aa"` are different substrings. Any solution that puts results in a `set` gets this wrong. |
| `"abba"` | `6` | Four singles, plus `"bb"` at the even centre between indices 1 and 2, plus `"abba"` expanded from the same centre. **An odd-centres-only version returns `4`** — verified. |
| `"xyzyx"` | `7` | Five singles, plus `"yzy"`, plus `"xyzyx"`. Both of the non-trivial ones sit at the *same* centre, one nested inside the other, which is the visual for why a single expansion contributes several counts. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length <= 1000` | The lower bound of `1` makes `if not s: return 0` dead code — never exercised by the judge. The upper bound sets the budget: **n = 1000 puts the O(n²) expansion at roughly 5 × 10⁵ character comparisons, which is nothing**, while the brute force that enumerates all ~5 × 10⁵ substrings and tests each in O(n) is ~10⁹ operations and times out in Python. It also caps the answer at `n(n+1)/2 = 500500`, comfortably inside a machine integer in any language (and irrelevant in Python), and it means **Manacher's O(n) is not worth writing** — there is no input here where it would be measurably faster. Finally, an O(n²) DP table would be 10⁶ booleans: affordable, but pure waste against this solution's O(1). |
| `s consists of lowercase English letters.` | Removes every character-class question before it is asked: **no case folding, no punctuation to skip, no Unicode surprises**, so palindromicity really is plain `==` on characters. It also rules out the "are digits allowed?" hesitation. What it does *not* do is enable a shortcut — a 26-letter alphabet is small enough to tempt a bitmask or per-letter bucketing, but palindromes depend on position, not on which letters appear, so nothing here exploits it. |

## Key insight

This is [Longest Palindromic Substring](../0005-longest-palindromic-substring/README.md)
with the answer read off differently. Expanding around a centre does not just
find the *widest* palindrome there — it walks through **every** palindrome
centred there, one per iteration, from the inside out. So the count you want is
simply the total number of successful expansion steps over all `2n - 1` centres.
Add one inside the loop instead of taking a maximum after it.

The reason no deduplication is needed is worth stating separately: every
palindromic substring has exactly one centre and exactly one radius, so this
enumeration hits each one exactly once — no double counting to correct for, and
no dedup to accidentally introduce.

## Approach

1. Return `0` if `s` is empty. (Dead under the constraints.)
2. `total = 0`.
3. For each index `centre`, run two expansions:
   - **odd**: `left = right = centre`;
   - **even**: `left = centre, right = centre + 1`.
4. In each, while `left >= 0 and right < len(s) and s[left] == s[right]`:
   increment `total`, and step `left` down and `right` up.
5. Return `total`.

What is load-bearing in step 4 is that the increment lives **inside** the
`while` — one per iteration, not one per centre. Its position *within* the body
is not: the total is just the number of successful tests, so moving `total += 1`
below the two pointer updates changes nothing (checked). It is written at the
top only because there it reads as counting `s[left .. right]`, the window the
condition has just validated, which is what the correctness argument below talks
about. The clause order inside the `while` does matter, for the same reason as
in problem 5: `left >= 0` must be tested before `s[left]`, because a negative
index in Python reads from the end of the string instead of failing.

### Why it's correct

**Invariant of a single expansion**: *whenever the loop body executes,
`s[left .. right]` is a palindrome, and it is the `k`-th smallest palindrome
centred here on the `k`-th iteration.* The condition has just shown the two ends
are equal, and the interior `s[left+1 .. right-1]` is either the window counted
on the previous iteration (a palindrome, by this invariant) or — on the first
iteration — a single character in the odd case and the empty string in the even
case, both palindromes. Equal ends around a palindromic interior is a
palindrome. So every `total += 1` corresponds to a real palindromic substring.

**Nothing is counted twice**: fix any palindromic substring `s[i .. j]`. Its
centre is determined by `i + j` — if `i + j` is even it is the character at
`(i+j)/2` and only the odd pass can produce it; if odd it is the gap after
index `(i+j-1)/2` and only the even pass can. Within that one expansion, `left`
strictly decreases every iteration, so `s[i .. j]` appears on exactly one
iteration. One centre, one iteration, one increment.

**Nothing is missed**: the argument runs the other way. That centre is visited,
because both `(i+j)/2` and `(i+j-1)/2` lie in `range(len(s))`. And the expansion
from it does reach `s[i .. j]`, because every window it passes through on the
way — `s[i+d .. j-d]` for `d` from the middle outwards — is a centred
sub-window of the palindrome `s[i .. j]` and therefore itself a palindrome, so
the loop condition holds at each of those steps and the loop cannot have stopped
early. This is also why breaking at the first mismatch is safe: past a mismatch,
no wider window at this centre can be a palindrome, since it would contain the
mismatching pair as its own middle.

Together: a bijection between successful iterations and palindromic substrings.
`total` is the count.

**Termination and the edge of the range.** Each iteration decreases `left` by 1
and increases `right` by 1, both bounded, so every expansion halts within `n`
steps. The odd expansion always runs at least once (`s[centre] == s[centre]`),
contributing the `n` single characters — that is where the floor of `len(s)`
comes from. The even expansion may run zero times, which is correct whenever
`s[centre] != s[centre+1]`, and *must* run zero times at `centre = len(s) - 1`:
there `right = len(s)`, so `right < len(s)` is false on the first test. That
bound being `<` and not `<=` is exactly what makes the last centre behave, and
it is also why the loop never indexes past the end.

The part I would flag as easiest to get wrong on a cold rebuild is the
**level** the increment sits at. The bijection is between *iterations* and
palindromes, so the `+= 1` has to be inside the `while`. Rebuilding this from a
memory of problem 5 — where the interesting work (`max`) happens *after* the
expansion — is exactly how it ends up one level out, counting widest-per-centre
instead of all-per-centre.

## Solution

```python
# 647. Palindromic Substrings (Medium) - expand around each of the 2n-1 centres, adding 1 per successful expansion. O(n^2) time, O(1) space.
class Solution:
    def countSubstrings(self, s: str) -> int:
        # Unreachable on LeetCode: the constraints promise 1 <= s.length.
        if not s:
            return 0


        total = 0

        # Every palindromic substring has exactly ONE centre - a character when
        # its length is odd, the gap between two characters when it is even -
        # and exactly one radius at that centre. So walking all 2n-1 centres
        # and counting every successful expansion counts each palindromic
        # substring once and once only. Nothing is deduplicated, and nothing
        # should be: two occurrences of the same TEXT at different positions
        # are two different substrings and both count.
        for centre in range(len(s)):

            # --- odd lengths: centre is a character. The first test is
            # s[centre] == s[centre], always true, so each of the n single
            # characters is counted exactly here.
            left = centre
            right = centre

            # `left >= 0` is load-bearing: at left == -1 Python wraps round to
            # the end of the string and starts matching unrelated characters.
            # Breaking at the first mismatch is safe because a wider window at
            # this centre contains this one as its middle - if this is not a
            # palindrome, nothing wider here is either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                # One increment per successful test. Written at the top of the
                # body so it reads as counting s[left..right], the window the
                # condition has just proved palindromic - though the total is
                # the same wherever inside the body it sits, since what is
                # really being counted is the number of iterations. What IS
                # load-bearing is that it is inside the while at all: one per
                # ITERATION, not one per centre.
                total += 1

                left -= 1
                right += 1

            # --- even lengths: the centre is the gap between s[centre] and
            # s[centre+1]. If those differ, or centre is the last index, the
            # body never runs and nothing is added, which is correct.
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1

                left -= 1
                right += 1

        return total

```

[solution.py](solution.py) · [raw submission](../../data/raw/palindromic-substrings.py)

## Why this approach

| Alternative | Cost | Why centre expansion beats it |
|---|---|---|
| Brute force: enumerate all substrings, test each one | O(n³) time, O(1) space | ~5 × 10⁵ substrings at `n = 1000`, each tested in up to 1000 comparisons — about 10⁹ operations, a TLE in Python. The waste is that each test re-verifies an interior that some other test already verified; centre expansion is precisely the version that keeps that work. |
| DP table: `dp[i][j] = (s[i] == s[j] and (j - i < 2 or dp[i+1][j-1]))`, count the `True`s | O(n²) time, **O(n²) space** | Matches on time, loses on space (10⁶ entries) and on code: it needs a deliberate fill order — by increasing substring length, or bottom-up over `i` — because `dp[i][j]` depends on `dp[i+1][j-1]`, plus separate base cases for lengths 1 and 2. This is the tagged "Dynamic Programming" solution and it is the same recurrence the expansion walks implicitly, just materialised. |
| Manacher's algorithm | **O(n)** time, O(n) space | Reads the answer off almost for free: the count is `sum((radius + 1))` over all centres. Asymptotically better and genuinely elegant, but at `n = 1000` the quadratic version finishes in ~117 ms and the implementation risk (mirror indices, the right boundary) is real. Reach for it above `n ≈ 10⁵`. |
| Collect palindromes into a `set` and return its size | O(n²) time, O(n²) space, and **wrong** | Returns `3` on `"aaa"` instead of `6`. It answers a different question — *distinct* palindromic substrings, which is its own problem and normally wants an Eertree. The misreading is easy because "count the palindromic substrings" sounds like it could mean either; the examples settle it. |
| Hashing plus binary search on the radius at each centre | O(n log n) time, O(n) space | Correct and asymptotically decent: palindromic radii at a fixed centre are downward-closed, so the largest valid radius can be binary searched with prefix-hash comparisons, and it contributes `radius + 1` to the count. But it needs forward and reverse rolling hashes and carries a collision caveat, for no gain at `n = 1000`. |

## Complexity

- **Time — O(n²)**. `n` centres, two expansions each, each expansion bounded by
  `O(n)` steps before a pointer leaves the string. Tight on `"aaa...a"`, where
  every expansion runs to an edge — about `n²/2 ≈ 5 × 10⁵` comparisons at the
  maximum `n`. Note the count of *successful* iterations is exactly the answer,
  which is itself at most `n(n+1)/2`, so the running time is also bounded by
  the size of the output plus the `2n - 1` failed tests.
- **Space — O(1)**. Three integers: `total`, `left`, `right`. Nothing is stored
  per substring — which is the whole reason the answer can be half a million
  without any memory cost, and the reason the `set`-based variant in the table
  above is worse on both axes as well as wrong.

## Pitfalls

- **Counting distinct strings instead of occurrences.** `"aaa"` is `6`, not `3`.
  Any use of a `set` of substrings produces the wrong answer, and does so
  silently on every input with a repeated palindrome.
- **Forgetting the even-length centres.** `"abba"` returns `4` instead of `6` —
  verified. The single characters still get counted, so the answer looks
  plausible rather than absurd, which is what makes this hard to spot.
- **Incrementing outside the `while` loop** — once per centre rather than once
  per successful test. That counts at most the widest palindrome at each centre
  and misses every one nested inside it. Counting one per expansion that matched
  at least once gives `5` on `"xyzyx"` instead of `7`, and `5` on `"aaa"` instead
  of `6`; counting one per expansion unconditionally gives `10` and `6` — right
  on `"aaa"` by pure coincidence, which is the sort of luck that hides a bug
  through a first test. All verified. This is the bug you get by porting the shape
  of problem 5, where the interesting work happens *after* the expansion,
  without rethinking what is being accumulated. (Moving `total += 1` around
  *within* the loop body, by contrast, is harmless — the total is the iteration
  count.)
- **Dropping `left >= 0` from the condition.** Python does not raise on `s[-1]`,
  it reads the last character, so the expansion quietly matches characters that
  are not adjacent and inflates the count: `"aa"` returns `4` instead of `3`,
  and `"aaa"` returns `9` instead of `6`. Verified. Note that `"abc"` and
  `"abba"` are both unaffected, so the bug hides from exactly the inputs you are
  most likely to try first.
- **Testing `s[left] == s[right]` before the bounds checks.** The `and` chain
  short-circuits left to right; the order *is* the guard, not merely a
  formatting choice.
- **Assuming single characters need a separate `+= len(s)`.** They do not — the
  odd expansion's first iteration is always successful, so they are already
  counted. Adding them again doubles the floor.
- **Using `right <= len(s)`.** At `centre = len(s) - 1` the even pass would
  index `s[len(s)]` and raise. The `<` is what makes the final centre safe.
- **Handling the empty string.** The `if not s` guard is dead under the
  constraints, but the loop would return `0` anyway — `range(0)` is empty.
  Nothing depends on the guard.

## Redo from scratch

1. Settle the ambiguity out loud before writing anything: **occurrences, not
   distinct strings.** `"aaa"` → `6`.
2. Say the reframing: `2n - 1` centres — `n` characters, `n - 1` gaps — and each
   expansion enumerates every palindrome at its centre, innermost first.
3. `total = 0`; loop over `centre`; run the expansion twice,
   `(centre, centre)` and `(centre, centre + 1)`.
4. The increment goes **inside the `while`**, once per successful test — that is
   the one structural difference from problem 5. Bounds checks before the
   character comparison.
5. Return `total`. There is no post-processing, no maximum, no dedup.
6. Test `"abc"` → `3` (the floor), `"aaa"` → `6` (occurrences), `"abba"` → `6`
   (even centres), `"xyzyx"` → `7` (nesting at one centre).

Be able to justify out loud: **why each palindromic substring is counted exactly
once** — the centre is determined by the parity of `i + j`, and within an
expansion `left` strictly decreases, so exactly one iteration produces it. And
**why the increment belongs inside the expansion loop rather than after it**,
which is the same bijection asked of the code rather than of the algorithm. If
you can state the bijection, the code writes itself; if you only remember the
code, the level `total += 1` sits at is where it will go wrong.

## Related problems

- [Longest Palindromic Substring](../0005-longest-palindromic-substring/README.md)
  — already solved, and the direct parent: identical expansion, different
  accumulator. One takes a maximum after the loop, this one counts inside it.
  Reading them side by side is the clearest way to see that centre expansion is
  an *enumeration* and the question only decides what to do with each item.
- [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/)
  — not solved yet. Drop contiguity and the centre argument collapses — there is
  no single centre to expand from — leaving an interval DP over `(i, j)`. The
  sharpest available test of whether "substring" versus "subsequence" is a real
  distinction to you or just a word.
- [Count Different Palindromic Subsequences](https://leetcode.com/problems/count-different-palindromic-subsequences/)
  — not solved yet. The "distinct" reading of this very problem, one level
  harder: both the dedup and the subsequence relaxation at once. Worth a look
  purely to see what the `set`-based misreading of *this* problem would actually
  cost if it were the question.
- [Palindrome Partitioning](https://leetcode.com/problems/palindrome-partitioning/)
  — not solved yet. Backtracking that needs "is `s[i..j]` a palindrome?" over
  and over, and is usually precomputed with the exact DP table this problem's
  solution avoids. Good illustration of when materialising that table finally
  pays for itself.
- [Longest Palindrome](https://leetcode.com/problems/longest-palindrome/) — not
  solved yet. Palindromes by character frequency rather than by position, which
  is the other way of characterising them entirely.
