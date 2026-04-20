# Shrike

A sovereign, ceremony-first distributed compute fabric.
Phantom core · Hyperion transport · GHOST observer.

Designed to last 100 years.

---

## What this repository is

Shrike is a systems-thinking engineering fabric built under an
explicit, versioned doctrine. Every action the system performs is a
registered ritual, logged to an append-only ledger, bound by
invariants that are encoded as code — not just described in prose.

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

1. [`CONSTELLATION.md`](./CONSTELLATION.md) — **the constitution**, v0.1.1 (Constellation Doctrine)
2. [`constellation.toml`](./constellation.toml) — machine-readable constitution
3. [`DOCTRINE.md`](./DOCTRINE.md) — Shrike architectural doctrine, v0.2.0
4. [`doctrine.toml`](./doctrine.toml) — machine-readable architectural invariants
5. [`ARCHITECTURE.md`](./ARCHITECTURE.md) — three layers + Meadows analysis
6. [`RITUALS.md`](./RITUALS.md) — ritual contracts (Verify, Deploy, LAN Scan)
7. [`LANGUAGES.md`](./LANGUAGES.md) — 100-year language policy
8. [`AGENTS.md`](./AGENTS.md) — rules for agents (human or AI)
9. [`WAIVERS.md`](./WAIVERS.md) — active waiver registry
10. [`ledger/SPEC.md`](./ledger/SPEC.md) — ledger format specification

## Status

**v0.2.0 — Constitution ratified.** Documents only. Ledger bootstrapped
with the genesis entry recording ratification. No executable code yet.
The next phase scaffolds the three layer crates (`phantom-core`,
`hyperion-net`, `ghost-observer`) and implements the `verify` ritual
end-to-end.

## License

Source-available under a dual license:

- **Non-commercial use** — [PolyForm Noncommercial 1.0.0](./LICENSE-NONCOMMERCIAL)
- **Commercial use** — [separate paid license](./LICENSE-COMMERCIAL), by contact

See [`LICENSE`](./LICENSE) for the top-level notice.

## Contributing

Contributions follow the doctrine. Read `DOCTRINE.md` and `AGENTS.md`,
then open an issue with a proposed plan.
