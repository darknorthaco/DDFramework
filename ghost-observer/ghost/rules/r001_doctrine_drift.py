"""R001 — doctrine drift.

Fires when `doctrine.toml` on disk (normalized hash) differs from the
hash recorded in the most recent `doctrine.amended` or
`doctrine_amendment` ledger entry. This catches un-ceremonied edits
to the architectural doctrine.
"""

from __future__ import annotations

from ..model import Advisory, AdvisorContext

AMENDMENT_EVENTS = frozenset({"doctrine_amendment", "doctrine.amended"})


def check(ctx: AdvisorContext) -> list[Advisory]:
    last = _last_amendment(ctx)
    if last is None:
        return []
    recorded = last.get("doctrine_hash")
    if not recorded:
        return []
    if recorded == ctx.doctrine_hash:
        return []
    return [
        Advisory(
            rule_id="R001_doctrine_drift",
            severity="warn",
            subject="doctrine.toml has drifted from the last recorded amendment",
            evidence={
                "current_on_disk": ctx.doctrine_hash,
                "last_amended_hash": recorded,
                "last_amended_timestamp": last.get("timestamp"),
                "last_amended_version": last.get("version"),
            },
            recommended_action=(
                "Either revert the edit, or run "
                "`phantom amend-doctrine --version <v> --rationale \"...\" "
                "--domain <cynefin> --approve` to record the ceremony."
            ),
        )
    ]


def _last_amendment(ctx: AdvisorContext) -> dict | None:
    for entry in reversed(ctx.ledger_entries):
        if entry.get("event") in AMENDMENT_EVENTS:
            return entry
    return None
