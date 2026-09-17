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
