"""Ledger replay simulator (STUB — Phase 6).

Walks the main ledger from genesis, recomputes the hash chain, and
replays each ritual's observable effects (e.g. which blobs would be
written). Read-only; intended for disaster-recovery and audit.

Phase 5: namespace reserved; no implementation.
"""

from __future__ import annotations
import pathlib
from typing import Any


def run(ledger_path: pathlib.Path) -> dict[str, Any]:
    """Phase 6: replay the main ledger and return a structured report."""
    raise NotImplementedError(
        "ledger_replay.run is a Phase 6 stub; see ddf-core/simulation/README.md"
    )
