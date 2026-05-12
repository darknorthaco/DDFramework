# Shrike — Ritual Contracts

A ritual is the only way a Shrike binary performs an observable
action. Every ritual has a manifest in `ceremonies/NNNN-name.toml` and
an entry in [`doctrine.toml`](./doctrine.toml) §`[rituals].registered`.

This document is the contract specification for the implemented
engine rituals (Verify, amend-doctrine, file-waiver, ghost-advise,
and kernelize). Later rituals follow the same template.

---

## 0. Ritual Template

Every ritual declares:

| Field | Meaning |
|---|---|
| `id` | zero-padded 4-digit ordinal, e.g. `0001` |
| `name` | lowercase-kebab identifier |
| `purpose` | one-sentence description |
| `inputs` | exhaustive list of explicit arguments (I5) |
| `outputs` | files produced, ledger entries appended |
| `side_effects` | observable external changes (network, disk, stdout) |
| `invariants_upheld` | which of I1–I8 are load-bearing for this ritual |
| `inverse` | name of inverse ritual, or `"none (irreversible)"` |
| `irreversibility_confirmation` | required when `inverse = "none"` |
| `ledger_entry_schema` | schema for the ledger entry this ritual writes |
| `failure_modes` | enumerated, each with a recovery path |

---

## 1. Verify

**`id`:** 0001 · **`name`:** `verify` · **`inverse`:** self (idempotent, read-only)

### Purpose

Confirm that the repository on disk matches its doctrinal and content
expectations. The simplest ritual. Entirely read-only. Serves as the
smoke test for the whole fabric.

### Inputs

- `--root <path>` — repository root. Default: current working
  directory. *(Declared here per I5; no ambient `cwd` inference.)*
- `--doctrine <path>` — path to `doctrine.toml`. Default:
  `<root>/doctrine.toml`.

### Outputs

- `stdout` — human-readable verification report
- Ledger entry of `kind = "verify.result"` appended to
  `ledger/events.jsonl`

### Side Effects

Read-only on all files. Writes one ledger entry. No network.

### Invariants Upheld

- **I2** — every file tracked by git is hashed and reported by SHA-256.
- **I4** — reports the active toolchain pin.
- **I6** — compares `doctrine.toml` SHA-256 against the binary's
  embedded hash. Mismatch is a fatal error and still writes a
  `verify.result` entry with `status = "doctrine-mismatch"`.

### Inverse

`verify` is idempotent and read-only. Its inverse is itself.

### Ledger Entry Schema

```json
{
  "ts": "2026-04-20T12:34:56.789Z",
  "kind": "verify.result",
  "schema": 1,
  "ritual_id": "0001",
  "status": "ok | doctrine-mismatch | workspace-dirty | error",
  "doctrine_hash_expected": "sha256:…",
  "doctrine_hash_actual":   "sha256:…",
  "file_count": 42,
  "merkle_root": "sha256:…",
  "prev_entry_hash": "sha256:…",
  "entry_hash": "sha256:…"
}
```

### Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| `doctrine.toml` missing | file stat | halt; operator must restore or run `amend-doctrine` |
| doctrine hash mismatch | SHA-256 compare | halt; operator investigates drift |
| workspace has unhashable file | read error | report and halt; operator fixes permissions |
| ledger append fails | write error | halt; operator inspects disk / permissions |

---

> **Historical note:** the `deploy` (0002) and `lan-scan` (0003)
> rituals were declared in earlier phases as part of the engine's
> Hyperion transport story. Both were removed at v1.0.0 along with
> the Hyperion layer; the engine no longer presumes a transport.
> Applications are free to define their own deploy / discovery
> rituals against their own transports.

---

## 4. Ledger Entry Framing

Every ledger entry, regardless of ritual, is a single JSON object on a
single line (NDJSON). The first line of a fresh ledger is a `genesis`
entry with `prev_entry_hash = "sha256:0000…"`. Each subsequent entry
includes the SHA-256 of the previous entry, forming a hash chain —
tamper-evident by construction (I1).

Full framing and validation rules belong in `ledger/SPEC.md` (Phase 2).

---

## 5. Adding New Rituals

To add a ritual:

1. Reserve the next ordinal in `ceremonies/`.
2. Write the manifest TOML.
3. Add the name to `[rituals].registered` in `doctrine.toml`.
4. Bump `doctrine_version` (minor).
5. Amend via the `amend-doctrine` ritual.
6. Implement the ritual in `phantom-core`.
7. Add tests.
8. Add GHOST observer heuristics if the ritual has new anomaly shapes.
