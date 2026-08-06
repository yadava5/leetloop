<!-- GENERATED. Problem restated in my own words with my own examples; never
     LeetCode's text. The ```python block below is gated by
     scripts/verify_ast.py against data/raw/valid-parentheses.py. -->

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

## The problem

**Given** a string `s` containing only the six characters `(`, `)`, `{`, `}`,
`[`, `]`.

**Return** `True` if the string is well-formed, `False` otherwise. Well-formed
means all three of:

1. every closing bracket closes a bracket that is actually open;
2. it closes the **most recently** opened unclosed bracket — brackets may nest
   but may not interleave;
3. nothing is still open when the string ends.

**Signature:** `def isValid(self, s: str) -> bool`

### Examples (mine, not LeetCode's)

| `s` | Answer | Why |
|---|---|---|
| `"([{}])"` | `True` | properly nested, innermost closes first |
| `"(){}[]"` | `True` | siblings, not nested — also fine |
| `"([)]"` | `False` | interleaved: `)` tries to close `[`. **The counterexample that kills counting.** |
| `"((("` | `False` | nothing is wrong *during* the scan; it fails only because three are left open |
| `"]"` | `False` | a closer with nothing open |

### Constraints, and what each one forces

| Constraint | Consequence |
|---|---|
| `1 <= len(s) <= 10^4` | The string is never empty, so no empty-input special case. One linear pass is comfortably fast; an O(n²) approach is wasteful at this size. |
| `s` contains only `()[]{}` | There are no other characters to defend against, which is what makes "not a closer ⇒ it's an opener" safe. With an arbitrary alphabet that shortcut would be a bug. |
| nesting can be 10⁴ deep | A recursive formulation would risk `RecursionError` at Python's default limit of 1000. An explicit stack has no such ceiling. |

## Key insight

"Must match the **most recently** opened bracket" is the definition of a stack —
last in, first out. Once you read that sentence as *stack*, the problem is
mechanical.

The corollary matters just as much: **counting cannot work.** `([)]` has one of
each bracket and is perfectly balanced by count, yet it's invalid. Any solution
that only tracks how many of each type are open is wrong, not merely imprecise.

## Approach

1. `stack` holds openers that are still waiting to be closed.
2. `map` sends each **closer** to the opener it requires. Keying by the closer is
   a small trick: `char in map` doubles as "is this a closing bracket?".
3. Walk the string one character at a time.
   - **Closer:** pop the top of the stack — or substitute the sentinel `"#"` if
     the stack is empty — and compare against `map[char]`. Mismatch → `False`
     immediately.
   - **Opener:** push it.
4. After the loop, `return not stack`. An empty stack means everything opened got
   closed.

The `"#"` sentinel is the elegant part: it collapses "there is nothing to match
against" into the same comparison as "the wrong thing is there", so there's no
separate empty-stack branch and no `IndexError`.

## Solution

My exact submission, with comments added and nothing else changed — the AST gate
proves it. Also at [`solution.py`](solution.py); raw at
[`../../data/raw/valid-parentheses.py`](../../data/raw/valid-parentheses.py).

```python
class Solution:
    def isValid(self, s: str) -> bool:
        # Holds every opener that is still waiting to be closed. A stack is the
        # right structure because "most recently opened" is exactly what a
        # closing bracket has to match.
        stack = []

        # closer -> the opener it demands. Keying by the closer means `char in
        # map` doubles as the test "is this a closing bracket?".
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            if char in map:
                # A closer. The opener it must match is whatever is on top.
                if stack:
                    top_element = stack.pop()
                else:
                    # Nothing is open, so this closer can't be matched. The
                    # sentinel loses the comparison below, which avoids both an
                    # IndexError and an early-return special case.
                    top_element = "#"

                # Right kind of bracket in the wrong place, or none at all.
                if map[char] != top_element:
                    return False
            else:
                # Not a closer, so by the problem's alphabet it is an opener:
                # record it as now-open.
                stack.append(char)

        # Everything matched, but trailing openers like "(((" leave the stack
        # non-empty - only an empty stack means well-formed.
        return not stack
```

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Three counters, one per bracket type | O(n) time, O(1) space | **Wrong**, not just weaker: it accepts `([)]`. Counters discard ordering, and ordering is the entire problem. |
| Repeatedly delete `"()"`, `"[]"`, `"{}"` substrings until the string stops shrinking | O(n²) time | Correct but quadratic — each pass rescans. Up to ~10⁸ character operations for what one pass does. |
| Recursive descent | O(n) time, O(n) stack | Same algorithm in spirit, but 10⁴-deep nesting risks `RecursionError` at the default limit of 1000. The explicit stack removes the ceiling. |

## Complexity

- **Time — O(n).** Each character is pushed at most once and popped at most
  once; every comparison is O(1).
- **Space — O(n).** Worst case is all openers, `"((((("`, where the stack grows
  to the full length of the input.

## Pitfalls

- **Forgetting the final `return not stack`.** `"((("` never triggers a mismatch,
  because comparisons only happen on closers — so a bare `return True` at the end
  wrongly accepts it. This is the single most common wrong answer here.
- **Popping an empty stack.** A lone `")"` raises `IndexError` without the `"#"`
  sentinel or an explicit emptiness check.
- **Counting instead of ordering.** `([)]` is the counterexample to keep in your
  pocket.
- **Matching only the bracket *kind* and not the position.** Checking "is the top
  of the stack any opener?" accepts `"(]"`. The comparison has to be against the
  *specific* opener `map[char]`.
- **`map` shadows the builtin.** Inside this method `map` is a dict, so the
  builtin `map()` is unavailable for the rest of the function. Harmless here and
  the code is preserved exactly as submitted, but `pairs` or `closer_to_opener`
  is the better habit — shadowing builtins gets genuinely confusing in longer
  functions.
- **Treating "not a closer" as "an opener"** is safe *only* because the
  constraints guarantee the six-character alphabet.

## Redo from scratch

Rebuild it cold, without reading the code:

1. `stack = []`.
2. Dict mapping **closer → opener** (not the other way round).
3. For each character: if it's in the dict it's a closer → pop, or substitute a
   sentinel if empty → compare → `return False` on mismatch. Otherwise push.
4. `return not stack`.

Be able to justify out loud: why the sentinel removes a special case, why the
final emptiness check isn't optional, and why `([)]` defeats counting.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) — the constructive counterpart: build every valid string instead of checking one.
- [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) — Hard; same stack, but storing *indices* so you can measure spans.
- [Minimum Remove to Make Valid Parentheses](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) — stack of indices to delete rather than a boolean verdict.
- [Minimum Add to Make Parentheses Valid](https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/) — with a single bracket type a counter genuinely *is* enough; worth doing to feel exactly where the third type breaks it.
