# Rules for agents in the AO (Constitutional Agent Shell) repository

This file is the **application** counterpart to the engine’s [`AGENTS.md`](../AGENTS.md). When working in **both** trees, read the engine file first for invariant I1–I8 and ceremony policy; then follow this overlay.

## 1. Scope

- **Engine doctrine** (`DOCTRINE.md`, `doctrine.toml` in DDFramework) is **never** amended from AO. Amendments are engine **Tier 1** work in the engine repository only.
- **Application doctrine** (future `AO/doctrine.toml` if introduced) would be amended only via application ceremony — not in this scaffold unless explicitly added.

## 2. Kernel boundary

- Use **`ddf`** / [`KERNEL_API_MAP.md`](../ddf-core/KERNEL_API_MAP.md) for Rust and `ddf` Python from `ddf-core/ddf_py` when you need ledger read / advise.
- Do not import `ddf_exec_core` (the engine executor crate, formerly `phantom_core`) from application code except through the `ddf` re-exports already used in `ca-shell`.

## 3. Rituals

- All **mutating agent steps** must go through the **application rituals** documented in [`RITUALS.md`](./RITUALS.md) (ledger event kinds `agent.*`).
- **Privileged external acts** require operator ceremony files as described in [`SECURITY_MODEL.md`](./SECURITY_MODEL.md).

## 4. GHOST

- **All advisories** must be produced by **GHOST** (`engine-advise` / `ddf advise`). The shell must not pretend an LLM string is a substitute for GHOST rule output.

## 5. Naming

- Prefer **mechanical** names in new Rust modules (ritual, ledger, advisor, verify), per [`GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md).
- Mission names (Phantom, GHOST, Constellation) stay in docs and constitution references.
