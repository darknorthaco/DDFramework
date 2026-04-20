"""Entry point for `python -m ghost`.

Subcommands:
    python -m ghost                   ledger summary (default, read-only)
    python -m ghost <path>            summary of a specific ledger file
    python -m ghost advise            run advisor; append advisories
    python -m ghost verify-advisories validate advisory stream chain

The summary mode is read-only on the main ledger (and on everything).
The `advise` mode is read-only on the main ledger and writes only to
`advisories/stream.jsonl` (Shrike I8).
"""

from __future__ import annotations
import pathlib
import sys

from .advisor import run as run_advisor
from .advisory_writer import verify_chain as verify_advisory_chain
from .reader import ZERO_HASH, iter_entries, verify


DEFAULT_LEDGER = pathlib.Path("ledger/events.jsonl")
DEFAULT_DOCTRINE = pathlib.Path("doctrine.toml")
DEFAULT_CONSTELLATION = pathlib.Path("constellation.toml")
DEFAULT_WAIVERS = pathlib.Path("WAIVERS.md")
DEFAULT_ADVISORIES = pathlib.Path("advisories/stream.jsonl")


def _summary(path: pathlib.Path) -> int:
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

    print(f"ghost: ledger OK - {result.count} entries")
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


def _advise() -> int:
    advisories, run_id, head = run_advisor(
        ledger_path=DEFAULT_LEDGER,
        doctrine_path=DEFAULT_DOCTRINE,
        constellation_path=DEFAULT_CONSTELLATION,
        waivers_path=DEFAULT_WAIVERS,
        advisory_path=DEFAULT_ADVISORIES,
    )
    by_sev = {"info": 0, "warn": 0, "critical": 0}
    for a in advisories:
        by_sev[a.severity] = by_sev.get(a.severity, 0) + 1

    print(f"ghost advise: run_id={run_id}")
    print(f"  stream head            = {head}")
    print(
        f"  advisories from rules  = {len(advisories)} "
        f"(info={by_sev['info']} warn={by_sev['warn']} critical={by_sev['critical']})"
    )
    if not advisories:
        print("  state: clean (bootstrap entry present if this was first run)")
        return 0
    print("  entries:")
    for a in advisories:
        print(f"    [{a.severity:<8}] {a.rule_id}: {a.subject}")
    # Return non-zero for any critical advisory so CI can gate.
    if by_sev["critical"] > 0:
        return 1
    return 0


def _verify_advisories() -> int:
    ok, count, head, err = verify_advisory_chain(DEFAULT_ADVISORIES)
    if not ok:
        print(f"ghost verify-advisories: chain BROKEN", file=sys.stderr)
        print(f"  count before break = {count}", file=sys.stderr)
        print(f"  last valid head    = {head}", file=sys.stderr)
        print(f"  error              = {err}", file=sys.stderr)
        return 2
    print(f"ghost verify-advisories: OK - {count} advisories, chain valid")
    print(f"  head advisory_hash = {head}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    if len(argv) <= 1:
        return _summary(DEFAULT_LEDGER)
    first = argv[1]
    if first == "advise":
        return _advise()
    if first == "verify-advisories":
        return _verify_advisories()
    # Fall through: positional ledger path for the summary view.
    return _summary(pathlib.Path(first))


if __name__ == "__main__":
    sys.exit(main())
