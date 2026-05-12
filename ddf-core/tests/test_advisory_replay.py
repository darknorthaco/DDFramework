"""T — Phase 6 advisory_replay chain auditor.

Covers:
- missing advisory stream -> chain_error="advisory_stream_missing"
- empty advisory stream -> chain_ok=True (vacuous), advisory_count=0
- single bootstrap advisory linking a real ledger tail -> ok
- multi-advisory chain across one run_id, severity counts surfaced
- chain break (wrong prev_advisory_hash) reported with line number
- advisory_hash mismatch (mutated body) reported
- ledger_tail_hash that doesn't exist in ledger -> tail_hashes_missing > 0
- deterministic ordered_summary
- live engine advisory stream replays cleanly against live ledger

Fixtures synthesize valid hashes in the test helper. No engine
writes.
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

from simulation import advisory_replay  # noqa: E402

ZERO = "sha256:" + "0" * 64


def _canonical_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _hash(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(obj)).hexdigest()


def _append_advisory(path: pathlib.Path, entry: dict, *, prev: str) -> str:
    body = dict(entry)
    body["prev_advisory_hash"] = prev
    ah = _hash(body)
    body["advisory_hash"] = ah
    with open(path, "ab") as f:
        f.write((json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return ah


def _append_ledger(path: pathlib.Path, entry: dict, *, prev: str) -> str:
    body = dict(entry)
    body["prev_entry_hash"] = prev
    eh = _hash(body)
    body["entry_hash"] = eh
    with open(path, "ab") as f:
        f.write((json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return eh


def _new_paths() -> tuple[pathlib.Path, pathlib.Path]:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ddf-adv-"))
    return tmp / "stream.jsonl", tmp / "events.jsonl"


def _genesis_ledger_entry() -> dict:
    return {
        "timestamp": "2026-01-01T00:00:00Z",
        "event": "doctrine_amendment",
        "version": "0.1.0",
        "change": "genesis",
        "domain": "complicated",
        "integrity_check": True,
        "regenerative_check": True,
        "simulation_required": False,
        "disruption_considered": False,
        "doctrine_hash": "sha256:" + "a" * 64,
    }


def _bootstrap_advisory(ledger_tail_hash: str) -> dict:
    return {
        "timestamp": "2026-01-02T00:00:00Z",
        "rule_id": "R000_bootstrap",
        "severity": "info",
        "subject": "GHOST advisory stream initialized",
        "evidence": {"ghost_version": "0.5.0"},
        "recommended_action": "No action.",
        "ledger_tail_hash": ledger_tail_hash,
        "run_id": "abcdef0123456789",
    }


def _drift_advisory(ledger_tail_hash: str, run_id: str = "abcdef0123456789") -> dict:
    return {
        "timestamp": "2026-01-02T00:00:01Z",
        "rule_id": "R001_doctrine_drift",
        "severity": "warn",
        "subject": "doctrine drift detected",
        "evidence": {"observed_hash": "sha256:" + "9" * 64},
        "recommended_action": "Run amend-doctrine.",
        "ledger_tail_hash": ledger_tail_hash,
        "run_id": run_id,
    }


class AdvisoryReplayTest(unittest.TestCase):
    def test_missing_advisory_stream(self):
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="ddf-adv-"))
        r = advisory_replay.run(tmp / "nope.jsonl", tmp / "events.jsonl")
        self.assertFalse(r["advisory_path_exists"])
        self.assertFalse(r["chain_ok"])
        self.assertEqual(r["chain_error"], "advisory_stream_missing")
        self.assertEqual(r["advisory_count"], 0)

    def test_empty_advisory_stream_is_vacuously_ok(self):
        adv, led = _new_paths()
        adv.write_bytes(b"")
        led.write_bytes(b"")
        r = advisory_replay.run(adv, led)
        self.assertTrue(r["advisory_path_exists"])
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["advisory_count"], 0)
        self.assertEqual(r["head_hash"], ZERO)

    def test_single_bootstrap_with_present_tail(self):
        adv, led = _new_paths()
        # Seed the ledger with one entry so the advisory's tail is "present".
        led_entry_hash = _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        h1 = _append_advisory(adv, _bootstrap_advisory(led_entry_hash), prev=ZERO)
        r = advisory_replay.run(adv, led)
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["advisory_count"], 1)
        self.assertEqual(r["head_hash"], h1)
        self.assertEqual(r["rule_id_counts"], {"R000_bootstrap": 1})
        self.assertEqual(r["severity_counts"], {"info": 1})
        self.assertEqual(r["run_count"], 1)
        self.assertEqual(r["tail_hashes_present_in_ledger"], 1)
        self.assertEqual(r["tail_hashes_missing"], 0)

    def test_multi_advisory_one_run(self):
        adv, led = _new_paths()
        led_entry_hash = _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        h1 = _append_advisory(adv, _bootstrap_advisory(led_entry_hash), prev=ZERO)
        h2 = _append_advisory(adv, _drift_advisory(led_entry_hash), prev=h1)
        r = advisory_replay.run(adv, led)
        self.assertTrue(r["chain_ok"])
        self.assertEqual(r["advisory_count"], 2)
        self.assertEqual(r["head_hash"], h2)
        self.assertEqual(
            r["rule_id_counts"], {"R000_bootstrap": 1, "R001_doctrine_drift": 1}
        )
        self.assertEqual(r["severity_counts"], {"info": 1, "warn": 1})
        self.assertEqual(r["run_count"], 1)

    def test_chain_break_wrong_prev(self):
        adv, led = _new_paths()
        led_entry_hash = _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        _append_advisory(adv, _bootstrap_advisory(led_entry_hash), prev=ZERO)
        _append_advisory(adv, _drift_advisory(led_entry_hash), prev="sha256:" + "9" * 64)
        r = advisory_replay.run(adv, led)
        self.assertFalse(r["chain_ok"])
        self.assertEqual(r["chain_break_at_line"], 2)
        self.assertTrue(r["chain_error"].startswith("chain_link_broken:2:"))

    def test_advisory_hash_mismatch_after_mutation(self):
        adv, led = _new_paths()
        led_entry_hash = _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        _append_advisory(adv, _bootstrap_advisory(led_entry_hash), prev=ZERO)
        bad = _drift_advisory(led_entry_hash)
        bad["prev_advisory_hash"] = "sha256:0000"  # placeholder; we replace below
        # Compute hash on one body, then mutate after.
        bad["prev_advisory_hash"] = _hash(_bootstrap_advisory(led_entry_hash) | {"prev_advisory_hash": ZERO})
        ah = _hash(bad)
        bad["advisory_hash"] = ah
        bad["subject"] = "tampered after hashing"
        with open(adv, "ab") as f:
            f.write(
                (json.dumps(bad, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            )
        r = advisory_replay.run(adv, led)
        self.assertFalse(r["chain_ok"])
        self.assertEqual(r["chain_break_at_line"], 2)
        self.assertTrue(
            r["chain_error"].startswith("advisory_hash_mismatch:2:")
            or r["chain_error"].startswith("chain_link_broken:2:")
        )

    def test_tail_hash_missing_in_ledger_is_reported(self):
        adv, led = _new_paths()
        # Empty ledger, advisory references a phantom tail.
        led.write_bytes(b"")
        unknown_tail = "sha256:" + "f" * 64
        _append_advisory(adv, _bootstrap_advisory(unknown_tail), prev=ZERO)
        r = advisory_replay.run(adv, led)
        self.assertTrue(r["chain_ok"])  # advisory chain is internally fine
        # With empty ledger we have no known hashes -> tails_present_in_ledger=0
        # and tails_missing=0 (we cannot judge without a ledger).
        self.assertEqual(r["tail_hashes_present_in_ledger"], 0)
        self.assertEqual(r["tail_hashes_missing"], 0)

        # Now write a non-empty ledger that does NOT contain the referenced tail.
        _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        r2 = advisory_replay.run(adv, led)
        self.assertEqual(r2["tail_hashes_missing"], 1)
        self.assertEqual(r2["tail_hash_missing_lines"], [1])

    def test_ordered_summary_is_sorted_and_deterministic(self):
        adv, led = _new_paths()
        led_entry_hash = _append_ledger(led, _genesis_ledger_entry(), prev=ZERO)
        h1 = _append_advisory(adv, _bootstrap_advisory(led_entry_hash), prev=ZERO)
        _append_advisory(adv, _drift_advisory(led_entry_hash), prev=h1)
        r1 = advisory_replay.run(adv, led)
        r2 = advisory_replay.run(adv, led)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["ordered_summary"], sorted(r1["ordered_summary"]))

    def test_live_engine_advisory_stream_replays_cleanly(self):
        adv = REPO_ROOT / "advisories" / "stream.jsonl"
        led = REPO_ROOT / "ledger" / "events.jsonl"
        if not adv.exists() or not led.exists():
            self.skipTest("live advisory/ledger not present in this checkout")
        r = advisory_replay.run(adv, led)
        self.assertTrue(r["advisory_path_exists"])
        self.assertTrue(r["ledger_path_exists"])
        self.assertTrue(r["chain_ok"], f"live advisory chain broken: {r['chain_error']}")
        self.assertGreater(r["advisory_count"], 0)


if __name__ == "__main__":
    unittest.main()
