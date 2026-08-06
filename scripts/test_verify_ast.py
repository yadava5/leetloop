#!/usr/bin/env python3
"""Tests for the gate — asserted in BOTH directions.

A gate that only ever passes is not a gate. Every case below states the
expected verdict, and the suite fails if the gate disagrees, including when it
is wrongly permissive.

Run: /usr/bin/python3 scripts/test_verify_ast.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_ast import GateFailure, compare  # noqa: E402

# Ayush's real Two Sum submission, byte for byte - including `return[...]`
# with no space, which the annotator is forbidden from tidying up.
RAW = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}

        for i, num in enumerate(nums):
            comp = target - num

            if comp in seen:
                return[seen[comp], i]
            seen[num] = i
        return []
'''

# --- must PASS: comments and blank lines only -----------------------------
ANNOTATED_OK = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # value -> index for everything walked so far
        seen = {}

        for i, num in enumerate(nums):
            # the partner this element needs in order to hit `target`
            comp = target - num

            # seen before? then its index is the other half of the answer
            if comp in seen:
                return[seen[comp], i]

            # record AFTER the lookup, so an element can't pair with itself
            seen[num] = i

        return []
'''

# --- must PASS: comment on every line, weird indentation of comments ------
ANNOTATED_DENSE = '''# hash-map one-pass
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}  # trailing comment

        for i, num in enumerate(nums):
                # over-indented comment is still just a comment
            comp = target - num

            if comp in seen:
                return[seen[comp], i]
            seen[num] = i
        return []
# trailing comment at end of file
'''

# --- must FAIL: one renamed variable (seen -> cache) ----------------------
RENAMED = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        cache = {}

        for i, num in enumerate(nums):
            comp = target - num

            if comp in cache:
                return[cache[comp], i]
            cache[num] = i
        return []
'''

# --- must FAIL: a docstring is an AST node, not a comment -----------------
DOCSTRING_ADDED = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """One-pass hash map."""
        seen = {}

        for i, num in enumerate(nums):
            comp = target - num

            if comp in seen:
                return[seen[comp], i]
            seen[num] = i
        return []
'''

# --- must FAIL: two statements swapped (the classic self-pairing bug) -----
REORDERED = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}

        for i, num in enumerate(nums):
            comp = target - num

            seen[num] = i
            if comp in seen:
                return[seen[comp], i]
        return []
'''

# --- must FAIL: "helpfully" tidied formatting that changes the tree -------
STYLE_FIX = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}

        for i, num in enumerate(nums):
            comp = target - num

            if comp in seen:
                return [seen[comp], i]
            seen[num] = i
        return None
'''

# --- must FAIL: does not parse -------------------------------------------
BROKEN = '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]
        seen = {}
'''

CASES = [
    ("comments and blank lines only", ANNOTATED_OK, True),
    ("comment on nearly every line", ANNOTATED_DENSE, True),
    ("identical file", RAW, True),
    ("one renamed variable (seen -> cache)", RENAMED, False),
    ("docstring added", DOCSTRING_ADDED, False),
    ("two statements reordered", REORDERED, False),
    ("return [] changed to return None", STYLE_FIX, False),
    ("annotated file does not parse", BROKEN, False),
]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="gate-test-"))
    raw = tmp / "raw.py"
    raw.write_text(RAW, encoding="utf-8")

    problems = 0
    print("gate self-test  (temp dir %s)\n" % tmp)
    for name, source, should_pass in CASES:
        candidate = tmp / "candidate.py"
        candidate.write_text(source, encoding="utf-8")
        try:
            compare(raw, candidate)
            passed = True
            detail = ""
        except GateFailure as exc:
            passed = False
            detail = str(exc).splitlines()[0]

        want = "PASS" if should_pass else "FAIL"
        got = "PASS" if passed else "FAIL"
        ok = passed == should_pass
        if not ok:
            problems += 1
        print(
            "  [%s] gate said %s, expected %s   %s"
            % ("ok" if ok else "BUG", got, want, name)
        )
        if not ok:
            print("        ^ the gate is wrong here%s" % (": " + detail if detail else ""))

    # A gate that never rejects anything is useless even if every case above
    # happened to line up, so assert the two directions explicitly.
    rejected = sum(1 for _, _, should_pass in CASES if not should_pass)
    accepted = len(CASES) - rejected
    print(
        "\n%d case(s): %d must pass, %d must fail. %d disagreement(s)."
        % (len(CASES), accepted, rejected, problems)
    )
    if problems:
        print("GATE IS BROKEN - do not commit annotations until this is green")
        return 1
    print("gate behaves correctly in both directions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
