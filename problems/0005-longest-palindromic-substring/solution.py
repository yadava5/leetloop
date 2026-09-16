# 5. Longest Palindromic Substring (Medium) - expand around each of the 2n-1 centres, remember the widest. O(n^2) time, O(1) extra space.
class Solution:
    def longestPalindrome(self, s: str) -> str:
        # Unreachable on LeetCode: the constraints promise 1 <= s.length, so s
        # is never empty. Kept because it costs nothing and makes the function
        # total if it is ever called from elsewhere.
        if not s:
            return ""

        # The answer is carried as (start, length), not as a string. Slicing
        # inside the loop would copy up to n characters every time a better
        # palindrome turned up; slicing once at the end copies exactly once.
        best_start = 0
        best_length = 1 # every single character is a palindrome itself!


        # Every palindrome is pinned by its CENTRE plus a radius, and there are
        # 2n-1 centres: n characters (which generate the odd lengths) and n-1
        # gaps between adjacent characters (the even lengths). Each pass of
        # this loop tries both kinds of centre anchored at index `centre`, so
        # over the whole loop all 2n-1 are covered.
        for centre in range(len(s)):

            # --- odd lengths. The window starts as the single character
            # s[centre], which is trivially a palindrome, so the while below
            # always runs at least once and `length` ends up at least 1.
            left = centre
            right = centre

            # `left >= 0` is load-bearing, not defensive: once left reaches -1
            # Python wraps it to the END of the string and starts comparing
            # characters that are nowhere near each other.
            # Stopping at the first mismatch is safe because any wider window
            # at this centre CONTAINS this one as its middle, so if this one is
            # not a palindrome no wider one can be either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            # The loop always exits one step PAST the palindrome on both sides
            # (either a mismatch or a fallen-off end), so the real window is
            # s[left+1 .. right-1] and its length is
            # (right - 1) - (left + 1) + 1 = right - left - 1.
            length = right - left - 1

            # Strict `>` keeps the FIRST palindrome of a given length, i.e. the
            # leftmost. LeetCode accepts any longest one; this just makes the
            # output deterministic.
            if length > best_length:
                best_length = length
                # left overshot by one, so the window begins at left + 1.
                # Writing `best_start = left` is the classic off-by-one here.
                best_start = left + 1

            # --- even lengths. The centre is now the GAP between s[centre] and
            # s[centre+1]. If those two differ, or centre is the last index,
            # the while body never runs and length comes out as
            # (centre + 1) - centre - 1 = 0, which loses every comparison
            # below - exactly right, since there is no even palindrome here.
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1

            if length > best_length:
                best_length = length
                best_start = left + 1

        # Same thing as s[best_start : best_start + best_length]; the two
        # operands of the sum are simply written the other way round.
        return s[best_start : best_length + best_start]
