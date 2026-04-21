"""T1 — Kernel directory structure test.

Asserts:
  - `ddf-core/` exists at the repo root.
  - Required submodules are present (ddf Rust crate, ddf_py Python
    package, simulation stubs, README).
  - No application code lives inside the kernel boundary. Since we
    have no applications yet, the check is: no file path under
    ddf-core/ matches common application-layer patterns.
"""

from __future__ import annotations
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent
REPO_ROOT = DDF_CORE.parent


REQUIRED_PATHS = [
    DDF_CORE / "README.md",
    DDF_CORE / "ddf" / "Cargo.toml",
    DDF_CORE / "ddf" / "src" / "lib.rs",
    DDF_CORE / "ddf" / "src" / "main.rs",
    DDF_CORE / "ddf_py" / "pyproject.toml",
    DDF_CORE / "ddf_py" / "ddf" / "__init__.py",
    DDF_CORE / "ddf_py" / "ddf" / "__main__.py",
    DDF_CORE / "simulation" / "README.md",
    DDF_CORE / "simulation" / "doctrine_diff.py",
    DDF_CORE / "simulation" / "ritual_dryrun.py",
    DDF_CORE / "simulation" / "ledger_replay.py",
    DDF_CORE / "simulation" / "advisory_replay.py",
    DDF_CORE / "simulation" / "drift_simulation.py",
]


class KernelStructureTest(unittest.TestCase):
    def test_kernel_root_exists(self):
        self.assertTrue(DDF_CORE.is_dir(), f"expected {DDF_CORE} to be a directory")

    def test_required_paths_present(self):
        missing = [str(p.relative_to(REPO_ROOT)) for p in REQUIRED_PATHS if not p.exists()]
        self.assertEqual(missing, [], f"missing kernel paths: {missing}")

    def test_kernel_has_no_application_code(self):
        """No Shrike-Monitor / Phantom-Orchestrator etc. inside the kernel boundary."""
        forbidden_names = {
            "shrike-monitor", "shrike_monitor",
            "phantom-orchestrator", "phantom_orchestrator",
            "drknrth-app", "drknrth_app",
            "app", "applications",
        }
        offenders = []
        for path in DDF_CORE.rglob("*"):
            if path.is_dir():
                if path.name in forbidden_names:
                    offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(
            offenders,
            [],
            f"application-layer directories inside ddf-core/: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
