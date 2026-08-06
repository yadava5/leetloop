# 20. Valid Parentheses (Easy) - stack of unmatched openers. O(n) time, O(n) space.
class Solution:
    def isValid(self, s: str) -> bool:
        # Holds every opening bracket seen so far that is still unmatched.
        # A stack is the right shape because brackets must close in reverse
        # order of opening: the most recent opener is always the one that has
        # to be closed next.
        stack = []

        # WART worth knowing: `map` shadows the Python builtin inside this
        # method. Harmless here since the builtin is never used, but it is the
        # kind of habit that bites in a longer function.
        # Keyed by CLOSER -> its matching opener, not the other way round. That
        # direction is what lets `char in map` below act as the "is this a
        # closing bracket?" test in the same lookup structure.
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            # Membership in map means char is a closer, because only closers
            # are keys. The problem guarantees s contains nothing but the six
            # bracket characters, so "not a closer" safely means "an opener".
            if char in map:
                if stack:
                    top_element = stack.pop()
                else:
                    # Empty stack means this closer has no opener at all, e.g.
                    # "()]" or a leading ")". "#" is a sentinel that can never
                    # equal any value in map, so the comparison below fails and
                    # we return False without needing a separate branch.
                    top_element = "#"
                # The popped opener must be the partner of THIS closer.
                # Mismatch means crossed brackets like "([)]" - each type is
                # individually balanced, but the nesting is wrong, which is
                # exactly the case a counter-per-bracket-type approach misses.
                if map[char] != top_element:
                    return False
            else:
                # An opener: park it until its closer shows up.
                stack.append(char)
        # Falling out of the loop only means nothing mismatched. Leftover
        # openers like "(((" are still invalid, so the answer is "the stack
        # drained completely", not plain True.
        return not stack
