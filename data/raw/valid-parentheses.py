class Solution:
    def isValid(self, s: str) -> bool:
        stack = []

        map = {
            ")" : "(",
            "}" : "{",
            "]" : "["
        }

        for char in s:
            if char in map:
                if stack:
                    top_element = stack.pop()
                else:
                    top_element = "#"
                if map[char] != top_element:
                    return False
            else:
                stack.append(char)
        return not stack
