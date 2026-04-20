# Shrike — Ritual Contracts

A ritual is the only way a Shrike binary performs an observable
action. Every ritual has a manifest in `ceremonies/NNNN-name.toml` and
an entry in [`doctrine.toml`](./doctrine.toml) §`[rituals].registered`.

This document is the contract specification for the three bootstrap
rituals: **Verify**, **Deploy**, **LAN Scan**. Later rituals follow the
same template.

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
  `ledger/phantom.ndjson`

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

## 2. Deploy

**`id`:** 0002 · **`name`:** `deploy` · **`inverse`:** `rollback`

### Purpose

Install a Phantom-built artifact onto a Hyperion node. The canonical
mutating ritual. Every deployment is an explicit, logged, reversible
ceremony.

### Inputs

- `--artifact <sha256>` — content-address of the artifact to deploy.
  The artifact must already be present in the local blob store.
- `--target <node-id>` — Hyperion node identifier.
- `--manifest <path>` — deployment manifest (declares env vars,
  mount points, service name). All env must be declared here per I5.

### Outputs

- Artifact installed at the target node
- Ledger entry `kind = "deploy.applied"` with the pre-image hash of
  whatever was previously installed (for rollback)

### Side Effects

Writes to the target node's filesystem. May (re)start a service
declared in the manifest. All side effects must be preceded by the
ledger entry (I7).

### Invariants Upheld

- **I1** — prior state captured in the ledger entry before mutation
- **I2** — artifact referenced by SHA-256
- **I3** — declares `rollback` as inverse
- **I5** — manifest declares all environment
- **I7** — ledger write precedes the filesystem mutation

### Inverse

`rollback` — restores the pre-image captured in the `deploy.applied`
entry. Must be run against the same target within a configurable
window (default: 24h); beyond that window rollback becomes a
confirmation ceremony.

### Ledger Entry Schema

```json
{
  "ts": "…",
  "kind": "deploy.applied",
  "schema": 1,
  "ritual_id": "0002",
  "artifact":      "sha256:…",
  "target":        "node-abc",
  "manifest_hash": "sha256:…",
  "pre_image":     "sha256:…",
  "status": "applied | failed | partial",
  "prev_entry_hash": "sha256:…",
  "entry_hash":    "sha256:…"
}
```

### Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| artifact not in blob store | hash lookup | halt before any mutation |
| manifest references undeclared env | manifest parse | halt with listing |
| target unreachable | transport error | no mutation occurred; log `status=failed` |
| partial write | post-check hash differs | log `status=partial`; `rollback` required |

---

## 3. LAN Scan

**`id`:** 0003 · **`name`:** `lan-scan` · **`inverse`:** self (read-only)

### Purpose

Enumerate reachable Hyperion nodes on the local network segment. A
read-only discovery ritual. Must be explicit and consented — no
ambient scanning.

### Inputs

- `--cidr <cidr-block>` — explicit CIDR to scan. No default. The
  operator must state the scope.
- `--port <u16>` — Hyperion listening port to probe.
- `--timeout-ms <u32>` — per-host timeout.

### Outputs

- `stdout` — table of responding nodes with their reported
  doctrine-hash and version
- Ledger entry `kind = "lan.scan.result"` with the full response set

### Side Effects

Sends TCP SYN (or UDP probe, depending on transport) to each address
in the CIDR. No writes to remote hosts.

### Invariants Upheld

- **I5** — CIDR is explicit; no auto-discovery of "my subnet"
- **I7** — scan summary written to ledger

### Inverse

Read-only; no inverse needed beyond re-running the scan.

### Ledger Entry Schema

```json
{
  "ts": "…",
  "kind": "lan.scan.result",
  "schema": 1,
  "ritual_id": "0003",
  "cidr": "192.168.1.0/24",
  "port": 7777,
  "responders": [
    {
      "addr": "192.168.1.42",
      "node_id": "…",
      "doctrine_hash": "sha256:…",
      "version": "0.1.0",
      "rtt_ms": 3
    }
  ],
  "prev_entry_hash": "sha256:…",
  "entry_hash": "sha256:…"
}
```

### Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| invalid CIDR | parse error | halt immediately |
| raw socket permission denied | syscall error | report; suggest capability-setting procedure |
| doctrine-hash mismatch on responder | hash compare | include in result with `warning: "doctrine-drift"` flag; GHOST will advise |

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
