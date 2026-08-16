# 242. Valid Anagram (Easy) - compare the two character multisets with Counter. O(n) time, O(k) space.

# Counter is a dict subclass that maps each distinct element to how many times
# it occurred. Built from a string it is exactly the "letter frequency table"
# this problem is asking about, so the whole solution is one comparison.
from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # An anagram is a reordering, and reordering changes nothing about WHICH
        # characters are present or HOW MANY of each - only their positions. So
        # two strings are anagrams exactly when their frequency tables match.
        # Position information is discarded on purpose; it is the thing the
        # problem says not to care about.
        #
        # Counter equality is multiset equality: same keys, same counts. It also
        # subsumes the length check for free, because if len(s) != len(t) then
        # some character's count must differ (counts sum to the length), so no
        # separate `if len(s) != len(t): return False` guard is needed.
        #
        # Note also that this compares COUNTS, not the set of characters used.
        # set(s) == set(t) would call "aabb" and "abbb" anagrams; Counter does
        # not, because it sees a:2/b:2 against a:1/b:3.
        if Counter(s) == Counter(t):
            return True
        # WART worth knowing: this if/return True/return False is a three-line
        # spelling of `return Counter(s) == Counter(t)`. The comparison is
        # already a bool, so the branch adds nothing but lines. Not a bug and
        # not a slowdown - both Counters are built either way - but the shorter
        # form is what to write next time.
        return False
