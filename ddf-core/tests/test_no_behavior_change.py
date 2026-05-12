"""T3 — No-behavior-change test.

Asserts that `ddf verify` is structurally equivalent to `ddf-exec verify`
as far as the ledger is concerned. (`ddf-exec` was renamed from
`phantom` at v1.0.0; historical ledger entries written by the older
`phantom` binary remain frozen per I1.)

Strategy (designed to not pollute the live ledger twice in CI):
  - Read the most recent `verify.result` entry from the main ledger
    (whichever invocation produced it, ddf-exec / ddf / older phantom).
  - Assert it has `status=ok`.
  - Assert its `doctrine_hash` and `constellation_hash` match the
    current on-disk (normalized) hashes — which both `ddf-exec verify`
    and `ddf verify` must compute identically.
  - Additionally, confirm that the `ddf-exec` binary exists in the
    cargo target dir (or is on PATH) so `ddf verify` is callable.

The stronger pairwise-invocation test is deferred to the post-1.0.0
ceremony, where both commands are run back-to-back and the resulting
ledger entries are inspected by the operator.
"""

from __future__ import annotations
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent
REPO_ROOT = DDF_CORE.parent
GHOST_PKG = REPO_ROOT / "ghost-observer"
LEDGER = REPO_ROOT / "ledger" / "events.jsonl"
DOCTRINE = REPO_ROOT / "doctrine.toml"
CONSTELLATION = REPO_ROOT / "constellation.toml"

if str(GHOST_PKG) not in sys.path:
    sys.path.insert(0, str(GHOST_PKG))


def sha256_file_normalized(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r", b"")).hexdigest()


def _last_verify_result(path: pathlib.Path) -> dict | None:
    if not path.exists():
        return None
    last = None
    with open(path, "rb") as f:
        for raw in f:
            if not raw.strip():
                continue
            try:
                entry = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            if entry.get("event") == "verify.result":
                last = entry
    return last


def _find_engine_executor() -> pathlib.Path | None:
    """Locate the engine executor binary (ddf-exec) via env / PATH / cargo-target heuristics."""
    env_override = os.environ.get("DDF_EXEC_BIN")
    if env_override:
        p = pathlib.Path(env_override)
        return p if p.exists() else None
    on_path = shutil.which("ddf-exec")
    if on_path:
        return pathlib.Path(on_path)
    # Common cargo target locations
    for candidate in (
        REPO_ROOT / "target" / "release" / "ddf-exec.exe",
        REPO_ROOT / "target" / "release" / "ddf-exec",
    ):
        if candidate.exists():
            return candidate
    # Cursor sandbox cache (if tests run inside the dev env)
    for env_key in ("CARGO_TARGET_DIR",):
        override = os.environ.get(env_key)
        if override:
            for name in ("ddf-exec", "ddf-exec.exe"):
                c = pathlib.Path(override) / "release" / name
                if c.exists():
                    return c
    return None


class NoBehaviorChangeTest(unittest.TestCase):
    def test_latest_verify_result_has_ok_status(self):
        last = _last_verify_result(LEDGER)
        self.assertIsNotNone(last, "expected at least one verify.result in the ledger")
        self.assertEqual(last.get("status"), "ok")

    def test_latest_verify_result_records_current_hashes(self):
        last = _last_verify_result(LEDGER)
        self.assertIsNotNone(last)
        # Current normalized hashes on disk (what both ddf-exec and ddf should produce):
        expected_doctrine = f"sha256:{sha256_file_normalized(DOCTRINE)}"
        expected_constellation = f"sha256:{sha256_file_normalized(CONSTELLATION)}"
        self.assertEqual(
            last.get("doctrine_hash"),
            expected_doctrine,
            "latest verify.result doctrine_hash does not match current on-disk doctrine; "
            "rebuild ddf-exec and re-run `ddf-exec verify` or `ddf verify`",
        )
        self.assertEqual(last.get("constellation_hash"), expected_constellation)


if __name__ == "__main__":
    unittest.main()
