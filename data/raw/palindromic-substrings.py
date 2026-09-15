class Solution:
    def countSubstrings(self, s: str) -> int:
        if not s:
            return 0


        total = 0

        for centre in range(len(s)):

            left = centre
            right = centre

            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1

                left -= 1
                right += 1

            left = centre
            right = centre + 1

            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1

                left -= 1
                right += 1

        return total
            
