"""Shrike I8 structural test.

GHOST must never open `ledger/events.jsonl` in a write mode, and must
never import from `phantom_core` or `hyperion_net`. These guarantees
are enforced by walking the `ghost/` source tree with ast + regex.

If this test fails, the invariant is broken at the source level
regardless of runtime behavior.
"""

from __future__ import annotations
import ast
import pathlib
import re
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

GHOST_SRC = PKG_ROOT / "ghost"

FORBIDDEN_IMPORT_PREFIXES = ("phantom_core", "hyperion_net")

# Any `open("events.jsonl", "w..." / "a..." / "r+..." / "x..."`-style
# call anywhere under ghost/. We match conservatively: any literal that
# ends in events.jsonl combined with a mode argument containing w/a/+/x.
WRITE_MODE_RE = re.compile(
    r"""open\([^)]*events\.jsonl[^)]*['"][^'"]*[wax+][^'"]*['"]""",
    re.DOTALL,
)


def _py_files(root: pathlib.Path):
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


class ReadonlyInvariantTest(unittest.TestCase):
    def test_no_writes_to_main_ledger(self):
        offenders = []
        for path in _py_files(GHOST_SRC):
            src = path.read_text(encoding="utf-8")
            if WRITE_MODE_RE.search(src):
                offenders.append(str(path.relative_to(PKG_ROOT)))
        self.assertEqual(
            offenders,
            [],
            f"Shrike I8 VIOLATION: ghost/ opens events.jsonl in a write mode in: {offenders}",
        )

    def test_no_phantom_core_or_hyperion_net_imports(self):
        offenders = []
        for path in _py_files(GHOST_SRC):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                            offenders.append(f"{path.name}: import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    if mod.startswith(FORBIDDEN_IMPORT_PREFIXES):
                        offenders.append(f"{path.name}: from {mod} import ...")
        self.assertEqual(
            offenders,
            [],
            f"Shrike I8 VIOLATION: ghost/ imports forbidden modules: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
