# 1. Two Sum - Easy - one-pass hash map, O(n) time / O(n) space.
#
# GENERATED. This is data/raw/two-sum.py with comments added and nothing else
# changed; scripts/verify_ast.py proves that by comparing ASTs.
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # value -> the index it was last seen at, covering only elements
        # strictly to the LEFT of the current one. That invariant is the whole
        # correctness argument: anything found in here is a different element,
        # never i itself.
        seen = {}

        for i, num in enumerate(nums):
            # The partner nums[i] would need. Computing it turns "search for a
            # pair" into "have I already passed this exact value?" - a question
            # a dict answers in O(1) instead of an inner loop.
            comp = target - num

            if comp in seen:
                # seen[comp] is strictly less than i, so the two indices are
                # distinct, which the problem requires. (No space after
                # `return`: this is `return [a, b]`, a list literal, not an
                # index expression. Preserved exactly as submitted.)
                return[seen[comp], i]
            # ORDER IS LOAD-BEARING: record num only AFTER the lookup above.
            # Insert first and nums = [4, 1, 7] with target 8 matches the 4
            # against itself and answers [0, 0].
            seen[num] = i
        # Unreachable given the problem's promise that exactly one pair exists;
        # a defensive fallback so every path returns a list.
        return []
