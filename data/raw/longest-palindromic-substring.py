class Solution:
    def longestPalindrome(self, s: str) -> str:
        if not s:
            return ""

        best_start = 0
        best_length = 1 # every single character is a palindrome itself!


        for centre in range(len(s)):

            left = centre
            right = centre

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1

            if length > best_length:
                best_length = length
                best_start = left + 1

            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1

            if length > best_length:
                best_length = length
                best_start = left + 1

        return s[best_start : best_length + best_start]
