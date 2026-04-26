# AO application rituals

These rituals are **application-level** contracts. They are **not** registered in the engine’s `doctrine.toml` `[rituals].registered` list (engine policy: no app-specific rituals in the engine registry). They **are** the sole normal path for mutating the **shell ledger**.

Ritual manifests for the engine use `ceremonies/*.toml`; AO uses this markdown as the manifest until a separate application ceremony format is ratified.

## Template (all AO rituals)

| Field | Value |
|-------|--------|
| **inputs** | CLI flags + paths in `config/shell.toml` (I5: explicit `engine_root`) |
| **outputs** | One NDJSON line on `AO/ledger/events.jsonl` |
| **side_effects** | None beyond ledger append (external tools are **out of scope** for the library; orchestrators must log `agent.act` **before** invoking tools) |
| **invariants** | Shell ledger append uses engine `ddf::ledger::append`; `doctrine_hash` from engine `doctrine.toml` |
| **inverse** | Application-level compensating entries (future); destructive external acts require human rollback |

---

## ao-0001 — `agent.propose`

| | |
|--|--|
| **Purpose** | Record operator/agent intent with a stable `proposal_id`. |
| **Event** | `agent.propose` |
| **Engine verify** | Not required (read-only on engine). |
| **Extra fields** | `proposal_id`, `ritual_id`, `schema`, summary in `change` |

---

## ao-0002 — `agent.evaluate`

| | |
|--|--|
| **Purpose** | Bind a proposal to an evaluation verdict under a verified engine envelope. |
| **Event** | `agent.evaluate` |
| **Engine verify** | **Required** (`phantom verify` must succeed). |
| **Extra fields** | `proposal_id`, `verdict`, `ritual_id`, `schema` |

---

## ao-0003 — `agent.act`

| | |
|--|--|
| **Purpose** | Record an act (tool invocation intent). |
| **Event** | `agent.act` |
| **Engine verify** | **Required** before append. |
| **Privilege** | If `effect_class = external`, **ceremony file** required with `OPERATOR_APPROVED=1`. |
| **Extra fields** | `proposal_id`, `tool_id`, `effect_class`, `external_effect` (bool), optional `ceremony_content_sha256` |

---

## ao-0004 — `agent.reflect`

| | |
|--|--|
| **Purpose** | Learning-loop closure (hypothesis → observation → reflection). |
| **Event** | `agent.reflect` |
| **Engine verify** | **Required**. |
| **Extra fields** | `proposal_id`, `notes`, `ritual_id`, `schema` |

---

## ao-0005 — `agent.simulate` (Phase 6 stub)

| | |
|--|--|
| **Purpose** | Reserve ledger shape for simulation-first policy (Constellation §7). |
| **Event** | `agent.simulate` |
| **Engine verify** | **Required**. |
| **Extra fields** | `proposal_id`, `scenario_id`, `phase = 6-stub`, `simulation_stub = true` |

See [`PHASE6_MIGRATION.md`](./PHASE6_MIGRATION.md) for wiring to `ddf-core/simulation/`.
