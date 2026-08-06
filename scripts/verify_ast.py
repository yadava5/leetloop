#!/usr/bin/env python3
"""The gate.

Proves that an annotated solution differs from the submitted code by comments
and whitespace ONLY. Nothing else in this repo is allowed to claim that; this
is the thing that establishes it.

How it works: Python's parser discards comments and blank lines entirely, so
they cannot appear in an AST. If

    ast.dump(ast.parse(raw)) == ast.dump(ast.parse(annotated))

then the two files describe the identical program, and every difference between
their bytes is a comment or whitespace. A renamed variable, a reordered
statement, a changed literal, an added docstring (docstrings ARE AST nodes) or a
"helpful" bug fix all change the dump and are rejected.

`include_attributes` is deliberately left False: line and column numbers move
when comments are inserted, and including them would make every annotation fail.
Field names ARE included (`annotate_fields=True`) so that structurally similar
but semantically different trees cannot collide.

WHAT GETS CHECKED
    problems/<n>-<slug>/solution.py         the annotated file
    problems/<n>-<slug>/README.md           every ```python fence in it that
                                            contains "class Solution"

The README is checked too because each problem page shows the full solution
inline for reading in one place, and a copy that isn't gated is a copy that can
drift. Illustrative fragments must therefore use inline code or a non-`python`
fence; a ```python fence containing `class Solution` is treated as a claim that
this is the real submission, and is verified as one.

Usage:
    verify_ast.py <raw.py> <annotated.py|README.md>   compare one pair
    verify_ast.py --all                               compare every pair

Exit status: 0 = everything passed. 1 = at least one failure. 2 = bad usage.

No third-party dependencies, by design: this must run identically in the
GitHub Action, in the cloud routine, and on a laptop.
"""

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW_DIR = REPO / "data" / "raw"
PROBLEMS_DIR = REPO / "problems"

FENCE_RE = re.compile(r"^```python[ \t]*\r?\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FULL_SOLUTION_MARKER = "class Solution"


class GateFailure(Exception):
    """Raised when something is not comments-only equivalent to the submission."""


def dump_source(source: str, label: str) -> str:
    """AST dump of `source`, or raise GateFailure describing why it won't parse."""
    try:
        tree = ast.parse(source, filename=label)
    except SyntaxError as exc:
        raise GateFailure(
            "%s does not parse as Python: line %s: %s" % (label, exc.lineno, exc.msg)
        ) from exc
    return ast.dump(tree, annotate_fields=True, include_attributes=False)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateFailure("cannot read %s: %s" % (path, exc)) from exc


def normalized_dump(path: Path) -> str:
    return dump_source(read_text(path), str(path))


def first_divergence(a: str, b: str, window: int = 90) -> str:
    """Human-readable pointer at where two dumps start to differ."""
    limit = min(len(a), len(b))
    i = 0
    while i < limit and a[i] == b[i]:
        i += 1
    start = max(0, i - window // 2)
    return (
        "  first divergence at character %d of the AST dump\n"
        "    raw       ...%s...\n"
        "    annotated ...%s..." % (i, a[start : i + window], b[start : i + window])
    )


def compare(raw: Path, annotated: Path) -> None:
    """Raise GateFailure unless the two FILES are comments-only equivalent."""
    raw_dump = normalized_dump(raw)
    ann_dump = normalized_dump(annotated)
    if raw_dump != ann_dump:
        raise GateFailure(
            "AST mismatch: %s is not %s plus comments\n%s"
            % (annotated, raw, first_divergence(raw_dump, ann_dump))
        )


def solution_blocks(markdown_path: Path):
    """Every ```python fence in a README that claims to be the full solution."""
    if not markdown_path.exists():
        return []
    text = read_text(markdown_path)
    found = []
    for ordinal, match in enumerate(FENCE_RE.finditer(text), start=1):
        code = match.group(1)
        if FULL_SOLUTION_MARKER in code:
            found.append((ordinal, code))
    return found


def compare_markdown(raw: Path, markdown_path: Path) -> int:
    """Gate every full-solution fence in a README. Returns the failure count."""
    blocks = solution_blocks(markdown_path)
    if not blocks:
        print(
            "WARN  %s\n  no ```python fence containing `class Solution` — the page does"
            "\n  not show the solution inline, so nothing to verify there" % markdown_path
        )
        return 0

    raw_dump = normalized_dump(raw)
    failures = 0
    for ordinal, code in blocks:
        label = "%s (```python block %d)" % (markdown_path, ordinal)
        try:
            block_dump = dump_source(code, label)
        except GateFailure as exc:
            print("FAIL  %s\n  %s" % (label, exc))
            failures += 1
            continue
        if block_dump != raw_dump:
            print(
                "FAIL  %s\n  inline solution is not %s plus comments\n%s"
                % (label, raw, first_divergence(raw_dump, block_dump))
            )
            failures += 1
        else:
            print("PASS  %s  (comments-only vs %s)" % (label, raw.name))
    return failures


def discover_pairs() -> list:
    """Every (raw, problem directory) pair the repo currently contains."""
    pairs = []
    if not PROBLEMS_DIR.is_dir():
        return pairs
    for solution in sorted(PROBLEMS_DIR.glob("*/solution.py")):
        folder = solution.parent.name
        slug = folder.split("-", 1)[1] if "-" in folder else folder
        pairs.append((RAW_DIR / ("%s.py" % slug), solution))
    return pairs


def main(argv: list) -> int:
    if len(argv) == 2 and argv[1] == "--all":
        pairs = discover_pairs()
        if not pairs:
            print("gate: no annotated solutions found yet - nothing to check")
            return 0
        check_readmes = True
    elif len(argv) == 3:
        pairs = [(Path(argv[1]), Path(argv[2]))]
        check_readmes = False
    else:
        print(__doc__.strip())
        return 2

    failures = 0
    checks = 0

    for raw, annotated in pairs:
        if not raw.exists():
            print("FAIL  %s\n  missing reference copy %s" % (annotated, raw))
            failures += 1
            checks += 1
            continue

        if annotated.suffix == ".md":
            blocks = solution_blocks(annotated)
            checks += max(len(blocks), 1)
            failures += compare_markdown(raw, annotated)
            continue

        checks += 1
        try:
            compare(raw, annotated)
        except GateFailure as exc:
            print("FAIL  %s\n%s" % (annotated, exc))
            failures += 1
        else:
            print("PASS  %s  (comments-only vs %s)" % (annotated, raw.name))

        if check_readmes:
            readme = annotated.parent / "README.md"
            blocks = solution_blocks(readme)
            checks += max(len(blocks), 1) if readme.exists() else 0
            if readme.exists():
                failures += compare_markdown(raw, readme)

    print("\ngate: %d passed, %d failed, %d checked" % (checks - failures, failures, checks))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
