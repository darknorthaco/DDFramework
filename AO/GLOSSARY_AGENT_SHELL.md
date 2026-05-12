# Glossary — Constitutional Agent Shell

Decodes **application** terms. Engine mission vs mechanism vocabulary is in [`GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md).

| Term | Meaning |
|------|---------|
| **Shell ledger** | `AO/ledger/events.jsonl` — append-only application truth |
| **Engine ledger** | `ledger/events.jsonl` in DDFramework — Phantom-only |
| **Kernel** | `ddf` Rust crate / CLI per [`KERNEL_API_MAP.md`](../ddf-core/KERNEL_API_MAP.md) |
| **Ritual (application)** | One of `agent.propose`, `agent.evaluate`, `agent.act`, `agent.reflect`, `agent.simulate` |
| **Ritual (engine)** | Registered in engine `doctrine.toml` — `verify`, `deploy`, … |
| **Ceremony file** | Operator-written token file for external-effect approval |
| **GHOST** | Engine advisor; invoked only via `engine_advise` / `ddf advise` |
| **Phantom** | Engine ritual executor; invoked only via `engine_verify` / `ddf verify` |
| **proposal_id** | Correlates a single lifecycle across shell events |

## Event kinds (shell)

| `event` | Ritual id |
|---------|-----------|
| `agent.propose` | ao-0001 |
| `agent.evaluate` | ao-0002 |
| `agent.act` | ao-0003 |
| `agent.reflect` | ao-0004 |
| `agent.simulate` | ao-0005 |

These are **application** kinds — they are **not** listed in engine [`ledger/SPEC.md`](../ledger/SPEC.md) §7 and must not be written to the **engine** main ledger.
