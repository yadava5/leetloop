# 705. Design HashSet

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Array, Hash Table, Linked List, Design, Hash Function |
| **Solved** | 2026-08-17 |
| **Runtime** | 47 ms (47.31th percentile) |
| **Memory** | 46.1 MB (11.94th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/design-hashset/ |

## The problem

**Design and implement** a set of non-negative integers, without using any
built-in hash-set type, supporting three operations:

- `add(key)` — insert `key` into the set. Inserting a key already present
  changes nothing.
- `remove(key)` — delete `key` from the set, if present. Removing a key that
  isn't there changes nothing.
- `contains(key)` — return whether `key` is currently in the set.

**Given**: a sequence of calls to these three methods, each with an integer
`key`.

**Return**: for `contains`, a boolean; `add` and `remove` return nothing (they
mutate the set).

**Guaranteed**: `key` is always a non-negative integer, `0 <= key <= 10^6`.
No negative keys, no other types.

```text
class MyHashSet:
    def __init__(self)
    def add(self, key: int) -> None
    def remove(self, key: int) -> None
    def contains(self, key: int) -> bool
```

### Examples (mine, not LeetCode's)

| Calls | Returns | Why |
|---|---|---|
| `add(3)`, `contains(3)` | `True` | The ordinary case — insert, then look it up. |
| `contains(9)` (never added) | `False` | A key that was never inserted is absent from the start; nothing needs to be initialized to "present" first. |
| `add(5)`, `add(5)`, `remove(5)`, `contains(5)` | `False` | **Idempotence:** adding the same key twice must not require removing it twice. One `remove` fully deletes it regardless of how many times `add` ran. |
| `remove(2)` (never added), then `contains(2)` | `False` | **Edge case:** removing an absent key must not raise or corrupt state — it's simply a no-op. |
| `add(0)`, `contains(0)` | `True` | **Edge case:** `key = 0`, the low end of the allowed range — a solution that treats `0` as falsy (e.g. skips storing it, or table-checks `if key:`) would break here. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `0 <= key <= 10^6` | Non-negative and bounded above by exactly a million. That upper bound is what makes **direct addressing** viable at all: a flat array of `10^6 + 1` booleans is under 8 MB even at one byte per slot, so the whole key space can be materialized instead of hashed into a smaller table. A key space of, say, `10^18` would rule this out entirely and force real hashing with buckets. |
| At most `10^4` calls will be made to `add`, `remove`, and `contains` | Caps total work regardless of per-call cost — even an O(key range) per-call approach would be disqualified by this bound, but every call here is O(1), so `10^4` calls finishes near-instantly either way. This bound mainly rules out *initialization* cost per call, not per-call logic. |

## Key insight

The key space (`0` to `10^6`) is small enough to allocate directly: instead
of hashing `key` down into a smaller table and handling collisions, just make
an array with one slot **per possible key value** and use the key itself as
the index. Presence becomes `array[key]`. This sidesteps hashing and
collision-handling entirely — it's the special case where the "hash table"
degenerates into direct addressing.

## Approach

1. In `__init__`, allocate `self.set` as a list of `1000001` booleans, all
   `False` — one slot for every key from `0` through `10^6` inclusive.
2. `add(key)` sets `self.set[key] = True`.
3. `remove(key)` sets `self.set[key] = False` — indistinguishable from "never
   added", which is exactly the desired post-condition.
4. `contains(key)` returns `self.set[key]` directly.

There is no ordering constraint between operations beyond the obvious: a
`contains` reflects whatever the most recent `add`/`remove` on that key set
it to, and unrelated keys never interact.

## Solution

```python
# 705. Design HashSet (Easy) - direct-address table: a boolean array indexed by the key itself. O(1) time per operation, O(max key) space.
class MyHashSet:

    def __init__(self):
       # A boolean flag PER POSSIBLE KEY, not a hash table in the usual sense -
       # this is direct addressing. Sized to 1,000,001 to cover every key up
       # to the stated upper bound of 10^6 inclusive (indices 0..10^6).
       self.set = 1000001 * [False]

    def add(self, key: int) -> None:
        self.set[key] = True

    def remove(self, key: int) -> None:
        self.set[key] = False

    def contains(self, key: int) -> bool:
        return self.set[key]


# Your MyHashSet object will be instantiated and called as such:
# obj = MyHashSet()
# obj.add(key)
# obj.remove(key)
# param_3 = obj.contains(key)
```

[solution.py](solution.py) · [raw submission](../../data/raw/design-hashset.py)

## Why this approach

| Alternative | Cost | Why direct addressing beats it here |
|---|---|---|
| Python `set()` (disqualified by the problem) | O(1) expected per op | The problem explicitly forbids using a built-in hash set — that's the entire point of the exercise. |
| A smaller table with real hashing and chaining (as in [Design HashMap](../0706-design-hashmap/README.md)) | O(1) expected, O(bucket size) worst case | More general — it would still work if the key space were much larger than the memory budget — but it's strictly more code (a hash function, a bucket list, a linear scan per op) for no benefit here, since `10^6` slots comfortably fits in memory. Worth reaching for the moment the key space stops being small and dense. |
| A Python `dict` keyed by `key`, storing presence | O(1) expected per op | Would also work and use less memory when the set is sparse (few keys actually inserted out of the million possible) — a dict only stores what's present. The array trades that memory efficiency for guaranteed O(1) worst case with zero hashing overhead, and simplicity. |
| Sorted array + binary search per operation | O(log n) `contains`, O(n) `add`/`remove` (shifting) | Strictly worse on every operation here; sorting only pays off when the ordering itself is needed (e.g. range queries), which this problem never asks for. |

## Complexity

- **Time — O(1) per operation.** Every method is a single array index, a
  single write, or a single read — no loop, no scan.
- **Space — O(M)**, where `M = 10^6` is the maximum possible key. The array
  is allocated once, in `__init__`, sized to the full key range regardless
  of how many keys are ever actually inserted — this is the memory cost of
  trading generality for guaranteed O(1) access.

## Pitfalls

- **Off-by-one on the array size.** `1000000 * [False]` (without the `+ 1`)
  has valid indices `0` through `999999` and raises `IndexError` on
  `add(1000000)`, which is a legal key per `key <= 10^6`. The `1000001`
  size in this solution is exactly the `+ 1` that covers it.
- **Treating `key = 0` as falsy.** A rewrite that does `if not self.set[key]:`
  to mean "absent" is fine, but a rewrite that does `if key:` to guard some
  shortcut would silently break every operation on key `0`, since `0` is
  falsy in Python. Nothing in this solution does that, but it's the trap a
  "helpful" refactor could introduce.
- **This solution does not scale key spaces beyond `10^6`.** It is a
  direct-address table sized to the stated constraint, not a general hash
  set — if the constraint changed to allow `key` up to `10^18`, this exact
  approach would try to allocate an impossibly large array and crash on
  `__init__` before a single operation ran.

## Redo from scratch

1. Recognize the constraint `0 <= key <= 10^6` as the signal: the key space
   is small and dense enough to allocate directly, no hashing needed.
2. `self.set = [False] * 1000001` in `__init__` — remember the `+ 1` for the
   inclusive upper bound.
3. `add`: `self.set[key] = True`. `remove`: `self.set[key] = False`.
   `contains`: `return self.set[key]`.
4. Sanity check: `add(0)` then `contains(0)` must be `True` — confirms `0` is
   handled like any other key, not specially.

Be able to justify out loud: why this is called direct addressing rather than
hashing (the key *is* the index, no hash function involved), and what
specifically about the constraint (`10^6`, not `10^18`) makes it viable —
and what you'd switch to if it weren't (bucketed chaining, as in Design
HashMap).

## Related problems

- [Design HashMap](../0706-design-hashmap/README.md) — solved. The
  key-value version of this exact idea, and it can't use direct addressing
  the same way because values aren't booleans — that page uses real
  chaining with a smaller table instead, which is the technique to reach
  for once direct addressing stops being an option.
- [Design Skiplist](https://leetcode.com/problems/design-skiplist/) — not
  solved yet. A completely different data structure for a similar
  "implement it yourself" exercise — ordered rather than hashed, and
  supports duplicates, which neither hash-based design here does.
