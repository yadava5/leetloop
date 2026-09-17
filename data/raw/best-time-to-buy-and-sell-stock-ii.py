class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        
        total = 0

        for index in range(1, len(prices)):

            rise = prices[index] - prices[index - 1]

            if rise > 0:
                total += rise
        
        return total
