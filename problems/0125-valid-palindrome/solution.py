# 125. Valid Palindrome (Easy) - two pointers converging from the ends, skipping non-alphanumerics in place and comparing case-folded. O(n) time, O(1) space.
class Solution:
    def isPalindrome(self, s: str) -> bool:

        left = 0
        right = len(s) - 1

        # Filtering in place rather than building a cleaned copy first is what
        # keeps this O(1) in extra space. On the empty string right is -1 and
        # the body never runs, returning True - which is the right answer,
        # though the constraints promise a non-empty s.
        while left < right:

            # Advance past anything that is not a letter or a digit.
            # `left < right` inside these inner loops is load-bearing, not
            # belt-and-braces: on a string with no alphanumerics at all, such
            # as "...", an unguarded scan would walk left off the end of the
            # string and raise IndexError. With the guard, left simply stops
            # once it meets right.
            while left < right and not s[left].isalnum():
                left += 1

            while left < right and not s[right].isalnum():
                right -= 1

            # If the skipping above collapsed the two pointers onto the same
            # index, this compares a character with ITSELF and is therefore
            # equal - so a single leftover character never causes a false
            # negative. That case then falls through to the increments below,
            # which cross the pointers and end the loop.
            #
            # .lower() on both sides is the case folding. Note isalnum() also
            # admits digits, and digits are unaffected by lower(), so numbers
            # compare as themselves.
            if s[left].lower() != s[right].lower():
                return False

            # Unconditional: the pair just matched, so both ends are consumed.
            # Moving only one pointer here would compare the same character
            # against its neighbour and loop forever on a match.
            left += 1
            right -= 1

        # Pointers crossed without a mismatch, so every alphanumeric pair
        # agreed and the string is a palindrome.
        return True
