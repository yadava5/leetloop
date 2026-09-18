class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        

        best = nums[0]
        current = nums[0]


        for i in range(1, len(nums)):
            value = nums[i]

            if current < 0:
                current = value

            else:
                current = current + value
            
            if current > best:
                best = current
        
        return best
