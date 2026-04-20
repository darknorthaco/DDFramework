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

**v0.5.0 — Sound doctrine, sound body, sound mind.** GHOST now
advises: seven rules (R001-R007) scan the ledger, doctrine files, and
waivers on demand; findings are appended to an independent
hash-chained advisory stream at `advisories/stream.jsonl`. GHOST is
structurally read-only on the main ledger (a unit test enforces Shrike
I8 by walking the source tree). Six rituals registered; four executors
implemented (`verify`, `amend-doctrine`, `file-waiver`, `ghost-advise`).

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
