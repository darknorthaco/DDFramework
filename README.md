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

## Status

**v0.6.0 — Engine Era complete; identity ratified as DDFramework.**
Scope redefinition commit: this repository is the DDFramework engine.
Legacy "Shrike" branding is preserved exactly where it already exists
(help text, C FFI prefixes, pyproject metadata, doctrine `project`
field, LICENSE text, invariant labels I1–I8) and will not be expanded.
No executable behavior changes in this version. Six rituals registered;
four executors implemented (`verify`, `amend-doctrine`, `file-waiver`,
`ghost-advise`). GHOST's seven rules (R001–R007) remain silent on the
clean post-amendment state. Phase 5+ moves into the Application Era.

```sh
make build                                    # release build
make verify                                   # phantom verify ritual
make verify-ledger                            # audit main-ledger chain
make ghost                                    # ledger summary (read-only)
make ghost-advise                             # run GHOST advisor (R001-R007)
make ghost-verify                             # audit advisory-stream chain
make test                                     # full test gate

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
