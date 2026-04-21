"""ddf — DDFramework kernel Python API.

Kernel API version: 0.1.0
Engine doctrine_version it binds to: 0.7.0

Re-exports stable surface from the `ghost-observer` package under the
kernel namespace. Zero new behavior.
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
__version__ = "0.1.0"
"""Kernel API SemVer; governs the stability contract of the `ddf` package."""

ENGINE_VERSION = "0.7.0"
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
    """Verify the main-ledger hash chain. Returns a `ghost.reader.ChainResult`.

    Behavior-identical to `python -m ghost <path>` summary mode.
    """
    defaults = _default_paths()
    target = _pathlib.Path(path) if path is not None else defaults["ledger_path"]
    return reader.verify(target)


def advise(**overrides) -> tuple:
    """Run the GHOST advisor. Returns `(advisories, run_id, head_advisory_hash)`.

    Any of the five path arguments may be overridden via keyword:
    `ledger_path`, `doctrine_path`, `constellation_path`,
    `waivers_path`, `advisory_path`.
    """
    defaults = _default_paths()
    defaults.update({k: _pathlib.Path(v) for k, v in overrides.items()})
    return advisor.run(**defaults)
