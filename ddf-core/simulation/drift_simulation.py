"""Drift simulation — Phase 6 simulation module.

For a given scenario in
``{doctrine_drift, constellation_drift, binary_stale, all}``,
decide whether the corresponding GHOST rule (R001 / R002 / R003)
would fire **right now** given the on-disk state of ``doctrine.toml``,
``constellation.toml``, and the main ledger.

Stdlib-only; pure function; **read-only** on the ledger and both
TOML documents (all opened ``"rb"``; no writes anywhere). Honors
invariant I5 (no ambient state): every path is an explicit
argument.

Rule semantics (mirroring ``ghost-observer/ghost/rules`` R001–R003):

- **R001 doctrine_drift**: ``sha256(doctrine.toml on disk)`` differs
  from the ``doctrine_hash`` recorded by the most recent ledger
  amendment entry (``event ∈ {doctrine.amended, doctrine_amendment}``).
- **R002 constellation_drift**: same comparison for
  ``constellation.toml`` against the most recent amendment's
  ``constellation_hash``.
- **R003 binary_stale**: the most recent ``verify.result`` entry's
  ``doctrine_hash`` differs from the most recent amendment's
  ``doctrine_hash`` (the executing binary still embeds an older
  doctrine hash than the ledger of record reports).

The file hash uses ``ghost.reader``'s LF-normalized form: read bytes,
strip ``\\r``, then ``sha256``. This matches what phantom records.

The ``scenario`` argument selects which rules to evaluate; all other
rules report ``would_fire = False`` and are omitted from
``scenarios_checked``.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

_SCENARIOS = {
    "doctrine_drift": {"R001_doctrine_drift"},
    "constellation_drift": {"R002_constellation_drift"},
    "binary_stale": {"R003_binary_stale"},
    "all": {
        "R001_doctrine_drift",
        "R002_constellation_drift",
        "R003_binary_stale",
    },
}

_AMENDMENT_EVENTS = frozenset({"doctrine.amended", "doctrine_amendment"})
_VERIFY_EVENT = "verify.result"


def _file_hash_lf(path: pathlib.Path) -> str | None:
    """SHA-256 of a text file with CR bytes stripped (LF-normalized).

    Returns ``"sha256:<hex>"`` or ``None`` on read failure / missing.
    """
    try:
        data = path.read_bytes().replace(b"\r", b"")
    except OSError:
        return None
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _find_latest_by_event(
    ledger_path: pathlib.Path, events: frozenset[str] | set[str]
) -> tuple[dict[str, Any] | None, int | None, int]:
    """Walk the ledger and return (latest_entry, line_no, total_entries).

    The walk is *not* a hash-chain audit; it parses JSON line by line and
    keeps the last entry whose ``event`` is in ``events``. Total entries
    counts every well-formed JSON line regardless of event.
    """
    latest: dict[str, Any] | None = None
    latest_line: int | None = None
    total = 0
    if not ledger_path.exists():
        return None, None, 0
    try:
        with open(ledger_path, "rb") as f:
            for lineno, raw in enumerate(f, start=1):
                if not raw.strip():
                    continue
                try:
                    entry = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                total += 1
                if entry.get("event") in events:
                    latest = entry
                    latest_line = lineno
    except OSError:
        return latest, latest_line, total
    return latest, latest_line, total


def run(
    ledger_path: pathlib.Path,
    doctrine_path: pathlib.Path,
    constellation_path: pathlib.Path,
    scenario: str,
) -> dict[str, Any]:
    """Decide which of R001 / R002 / R003 would fire given current state.

    Parameters
    ----------
    ledger_path:
        Path to ``ledger/events.jsonl`` (read-only).
    doctrine_path:
        Path to the on-disk ``doctrine.toml`` whose drift you want to
        check (read-only).
    constellation_path:
        Path to the on-disk ``constellation.toml`` (read-only).
    scenario:
        One of ``"doctrine_drift"``, ``"constellation_drift"``,
        ``"binary_stale"``, or ``"all"``.

    Returns
    -------
    dict
        See module docstring; stable keys with sorted list values and
        a deterministic ``ordered_summary``.
    """
    errors: list[str] = []

    selected = _SCENARIOS.get(scenario)
    if selected is None:
        errors.append(f"unknown_scenario:{scenario!r}")
        selected = set()

    ledger_p = pathlib.Path(ledger_path)
    doctrine_p = pathlib.Path(doctrine_path)
    constellation_p = pathlib.Path(constellation_path)

    amendment, amendment_line, total_entries = _find_latest_by_event(
        ledger_p, _AMENDMENT_EVENTS
    )
    verify_entry, verify_line, _ = _find_latest_by_event(
        ledger_p, {_VERIFY_EVENT}
    )

    doctrine_hash_on_disk = _file_hash_lf(doctrine_p) if doctrine_p.exists() else None
    if not doctrine_p.exists() and selected.intersection({
        "R001_doctrine_drift", "R003_binary_stale"
    }):
        errors.append("doctrine_file_missing")
    constellation_hash_on_disk = (
        _file_hash_lf(constellation_p) if constellation_p.exists() else None
    )
    if not constellation_p.exists() and "R002_constellation_drift" in selected:
        errors.append("constellation_file_missing")

    latest_amend_doctrine_hash = (
        amendment.get("doctrine_hash") if isinstance(amendment, dict) else None
    )
    latest_amend_constellation_hash = (
        amendment.get("constellation_hash") if isinstance(amendment, dict) else None
    )
    latest_verify_doctrine_hash = (
        verify_entry.get("doctrine_hash") if isinstance(verify_entry, dict) else None
    )

    would_fire: dict[str, bool] = {}
    for rule in (
        "R001_doctrine_drift",
        "R002_constellation_drift",
        "R003_binary_stale",
    ):
        would_fire[rule] = False

    if "R001_doctrine_drift" in selected:
        if doctrine_hash_on_disk is not None and latest_amend_doctrine_hash is not None:
            would_fire["R001_doctrine_drift"] = (
                doctrine_hash_on_disk != latest_amend_doctrine_hash
            )
        elif latest_amend_doctrine_hash is None:
            errors.append("no_doctrine_amendment_in_ledger")

    if "R002_constellation_drift" in selected:
        if (
            constellation_hash_on_disk is not None
            and latest_amend_constellation_hash is not None
        ):
            would_fire["R002_constellation_drift"] = (
                constellation_hash_on_disk != latest_amend_constellation_hash
            )
        elif latest_amend_constellation_hash is None:
            errors.append("no_constellation_hash_in_latest_amendment")

    if "R003_binary_stale" in selected:
        if (
            latest_verify_doctrine_hash is not None
            and latest_amend_doctrine_hash is not None
        ):
            would_fire["R003_binary_stale"] = (
                latest_verify_doctrine_hash != latest_amend_doctrine_hash
            )
        elif latest_verify_doctrine_hash is None:
            errors.append("no_verify_result_in_ledger")

    fire_count = sum(1 for rule in selected if would_fire.get(rule))
    summary: list[str] = [
        f"scenario:{scenario}",
        f"scenarios_checked:{len(selected)}",
        f"ledger_entry_count:{total_entries}",
        f"rules_would_fire:{fire_count}",
    ]
    for rule in sorted(selected):
        summary.append(f"would_fire:{rule}:{str(would_fire[rule]).lower()}")
    if amendment_line is not None:
        summary.append(f"latest_amendment_line:{amendment_line}")
    if verify_line is not None:
        summary.append(f"latest_verify_line:{verify_line}")
    summary.sort()

    return {
        "scenario": scenario,
        "scenarios_checked": sorted(selected),
        "would_fire": would_fire,
        "doctrine_hash_on_disk": doctrine_hash_on_disk,
        "latest_amendment_doctrine_hash": latest_amend_doctrine_hash,
        "constellation_hash_on_disk": constellation_hash_on_disk,
        "latest_amendment_constellation_hash": latest_amend_constellation_hash,
        "latest_verify_doctrine_hash": latest_verify_doctrine_hash,
        "latest_amendment_line": amendment_line,
        "latest_verify_line": verify_line,
        "ledger_entry_count": total_entries,
        "errors": sorted(errors),
        "ordered_summary": summary,
    }
