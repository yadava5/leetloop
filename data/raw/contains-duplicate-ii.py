class Solution:
    def containsNearbyDuplicate(self, nums: list[int], k: int) -> bool:
        
        seen = {}

        for i, num in enumerate(nums):
            
            if num in seen:
                if i - seen[num] <= k:
                    return True
            seen[num] = i

        return False
