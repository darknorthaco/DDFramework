"""Tests for ghost.reader. Stdlib unittest only."""

from __future__ import annotations
import pathlib
import sys
import unittest

# Ensure the sibling `ghost` package is importable when tests run
# from the project root (e.g. `python -m unittest discover -s ghost-observer`).
HERE = pathlib.Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

from ghost import reader  # noqa: E402


REPO_ROOT = PKG_ROOT.parent
LEDGER = REPO_ROOT / "ledger" / "events.jsonl"

GENESIS_ENTRY_HASH = (
    "sha256:cac802cf5f41756834620be8bb2b64b6d175b5a541ef4cd984067a3dcc7e098e"
)


class GenesisTest(unittest.TestCase):
    def test_ledger_file_exists(self):
        self.assertTrue(LEDGER.exists(), f"expected {LEDGER} to exist")

    def test_genesis_entry_hash_matches_committed(self):
        entries = list(reader.iter_entries(LEDGER))
        self.assertGreaterEqual(len(entries), 1, "ledger must have >=1 entry")
        self.assertEqual(entries[0].entry_hash, GENESIS_ENTRY_HASH)

    def test_chain_is_valid(self):
        result = reader.verify(LEDGER)
        self.assertTrue(result.ok, f"chain broken: {result.error}")
        self.assertGreaterEqual(result.count, 1)


class CanonicalTest(unittest.TestCase):
    def test_canonical_sorts_keys(self):
        got = reader.canonical_bytes({"b": 2, "a": 1})
        self.assertEqual(got, b'{"a":1,"b":2}')

    def test_canonical_bool_literals(self):
        got = reader.canonical_bytes({"ok": True, "bad": False})
        self.assertEqual(got, b'{"bad":false,"ok":true}')


if __name__ == "__main__":
    unittest.main()
