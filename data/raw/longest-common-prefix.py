class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        
        reference = strs[0]

        for i in range(len(reference)):
            for word in strs:
                if i >= len(word) or word[i] != reference[i]:
                    return reference[:i]

        return reference
