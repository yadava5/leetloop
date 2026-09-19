# 904. Fruit Into Baskets (Medium) - longest window holding at most 2 distinct values, via a sliding window with a count map. O(n) time, O(1) space.
class Solution:
    def totalFruit(self, fruits: list[int]) -> int:

        # Two baskets, one fruit type each. The problem is "longest subarray
        # with at most k distinct values" with k pinned to 2; the general
        # version is left in as a named constant rather than a literal, which
        # is why the code reads like the k-distinct template.
        k = 2

        # Both halves of this guard are dead on LeetCode: k is literally 2, so
        # `k == 0` is never true, and the constraints promise
        # 1 <= fruits.length, so `not fruits` is never true either. It is the
        # generic template's guard, harmless, and kept as written.
        if k == 0 or not fruits:
            return 0

        # fruit type -> how many of it are inside the current window. Only
        # types actually present are keys, so len(basket) IS the number of
        # distinct types in the window. That equality is what the while loop
        # below tests, and it is maintained by the `del` further down.
        basket = {}

        best_total = 0
        left = 0

        # `right` is the inclusive right end of the window. It only ever moves
        # forward, and so does `left` - which is why the nested while does not
        # make this quadratic.
        for right, fruit in enumerate(fruits):

            # Admit the new tree first. The window is briefly INVALID here
            # (it may now hold 3 types); the while loop immediately repairs it
            # before anything is measured.
            if fruit not in basket:
                basket[fruit] = 0
            basket[fruit] += 1

            # Shrink from the left until at most k types remain. One tree at a
            # time, re-testing each round, so it stops at the very first
            # position that makes the window legal again - giving the LONGEST
            # valid window ending at `right`, not merely a valid one.
            while len(basket) > k:
                basket[fruits[left]] -= 1

                # Deleting the key at zero is what keeps len(basket) equal to
                # the distinct count. Decrementing without deleting leaves a
                # dead key behind, len(basket) never falls back to k, and the
                # loop keeps advancing `left` past the end of the array: on
                # [1, 2, 3, 3, 3] it walks off and raises IndexError rather
                # than returning a wrong answer.
                if basket[fruits[left]] == 0:
                    del basket[fruits[left]]
                left += 1

            # Measured only AFTER the repair, never before. Measuring between
            # the insert and the while loop scores an illegal 3-type window:
            # on [1, 2, 1, 2, 3] that reports 5 where the answer is 4.
            current_length = right - left + 1

            if best_total < current_length:
                # Style wart: the guard has already established that
                # current_length is the larger of the two, so max() here is
                # redundant - `best_total = current_length` does the same
                # thing. Harmless, and not mine to edit.
                best_total = max(best_total, current_length)

        return best_total
