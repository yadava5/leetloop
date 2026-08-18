class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """

        i = 0
        left = 0
        right = len(nums) - 1

        while i <= right:

            if nums[i] == 0:
                nums[i], nums[left] = nums[left], nums[i]
                left += 1
                i += 1

            elif nums[i] == 1:
                i+= 1
            
            else:
                nums[i], nums[right] = nums[right], nums[i]
                right -= 1
            
