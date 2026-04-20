"""R002 — constellation drift.

Like R001 but for `constellation.toml`. Catches un-ceremonied edits to
the constitutional layer.
"""

from __future__ import annotations

from ..model import Advisory, AdvisorContext

AMENDMENT_EVENTS = frozenset({"doctrine_amendment", "doctrine.amended"})


def check(ctx: AdvisorContext) -> list[Advisory]:
    last = _last_amendment(ctx)
    if last is None:
        return []
    recorded = last.get("constellation_hash")
    if not recorded:
        return []
    if recorded == ctx.constellation_hash:
        return []
    return [
        Advisory(
            rule_id="R002_constellation_drift",
            severity="warn",
            subject="constellation.toml has drifted from the last recorded amendment",
            evidence={
                "current_on_disk": ctx.constellation_hash,
                "last_amended_hash": recorded,
                "last_amended_timestamp": last.get("timestamp"),
            },
            recommended_action=(
                "Either revert the constellation edit or run "
                "`phantom amend-doctrine` with an appropriate rationale "
                "to record the amendment to the constitutional layer."
            ),
        )
    ]


def _last_amendment(ctx: AdvisorContext) -> dict | None:
    for entry in reversed(ctx.ledger_entries):
        if entry.get("event") in AMENDMENT_EVENTS:
            return entry
    return None
