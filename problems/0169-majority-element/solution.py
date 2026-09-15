# 169. Majority Element (Easy) - Boyer-Moore majority vote: one candidate, one counter, single pass. O(n) time, O(1) space.
class Solution:
    def majorityElement(self, nums: List[int]) -> int:
            
        # WART: this initial assignment is dead. On the very first iteration
        # count is 0, so `candidate = num` immediately overwrites it with the
        # same nums[0]. Harmless, and it does document the intent, but it is
        # not load-bearing - deleting it would not change the result.
        candidate = nums[0]

        count = 0
        for num in nums:
            # A count of 0 means every element seen so far has been cancelled
            # out in pairs, so the prefix examined up to this point has no
            # surviving leader. Restart the vote from the current element.
            if count == 0:
                candidate = num

            # ORDER MATTERS: this `if` is deliberately NOT an `elif` attached
            # to the count == 0 test above. When the counter has just been
            # reset, the current element must also cast its own vote (+1),
            # otherwise a fresh candidate would start at count 0 and be
            # replaced again on the very next element, and the counter could
            # never grow.
            if num == candidate:
                count += 1
            else:
                count -= 1

        # No verification pass is needed because the problem guarantees a
        # majority element exists. Without that guarantee this returns
        # garbage - see Pitfalls.
        return candidate
        
