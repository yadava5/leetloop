# 706. Design HashMap

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table, Linked List, Design, Hash Function |
| **Solved** | 2026-08-17 |
| **Runtime** | 21 ms (92.56th percentile) |
| **Memory** | 23.2 MB (39.72th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/design-hashmap/ |

## The problem

**Design and implement** a map from integer keys to integer values, without
using any built-in hash-map type, supporting three operations:

- `put(key, value)` — insert `(key, value)`. If `key` already exists,
  overwrite its value.
- `get(key)` — return the value mapped to `key`, or `-1` if `key` is not in
  the map.
- `remove(key)` — delete the mapping for `key`, if present. Removing an
  absent key changes nothing.

**Given**: a sequence of calls to these three methods.

**Return**: `get` returns an int (the value, or the sentinel `-1`); `put` and
`remove` return nothing.

**Guaranteed**: `0 <= key, value <= 10^6` — both are non-negative and bounded,
so `-1` can never collide with a real stored value and is safe to use as the
"not found" sentinel.

```text
class MyHashMap:
    def __init__(self)
    def put(self, key: int, value: int) -> None
    def get(self, key: int) -> int
    def remove(self, key: int) -> None
```

### Examples (mine, not LeetCode's)

| Calls | Returns | Why |
|---|---|---|
| `put(1, 100)`, `get(1)` | `100` | The ordinary case. |
| `get(50)` (never put) | `-1` | An absent key returns the sentinel, not an exception. |
| `put(1, 100)`, `put(1, 200)`, `get(1)` | `200` | **Overwrite, not duplicate:** re-putting an existing key replaces its value rather than adding a second entry. A solution that always appends without checking for an existing key would leak stale duplicates and could return the wrong one depending on scan order. |
| `put(1000, 5)`, `put(2000, 9)`, `get(1000)` | `5` | **Counterexample to a naive bucket scheme:** `1000 % 1000 == 0` and `2000 % 1000 == 0` — both keys collide into the *same* bucket. A `get` that assumes one entry per bucket, or indexes the bucket directly instead of scanning it, returns the wrong value here. |
| `put(7, 1)`, `remove(7)`, `get(7)` | `-1` | **Edge case:** after removal the key must behave exactly as if it were never inserted, including returning the sentinel rather than a stale value. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `0 <= key, value <= 10^6` | Non-negative and bounded, on both key and value. The key bound (`10^6`) is what makes a **fixed-size bucket array with `% modulus` hashing** viable without a dynamically resizing table. The value bound guarantees `-1` is never a real value, so it's a safe, unambiguous sentinel for "not found" — no separate present/absent flag is needed. |
| At most `10^4` calls will be made to `put`, `get`, and `remove` | Bounds total work. With `1000` buckets and at most `10^4` keys, each bucket holds at most ~10 entries on average, so a linear scan per bucket (rather than a nested structure per bucket) stays cheap — this is what makes the simple chaining approach fast enough without needing to be clever about bucket count or a smarter hash. |

## Key insight

A hash map is a **fixed array of buckets** plus a function that sends every
key to one bucket, with **chaining** to handle the keys that land in the same
bucket. The key insight is decoupling the *placement* (`key % bucket_count`,
O(1)) from the *disambiguation* (a linear scan within the bucket, checking
the actual key) — the modulus alone cannot tell two colliding keys apart, so
each bucket must store enough to look the real key up again, not just its
value.

## Approach

1. In `__init__`, allocate `self.buckets` as `1000` empty lists — chosen
   because `10^4` calls over `1000` buckets keeps each bucket small on
   average (see constraints above).
2. For every operation, first compute `bucket = self.buckets[key % 1000]` —
   this locates the *candidate* bucket, not the entry itself, since other
   keys may share it.
3. `put(key, value)`: scan `bucket` for an existing `[key, value]` pair with
   a matching key. If found, overwrite its value **in place** and return —
   this must happen *before* falling through to the append, or a repeated
   `put` on the same key would create duplicate entries. If the scan
   finishes with no match, append a new `[key, value]` pair.
4. `get(key)`: scan `bucket` for a matching key; return its value if found,
   else `-1`.
5. `remove(key)`: scan `bucket` for a matching key; if found, remove that
   pair from the bucket and return. If never found, the method simply falls
   off the end — an implicit no-op, matching the requirement that removing
   an absent key changes nothing.

The one load-bearing order is in `put`: the "does this key already exist"
scan must run in full *before* any append, so an update never becomes a
second entry.

## Solution

```python
# 706. Design HashMap (Easy) - chaining hash table: 1000 buckets, each a list of [key, value] pairs, linear scan within a bucket. O(1) expected per operation, O(n) worst case if many keys collide.
class MyHashMap:

    def __init__(self):
        # 1000 buckets. Each key lands in bucket key % 1000, and collisions
        # within a bucket are resolved by chaining - a plain list of pairs.
        self.buckets = [[] for _ in range(1000)]

    def put(self, key: int, value: int) -> None:
        bucket = self.buckets[key % 1000]

        # Scan the bucket for an existing entry with this key so put() can
        # UPDATE in place rather than append a duplicate. Mutating pair[1]
        # directly (rather than rebuilding the pair) keeps this an O(1)
        # in-place update once the matching entry is found.
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        # No existing entry for this key: append a new [key, value] pair.
        bucket.append([key, value])

    def get(self, key: int) -> int:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        # Key was never put(), or was removed: the problem defines this as -1.
        return -1

    def remove(self, key: int) -> None:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                bucket.remove(pair)
                return


# Your MyHashMap object will be instantiated and called as such:
# obj = MyHashMap()
# obj.put(key,value)
# param_2 = obj.get(key)
# obj.remove(key)
```

[solution.py](solution.py) · [raw submission](../../data/raw/design-hashmap.py)

### Why it's correct

**Invariant:** at any point, for every key `k` ever `put` and not
subsequently `remove`d, `self.buckets[k % 1000]` contains exactly one pair
whose first element is `k`, and its second element is the value from the
most recent `put(k, ...)` call.

`put` maintains it: if a pair for `k` already exists in the bucket, it is
updated in place (no new pair created, so still exactly one); if not, one new
pair is appended (going from zero to exactly one). `remove` maintains it by
deleting the one pair for `k`, if present, restoring "zero pairs for `k`"
which is exactly the invariant's statement about a removed or never-inserted
key. `get` only reads, so it cannot break the invariant, and by the
invariant its scan finds at most one matching pair — the correct one — or
none, correctly returning `-1`.

**Termination**: every scan is a bounded `for pair in bucket` with no
recursion and no unbounded growth risk — the loop exits either by an early
`return`/`remove` (found the key) or by exhausting the bucket (key absent),
and both are reached in finitely many steps since a bucket is a finite list.
There's no numeric range or index arithmetic here to get an off-by-one in;
the only edge is an **empty bucket**, where the `for` loop body never
executes and each method falls through to its "not found" behavior (`get`
returns `-1`, `remove` and the append-branch of `put` do nothing extra) —
which is exactly correct with no special-casing required.

## Why this approach

| Alternative | Cost | Why this beats it here |
|---|---|---|
| Python `dict()` (disqualified by the problem) | O(1) expected per op | The problem explicitly forbids the built-in map type — that's the exercise. |
| Direct addressing: an array of size `10^6 + 1`, storing the value (or a "missing" sentinel) at index `key` | O(1) worst case, no scanning ever | Would work here too, since the key bound (`10^6`) is small enough, mirroring [Design HashSet](../0705-design-hashset/README.md). It trades this solution's smaller, collision-handling table for a much larger, collision-free one — and it does not generalize if the key space grew beyond what fits in memory, whereas bucket-and-chain does. |
| More buckets (e.g. `10^6`) to reduce collisions further | Still O(1) expected, larger constant memory | Diminishing returns: with only `10^4` calls total, `1000` buckets already keeps expected bucket size under 10, so a much larger table mostly just spends memory without meaningfully cutting scan length. |
| Fewer buckets (e.g. 10) | O(n) per operation in the worst case | Every key funnels into one of 10 buckets, so with `10^4` puts the average bucket holds ~1000 entries — each `get`/`put`/`remove` degrades toward a linear scan of a near-full list, defeating the point of hashing. |
| A separate `dict` mapping bucket index → sub-dict keyed by `key` (nested hashing) | O(1) expected per op | Functionally similar performance to this solution but doesn't hand-implement collision handling — it just pushes the disallowed built-in one level down. This solution's flat list-of-pairs per bucket is the more honest "build it yourself" version. |

## Complexity

- **Time — O(1) expected per operation**, since each bucket holds
  `O(n / 1000)` entries on average for `n` total keys (at most `10^4` here,
  so a handful per bucket), and every operation does one modulus plus a
  linear scan of one bucket. **Worst case O(n)** per operation if many keys
  happen to collide into the same bucket (e.g. many keys that are multiples
  of 1000 apart), since the scan is linear in bucket size with no fallback
  structure inside a bucket.
- **Space — O(n)**, where `n` is the number of currently-stored keys — each
  `put` of a new key adds one `[key, value]` pair to exactly one bucket, plus
  the fixed O(1000) overhead for the empty bucket array itself.

## Pitfalls

- **Forgetting the "update, not duplicate" check in `put`.** Skipping the
  scan-for-existing-key and always appending means `put(1, 5)` followed by
  `put(1, 9)` leaves *two* pairs for key `1` in the bucket — `get(1)` then
  returns whichever pair the scan reaches first, which happens to be the
  first one inserted (`5`, the stale value) rather than the intended `9`.
- **Modulus collisions across different keys.** `put(1000, 5)` and
  `put(2000, 9)` land in the same bucket (`0`) because `1000 % 1000 ==
  2000 % 1000 == 0`. Any implementation that stores only a value per bucket
  index — instead of `[key, value]` pairs and a scan — silently overwrites
  one key's value with the other's. This solution's per-pair key check is
  exactly what avoids that.
- **`bucket.remove(pair)` relies on `pair` being the literal object found by
  the loop**, which is why `remove` re-uses the same `pair` variable from
  the `for` loop rather than reconstructing `[key, ...]` — list `.remove()`
  deletes by equality, and reconstructing a *new* list literal with a
  wrong/stale value could remove the wrong equal-looking entry if duplicate
  `[key, value]` pairs ever existed (they shouldn't, given the invariant,
  but this is the reason to lean on the loop's own reference rather than
  rebuild one).

## Redo from scratch

1. Pick a bucket count (1000 is a reasonable default at these constraints)
   and allocate that many empty lists.
2. `put`: hash to a bucket with `key % bucket_count`, scan for an existing
   pair with that key, update in place if found, else append a new pair.
   Remember the "check first" ordering — it's what prevents duplicates.
3. `get`: hash to the same bucket, scan for the key, return its value or
   `-1`.
4. `remove`: hash to the same bucket, scan for the key, remove that pair if
   found; a miss is silently fine.
5. Stress-test mentally on two keys that collide (`1000` and `2000` with
   `% 1000`) — confirm `put` on one doesn't clobber the other's value, and
   `get` on each returns its own value.

Be able to justify out loud: why storing `[key, value]` pairs per bucket
(rather than just values) is required — because the modulus is many-to-one,
so the bucket alone can't tell which key a given slot's value belongs to.

## Related problems

- [Design HashSet](../0705-design-hashset/README.md) — solved. The
  presence-only version, which gets to skip chaining entirely because the
  key space (`10^6`) fits in a flat boolean array — reading it alongside
  this one shows when direct addressing suffices and when real hashing with
  buckets is required (here, because values — not just presence — must be
  stored and retrieved).
- [Design Skiplist](https://leetcode.com/problems/design-skiplist/) — not
  solved yet. A different from-scratch data structure exercise — ordered
  rather than hashed, so it teaches probabilistic balancing instead of
  collision resolution, with none of this problem's bucket/modulus
  machinery.
