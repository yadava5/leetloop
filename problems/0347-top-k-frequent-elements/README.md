# 347. Top K Frequent Elements

| | |
|---|---|
| **Difficulty** | Medium |
| **Topics** | Array, Hash Table, Divide and Conquer, Sorting, Heap (Priority Queue), Bucket Sort, Counting, Quickselect |
| **Solved** | 2026-08-18 |
| **Runtime** | 0 ms (100th percentile) |
| **Memory** | 22.7 MB (80.83th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/top-k-frequent-elements/ |

## The problem

**Given** an integer array `nums` and an integer `k`.

**Return** the `k` **values** that occur most often in `nums` — the values
themselves, not their counts and not their indices. The returned list may be
in any order.

**Guaranteed**: `k` is at least `1` and never exceeds the number of distinct
values in `nums`, so the answer always has exactly `k` elements. And **the
answer is unique** — there is no tie at the `k`-th position that would make
two different outputs equally valid. That second guarantee is what lets an
arbitrary tie-break be correct rather than merely lucky.

```text
def topKFrequent(self, nums, k)
```

Note this signature carries no type hints, unlike most solutions in this repo —
it is LeetCode's older stub for this problem, kept verbatim.

### Examples (mine, not LeetCode's)

| `nums`, `k` | Returns | Why |
|---|---|---|
| `[9, 9, 4, 4, 4, 7]`, `k = 2` | `[4, 9]` | The ordinary case. Counts are `{9: 2, 4: 3, 7: 1}`; sorted descending by count gives `[4, 9, 7]`; the first two are the answer. |
| `[5]`, `k = 1` | `[5]` | **Edge case:** one element, one distinct value. `k` cannot exceed the distinct count, so `k = 1` is the only legal query. |
| `[8, 8, 8]`, `k = 1` | `[8]` | All identical. The frequency map has a single key — the sort has nothing to order, and the slice takes the only entry. |
| `[1, 1, 2, 2, 3]`, `k = 2` | `[1, 2]` | **The case that shows what the uniqueness guarantee is doing.** `1` and `2` both occur twice, so this input actually *violates* the guarantee if `k` were such that the cut fell between them — here it does not, because both are taken. Worth holding onto: the guarantee is about the boundary at position `k`, not about ties in general. |
| `[6, 6, 6, 1, 1, 9]`, `k = 2` | `[6, 1]` | **Counterexample to sorting `nums` itself rather than the distinct keys.** Sorting the six-element array by frequency would produce `[6, 6, 6, 1, 1, 9]` and slicing two gives `[6, 6]` — duplicated values, not distinct ones. The thing being sorted must be the *keys* of the frequency map. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= nums.length <= 10^5` | 100,000 elements. Counting is one linear pass and unavoidable. The size matters most for what comes *after* counting: if the array were all-distinct, there would be 10⁵ keys to order, and an O(m²) selection (repeatedly scanning for the next-largest count) would be 10¹⁰ operations — hopelessly slow. It also means the array is never empty, so the frequency map always has at least one key. |
| `-10^4 <= nums[i] <= 10^4` | Only **20,001 distinct values are possible**, so `m <= 20001` no matter how long the array gets. This is a genuinely useful bound: it caps the sort at 20,001 items regardless of `n`, which is why the `O(m log m)` approach below is comfortably fast here even though it is not the asymptotically best answer. It would also permit a direct 20,001-slot counting array in place of the dict. Negative values are ordinary keys — nothing here assumes non-negativity. |
| `k is in the range [1, the number of unique elements in the array].` | **Why `result[:k]` needs no guard.** `k` never exceeds `m`, so the slice always yields exactly `k` elements and can never short-return. (A Python slice would silently return fewer rather than raise, so without this guarantee the bug would be invisible.) `k >= 1` means an empty answer is never correct. |
| `It is guaranteed that the answer is unique.` | **The line that makes an arbitrary tie-break safe.** Sorting by count alone leaves elements with equal counts in an unspecified relative order — here, whatever Python's stable sort preserves from dict insertion order. If two values tied at the `k`-th position, the choice between them would be arbitrary and could disagree with the expected output. This guarantee says that situation never arises, so no secondary sort key is needed. |

## Key insight

Two separate problems wearing one coat. First, **collapse `n` elements into
`m` distinct values with counts** — one pass, unavoidable. After that, `nums`
is irrelevant and the problem is just "pick the `k` largest from `m` items,"
which is a pure selection problem on a much smaller collection. Every
difference between the solutions to this problem is a different answer to that
second half.

## Approach

1. Build `freq`, a dict from value to occurrence count, in one pass over
   `nums`. `freq.get(num, 0) + 1` supplies the default on first sight, so no
   membership branch is needed.
2. Sort the dict's **keys** by their counts, descending:
   `sorted(freq, key=freq.get, reverse=True)`. Iterating a dict yields keys,
   so this orders the `m` distinct values, not the `n` array elements.
3. Slice the first `k`.

Step 2 is where the whole cost sits, and where the alternatives diverge. Note
also that `key=freq.get` passes the bound method itself — Python calls it once
per key. Writing `key=lambda x: freq[x]` is equivalent and slightly slower.

### Why it's correct

**Invariant** for the counting pass: after processing the first `i` elements,
`freq` maps each value seen so far to exactly its number of occurrences among
those `i`. It holds at the start (empty dict, zero elements) and each step
either creates a key at `1` or increments an existing one by `1`, which is
precisely the change to the true count caused by seeing one more copy. At the
end, `freq` is the exact frequency table of the whole array.

For the selection step, the correctness claim is just the definition of
sorting: `sorted(..., key=freq.get, reverse=True)` produces a permutation of
the keys in which `freq[result[i]] >= freq[result[j]]` whenever `i < j`. So
every element of `result[:k]` has a count greater than or equal to every
element outside it, which is exactly the definition of "the `k` most
frequent."

**Where the argument is not airtight, and why it still holds**: that
`>=` allows ties straddling the cut — an element at index `k - 1` and one at
index `k` could have equal counts, in which case *both* slices would satisfy
"the k most frequent" and the function's output would be one arbitrary choice.
The uniqueness guarantee in the constraints is the only thing ruling that out.
This is worth stating plainly because the code contains nothing that handles
it; correctness here is imported from the problem statement, not established
by the algorithm.

**Termination and the edge of the range**: both the counting loop and the sort
are over finite collections, so termination is trivial — there is no `while`
and no index arithmetic anywhere in this solution, which is a large part of
why it is hard to get wrong. The one bound worth checking is the slice
`result[:k]`, which takes indices `0` through `k - 1`. Since `k <= m` by
constraint, the slice is fully populated. Python's slicing would clamp rather
than raise if `k` exceeded `m`, so this is a place where the constraint is
doing real work silently.

## Solution

```python
# 347. Top K Frequent Elements (Medium) - count into a dict, sort the DISTINCT keys by count descending, slice the first k. O(m log m) time, O(m) space, m = distinct values.
class Solution:
    def topKFrequent(self, nums, k):
        # Step 1: Count frequencies
        # freq maps value -> occurrence count. dict.get(num, 0) supplies the
        # default on first sight, so there is no separate "not in freq" branch.
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1   # easy way to count

        # Step 2: Sort keys by frequency (descending)
        # Iterating a dict yields its KEYS, so sorted() here sorts the m
        # distinct values, not the n input elements - that is why this is
        # O(m log m) and not O(n log n), and why it is fast when the array is
        # long but repetitive.
        #
        # key=freq.get passes each key back through the dict to fetch its
        # count. Python's sort is stable, so equal counts keep first-seen
        # order; that arbitrary tie-break is only safe because the problem
        # guarantees the answer is unique (see Pitfalls).
        result = sorted(freq, key=freq.get, reverse=True)

        # Step 3: Return top k
        # k is guaranteed to be at most the number of distinct values, so this
        # slice always yields exactly k elements and never short-returns.
        return result[:k]

                
```

[solution.py](solution.py) · [raw submission](../../data/raw/top-k-frequent-elements.py)

## Why this approach

| Alternative | Cost | Why this one is (or is not) better |
|---|---|---|
| **Bucket sort**: an array `buckets` of size `n + 1` where `buckets[c]` lists the values occurring `c` times; walk it from the back collecting until `k` are gathered | **O(n) time**, O(n) space | **The asymptotically best answer, and the one this solution loses to.** A count can never exceed `n`, so counts can index an array directly — no comparisons needed at all. This solution's `O(m log m)` is beaten here. It passes comfortably because `m <= 20001` caps the sort, but if asked "can you do better than sorting?", bucket sort is the expected reply. |
| `heapq.nlargest(k, freq, key=freq.get)` | O(m log k) time, O(k) space | Better than a full sort whenever `k` is much smaller than `m`, because the heap only ever holds `k` items. Also the shortest correct line of Python available. Strictly preferable to this solution for large `m` with small `k`; the gap is `log k` versus `log m`. |
| `collections.Counter(nums).most_common(k)` | O(m log k) time | The idiomatic answer — internally it uses exactly the `nlargest` heap above. Returns `(value, count)` pairs, so it needs unpacking. In real code this is what to write; the hand-rolled dict here shows the machinery `Counter` hides. |
| **Quickselect** on the (value, count) pairs, partitioning around a pivot count until the `k`-th boundary is in place | **O(m) average**, O(m²) worst case, O(m) space | Linear on average without bucket sort's auxiliary array, and the classic interview follow-up. Loses on worst-case time and on how easy it is to get the partition boundaries wrong under pressure. |
| Sort `nums` itself by frequency, then slice | O(n log n) time | **Wrong**, not merely slow: it returns duplicated values. On `[6, 6, 6, 1, 1, 9]` with `k = 2` it yields `[6, 6]`. The slice must be taken over distinct keys, which is the single most important thing the line `sorted(freq, ...)` gets right by iterating the dict. |
| For each of `k` rounds, scan all `m` counts for the current maximum and remove it | O(k · m) time | Fine when `k` is tiny, but degrades to O(m²) as `k` approaches `m` — with `m` up to 20,001 that is 4 × 10⁸ operations. No reason to prefer it over a heap. |

## Complexity

- **Time — O(n + m log m)**, where `n = len(nums)` and `m` is the number of
  distinct values. The counting pass is O(n) with O(1) dict operations per
  element. The sort is O(m log m) comparisons, each of which calls `freq.get`
  — note Python's `sorted` computes the key **once per element** up front
  (a Schwartzian transform), not once per comparison, so that is `m` lookups
  total, not `m log m`. The final slice is O(k). Since `m <= n`, this is never
  worse than O(n log n), and it is much better than that on repetitive input.
- **Space — O(m)**. The dict holds one entry per distinct value, and `sorted`
  builds a new list of the same `m` keys. The `result[:k]` slice adds another
  `k`. Bounded by 20,001 entries here regardless of `n`, thanks to the value
  range.

## Pitfalls

- **Sorting the array instead of the keys.** `sorted(nums, key=...)` returns
  `n` elements with duplicates; `sorted(freq, key=...)` returns `m` distinct
  keys. On `[6, 6, 6, 1, 1, 9]` with `k = 2` the first gives `[6, 6]` and the
  second gives `[6, 1]`. The two lines differ by three characters.
- **Returning counts instead of values.** `sorted(freq.values(), ...)` returns
  `[3, 2, 1]` — the frequencies themselves. The problem wants the values that
  *have* those frequencies. Easy to do when reaching for `.items()` and then
  indexing the wrong half of the tuple.
- **Forgetting `reverse=True`.** Silently returns the `k` **least** frequent
  elements. Every test with a symmetric-looking distribution still produces a
  plausible-looking list, so this can survive casual checking.
- **`key=freq.get` versus `key=freq`.** The first is a callable that Python
  invokes per key; the second is a dict, which is not callable and raises
  `TypeError: 'dict' object is not callable`. Fast to diagnose, easy to
  mistype.
- **Relying on the tie-break.** Equal counts come out in dict insertion order
  because Python's sort is stable — this is *arbitrary*, not meaningful. It is
  only safe here because the problem guarantees a unique answer. If you reuse
  this where ties are possible and a deterministic order matters, add an
  explicit secondary key, e.g. `key=lambda x: (-freq[x], x)` (and drop
  `reverse=True`, since the negation already inverts the count ordering — a
  place where combining `reverse=True` with a negated key silently reverses
  the tie-break too).
- **Assuming this is O(n).** It is not; it is O(n + m log m). If an interviewer
  asks for linear, the answer is bucket sort, and the reason bucket sort is
  available at all is that counts are bounded by `n` and therefore usable as
  array indices.

## Redo from scratch

1. Split the problem in two out loud: **count**, then **select the top `k`**.
   Everything interesting is in the second half.
2. Count with a dict: `freq[num] = freq.get(num, 0) + 1`.
3. Select. Simplest correct version: `sorted(freq, key=freq.get,
   reverse=True)[:k]`. Say "sorted over the **keys**" deliberately — that is
   the one place this goes wrong.
4. Know the two upgrades and when each applies: `heapq.nlargest(k, freq,
   key=freq.get)` for O(m log k) when `k << m`, and **bucket sort** for true
   O(n) when asked to beat sorting entirely.
5. Sketch the bucket version too, since it is the expected follow-up: allocate
   `n + 1` empty lists, put each value into `buckets[count]`, then walk from
   index `n` down to `1` collecting values until you have `k`.
6. Check `[6, 6, 6, 1, 1, 9]` with `k = 2` — the input that exposes sorting the
   array instead of the keys.

Be able to justify out loud: why the complexity is in terms of `m` (distinct
values) rather than `n`, and why counts can be used as array indices in the
bucket-sort version — the fact that no count can exceed `n` is what makes that
legal.

## Related problems

- [Majority Element](../0169-majority-element/README.md) — already solved. The
  extreme special case: `k = 1` *and* the winner guaranteed to hold more than
  half the array. That much stronger guarantee collapses the problem to O(1)
  space with no counting at all, which is the clearest illustration of how
  much a frequency map is actually buying you here.
- [Group Anagrams](../0049-group-anagrams/README.md) — already solved. The
  same dict-as-accumulator reflex, keyed by a canonical form instead of by
  value. If the counting pass here felt automatic, that is why.
- [Valid Anagram](../0242-valid-anagram/README.md) — already solved. Frequency
  counting used for comparison rather than ranking — the same table, a
  different question asked of it.
- [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/)
  — not solved yet. Selection without the counting step, and the canonical
  home of quickselect. The natural place to learn the partition properly,
  since it is the same selection half of this problem with the frequency map
  stripped away.
- [Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/)
  — not solved yet. This problem plus a **required** tie-break (lexicographic
  among equal counts), which removes the uniqueness guarantee that the code
  above quietly leans on. The best possible follow-up for exactly that reason.
- [Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/)
  — not solved yet. Same count-then-order pipeline, but it returns all of them
  rather than the top `k`, so bucket sort applies even more directly.
- [K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/)
  — not solved yet. Identical selection skeleton with distance in place of
  frequency — good confirmation that "top k by some computed key" is one
  pattern, not several.
