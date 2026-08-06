# 20. Valid Parentheses

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | String, Stack, Bracket Sequences |
| **Solved** | 2026-08-05 |
| **Runtime** | 4 ms (12.37th percentile) |
| **Memory** | 19.4 MB (23.97th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/valid-parentheses/ |

## The problem

**Given** a string `s` made up only of the six bracket characters
`(`, `)`, `{`, `}`, `[`, `]`. No letters, digits or spaces ever appear.

**Return** a boolean: `True` if the string is a well-formed bracket sequence,
`False` otherwise. Well-formed means all three of the following hold at once —
and it is the third that makes this more than a counting exercise:

1. every opening bracket is eventually closed;
2. every closing bracket has an opening bracket before it;
3. brackets close in the **reverse order** they were opened, so pairs nest and
   never cross. `([)]` fails only this third rule.

**Guaranteed**: the string contains nothing but those six characters, and is
non-empty. So "this character is not a closer" can be read directly as "this
character is an opener", with no validation branch.

```text
def isValid(self, s: str) -> bool
```

### Examples (mine, not LeetCode's)

| `s` | Returns | Why |
|---|---|---|
| `{[()]}` | `True` | Fully nested, three levels deep. The stack fills to depth 3 and then drains cleanly. |
| `(){}[]` | `True` | Sequential rather than nested — the stack never exceeds depth 1. Both shapes are valid; nesting is not required. |
| `([)]` | `False` | **Counterexample to the naive approach.** Each bracket type appears exactly once open and once closed, so any counting scheme calls this valid. It is not: the pairs cross. Only a stack catches it. |
| `(((` | `False` | **Edge case:** nothing ever mismatches, so the loop finishes without returning early. The answer comes entirely from the leftover stack — this is why the last line is `not stack` and not `True`. |
| `]` | `False` | **Edge case:** the minimum legal input, and a closer with no opener at all. The stack is empty at the moment it is consulted, which is what the `"#"` sentinel exists to handle. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `1 <= s.length <= 10^4` | The lower bound means the empty string is never tested, so you do not need to decide whether `""` is valid (the code returns `True` for it anyway, which is the conventional answer). The upper bound is comfortable for anything linear, and generous enough that an O(n²) "repeatedly delete `()`, `[]`, `{}` substrings until nothing changes" approach degenerates badly — on `(((...)))` it rebuilds the whole string on each pass, ~10^8 character copies. |
| `s consists of parentheses only '()[]{}'.` | This is the constraint the code leans on hardest. Because nothing else can appear, `else: stack.append(char)` is safe — "not a key in `map`" is a *proof* that `char` is an opener, not an assumption. Drop this guarantee and letters would be pushed onto the stack as if they were brackets, and a string like `a` would come back `False` instead of raising or being rejected on its own terms. |

## Key insight

When you hit a closing bracket, only one opener can legally match it: the most
recent one still unclosed. That is the definition of a stack, so you do not need
to search or count — you pop, and compare against exactly one candidate. Counting
brackets per type cannot work, because counts are blind to order and `([)]` has
perfectly balanced counts.

## Approach

1. Start with an empty `stack` holding the openers seen so far that are still
   unmatched.
2. Build a dict keyed by **closer → its opener**. The direction matters: keying
   this way makes `char in map` double as the test "is this a closing bracket?",
   so one structure does two jobs.
3. Walk the string one character at a time.
4. If `char` is in `map` it is a closer. Pop the top of the stack to get the
   opener it must match. If the stack is empty there is no opener at all, so use
   the sentinel `"#"` — a value that cannot equal any opener, which lets the same
   comparison handle both "wrong bracket" and "no bracket" without a second
   branch.
5. If `map[char]` does not equal the popped element, the string is invalid;
   return `False` immediately. Two ways to get here: a mismatch (`(]`) or the
   sentinel (`)` with nothing open).
6. Otherwise `char` is an opener; push it and continue.
7. **After the loop, return `not stack`, not `True`.** Surviving the loop only
   proves nothing *mismatched*; leftover openers like `(((` never mismatch
   because their closers never arrive. The stack being empty is the second half
   of the answer, and forgetting this step is the single most common way to fail
   this problem.

## Solution

```python
# 20. Valid Parentheses (Easy) - stack of unmatched openers. O(n) time, O(n) space.
class Solution:
    def isValid(self, s: str) -> bool:
        # Holds every opening bracket seen so far that is still unmatched.
        # A stack is the right shape because brackets must close in reverse
        # order of opening: the most recent opener is always the one that has
        # to be closed next.
        stack = []

        # WART worth knowing: `map` shadows the Python builtin inside this
        # method. Harmless here since the builtin is never used, but it is the
        # kind of habit that bites in a longer function.
        # Keyed by CLOSER -> its matching opener, not the other way round. That
        # direction is what lets `char in map` below act as the "is this a
        # closing bracket?" test in the same lookup structure.
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            # Membership in map means char is a closer, because only closers
            # are keys. The problem guarantees s contains nothing but the six
            # bracket characters, so "not a closer" safely means "an opener".
            if char in map:
                if stack:
                    top_element = stack.pop()
                else:
                    # Empty stack means this closer has no opener at all, e.g.
                    # "()]" or a leading ")". "#" is a sentinel that can never
                    # equal any value in map, so the comparison below fails and
                    # we return False without needing a separate branch.
                    top_element = "#"
                # The popped opener must be the partner of THIS closer.
                # Mismatch means crossed brackets like "([)]" - each type is
                # individually balanced, but the nesting is wrong, which is
                # exactly the case a counter-per-bracket-type approach misses.
                if map[char] != top_element:
                    return False
            else:
                # An opener: park it until its closer shows up.
                stack.append(char)
        # Falling out of the loop only means nothing mismatched. Leftover
        # openers like "(((" are still invalid, so the answer is "the stack
        # drained completely", not plain True.
        return not stack
```

[solution.py](solution.py) · [raw submission](../../data/raw/valid-parentheses.py)

## Why this approach

| Alternative | Cost | Why the stack beats it |
|---|---|---|
| Three counters, one per bracket type; check none go negative and all end at zero | O(n) time, O(1) space | **Wrong, not slow.** `([)]` gives every counter a clean 1-up-1-down and passes, but it is invalid. Counters cannot see interleaving. This is *sound* for a single bracket type — which is exactly why the one-type variants of this problem are easier, and why it is a trap here. |
| Repeatedly `s.replace("()", "").replace("[]", "").replace("{}", "")` until the string stops shrinking | O(n²) time, O(n) space | Correct, but each pass rebuilds the whole string and removes only the innermost layer. On a 10^4-character nest like `((( ... )))`, that is 5×10^3 passes over an O(n) string — roughly 10^8 character copies, a plausible TLE and certainly not what the problem is teaching. |
| Regex | — | No regular expression can match balanced nesting to arbitrary depth; that is the textbook example of a non-regular language. Some engines have recursive extensions, but reaching for them here is answering a different question. |
| Recursive descent / explicit grammar parse | O(n) time, O(n) space | Same asymptotics, but Python's default recursion limit is 1000 and the input can nest 10^4 deep, so `((((...` blows the stack and crashes. The explicit stack is the same algorithm with the recursion made iterative — strictly better here. |
| Push the *expected closer* instead of the opener | O(n) time, O(n) space | Equally correct and arguably tidier: on `(` push `)`, and on any closer just check it equals `stack.pop()`. Worth knowing as a variant. The version here keeps the raw openers on the stack, which is easier to debug because printing the stack shows the literal unclosed brackets. |

## Complexity

- **Time — O(n).** Each character is examined once. Every character is pushed at
  most once and popped at most once, and dict membership and lookup are O(1), so
  the total work is linear in `len(s)`. Early `False` returns only cut it short.
- **Space — O(n).** The stack holds unmatched openers, which in the worst case is
  every character: a fully nested string like `((((...` reaches depth `n`. The
  `map` dict is three fixed entries, i.e. O(1). The 4 ms / 12th-percentile
  runtime is not an algorithmic problem — it is per-character Python interpreter
  overhead on a 10^4 string, and the judge's timing noise at this scale is larger
  than most of the percentile spread.

## Pitfalls

- **Returning `True` after the loop instead of `not stack`.** The number-one bug.
  `(((` never triggers a mismatch, so the loop completes normally and the buggy
  version reports valid. The leftover stack *is* the failure.
- **Popping an empty stack.** `s = ")"` calls `.pop()` on an empty list and
  raises `IndexError`. The `if stack: ... else: top_element = "#"` dance exists
  purely to prevent that. Any sentinel works as long as it can never be a value
  in `map` — using `""` or `None` is equally fine, using `"("` is a disaster.
- **Trusting counts.** `([)]` is the canonical input that separates a real
  solution from a plausible one. Test it first, every time.
- **Keying the dict opener → closer.** It works, but then `char in map` means
  "is this an *opener*", and the whole body inverts: you push when `char in map`
  and compare `map[stack.pop()] != char` otherwise. Half-converting between the
  two directions is how this problem gets failed by someone who understands it.
- **Assuming input is non-bracket-safe and adding validation.** Wasted code —
  the constraint rules it out. But do notice that the code *depends* on that;
  it is not defensively written.
- **`map` shadowing the builtin.** No effect in this method, but if you later
  add a line that wants the real `map()`, it is gone. Worth breaking the habit
  even though the submission is correct.

## Redo from scratch

1. `stack = []`.
2. Dict keyed **closer → opener**, three entries. Fix the direction in your head
   before typing, since the rest of the loop follows from it.
3. Loop over the characters of `s`.
4. If the character is a key, it is a closer: pop the stack if non-empty, else
   take a sentinel that can never match.
5. Compare `map[char]` against what you popped; mismatch means `return False`.
6. Else push the character.
7. **`return not stack`** — never a bare `True`.

Be able to justify out loud:

- **Why counting brackets per type cannot work.** Give `([)]` as the concrete
  counterexample: balanced counts, invalid string. Counts have no notion of
  order; the stack encodes exactly the ordering constraint that is being tested.
- **Why the last line is `not stack`.** Give `(((` as the input: the loop returns
  no failure, so the entire answer rests on that final check.

## Related problems

- [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) — not solved yet. The inverse: instead of validating a sequence, enumerate all valid ones by backtracking. It converts the *rule* you just implemented into a *pruning condition*, which is the point.
- [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) — not solved yet. Hard, and the natural escalation. Push *indices* rather than characters so you can measure the span between matches — the step from "is it valid" to "how much of it is valid".
- [Check If a Parentheses String Can Be Valid](https://leetcode.com/problems/check-if-a-parentheses-string-can-be-valid/) — not solved yet. Adds locked and unlocked positions, so a single stack is no longer enough and you need a two-pass range-of-possible-depths argument. Good for seeing where the simple stack stops scaling.
- [Remove Invalid Parentheses](https://leetcode.com/problems/remove-invalid-parentheses/) — not solved yet. Hard. Uses this validity check as the test inside a BFS over deletions; a direct demonstration that this problem is a primitive other problems call.
- [Minimum Add to Make Parentheses Valid](https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/) — not solved yet, and not in the similar list, but the best immediate follow-up. Single bracket type, so a counter *is* sufficient — solving it right after this one is how you learn precisely when the stack is overkill and when it is mandatory.
- [Check If Word Is Valid After Substitutions](https://leetcode.com/problems/check-if-word-is-valid-after-substitutions/) — not solved yet. Same stack machinery with a three-character pattern instead of paired brackets; tests whether you learned the technique or the special case.

*None of the related problems above are in this repo yet.*
