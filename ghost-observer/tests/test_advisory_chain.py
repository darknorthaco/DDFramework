"""Advisory chain write + verify roundtrip tests."""

from __future__ import annotations
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

from ghost.advisory_writer import AdvisoryWriter, ZERO_HASH, verify_chain  # noqa: E402
from ghost.model import Advisory  # noqa: E402


class AdvisoryChainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="shrike_advisory_"))
        self.path = self.tmp / "stream.jsonl"

    def tearDown(self) -> None:
        if self.path.exists():
            self.path.unlink()
        self.tmp.rmdir()

    def test_empty_stream_has_zero_head(self):
        w = AdvisoryWriter(self.path)
        self.assertTrue(w.is_empty())
        self.assertEqual(w.current_head(), ZERO_HASH)

    def test_writer_refuses_to_write_to_main_ledger_path(self):
        with self.assertRaises(ValueError):
            AdvisoryWriter(self.tmp / "events.jsonl")

    def test_write_and_verify_three_advisories(self):
        w = AdvisoryWriter(self.path)
        for i in range(3):
            w.append(
                Advisory(
                    rule_id=f"RTEST_{i}",
                    severity="info",
                    subject=f"entry {i}",
                    evidence={"i": i},
                    recommended_action="",
                ),
                run_id="deadbeefcafef00d",
                ledger_tail_hash="sha256:ledger_tip",
                timestamp=f"2026-04-20T00:00:0{i}Z",
            )
        ok, count, head, err = verify_chain(self.path)
        self.assertTrue(ok, f"chain should be valid: {err}")
        self.assertEqual(count, 3)

    def test_verify_detects_tampering(self):
        w = AdvisoryWriter(self.path)
        w.append(
            Advisory(
                rule_id="RTEST",
                severity="info",
                subject="to be tampered",
                evidence={},
                recommended_action="",
            ),
            run_id="deadbeefcafef00d",
            ledger_tail_hash="sha256:tip",
            timestamp="2026-04-20T00:00:00Z",
        )
        # Tamper: change "subject" value in-file.
        raw = self.path.read_bytes()
        tampered = raw.replace(b"to be tampered", b"tampered content")
        self.path.write_bytes(tampered)

        ok, _, _, err = verify_chain(self.path)
        self.assertFalse(ok)
        self.assertIn("mismatch", err or "")


if __name__ == "__main__":
    unittest.main()
