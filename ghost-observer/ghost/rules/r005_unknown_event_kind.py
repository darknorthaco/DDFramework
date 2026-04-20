"""R005 — unknown event kind.

Fires when the ledger contains an `event` value not in the known
registry. Indicates stale tooling or an event that was never
registered in `ledger/SPEC.md §7`.

Known kinds are listed below and MUST stay in sync with `ledger/SPEC.md`.
"""

from __future__ import annotations

from ..model import Advisory, AdvisorContext

KNOWN_EVENT_KINDS = frozenset({
    # Active registry (ledger/SPEC.md §7)
    "doctrine_amendment",
    "doctrine.amended",
    "verify.result",
    "deploy.applied",
    "lan.scan.result",
    "waiver.filed",
    "waiver.expired",
    "postmortem",
    "ledger_correction",
    # Bootstrap-era kinds (Phases 2-3) — retired but accepted historically.
    "phase2.committed",
    "phase3.committed",
})


def check(ctx: AdvisorContext) -> list[Advisory]:
    seen: dict[str, str] = {}
    for entry in ctx.ledger_entries:
        event = entry.get("event")
        if not event:
            continue
        if event not in KNOWN_EVENT_KINDS and event not in seen:
            seen[event] = entry.get("entry_hash", "")

    return [
        Advisory(
            rule_id="R005_unknown_event_kind",
            severity="warn",
            subject=f"ledger contains unregistered event kind '{kind}'",
            evidence={"event_kind": kind, "example_entry_hash": eh},
            recommended_action=(
                "Register the event in `ledger/SPEC.md §7` and in "
                "`KNOWN_EVENT_KINDS` (rules/r005), or investigate whether "
                "it was written by stale tooling."
            ),
        )
        for kind, eh in seen.items()
    ]
