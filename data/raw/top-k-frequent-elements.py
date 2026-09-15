class Solution:
    def topKFrequent(self, nums, k):
        # Step 1: Count frequencies
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1   # easy way to count

        # Step 2: Sort keys by frequency (descending)
        result = sorted(freq, key=freq.get, reverse=True)

        # Step 3: Return top k
        return result[:k]

                
