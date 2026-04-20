"""R006 — timestamp regression.

Fires when any ledger entry's `timestamp` is strictly earlier than
the previous entry's `timestamp`. Indicates a clock anomaly or
deliberate backdating. Critical severity.

Equal timestamps are allowed (common when two ceremonies happen in
the same second).
"""

from __future__ import annotations

from ..model import Advisory, AdvisorContext


def check(ctx: AdvisorContext) -> list[Advisory]:
    advisories: list[Advisory] = []
    prev_ts: str | None = None
    for entry in ctx.ledger_entries:
        ts = entry.get("timestamp")
        if prev_ts and ts and ts < prev_ts:
            advisories.append(
                Advisory(
                    rule_id="R006_timestamp_regression",
                    severity="critical",
                    subject="ledger timestamp regression detected",
                    evidence={
                        "previous_timestamp": prev_ts,
                        "current_timestamp": ts,
                        "entry_hash": entry.get("entry_hash"),
                        "event": entry.get("event"),
                    },
                    recommended_action=(
                        "Investigate: system clock anomaly, deliberate "
                        "backdating, or a ledger replay. File a waiver "
                        "(ritual 0005) if the regression is expected."
                    ),
                )
            )
        if ts:
            prev_ts = ts
    return advisories
