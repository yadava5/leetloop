# 20. Valid Parentheses (Easy) - single left-to-right pass with an explicit stack
# of unmatched openers; O(n) time, O(n) space. My submission, comments only.

class Solution:
    def isValid(self, s: str) -> bool:
        # The stack holds every opener seen so far that is still waiting to be
        # closed, most recent on top. "Closed in the right order" is exactly
        # last-in-first-out, which is why a stack - and nothing simpler, like
        # three counters - is the right structure here.
        stack = []

        # closer -> the opener it must be matched against. Note this dict is
        # doing double duty: `char in map` is also the test for "is this a
        # closing bracket?", which is what makes the loop below a clean
        # two-way branch with no separate set of openers to maintain.
        #
        # WART: `map` shadows the builtin `map()`. Harmless inside this method
        # because the builtin is never used, but it is a habit worth dropping;
        # `pairs` or `closer_to_opener` would say more and shadow nothing.
        # Preserved exactly as submitted - the AST gate would reject a rename.
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            if char in map:
                # A closer. Whatever it closes must be sitting on top of the
                # stack right now; anything else means the nesting is wrong.
                if stack:
                    top_element = stack.pop()
                else:
                    # Sentinel for "there is nothing to match against", i.e. a
                    # closer with no opener at all, like ")(" or "]". Using a
                    # character that can never be a legal opener collapses the
                    # empty-stack case into the same comparison as the normal
                    # case, so there is only one `return False` to reason about.
                    top_element = "#"
                if map[char] != top_element:
                    # Wrong type ("(]"), or nothing left to close (")"). Either
                    # way the string is already unsalvageable - no later
                    # character can repair a mismatch, so returning here is
                    # safe as well as fast.
                    return False
            else:
                # Not a closer, so under this problem's alphabet it is an
                # opener: push it and wait. The pop above is unconditional once
                # a closer arrives, so an opener that is never closed simply
                # survives to the end - which is what the final check catches.
                #
                # WART: this branch pushes ANY non-closing character, not just
                # the three openers. Correct here only because the constraints
                # promise s contains bracket characters and nothing else. Feed
                # it "a" and it happily pushes it and reports False.
                stack.append(char)
        # Every closer matched, but leftovers mean unclosed openers ("(("), so
        # the string is valid only if the stack drained completely. Forgetting
        # this line and returning True is the classic wrong answer: it passes
        # every balanced test and every mismatched one, and fails only on
        # prefixes that are still open.
        return not stack
