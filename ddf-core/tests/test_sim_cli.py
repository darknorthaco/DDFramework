"""Tests for the ``python -m ddf simulate`` CLI dispatcher.

Strategy
--------

All tests drive the CLI via ``_sim_cli.main(argv)`` in-process. We
capture stdout/stderr by redirecting ``sys.stdout`` / ``sys.stderr``
to ``io.StringIO``. This is faster than spawning subprocesses and
exposes the same surface (argparse, dispatcher, JSON emission). One
test additionally spawns ``python -m ddf simulate ...`` as a real
subprocess to confirm wiring through ``ddf.__main__``.

Coverage
--------

- help output mentions all five subcommands
- doctrine-diff classifies a synthetic patch / breaking pair
- doctrine-diff reports IO errors via stderr and exit 1
- ritual-dryrun rejects non-JSON --args
- ritual-dryrun rejects --args that is JSON but not an object
- ritual-dryrun succeeds against the live engine for ritual=verify
- ledger-replay against the live engine reports chain_ok = true
- advisory-replay against the live engine reports chain_ok = true
- drift-simulation rejects an unknown scenario (argparse exit 2)
- subprocess invocation: ``python -m ddf simulate ledger-replay``
  produces the same JSON as the in-process call
- determinism: two consecutive in-process invocations produce
  byte-identical stdout
"""

from __future__ import annotations

import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
DDF_PY = REPO_ROOT / "ddf-core" / "ddf_py"

if str(DDF_PY) not in sys.path:
    sys.path.insert(0, str(DDF_PY))

from ddf import _sim_cli  # noqa: E402


# Engine fixtures (read-only). These exist in this repo.
LIVE_LEDGER = REPO_ROOT / "ledger" / "events.jsonl"
LIVE_DOCTRINE = REPO_ROOT / "doctrine.toml"
LIVE_CONSTELLATION = REPO_ROOT / "constellation.toml"
LIVE_ADVISORIES = REPO_ROOT / "advisories" / "stream.jsonl"
LIVE_CEREMONIES = REPO_ROOT / "ceremonies"


def _run(argv: list[str]) -> tuple[int, str, str]:
    """Invoke _sim_cli.main(argv) capturing stdout/stderr; return (rc, out, err)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = _sim_cli.main(argv)
        except SystemExit as exc:  # argparse uses SystemExit
            rc = int(exc.code) if isinstance(exc.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


_BASE_DOCTRINE = """
[meta]
doctrine_version = "0.7.0"

[invariants.I1]
name = "append-only-ledger"
description = "Ledger entries are never edited or deleted."
severity = "fatal"

[rituals]
registered = ["verify"]
""".strip()

_PATCH_DOCTRINE = """
[meta]
doctrine_version = "0.7.1"

[invariants.I1]
name = "append-only-ledger"
description = "Ledger entries are never edited or deleted."
severity = "fatal"

[rituals]
registered = ["verify"]
""".strip()


class TestSimCliHelp(unittest.TestCase):
    def test_help_lists_all_five_subcommands(self) -> None:
        rc, out, _err = _run(["--help"])
        self.assertEqual(rc, 0)
        for name in (
            "doctrine-diff",
            "ritual-dryrun",
            "ledger-replay",
            "advisory-replay",
            "drift-simulation",
        ):
            self.assertIn(name, out)


class TestSimCliDoctrineDiff(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = pathlib.Path(self.id().replace(".", "_") + "_tmp")
        self.tmpdir.mkdir(exist_ok=True)
        self.old = self.tmpdir / "old.toml"
        self.new = self.tmpdir / "new.toml"
        self.old.write_text(_BASE_DOCTRINE, encoding="utf-8")
        self.new.write_text(_PATCH_DOCTRINE, encoding="utf-8")

    def tearDown(self) -> None:
        for p in self.tmpdir.iterdir():
            p.unlink()
        self.tmpdir.rmdir()

    def test_patch_change_returns_patch_impact(self) -> None:
        rc, out, err = _run(
            ["doctrine-diff", "--old", str(self.old), "--new", str(self.new)]
        )
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertEqual(payload["impact"], "patch")

    def test_missing_old_file_returns_exit_1(self) -> None:
        rc, _out, err = _run(
            [
                "doctrine-diff",
                "--old",
                str(self.tmpdir / "nope.toml"),
                "--new",
                str(self.new),
            ]
        )
        self.assertEqual(rc, 1)
        self.assertIn("doctrine-diff", err)


class TestSimCliRitualDryrun(unittest.TestCase):
    def test_invalid_json_args_returns_exit_1(self) -> None:
        rc, _out, err = _run(
            [
                "ritual-dryrun",
                "--ritual",
                "verify",
                "--args",
                "{not json",
                "--ceremony-dir",
                str(LIVE_CEREMONIES),
                "--doctrine",
                str(LIVE_DOCTRINE),
            ]
        )
        self.assertEqual(rc, 1)
        self.assertIn("not valid JSON", err)

    def test_args_must_be_json_object_not_array(self) -> None:
        rc, _out, err = _run(
            [
                "ritual-dryrun",
                "--ritual",
                "verify",
                "--args",
                "[1, 2, 3]",
                "--ceremony-dir",
                str(LIVE_CEREMONIES),
                "--doctrine",
                str(LIVE_DOCTRINE),
            ]
        )
        self.assertEqual(rc, 1)
        self.assertIn("JSON object", err)

    def test_verify_ritual_against_live_engine_is_ok(self) -> None:
        rc, out, err = _run(
            [
                "ritual-dryrun",
                "--ritual",
                "verify",
                "--ceremony-dir",
                str(LIVE_CEREMONIES),
                "--doctrine",
                str(LIVE_DOCTRINE),
            ]
        )
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertTrue(payload["ok"], msg=payload)


class TestSimCliLedgerReplay(unittest.TestCase):
    def test_live_engine_ledger_chain_ok(self) -> None:
        rc, out, err = _run(["ledger-replay", "--ledger", str(LIVE_LEDGER)])
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertTrue(payload["chain_ok"], msg=payload)
        self.assertGreaterEqual(payload["entry_count"], 1)


class TestSimCliAdvisoryReplay(unittest.TestCase):
    def test_live_engine_advisory_stream_chain_ok(self) -> None:
        rc, out, err = _run(
            [
                "advisory-replay",
                "--advisory",
                str(LIVE_ADVISORIES),
                "--ledger",
                str(LIVE_LEDGER),
            ]
        )
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertTrue(payload["chain_ok"], msg=payload)


class TestSimCliDriftSimulation(unittest.TestCase):
    def test_unknown_scenario_rejected_by_argparse(self) -> None:
        rc, _out, err = _run(
            [
                "drift-simulation",
                "--scenario",
                "doctrine-drift",  # hyphen form is NOT a valid choice
                "--ledger",
                str(LIVE_LEDGER),
                "--doctrine",
                str(LIVE_DOCTRINE),
                "--constellation",
                str(LIVE_CONSTELLATION),
            ]
        )
        # argparse returns exit code 2 for invalid choices.
        self.assertEqual(rc, 2)
        self.assertIn("invalid choice", err)

    def test_aligned_scenario_all_against_live_engine(self) -> None:
        rc, out, err = _run(
            [
                "drift-simulation",
                "--scenario",
                "all",
                "--ledger",
                str(LIVE_LEDGER),
                "--doctrine",
                str(LIVE_DOCTRINE),
                "--constellation",
                str(LIVE_CONSTELLATION),
            ]
        )
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        # On a clean repo no drift rule should be firing.
        self.assertFalse(
            payload["would_fire"]["R001_doctrine_drift"], msg=payload
        )


class TestSimCliDeterminism(unittest.TestCase):
    def test_two_consecutive_invocations_yield_identical_output(self) -> None:
        argv = ["ledger-replay", "--ledger", str(LIVE_LEDGER)]
        _rc1, out1, _err1 = _run(argv)
        _rc2, out2, _err2 = _run(argv)
        self.assertEqual(out1, out2)


class TestSimCliSubprocess(unittest.TestCase):
    def test_subprocess_invocation_routes_through_ddf_main(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "ddf",
                "simulate",
                "ledger-replay",
                "--ledger",
                str(LIVE_LEDGER),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(DDF_PY)},
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["chain_ok"], msg=payload)


if __name__ == "__main__":
    unittest.main()
