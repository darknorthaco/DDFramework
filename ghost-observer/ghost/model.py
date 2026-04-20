"""Pure data types for the GHOST advisor.

This module has NO dependencies on other ghost modules, no I/O, and no
side effects. It exists so rule modules can import types without
triggering circular imports via advisor.py.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


SEVERITIES = ("info", "warn", "critical")


@dataclass(frozen=True)
class Advisory:
    """A single advisory produced by a rule.

    `evidence` may contain nested dicts/lists/strings/numbers/bools.
    The advisory_writer will serialize it in canonical form for hashing.
    """
    rule_id: str
    severity: str
    subject: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommended_action: str = ""

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(
                f"Advisory severity must be one of {SEVERITIES}, got {self.severity!r}"
            )


@dataclass(frozen=True)
class AdvisorContext:
    """Snapshot of system state passed to every rule.

    Built once per advisor run and handed to each rule's check function.
    Rules MUST treat this as read-only.
    """
    ledger_entries: list[dict[str, Any]]
    doctrine_hash: str
    constellation_hash: str
    waivers_md_text: str
    now: datetime
