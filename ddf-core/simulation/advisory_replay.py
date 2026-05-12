"""Advisory replay — Phase 6 simulation module.

Walk ``advisories/stream.jsonl`` from genesis, recompute the
canonical hash chain per ``advisories/SPEC.md`` §4, and report
counts by rule id and severity, run-id grouping, and whether each
advisory's ``ledger_tail_hash`` resolves to an entry in the main
ledger.

Stdlib-only; pure function; **read-only** on both streams (both
opened ``"rb"``; no writes anywhere). Honors invariant I5 (no
ambient state): advisory path and ledger path are explicit
arguments.

Canonical form (matching ``advisories/SPEC.md`` §4 and
``ledger/SPEC.md`` §5):

- JSON object **without** the ``advisory_hash`` field.
- ``json.dumps`` with ``sort_keys=True``, ``separators=(',', ':')``,
  ``ensure_ascii=False``; UTF-8; no trailing newline.
- ``advisory_hash = "sha256:" + sha256(canonical_bytes).hex()``.
- Genesis: ``prev_advisory_hash`` is ``"sha256:" + "0" * 64``.

Per ``advisories/SPEC.md`` §7 every advisory may reference a ledger
``ledger_tail_hash``. This module verifies that each referenced
hash exists somewhere in the ledger's known ``entry_hash`` set
(checked without re-verifying the ledger chain — for that, run
``ledger_replay`` separately and compose the results).
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


def _collect_ledger_entry_hashes(ledger_path: pathlib.Path) -> set[str]:
    """Return the set of ``entry_hash`` strings in the ledger file.

    Does not verify the chain; failures fall back to an empty set so
    the caller can still report advisory-side chain integrity.
    """
    if not ledger_path.exists():
        return set()
    out: set[str] = set()
    try:
        with open(ledger_path, "rb") as f:
            for raw in f:
                if not raw.strip():
                    continue
                try:
                    entry = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                eh = entry.get("entry_hash")
                if isinstance(eh, str):
                    out.add(eh)
    except OSError:
        return out
    return out


def run(advisory_path: pathlib.Path, ledger_path: pathlib.Path) -> dict[str, Any]:
    """Replay the advisory stream and return a structured audit report.

    Parameters
    ----------
    advisory_path:
        Path to ``advisories/stream.jsonl`` (opened ``"rb"``).
    ledger_path:
        Path to ``ledger/events.jsonl`` (opened ``"rb"``). Used only
        to verify that each advisory's ``ledger_tail_hash`` references
        a known ledger entry. The ledger's own chain is **not**
        re-verified here; compose with ``ledger_replay`` for that.

    Returns
    -------
    dict
        Stable keys: ``advisory_path_exists``, ``ledger_path_exists``,
        ``advisory_count``, ``chain_ok``, ``chain_break_at_line``,
        ``chain_error``, ``rule_id_counts`` (key-sorted dict),
        ``severity_counts`` (key-sorted dict), ``run_ids`` (sorted
        unique), ``run_count``, ``tail_hashes_present_in_ledger``,
        ``tail_hashes_missing``, ``tail_hash_missing_lines`` (sorted
        list of line numbers), ``head_hash``, ``genesis_prev_hash``,
        ``errors`` (sorted), ``ordered_summary`` (sorted,
        deterministic).
    """
    advisory_p = pathlib.Path(advisory_path)
    ledger_p = pathlib.Path(ledger_path)

    errors: list[str] = []

    if not advisory_p.exists():
        return _empty_report(
            advisory_exists=False,
            ledger_exists=ledger_p.exists(),
            errors=errors + ["advisory_stream_missing"],
        )

    ledger_hashes = _collect_ledger_entry_hashes(ledger_p)

    advisory_count = 0
    chain_ok = True
    chain_break_at_line: int | None = None
    chain_error: str | None = None
    rule_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    run_ids: set[str] = set()
    tails_present = 0
    tails_missing_lines: list[int] = []
    genesis_prev: str | None = None
    head_hash = ZERO_HASH

    prev_hash = ZERO_HASH
    with open(advisory_p, "rb") as f:
        for lineno, raw in enumerate(f, start=1):
            if not raw.strip():
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

            stored_hash = entry.pop("advisory_hash", None)
            if not isinstance(stored_hash, str):
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = f"missing_advisory_hash:{lineno}"
                errors.append(chain_error)
                break

            recomputed = _recomputed_hash(entry)
            if recomputed != stored_hash:
                chain_ok = False
                chain_break_at_line = lineno
                chain_error = (
                    f"advisory_hash_mismatch:{lineno}:stored={stored_hash}:recomputed={recomputed}"
                )
                errors.append(chain_error)
                break

            stored_prev = entry.get("prev_advisory_hash")
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

            rule_id = entry.get("rule_id")
            if isinstance(rule_id, str):
                rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            severity = entry.get("severity")
            if isinstance(severity, str):
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            run_id = entry.get("run_id")
            if isinstance(run_id, str) and run_id:
                run_ids.add(run_id)

            tail = entry.get("ledger_tail_hash")
            if isinstance(tail, str):
                # Genesis advisory (R000_bootstrap) references the ledger head
                # *as of stream init*; both are real ledger entries unless the
                # ledger has been truncated. Treat presence-only as the check.
                if ledger_hashes and tail not in ledger_hashes:
                    tails_missing_lines.append(lineno)
                elif ledger_hashes:
                    tails_present += 1

            advisory_count += 1
            head_hash = stored_hash
            prev_hash = stored_hash

    ordered = [
        f"advisory_count:{advisory_count}",
        f"chain_ok:{str(chain_ok).lower()}",
        f"run_count:{len(run_ids)}",
        f"rule_kinds_total:{len(rule_counts)}",
        f"tail_hashes_present_in_ledger:{tails_present}",
        f"tail_hashes_missing:{len(tails_missing_lines)}",
    ]
    if chain_break_at_line is not None:
        ordered.append(f"chain_break_at_line:{chain_break_at_line}")
    for rule, count in rule_counts.items():
        ordered.append(f"rule:{rule}:{count}")
    for sev, count in severity_counts.items():
        ordered.append(f"severity:{sev}:{count}")
    ordered.sort()

    return {
        "advisory_path_exists": True,
        "ledger_path_exists": ledger_p.exists(),
        "advisory_count": advisory_count,
        "chain_ok": chain_ok,
        "chain_break_at_line": chain_break_at_line,
        "chain_error": chain_error,
        "rule_id_counts": dict(sorted(rule_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "run_ids": sorted(run_ids),
        "run_count": len(run_ids),
        "tail_hashes_present_in_ledger": tails_present,
        "tail_hashes_missing": len(tails_missing_lines),
        "tail_hash_missing_lines": sorted(tails_missing_lines),
        "head_hash": head_hash,
        "genesis_prev_hash": genesis_prev,
        "errors": sorted(errors),
        "ordered_summary": ordered,
    }


def _empty_report(
    *, advisory_exists: bool, ledger_exists: bool, errors: list[str]
) -> dict[str, Any]:
    return {
        "advisory_path_exists": advisory_exists,
        "ledger_path_exists": ledger_exists,
        "advisory_count": 0,
        "chain_ok": False,
        "chain_break_at_line": None,
        "chain_error": errors[0] if errors else None,
        "rule_id_counts": {},
        "severity_counts": {},
        "run_ids": [],
        "run_count": 0,
        "tail_hashes_present_in_ledger": 0,
        "tail_hashes_missing": 0,
        "tail_hash_missing_lines": [],
        "head_hash": ZERO_HASH,
        "genesis_prev_hash": None,
        "errors": sorted(errors),
        "ordered_summary": sorted(
            [
                "advisory_count:0",
                "chain_ok:false",
                f"advisory_path_exists:{str(advisory_exists).lower()}",
                f"ledger_path_exists:{str(ledger_exists).lower()}",
            ]
        ),
    }
