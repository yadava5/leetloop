# 1. Two Sum (Easy) - one pass hash map of value -> index. O(n) time, O(n) space.
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # seen maps a value we have already walked past -> the index it sat at.
        # Only values to the LEFT of the current index ever live in here, which
        # is what makes "found a partner" automatically mean "two distinct
        # indices" without any i != j check.
        seen = {}

        for i, num in enumerate(nums):
            # The exact other number that would complete the pair with num.
            # Searching for a known value in a dict is O(1); searching for
            # "some pair that sums to target" by scanning is O(n).
            comp = target - num

            # ORDER IS LOAD-BEARING: look up comp BEFORE inserting num.
            # If num were inserted first, an element would find itself whenever
            # target == 2 * num. On nums = [5, 3, 7], target = 10 the insert
            # first version returns [0, 0] at i = 0, because the 5 it just
            # stored answers its own lookup - and never reaches the real pair
            # 3 + 7 at indices 1 and 2. Checking first makes that impossible.
            if comp in seen:
                # seen[comp] is the earlier index, i is the current one, so the
                # pair comes back in ascending order. Returning here also means
                # the loop stops at the first valid pair, which the constraints
                # state is safe: "Only one valid answer exists."
                return[seen[comp], i]
            # Insert AFTER the check. A duplicate value overwrites the older
            # index; harmless, because if the older index were part of the
            # answer the loop would already have returned at that point.
            seen[num] = i
        # WART worth knowing: unreachable for any valid LeetCode input, since
        # the constraints guarantee an answer exists. It is here to satisfy the
        # declared -> List[int] return type on the fall-through path. If this
        # ever fires in your own testing, the input violated that guarantee.
        return []
