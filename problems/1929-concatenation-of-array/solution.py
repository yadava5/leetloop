# 1929. Concatenation of Array (Easy) - preallocate a 2n array, write each element to its two mirrored slots. O(n) time, O(n) extra space.
class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:

        n = len(nums)
        # Preallocating the full 2n-length answer up front avoids ever growing
        # a list with individual appends, which is why this beats `nums + nums`
        # only in principle - see Why this approach below.
        ans = [0] * 2 * n

        # Each element is written to BOTH halves in the same pass: ans[i] is
        # the first copy, ans[i + n] is the second. One loop instead of two,
        # relying on index arithmetic instead of slicing.
        for i, num in enumerate(nums):
            ans[i] = ans[i + n] = num
        return ans
