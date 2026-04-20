"""Entry point for `python -m ghost`.

Walks the ledger, prints chain-status summary. Exits non-zero on any
chain break. Read-only by construction.
"""

from __future__ import annotations
import pathlib
import sys

from .reader import ZERO_HASH, iter_entries, verify


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    path = pathlib.Path(argv[1]) if len(argv) >= 2 else pathlib.Path("ledger/events.jsonl")

    if not path.exists():
        print(f"ghost: ledger not found at {path}", file=sys.stderr)
        return 2

    result = verify(path)

    if not result.ok:
        print(f"ghost: chain BROKEN at {path}", file=sys.stderr)
        print(f"  count before break  = {result.count}", file=sys.stderr)
        print(f"  last valid head     = {result.head_hash}", file=sys.stderr)
        print(f"  error               = {result.error}", file=sys.stderr)
        return 2

    print(f"ghost: ledger OK — {result.count} entries")
    print(f"  head entry_hash = {result.head_hash}")
    print("  entries:")
    for e in iter_entries(path):
        event = e.data.get("event", "?")
        version = e.data.get("version", "?")
        ts = e.data.get("timestamp", "?")
        status = e.data.get("status", "")
        status_str = f" status={status}" if status else ""
        print(f"    #{e.line_no:>3}  {ts}  {event:<22} v{version}{status_str}")

    if result.head_hash == ZERO_HASH:
        print("ghost: (ledger empty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
