# 560. Subarray Sum Equals K (Medium) - prefix sums in a hash map, counting how many earlier prefixes make the window hit k. O(n) time, O(n) space.
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:

        # Style wart, left alone because the AST gate forbids editing code:
        # `List` is used bare. LeetCode's preamble does the
        # `from typing import List` for you, so this runs there, but copying
        # this file into a plain script raises NameError on the annotation.
        # The rest of the repo uses the builtin `list[int]` form.

        # Maps a prefix sum to HOW MANY prefixes so far had that sum. The
        # count, not a boolean - several different prefixes can share a sum,
        # and each of them is a distinct subarray start.
        #
        # The {0: 1} seed is the empty prefix, and it is load-bearing: it is
        # what lets a subarray that starts at index 0 be counted. Without it,
        # nums = [3], k = 3 returns 0 instead of 1, because the only prefix
        # that makes the window work is the empty one.
        seen = {0 : 1}

        # `counting` is the running PREFIX SUM, despite the name - it counts
        # nothing. `total` is the actual count and the return value.
        counting = 0
        total = 0

        for num in nums:
            counting += num

            # Every subarray ending here is (prefix up to here) minus (some
            # earlier prefix). Its sum is k exactly when that earlier prefix
            # equals counting - k. So the number of subarrays ending at this
            # index with sum k is the number of earlier prefixes with that
            # value, which is precisely what `seen` stores.
            #
            # Add the STORED COUNT, not 1. On [0, 0, 0] with k = 0 the prefix
            # 0 is reached repeatedly, and `total += 1` returns 3 where the
            # answer is 6.
            if counting - k in seen:
                total += seen[counting - k]

            # ORDER IS LOAD-BEARING: the lookup above happens BEFORE this
            # index's own prefix is recorded. Recording first would let the
            # current prefix match itself whenever k == 0, counting the empty
            # subarray once per index - [1, 2, 3] with k = 0 would return 3
            # instead of 0. The read-then-write order is what keeps "earlier
            # prefix" strictly earlier.
            if counting not in seen:
                seen[counting] = 0
            seen[counting] += 1

        return total
