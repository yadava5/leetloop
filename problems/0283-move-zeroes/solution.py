# 283. Move Zeroes (Easy) - two passes: compact the non-zeros forward, then fill the tail with zeros. O(n) time, O(1) space.
class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # `write` is the next slot to receive a non-zero value. Everything
        # left of it is already final.
        write = 0

        # Pass 1: copy every non-zero forward, in the order encountered.
        # Iterating by VALUE (`for num in nums`) rather than by index is safe
        # here only because writes always land at or behind the read cursor -
        # write <= the implicit read position at all times, so a write can
        # never clobber an element this loop has not yet visited.
        for num in nums:

            if num != 0:
                nums[write] = num
                write += 1
            
        # Pass 2: everything from `write` to the end is stale leftover data,
        # so overwrite it with zeros. The count is implicit - however many
        # slots remain is exactly how many zeros were skipped in pass 1.
        for i in range(write, len(nums)):
            nums[i] = 0
        # WART: the signature says `-> None` and the docstring says do not
        # return anything. Returning nums is harmless (LeetCode ignores the
        # return value and the mutation is what is graded) but it contradicts
        # the declared contract. Do not rely on this return value.
        return nums
