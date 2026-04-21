"""Ritual dry-run simulator (STUB — Phase 6).

Executes a ritual end-to-end without writing to the ledger. Returns
the would-be ledger entry plus any derived state.

Phase 5: namespace reserved; no implementation.
"""

from __future__ import annotations
from typing import Any


def run(ritual_id: str, args: dict[str, Any]) -> dict[str, Any]:
    """Phase 6: simulate a ritual without side effects."""
    raise NotImplementedError(
        "ritual_dryrun.run is a Phase 6 stub; see ddf-core/simulation/README.md"
    )
