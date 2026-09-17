# 167. Two Sum II - Input Array Is Sorted (Medium) - converge two pointers from the ends, moving whichever one the comparison proves useless. O(n) time, O(1) space.
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:

        # The pointers start at the two extremes, so the first sum considered
        # is the largest possible and the last is the smallest. Every move
        # shrinks the range by exactly one element.
        left = 0
        right = len(numbers) - 1

        # `left < right` and not `<=`: an element may not be paired with
        # itself, and at left == right that is the only pair left. The loop
        # therefore runs at most len(numbers) - 1 times, since each pass moves
        # one pointer one step towards the other.
        while left < right:
            current = numbers[left] + numbers[right]

            # The answer is 1-INDEXED, which is the difference from Two Sum I
            # that costs people a wrong answer. Hence the + 1 on both.
            if current == target:
                return [left + 1, right + 1]
            # Sum is short. numbers[left] is the smallest value still in play,
            # and it is already being paired with the LARGEST one available;
            # every remaining partner is <= numbers[right], so no pair using
            # numbers[left] can ever reach the target. Discarding it loses
            # nothing. This elimination argument is the whole proof, and it
            # depends entirely on the array being sorted.
            elif current < target:
                left += 1
            # Symmetrically: the sum is too big, numbers[right] is already
            # paired with the smallest available value, so it cannot appear in
            # any solution either.
            else:
                right -= 1

        # WART worth knowing about: there is no return after the loop, so this
        # function falls off the end and returns None if no pair exists. That
        # is unreachable on LeetCode - the problem guarantees exactly one
        # solution, which is found before the pointers meet - but it means the
        # function is not total, and copying it into code without that
        # guarantee will hand the caller a None to unpack.
