# DDFramework

**Engine identity ratified at repository version 0.6.0.**

This document is the single source of truth for **what this repository
is** and **what it is not**. It is cited by [`doctrine.toml`](./doctrine.toml)
`[meta].engine_identity_doc` and is the anchor for all future scope
decisions.

---

## 1. What this repository contains

This repository contains the **DDFramework engine**: a sovereign,
ceremony-first, app-agnostic substrate for building long-horizon,
regenerative, coherent systems.

The engine is composed of four layers. Together, these four layers *are*
DDFramework:

| Layer | Role | Crate / package |
|---|---|---|
| **ddf-exec** (historically *Phantom*) | Execution + rituals; deterministic ritual core | `ddf-exec-core/` |
| **Constellation** | Doctrine; constitutional layer | `CONSTELLATION.md` + `constellation.toml` |
| **GHOST** | Advisory engine; read-only observer and rule runner | `ghost-observer/` |
| **Ledger** | Truth substrate; append-only hash-chained record | `ledger/` + `advisories/` |

The engine is the thing that gets reused. It must remain:

- **App-agnostic** — no application logic lives in the engine.
- **Transport-agnostic** — the engine takes no position on how applications move data between nodes; transport is an application concern.
- **Reusable** — every future DRKNRTH application consumes the engine via stable interfaces.
- **Portable** — deterministic builds, ISO-standard languages, no proprietary runtime dependencies.

---

## 2. What this repository is **not**

- It is not *Shrike*. Shrike is an umbrella label at the workspace level and the name of a future *application* that will be built on top of DDFramework in the Application Era (v5.0.0 and later).
- It is not an application. No application-specific functionality belongs in the engine's crates or packages.
- It is not locked to one deployment model, one OS, one cloud, or one hosting pattern. Applications choose those; the engine abstains.

---

## 3. Era separation

| Era | Versions | Scope | Examples of in-scope work |
|---|---|---|---|
| **Engine Era** | 0.x – 4.x | Build the DDFramework engine itself | Phases 1–4 (completed): doctrine, ritual core, ledger, advisory engine |
| **Application Era** | 5.x and later | Applications consume the engine | `Shrike Monitor`, `Phantom Orchestrator`, and other DRKNRTH apps |

**The Engine Era is complete at v0.6.0** as far as identity and
scoping are concerned. Further engine evolution continues (Phase 5+
engine concerns such as `--strict` mode, waiver expiry, and
additional simulation capabilities) but that work is framed as
*DDFramework engine work*, not Shrike work.

Applications live in separate repositories (or separate top-level
directories in this one, when that decision is made) and depend on
DDFramework as an external substrate.

---

## 4. The four layers, in more detail

### 4.1 ddf-exec (engine executor, historically *Phantom*)

The sovereign ritual executor. Rust binary (`ddf-exec`) with zero
third-party dependencies. Embeds the SHA-256 of `doctrine.toml` and
`constellation.toml` at build time and refuses to run on mismatch
(invariant I6).

**`ddf-exec` is the only component authorized to write to the main
ledger.**

### 4.2 Constellation

The constitutional doctrine. Nine principles, nine mandates, twelve
scoping tiers. Versioned independently of the architectural doctrine.
When architectural and constitutional rules conflict, Constellation
§11 priority applies.

### 4.3 GHOST

The read-only advisory engine. Python, stdlib-only. Seven rules
(R001–R007) plus an R000 bootstrap. Writes advisories to its own
hash-chained stream (`advisories/stream.jsonl`). Structurally
forbidden from writing to the main ledger or importing `ddf_exec_core`
(invariant I8, enforced by `tests/test_readonly_on_main_ledger.py`).

### 4.4 Ledger

The truth substrate. Two hash-chained NDJSON streams:

- `ledger/events.jsonl` — the main ledger. Written by `ddf-exec` only.
  Ceremonial ground truth.
- `advisories/stream.jsonl` — GHOST's advisory stream. Written by GHOST
  only. Observational ground truth.

Both streams are append-only, content-addressed, and tracked in git.

---

## 5. Invariants

DDFramework upholds invariants **I1–I8**. For historical reasons
these are labeled **"Shrike I1–I8"** in existing code comments,
ceremony manifests, rule subjects, and tests. The label is legacy and
frozen; the identifiers themselves (`I1`, `I2`, …) are the real
interface. New prose (including this document) refers to them as
*"the DDFramework invariants I1–I8 (historically labeled 'Shrike
I1–I8')"*.

The invariants themselves are unchanged by this amendment. See
[`DOCTRINE.md`](./DOCTRINE.md) §IV for the authoritative list.

---

## 6. Legacy "Shrike" references

Where the word "Shrike" currently appears in the engine — help text,
`doctrine.toml [meta].project`, pyproject.toml metadata, LICENSE
copyright holder text, ritual manifest invariant labels, test path
prefixes — it is **legacy branding**. Policy:

- **Do not expand it.** No new runtime references, no new strings, no new symbols using "Shrike".
- **Do not deepen it.** Do not make existing Shrike strings more load-bearing.
- **Do not propagate it.** No new files should adopt the prefix.
- **Do not thrash to remove it.** Churn is a bigger cost than stale branding.

Legacy references are frozen exactly where they are. New engine work
is framed as DDFramework work. (The `shrike_sock_*` C FFI prefixes
mentioned in earlier amendments were tied to the removed Hyperion
transport skeleton and went out with it; the policy above refers only
to the remaining legacy strings.)

---

## 7. Applications are out of scope (until Phase 5+)

- No application logic in `ddf-exec-core/`, `ghost-observer/`, or `tools/`.
- No application-specific ritual kinds added to `ceremonies/`.
- No application-specific event kinds added to the main ledger registry.
- No GHOST rules tailored to a specific application's anomaly shape.

When an application is created (Phase 5+), it lives in a sibling
directory (or sibling repo) and depends on DDFramework via:

- Running `ddf-exec` as a subprocess for rituals.
- Importing `ghost-observer` as a Python package for observation.
- Reading ledger / advisory streams as authoritative history.

Transport — how the application moves data between nodes — is the
application's choice. The engine takes no position.

---

## 7.1 Kernelization (v0.7.0)

Starting at engine v0.7.0, the kernel API surface is formally
declared under [`ddf-core/`](./ddf-core/). Downstream applications
(Application Era, v5.0.0+) depend on that boundary rather than on
the internal layer crates.

Kernel boundary:

```
ddf-core/
├── README.md            stable API contract
├── ddf/                 Rust crate: `ddf` library + binary
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs       ddf::verify, amend_doctrine, run_ritual, ledger, ghost
│       └── main.rs      `ddf <subcommand>` CLI dispatcher
├── ddf_py/              Python package: `ddf`
│   ├── pyproject.toml
│   └── ddf/             import ddf; ddf.verify(), ddf.advise(), ddf.ledger
├── simulation/          Phase 6 scaffolding: diff, dryrun, replay, drift
└── tests/               T1 structure, T2 API, T3 no-behavior-change
```

What does NOT change in v0.7.0:

- No layer crate is moved. `ddf-exec-core/` (formerly `phantom-core/`)
  and `ghost-observer/` stay at the repo root as the engine's internal
  implementation. The kernel boundary is **conceptual**, enforced by
  the `ddf-core/` API surface and by its tests.
- No existing invariant is weakened (I1–I8 unchanged).
- No ritual semantics change. `ddf-exec verify` (formerly
  `phantom verify`) and every other subcommand behave exactly as they
  did in v0.6.0. The `ddf` binary is a thin dispatcher that forwards
  to them.

Stability contract:

- `ddf::API_VERSION = "0.1.0"` and `ddf.__version__ = "0.1.0"` govern
  the kernel API itself. They may evolve independently of the engine
  `doctrine_version`.
- Weakening the API surface (removing a function, renaming a public
  symbol) is a **major** API bump and requires a Tier 1 amendment.
- Adding to the surface is a **minor** bump.

## 8. Amendment policy

This document and the engine's scope definition are governed by the
same ceremony as the rest of doctrine ([`DOCTRINE.md`](./DOCTRINE.md)
§VII + [`CONSTELLATION.md`](./CONSTELLATION.md) §14):

- Proposal → rationale → review → ledger entry → version bump.
- Amendments require `ddf-exec amend-doctrine --approve`.
- Weakening "app-agnostic" or "portable" is a **major** bump.
- Adding clarifications is a **patch** bump.
