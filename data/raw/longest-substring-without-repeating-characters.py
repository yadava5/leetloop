class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if not s:
            return 0

        seen = {}

        start = 0

        max_length = 0

        for index, character in enumerate(s):

            if character in seen and seen[character] >= start:
                start = seen[character] + 1
            seen[character] = index

            current_length = index - start + 1

            max_length = max(max_length, current_length)

        return max_length
        
