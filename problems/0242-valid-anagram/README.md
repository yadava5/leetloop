# 242. Valid Anagram

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Hash Table, String, Sorting |
| **Solved** | 2026-08-16 |
| **Runtime** | 3 ms (98.40th percentile) |
| **Memory** | 19.5 MB (30.08th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/valid-anagram/ |

## The problem

**Given** two strings `s` and `t`.

**Return** a boolean: `True` if `t` is an anagram of `s`, `False` otherwise.
An anagram is a *rearrangement* — `t` must use exactly the same characters as
`s`, each exactly as many times, in any order. Nothing is added, nothing is
dropped, nothing is substituted. Neither string is modified and nothing is
printed; the return value is the entire answer.

Two consequences of that definition are worth stating explicitly, because they
are what the solution actually tests:

- **Multiplicity counts.** `"aabb"` and `"abbb"` use the same two letters but
  are not anagrams. It is not enough to ask *which* characters appear.
- **Position does not count.** `"listen"` and `"silent"` share no character
  position, and are anagrams. Any comparison that looks at indices is asking
  the wrong question.

**Guaranteed**: both strings are non-empty (`length >= 1`), so there is no
empty-input case to reason about — though this solution would return `True` for
two empty strings anyway, which is the conventional answer.

```text
def isAnagram(self, s: str, t: str) -> bool
```

### Examples (mine, not LeetCode's)

| `s` | `t` | Returns | Why |
|---|---|---|---|
| `"listen"` | `"silent"` | `True` | The ordinary case: same six letters, all positions differ. Frequency tables are identical, so the answer does not depend on order at all. |
| `"aabb"` | `"abab"` | `True` | Repeats are allowed, and the repeats do not have to be adjacent in both strings. `a:2, b:2` on each side. |
| `"aabb"` | `"abbb"` | `False` | **Counterexample to the naive approach.** Same length, and the same *set* of characters `{a, b}`, so `set(s) == set(t)` reports `True` here. It is wrong: `a:2, b:2` is not `a:1, b:3`. This is the input that separates counting from set membership. |
| `"ad"` | `"bc"` | `False` | **Counterexample to a second naive approach.** `97 + 100` and `98 + 99` both equal 197, so a "compare the sum of character codes" hash reports `True`. Sums collide; multisets do not. |
| `"a"` | `"aa"` | `False` | **Edge case:** the shortest legal inputs, and different lengths. No explicit length check exists in the code — the count of `a` differs (1 vs 2), so `Counter` equality catches it on its own. |
| `"x"` | `"x"` | `True` | **Edge case:** minimum input on both sides. A single character is trivially a rearrangement of itself. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length, t.length <= 5 * 10^4` | The lower bound removes the empty string, so "is `""` an anagram of `""`?" never has to be decided. The upper bound is the interesting half: at 5×10^4 per string, anything linear is trivially fast, `O(n log n)` sorting is still comfortably fast (~5×10^4 × 16 ≈ 10^6 comparisons), but an `O(n^2)` approach — for each character of `s`, scan `t` for a match and strike it out — is ~2.5×10^9 operations and will TLE in Python by a wide margin. So the bound rules out the "cross off matching letters" simulation while leaving both the sort and the hash-count solutions on the table. Note the two lengths are bounded *independently*: nothing here promises `len(s) == len(t)`, which is why the solution must handle mismatched lengths rather than assume them away. |

*Only one constraint was captured from the problem statement, so only one is
quoted above. From memory — **recalled, not read**, so treat it as unverified —
the statement also restricts both strings to lowercase English letters, and adds
a follow-up asking what changes if the input may contain Unicode. That
restriction is what would make a fixed 26-slot array viable; this solution does
not rely on it and works for any hashable characters, which is precisely the
follow-up's answer.*

## Key insight

An anagram is a permutation, and a permutation changes only *where* characters
sit, never which ones or how many. So throw away position entirely: reduce each
string to its character-frequency table and compare the tables. Once you state
it that way there is no algorithm left to design — the only decision is how to
represent "frequency table", and `collections.Counter` already is one.

## Approach

1. Build `Counter(s)` — a dict from each distinct character of `s` to its number
   of occurrences. One linear pass over the string.
2. Build `Counter(t)` the same way.
3. Compare the two with `==`. For `Counter`, that is multiset equality: same set
   of keys, same count under every key.
4. Return the result of that comparison. (The submitted code spells this as
   `if ...: return True` / `return False`, which is the same thing in three
   lines instead of one.)

No step's order is load-bearing here — the two Counters are independent, and
there is no loop with a termination condition to get wrong. That is the whole
appeal of the approach: it has no moving parts to misplace.

The one thing worth noticing is what step 3 gets for free. There is deliberately
**no `if len(s) != len(t): return False` guard**, and none is needed: counts sum
to the length, so unequal lengths force at least one differing count. Adding the
guard is a legitimate micro-optimization (it exits before building either
Counter) but not a correctness fix.

## Solution

```python
# 242. Valid Anagram (Easy) - compare the two character multisets with Counter. O(n) time, O(k) space.

# Counter is a dict subclass that maps each distinct element to how many times
# it occurred. Built from a string it is exactly the "letter frequency table"
# this problem is asking about, so the whole solution is one comparison.
from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # An anagram is a reordering, and reordering changes nothing about WHICH
        # characters are present or HOW MANY of each - only their positions. So
        # two strings are anagrams exactly when their frequency tables match.
        # Position information is discarded on purpose; it is the thing the
        # problem says not to care about.
        #
        # Counter equality is multiset equality: same keys, same counts. It also
        # subsumes the length check for free, because if len(s) != len(t) then
        # some character's count must differ (counts sum to the length), so no
        # separate `if len(s) != len(t): return False` guard is needed.
        #
        # Note also that this compares COUNTS, not the set of characters used.
        # set(s) == set(t) would call "aabb" and "abbb" anagrams; Counter does
        # not, because it sees a:2/b:2 against a:1/b:3.
        if Counter(s) == Counter(t):
            return True
        # WART worth knowing: this if/return True/return False is a three-line
        # spelling of `return Counter(s) == Counter(t)`. The comparison is
        # already a bool, so the branch adds nothing but lines. Not a bug and
        # not a slowdown - both Counters are built either way - but the shorter
        # form is what to write next time.
        return False
```

[solution.py](solution.py) · [raw submission](../../data/raw/valid-anagram.py)

## Why this approach

| Alternative | Cost | Why the Counter beats it |
|---|---|---|
| `return sorted(s) == sorted(t)` | O(n log n) time, O(n) space | Correct, and a perfectly respectable one-liner — it is why "Sorting" is one of the topic tags. But it is asymptotically worse for no benefit, and it materialises two lists of `n` single-character objects, which is heavier than a table of at most a few dozen entries. Worth knowing as the answer to "what if you can't use extra space" — sorting in place is O(1) auxiliary in a language with mutable strings, though not in Python. |
| Fixed 26-int array: `+1` for each char of `s`, `-1` for each char of `t`, then check all zero | O(n) time, O(1) space | Genuinely competitive, and lower constant-factor memory than a dict — this is what would improve the 30th-percentile memory number. The cost is that it hard-codes the lowercase-English assumption: one Unicode character and it either crashes on the index or silently mis-buckets. `Counter` answers the problem's own Unicode follow-up without a change. |
| `set(s) == set(t)` | O(n) time, O(k) space | **Wrong, not slow.** `"aabb"` vs `"abbb"` returns `True`. Sets record presence and discard multiplicity, which is exactly the half of the problem that matters. Adding `and len(s) == len(t)` patches this specific case but is still wrong in general: `"aab"` vs `"abb"` has equal lengths and equal sets. |
| Compare a numeric hash — sum of `ord()` values, or sum of squares | O(n) time, O(1) space | **Wrong.** `"ad"` and `"bc"` both sum to 197. Any additive fingerprint collides, because addition is blind to which letters produced the total. The prime-product variant (map each letter to a distinct prime, multiply) *is* sound in Python's bignums, but it is slower than counting, needs a prime table, and overflows in most other languages — a worse solution dressed as a clever one. |
| For each character of `s`, find and remove it from a mutable copy of `t` | O(n^2) time, O(n) space | Correct but quadratic. At `len(t) = 5*10^4` that is ~2.5×10^9 character comparisons; the constraint bound exists precisely to rule this out. |

## Complexity

- **Time — O(n + m)**, where `n = len(s)` and `m = len(t)`. Each Counter is one
  linear pass over its string. The final `==` walks the keys, of which there are
  at most `k` = the number of distinct characters (≤ 26 under the lowercase
  alphabet, and ≤ min(n, m) in general), so it is dominated by the two passes.
  The 3 ms / 98th-percentile runtime comes from `Counter`'s construction being a
  C-level loop (`_collections._count_elements`) rather than a Python-level
  `for` — a hand-written counting loop with the same asymptotics typically
  measures slower here.
- **Space — O(k)**, one dict entry per distinct character, so O(1) under a
  bounded alphabet and O(n) in the worst case if every character is distinct
  (which the Unicode follow-up allows). Two dicts are live at once, which is the
  likely reason memory lands at the 30th percentile while runtime sits at the
  98th: this trades a little space for a lot of speed.

## Pitfalls

- **Comparing sets instead of counts.** `set(s) == set(t)` on `"aabb"` /
  `"abbb"` returns `True`. The classic wrong answer that passes casual tests,
  because most randomly-chosen non-anagram pairs also differ in their character
  sets.
- **Comparing sums of character codes.** `"ad"` vs `"bc"` — both 197 — returns
  `True`. Any commutative fold into a single number will collide eventually.
- **Assuming `len(s) == len(t)`.** The constraint bounds the two lengths
  separately; nothing promises they match. Here it is handled invisibly by the
  count comparison, which is exactly the kind of non-obvious correctness that
  gets "simplified" away later — if you rewrite this as a manual decrement loop,
  the length check stops being free and you must add it back.
- **The decrement-one-Counter variant, and zero counts.** If you rewrite it as
  `c = Counter(s)` then `for ch in t: c[ch] -= 1`, the leftover entries are
  `{'a': 0, 'b': 0, ...}` rather than an empty Counter. On the Python 3.11 used
  here, `c == Counter()` is still `True` — `Counter.__eq__` treats a missing key
  as zero. On older Pythons (before 3.10) `Counter` inherited plain dict
  equality and the same expression was `False`, so this is version-dependent
  behaviour and not something to rely on from memory. `all(v == 0 for v in
  c.values())` is unambiguous everywhere. Note also `not +c` is **not** a
  correct check: unary `+` strips non-positive counts, so it silently hides the
  negative counts that mean `t` has extra characters.
- **`Counter` on something that isn't a string.** `Counter("ab")` is
  `{'a': 1, 'b': 1}`, but `Counter(["ab"])` is `{'ab': 1}`. Passing a list of
  words when you meant the characters of one word gives a silently wrong answer.
- **The if/else wart.** `if cond: return True` followed by `return False` is
  three lines for `return cond`. Harmless, but reviewers notice, and the habit
  hides genuine bugs in longer functions where the two branches drift apart.
- **Reading "anagram" as "permutation with different letters".** Case and
  whitespace, if the constraints ever allowed them, would count as characters —
  `"Listen"` and `"silent"` are *not* anagrams under a literal reading. The
  lowercase-only restriction is what lets that question go unasked.

## Redo from scratch

1. Say out loud what an anagram is: same characters, same multiplicities, any
   order. The algorithm falls out of that sentence.
2. `from collections import Counter`.
3. `return Counter(s) == Counter(t)`. That is the whole solution.
4. Do **not** add a length check thinking it is needed for correctness. Add it
   only if you want the early exit.
5. If you are asked for the no-imports version: a `dict`, `+1` per character of
   `s`, `-1` per character of `t`, then verify every value is zero — plus an
   explicit length check, which is no longer free if you only iterate one string.

Be able to justify out loud:

- **Why a set comparison is wrong and a count comparison is right.** Give
  `"aabb"` vs `"abbb"` as the concrete counterexample: identical sets,
  different multisets.
- **Why no explicit length check is needed.** Because the counts sum to the
  length, so unequal lengths guarantee at least one unequal count — the length
  test is already contained in the multiset test.
- **What changes for the Unicode follow-up.** Nothing, for this solution — that
  is the argument for a hash map over a fixed 26-slot array, and it is the only
  reason to prefer `Counter` over the array in an interview.

## Related problems

- [Group Anagrams](https://leetcode.com/problems/group-anagrams/) — not solved yet. The direct escalation: instead of comparing two strings, bucket `n` of them. It forces the frequency table to become a *hashable key* (a sorted string, or a 26-tuple of counts), which is the same insight used as an index rather than as a comparison.
- [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) — not solved yet. Runs this check at every window position, so rebuilding a Counter each time is O(n·m) and TLEs; you must maintain one Counter incrementally as the window slides. Best next problem, because it teaches the cost of the operation you just used for free.
- [Palindrome Permutation](https://leetcode.com/problems/palindrome-permutation/) — not solved yet. Same frequency table, different predicate: at most one character may have an odd count. Good for seeing that "count the characters" is the reusable primitive and the question is what you then ask of the counts.
- [Determine if Two Strings Are Close](https://leetcode.com/problems/determine-if-two-strings-are-close/) — not solved yet, and not in the similar list. A deliberately weakened version of this problem: the *sets* of characters must match and the *multiset of counts* must match, but counts may be swapped between characters. Solving it right after this one sharpens exactly the set-versus-counts distinction that the `"aabb"` / `"abbb"` counterexample is about.
- [Find Resultant Array After Removing Anagrams](https://leetcode.com/problems/find-resultant-array-after-removing-anagrams/) — not solved yet. Little more than this check applied to adjacent list elements; useful mainly as confirmation that the primitive is the point and the wrapper is trivial.
- [Ransom Note](https://leetcode.com/problems/ransom-note/) — not solved yet, and not in the similar list. The one-sided version: `Counter(note) <= Counter(magazine)` instead of `==`. Worth knowing because Python 3.10 added exactly that `<=` multiset containment operator to `Counter`.

*None of the related problems above are in this repo yet.*
