# 49. Group Anagrams (Medium) - bucket words by their sorted-character canonical form. O(n * k log k) time, O(n * k) space.
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:

        # Maps a canonical form -> the list of original words that reduce to it.
        # A plain dict rather than defaultdict(list) so the missing-key case is
        # handled explicitly a few lines down; see the note there.
        groups = {}

        for word in strs:

            # THE WHOLE ALGORITHM IS THIS LINE. Sorting a word's characters is a
            # canonical form for its anagram class: two words are anagrams
            # exactly when they contain the same characters with the same
            # multiplicities, and sorting maps every arrangement of one multiset
            # to the same sequence. So an O(1) dict lookup replaces the O(n^2)
            # pairwise "is a an anagram of b" comparison.
            #
            # tuple() is NOT decoration. sorted() returns a LIST, and lists are
            # unhashable, so `groups[sorted(word)]` raises TypeError. Any
            # hashable rendering works - "".join(sorted(word)) is the common
            # alternative and produces a string key instead.
            key = tuple(sorted(word))

            # First word of a new anagram class: create its (empty) bucket. This
            # must run BEFORE the append below, which is the only ordering
            # constraint in the function. groups.setdefault(key, []) or a
            # defaultdict(list) collapse these three lines into the append
            # itself; this spelling is longer but shows the branch.
            if key not in groups:
                groups[key] = []

            # Append the ORIGINAL word, never the key. The problem asks for the
            # input strings grouped, not their sorted forms - appending `key`
            # here is a silent wrong answer that still has the right shape.
            groups[key].append(word)

        # The keys were only ever a device for bucketing, so they are discarded.
        # dict preserves insertion order in Python 3.7+, so the groups come back
        # ordered by first appearance and each group is in input order - neither
        # is required by the problem, which accepts any order, but it makes
        # output stable and diffable when testing.
        return list(groups.values())
