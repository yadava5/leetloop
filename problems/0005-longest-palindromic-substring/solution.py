# 5. Longest Palindromic Substring (Medium) - expand around all 2n-1 centres, recording the widest window as it grows. O(n^2) time, O(1) extra space.
class Solution:
    def longestPalindrome(self, s: str) -> str:

        # Unreachable on LeetCode: the constraints promise 1 <= s.length, so
        # s is never empty. Costs nothing and makes the function total if it
        # is ever called from elsewhere.
        if not s:
            return ""

        # The answer is carried as (start, length), never as a string.
        # Slicing inside the loop would copy up to n characters every time a
        # wider palindrome turned up; slicing once at the end copies once.
        #
        # `best_string` holds a LENGTH, not a string - the name is a wart.
        # Seeding it at 1 with best_start 0 means "the first character" is the
        # standing answer: every single character is a palindrome, so on a
        # string with no palindrome longer than 1 ("abc") the loop below never
        # improves on this and s[0] is returned. Note the loop does compute a
        # length of 1 at every odd centre, but `1 > 1` is false, so it is the
        # seed and not the loop that supplies that case.
        best_string = 1
        best_start = 0

        # Every palindrome is pinned by a CENTRE plus a radius, and there are
        # 2n-1 centres: n characters (odd lengths) and n-1 gaps between
        # adjacent characters (even lengths). Each pass handles both kinds
        # anchored at `centre`, so all 2n-1 are covered.
        for centre in range(len(s)):

            # --- odd lengths. The window starts as the single character
            # s[centre], which is trivially a palindrome, so this while always
            # runs at least once.
            left = centre
            right = centre

            # `left >= 0` is load-bearing, not defensive. Once left reaches -1
            # Python wraps it to the END of the string and starts comparing
            # characters nowhere near each other: without this test, "aa"
            # returns "a" and "aab" returns "b".
            #
            # Stopping at the first mismatch is safe because any wider window
            # at this centre CONTAINS this one as its middle, so if this one
            # is not a palindrome no wider one can be either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1

                # Measured INSIDE the loop, after each successful step. left
                # and right have already moved one past the palindrome on both
                # sides, so the real window is s[left+1 .. right-1] and its
                # length is (right - 1) - (left + 1) + 1 = right - left - 1.
                current_string = right - left - 1

                # Strict `>` keeps the FIRST palindrome of a given length,
                # i.e. the leftmost. LeetCode accepts any longest one; this
                # just makes the output deterministic.
                if current_string > best_string:
                    best_string = current_string

                    # left overshot by one, so the window begins at left + 1.
                    # Writing `best_start = left` is the classic off-by-one:
                    # it turns "abba" into "" and "bananas" into "banan".
                    best_start = left + 1


            # --- even lengths. The centre is now the GAP between s[centre]
            # and s[centre+1]. If those differ, or centre is the last index,
            # the body never runs and nothing is recorded for this centre -
            # correct, since there is no even palindrome here. (Unlike the odd
            # case, this loop can record nothing at all, which is why the
            # measurement lives inside the body rather than after it.)
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1

                current_string = right - left - 1

                if current_string > best_string:
                    best_string = current_string

                    best_start = left + 1

        return s[best_start : best_start + best_string]
