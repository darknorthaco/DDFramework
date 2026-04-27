# DDFramework

A sovereign, ceremony-first, app-agnostic engine for long-horizon,
regenerative, coherent systems.
Phantom · Constellation · GHOST · Hyperion · Ledger.

Designed to last 100 years.

> **Repository scope (ratified at v0.6.0):** this repository contains
> the **DDFramework engine**. "Shrike FMS" is the workspace-level
> umbrella label retained from the project's Engine Era (Phases 1–4).
> Shrike itself will be a future *application* built on top of
> DDFramework, starting in the Application Era (v5.0.0+). For the
> authoritative engine identity, see [`DDFRAMEWORK.md`](./DDFRAMEWORK.md).

---

## What this repository is

DDFramework is a systems-thinking engine built under an explicit,
versioned doctrine. Every action the system performs is a registered
ritual, logged to an append-only ledger, bound by invariants that are
encoded as code — not just described in prose.

The core idea: **bounded emergence.** Intelligent, adaptive behavior
is welcome, but only inside lines that are drawn in advance, in
public, and with the operator's consent.

## How to read this repository

- **Operators (ceremony, governance, audits):** start with
  [`DDFRAMEWORK.md`](./DDFRAMEWORK.md), [`RITUALS.md`](./RITUALS.md),
  and the `make` targets below. Mission names (Phantom, GHOST, …) are
  intentional there.
- **Implementors (code, APIs, embedding):** start with
  [`ddf-core/README.md`](./ddf-core/README.md),
  [`ddf-core/KERNEL_API_MAP.md`](./ddf-core/KERNEL_API_MAP.md), and
  [`ledger/SPEC.md`](./ledger/SPEC.md). Prefer **mechanical** terms
  (ritual executor, ledger, advisor) in new code and reviews.
- **Decoder ring (both):** [`GLOSSARY_ENGINE_NAMES.md`](./GLOSSARY_ENGINE_NAMES.md)
  maps mission names to standard software terms.
- **Diagrams:** [`docs/VISUAL_LAYERS.md`](./docs/VISUAL_LAYERS.md) — stack, kernel,
  sequence, and Meadows views (Mermaid + printable SVG).

## Three layers

- **Phantom** — the sovereign ritual core. Rust, with C primitives.
- **Hyperion** — the network fabric. Rust + C FFI.
- **GHOST** — the read-only observer. Python, stdlib-heavy.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full picture.

## Start here

Read these, in this order:

1. [`DDFRAMEWORK.md`](./DDFRAMEWORK.md) — **engine identity**, scope, era separation
2. [`CONSTELLATION.md`](./CONSTELLATION.md) — **the constitution**, v0.1.1
3. [`constellation.toml`](./constellation.toml) — machine-readable constitution
4. [`DOCTRINE.md`](./DOCTRINE.md) — DDFramework architectural doctrine, v0.6.0
5. [`doctrine.toml`](./doctrine.toml) — machine-readable architectural invariants
6. [`ARCHITECTURE.md`](./ARCHITECTURE.md) — three layers + Meadows analysis
7. [`RITUALS.md`](./RITUALS.md) — ritual contracts (Verify, Deploy, LAN Scan, amend, waiver, advise)
8. [`LANGUAGES.md`](./LANGUAGES.md) — 100-year language policy
9. [`AGENTS.md`](./AGENTS.md) — rules for agents (human or AI)
10. [`WAIVERS.md`](./WAIVERS.md) — active waiver registry
11. [`ledger/SPEC.md`](./ledger/SPEC.md) — ledger format specification
12. [`advisories/SPEC.md`](./advisories/SPEC.md) — GHOST advisory stream specification
13. [`GLOSSARY_ENGINE_NAMES.md`](./GLOSSARY_ENGINE_NAMES.md) — mission names ↔ mechanisms (decoder ring)
14. [`ddf-core/KERNEL_API_MAP.md`](./ddf-core/KERNEL_API_MAP.md) — kernel public API map (Rust + Python)
15. [`docs/RENAME_IMPACT_ANALYSIS.md`](./docs/RENAME_IMPACT_ANALYSIS.md) — Phase 3 rename inventory (binaries, crates, protocol)
16. [`docs/RENAME_COMPATIBILITY_STRATEGY.md`](./docs/RENAME_COMPATIBILITY_STRATEGY.md) — Phase 3 waves, deprecation, rollback
17. [`docs/VISUAL_LAYERS.md`](./docs/VISUAL_LAYERS.md) — layer diagrams (Mermaid + SVG for Visio/import)

## Status

**v0.7.0 — Kernelization; embeddable kernel API formalized.** The
DDFramework engine now exposes a stable API surface under
[`ddf-core/`](./ddf-core/). Downstream applications depend on that
boundary, not on the internal layer crates. `ddf` Rust bin +
`ddf` Python package provide byte-for-byte parity with the underlying
`phantom` CLI and `ghost` package respectively. No executable
behavior changed; seven rituals registered (adds `kernelize`); four
executors implemented (`verify`, `amend-doctrine`, `file-waiver`,
`ghost-advise`); GHOST remains clean against the post-amendment state.
Phase 6 will implement the simulation layer; Phase 5+ applications
are still out of scope in this repository.

**Application 1 (shell):** the **Constitutional Agent Shell** scaffold lives under
[`AO/`](./AO/) (governed agent runtime on the `ddf` kernel). It does not change
engine doctrine; it consumes the engine via the paths documented there.

**Mechanical naming POAM:** **Closed** for Phases 1–2 and Phase 3 Wave 1
(glossary, kernel map, Makefile aliases, rename strategy docs, visuals).
Formal record: closure block in
[`docs/RENAME_COMPATIBILITY_STRATEGY.md`](./docs/RENAME_COMPATIBILITY_STRATEGY.md).
Further binary or crate renames are **event-driven** (packaging, embedders, or a
planned major release). Prefer new effort on **Phase 6 simulation** or on
**applications that depend on this engine**, not on cosmetic renames here.

```sh
make build                                    # release build (phantom + ddf)
make verify                                   # phantom verify ritual
make verify-ledger                            # audit main-ledger chain
make ghost                                    # ledger summary (read-only)
make ghost-advise                             # run GHOST advisor (R001-R007)
make ghost-verify                             # audit advisory-stream chain
# Mechanical Makefile aliases (same behavior): ledger-summary, advise,
# advisory-verify, executor-doctrine — see docs/RENAME_COMPATIBILITY_STRATEGY.md
make test                                     # full test gate

# Kernel API (v0.7.0+)
make ddf ARGS="verify"                        # ddf verify (parity with phantom verify)
make ddf ARGS="advise"                        # ddf advise (parity with ghost advise)
make ddf ARGS="ddf-version"                   # print ddf + engine version

# Ceremonies (all require --approve per Constellation §14)
phantom amend-doctrine --version <v> --rationale "<why>" --approve
phantom file-waiver    --id <W-id>  --waiver <path>        --approve
```

## License

Source-available under a dual license:

- **Non-commercial use** — [PolyForm Noncommercial 1.0.0](./LICENSE-NONCOMMERCIAL)
- **Commercial use** — [separate paid license](./LICENSE-COMMERCIAL), by contact

See [`LICENSE`](./LICENSE) for the top-level notice.

## Contributing

Contributions follow the doctrine. Read `DOCTRINE.md` and `AGENTS.md`,
then open an issue with a proposed plan.
