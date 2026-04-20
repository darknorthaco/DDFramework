#!/usr/bin/env python3
"""Write the genesis ledger entry for Shrike.

Single-purpose bootstrap script. Writes exactly one NDJSON line to
ledger/events.jsonl with the doctrine-amendment event that ratifies
Constellation Doctrine v0.1.1. Canonical-form hashing per
ledger/SPEC.md §5.

This file is committed alongside ledger/events.jsonl so the derivation
of the genesis entry_hash is reproducible a century from now.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import sys

ZERO_HASH = "sha256:" + "0" * 64

DOCTRINE_HASH = "sha256:27e11460eaa3aafe3d4910d32fbf131179c3a4386180419e5108af36a4d742af"
CONSTELLATION_HASH = "sha256:400b1da3dbb9e106e10b834ba00c5ca0efea390df0c72d8db88083dc4f733fdd"

CHANGE = (
    "Ratified Constellation Doctrine v0.1.1 as constitutional layer "
    "above Shrike architectural doctrine v0.1.0. Project "
    "doctrine_version bumped 0.1.0 -> 0.2.0 (minor: added "
    "constitutional layer; no invariants weakened). Genesis ledger entry."
)


def canonical_bytes(obj: dict) -> bytes:
    """RFC-8785-subset canonical form: sorted keys, no insignificant whitespace, UTF-8."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def main() -> int:
    entry = {
        "timestamp": "2026-04-20T00:00:00Z",
        "event": "doctrine_amendment",
        "version": "0.2.0",
        "change": CHANGE,
        "domain": "complicated",
        "integrity_check": True,
        "regenerative_check": True,
        "simulation_required": False,
        "disruption_considered": True,
        "doctrine_hash": DOCTRINE_HASH,
        "constellation_hash": CONSTELLATION_HASH,
        "prev_entry_hash": ZERO_HASH,
    }

    entry_hash = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()

    ordered = dict(sorted(entry.items()))
    ordered["entry_hash"] = entry_hash
    line = json.dumps(ordered, separators=(",", ":"), ensure_ascii=False) + "\n"

    out = pathlib.Path(__file__).parent / "events.jsonl"
    out.write_bytes(line.encode("utf-8"))

    print(f"wrote:        {out}")
    print(f"entry_hash =  {entry_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
