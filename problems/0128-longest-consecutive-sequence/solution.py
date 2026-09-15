# 128. Longest Consecutive Sequence (Medium) - hash set, walk each run only from its smallest element. O(n) time, O(n) space.
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        
        # nums.length may be 0, and max() over no streaks would never run,
        # leaving longest_streak at 0 anyway - but the guard also protects
        # against nothing else here, so it is really just an early exit.
        if not nums:
            return 0

        longest_streak = 0

        # The set does two jobs: O(1) membership tests, and deduplication.
        # Deduplication is what makes the outer loop touch each DISTINCT value
        # once rather than once per copy.
        num_set = set(nums)

        # ORDER MATTERS: iterate over num_set, not nums. Iterating the raw
        # list would redo the same walk once per duplicate copy of a run's
        # start value.
        for num in num_set:

            # This is the whole algorithm. Only start counting from a value
            # that has no left neighbour - i.e. the SMALLEST element of its
            # run. Every other member of the run fails this test and costs
            # O(1). Without it, a run of length L would be walked from all L
            # of its members, making the whole thing O(n^2) on input like
            # [1..100000].
            if (num - 1) not in num_set:

                current_num = num
                current_streak = 1

                # Walk right until the run breaks. Each iteration consumes one
                # element of THIS run, and runs are disjoint, so across the
                # entire outer loop this inner loop runs at most n times in
                # total - that is why two nested loops still add up to O(n).
                while (current_num + 1) in num_set:

                    current_num += 1
                    current_streak += 1
                
                # Only reached at the end of a complete run, so current_streak
                # is that run's full length.
                longest_streak = max(longest_streak, current_streak)    
        
        return longest_streak
