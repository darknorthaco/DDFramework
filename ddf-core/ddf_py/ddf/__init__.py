"""ddf — DDFramework **kernel** Python API (stable embedder surface).

Kernel API version: 1.0.0 — engine doctrine_version: 1.0.0

Mechanical roles (mission names like GHOST live in `ghost-observer`):

- ``verify`` — verify the main **append-only ledger** hash chain.
- ``advise`` — run the **read-only advisor** (rules → advisories).
- ``ledger`` / ``reader`` — **ledger reader** module.
- ``advisor`` — **advisor orchestrator** module.
- ``advisory_writer`` — append to the **advisory stream** (hash-chained NDJSON).

Re-exports the `ghost-observer` package under the `ddf` namespace. Zero new behavior.
See `GLOSSARY_ENGINE_NAMES.md` and `ddf-core/KERNEL_API_MAP.md` at the repo root.
"""

from __future__ import annotations
import pathlib as _pathlib
import sys as _sys

# Locate ghost-observer relative to the repo root and add it to
# sys.path if not already importable. The repo root is 4 levels up
# from this file: ddf-core/ddf_py/ddf/__init__.py -> repo root.
_HERE = _pathlib.Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[3]
_GHOST_PKG = _REPO_ROOT / "ghost-observer"
if _GHOST_PKG.is_dir() and str(_GHOST_PKG) not in _sys.path:
    _sys.path.insert(0, str(_GHOST_PKG))

# Version constants
__version__ = "1.0.0"
"""Kernel API SemVer; governs the stability contract of the `ddf` package."""

ENGINE_VERSION = "1.0.0"
"""Engine doctrine_version this API was released against."""

# Re-exports from the engine's advisor / reader
from ghost import reader  # noqa: E402
from ghost import advisor  # noqa: E402
from ghost import advisory_writer  # noqa: E402
from ghost import __version__ as ghost_version  # noqa: E402

# Namespace alias: `ddf.ledger` is the reader module (reading the main ledger)
ledger = reader

__all__ = [
    "__version__",
    "ENGINE_VERSION",
    "ghost_version",
    "ledger",
    "reader",
    "advisor",
    "advisory_writer",
    "verify",
    "advise",
]


def _default_paths():
    return {
        "ledger_path": _REPO_ROOT / "ledger" / "events.jsonl",
        "doctrine_path": _REPO_ROOT / "doctrine.toml",
        "constellation_path": _REPO_ROOT / "constellation.toml",
        "waivers_path": _REPO_ROOT / "WAIVERS.md",
        "advisory_path": _REPO_ROOT / "advisories" / "stream.jsonl",
    }


def verify(path: _pathlib.Path | None = None):
    """Verify the **main ledger** hash chain (read-only).

    Returns a `ghost.reader.ChainResult`. Same behavior as
    ``python -m ghost <path>`` summary mode.
    """
    defaults = _default_paths()
    target = _pathlib.Path(path) if path is not None else defaults["ledger_path"]
    return reader.verify(target)


def advise(**overrides) -> tuple:
    """Run the **advisor** (GHOST ruleset). Returns ``(advisories, run_id, head_advisory_hash)``.

    Overrides for paths: ``ledger_path``, ``doctrine_path``,
    ``constellation_path``, ``waivers_path``, ``advisory_path``.
    """
    defaults = _default_paths()
    defaults.update({k: _pathlib.Path(v) for k, v in overrides.items()})
    return advisor.run(**defaults)
