"""Advisory replay simulator (STUB — Phase 6).

Walks the advisory stream; for each advisory, verifies that the rule
would produce the same advisory given the ledger tail recorded in
`ledger_tail_hash`. Detects: stale rule logic, ledger-advisory
desync, hash-chain breaks.

Phase 5: namespace reserved; no implementation.
"""

from __future__ import annotations
import pathlib
from typing import Any


def run(advisory_path: pathlib.Path, ledger_path: pathlib.Path) -> dict[str, Any]:
    """Phase 6: replay the advisory stream and return a structured report."""
    raise NotImplementedError(
        "advisory_replay.run is a Phase 6 stub; see ddf-core/simulation/README.md"
    )
