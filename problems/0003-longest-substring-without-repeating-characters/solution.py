# 3. Longest Substring Without Repeating Characters (Medium) - sliding window whose left edge jumps past the previous copy of a repeated character. O(n) time, O(min(n, alphabet)) space.
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # Reachable, unlike most such guards: the constraints allow
        # s.length == 0. Strictly it is redundant anyway - the loop body would
        # never run and max_length would already be 0 - but it is honest here.
        if not s:
            return 0

        # character -> the LAST index at which it appeared. Not a set and not
        # a count: the index is what allows the left edge to jump straight to
        # the right place instead of crawling one step at a time.
        seen = {}

        # Left edge of the window, inclusive. The window is s[start .. index].
        start = 0

        max_length = 0

        for index, character in enumerate(s):

            # THE line that makes this correct. `character in seen` alone is
            # not enough - `seen` is never pruned, so it still remembers
            # characters that have already fallen out of the window to the
            # left of `start`. Acting on those would drag `start` BACKWARDS
            # and produce a window containing a duplicate.
            #
            # Concretely on "abba": at index 3 the stored index of 'a' is 0,
            # but start is already 2. Without `seen[character] >= start` the
            # left edge would be reset to 1, the window would become "bba",
            # and the answer would come back 3 instead of 2.
            #
            # Because start only ever moves right, the window is always
            # duplicate-free, and this is the step that guarantees it.
            if character in seen and seen[character] >= start:
                start = seen[character] + 1
            # Must come AFTER the test above, otherwise the character would be
            # found at its own index and the window would collapse every step.
            seen[character] = index

            # Inclusive on both ends, hence the + 1.
            current_length = index - start + 1

            # Measured on every iteration rather than only when the window
            # shrinks, because the longest window may well be the final one.
            max_length = max(max_length, current_length)

        return max_length
