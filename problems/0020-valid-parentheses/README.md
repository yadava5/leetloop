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

**Given** a string `s` built only from the six bracket characters
`(` `)` `[` `]` `{` `}`.

**Return** a boolean — `True` if the string is a well-formed bracket sequence,
`False` otherwise. Nothing is returned about *where* it broke, and the string is
not modified.

Well-formed means all three of these at once:

- every opener is eventually closed by a bracket **of the same type**;
- brackets close in the **reverse order they were opened**, so `[(` must be
  closed `)]` and never `])`;
- every closer has a matching opener that is still open at that moment — a
  closer arriving with nothing outstanding is invalid on its own.

**Guaranteed:** the string contains bracket characters and nothing else — no
letters, digits or spaces — and it is non-empty. The solution leans on the first
of those hard: it treats "not a closing bracket" as a synonym for "an opening
bracket" and pushes it without checking.

**Signature:** `def isValid(self, s: str) -> bool`

### Examples (mine, not LeetCode's)

| `s` | Answer | Why |
|---|---|---|
| `"{[()]}"` | `True` | Three types nested three deep. The stack grows to `['{', '[', '(']` and then unwinds exactly in reverse — the shape the algorithm is built around. |
| `"[[]][]"` | `True` | Siblings mixed with nesting. The stack empties completely in the middle of the string and that is fine; only its state at the *end* decides the answer. |
| `"([)]"` | `False` | **The counterexample.** Both types are balanced by count — one `(`, one `)`, one `[`, one `]` — and the string is still invalid. Any solution that tallies each bracket type independently answers `True` here and is wrong. |
| `"(("` | `False` | Nothing ever mismatches, so every check inside the loop passes. Only the final `return not stack` catches it. Drop that line and return `True` instead and this is the input that exposes it. |
| `"]"` | `False` | Shortest legal input, and the edge case: a closer arrives with an empty stack, so there is no `top_element` to compare against until the `"#"` sentinel supplies one. |

### Constraints, and what each one forces

*Recalled, not read: this environment has no network egress to leetcode.com —
the public GraphQL endpoint is blocked at the proxy — so the constraints below
are from memory rather than fetched from the problem page. The consequences hold
for the stated bounds; re-check the exact numbers against the live page if a
decision turns on them.*

| Constraint | Consequence |
|---|---|
| `1 <= len(s) <= 10^4` | Never empty, so there is no degenerate input to special-case. (The code would answer `True` for `""` anyway — vacuously correct, since a string with no brackets breaks no rule.) At n = 10⁴ a single O(n) pass is nothing; what the bound rules *out* is the tempting "repeatedly delete adjacent matched pairs until nothing changes" loop, which is O(n²) — around 10⁸ character moves here, far too slow in Python. |
| `s` consists only of `'()[]{}'` | The load-bearing constraint for *this* implementation. It is what makes `else: stack.append(char)` safe: anything that is not a key of `map` must be one of the three openers. Widen the alphabet by one character and the `else` branch silently pushes garbage onto the stack. |
| Three distinct bracket types, not one | Kills the single-integer-counter solution. With only `()` you could increment and decrement one counter and check it never goes negative; with three types you must remember *which* opener you are inside, and that is the whole reason a stack appears. |
| Order matters, not just counts | `"([)]"` is balanced per type and still invalid, so no per-type tally can decide this. The structure being tested is nesting, and nesting is last-in-first-out by definition. |
| Answer is a plain boolean | No need to track positions, build a repair, or count how many brackets are wrong — so the algorithm may return the instant it finds a single violation and never look at the rest of the string. |

## Key insight

The rule "closed in the correct order" is not an extra condition bolted onto
counting — it *is* the definition of a stack. The most recently opened bracket is
always the one that must close next, so the only fact worth remembering about
everything you have read so far is the list of still-open brackets in the order
they were opened. Every closer then asks one O(1) question: *are you the partner
of the thing on top?* If the answer is ever no, the string is dead; if the stack
is empty at the end, it was alive all along.

## Approach

1. `stack` starts empty and holds the openers seen so far that are still
   unclosed, most recent last.
2. `map` maps each **closer to its opener**. The direction matters: the loop
   looks things up by the closer it just read, so the closer has to be the key.
3. Walk the string one character at a time. `char in map` is the test for "is
   this a closing bracket?" — the same dict does membership duty and lookup
   duty, which is why there is no separate set of openers anywhere.
4. **If it is a closer**, pop the top of the stack into `top_element`. If the
   stack is empty there is nothing to pop, so use `"#"` — a character that can
   never equal any opener, guaranteeing the comparison on the next line fails.
5. Compare `map[char]` with `top_element`. Mismatch ⇒ return `False`
   immediately. This covers *both* failure modes with one comparison: wrong type
   (`"(]"`) and no opener at all (`")"`, via the sentinel).
6. **Otherwise it is an opener** — push it and move on.
7. After the loop, return `not stack`. Leftovers mean openers that were never
   closed, so an empty stack is the last condition for validity.

Two steps have load-bearing order. The pop in step 4 must happen **before** the
comparison in step 5, and it must be a `pop`, not a peek — consuming the opener
is what advances the match. And step 7 must run **after** the loop, not inside
it: `stack` legitimately empties and refills mid-string (see `"[[]][]"`), so an
empty stack only means anything once the input is exhausted.

## Solution

My exact submission, with comments added and nothing else changed — the AST gate
proves it. Also at [`solution.py`](solution.py); raw at
[`../../data/raw/valid-parentheses.py`](../../data/raw/valid-parentheses.py).

```python
# 20. Valid Parentheses (Easy) - single left-to-right pass with an explicit stack
# of unmatched openers; O(n) time, O(n) space. My submission, comments only.

class Solution:
    def isValid(self, s: str) -> bool:
        # The stack holds every opener seen so far that is still waiting to be
        # closed, most recent on top. "Closed in the right order" is exactly
        # last-in-first-out, which is why a stack - and nothing simpler, like
        # three counters - is the right structure here.
        stack = []

        # closer -> the opener it must be matched against. Note this dict is
        # doing double duty: `char in map` is also the test for "is this a
        # closing bracket?", which is what makes the loop below a clean
        # two-way branch with no separate set of openers to maintain.
        #
        # WART: `map` shadows the builtin `map()`. Harmless inside this method
        # because the builtin is never used, but it is a habit worth dropping;
        # `pairs` or `closer_to_opener` would say more and shadow nothing.
        # Preserved exactly as submitted - the AST gate would reject a rename.
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            if char in map:
                # A closer. Whatever it closes must be sitting on top of the
                # stack right now; anything else means the nesting is wrong.
                if stack:
                    top_element = stack.pop()
                else:
                    # Sentinel for "there is nothing to match against", i.e. a
                    # closer with no opener at all, like ")(" or "]". Using a
                    # character that can never be a legal opener collapses the
                    # empty-stack case into the same comparison as the normal
                    # case, so there is only one `return False` to reason about.
                    top_element = "#"
                if map[char] != top_element:
                    # Wrong type ("(]"), or nothing left to close (")"). Either
                    # way the string is already unsalvageable - no later
                    # character can repair a mismatch, so returning here is
                    # safe as well as fast.
                    return False
            else:
                # Not a closer, so under this problem's alphabet it is an
                # opener: push it and wait. The pop above is unconditional once
                # a closer arrives, so an opener that is never closed simply
                # survives to the end - which is what the final check catches.
                #
                # WART: this branch pushes ANY non-closing character, not just
                # the three openers. Correct here only because the constraints
                # promise s contains bracket characters and nothing else. Feed
                # it "a" and it happily pushes it and reports False.
                stack.append(char)
        # Every closer matched, but leftovers mean unclosed openers ("(("), so
        # the string is valid only if the stack drained completely. Forgetting
        # this line and returning True is the classic wrong answer: it passes
        # every balanced test and every mismatched one, and fails only on
        # prefixes that are still open.
        return not stack
```

## Why this approach

| Alternative | Cost | Why this beats it |
|---|---|---|
| Three independent counters, one per bracket type | O(n) time, O(1) space | **Wrong, not slow.** `"([)]"` gives every counter a final value of zero and the string is still invalid. Counting can never see interleaving, because nesting is an ordering property and a tally throws ordering away. |
| One counter with a "never goes negative" check | O(n) time, O(1) space | The correct solution to the *single*-bracket-type version of this problem, and it does not generalise: with three types the counter cannot say which opener you are inside, so `"(]"` slips through. Worth knowing precisely because it shows what the stack is buying. |
| Repeatedly `s.replace("()", "").replace("[]", "").replace("{}", "")` until the string stops shrinking | O(n²) time | Genuinely correct — collapsing innermost pairs is a valid reduction — but each pass rebuilds the whole string and there can be O(n) passes. At n = 10⁴ that is ~10⁸ character copies, a TLE in Python. Two lines of cleverness for a quadratic. |
| Recursive descent / grammar parser | O(n) time, O(n) stack | Same complexity, but it moves the stack from the heap to Python's call stack, where it is capped at ~1000 frames by default. `"(" * 5000` — legal input under the constraints — raises `RecursionError`. Strictly worse for no gain. |
| Regex | — | Not expressible. Balanced nesting to arbitrary depth is not a regular language; no pure regex can decide it. |
| Same stack, but peek instead of pop and clean up later | O(n) time, O(n) space | Equivalent in principle, but it needs an extra "consume the top" step after every successful match and an index or second pass to know how far it got. The pop-and-compare here fuses the two into one operation. |

## Complexity

- **Time — O(n).** One left-to-right pass over the string, and every character
  does a constant amount of work: one dict membership test, at most one dict
  lookup, and at most one push or pop. Early `return False` only makes it
  finish sooner. No character is ever revisited.
- **Space — O(n).** The stack is bounded by the number of unclosed openers,
  which is at most the whole string — `"(" * n` pushes n items before the loop
  ends. `map` is three fixed entries, so O(1). No copy of the input is made.

## Pitfalls

- **Forgetting the final `return not stack`.** The most common wrong answer, and
  it is invisible on most test cases: `"(("` never triggers a mismatch, so a
  version that returns `True` after the loop passes everything balanced and
  everything mismatched, and fails only on unclosed prefixes.
- **Believing counts are enough.** `"([)]"` is the input that settles it —
  balanced per type, invalid overall. If a candidate approach cannot explain why
  this string is `False`, it is not a solution.
- **Popping without checking for an empty stack.** `"]"` on an empty stack is
  `IndexError: pop from empty list`, a crash rather than a `False`. The `"#"`
  sentinel is how this code sidesteps it; a `if not stack: return False` guard
  is the more usual phrasing and does the same job.
- **Mapping opener → closer instead of closer → opener.** It also works, but
  only if you restructure the loop around it. Half-converting — building
  `{"(": ")"}` and still writing `if char in map` — silently inverts the test so
  every *opener* takes the closing branch, and the whole thing inverts.
- **The `else` branch pushes anything.** It is an `else`, not an
  `elif char in "([{"`. This is correct under the stated alphabet and only
  there; reuse this code on a string containing other characters and every
  letter becomes a phantom opener that can never be closed.
- **`map` shadows the builtin.** No bug in this method, since `map()` is never
  called after the assignment — but the shadow lasts to the end of the function,
  so adding a line that uses `map(...)` later would fail with
  `TypeError: 'dict' object is not callable`, which reads as nonsense until you
  spot the cause.
- **Assuming an early `return False` is unsafe.** It is safe, and worth being
  able to say why: a mismatch is unrepairable. No suffix can retroactively
  supply a missing opener or change what was already closed.

## Redo from scratch

Rebuild it cold, without reading the code:

1. `stack = []` — holds unclosed **openers**, in order.
2. A dict mapping **closer → opener**. Direction matters; the closer is what you
   have in hand when you need to look something up.
3. `for char in s:`
4. If `char` is in the dict, it is a closer: pop the top (or use a sentinel that
   matches nothing if the stack is empty), and `return False` unless it equals
   `map[char]`.
5. Otherwise push `char`.
6. After the loop, `return not stack`.

Be able to justify out loud: why a stack rather than three counters, using
`"([)]"` as the proof; why the empty-stack case needs handling at all and what
Python does if you skip it; and why `not stack` has to be checked after the loop
rather than inside it, given that the stack legitimately hits empty partway
through a valid string.

## Related problems

None of these are solved yet — links go to LeetCode.

- [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) — the natural next step: instead of *checking* validity you *construct* every valid string, so the same open/close invariant becomes the pruning rule in a backtracking search.
- [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) — hard, and the best stretch from here. Same stack, but it stores **indices** rather than characters so that the distance between a closer and the position below it gives a length. Learning to push indices instead of values is the transferable move.
- [Remove Invalid Parentheses](https://leetcode.com/problems/remove-invalid-parentheses/) — turns the boolean into a repair problem: find the minimum deletions that make the string valid. The validity check here becomes the inner test of a BFS.
- [Valid Parenthesis String](https://leetcode.com/problems/valid-parenthesis-string/) — adds a wildcard `*` that may be `(`, `)` or empty. A single stack no longer suffices because the state is now a *range* of possible open counts; the direct sequel to this problem's core idea.
- [Check If a Parentheses String Can Be Valid](https://leetcode.com/problems/check-if-a-parentheses-string-can-be-valid/) — some positions are locked and others are free to flip, which forces a two-pass left-then-right scan. Shows what happens when a single left-to-right stack is no longer enough information.
- [Check If Word Is Valid After Substitutions](https://leetcode.com/problems/check-if-word-is-valid-after-substitutions/) — same stack, but the "pair" being cancelled is the three-character block `abc` instead of a bracket, which makes it obvious that this technique is about reductions, not punctuation.
- [Move Pieces to Obtain a String](https://leetcode.com/problems/move-pieces-to-obtain-a-string/) — listed as similar; a two-pointer relative-order argument rather than a stack, useful mainly as a contrast for when order-checking does *not* need one.
- [Min Stack](https://leetcode.com/problems/min-stack/) — not about brackets, but the other canonical "why a stack" problem: here the LIFO order is the answer, there it is the thing you augment.
- [Basic Calculator](https://leetcode.com/problems/basic-calculator/) — where this leads. Parenthesis matching stops being the question and becomes the mechanism for saving and restoring evaluation state at each nesting level.
