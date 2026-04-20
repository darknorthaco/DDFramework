"""GHOST advisor orchestrator.

Builds an AdvisorContext from the repo state, runs the rule registry,
and appends any emitted advisories to the advisory stream. Bootstraps
the stream on first run.

Read-only on the main ledger (Shrike I8). The only file this module
causes to be written is the advisory stream, via AdvisoryWriter.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import secrets
import time
from datetime import datetime, timezone

from .advisory_writer import AdvisoryWriter, ZERO_HASH
from .model import Advisory, AdvisorContext
from .reader import iter_entries
from .rules import RULES


GHOST_VERSION = "0.5.0"
RULESET_IDS = [
    "R001_doctrine_drift",
    "R002_constellation_drift",
    "R003_binary_stale",
    "R004_waiver_expiring",
    "R005_unknown_event_kind",
    "R006_timestamp_regression",
    "R007_ledger_staleness",
]


def sha256_file_normalized(path: pathlib.Path) -> str:
    data = path.read_bytes().replace(b"\r", b"")
    return hashlib.sha256(data).hexdigest()


def _read_ledger_as_dicts(path: pathlib.Path) -> list[dict]:
    """Read and validate the main ledger; return entries as dicts.

    Uses the chain-validating iterator so GHOST refuses to advise on a
    corrupt ledger.
    """
    if not path.exists():
        return []
    out: list[dict] = []
    for entry in iter_entries(path):
        out.append(entry.data)
    return out


def _current_ledger_tail(path: pathlib.Path) -> str:
    """Return the entry_hash of the last ledger line, or ZERO_HASH."""
    if not path.exists() or path.stat().st_size == 0:
        return ZERO_HASH
    last = None
    with open(path, "rb") as f:
        for raw in f:
            if raw.strip():
                last = raw
    if last is None:
        return ZERO_HASH
    return json.loads(last.decode("utf-8")).get("entry_hash", ZERO_HASH)


def build_context(
    ledger_path: pathlib.Path,
    doctrine_path: pathlib.Path,
    constellation_path: pathlib.Path,
    waivers_path: pathlib.Path,
    now: datetime | None = None,
) -> AdvisorContext:
    return AdvisorContext(
        ledger_entries=_read_ledger_as_dicts(ledger_path),
        doctrine_hash=f"sha256:{sha256_file_normalized(doctrine_path)}"
        if doctrine_path.exists()
        else "",
        constellation_hash=f"sha256:{sha256_file_normalized(constellation_path)}"
        if constellation_path.exists()
        else "",
        waivers_md_text=waivers_path.read_text(encoding="utf-8") if waivers_path.exists() else "",
        now=now or datetime.now(timezone.utc),
    )


def _bootstrap_advisory() -> Advisory:
    return Advisory(
        rule_id="R000_bootstrap",
        severity="info",
        subject="GHOST advisory stream initialized",
        evidence={
            "ghost_version": GHOST_VERSION,
            "ruleset": RULESET_IDS,
        },
        recommended_action="No action; this is the genesis of the advisory stream.",
    )


def run(
    ledger_path: pathlib.Path,
    doctrine_path: pathlib.Path,
    constellation_path: pathlib.Path,
    waivers_path: pathlib.Path,
    advisory_path: pathlib.Path,
    now: datetime | None = None,
) -> tuple[list[Advisory], str, str]:
    """Run the advisor once.

    Returns (advisories_written, run_id, head_advisory_hash).
    """
    ctx = build_context(
        ledger_path, doctrine_path, constellation_path, waivers_path, now=now
    )
    ledger_tail = _current_ledger_tail(ledger_path)
    run_id = secrets.token_hex(8)

    advisories: list[Advisory] = []
    for rule_check in RULES:
        advisories.extend(list(rule_check(ctx)))

    writer = AdvisoryWriter(advisory_path)

    # Bootstrap on first run.
    if writer.is_empty():
        writer.append(_bootstrap_advisory(), run_id=run_id, ledger_tail_hash=ledger_tail)

    # Slight delay so bootstrap and rule advisories do not collide on the
    # same second; keeps the stream monotonically ordered when inspected
    # with human eyes. One-time cost per run; does not affect behavior.
    time.sleep(1.0 if not advisories else 0)

    head = writer.current_head()
    for adv in advisories:
        head = writer.append(adv, run_id=run_id, ledger_tail_hash=ledger_tail)

    return advisories, run_id, head
