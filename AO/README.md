# Constitutional Agent Shell (AO)

**Application identity:** Application 1 on **DDFramework** (engine pin **b02ac4d** / **v0.7.0** kernel). This repository path (`AO/`) is the first **Application Era** scaffold: a governed, ceremony-first agent runtime that consumes the engine only through the **`ddf` kernel boundary** — never by editing `DOCTRINE.md`, `doctrine.toml`, or engine crates.

**Target home:** [github.com/darknorthaco/AO](https://github.com/darknorthaco/AO) (may be extracted as a standalone repo; see `engines/README.md` for the `Cargo.toml` path switch).

---

## Operator vs implementor

| Audience | Start here |
|----------|------------|
| **Operator** (governance, audits, ceremony) | [`SECURITY_MODEL.md`](./SECURITY_MODEL.md), [`RITUALS.md`](./RITUALS.md), [`AGENT_LIFECYCLE.md`](./AGENT_LIFECYCLE.md), engine [`CONSTELLATION.md`](../CONSTELLATION.md) |
| **Implementor** (code, embedding) | [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`GLOSSARY_AGENT_SHELL.md`](./GLOSSARY_AGENT_SHELL.md), engine [`ddf-core/KERNEL_API_MAP.md`](../ddf-core/KERNEL_API_MAP.md), [`GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md) |

---

## Principles (non-negotiable)

- **Sovereign:** the shell owns its **application ledger** under `AO/ledger/`; the engine’s main ledger remains engine-only (Phantom is still the only writer there).
- **Human-first:** privileged effects require an explicit **operator ceremony file** (see `config/ceremony/`).
- **Deterministic:** ritual code paths use explicit inputs; ledger lines use the same canonical hashing rules as [`ledger/SPEC.md`](../ledger/SPEC.md).
- **Auditable:** every agent step is an **`agent.*` ledger event** on the shell ledger; engine health uses `phantom verify` + optional GHOST advisories.
- **Invariant-bound:** engine **I1–I8** are unchanged; the shell adds **application invariants** in [`SECURITY_MODEL.md`](./SECURITY_MODEL.md).
- **Ceremony-governed:** no `agent.act` with external effects without `OPERATOR_APPROVED=1` in the ceremony file passed to the CLI.
- **Advisory-only conscience:** all **GHOST** advisories come from the engine’s advisor subprocess (`python -m ghost advise`); the shell does not synthesize “advice” in place of GHOST.

---

## Layout

```text
AO/
  README.md                 ← you are here
  ARCHITECTURE.md
  RITUALS.md
  AGENT_LIFECYCLE.md
  SECURITY_MODEL.md
  GLOSSARY_AGENT_SHELL.md
  PHASE6_MIGRATION.md
  AGENTS.md
  config/                   ← operator config (shell.toml, ceremony templates)
  ledger/                   ← append-only shell truth (git-tracked like engine)
  crates/ca-shell/          ← Rust library + `ca-shell` CLI
  python/                   ← stdlib-only shim (`ao-shell` entrypoint)
  engines/README.md         ← where to clone DDFramework when AO is standalone
```

---

## Quick start (inside DDFramework monorepo)

1. Copy `config/shell.toml.example` → `config/shell.toml` and set `engine_root` to the DDFramework workspace root (e.g. `..` when `AO/` is under the engine repo).
2. Build the CLI: `cargo build -p ca-shell` from `AO/` (workspace root file is `AO/Cargo.toml`).
3. Run engine verify through the shell: `cargo run -p ca-shell -- engine-verify` (or install `ca-shell` and run `ca-shell engine-verify`).

---

## Engine coupling

- **Rust:** `crates/ca-shell` depends on the `ddf` crate (see `Cargo.toml` `path = …`).
- **Binaries:** `phantom` and Python `ghost` are invoked **only** via the thin wrappers in `ca_shell::kernel` (aligned with [`KERNEL_API_MAP.md`](../ddf-core/KERNEL_API_MAP.md): verify + advise entrypoints).

Do **not** rename engine binaries or crates from this application.
