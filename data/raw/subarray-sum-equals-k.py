class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        
        seen = {0 : 1}
        
        counting = 0
        total = 0


        for num in nums:
            counting += num

            if counting - k in seen:
                total += seen[counting - k]
            
            if counting not in seen:
                seen[counting] = 0
            seen[counting] += 1
        
        return total
