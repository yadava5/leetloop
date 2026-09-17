# 219. Contains Duplicate II (Easy) - hash map from value to its MOST RECENT index; a repeat within k of that index answers yes. O(n) time, O(n) space.
class Solution:
    def containsNearbyDuplicate(self, nums: list[int], k: int) -> bool:

        # value -> the last index at which that value was seen. Only the last
        # one is kept, and that is sufficient, not a shortcut: for a fixed j,
        # the nearest earlier twin is the one that minimises j - i, so if any
        # earlier occurrence satisfies the distance test, the most recent one
        # does too. Storing a list of all past indices would cost more memory
        # and answer exactly the same question.
        seen = {}

        for i, num in enumerate(nums):

            if num in seen:
                # seen[num] is strictly less than i, so the difference is
                # always positive - which is exactly why k = 0 can never
                # return True, matching the problem's requirement that the
                # two indices be distinct.
                if i - seen[num] <= k:
                    return True
            # NOT an else. A failed distance test must fall through to the
            # update, because a later occurrence may still be close enough to
            # THIS one even though it was too far from the older one.
            # Example: nums = [1, 0, 0, 0, 1], k = 1. At i = 4 the pair of 1s
            # is 4 apart and fails, but the pair of 0s at i = 2 already
            # returned True - and had the array been [1, 2, 1, 1] with k = 1,
            # the i = 2 test fails while i = 3 succeeds only because i = 2
            # overwrote the stored index.
            #
            # The ORDER here is load-bearing: the lookup must happen before
            # the write. Writing first would make `seen[num] == i` and every
            # element would report a distance of 0 <= k.
            seen[num] = i

        # No qualifying pair anywhere in the array.
        return False
