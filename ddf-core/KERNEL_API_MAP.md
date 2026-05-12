# Kernel API map — public surface (mechanical names)

**Kernel API version:** 1.0.0 (see `ddf::API_VERSION` / `ddf.__version__`)  
**Stability:** ratified at engine v1.0.0. Additive changes only across engine patch/minor per `ddf-core/README.md`.

This document maps **every intentional public symbol** on the kernel boundary to
its **mechanical role**. Mission names appear only in the “Notes” column.

---

## Rust (`ddf` crate)

| Public item | Role | Delegates / implements |
|-------------|------|-------------------------|
| `API_VERSION` | Kernel API SemVer string. | Constant |
| `ENGINE_VERSION` | Engine `doctrine_version` string this API targets. | Constant |
| `ledger` module | Ledger **types and operations** re-exported from engine core. | `ddf_exec_core::ledger` |
| `canonical` | **Canonical serialization** types for ledger entries. | `ddf_exec_core::canonical` |
| `sha256` | **SHA-256** helpers (hex, bytes). | `ddf_exec_core::sha256` |
| `timestamp` | **RFC 3339 timestamp** helper. | `ddf_exec_core::timestamp` |
| `exec_bin_path` | Resolve path to **engine executor binary** (`ddf-exec`). Doc-aliased as `phantom_bin_path` for traceability. | Env `DDF_EXEC_BIN`, sibling exe, `PATH` |
| `verify` | Run **verify ritual** (0001); exit status from subprocess. | `ddf-exec verify` |
| `amend_doctrine` | Run **doctrine amendment ritual** (0004); `--approve` injected. | `ddf-exec amend-doctrine …` |
| `file_waiver` | Run **waiver filing ritual** (0005); `--approve` injected. | `ddf-exec file-waiver …` |
| `run_ritual` | **Dispatch** a zero-argument ritual by id (`0001`, `0006`, aliases `verify`, `ghost-advise`). | `verify` / `ghost::advise` |
| `ghost::advise` | Run **advisor ritual** (0006); may append advisory stream. | `python -m ghost advise` |
| `ghost::verify_advisories` | **Audit** advisory NDJSON hash chain. | `python -m ghost verify-advisories` |

**Notes:** The `ghost` module name is the **kernel namespace** for advisor subprocess helpers; it does not import the Python package at compile time.

---

## Python (`ddf` package)

| Public name | Role | Implements |
|-------------|------|------------|
| `__version__` | Kernel API SemVer. | `"1.0.0"` |
| `ENGINE_VERSION` | Engine `doctrine_version`. | `"1.0.0"` |
| `ghost_version` | Version string of underlying `ghost-observer` package. | Re-export |
| `ledger` | Alias for **`reader`**: read / verify main ledger file. | `ghost.reader` |
| `reader` | **Main ledger reader** module. | `ghost.reader` |
| `advisor` | **Advisor orchestrator** module (runs rules, returns advisories). | `ghost.advisor` |
| `advisory_writer` | **Advisory stream append** helper (hash-chained NDJSON). | `ghost.advisory_writer` |
| `verify(path=…)` | **Verify** main ledger hash chain; returns `ChainResult`. | `reader.verify` |
| `advise(**paths)` | Run **advisor** over default or overridden paths; returns `(advisories, run_id, head_hash)`. | `advisor.run` |

---

## CLI (`ddf` binary)

See table in [`README.md`](./README.md) in this directory (`ddf-core/README.md`).

### Simulation subcommand (Phase 6 wave 2)

`python -m ddf simulate <name>` exposes the read-only Phase 6 modules.
The dispatcher lives at `ddf-core/ddf_py/ddf/_sim_cli.py`; the modules
live at `ddf-core/simulation/`. JSON output, deterministic ordering,
stdlib only, zero side effects.

| Subcommand | Module | Purpose |
|------------|--------|---------|
| `doctrine-diff`     | `simulation.doctrine_diff`     | Semantic diff of two `doctrine.toml` files. |
| `ritual-dryrun`     | `simulation.ritual_dryrun`     | Static validation of a ritual invocation. |
| `ledger-replay`     | `simulation.ledger_replay`     | Chain audit of the main ledger. |
| `advisory-replay`   | `simulation.advisory_replay`   | Chain audit of the advisory stream. |
| `drift-simulation`  | `simulation.drift_simulation`  | Decide whether GHOST R001 / R002 / R003 would fire now. |

---

## Compatibility and renames

- Any **new** public API should prefer **mechanical** names in signatures and rustdoc/pydoc.
- **Renaming** existing symbols is a **major** kernel API bump unless only `#[doc(alias)]` / docstring clarification is added.
- Ledger **event type strings** and ceremony **ids** are **protocol**; they are not renamed by this document.
