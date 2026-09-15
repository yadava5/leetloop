# 14. Longest Common Prefix

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, String, Trie |
| **Solved** | 2026-08-16 |
| **Runtime** | 0 ms (100.00th percentile) |
| **Memory** | 19.3 MB (31.22th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/longest-common-prefix/ |

## The problem

**Given** a list of strings `strs`.

**Return** the longest string that is a prefix of *every* string in the list. If
there is no such string beyond the empty one, return `""` — never `None`, never
a sentinel.

"Prefix" means a leading run of characters starting at index 0. `"ab"` is a
prefix of `"abc"`; `"bc"` is not. So the answer is always `strs[0][:i]` for some
`i`, and the entire problem is finding the largest legal `i`.

Nothing is modified and nothing is printed; the returned string is the whole
answer.

**Guaranteed**: the list itself is non-empty (`1 <= strs.length`), so `strs[0]`
can be taken without a guard. **Not** guaranteed: that the strings are non-empty
— `0 <= strs[i].length` means `""` is a legal member, and one empty string in
the list forces the answer to `""`. Also not guaranteed: that `strs[0]` is the
shortest, which is the assumption most broken first attempts smuggle in.

```text
def longestCommonPrefix(self, strs: List[str]) -> str
```

### Examples (mine, not LeetCode's)

| `strs` | Returns | Why |
|---|---|---|
| `["prefix", "pretend", "press"]` | `"pre"` | The ordinary case. Columns 0–2 agree everywhere; column 3 is `f`/`t`/`s` and the scan stops, returning the three columns already cleared. |
| `["abcd", "abc"]` | `"abc"` | **Edge case, and the one that breaks careless code.** The reference `strs[0]` is the *longer* string. At column 3 the second word has no character at all, so the length test — not a character comparison — is what ends the scan. Compare characters without checking bounds first and this is an `IndexError`, not a wrong answer. |
| `["ab", "abc", "ax"]` | `"a"` | **Counterexample to the naive approach.** Folding pairwise and stopping early is tempting: the first two strings share `"ab"`, so a solution that computes the prefix of `strs[0]` and `strs[1]` and returns it answers `"ab"`. Wrong — `"ax"` cuts it to `"a"`. Every string has to be consulted, not a convenient subset. |
| `["dog", "cat"]` | `""` | Disagreement at column 0. `reference[:0]` is `""`, so the empty answer needs no special case — it is what the general return produces when `i` never advances. |
| `["", "anything"]` | `""` | **Edge case:** an empty string in the list. The reference is `""`, `range(0)` is empty, the loop body never runs, and the function returns the reference — `""`. Correct for the right reason, and it also covers `strs = [""]` alone. |
| `["solo"]` | `"solo"` | **Edge case:** one string. The inner loop compares the reference against itself at every column, always matches, and the fall-through returns the whole string. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= strs.length <= 200` | The lower bound is the load-bearing half: the list is **never empty**, which is precisely the licence to write `reference = strs[0]` with no `if not strs: return ""` in front of it. Remove that promise and the first line raises `IndexError`. The upper bound of 200 is small enough that the number of strings contributes essentially nothing to the runtime, and it kills any temptation to be clever about the outer dimension — no divide-and-conquer over the list, no sorting, no trie, all of which are legitimate techniques that this input size makes pure overhead. |
| `0 <= strs[i].length <= 200` | The lower bound of **zero** is the trap: `""` is a legal element, so the answer can be forced to `""` by a single empty string, and any solution that assumes it can index `word[0]` is broken. This code handles it through the same `i >= len(word)` test that handles merely-short words, which is why there is no separate empty-string branch. The upper bound caps the work: with at most 200 strings of at most 200 characters, the total input is ~4×10^4 characters, so the worst case of the vertical scan is ~4×10^4 comparisons — instant. It also means even an aggressively wasteful approach passes, so the bound is not what selects the algorithm here; clarity is. |

*Only two constraints were captured for this problem. From memory — **recalled,
not read**, so treat it as unverified — the statement also restricts the strings
to lowercase English letters. This solution never depends on that: it compares
characters for equality and slices, both of which are alphabet-agnostic, so a
Unicode input would work unchanged.*

## Key insight

The answer is a prefix of `strs[0]`, so there is nothing to *search for* — only
a length to determine. That flips the problem from "find the common prefix" to
"how far can I walk down column 0, column 1, column 2 … before some word
disagrees or runs out". Scanning by column rather than by string is what makes
the first failure the final answer, so you can return the instant you find one.

## Approach

1. Take `reference = strs[0]` as the yardstick. Legal without a guard because
   the list is guaranteed non-empty.
2. Walk the columns `i = 0, 1, 2, …, len(reference) - 1`.
3. For each column, walk **every** word in the list — including the reference
   itself, which trivially matches and is not worth special-casing.
4. A word fails column `i` if it is too short (`i >= len(word)`) or has a
   different character there. **This test's order is load-bearing**: Python's
   `or` short-circuits, so the length check must come first or `word[i]` is
   evaluated on a word that has no index `i`.
5. On the first failure, return `reference[:i]` — the columns *before* the
   failing one. Exclusive slice, not `[:i+1]`.
6. If no column ever fails, the reference is a prefix of everything; return it
   whole.

The outer/inner nesting is the part that matters. Scanning **horizontally**
instead — take a candidate prefix and shrink it string by string — is also
correct, but then no single comparison is final and you must carry state; the
vertical order is what licenses the early return.

### Why it's correct

The **invariant**, stated at the top of the outer loop for column `i`:

> every word in `strs` starts with `reference[:i]`.

It is vacuous at `i = 0` (every string starts with `""`). The inner loop is
exactly the check that extends it: if every word has a character at index `i`
and that character equals `reference[i]`, then every word starts with
`reference[:i+1]`, and the invariant holds for the next iteration. If some word
fails, the invariant still says `reference[:i]` is common to all — so returning
it is returning a genuine common prefix.

That it is the **longest** one takes the other half of the argument, and it is
the half people skip. Suppose a longer common prefix `P` existed, with
`len(P) > i`. `P` is a prefix of every word, and in particular of `reference`,
so `P` and `reference` agree on their first `len(P)` characters — meaning
`P[i] == reference[i]` and every word must have `reference[i]` at index `i`. But
the loop stopped precisely because some word did *not*. Contradiction. So the
first failing column is a hard ceiling, and the early return forfeits nothing.

**Termination** is a bounded `for` over `range(len(reference))` with no mutation
— it ends after at most `len(reference)` columns even if nothing ever fails.
**At the edges**: the slice `reference[:i]` is exclusive on the right, dropping
the column that just failed; `[:i+1]` would include the mismatching character
and is the off-by-one to watch for. At `i = 0` the slice is `""`, which is the
correct answer for words sharing nothing, so the "no common prefix" case needs
no branch. And if the loop completes, `i` reached `len(reference) - 1`
successfully, so every word starts with the whole reference — `return reference`
is the same expression as `return reference[:len(reference)]`, just spelled
without the slice.

The step I would double-check when redoing this cold is the `range` bound: it
runs over the reference's length, not over the shortest word's length or over
`min(len(w) for w in strs)`. Both alternatives are also correct; the reason this
one is safe is that a shorter word triggers `i >= len(word)` before the loop
overruns, so the bound and the length test are covering for each other.

## Solution

```python
# 14. Longest Common Prefix (Easy) - vertical scan, column by column against strs[0]. O(S) time, O(1) extra space.
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:

        # Any common prefix of the whole list is in particular a prefix of
        # strs[0], so strs[0] can serve as the yardstick: the answer is some
        # reference[:i] and the only question is how large i gets. This is safe
        # without a guard because the constraints promise 1 <= strs.length, so
        # there is always a strs[0] to take. It does NOT need to be the shortest
        # string - a short word elsewhere is handled by the i >= len(word) test
        # below rather than by picking a better reference up front.
        reference = strs[0]

        # Scan VERTICALLY: fix a column i, then check that column across every
        # word, before moving to column i + 1. That ordering is what makes the
        # early return correct - by the time column i is examined, columns
        # 0..i-1 have already been confirmed to match in every word, so the
        # moment column i fails, reference[:i] is known to be the full answer
        # and nothing further needs to be looked at.
        for i in range(len(reference)):
            for word in strs:
                # ORDER INSIDE THE `or` IS LOAD-BEARING: `i >= len(word)` must
                # be tested first. Python short-circuits, so a word shorter than
                # the reference bails out here and word[i] is never evaluated.
                # Flip the two operands and this raises IndexError on input like
                # ["abcd", "abc"] at i == 3.
                #
                # Two different failure modes, one exit: the word ran out of
                # characters, or it has a character here and it disagrees.
                # Either way column i is not shared, so the common prefix is
                # exactly the i columns already cleared.
                if i >= len(word) or word[i] != reference[i]:
                    # reference[:i] EXCLUDES index i, which is the column that
                    # just failed. Off-by-one central: [:i+1] would return the
                    # mismatching character too. At i == 0 this is "", the
                    # correct answer for words sharing nothing.
                    return reference[:i]

        # Falling out of the loop means every column of the reference matched in
        # every word, so the reference is itself a prefix of all of them and is
        # the answer entire. This is also the path taken when strs has a single
        # element, and when reference is the empty string (range(0) is empty).
        return reference
```

[solution.py](solution.py) · [raw submission](../../data/raw/longest-common-prefix.py)

## Why this approach

| Alternative | Cost | Why the vertical scan beats it |
|---|---|---|
| Horizontal scan: start with `p = strs[0]`, then for each word shrink `p` until `word.startswith(p)` | O(S) time, O(1) space where S is total input length | Correct and about as fast — the `startswith` loop is C-level, so it often measures *faster* in Python despite doing more character comparisons in the worst case. The reason to prefer the vertical version is that its early exit is provably final after one failure, whereas here every word can still shrink the answer, so there is no point at which you may stop early. A matter of clarity, not of complexity. |
| Take the common prefix of `strs[0]` and `strs[1]` and return it | O(k) time | **Wrong, not slow.** `["ab", "abc", "ax"]` returns `"ab"` instead of `"a"`. Any approach that consults a subset of the list can be defeated by putting the disagreement in a string it never reads. |
| `min(strs)` and `max(strs)`, then common prefix of just those two | O(n·k) time | **Correct, and worth knowing** — under lexicographic order, anything shared by the smallest and largest strings is shared by everything between them. It is a genuinely cute reduction of "all n strings" to "two strings", but it needs a paragraph of justification per line of code, and it is *not* the same as the wrong pairwise idea above, which is exactly why it invites being confused for it under pressure. |
| Sort `strs`, compare first and last | O(n·k log n) time | Same idea as the previous row with a needless sort bolted on. Strictly worse than taking `min` and `max` directly. |
| Build a trie of all strings, walk down while each node has exactly one child and is not a word end | O(S) time, O(S) space | The reason "Trie" is a topic tag, and the right structure if the same list were queried repeatedly. For a single query it allocates a node per character to answer a question a scan answers in place — 4×10^4 nodes to avoid 4×10^4 comparisons. |
| `os.path.commonprefix(strs)` | O(S) time | Actually returns the right answer here (it is a plain character-wise common prefix, despite the module it lives in), but it is a library call standing in for the thing being tested, and its `path` framing makes it look like it might respect `/` boundaries — it does not, which is a trap in the other direction. |

## Complexity

- **Time — O(S)** in the worst case, where `S` is the total number of characters
  across all strings: the outer loop runs at most `len(strs[0])` times and the
  inner loop at most `len(strs)` times, giving `O(len(strs) * len(strs[0]))`,
  bounded by 200 × 200 = 4×10^4 character comparisons. That worst case needs
  every string to share the reference entirely; the moment a disagreement
  appears at column `i`, the actual work is `O(i * len(strs))` and the function
  returns. The 0 ms / 100th-percentile runtime reflects how small this input is
  more than anything about the algorithm.
- **Space — O(1) extra.** Two integers' worth of loop state and a reference to
  an existing string; no new list, dict or trie is built. The one allocation is
  the returned slice, at most 200 characters, which is the answer itself rather
  than working memory.

## Pitfalls

- **Indexing before checking the length.** Writing
  `if word[i] != reference[i] or i >= len(word)` raises `IndexError` on
  `["abcd", "abc"]` at `i == 3`. Both operands look symmetric; they are not,
  because `or` short-circuits left to right.
- **Returning `reference[:i+1]`.** Includes the character that just failed. On
  `["ab", "ax"]` it returns `"ab"` rather than `"a"`. The failing column is
  never part of the answer.
- **Comparing only the first two strings.** `["ab", "abc", "ax"]` → `"ab"`,
  wrong. It passes casual testing because most random test lists put the
  disagreement early.
- **Assuming `strs[0]` is the shortest.** It need not be, and picking a
  "better" reference is unnecessary work: `i >= len(word)` already stops the
  scan at the shortest word's length. If you *do* precompute
  `min(len(w) for w in strs)` as the loop bound, you must still keep or replace
  the length check when the reference is not the shortest string — dropping both
  is how the `IndexError` comes back.
- **Forgetting that `""` is a legal element.** `["", "abc"]` must return `""`.
  Here it works for a slightly sneaky reason — the reference itself is empty, so
  `range(0)` never iterates — and `["abc", ""]` works for the other reason, the
  length test. Both paths are needed; testing only one of them proves nothing.
- **Guarding against an empty list.** `if not strs: return ""` is dead code
  under `1 <= strs.length`. Harmless, but it signals you did not read the
  constraint, and in an interview the follow-up is "what does your code do
  without that guarantee?"
- **Returning `None` for "no common prefix".** The signature is `-> str`. The
  empty string is the answer, and the code produces it naturally as
  `reference[:0]`.

## Redo from scratch

1. Say the reframing out loud: the answer is `strs[0][:i]`, so this is a search
   for one integer, not for a string.
2. `reference = strs[0]` — no emptiness guard; `1 <= strs.length` is promised.
3. `for i in range(len(reference)):` then `for word in strs:` — columns outside,
   words inside. Getting this nesting backwards loses the early return.
4. `if i >= len(word) or word[i] != reference[i]: return reference[:i]` — length
   test first, exclusive slice.
5. `return reference` after the loops, for the case where nothing ever
   disagreed.
6. Check it mentally against `["abcd", "abc"]` (reference is longer),
   `["", "x"]` (empty reference) and `["dog", "cat"]` (immediate failure) before
   submitting.

Be able to justify out loud:

- **Why the first failing column ends the search.** Not just "because it
  failed", but the contradiction: a longer common prefix would have to agree
  with the reference at that column too, and some word demonstrably does not.
- **Why the length test must precede the character comparison.** Short-circuit
  evaluation is the only thing preventing an `IndexError`, and the example that
  triggers it is a list whose first string is the longest.

## Related problems

- [Valid Anagram](../0242-valid-anagram/README.md) — solved. The opposite reduction on strings: this problem cares only about *position* and discards nothing, while that one discards position entirely and keeps only counts. Reading them together is a good reminder that "what can I throw away?" is the first question for any string problem.
- [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) — not solved yet, and not in the similar list. Builds the structure the topic tag is hinting at. Do it after this one to see what changes when the list of words is fixed and the prefix queries are many.
- [Longest Common Prefix After at Most One Removal](https://leetcode.com/problems/longest-common-prefix-after-at-most-one-removal/) — not solved yet. The same column scan with one permitted mismatch, which turns a single index into a small state machine. The natural difficulty step up from here.
- [Find the Length of the Longest Common Prefix](https://leetcode.com/problems/find-the-length-of-the-longest-common-prefix/) — not solved yet. Prefixes across two *arrays* of numbers, all pairs — the input size finally makes the trie mandatory, so it is the problem that justifies the tag on this one.
- [Longest Common Suffix Queries](https://leetcode.com/problems/longest-common-suffix-queries/) — not solved yet. Same machinery read right to left, plus queries. Useful mainly to confirm that "prefix" was never special — reversing the strings reduces one to the other.
- [Smallest Missing Integer Greater Than Sequential Prefix Sum](https://leetcode.com/problems/smallest-missing-integer-greater-than-sequential-prefix-sum/) — not solved yet. Shares only the word "prefix" and none of the ideas; listed by LeetCode as similar, but do not expect it to teach anything about this one.

*Of the related problems above, only Valid Anagram is in this repo so far.*
