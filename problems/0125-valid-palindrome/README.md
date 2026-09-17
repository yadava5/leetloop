# 125. Valid Palindrome

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Two Pointers, String |
| **Solved** | 2026-09-15 |
| **Runtime** | 7 ms (80.69th percentile) |
| **Memory** | 19.5 MB (94.54th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/valid-palindrome/ |

## The problem

**Given** a string `s` that may contain letters, digits, punctuation and spaces
in any mixture of cases.

**Return** `True` if, after **deleting every non-alphanumeric character** and
**folding all letters to one case**, what remains reads the same forwards and
backwards. `False` otherwise. A boolean — you are not asked to produce the
cleaned string.

Three details the definition settles. **Digits count** as alphanumeric and are
compared as themselves — `"0P"` is *not* a palindrome, because `'0'` and `'p'`
are different characters, and the fact that `'0'` looks like an `'O'` is a
red herring the problem is fond of. Everything that is neither a letter nor a
digit is **deleted, not treated as a wildcard**, so underscores, spaces and
punctuation simply vanish. And a string that cleans down to **nothing at all**
is a palindrome — the empty string reads the same both ways.

**Guaranteed**: `s` is non-empty. That promise is barely used; the code returns
`True` on `""` anyway, since `right = -1` makes the loop body unreachable.

```text
def isPalindrome(self, s: str) -> bool
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `"Zz"` | `True` | Case folding, minimal form. Without `.lower()` this returns `False`, so it is the smallest input that separates the two. |
| `"0P"` | `False` | **Counterexample to sloppy case handling.** `'0'` and `'P'` are both alphanumeric, so neither is skipped, and `'0' != 'p'`. Anyone who normalises with something looser than exact character comparison — or who assumes only letters survive the filter — gets `True` here. |
| `"ab_a"` | `True` | The underscore is **not** alphanumeric (`'_'.isalnum()` is `False`), so it is deleted and the string cleans to `"aba"`. Easy to get wrong if you reach for `isidentifier`-style thinking or a regex like `\w`, which *does* match underscore. |
| `"..."` | `True` | **Edge case:** nothing survives the filter, and the empty string is a palindrome. This is also the input that crashes an implementation whose inner skip loops lack the `left < right` guard. |
| `"race a car"` | `False` | Cleans to `"raceacar"`, whose reverse is `"racaecar"` — the first mismatch is at the fourth character, `'e'` against `'a'`. A case where the spaces make the string *look* more symmetric than it is. |
| `"A man, a plan, a canal: Panama"` | `True` | The full workout: mixed case, spaces, a comma and a colon, all in one. Verified. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length <= 2 * 10^5` | The lower bound of `1` means **`s` is never empty**, so no guard is needed — although the loop degenerates harmlessly anyway, since `right` starts at `-1` and `0 < -1` is false. The upper bound is what makes the in-place filtering worth doing: **2 × 10⁵ characters is far too many to be casual about allocating**, and the tempting one-liner (`t = [c.lower() for c in s if c.isalnum()]; return t == t[::-1]`) builds *two* extra sequences of that size. It is still O(n) and still passes comfortably — but it is where the 94.54th-percentile memory figure comes from not being spent. The bound also rules out anything super-linear: an O(n²) approach at 2 × 10⁵ is 4 × 10¹⁰ operations and hopeless. |

One honesty note about this table: the fetched `constraints` array contains only
this single bound. The statement also restricts `s` to printable ASCII, which
was not captured. Nothing here depends on it — `.isalnum()` and `.lower()` are
defined for the whole of Unicode — but it is worth knowing that on a genuinely
Unicode input `.isalnum()` admits letters and digits from every script, which
may or may not be what a caller outside LeetCode wants.

## Key insight

You never have to build the cleaned string. Walk two pointers inwards and let
each one **skip forward over junk on its own** before the comparison; the filter
becomes part of the traversal rather than a preprocessing step. That is what
turns an O(n)-space problem into an O(1)-space one, and it is the whole reason
this is tagged Two Pointers rather than String.

The one thing that then needs care is that the skipping can run off the end, so
every skip must be bounded by the *other* pointer.

## Approach

1. `left` at the start, `right` at the last index.
2. While `left < right`:
   - advance `left` past any non-alphanumeric character, **never past `right`**;
   - retreat `right` past any non-alphanumeric character, **never past `left`**;
   - compare `s[left].lower()` with `s[right].lower()`; return `False` on a
     mismatch;
   - step both pointers inwards.
3. If the loop completes, return `True`.

Two things are load-bearing. **The `left < right` clause inside each inner
`while`** is not defensive padding — it is the termination condition for the
skip. On `"..."` an unguarded `while not s[left].isalnum(): left += 1` walks
straight off the end of the string and raises `IndexError`. And **both pointers
must move after a successful match**; moving only one compares a character
against its own neighbour and, on a repeated character like `"aa"`, never
terminates.

### Why it's correct

**Invariant**: at the top of each iteration, every alphanumeric character
*outside* the range `s[left .. right]` has already been matched against its
mirror, and all those comparisons succeeded.

The body preserves it. The two skips discard only characters that the cleaned
string does not contain, so they cannot break a pairing. The comparison then
matches the outermost surviving character on each side — which, given that
everything outside has already been paired off in order, are genuinely each
other's mirrors in the cleaned string. Success shrinks the range by exactly that
pair and the invariant carries. A mismatch returns `False`, correctly, because
those two characters occupy mirror positions in the cleaned string and differ.
When the loop ends, at most one alphanumeric character lies inside the range,
which is the middle character of an odd-length cleaned string and has no partner
to contradict.

**Termination and the edge of the range.** Each inner `while` is bounded by
`left < right`, so no pointer can pass the other, and each outer iteration
either returns or strictly decreases `right - left` by two. The loop therefore
ends after at most `n/2` iterations. The case worth checking by hand is the one
where the skips collapse both pointers onto the **same index** — `" a "`, say,
or `"..."` where they meet on a full stop. The comparison then evaluates
`s[left].lower() != s[left].lower()`, which is `False`, so no spurious mismatch
is reported; the increments then cross the pointers and the loop exits `True`.
This is the non-obvious case that makes the code correct without a special
branch, and it is exactly the sort of thing a reader "simplifying" this function
would break.

## Solution

```python
# 125. Valid Palindrome (Easy) - two pointers converging from the ends, skipping non-alphanumerics in place and comparing case-folded. O(n) time, O(1) space.
class Solution:
    def isPalindrome(self, s: str) -> bool:

        left = 0
        right = len(s) - 1

        # Filtering in place rather than building a cleaned copy first is what
        # keeps this O(1) in extra space. On the empty string right is -1 and
        # the body never runs, returning True - which is the right answer,
        # though the constraints promise a non-empty s.
        while left < right:

            # Advance past anything that is not a letter or a digit.
            # `left < right` inside these inner loops is load-bearing, not
            # belt-and-braces: on a string with no alphanumerics at all, such
            # as "...", an unguarded scan would walk left off the end of the
            # string and raise IndexError. With the guard, left simply stops
            # once it meets right.
            while left < right and not s[left].isalnum():
                left += 1

            while left < right and not s[right].isalnum():
                right -= 1

            # If the skipping above collapsed the two pointers onto the same
            # index, this compares a character with ITSELF and is therefore
            # equal - so a single leftover character never causes a false
            # negative. That case then falls through to the increments below,
            # which cross the pointers and end the loop.
            #
            # .lower() on both sides is the case folding. Note isalnum() also
            # admits digits, and digits are unaffected by lower(), so numbers
            # compare as themselves.
            if s[left].lower() != s[right].lower():
                return False

            # Unconditional: the pair just matched, so both ends are consumed.
            # Moving only one pointer here would compare the same character
            # against its neighbour and loop forever on a match.
            left += 1
            right -= 1

        # Pointers crossed without a mismatch, so every alphanumeric pair
        # agreed and the string is a palindrome.
        return True
```

[solution.py](solution.py) · [raw submission](../../data/raw/valid-palindrome.py)

## Why this approach

| Alternative | Cost | Why the in-place two pointers beat it |
|---|---|---|
| Filter into a new string, then compare with its reverse: `t = [c.lower() for c in s if c.isalnum()]; return t == t[::-1]` | O(n) time, **O(n) space** | Shorter, obviously correct, and in CPython often *faster*, because the filtering and the reversal both run in C. It is disqualified only by the O(1)-space expectation — and that is a real expectation for this problem, since "do it without building the cleaned string" is the entire difficulty. Know it as the answer in production code. |
| `re.sub(r'[^a-z0-9]', '', s.lower())` then compare with the reverse | O(n) time, O(n) space | Same trade, plus a regex to get wrong. Note `\w` would be the natural shorthand and is **wrong here**: `\w` matches underscore, so `"ab_a"` would clean to `"ab_a"` and return `False` instead of `True`. Verified: `'_'.isalnum()` is `False`. |
| Recursion on the trimmed ends | O(n) time, **O(n) stack** | At 2 × 10⁵ characters this blows Python's default recursion limit of 1000 long before it finishes. Elegant on paper, unusable here. |
| Precompute the indices of the alphanumeric characters, then two-pointer that list | O(n) time, O(n) space | Correct, and it does separate the two concerns cleanly — but it allocates an index list of nearly the input's size to avoid a skip loop that costs nothing. |
| Compare `s[left] == s[right]` without case folding | O(n) and **wrong** | Returns `False` on `"Zz"` and on `"A man, a plan, a canal: Panama"`. The problem says case-insensitively. |
| Filter with `c.isalpha()` instead of `c.isalnum()` | O(n) and **wrong** | Deletes the digits along with the punctuation. `"0P"` cleans to `"p"`, a one-character string, and comes back `True` where the answer is `False`. Verified. The easiest of these to write by accident, because "alphanumeric" and "alphabetic" differ by three characters and the test cases that expose it are rare. |

## Complexity

- **Time — O(n)**. Every index is visited at most once by `left` and at most once
  by `right`, counting the inner skip loops: neither pointer ever moves backwards,
  so the inner `while`s amortise into the single sweep rather than multiplying it.
  One `.isalnum()` and at most two `.lower()` calls per character.
- **Space — O(1)**. Two integers and the one-character strings produced by
  `.lower()`, which are transient. Nothing proportional to `n` is allocated —
  which is where the 94.54th-percentile memory comes from, and the only real
  advantage over the filter-and-reverse one-liner.

## Pitfalls

- **Omitting `left < right` from the inner skip loops.** On a string with no
  alphanumeric characters at all — `"..."`, `",,"`, `" "` — `left` walks past the
  end and raises `IndexError`. This is the crash, and it only shows up on inputs
  most people never write a test for.
- **Using `\w` or `isidentifier`-flavoured filtering.** `\w` includes underscore,
  so `"ab_a"` would fail. `'_'.isalnum()` is `False`, which is the behaviour the
  problem wants; `str.isalnum()` is the right predicate and is easy to reach past.
- **Forgetting `.lower()`.** `"Zz"` returns `False`.
- **Filtering with `.isalpha()` rather than `.isalnum()`.** Silently deletes the
  digits, so `"0P"` cleans to `"p"` and returns `True` instead of `False`. The
  problem counts digits as content.
- **Moving only one pointer after a match.** `left += 1` without `right -= 1`
  compares each character against a fixed right-hand character; on `"aa"` the
  pointers never cross the way you expect and the function either loops or
  reports nonsense. Both ends are consumed by a successful comparison.
- **Special-casing the pointers landing on the same index.** They can, and the
  code already handles it: the character compares equal to itself, so nothing is
  reported and the increments end the loop. Adding a branch is harmless, but
  *removing* the possibility — e.g. by asserting `left != right` — turns a
  correct non-obvious case into a crash. This is the line most likely to be
  "simplified" back into a bug by a future reader.
- **Assuming the cleaned string is non-empty.** `"..."` cleans to `""` and the
  answer is `True`. A filter-then-compare solution gets this right by accident;
  anything that indexes `t[0]` does not.
- **Returning `True` from inside the loop** on a successful match. The loop must
  run to completion; a single matching pair proves nothing about the rest.
  `"abca"` would return `True` after matching the two `a`s.

## Redo from scratch

1. Say the framing: **filter during the walk, not before it.** That is what makes
   it O(1) space and it is the only reason this is not a one-liner.
2. Pointers at both ends, `while left < right`.
3. Two inner skip loops, each with `left < right` in its own condition. Write
   that clause at the same moment you write the `while`, not as an afterthought.
4. Compare with `.lower()` on both sides — and remember digits are in play, so
   the fold must be a real `.lower()` and not a bit trick.
5. Step both pointers inwards.
6. Test `"..."` (crashes an unguarded version), `"0P"` (digits), `"ab_a"`
   (underscore), `"Zz"` (case).

Be able to justify out loud: **why the inner loops need their own `left < right`
bound**, with `"..."` as the concrete crash. And **what happens when both
pointers land on the same character** — that it compares equal to itself and
costs nothing — because that is the case that makes the absence of a special
branch correct rather than lucky.

## Related problems

- [Palindrome Number](../0009-palindrome-number/README.md) — already solved, and
  the same property tested on an integer with arithmetic instead of pointers.
  Together they make the point that "palindrome" is a property and the traversal
  is a separate choice.
- [Palindromic Substrings](../0647-palindromic-substrings/README.md) and
  [Longest Palindromic Substring](../0005-longest-palindromic-substring/README.md)
  — both already solved, and both the *inverse* motion: expanding outwards from a
  centre rather than converging from the ends. Worth reading straight after this
  one to fix which direction belongs to which question.
- [Valid Palindrome II](https://leetcode.com/problems/valid-palindrome-ii/) — not
  solved yet, and the best follow-up: you may delete at most one character, so on
  a mismatch you branch into two ordinary palindrome checks. It reuses this exact
  loop as a subroutine and teaches the "try both, recurse once" pattern.
- [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/)
  — not solved yet. The same check without random access, which forces reversing
  half the list in place. The O(1)-space requirement there is genuinely hard
  rather than merely preferred.
- [Valid Palindrome IV](https://leetcode.com/problems/valid-palindrome-iv/) — not
  solved yet. Two moves allowed instead of a deletion; a variation on the same
  two-pointer scan with a counter.
- [Find First Palindromic String in the Array](https://leetcode.com/problems/find-first-palindromic-string-in-the-array/)
  — not solved yet, and close to free once this is understood: the check from
  this page applied in a loop.
