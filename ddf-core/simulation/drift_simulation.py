"""Drift simulator (STUB — Phase 6).

Synthesizes un-ceremonied-edit scenarios (doctrine edited but
amend-doctrine not run) and confirms that GHOST R001/R002/R003 fire
at the expected severities. Used to guard rule logic against silent
regressions.

Phase 5: namespace reserved; no implementation.
"""

from __future__ import annotations
import pathlib
from typing import Any


def run(
    ledger_path: pathlib.Path,
    doctrine_path: pathlib.Path,
    constellation_path: pathlib.Path,
    scenario: str,
) -> dict[str, Any]:
    """Phase 6: synthesize a drift scenario and return observed advisories."""
    raise NotImplementedError(
        "drift_simulation.run is a Phase 6 stub; see ddf-core/simulation/README.md"
    )
