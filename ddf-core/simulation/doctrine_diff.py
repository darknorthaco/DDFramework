"""Doctrine diff simulator (STUB — Phase 6).

Computes a semantic diff between two doctrine.toml versions:
added/removed invariants, changed ritual registry, version delta,
and an impact classification (patch / minor / major / breaking).

Phase 5: namespace reserved; no implementation.
"""

from __future__ import annotations
from typing import Any


def run(before_toml: str, after_toml: str) -> dict[str, Any]:
    """Phase 6: compute a semantic diff of two doctrine documents."""
    raise NotImplementedError(
        "doctrine_diff.run is a Phase 6 stub; see ddf-core/simulation/README.md"
    )
