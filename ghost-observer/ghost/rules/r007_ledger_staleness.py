"""R007 — ledger staleness.

Fires when the most recent ledger entry's `timestamp` is far enough in
the past that the fabric may be dead without anyone noticing.

Severity ladder:
  - > 365 days: critical
  - >  90 days: warn
  - >  30 days: info
  - <= 30 days: no advisory
"""

from __future__ import annotations
from datetime import datetime, timezone

from ..model import Advisory, AdvisorContext


def check(ctx: AdvisorContext) -> list[Advisory]:
    if not ctx.ledger_entries:
        return []
    last = ctx.ledger_entries[-1]
    ts_str = last.get("timestamp")
    if not ts_str:
        return []

    # Parse RFC 3339 UTC; our writer emits "YYYY-MM-DDTHH:MM:SSZ".
    try:
        last_ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return []
    if last_ts.tzinfo is None:
        last_ts = last_ts.replace(tzinfo=timezone.utc)
    now = ctx.now if ctx.now.tzinfo else ctx.now.replace(tzinfo=timezone.utc)

    days_stale = (now - last_ts).days
    if days_stale <= 30:
        return []

    if days_stale > 365:
        severity = "critical"
    elif days_stale > 90:
        severity = "warn"
    else:
        severity = "info"

    return [
        Advisory(
            rule_id="R007_ledger_staleness",
            severity=severity,
            subject=f"ledger has been idle for {days_stale} days",
            evidence={
                "last_entry_timestamp": ts_str,
                "last_entry_event": last.get("event"),
                "days_stale": days_stale,
            },
            recommended_action=(
                "Run `ddf-exec verify` to record a heartbeat, or investigate "
                "why the fabric has been idle."
            ),
        )
    ]
