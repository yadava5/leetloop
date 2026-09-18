# 122. Best Time to Buy and Sell Stock II (Medium) - greedy: bank every upward day-to-day move. O(n) time, O(1) space.
class Solution:
    def maxProfit(self, prices: list[int]) -> int:

        # The running answer. Seeded at 0, which is also the correct answer for
        # a single-day array and for any series that never rises - you are
        # allowed to make no trades at all, so the result is never negative.
        total = 0

        # Start at 1, not 0. Every iteration looks BACKWARDS at index - 1, so
        # index 0 has no partner and must be skipped. Starting at 0 would read
        # prices[-1], which in Python is the LAST element rather than an error:
        # a silent wrong answer, not a crash. That is the load-bearing detail
        # in this line.
        for index in range(1, len(prices)):

            # The change in price from yesterday to today. Note the direction:
            # today minus yesterday. Reversing it flips the sign of every term
            # and the function returns 0 on every rising series.
            rise = prices[index] - prices[index - 1]

            # Keep only the up days. A day where the price falls or stays flat
            # contributes nothing, because you simply hold no shares over it.
            #
            # Why this is allowed to be this crude: buying and selling on the
            # same day is permitted, so a real trade held from day i to day j
            # can be split into j - i one-day trades with the identical total
            # profit. Summing the positive one-day moves therefore reaches the
            # optimum, and no bookkeeping of "am I currently holding?" is
            # needed. That equivalence is the entire proof.
            if rise > 0:
                total += rise

        return total
