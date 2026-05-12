# How AO aligns with DDFramework doctrine

This is a concise mapping for auditors. Engine prose sources: [`DDFRAMEWORK.md`](../DDFRAMEWORK.md), [`CONSTELLATION.md`](../CONSTELLATION.md), [`DOCTRINE.md`](../DOCTRINE.md).

| Engine principle / invariant | AO behavior |
|-------------------------------|-------------|
| **Ceremony-first** (DOCTRINE II.1) | External `agent.act` requires operator ceremony file; evaluate/act gate on `phantom verify` |
| **Append-only ledger (I1)** | Shell ledger via `ddf::ledger::append`; no in-place edits |
| **Content-addressed (I2)** | `doctrine_hash` binds each line to engine doctrine; optional `ceremony_content_sha256` |
| **Reversibility (I3)** | Application compensating entries are future work; destructive acts require explicit human rollback playbooks |
| **Deterministic builds (I4)** | AO crate is stdlib + `ddf` only; no new third-party deps in v0.1.0 |
| **No ambient state (I5)** | `engine_root` from `config/shell.toml`; CLI `--shell-root` optional override |
| **Doctrine-as-code (I6)** | Engine verify ensures the checked-out engine matches embedded Phantom hashes |
| **No silent mutation (I7)** | Orchestrators are instructed to append `agent.act` **before** external side effects become visible |
| **GHOST read-only (I8)** | Shell invokes GHOST only via `python -m ghost advise`; never writes advisories itself |
| **Constellation §9 / §10** | Proposal → evaluate → act → reflect mirrors doctrine-as-law and the Constellation loop at application scope |
| **Constellation §7 (simulation)** | `agent.simulate` stub + [`PHASE6_MIGRATION.md`](./PHASE6_MIGRATION.md) ties forward to `ddf-core/simulation/` |

**Explicit non-goals:** AO does not amend engine doctrine, does not register rituals in engine `doctrine.toml`, and does not write `agent.*` events to the engine main ledger.
