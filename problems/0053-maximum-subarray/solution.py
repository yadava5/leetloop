# 53. Maximum Subarray (Medium) - Kadane: one pass carrying the best sum ending at the current index. O(n) time, O(1) space.
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:

        # Two different quantities, and confusing them is the whole problem:
        #
        #   `best`    - the largest sum of ANY subarray seen so far. This is
        #               the answer.
        #   `current` - the largest sum of a subarray that ENDS EXACTLY at the
        #               index being visited. Not the answer, the state.
        #
        # Both start at nums[0] rather than at 0, and that is load-bearing.
        # Every subarray is non-empty, so on an all-negative input the answer
        # is negative; seeding `best` with 0 returns 0 on [-5, -2, -9] where
        # the answer is -2. nums[0] is safe to read because the constraints
        # promise 1 <= nums.length.
        best = nums[0]
        current = nums[0]

        # Index 0 is already folded into the two seeds above, so the scan
        # starts at 1. Starting at 0 would count nums[0] twice - `current`
        # would become nums[0] + nums[0] on the first step.
        for i in range(1, len(nums)):
            value = nums[i]

            # The single decision Kadane makes, once per element: does the
            # subarray ending here START here, or does it EXTEND the one that
            # ended at i-1?
            #
            # Note the test is on `current`, the running sum, NOT on `value`.
            # A negative element is no reason to restart - on [4, -1, 4] the
            # right answer crosses the -1 and totals 7, while a rule that
            # restarted on every negative element returns 4. What makes a
            # prefix worth dropping is that the prefix itself sums to
            # something negative, i.e. it would cost more than it contributes.
            if current < 0:
                current = value

            else:
                current = current + value

            # The boundary case current == 0 takes this else branch and gives
            # current + value == value, which is exactly what the if branch
            # would have produced. So `< 0` and `<= 0` behave identically here
            # and neither is a bug; nothing hinges on which was written.

            # Fold into the running maximum AFTER `current` has been updated
            # for this index. Comparing first would measure the window ending
            # at i-1 against itself and miss the one ending at i entirely.
            if current > best:
                best = current

        return best
