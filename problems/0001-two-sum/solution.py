# 1. Two Sum - Easy - one-pass hash map, O(n) time / O(n) space.
#
# GENERATED. This is data/raw/two-sum.py with comments added and nothing else
# changed; scripts/verify_ast.py proves that by comparing both files' ASTs.
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # value -> index, for every element walked so far. The whole trick is
        # storing values as keys: the question "is the partner I need already
        # behind me?" becomes a dict lookup instead of a scan.
        seen = {}

        for i, num in enumerate(nums):
            # The exact value that would complete the pair with `num`.
            comp = target - num

            # Look BEFORE inserting. If this ran after the insert below, an
            # element would find itself whenever target == 2 * num.
            if comp in seen:
                # seen[comp] is the earlier index, i is the current one.
                return[seen[comp], i]

            # Not a match, so remember this element for later elements to find.
            # A duplicate value overwrites the older index, which is safe here:
            # the problem guarantees exactly one valid answer.
            seen[num] = i

        # Unreachable given that guarantee, but it keeps the declared
        # List[int] return type honest.
        return []
