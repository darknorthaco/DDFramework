#!/usr/bin/env python3
"""Shrike ledger chain auditor — stdlib-only.

Reads ledger/events.jsonl and verifies:
  1. Every entry parses as JSON
  2. Every entry's `entry_hash` matches its canonical-form SHA-256
  3. Every `prev_entry_hash` links correctly to the previous line's
     `entry_hash` (genesis entry has prev = sha256:0000...)

Exits 0 on valid chain, non-zero on any break.

This tool intentionally has ZERO third-party dependencies. It is the
100-year safety net: any Python 3 interpreter on any platform can
audit the chain without installing anything.

Usage:
    python tools/verify_ledger.py [ledger/events.jsonl]
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import sys

ZERO_HASH = "sha256:" + "0" * 64


def canonical_bytes(obj: dict) -> bytes:
    """RFC-8785-subset canonical form: sorted keys, no whitespace, UTF-8."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_file_normalized(path: pathlib.Path) -> str:
    """SHA-256 of a text file after stripping CR bytes (LF-normalized)."""
    data = path.read_bytes().replace(b"\r", b"")
    return hashlib.sha256(data).hexdigest()


def verify(path: pathlib.Path) -> int:
    if not path.exists():
        print(f"ledger: {path} does not exist", file=sys.stderr)
        return 2

    prev_hash = ZERO_HASH
    count = 0
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f, start=1):
            if not raw.strip():
                print(f"ledger: blank line at {lineno}", file=sys.stderr)
                return 2
            try:
                entry = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                print(f"ledger: line {lineno}: invalid JSON: {exc}", file=sys.stderr)
                return 2

            stored_entry_hash = entry.pop("entry_hash", None)
            if stored_entry_hash is None:
                print(f"ledger: line {lineno}: missing entry_hash", file=sys.stderr)
                return 2

            recomputed = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
            if recomputed != stored_entry_hash:
                print(
                    f"ledger: line {lineno}: entry_hash mismatch\n"
                    f"  stored:     {stored_entry_hash}\n"
                    f"  recomputed: {recomputed}",
                    file=sys.stderr,
                )
                return 2

            stored_prev = entry.get("prev_entry_hash")
            if stored_prev != prev_hash:
                print(
                    f"ledger: line {lineno}: broken chain\n"
                    f"  expected prev_entry_hash: {prev_hash}\n"
                    f"  stored   prev_entry_hash: {stored_prev}",
                    file=sys.stderr,
                )
                return 2

            prev_hash = stored_entry_hash
            count += 1

    print(f"ledger: OK — {count} entries, chain valid from genesis.")
    print(f"  head entry_hash = {prev_hash}")
    return 0


def main(argv: list[str]) -> int:
    path = pathlib.Path(argv[1]) if len(argv) >= 2 else pathlib.Path("ledger/events.jsonl")
    return verify(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
