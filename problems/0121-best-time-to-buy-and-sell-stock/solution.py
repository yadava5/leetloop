# 121. Best Time to Buy and Sell Stock (Easy) - one pass tracking the cheapest day seen so far and the best profit against it. O(n) time, O(1) space.
class Solution:
    def maxProfit(self, prices: list[int]) -> int:

        # NAMING WART worth knowing about: `max_price` does not hold a price.
        # It holds the best PROFIT found so far. `min_price` really is a price.
        # Seeding the profit at 0 is what encodes "you are allowed to not
        # trade at all" - on a strictly falling series nothing ever beats 0,
        # so 0 is returned rather than a negative loss.
        max_price = 0

        # float("inf") so that the very first day is unconditionally cheaper
        # and becomes the buy candidate. A sentinel of 0 would be wrong here
        # (prices can be 0, and nothing would ever go below it).
        min_price = float("inf")

        # Single left-to-right pass. The direction is the whole point: buying
        # must happen before selling, so by only ever comparing `current`
        # against a minimum drawn from STRICTLY EARLIER days, the ordering
        # constraint is enforced for free and never has to be checked.
        for current in prices:

            # Case 1: today is the cheapest day so far, so it becomes the new
            # buy candidate for every future day.
            if current < min_price:
                min_price = current

            # Case 2 (elif, not if): today is not a new minimum, so selling
            # today against the cheapest earlier day is worth checking.
            #
            # The `elif` is safe rather than merely tidy. If the first branch
            # fired then current == min_price afterwards, so the profit this
            # branch would compute is current - current = 0, which can never
            # beat max_price (already >= 0). Skipping it loses nothing.
            # Equally it is NOT an optimisation you may invert: swapping the
            # branches, so the profit check runs first, would let day i sell
            # against itself - still 0, so still harmless here, but only by
            # accident of the >= 0 seed.
            elif current - min_price > max_price:
                max_price = current - min_price

        # 0 if no profitable pair exists, which is the required answer for a
        # series that only ever falls.
        return max_price
