# 347. Top K Frequent Elements (Medium) - count into a dict, sort the DISTINCT keys by count descending, slice the first k. O(m log m) time, O(m) space, m = distinct values.
class Solution:
    def topKFrequent(self, nums, k):
        # Step 1: Count frequencies
        # freq maps value -> occurrence count. dict.get(num, 0) supplies the
        # default on first sight, so there is no separate "not in freq" branch.
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1   # easy way to count

        # Step 2: Sort keys by frequency (descending)
        # Iterating a dict yields its KEYS, so sorted() here sorts the m
        # distinct values, not the n input elements - that is why this is
        # O(m log m) and not O(n log n), and why it is fast when the array is
        # long but repetitive.
        #
        # key=freq.get passes each key back through the dict to fetch its
        # count. Python's sort is stable, so equal counts keep first-seen
        # order; that arbitrary tie-break is only safe because the problem
        # guarantees the answer is unique (see Pitfalls).
        result = sorted(freq, key=freq.get, reverse=True)

        # Step 3: Return top k
        # k is guaranteed to be at most the number of distinct values, so this
        # slice always yields exactly k elements and never short-returns.
        return result[:k]

                
