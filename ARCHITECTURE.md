# Shrike — Architecture

This document describes the three-layer design of the Shrike fabric and
applies the Donella-Meadows systems-thinking lenses required by
[`DOCTRINE.md`](./DOCTRINE.md) §III. The architecture is an
**instantiation** of the [Constellation Doctrine](./CONSTELLATION.md);
when this document and Constellation conflict, Constellation §11
priority applies.

## 1. Three Layers

```
┌──────────────────────────────────────────────────────────┐
│  GHOST  (Python 3, stdlib-heavy, read-only)              │
│  observes, predicts, warns — writes only advisories      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  HYPERION FABRIC  (Rust + C FFI)                   │  │
│  │  routing, continuity, spatial collapse             │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  PHANTOM CORE  (Rust, with C primitives)     │  │  │
│  │  │   - ritual executor                          │  │  │
│  │  │   - append-only NDJSON ledger                │  │  │
│  │  │   - invariant checker (doctrine-as-code)     │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                            │
                            │  ledger feed (read-only)
                            ▼
                       operator
```

### 1.1 Phantom Core

- **Language:** Rust (stable, edition-pinned), C (ISO C11) for the
  lowest primitives only.
- **Responsibilities:** executing registered rituals, writing ledger
  entries, enforcing invariants I1–I8.
- **Contract:** exits non-zero on any invariant violation; refuses to
  run on doctrine-hash mismatch.

### 1.2 Hyperion Fabric

- **Language:** Rust (stable), with a thin `c-primitives/` layer for
  raw sockets / syscalls where the Rust standard library is
  insufficient or a 100-year-stable C ABI is preferred.
- **Responsibilities:** node-to-node routing, continuity across
  disconnection, predictive prewarming.
- **Contract:** never performs ritual side effects of its own; every
  fabric action is either a transport for a Phantom ritual or a
  cache-warming hint requested by Phantom.

### 1.3 GHOST Observer

- **Language:** Python 3 (stdlib-heavy; any third-party dependency must
  be justified in `LANGUAGES.md`).
- **Responsibilities:** tails the Phantom ledger, emits advisories,
  detects drift, scores system health.
- **Contract:** read-only on Phantom state. Advisories are written to a
  separate advisory stream that Phantom never reads automatically.

## 2. Meadows Analysis

### 2.1 Stocks

| Stock | Storage | Change rate |
|---|---|---|
| Doctrine | `DOCTRINE.md` + `doctrine.toml` | very slow (ceremony-only) |
| Source code | repo tree | moderate |
| Ledger entries | `ledger/phantom.ndjson` | every ritual = +1 entry |
| Binaries | content-addressed blobs | per-release |
| Ritual definitions | `ceremonies/*.toml` | slow |
| GHOST advisories | separate advisory stream | continuous |

### 2.2 Flows

```
operator intent
    → ritual invocation (phantom <name>)
        → doctrine-hash check (I6)
            → invariant preflight (I1–I8)
                → ledger write (BEFORE side effect, per I7)
                    → side effect executes
                        → ledger write (result)
                            → GHOST reads ledger (async)
                                → GHOST advisory (if anomaly)
```

### 2.3 Feedback Loops

- **Reinforcing (good):** more rituals → richer ledger → better GHOST
  predictions → fewer unsafe actions → more confidence to ritualize
  new operations.
- **Reinforcing (dangerous, to be blocked):** undefined behavior → ad
  hoc patches → more undefined behavior. Cut by requiring every
  operation to be a registered ritual before it touches the system.
- **Balancing (desired):** every attempted mutation triggers an
  invariant preflight. Violations halt the loop. This is the primary
  safety balancing loop.
- **Balancing (meta):** doctrine amendment itself is a ritual,
  preventing the doctrine from silently drifting via unreviewed
  edits.

### 2.4 Leverage Points (highest to lowest)

1. **Paradigm — ceremony-first, auditable, reversible.** Set by
   doctrine. Highest leverage, hardest to change.
2. **Rules — invariants I1–I8 encoded in `doctrine.toml` and enforced
   by the binary.** Prevents doctrine drift from being a
   documentation-only concern.
3. **Information flows — the NDJSON ledger.** Single source of
   observational truth. Every other component reads from or writes to
   it.
4. **Self-organization — ritual registry.** New capabilities added by
   writing new `ceremonies/*.toml` files, not by patching the core.
5. **Goals — 100-year durability.** Drives every technology choice.
6. **Parameters — toolchain pins, hash algorithms, ledger path.**
   Low leverage, high churn candidates; we pin them anyway for
   determinism (I4).

### 2.5 Attractors

**Attractors we seek:**

- Deterministic, reproducible builds
- Content-addressed everything
- Minimal dependency surface
- ISO-standardized languages and formats
- Read-only-by-default observability

**Attractors we avoid:**

- Vendored god-framework
- Runtime reflection magic
- Unversioned config
- Ambient state (env vars, `~/.config`, current working directory)
- Silent auto-upgrades

### 2.6 Known Risks and Mitigations

| Risk | Meadows category | Mitigation |
|---|---|---|
| Doctrine drift (prose vs TOML) | unstable attractor | hash check (I6), amendment ritual |
| Ledger corruption | stock loss | append-only (I1), content-addressed (I2) |
| GHOST feedback pollutes Phantom | boundary violation | separate advisory stream (I8) |
| Toolchain rot (10+ yr) | flow collapse | pinned toolchain, vendored deps, reproducible-build CI |
| Dependency abandonment | stock loss | vendored deps, minimal surface, `LANGUAGES.md` policy |
| Operator fatigue (too many confirmations) | balancing loop too strong | irreversibility levels in ritual manifests |

## 3. Physical Layout

```
Shrike/
├── DOCTRINE.md
├── doctrine.toml
├── ARCHITECTURE.md            (this file)
├── RITUALS.md
├── LANGUAGES.md
├── AGENTS.md
├── README.md
├── LICENSE
├── LICENSE-NONCOMMERCIAL
├── LICENSE-COMMERCIAL
├── Cargo.toml                 (workspace root, pinned 1.95.0)
├── rust-toolchain.toml        (stable-1.95.0 pin)
├── Makefile                   (POSIX build entry point)
├── phantom-core/              (Rust binary — phantom bin target)
│   ├── build.rs               (embeds doctrine hashes at build time)
│   └── src/ {main,lib,sha256,canonical,ledger,timestamp}.rs
├── hyperion-net/              (Rust lib — skeleton)
│   └── c-primitives/          (ISO C11 stubs, not yet linked)
├── ghost-observer/            (Python package, stdlib-only)
│   └── ghost/ {__init__,__main__,reader}.py
├── tools/                     (stdlib-only Python helpers)
│   ├── verify_ledger.py       (chain auditor)
│   └── append_ledger.py       (ceremony-entry appender)
├── ceremonies/                (ritual manifests)
│   ├── 0001-verify.toml         (status: implemented)
│   ├── 0002-deploy.toml         (status: declared)
│   ├── 0003-lan-scan.toml       (status: declared)
│   ├── 0004-amend-doctrine.toml (status: implemented)
│   └── 0005-file-waiver.toml    (status: implemented)
└── ledger/
    ├── SPEC.md                (format spec — NDJSON + hash chain)
    ├── events.jsonl           (append-only, tracked in git)
    └── blobs/                 (content-addressed artifact store)
```
