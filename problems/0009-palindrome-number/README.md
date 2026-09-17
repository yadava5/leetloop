# 9. Palindrome Number

| | |
|---|---|
| **Difficulty** | Easy |
| **Topics** | Math |
| **Solved** | 2026-09-16 |
| **Runtime** | 13 ms (23.61th percentile) |
| **Memory** | 19.2 MB (55.12th percentile) |
| **Language** | Python3 |
| **LeetCode** | https://leetcode.com/problems/palindrome-number/ |

## The problem

**Given** a signed 32-bit integer `x`.

**Return** `True` if the decimal digits of `x` read the same forwards and
backwards, `False` otherwise.

Two points of definition, both of which the problem settles rather than leaves
open. A **negative** number is never a palindrome, because the minus sign
appears only at one end — `-121` reads as `121-` reversed. And there are **no
leading zeros** in the decimal representation of an integer, which is what makes
`10` fail: it reverses to `01`, i.e. `1`, and `1 != 10`.

The idiomatic Python answer is `str(x) == str(x)[::-1]`. The problem's follow-up
asks you to do it without converting to a string, which is the version here.

**Guaranteed**: `x` fits in a signed 32-bit integer. In Python that guarantee
buys nothing (integers are arbitrary precision); in C++ or Java it is the crux
of the problem, since reversing a number near the limit overflows.

```text
def isPalindrome(self, x: int) -> bool
```

### Examples (mine, not LeetCode's)

| `x` | Returns | Why |
|---|---|---|
| `1000000001` | `True` | A long palindrome with interior zeros — the case that catches anyone who tries to strip zeros as a shortcut. The zeros must be reproduced, not skipped. |
| `100` | `False` | **Counterexample to "reverse the digits and compare the digit multiset".** The digits of `100` reversed are `001`, which as a *number* is `1`. Trailing zeros have no leading counterpart, so any number ending in `0` (except `0` itself) fails. |
| `0` | `True` | **Edge case:** the loop body never runs, `rev` stays `0`, and `0 == 0`. The one input where the `while` executes zero times, and it happens to give the right answer for free. |
| `-121` | `False` | The sign check does all the work. Also the input that would make the loop misbehave if the guard were removed — see Pitfalls. |
| `2147483647` | `False` | The 32-bit maximum. Included because it is the input that *breaks* this approach in a fixed-width language: its reversal, `7463847412`, exceeds `2^31 - 1`. In Python it is simply a large integer and nothing goes wrong. |
| `7` | `True` | Single digit. Every one-digit non-negative number is a palindrome, and the loop handles it with one iteration rather than a special case. |

### Constraints, and what each one forces

| Constraint | What it forces |
|---|---|
| `-2^31 <= x <= 2^31 - 1` | The **negative half of the range is the entire reason the first guard exists** — without `-2^31` being reachable, `if x < 0: return False` would be dead code. It is not merely a correctness shortcut either: the loop uses `//`, which in Python floors *towards minus infinity*, so `-121 // 10` is `-13`, then `-2`, then `-1`, then `-1` forever. The guard is what makes the function terminate, not just what makes it right. The **upper bound of `2^31 - 1` is what the problem is really testing**, and it is testing something Python is immune to: the reversal of a 10-digit number can need 10 digits of its own and overflow a 32-bit accumulator. That is why the canonical solution reverses only *half* the digits. Here the bound rules nothing out — Python's integers do not overflow — so the simpler full reversal is available and safe. The bound also caps the loop at 10 iterations, which is why the runtime is dominated by interpreter startup rather than by the work (hence the unremarkable 23.61th percentile: at this size, `str(x) == str(x)[::-1]` is measurably faster than arithmetic in CPython). |

## Key insight

You do not need the digits as a sequence. Building the reversed number
arithmetically — repeatedly peel the last digit off with `% 10` and push it onto
the growing reversal with `rev * 10 + digit` — produces a single integer you can
compare in one step. The only thing this costs you is the original value, which
the loop destroys, so it must be saved before the first peel.

## Approach

1. Reject negatives immediately.
2. Save `original = x` **before** touching `x`.
3. While `x > 0`: take `digit = x % 10`, do `rev = rev * 10 + digit`, then
   `x = x // 10`.
4. Return `original == rev`.

Two orderings are load-bearing. **Step 2 must precede step 3** — the loop
consumes `x` down to `0`, so comparing against `x` at the end would compare `0`
to the reversal and answer `True` only for `x = 0`. And **inside the loop,
`rev` must be updated before `x` is divided**, since the division destroys the
digit that `% 10` just read; writing `x = x // 10` first makes `digit` refer to
the wrong place.

## Solution

```python
# 9. Palindrome Number (Easy) - reverse the digits arithmetically and compare against a saved copy. O(d) time in the digit count, O(1) space.
class Solution:
    def isPalindrome(self, x: int) -> bool:

        # Any negative number loses immediately: the leading '-' has no
        # counterpart at the other end, so -121 reads as 121- backwards.
        # This guard is also what makes the loop below terminate on negatives
        # instead of spinning - Python's // floors towards minus infinity, so
        # -121 // 10 is -13, then -2, then -1, then -1 forever.
        if x < 0:
            return False


        # ORDER IS LOAD-BEARING: the loop consumes x destructively, so the
        # original value has to be copied before a single digit is stripped.
        # Comparing against x at the end would compare 0 to the reversal.
        original = x
        rev = 0

        # Strip the last digit off x and append it to rev. `while x > 0` and
        # not `>= 0`, because x hits exactly 0 when the digits run out and
        # `>= 0` would never end.
        #
        # x == 0 enters with the loop body never running: rev stays 0,
        # original is 0, and 0 == 0 is True. Correct, and it is the one input
        # where the body is skipped entirely.
        while x > 0:
            digit = x % 10
            rev = rev * 10 + digit
            x = x // 10

        # Trailing zeros are handled by this comparison rather than by a
        # special case: 10 reverses to 1, and 10 != 1. Only 0 itself survives.
        #
        # Note the full reversal is safe here purely because this is Python.
        # In a fixed-width language rev can overflow for inputs near 2^31 - 1,
        # which is why the standard solution reverses only half the digits.
        return original == rev
```

[solution.py](solution.py) · [raw submission](../../data/raw/palindrome-number.py)

## Why this approach

| Alternative | Cost | Why the arithmetic reversal is the one to know |
|---|---|---|
| `str(x) == str(x)[::-1]` | O(d) time, O(d) space | Shorter, and in CPython **faster** — the slicing runs in C while the loop here runs in the interpreter. It is the right answer in real code. It is excluded only because the problem's follow-up asks explicitly for a no-string solution, and because it teaches nothing. |
| Two pointers over `str(x)` | O(d) time, O(d) space | Same string conversion, more code, no advantage over the slice. Its one merit is that it generalises to *Valid Palindrome*, where characters must be filtered as you go. |
| Reverse **half** the digits: build `rev` until `rev >= x`, then compare `x == rev` (odd lengths: `x == rev // 10`) | O(d) time, O(1) space, **no overflow** | The canonical answer, and strictly better in a fixed-width language, since `rev` never exceeds the remaining `x` and so never overflows. It costs a special case for trailing zeros (any `x` ending in `0` and not equal to `0` must be rejected up front, or `10` is wrongly accepted) and a second special case to drop the middle digit. In Python, none of that is bought by anything, so the full reversal is the better trade here — but this is the version to reach for if the language changes. |
| Extract digits into a list, then two-pointer the list | O(d) time, O(d) space | Correct and easy to reason about, and it does avoid overflow. It just allocates a list to hold what a single integer already encodes. |
| Compare the leading and trailing digit using `10 ** (d-1)` to isolate the head | O(d) time, O(1) space, no overflow | Also correct, and overflow-proof without the half-reversal's trailing-zero case. The bookkeeping — recomputing the divisor by `100` each round, handling the odd middle digit — is fiddlier than either alternative above, which is why nobody writes it. |
| Convert the digit multiset and check it is symmetric | **Wrong** | Not an alternative at all, but it is the shape of a wrong idea worth naming: `100` and `001` have the same digits. Palindromicity is about *order and position*, and leading zeros are not representable, so any count-based approach loses exactly the information that distinguishes `100` from `001`. |

## Complexity

- **Time — O(d)** where `d` is the number of decimal digits, i.e. `O(log₁₀ x)`.
  Bounded at **10 iterations** by the 32-bit constraint, so in practice constant.
  Each iteration is one modulo, one multiply-add and one floor division.
- **Space — O(1)**. Three integers (`original`, `rev`, `digit`) and no allocation
  that grows with the input — which is the one concrete advantage over the string
  solution, whose `str(x)[::-1]` allocates a copy.

## Pitfalls

- **Comparing against `x` instead of `original`.** The loop leaves `x` at `0`, so
  the function returns `True` only for `x = 0` and `False` for everything else.
  Silent, and the reason the `original = x` line is not decoration.
- **Dropping the `x < 0` guard.** This does not merely return a wrong answer — it
  **hangs**. Python's `//` floors towards minus infinity, so `-121` goes
  `-13, -2, -1, -1, -1, …` and `x > 0` is never satisfied but `x` stops changing.
  (In C or Java, where `/` truncates towards zero, the same code terminates and
  returns the wrong answer instead. Different language, different failure.)
- **Trying to special-case trailing zeros.** Unnecessary in *this* version:
  `100` reverses to `1` and the comparison rejects it. The special case is
  required only in the half-reversal variant, and people import it from there by
  habit — where, written as `if x % 10 == 0: return False`, it also wrongly
  rejects `x = 0`.
- **`rev = rev + digit * 10`** instead of `rev = rev * 10 + digit`. The classic
  transposition, and it does not build a reversal at all — it builds a weighted
  digit sum. On `x = 11` it produces `rev = 20` against `original = 11` and
  answers `False`, where the truth is `True`. Any input it gets right, it gets
  right by coincidence.
- **`while x >= 0`.** Never terminates: `x` reaches `0` and stays there, with
  `rev` multiplied by `10` forever.
- **Reading `digit` after the division.** `x = x // 10` then `digit = x % 10`
  reads the *second-to-last* digit, dropping the last one entirely.
- **Assuming the 32-bit bound protects you in other languages.** It does the
  opposite: it is the bound that makes overflow possible for a 10-digit input.
  If you port this code to Java, `rev` must be a `long`, or you must switch to
  the half-reversal.

## Redo from scratch

1. Reject negatives first, and be able to say **both** reasons — the sign has no
   mirror, and the floor division would not terminate.
2. Save the original before the loop destroys `x`.
3. Peel with `% 10`, push with `rev * 10 + digit`, shrink with `// 10`, in that
   order.
4. `while x > 0`, not `>= 0`.
5. Compare `original == rev`.
6. Test `0` (empty loop), `10` (trailing zero), `1000000001` (interior zeros),
   `-121` (the guard).

Be able to justify out loud: **why `10` is not a palindrome** — because integers
have no leading zeros, so there is no `01` to match — and **why the negative
guard is a termination argument in Python and only a correctness argument in
C**. Also worth being able to say what the *half*-reversal buys and what it
costs, because that is the version an interviewer is usually fishing for.

## Related problems

- [Valid Palindrome](../0125-valid-palindrome/README.md) — already solved, and
  the same word applied to a string with filtering and case folding on top.
  Reading the two together separates "palindrome" as a property from the
  machinery used to test it.
- [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/)
  — not solved yet, and the genuinely interesting sibling: no random access, so
  you reverse the second half in place and walk the two halves towards each
  other. The O(1)-space requirement there is real, unlike here.
- [Reverse Integer](https://leetcode.com/problems/reverse-integer/) — not solved
  yet, and it is this problem's loop with the overflow check that Python let us
  skip made mandatory. The best follow-up if you want the 32-bit lesson to land.
- [Strictly Palindromic Number](https://leetcode.com/problems/strictly-palindromic-number/)
  — not solved yet. Asks for palindromicity in *every* base from 2 to `n - 2`,
  and the answer is a one-line proof rather than a loop. A nice reminder to look
  for the argument before writing the code.
- [Count Symmetric Integers](https://leetcode.com/problems/count-symmetric-integers/)
  — not solved yet. Digit manipulation over a range rather than a single number;
  a gentle step towards digit DP.
- [Find Palindrome With Fixed Length](https://leetcode.com/problems/find-palindrome-with-fixed-length/)
  — not solved yet. Inverts the question: *construct* the k-th palindrome of a
  given length instead of testing one. Forces you to notice that a palindrome is
  determined entirely by its first half, which is exactly the observation behind
  the half-reversal variant above.
