"""Ledger replay — Phase 6 simulation module.

Walk ``ledger/events.jsonl`` from genesis, recompute the canonical
hash chain per ``ledger/SPEC.md`` §5, and return a structured report
suitable for disaster-recovery and audit.

Stdlib-only; pure function; **read-only** on the ledger (open as
``"rb"``; no writes anywhere). Honors invariant I5 (no ambient
state): the ledger path is an explicit argument.

Canonical form (matching ``ghost.reader`` and ``ledger/SPEC.md`` §5):

- JSON object **without** the ``entry_hash`` field.
- ``json.dumps`` with ``sort_keys=True``, ``separators=(',', ':')``,
  ``ensure_ascii=False``; UTF-8 encoded; no trailing newline.
- ``entry_hash = "sha256:" + sha256(canonical_bytes).hex()``.
- Genesis entry: ``prev_entry_hash`` is ``"sha256:" + "0" * 64``.
- Every later entry: ``prev_entry_hash`` equals the previous line's
  ``entry_hash``.

Detected conditions, surfaced both as fields and as descriptors in
``ordered_summary``:

- ``chain_ok`` — every entry's recomputed hash matches the stored
  ``entry_hash`` and the chain links cleanly back to genesis.
- ``timestamps_monotonic`` — RFC 3339 timestamps are non-decreasing
  line over line. Regression line is captured for R006-style audit.
- ``event_kind_counts`` — counts per ``event`` field.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

ZERO_HASH = "sha256:" + "0" * 64


def _canonical_bytes(obj: dict[str, Any]) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _recomputed_hash(entry: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(entry)).hexdigest()


def run(ledger_path: pathlib.Path) -> dict[str, Any]:
    """Replay the main ledger and return a structured chain-audit report.

    Parameters
    ----------
    ledger_path:
        Path to ``ledger/events.jsonl``. The file is opened ``"rb"``
        and is never written.

    Returns
    -------
    dict
        Stable keys: ``entry_count``, ``chain_ok``,
        ``chain_break_at_line``, ``chain_error``, ``event_kind_counts``,
        ``event_kinds`` (sorted unique), ``first_entry_ts``,
        ``last_entry_ts``, ``timestamps_monotonic``,
        ``timestamp_regression_at_line``, ``genesis_prev_hash``,
        ``head_hash``, ``ledger_exists``, ``errors`` (sorted),
        ``ordered_summary`` (sorted, deterministic).

        All list values are sorted; absent values are ``None``.
    """
    path = pathlib.Path(ledger_path)
    errors: list[str] = []

    if not path.exists():
        return {
            "ledger_exists": False,
            "entry_count": 0,
            "chain_ok": False,
            "chain_break_at_line": None,
            "chain_error": "ledger_missing",
            "event_kind_counts": {},
            "event_kinds": [],
            "first_entry_ts": None,
            "last_entry_ts": None,
            "timestamps_monotonic": True,
            "timestamp_regression_at_line": None,
            "genesis_prev_hash": None,
            "head_hash": ZERO_HASH,
            "errors": sorted(errors + ["ledger_missing"]),
            "ordered_summary": sorted(["chain_ok:false", "ledger_exists:false"]),
        }

    entry_count = 0
    chain_ok = True
    chain_break_at_line: int | None = None
    chain_error: str | None = None
    event_counts: dict[str, int] = {}
    first_ts: str | None = None
    last_ts: str | None = None
    timestamps_monotonic = True
    timestamp_regression_at: int | None = None
    genesis_prev: str | None = None
    head_hash = ZERO_HASH

    prev_hash = ZERO_HASH
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f, start=1):
            if not raw.strip():
                # Blank lines are a doctrine violation per SPEC §1.
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = f"blank_line:{lineno}"
                errors.append(chain_error)
                break

            try:
                entry = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = f"json_parse_error:{lineno}:{exc}"
                errors.append(chain_error)
                break

            stored_hash = entry.pop("entry_hash", None)
            if not isinstance(stored_hash, str):
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = f"missing_entry_hash:{lineno}"
                errors.append(chain_error)
                break

            recomputed = _recomputed_hash(entry)
            if recomputed != stored_hash:
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = (
                    f"entry_hash_mismatch:{lineno}:stored={stored_hash}:recomputed={recomputed}"
                )
                errors.append(chain_error)
                break

            stored_prev = entry.get("prev_entry_hash")
            if lineno == 1:
                genesis_prev = stored_prev if isinstance(stored_prev, str) else None
            if stored_prev != prev_hash:
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = (
                    f"chain_link_broken:{lineno}:expected_prev={prev_hash}:stored_prev={stored_prev}"
                )
                errors.append(chain_error)
                break

            kind = entry.get("event")
            if isinstance(kind, str):
                event_counts[kind] = event_counts.get(kind, 0) + 1

            ts = entry.get("timestamp")
            if isinstance(ts, str):
                if first_ts is None:
                    first_ts = ts
                if last_ts is not None and ts < last_ts and timestamps_monotonic:
                    timestamps_monotonic = False
                    timestamp_regression_at = lineno
                last_ts = ts

            entry_count += 1
            head_hash = stored_hash
            prev_hash = stored_hash

    event_kinds = sorted(event_counts.keys())
    summary: list[str] = [
        f"entry_count:{entry_count}",
        f"chain_ok:{str(chain_ok).lower()}",
        f"timestamps_monotonic:{str(timestamps_monotonic).lower()}",
        f"event_kinds_total:{len(event_kinds)}",
    ]
    if chain_break_at_line is not None:
        summary.append(f"chain_break_at_line:{chain_break_at_line}")
    if timestamp_regression_at is not None:
        summary.append(f"timestamp_regression_at_line:{timestamp_regression_at}")
    if first_ts is not None:
        summary.append(f"first_entry_ts:{first_ts}")
    if last_ts is not None:
        summary.append(f"last_entry_ts:{last_ts}")
    for kind, count in event_counts.items():
        summary.append(f"event_kind:{kind}:{count}")
    summary.sort()

    return {
        "ledger_exists": True,
        "entry_count": entry_count,
        "chain_ok": chain_ok,
        "chain_break_at_line": chain_break_at_line,
        "chain_error": chain_error,
        "event_kind_counts": dict(sorted(event_counts.items())),
        "event_kinds": event_kinds,
        "first_entry_ts": first_ts,
        "last_entry_ts": last_ts,
        "timestamps_monotonic": timestamps_monotonic,
        "timestamp_regression_at_line": timestamp_regression_at,
        "genesis_prev_hash": genesis_prev,
        "head_hash": head_hash,
        "errors": sorted(errors),
        "ordered_summary": summary,
    }
