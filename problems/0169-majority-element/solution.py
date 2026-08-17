# 169. Majority Element (Easy) - Boyer-Moore majority vote, one pass, no counting table. O(n) time, O(1) space.
class Solution:
    def majorityElement(self, nums: List[int]) -> int:

        # count is NOT "how many times candidate has been seen". It is the size
        # of candidate's surviving lead: how many copies of candidate are left
        # over after every element seen so far has been paired off against a
        # DIFFERENT element and both thrown away. That reading is the whole
        # algorithm, and it is why a single integer can stand in for a frequency
        # table of up to 5 * 10^4 distinct values.
        count = 0
        # None is a safe initial candidate precisely because it can never equal
        # an int, so the first iteration is forced through the count == 0 branch
        # below. It is also what would be returned for an empty array - not a
        # case the constraints allow (1 <= n), and not a case this code defends.
        candidate = None

        for num in nums:
            # Lead exhausted: everything seen so far has cancelled out exactly,
            # so the prefix is irrelevant and the election restarts from here.
            # ORDER IS LOAD-BEARING - this reassignment must happen BEFORE the
            # comparison below, not after. Adopting num as the candidate first
            # means the very same num then votes for itself and count goes
            # 0 -> 1. Move this block after the vote and num would be compared
            # against the OLD candidate, count would go to -1, and the state
            # stops meaning anything.
            if count == 0:
                candidate = num

            # A matching element reinforces the lead...
            if num == candidate:
                count += 1

            # ...and a differing one cancels one copy of it. Note this is the
            # only place count decreases, and it never goes below zero, because
            # count == 0 was intercepted above and turned into a match.
            else:
                count -= 1

        # Whatever is holding the floor at the end. This is correct ONLY because
        # the problem guarantees a majority element exists: the survivor of the
        # cancellation is the majority element if there is one, but on input
        # with no majority it is an arbitrary element rather than a signal.
        # Without that guarantee this needs a second pass counting occurrences
        # of candidate and checking > n // 2.
        return candidate
