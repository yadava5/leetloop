# 75. Sort Colors (Medium) - Dutch national flag: three pointers partitioning nums into 0s, 1s, 2s in one pass, in place. O(n) time, O(1) space.
class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """

        # i scans forward through the unexamined region; left/right are the
        # boundaries of the growing 0-region (before left) and 2-region
        # (after right). The 1-region is implicitly everything between
        # left and i that i has already passed over.
        i = 0
        left = 0
        right = len(nums) - 1

        while i <= right:

            if nums[i] == 0:
                # Swap the 0 into place at `left` and advance BOTH pointers:
                # the element now at nums[i] (previously at left) is known to
                # be <= 1 already-processed territory, safe to move past.
                nums[i], nums[left] = nums[left], nums[i]
                left += 1
                i += 1

            elif nums[i] == 1:
                # Already in its correct region relative to i; just advance.
                i+= 1

            else:
                # Swap the 2 into place at `right` and advance ONLY `right`,
                # NOT `i` - the element swapped in from the right end hasn't
                # been examined yet, so i must re-check nums[i] next iteration.
                nums[i], nums[right] = nums[right], nums[i]
                right -= 1
