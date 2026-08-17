# 49. Group Anagrams

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Hash Table, String, Sorting |
| **Solved** | 2026-08-17 |
| **Runtime** | 7 ms (98.32th percentile) |
| **Memory** | 22.6 MB (38.83th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/group-anagrams/ |

## The problem

**Given** a list of strings `strs`.

**Return** a list of lists: the input strings partitioned into groups, where two
strings land in the same group exactly when they are anagrams of one another —
same characters, same number of each, any order.

Three details that the shape of the answer depends on:

- The groups contain the **original** strings, not their sorted forms. The
  sorting is internal machinery.
- It is a **partition**: every input string appears in exactly one group, and
  no group is empty. Duplicates in the input are duplicated in the output —
  `["ab", "ab"]` is one group of two, not one group of one.
- **Order is free.** The groups may come back in any order, and the strings
  within a group may be in any order. Graders for this problem compare as sets
  of multisets, so a solution should not waste effort imposing an order and
  should not assume one when testing.

**Guaranteed**: the list itself is non-empty (`1 <= strs.length`). **Not**
guaranteed: that the strings are non-empty — `""` is a legal member, and all the
empty strings form one group among themselves.

```text
def groupAnagrams(self, strs: List[str]) -> List[List[str]]
```

### Examples (mine, not LeetCode's)

| `strs` | Returns | Why |
|---|---|---|
| `["stop", "pots", "cat", "tops"]` | `[["stop", "pots", "tops"], ["cat"]]` | The ordinary case. All three of `stop`/`pots`/`tops` sort to `('o','p','s','t')`; `cat` is alone in its class, and a class of one is still a group. |
| `["ab", "ab", "ba"]` | `[["ab", "ab", "ba"]]` | **Duplicates are not deduplicated.** A repeated string is an anagram of itself and joins the same bucket twice. Any solution reaching for a `set` anywhere near the words loses one of these. |
| `["aab", "abb"]` | `[["aab"], ["abb"]]` | **Counterexample to the naive approach.** Both words use exactly the characters `{a, b}`, so keying by `frozenset(word)` — or by `"".join(sorted(set(word)))` — merges them into one group. Wrong: the key must record *how many* of each character, not *which* characters appear. |
| `["", "", "x"]` | `[["", ""], ["x"]]` | **Edge case:** empty strings are legal (`0 <= strs[i].length`). `tuple(sorted(""))` is `()`, a perfectly good hashable key, so they group together with no special case. |
| `["listen"]` | `[["listen"]]` | **Edge case:** a single word. One bucket, one member. Nothing about the code treats a lone word differently. |
| `["abc", "cba", "bca", "cab"]` | `[["abc", "cba", "bca", "cab"]]` | All 4 of the 6 permutations present collapse to one key. The point: group size is bounded by the input, not by anything about the words, so one group may hold every string. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= strs.length <= 10^4` | The lower bound makes an empty input impossible, so the "no groups at all" case never arises — though this code would return `[]` correctly anyway, since an empty loop leaves an empty dict. The upper bound is what kills the obvious solution: comparing every pair of strings to test anagram-hood is `10^4 * 10^4 / 2` = 5×10^7 *pairs*, each costing a sort or a count over up to 100 characters, so on the order of 10^9 character operations — a comfortable TLE in Python. That is the constraint that forces the canonical-key idea: `n` independent O(k log k) key computations plus `n` hash lookups instead of `n^2` comparisons. |
| `0 <= strs[i].length <= 100` | The **zero** is the sharp edge: `""` is a legal string, so the key function must survive being handed one (here `tuple(sorted(""))` is `()`, which is fine) and an approach that indexes `word[0]` to pre-bucket is broken. The upper bound of 100 is why sorting each word is comfortably affordable — `k log k` with `k <= 100` is a few hundred comparisons per word, ~10^6 in total across the whole input. It also explains why the theoretically-better O(k) count-tuple key does not win in practice: building a 26-element tally in Python costs more per word than handing 100 characters to a C-level `sorted`. |

*Only two constraints were captured for this problem. From memory — **recalled,
not read**, so treat it as unverified — the statement also restricts the strings
to lowercase English letters. Nothing in this solution depends on that: sorting
is defined for any comparable characters, so a Unicode input groups correctly
without a change. It matters only for the 26-count-tuple alternative discussed
below, which is the one approach that would break.*

## Key insight

Anagram-hood is an equivalence relation, and every equivalence relation you can
compute has a *canonical form* — a function that maps each element to a single
representative of its class, so that testing equivalence becomes testing
equality. For anagrams the canonical form is free: sort the characters. Once you
see the class as a **key** rather than as a comparison, grouping stops being a
clustering problem and becomes a single pass filling a dictionary.

## Approach

1. Create an empty dict `groups`, mapping canonical form → list of original
   words.
2. For each `word` in `strs`:
3. Compute `key = tuple(sorted(word))` — its canonical form. `sorted` returns a
   list, which is unhashable, so the `tuple` conversion is load-bearing, not
   cosmetic.
4. If the key is new, create an empty bucket for it. This must happen **before**
   the append; that is the one ordering constraint in the whole function, and
   `setdefault` or a `defaultdict` fuse the two steps so it cannot be got wrong.
5. Append the **original** `word` — not the key — to its bucket.
6. Return `list(groups.values())`. The keys have done their job and are thrown
   away.

Each word is handled independently, so the order in which words are processed
does not affect which groups exist. It affects only the order of the output,
which the problem does not constrain.

### Why it's correct

The **invariant**, stated after processing any prefix of `strs`:

> For every key `K` in `groups`, `groups[K]` is exactly the list of words seen
> so far whose sorted form is `K`; and every word seen so far is in exactly one
> bucket.

Each iteration preserves both halves: the word is appended to precisely one
bucket — the one named by its own key, created empty first if absent — and no
other bucket is touched. At the end, the prefix is the whole input, so the
buckets are exactly the classes of the "same sorted form" relation, and every
input word sits in exactly one.

That leaves the step that actually needs an argument, and it is not about the
loop at all: **why is "same sorted form" the same relation as "is an anagram
of"?** Both directions:

- If two words are anagrams, they have identical character multisets. Sorting a
  multiset yields its elements in non-decreasing order, and that sequence is
  determined by the multiset alone — the original arrangement cannot influence
  it. So the sorted forms are equal.
- If the sorted forms are equal, then reading the multiset back off the sorted
  sequence gives the same multiset for both, so each word is a rearrangement of
  the other, i.e. they are anagrams.

Sorting is therefore a *complete invariant*: never merges two different classes
(the second direction) and never splits one class across two keys (the first).
That is exactly the property a canonical form must have, and it is the property
that `frozenset(word)` lacks — sets discard multiplicity, so they merge `"aab"`
with `"abb"`, satisfying only the first direction. A key that is merely
*necessary* rather than *sufficient* produces over-large groups, which is the
failure mode to watch for in any hashing scheme here.

**Termination** is a bounded pass over a list with no early exit and no
mutation of `strs`. There is no numeric range to get an off-by-one in — no
index arithmetic appears anywhere — which is why this is a Medium about seeing
the reduction rather than about executing it. The one boundary worth naming is
the empty word, where `sorted("")` is `[]` and the key is the empty tuple `()`:
a legal, hashable, distinct key, so empty strings group together rather than
crashing or scattering.

## Solution

```python
# 49. Group Anagrams (Medium) - bucket words by their sorted-character canonical form. O(n * k log k) time, O(n * k) space.
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:

        # Maps a canonical form -> the list of original words that reduce to it.
        # A plain dict rather than defaultdict(list) so the missing-key case is
        # handled explicitly a few lines down; see the note there.
        groups = {}

        for word in strs:

            # THE WHOLE ALGORITHM IS THIS LINE. Sorting a word's characters is a
            # canonical form for its anagram class: two words are anagrams
            # exactly when they contain the same characters with the same
            # multiplicities, and sorting maps every arrangement of one multiset
            # to the same sequence. So an O(1) dict lookup replaces the O(n^2)
            # pairwise "is a an anagram of b" comparison.
            #
            # tuple() is NOT decoration. sorted() returns a LIST, and lists are
            # unhashable, so `groups[sorted(word)]` raises TypeError. Any
            # hashable rendering works - "".join(sorted(word)) is the common
            # alternative and produces a string key instead.
            key = tuple(sorted(word))

            # First word of a new anagram class: create its (empty) bucket. This
            # must run BEFORE the append below, which is the only ordering
            # constraint in the function. groups.setdefault(key, []) or a
            # defaultdict(list) collapse these three lines into the append
            # itself; this spelling is longer but shows the branch.
            if key not in groups:
                groups[key] = []

            # Append the ORIGINAL word, never the key. The problem asks for the
            # input strings grouped, not their sorted forms - appending `key`
            # here is a silent wrong answer that still has the right shape.
            groups[key].append(word)

        # The keys were only ever a device for bucketing, so they are discarded.
        # dict preserves insertion order in Python 3.7+, so the groups come back
        # ordered by first appearance and each group is in input order - neither
        # is required by the problem, which accepts any order, but it makes
        # output stable and diffable when testing.
        return list(groups.values())
```

[solution.py](solution.py) · [raw submission](../../data/raw/group-anagrams.py)

## Why this approach

| Alternative | Cost | Why the sorted-tuple key beats it |
|---|---|---|
| `defaultdict(list)`, then `groups[key].append(word)` | Identical complexity | Not an alternative algorithm — the same one, three lines shorter, and it makes the "create before append" ordering impossible to get wrong. `groups.setdefault(key, []).append(word)` does the same with no import. This is the version to write next time; the explicit `if key not in groups` is not wrong, just verbose. |
| Key by a 26-element tuple of character counts instead of by sorting | O(n·k) time, avoiding the `log k` | Asymptotically better, and the answer expected if an interviewer asks "can you drop the sort?" In practice it usually measures *slower* here: building a 26-slot list and incrementing it in interpreted Python beats `sorted`'s C loop only once `k` is large, and `k <= 100`. It also hard-codes the lowercase-English assumption, so a single character outside `a`–`z` either crashes on the index or silently mis-buckets. The 98th-percentile runtime suggests the sort was the right call at this input size. |
| Compare every pair of strings for anagram-hood, union them into groups | O(n^2 · k) time | **The reason the constraint exists.** 5×10^7 pairs at `n = 10^4`, each needing a sort or a count — around 10^9 character operations, a certain TLE. It is also more code, since you then need union-find or a visited array to assemble the groups. |
| Sort `strs` by the sorted-form key, then walk the list emitting a group per run of equal keys | O(n log n · k) time, O(n·k) space | Correct, and it needs no hash map, which matters in a language without one. Strictly worse here: it adds an `n log n` factor to do what a dict does in `n`, and the key must be computed twice or cached anyway. |
| Key by a product of primes (map `a`→2, `b`→3, …, multiply) | O(n·k) time | Sound *in Python*, because integers are arbitrary precision and the factorisation is unique — genuinely a canonical form. But it is slower than sorting (100 big-int multiplications per word), needs a prime table, and overflows silently in any fixed-width-integer language, which makes it a fragile solution wearing a clever costume. |
| Key by `frozenset(word)` | O(n·k) time | **Wrong, not slow.** `"aab"` and `"abb"` share the set `{a, b}` and get merged. Sets record presence and discard multiplicity, which is the exact half of the problem that matters. |
| Key by `sum(ord(c) for c in word)` or any additive hash | O(n·k) time | **Wrong.** `"ad"` and `"bc"` both sum to 197 and would be merged. Any commutative fold into a single number collides; unlike the prime product, addition is not injective on multisets. |

## Complexity

- **Time — O(n · k log k)**, where `n = len(strs)` (≤ 10^4) and `k` is the
  maximum word length (≤ 100). Each word is sorted once — `k log k` comparisons,
  done in C by `sorted` — and then hashed and appended in O(k) amortised
  (hashing a tuple of `k` characters is linear in `k`). With the constraint
  bounds that is at most about 10^4 × 700 ≈ 7×10^6 character comparisons, which
  is why this lands at 7 ms. Note the hashing cost is not negligible relative to
  the sort at these sizes; it is part of why the count-tuple variant, which
  still hashes a 26-tuple, does not gain as much as its asymptotics promise.
- **Space — O(n · k)**. The output alone holds all `n` original strings (as
  references, so the strings are not copied), and the dict holds one key per
  distinct anagram class, each key being a fresh `k`-character tuple. In the
  worst case — every word in its own class — that is a second full copy of the
  input in tuple form, which is heavier per character than the strings were.
  That is the likely reason memory sits at the 39th percentile while runtime is
  at the 98th; keying by `"".join(sorted(word))` instead would store compact
  strings rather than tuples of one-character objects and reclaim some of it.

## Pitfalls

- **`groups[sorted(word)]`** raises `TypeError: unhashable type: 'list'`.
  `sorted` returns a list; the key must be a tuple or a joined string. This is
  the single most common first-attempt failure, and it is a crash rather than a
  wrong answer, which is the good outcome.
- **Appending the key instead of the word.** `groups[key].append(key)` on
  `["eat"]` returns `[[('a','e','t')]]` — right shape, right grouping, wrong
  contents. Easy to miss because the group *structure* is completely correct.
- **Keying by `set` or `frozenset`.** `["aab", "abb"]` comes back as one group
  instead of two. Presence is not multiplicity.
- **Keying by a sum of character codes.** `["ad", "bc"]` comes back as one
  group. Both sum to 197.
- **Appending before ensuring the bucket exists.** Swap the two statements and
  every new key raises `KeyError` on the first word of its class. `setdefault`
  or `defaultdict` removes the possibility.
- **Deduplicating anywhere.** `["ab", "ab"]` must return a group of *two*. A
  `set` of words, or a dict keyed by word, silently drops the repeat.
- **Assuming the output order is checked.** It is not — neither the order of the
  groups nor the order within them. Writing a test with `assertEqual` against a
  hand-written nested list will fail spuriously on a correct solution; compare
  as a set of sorted tuples instead.
- **Forgetting `""` is a legal input.** It works here for a quiet reason —
  `tuple(sorted(""))` is `()`, a valid distinct key — and any rewrite that
  bootstraps a key from `word[0]`, or that treats a falsy key as "no key",
  breaks on it.
- **Reaching for `itertools.groupby` without sorting first.** `groupby` only
  groups *consecutive* equal keys, so on unsorted input it returns many tiny
  groups: `["ab", "cd", "ba"]` yields three groups rather than two. It is the
  right tool only in the sort-then-walk alternative above.

## Redo from scratch

1. Name the reduction out loud: *anagram classes have a canonical form, and the
   canonical form is the sorted characters.* Everything else is bookkeeping.
2. `groups = {}` — or `defaultdict(list)`, which is what to reach for.
3. One loop over `strs`. Per word: `key = tuple(sorted(word))`. Remember the
   `tuple`; a list will not hash.
4. `groups.setdefault(key, []).append(word)` — append the word, never the key.
5. `return list(groups.values())`.
6. Check mentally against `["aab", "abb"]` (must be two groups — this is the
   test that a set-based key fails) and `["ab", "ab"]` (must be one group of
   two).

Be able to justify out loud:

- **Why the sorted form is a *complete* invariant** — both directions: anagrams
  always sort to the same sequence, and equal sorted sequences always mean equal
  multisets, hence anagrams. A key satisfying only the first direction (a set, a
  sum) merges classes that should stay apart, and `"aab"` versus `"abb"` is the
  counterexample to have ready.
- **Why the `tuple` is required and what the alternatives are.** Hashability;
  `"".join(sorted(word))` is the other standard key and uses less memory.
- **When the 26-count key wins.** When `k` is large enough that `log k` matters
  and the alphabet is genuinely known to be small — and why that assumption is a
  cost, not a freebie.

## Related problems

- [Valid Anagram](../0242-valid-anagram/README.md) — solved. The two-string version of exactly this test. That page argues that `Counter` equality is the right way to *compare* two words; this one shows that the same information becomes a hash *key* when there are `n` words instead of 2. Reading them together is the clearest illustration of "a comparison and a canonical form are the same idea used differently".
- [Group Shifted Strings](https://leetcode.com/problems/group-shifted-strings/) — not solved yet. Identical structure with a harder canonical form: the sequence of gaps between consecutive characters, taken mod 26. The best next problem, because the algorithm is already known and the entire difficulty relocates into designing the key.
- [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) — not solved yet, and not in the similar list. Anagram-testing at every window of a string, where recomputing a key per position is too slow and the count table must be maintained incrementally. Teaches the cost of the key computation this problem gets to treat as free.
- [Find Resultant Array After Removing Anagrams](https://leetcode.com/problems/find-resultant-array-after-removing-anagrams/) — not solved yet. The same canonical form applied to adjacent elements only. Little new to learn, but quick confirmation that the primitive is the reusable part.
- [Count Anagrams](https://leetcode.com/problems/count-anagrams/) — not solved yet. Counts the distinct rearrangements of each word — multinomial coefficients with modular inverses. Shares the vocabulary and none of the technique; do not expect it to reinforce anything here.
- [Determine if Two Strings Are Close](https://leetcode.com/problems/determine-if-two-strings-are-close/) — not solved yet, and not in the similar list. A deliberately weakened equivalence where the counts may be permuted among characters. Good for stress-testing the "what exactly does my key preserve?" instinct that this problem installs.

*Of the related problems above, only Valid Anagram is in this repo so far.*
