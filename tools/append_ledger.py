#!/usr/bin/env python3
"""Shrike ledger append helper — stdlib-only.

Appends one ceremony entry to ledger/events.jsonl with proper
canonical-form hashing and chain linkage. Used for doctrine
amendments and phase-commit ceremonies until phantom grows more
subcommands.

Invocation (fields passed as JSON on stdin or via --fields):
    python tools/append_ledger.py --event phase2.committed \\
        --version 0.3.0 --domain complicated \\
        --change "..." \\
        --doctrine-hash sha256:... \\
        --constellation-hash sha256:...

All mandatory fields per ledger/SPEC.md §3 are computed or required.
The tool refuses to write if the last line's canonical hash cannot be
verified (prevents accidental chain corruption).
"""

from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys
import time

ZERO_HASH = "sha256:" + "0" * 64
LEDGER_PATH = pathlib.Path("ledger/events.jsonl")


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def read_head(path: pathlib.Path) -> str:
    """Return the entry_hash of the last ledger line, or ZERO_HASH."""
    if not path.exists() or path.stat().st_size == 0:
        return ZERO_HASH
    with open(path, "rb") as f:
        last = None
        for raw in f:
            if raw.strip():
                last = raw
        if last is None:
            return ZERO_HASH
        entry = json.loads(last.decode("utf-8"))
        stored = entry.pop("entry_hash", None)
        if stored is None:
            sys.exit("append_ledger: last line missing entry_hash; refusing to append.")
        recomputed = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
        if recomputed != stored:
            sys.exit(
                f"append_ledger: last line entry_hash mismatch; refusing to append.\n"
                f"  stored:     {stored}\n"
                f"  recomputed: {recomputed}"
            )
        return stored


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--domain", required=True, choices=["obvious", "complicated", "complex", "chaotic"])
    ap.add_argument("--change", required=True)
    ap.add_argument("--doctrine-hash", required=True, dest="doctrine_hash")
    ap.add_argument("--constellation-hash", required=True, dest="constellation_hash")
    ap.add_argument("--integrity-check", default="true", choices=["true", "false"])
    ap.add_argument("--regenerative-check", default="true", choices=["true", "false"])
    ap.add_argument("--simulation-required", default="false", choices=["true", "false"])
    ap.add_argument("--disruption-considered", default="true", choices=["true", "false"])
    ap.add_argument("--timestamp", default=None, help="RFC 3339 UTC; defaults to now")
    ap.add_argument("--ledger", default=str(LEDGER_PATH))
    args = ap.parse_args()

    path = pathlib.Path(args.ledger)
    prev_hash = read_head(path)

    ts = args.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    entry = {
        "timestamp": ts,
        "event": args.event,
        "version": args.version,
        "change": args.change,
        "domain": args.domain,
        "integrity_check": args.integrity_check == "true",
        "regenerative_check": args.regenerative_check == "true",
        "simulation_required": args.simulation_required == "true",
        "disruption_considered": args.disruption_considered == "true",
        "doctrine_hash": args.doctrine_hash,
        "constellation_hash": args.constellation_hash,
        "prev_entry_hash": prev_hash,
    }

    entry_hash = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
    ordered = dict(sorted(entry.items()))
    ordered["entry_hash"] = entry_hash
    line = json.dumps(ordered, separators=(",", ":"), ensure_ascii=False) + "\n"

    with open(path, "ab") as f:
        f.write(line.encode("utf-8"))

    print(f"appended: {entry_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
