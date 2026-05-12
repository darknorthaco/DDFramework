"""T — Phase 6 ledger_replay chain auditor.

Covers:
- missing ledger file -> ledger_exists=False, chain_error
- empty ledger file -> chain_ok=True (vacuous), entry_count=0
- single-entry valid genesis -> chain_ok=True, head=hash
- two-entry valid chain -> chain_ok=True, monotonic timestamps
- chain break (wrong prev_entry_hash) -> chain_ok=False, break line reported
- entry_hash mismatch (mutated body) -> chain_ok=False, break reported
- non-monotonic timestamps -> regression line reported
- event kind counts surfaced
- deterministic ordered_summary
- ledger_replay against the live engine ledger replays cleanly

Fixtures are synthesized into ``tmp_path`` using the same canonical
form as ``ghost.reader`` / ``ledger/SPEC.md`` §5. No engine writes.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent
REPO_ROOT = DDF_CORE.parent

if str(DDF_CORE) not in sys.path:
    sys.path.insert(0, str(DDF_CORE))

from simulation import ledger_replay  # noqa: E402

ZERO = "sha256:" + "0" * 64


def _canonical_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _hash(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(obj)).hexdigest()


def _append(path: pathlib.Path, entry: dict, *, prev: str) -> str:
    """Serialize ``entry`` with ``prev_entry_hash=prev`` + computed entry_hash."""
    body = dict(entry)
    body["prev_entry_hash"] = prev
    eh = _hash(body)
    body["entry_hash"] = eh
    with open(path, "ab") as f:
        f.write((json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return eh


def _new_ledger() -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ddf-ledger-"))
    return tmp / "events.jsonl"


def _genesis(ts: str = "2026-01-01T00:00:00Z", event: str = "doctrine_amendment") -> dict:
    return {
        "timestamp": ts,
        "event": event,
        "version": "0.1.0",
        "change": "genesis",
        "domain": "complicated",
        "integrity_check": True,
        "regenerative_check": True,
        "simulation_required": False,
        "disruption_considered": False,
        "doctrine_hash": "sha256:" + "a" * 64,
    }


def _verify_entry(ts: str, doctrine_hash: str = "sha256:" + "b" * 64) -> dict:
    return {
        "timestamp": ts,
        "event": "verify.result",
        "version": "0.7.0",
        "change": "phantom verify status=ok",
        "domain": "complicated",
        "integrity_check": True,
        "regenerative_check": True,
        "simulation_required": False,
        "disruption_considered": False,
        "doctrine_hash": doctrine_hash,
        "status": "ok",
    }


class LedgerReplayTest(unittest.TestCase):
    def test_missing_ledger(self):
        path = pathlib.Path(tempfile.mkdtemp(prefix="ddf-ledger-")) / "nope.jsonl"
        r = ledger_replay.run(path)
        self.assertFalse(r["ledger_exists"])
        self.assertEqual(r["entry_count"], 0)
        self.assertFalse(r["chain_ok"])
        self.assertEqual(r["chain_error"], "ledger_missing")
        self.assertEqual(r["head_hash"], ZERO)

    def test_empty_ledger_is_vacuously_ok(self):
        path = _new_ledger()
        path.write_bytes(b"")
        r = ledger_replay.run(path)
        self.assertTrue(r["ledger_exists"])
        self.assertEqual(r["entry_count"], 0)
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["head_hash"], ZERO)
        self.assertEqual(r["event_kind_counts"], {})

    def test_single_genesis_entry(self):
        path = _new_ledger()
        h1 = _append(path, _genesis(), prev=ZERO)
        r = ledger_replay.run(path)
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["entry_count"], 1)
        self.assertEqual(r["head_hash"], h1)
        self.assertEqual(r["genesis_prev_hash"], ZERO)
        self.assertEqual(r["event_kind_counts"], {"doctrine_amendment": 1})
        self.assertEqual(r["first_entry_ts"], "2026-01-01T00:00:00Z")

    def test_two_entry_valid_chain(self):
        path = _new_ledger()
        h1 = _append(path, _genesis(ts="2026-01-01T00:00:00Z"), prev=ZERO)
        h2 = _append(path, _verify_entry(ts="2026-01-02T00:00:00Z"), prev=h1)
        r = ledger_replay.run(path)
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["entry_count"], 2)
        self.assertEqual(r["head_hash"], h2)
        self.assertEqual(r["event_kinds"], ["doctrine_amendment", "verify.result"])
        self.assertTrue(r["timestamps_monotonic"])
        self.assertIsNone(r["timestamp_regression_at_line"])

    def test_chain_break_wrong_prev(self):
        path = _new_ledger()
        _append(path, _genesis(), prev=ZERO)
        # Link the second entry to a bogus prev:
        _append(path, _verify_entry(ts="2026-01-02T00:00:00Z"), prev="sha256:" + "9" * 64)
        r = ledger_replay.run(path)
        self.assertFalse(r["chain_ok"])
        self.assertEqual(r["chain_break_at_line"], 2)
        self.assertTrue(r["chain_error"].startswith("chain_link_broken:2:"))

    def test_entry_hash_mismatch_after_mutation(self):
        path = _new_ledger()
        _append(path, _genesis(), prev=ZERO)
        # Hand-write a line with a body that disagrees with its entry_hash.
        bad = _verify_entry(ts="2026-01-02T00:00:00Z")
        bad["prev_entry_hash"] = _hash(_genesis() | {"prev_entry_hash": ZERO})  # close enough
        # Compute hash on one body, then mutate the body before write.
        eh = _hash(bad)
        bad["entry_hash"] = eh
        bad["change"] = "tampered after hashing"
        with open(path, "ab") as f:
            f.write(
                (json.dumps(bad, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            )
        r = ledger_replay.run(path)
        self.assertFalse(r["chain_ok"])
        self.assertIsNotNone(r["chain_break_at_line"])
        # Either chain_link_broken (if prev hash also went stale) or entry_hash_mismatch.
        self.assertTrue(
            r["chain_error"].startswith("entry_hash_mismatch:2:")
            or r["chain_error"].startswith("chain_link_broken:2:")
        )

    def test_timestamp_regression_is_reported(self):
        path = _new_ledger()
        h1 = _append(path, _genesis(ts="2026-01-02T00:00:00Z"), prev=ZERO)
        _append(path, _verify_entry(ts="2026-01-01T00:00:00Z"), prev=h1)
        r = ledger_replay.run(path)
        self.assertTrue(r["chain_ok"], r["chain_error"])
        self.assertFalse(r["timestamps_monotonic"])
        self.assertEqual(r["timestamp_regression_at_line"], 2)

    def test_event_kind_counts(self):
        path = _new_ledger()
        h1 = _append(path, _genesis(ts="2026-01-01T00:00:00Z"), prev=ZERO)
        h2 = _append(path, _verify_entry(ts="2026-01-02T00:00:00Z"), prev=h1)
        h3 = _append(path, _verify_entry(ts="2026-01-03T00:00:00Z"), prev=h2)
        r = ledger_replay.run(path)
        self.assertEqual(r["event_kind_counts"], {"doctrine_amendment": 1, "verify.result": 2})
        self.assertEqual(r["entry_count"], 3)
        self.assertEqual(r["head_hash"], h3)

    def test_ordered_summary_is_sorted_and_deterministic(self):
        path = _new_ledger()
        h1 = _append(path, _genesis(ts="2026-01-01T00:00:00Z"), prev=ZERO)
        _append(path, _verify_entry(ts="2026-01-02T00:00:00Z"), prev=h1)
        r1 = ledger_replay.run(path)
        r2 = ledger_replay.run(path)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["ordered_summary"], sorted(r1["ordered_summary"]))

    def test_live_engine_ledger_replays_cleanly(self):
        live = REPO_ROOT / "ledger" / "events.jsonl"
        if not live.exists():
            self.skipTest("live ledger not present in this checkout")
        r = ledger_replay.run(live)
        self.assertTrue(r["ledger_exists"])
        self.assertTrue(r["chain_ok"], f"live ledger chain broken: {r['chain_error']}")
        self.assertGreater(r["entry_count"], 0)
        self.assertTrue(r["timestamps_monotonic"])


if __name__ == "__main__":
    unittest.main()
