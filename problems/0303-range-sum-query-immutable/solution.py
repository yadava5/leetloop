# 303. Range Sum Query - Immutable (Easy) - precompute a prefix-sum array once, answer each query by subtracting two entries. O(n) build, O(1) per query.
class NumArray:

    def __init__(self, nums: List[int]):

        # prefix[i] holds the sum of the first i elements, so prefix[0] = 0
        # for the empty prefix. That leading zero is what makes the query
        # formula below need no special case for left == 0.
        self.prefix = [0]

        # Each entry is the previous running total plus the current element,
        # so this builds all n + 1 prefix sums in a single pass.
        for num in nums:
            self.prefix.append(self.prefix[-1] + num)


    def sumRange(self, left: int, right: int) -> int:
        
        # sum(nums[left..right]) inclusive = (sum of first right+1 elements)
        # - (sum of first left elements). The +1 is because `right` is an
        # inclusive index but prefix is indexed by COUNT, so the element at
        # `right` must be included in the larger term.
        return (self.prefix[right + 1] - self.prefix[left])



# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# param_1 = obj.sumRange(left,right)
