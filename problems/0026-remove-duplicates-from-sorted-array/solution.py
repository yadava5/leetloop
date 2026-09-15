# 26. Remove Duplicates from Sorted Array (Easy) - two pointers: `read` scans, `write` marks the next slot in the deduplicated prefix. O(n) time, O(1) space.
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        
        # Dead branch given the constraints (1 <= nums.length), but harmless.
        # It matters only if this were ever called on an empty list, where
        # `write = 1` below would otherwise claim a prefix of length 1 that
        # does not exist.
        if not nums:
            return 0

        # Start at 1, not 0: nums[0] is always the first element of the answer
        # (a single element cannot be a duplicate of anything before it), so
        # the deduplicated prefix begins life as nums[0:1] and `write` points
        # at the next free slot.
        write = 1

        # `read` starts at 1 for the same reason - index 0 is already settled.
        for read in range(1, len(nums)):

            # Compare against nums[write - 1], the LAST VALUE KEPT, not
            # against nums[read - 1], the previous value seen. On a run of
            # duplicates these two diverge: after [1,1,2] copies nothing for
            # the second 1, nums[write-1] is still 1 while nums[read-1] is
            # also 1 - equal here, but once a copy has happened the written
            # prefix is the only reliable record of what was kept. Since the
            # input is sorted, equal values are adjacent, so one comparison
            # against the last kept value is enough to detect any duplicate.
            if nums[read] != nums[write - 1]:
                nums[write] = nums[read]
                write += 1

        # write is both the next free index and the count of distinct values,
        # which is exactly what the problem asks to return.
        return write
