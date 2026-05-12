"""Shrike GHOST — read-only observer for the DDFramework engine ledger.

Stdlib-only runtime dependencies. See LANGUAGES.md §3.3.
"""

__version__ = "1.0.0"
__all__ = ["__version__", "reader"]

from . import reader  # noqa: E402  (re-export after __version__)
