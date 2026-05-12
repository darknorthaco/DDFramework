# Engine names — mission language vs mechanism

This glossary decodes **mission names** (historically *Phantom*; now
the mechanical name `ddf-exec` for the executor, *GHOST* for the
observer) used in constitution and operator docs into **standard
software terms** used when reading or changing code.

- **Mission names** answer *why* and *who we are*.
- **Mechanisms** answer *what runs*, *what stores state*, and *who may write*.

For the stable embedder vocabulary, see [`ddf-core/README.md`](./ddf-core/README.md) and [`ddf-core/KERNEL_API_MAP.md`](./ddf-core/KERNEL_API_MAP.md).

**Diagrams:** [`docs/VISUAL_LAYERS.md`](./docs/VISUAL_LAYERS.md) (Mermaid + SVG).

---

## Maintaining this glossary (contributors and agents)

When you touch any of the following in the **same change**, update **this
file** and [`ddf-core/KERNEL_API_MAP.md`](./ddf-core/KERNEL_API_MAP.md) so the
decoder ring stays accurate:

- A **new or renamed** public `ddf` Rust or Python API symbol.
- A **new ritual**, ceremony id, ledger `event` kind, or operator-facing
  advisory rule identifier.
- A **new or renamed** environment variable for the kernel boundary (`DDF_*`)
  or a documented CLI entrypoint.
- A **material change** to what a layer may read or write (must stay aligned
  with [`DDFRAMEWORK.md`](./DDFRAMEWORK.md) and invariants I1–I8).

This glossary **explains** identifiers; it does **not** change protocol
strings, ledger history, or doctrine. Those follow `ledger/SPEC.md`,
ceremonies, and amendment rituals.

---

## Layers and directories

| Mission name | Mechanism (what it is) | Typical location |
|--------------|------------------------|------------------|
| **ddf-exec** (engine; historically *Phantom*) | **Ritual executor**: runs registered ceremonies, enforces invariants, **only writer** to the main append-only ledger. | `ddf-exec-core/`, `ddf-exec` binary |
| **GHOST** (engine) | **Read-only advisor**: rule runner over ledger tails; writes **only** the separate advisory stream. | `ghost-observer/`, `python -m ghost` |
| **Constellation** | **Constitution**: normative principles and mandates above architectural doctrine. | `CONSTELLATION.md`, `constellation.toml` |
| **Ledger** (main) | **Append-only event log** (hash-chained NDJSON): authoritative record of committed rituals. | `ledger/events.jsonl`, `ledger/SPEC.md` |
| **Advisories** | **Separate append-only advisory log**: observational output; not read automatically by the ritual executor for decisions. | `advisories/stream.jsonl`, `advisories/SPEC.md` |
| **Ceremony / ritual** | **Registered procedure**: named entrypoint with manifest (inputs, reversibility, executor); the only normal path to mutate sovereign state. | `ceremonies/*.toml`, `RITUALS.md` |
| **`ddf-core` / `ddf`** | **Kernel boundary**: stable API for embedders; thin dispatch over the engine. | `ddf-core/` |

---

## Kernel API (`ddf`) — quick decode

| Symbol / command | Mechanism |
|------------------|-----------|
| `ddf verify` | Run **verify** ritual on the workspace; append `verify.result` to main ledger. |
| `ddf ledger` | **Read-only** summary / chain check of main ledger (via Python reader). |
| `ddf advise` | Run **advisor** ritual; append to **advisory stream** only. |
| `ddf verify-advisories` | **Audit** advisory stream hash chain. |
| `ddf::ledger` | **Ledger types and helpers** (canonical entries, append primitives). |
| `ddf::ghost::*` | **Advisor subprocess** helpers (shell out to `python -m ghost …`). |

---

## Invariants I1–I8 (mechanical shorthand)

| ID | Mechanical meaning |
|----|---------------------|
| **I1** | Main ledger is **append-only** (no in-place edits). |
| **I2** | Artifacts are **content-addressed** (e.g. SHA-256). |
| **I3** | Rituals declare **reversibility** or explicit irreversibility + confirmation. |
| **I4** | **Reproducible** builds (pinned toolchain, deterministic policy). |
| **I5** | **No ambient state** for ritual inputs (explicit args / manifest). |
| **I6** | **Doctrine hash lock**: executor refuses if built-in hash ≠ on-disk `doctrine.toml`. |
| **I7** | **No silent mutation**: ledger intent **before** visible side effects. |
| **I8** | Advisor is **read-only** on main ledger and ceremony definitions. |

Historical label in code: *Shrike I1–I8* (frozen per v0.6.0). The identifiers `I1`…`I8` are the stable interface.

---

## RF-style intuition (optional)

- Main ledger ≈ **forward-only trace** of what the system committed to (no rewrite).
- Advisor ≈ **monitor / measurement receiver** on a **directional sample** of state; it must not drive power back into the authorized path in a way that violates I8.

---

## Out of scope for this file

Renaming crates, binaries, or ledger event type strings is a **separate**
migration (protocol and embedder impact). This glossary does **not**
change any on-disk identifiers.

**Phase 3 planning:** inventory and wave strategy live in
[`docs/RENAME_IMPACT_ANALYSIS.md`](./docs/RENAME_IMPACT_ANALYSIS.md) and
[`docs/RENAME_COMPATIBILITY_STRATEGY.md`](./docs/RENAME_COMPATIBILITY_STRATEGY.md).
