# 647. Palindromic Substrings (Medium) - expand around each of the 2n-1 centres, adding 1 per successful expansion. O(n^2) time, O(1) space.
class Solution:
    def countSubstrings(self, s: str) -> int:
        # Unreachable on LeetCode: the constraints promise 1 <= s.length.
        if not s:
            return 0


        total = 0

        # Every palindromic substring has exactly ONE centre - a character when
        # its length is odd, the gap between two characters when it is even -
        # and exactly one radius at that centre. So walking all 2n-1 centres
        # and counting every successful expansion counts each palindromic
        # substring once and once only. Nothing is deduplicated, and nothing
        # should be: two occurrences of the same TEXT at different positions
        # are two different substrings and both count.
        for centre in range(len(s)):

            # --- odd lengths: centre is a character. The first test is
            # s[centre] == s[centre], always true, so each of the n single
            # characters is counted exactly here.
            left = centre
            right = centre

            # `left >= 0` is load-bearing: at left == -1 Python wraps round to
            # the end of the string and starts matching unrelated characters.
            # Breaking at the first mismatch is safe because a wider window at
            # this centre contains this one as its middle - if this is not a
            # palindrome, nothing wider here is either.
            while left >= 0 and right < len(s) and s[left] == s[right]:
                # One increment per successful test. Written at the top of the
                # body so it reads as counting s[left..right], the window the
                # condition has just proved palindromic - though the total is
                # the same wherever inside the body it sits, since what is
                # really being counted is the number of iterations. What IS
                # load-bearing is that it is inside the while at all: one per
                # ITERATION, not one per centre.
                total += 1

                left -= 1
                right += 1

            # --- even lengths: the centre is the gap between s[centre] and
            # s[centre+1]. If those differ, or centre is the last index, the
            # body never runs and nothing is added, which is correct.
            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1

                left -= 1
                right += 1

        return total

