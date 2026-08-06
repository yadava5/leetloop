# 20. Valid Parentheses - Easy - stack, O(n) time / O(n) space.
#
# GENERATED. This is data/raw/valid-parentheses.py with comments added and
# nothing else changed; scripts/verify_ast.py proves that by comparing ASTs.
class Solution:
    def isValid(self, s: str) -> bool:
        # Holds every opener that is still waiting to be closed. A stack is the
        # right structure because "most recently opened" is exactly what a
        # closing bracket has to match.
        stack = []

        # closer -> the opener it demands. Keying by the closer means `char in
        # map` doubles as the test "is this a closing bracket?".
        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            if char in map:
                # A closer. The opener it must match is whatever is on top.
                if stack:
                    top_element = stack.pop()
                else:
                    # Nothing is open, so this closer can't be matched. The
                    # sentinel loses the comparison below, which avoids both an
                    # IndexError and an early-return special case.
                    top_element = "#"

                # Right kind of bracket in the wrong place, or none at all.
                if map[char] != top_element:
                    return False
            else:
                # Not a closer, so by the problem's alphabet it is an opener:
                # record it as now-open.
                stack.append(char)

        # Everything matched, but trailing openers like "(((" leave the stack
        # non-empty - only an empty stack means well-formed.
        return not stack
