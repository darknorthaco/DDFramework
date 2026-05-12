"""R003 — binary stale.

Fires when the most recent `verify.result` entry recorded a
`doctrine_hash` that does not match the most recent
`doctrine.amended` / `doctrine_amendment` entry. That means the
currently-running phantom binary was built against an older doctrine
than the current one.
"""

from __future__ import annotations

from ..model import Advisory, AdvisorContext

AMENDMENT_EVENTS = frozenset({"doctrine_amendment", "doctrine.amended"})


def check(ctx: AdvisorContext) -> list[Advisory]:
    last_verify = _last_by_event(ctx, "verify.result")
    if last_verify is None:
        return []
    last_amended = _last_by_events(ctx, AMENDMENT_EVENTS)
    if last_amended is None:
        return []

    verify_hash = last_verify.get("doctrine_hash")
    amended_hash = last_amended.get("doctrine_hash")
    if not verify_hash or not amended_hash or verify_hash == amended_hash:
        return []

    return [
        Advisory(
            rule_id="R003_binary_stale",
            severity="warn",
            subject="most recent ddf-exec verify ran against an older doctrine",
            evidence={
                "verify_doctrine_hash": verify_hash,
                "amended_doctrine_hash": amended_hash,
                "verify_timestamp": last_verify.get("timestamp"),
                "amended_timestamp": last_amended.get("timestamp"),
            },
            recommended_action=(
                "Rebuild ddf-exec (`make build`) and run `ddf-exec verify` "
                "to record a fresh verify.result against the current doctrine."
            ),
        )
    ]


def _last_by_event(ctx: AdvisorContext, event: str) -> dict | None:
    for entry in reversed(ctx.ledger_entries):
        if entry.get("event") == event:
            return entry
    return None


def _last_by_events(ctx: AdvisorContext, events: frozenset) -> dict | None:
    for entry in reversed(ctx.ledger_entries):
        if entry.get("event") in events:
            return entry
    return None
