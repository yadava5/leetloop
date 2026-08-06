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

Usage:
    verify_ast.py <raw.py> <annotated.py>     compare one pair
    verify_ast.py --all                       compare every pair in the repo

Exit status: 0 = every pair passed. 1 = at least one pair failed. 2 = bad usage.

No third-party dependencies, by design: this must run identically in the
GitHub Action, in the cloud routine, and on a laptop.
"""

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW_DIR = REPO / "data" / "raw"
PROBLEMS_DIR = REPO / "problems"


class GateFailure(Exception):
    """Raised when a pair is not comments-only equivalent."""


def normalized_dump(path: Path) -> str:
    """Parse `path` and return its AST dump, or raise GateFailure."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateFailure("cannot read %s: %s" % (path, exc)) from exc
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise GateFailure(
            "%s does not parse as Python: line %s: %s" % (path, exc.lineno, exc.msg)
        ) from exc
    return ast.dump(tree, annotate_fields=True, include_attributes=False)


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
    """Raise GateFailure unless the two files are comments-only equivalent."""
    raw_dump = normalized_dump(raw)
    ann_dump = normalized_dump(annotated)
    if raw_dump != ann_dump:
        raise GateFailure(
            "AST mismatch: %s is not %s plus comments\n%s"
            % (annotated, raw, first_divergence(raw_dump, ann_dump))
        )


def discover_pairs() -> list:
    """Every (raw, annotated) pair the repo currently contains."""
    pairs = []
    if not PROBLEMS_DIR.is_dir():
        return pairs
    for solution in sorted(PROBLEMS_DIR.glob("*/solution.py")):
        # problems/0001-two-sum/solution.py -> slug "two-sum"
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
    elif len(argv) == 3:
        pairs = [(Path(argv[1]), Path(argv[2]))]
    else:
        print(__doc__.strip())
        return 2

    failures = 0
    for raw, annotated in pairs:
        if not raw.exists():
            print("FAIL  %s\n  missing reference copy %s" % (annotated, raw))
            failures += 1
            continue
        try:
            compare(raw, annotated)
        except GateFailure as exc:
            print("FAIL  %s\n%s" % (annotated, exc))
            failures += 1
        else:
            print("PASS  %s  (comments-only vs %s)" % (annotated, raw.name))

    print(
        "\ngate: %d passed, %d failed, %d checked"
        % (len(pairs) - failures, failures, len(pairs))
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
