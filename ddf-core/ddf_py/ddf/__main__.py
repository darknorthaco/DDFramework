"""CLI entrypoint for `python -m ddf`.

Thin forwarder to the existing ghost CLI. Behavioral parity guaranteed
by construction.
"""

from __future__ import annotations
import sys

# Trigger ddf/__init__.py (which puts ghost-observer on sys.path).
from . import __version__, ENGINE_VERSION  # noqa: F401


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv

    if len(argv) >= 2 and argv[1] in ("ddf-version", "--ddf-version"):
        print(f"ddf {__version__} (DDFramework engine v{ENGINE_VERSION})")
        return 0

    if len(argv) >= 2 and argv[1] == "simulate":
        from . import _sim_cli

        return _sim_cli.main(argv[2:])

    # Forward everything else unchanged. ghost.__main__.main reads argv[0:]
    # and treats argv[1] as the subcommand.
    import ghost.__main__ as ghost_main

    return ghost_main.main(argv)


if __name__ == "__main__":
    sys.exit(main())
