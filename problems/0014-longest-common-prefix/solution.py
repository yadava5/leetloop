# 14. Longest Common Prefix (Easy) - vertical scan, column by column against strs[0]. O(S) time, O(1) extra space.
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:

        # Any common prefix of the whole list is in particular a prefix of
        # strs[0], so strs[0] can serve as the yardstick: the answer is some
        # reference[:i] and the only question is how large i gets. This is safe
        # without a guard because the constraints promise 1 <= strs.length, so
        # there is always a strs[0] to take. It does NOT need to be the shortest
        # string - a short word elsewhere is handled by the i >= len(word) test
        # below rather than by picking a better reference up front.
        reference = strs[0]

        # Scan VERTICALLY: fix a column i, then check that column across every
        # word, before moving to column i + 1. That ordering is what makes the
        # early return correct - by the time column i is examined, columns
        # 0..i-1 have already been confirmed to match in every word, so the
        # moment column i fails, reference[:i] is known to be the full answer
        # and nothing further needs to be looked at.
        for i in range(len(reference)):
            for word in strs:
                # ORDER INSIDE THE `or` IS LOAD-BEARING: `i >= len(word)` must
                # be tested first. Python short-circuits, so a word shorter than
                # the reference bails out here and word[i] is never evaluated.
                # Flip the two operands and this raises IndexError on input like
                # ["abcd", "abc"] at i == 3.
                #
                # Two different failure modes, one exit: the word ran out of
                # characters, or it has a character here and it disagrees.
                # Either way column i is not shared, so the common prefix is
                # exactly the i columns already cleared.
                if i >= len(word) or word[i] != reference[i]:
                    # reference[:i] EXCLUDES index i, which is the column that
                    # just failed. Off-by-one central: [:i+1] would return the
                    # mismatching character too. At i == 0 this is "", the
                    # correct answer for words sharing nothing.
                    return reference[:i]

        # Falling out of the loop means every column of the reference matched in
        # every word, so the reference is itself a prefix of all of them and is
        # the answer entire. This is also the path taken when strs has a single
        # element, and when reference is the empty string (range(0) is empty).
        return reference
