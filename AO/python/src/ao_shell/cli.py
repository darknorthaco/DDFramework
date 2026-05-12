"""Dispatch argv to the `ca-shell` binary (explicit path or PATH)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def _resolve_ca_shell_bin() -> str:
    env = os.environ.get("AO_SHELL_BIN")
    if env:
        return env
    found = shutil.which("ca-shell")
    if found:
        return found
    raise FileNotFoundError(
        "ca-shell not found; build the Rust crate and install the binary, "
        "or set AO_SHELL_BIN to its absolute path."
    )


def main() -> None:
    bin_path = _resolve_ca_shell_bin()
    # Pass through all args after script name
    argv = sys.argv[1:]
    # Optional: inject --shell-root from env for CI
    root = os.environ.get("AO_SHELL_ROOT")
    if root and "--shell-root" not in argv:
        argv = ["--shell-root", root, *argv]
    proc = subprocess.run([bin_path, *argv], check=False)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
