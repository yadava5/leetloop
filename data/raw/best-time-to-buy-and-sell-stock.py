class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        
        max_price = 0
        min_price = float('inf')

        for current in prices:

            if current < min_price:
                min_price = current

            elif current - min_price > max_price:
                max_price = current - min_price
        
        return max_price
