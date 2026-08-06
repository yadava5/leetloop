<!-- GENERATED. Problem restated in my own words; never LeetCode's text. -->

# 20. Valid Parentheses

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | String, Stack, Bracket Sequences |
| **Solved** | 2026-08-05 |
| **Runtime** | 4 ms — beats 12.4% |
| **Memory** | 19.4 MB — beats 24.0% |
| **Language** | Python3 |
| **Problem** | <https://leetcode.com/problems/valid-parentheses/> |

## Problem, restated

Given a string made only of the six bracket characters `(){}[]`, decide whether
it is well-formed: every closing bracket must close the **most recent** bracket
still open, must be the same type as it, and nothing may be left open at the end.

**Constraints that actually matter.** The string is 1 to 10⁴ characters, and the
alphabet is *only* those six characters — no letters or digits to defend
against, which is why "not a closer" can safely be treated as "is an opener".
Nesting can be 10⁴ deep, so a recursive formulation would flirt with Python's
default recursion limit; an explicit stack has no such ceiling.

## Key insight

"Must match the **most recent** unclosed bracket" is the definition of a stack —
last in, first out. Once you see that sentence as a stack, the problem is
mechanical.

The corollary matters just as much: **counting cannot work.** `([)]` has one of
each bracket, perfectly balanced by count, and is invalid. Any solution that
only tracks how many of each type are open is wrong, not just imprecise.

## Approach

1. `stack` holds openers that are still waiting to be closed.
2. `map` sends each **closer** to the opener it requires. Keying by the closer is
   a small trick: `char in map` doubles as "is this a closing bracket?".
3. Walk the string one character at a time.
   - **Closer:** pop the top of the stack — or use the sentinel `"#"` if the
     stack is empty — and compare it against `map[char]`. Mismatch → `False`
     immediately.
   - **Opener:** push it.
4. After the loop, `return not stack`. Empty stack means everything that was
   opened got closed.

The `"#"` sentinel is the neat part: it collapses "there is nothing to match
against" into the same comparison as "the wrong thing is there", so there's no
separate empty-stack branch and no `IndexError`.

*(Kept exactly as submitted, including the local name `map` — see Pitfalls.)*

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Three counters, one per bracket type | O(n) time, O(1) space | **Wrong**, not just slower: it accepts `([)]`. Counters lose the ordering, and ordering is the entire problem. |
| Repeatedly delete `"()"`, `"[]"`, `"{}"` substrings until the string stops shrinking | O(n²) time | Correct but quadratic — each pass rescans the string. At n = 10⁴ that's up to 10⁸ character operations for something one pass can do. |
| Recursive descent | O(n) time, O(n) stack | Equivalent in spirit, but 10⁴-deep nesting risks `RecursionError` at Python's default limit of 1000. The explicit stack is the same algorithm without the ceiling. |

## Complexity

- **Time — O(n).** Each character is pushed at most once and popped at most
  once, and every comparison is O(1).
- **Space — O(n).** Worst case is a string of all openers, `"(((((..."`, where
  the stack grows to the full length of the input.

## Pitfalls

- **Forgetting the final `return not stack`.** `"((("` never triggers a mismatch
  because the loop only compares on closers, so a bare `return True` at the end
  wrongly accepts it. This is the single most common wrong answer here.
- **Popping an empty stack.** `")"` on its own would raise `IndexError` without
  the `"#"` sentinel (or an explicit emptiness check).
- **Counting instead of ordering.** See above — `([)]` is the counterexample to
  keep in your pocket.
- **`map` shadows the builtin.** Inside this method `map` is a dict, so the
  builtin `map()` is unavailable for the rest of the function. Harmless here and
  the code is preserved as submitted, but `pairs` or `closer_to_opener` is a
  better habit — shadowing builtins gets genuinely confusing in longer functions.
- **Treating "not a closer" as "an opener"** is only safe because the
  constraints guarantee the six-character alphabet. If arbitrary characters were
  allowed, the `else` branch would need to check membership explicitly.

## Redo from scratch

Rebuild it cold, without reading the code:

1. `stack = []`.
2. Dict mapping **closer → opener** (not the other way round).
3. For each character: if it's in the dict it's a closer → pop, or substitute a
   sentinel if empty → compare → `return False` on mismatch. Otherwise push.
4. `return not stack`.

Two things to be able to justify out loud: why the sentinel removes a special
case, and why the final emptiness check is not optional.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) — the constructive counterpart: build all valid strings instead of checking one.
- [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) — Hard; same stack, but storing *indices* to measure spans.
- [Minimum Remove to Make Valid Parentheses](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) — stack of indices to delete.
- [Minimum Add to Make Parentheses Valid](https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/) — with one bracket type, a counter *is* enough; worth doing to see exactly why it fails once there are three types.
