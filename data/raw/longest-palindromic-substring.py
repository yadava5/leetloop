class Solution:
    def longestPalindrome(self, s: str) -> str:
        
        if not s:
            return ""

        best_string = 1
        best_start = 0

        for centre in range(len(s)):
            left = centre
            right = centre

            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1

                current_string = right - left - 1

                if current_string > best_string:
                    best_string = current_string

                    best_start = left + 1
            

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
