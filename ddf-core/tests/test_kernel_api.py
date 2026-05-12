"""T2 — Kernel API surface test.

Asserts:
  - Python `ddf` package imports cleanly and exposes the documented surface.
  - Re-exported `ghost` modules resolve.
  - `ddf.verify()` and `ddf.advise()` are callable (signatures only; not invoked
    for real to avoid polluting the live ledger with ceremonial test runs).
  - `ddf.ledger` is a valid namespace.
"""

from __future__ import annotations
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent
REPO_ROOT = DDF_CORE.parent
DDF_PY_PKG = DDF_CORE / "ddf_py"
GHOST_PKG = REPO_ROOT / "ghost-observer"

for p in (DDF_PY_PKG, GHOST_PKG):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ddf  # noqa: E402


class PythonKernelApiTest(unittest.TestCase):
    def test_version_constants(self):
        self.assertEqual(ddf.__version__, "1.0.0")
        self.assertEqual(ddf.ENGINE_VERSION, "1.0.0")

    def test_ghost_reexports_available(self):
        # Must be attributes, not modules we forgot to re-export.
        self.assertTrue(hasattr(ddf, "reader"))
        self.assertTrue(hasattr(ddf, "advisor"))
        self.assertTrue(hasattr(ddf, "advisory_writer"))
        self.assertTrue(hasattr(ddf, "ghost_version"))
        # ghost_version should be a non-empty string
        self.assertTrue(isinstance(ddf.ghost_version, str) and ddf.ghost_version)

    def test_ledger_namespace(self):
        self.assertIs(ddf.ledger, ddf.reader)
        # reader has the key functions we rely on
        self.assertTrue(callable(ddf.ledger.iter_entries))
        self.assertTrue(callable(ddf.ledger.verify))

    def test_verify_callable(self):
        self.assertTrue(callable(ddf.verify))

    def test_advise_callable(self):
        self.assertTrue(callable(ddf.advise))

    def test_engine_version_matches_ghost(self):
        """The kernel API's ENGINE_VERSION should line up with ghost's own version."""
        self.assertEqual(ddf.ENGINE_VERSION, ddf.ghost_version)


if __name__ == "__main__":
    unittest.main()
