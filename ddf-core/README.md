# ddf-core — DDFramework Kernel

The stable, app-agnostic, embeddable kernel API for the DDFramework
engine. Consumed by all future Application-Era software.

- **Engine binds to:** DDFramework v1.0.0 (`doctrine_version`).
- **Kernel API version:** 1.0.0 (ratified at engine v1.0.0).
- **Stability contract:** the API surface below MUST remain
source- and behavior-compatible across engine patch and minor
bumps. Weakening is a major API bump.

## Mechanical overview (kernel vocabulary)

The `ddf` crate and `ddf` Python package are the **stable kernel
boundary**. In plain software terms:


| You see (mission)                   | In code / API (mechanism)                                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------ |
| ddf-exec (this repo's engine; historically *Phantom*) | **Ritual executor** + ledger writer (`ddf-exec` binary, `ddf-exec-core` types) |
| GHOST (this repo’s engine)          | **Read-only advisor** + advisory stream writer (`python -m ghost`, `ghost-observer`) |
| `ddf verify` / `ddf::verify`        | Subprocess call to **verify ritual**                                                 |
| `ddf advise` / `ddf::ghost::advise` | Subprocess call to **advisor ritual**                                                |
| `ddf::ledger`                       | **Ledger** primitives (append-only hash chain)                                       |


Full symbol table: `[KERNEL_API_MAP.md](./KERNEL_API_MAP.md)`.  
Mission ↔ mechanism glossary (repo root): `[../GLOSSARY_ENGINE_NAMES.md](../GLOSSARY_ENGINE_NAMES.md)`.

## What this directory is

This directory is the **kernel boundary**. Downstream applications
depend on what is exposed here. The layer directories at the repository
root (`ddf-exec-core/`, `ghost-observer/`, `ledger/`, `advisories/`,
`constellation.toml`, `CONSTELLATION.md`) are the engine's *internal
implementation* and may be reorganized without affecting embedders.

## CLI

The `ddf` binary is a thin dispatcher. Every subcommand is
behavior-identical to the underlying engine command it delegates to.


| Command                  | Delegates to                        | Effect                                                    |
| ------------------------ | ----------------------------------- | --------------------------------------------------------- |
| `ddf verify`             | `ddf-exec verify`                   | Run the verify ritual; appends one `verify.result` entry. |
| `ddf doctrine`           | `phantom doctrine`                  | Print embedded doctrine hashes + versions.                |
| `ddf amend-doctrine ...` | `ddf-exec amend-doctrine ...`       | Record a doctrine amendment (`--approve` required).       |
| `ddf file-waiver ...`    | `ddf-exec file-waiver ...`          | Record a waiver filing (`--approve` required).            |
| `ddf run-ritual <id>`    | (dispatch)                          | Dispatch a zero-argument ritual by id (`0001`, `0006`).   |
| `ddf ledger [path]`      | `python -m ghost [path]`            | Read the main ledger summary (read-only).                 |
| `ddf advise`             | `python -m ghost advise`            | Run the GHOST advisor (ritual 0006).                      |
| `ddf verify-advisories`  | `python -m ghost verify-advisories` | Audit the advisory-stream chain.                          |


**Environment:**

- `DDF_PHANTOM_BIN` — override the resolved `phantom` binary path.
- `DDF_PYTHON` — override the Python interpreter.
- `PYTHONPATH` — set automatically to `ghost-observer` if unset.

## Rust library API (`ddf` crate)

```rust
use ddf;

let status = ddf::verify()?;
ddf::amend_doctrine("0.8.0", "...", "complicated")?;
ddf::file_waiver("W-20270101-01", "waivers/w-01.md")?;
ddf::run_ritual("0001")?;
let _ = ddf::ghost::advise()?;
let _ = ddf::ghost::verify_advisories()?;

// Core primitives re-exported from ddf-exec-core:
use ddf::ledger;
use ddf::canonical::Entry;
use ddf::sha256::sha256_hex;
use ddf::timestamp::now_rfc3339;
```

Constants:

- `ddf::API_VERSION` — the API version ("1.0.0").
- `ddf::ENGINE_VERSION` — the engine doctrine_version ("1.0.0").

## Python library API (`ddf` package)

```python
import ddf

print(ddf.__version__)        # "1.0.0" (kernel API)
print(ddf.ENGINE_VERSION)     # "1.0.0" (engine)

# Re-exported from ghost-observer:
ddf.verify()                           # ChainResult(count, head_hash, ok, error)
advisories, run_id, head = ddf.advise()

# Namespaces:
ddf.ledger      # -> ghost.reader (iter_entries, verify)
ddf.reader      # same, legacy
ddf.advisor     # the orchestrator
ddf.advisory_writer  # hash-chain append writer
```

## JSON-over-stdin protocol (Phase 6)

A JSON-over-stdin interface is reserved for Phase 6. Outline:
downstream tools submit `{"ritual": "<id>", "args": {...}}` on stdin
and receive a ledger entry object on stdout. Not implemented in
Phase 5.

## What is NOT part of the kernel API

- Application logic of any kind.
- The internal structure of `ddf-exec-core` and `ghost-observer`.
They may be refactored freely.
- Legacy `phantom` CLI banner text.
- Ceremony manifests' prose.
- The ledger file-format version (goverened by `ledger/SPEC.md`, not this crate).

## Invariants

This kernel upholds DDFramework invariants **I1–I8** (historically
labeled *"Shrike I1–I8"*; labels frozen per v0.6.0). None of them
are weakened in v1.0.0; the v1.0.0 amendment removed the Hyperion
layer and renamed the engine executor without touching any invariant.

The *no behavior change* guarantee for Phase 5 is enforced by
`ddf-core/tests/test_no_behavior_change.py`, which runs `ddf verify`
and `ddf-exec verify` and compares their output structurally.