# Security model — Constitutional Agent Shell

## Threat model (concise)

| Threat | Mitigation |
|--------|------------|
| Silent agent mutation | All mutations are **`agent.*` ledger lines** on the shell ledger |
| Bypassing engine safety | `agent.evaluate`, `agent.act`, `agent.reflect`, `agent.simulate` call **`phantom verify`** first |
| GHOST overriding Phantom | **Not possible** — GHOST never writes the engine main ledger (I8); AO never asks it to |
| Operator mistake on destructive tools | **External** `agent.act` requires **`OPERATOR_APPROVED=1`** in a ceremony file whose hash is logged |
| Audit forgery | Hash chain on shell ledger (`ddf::ledger::verify_chain`) |

## Application invariants (AO-specific)

**A1 — Shell append-only.** `AO/ledger/events.jsonl` is never edited in place; corrections are new lines (same spirit as engine I1).

**A2 — Engine envelope binding.** Every shell event includes `doctrine_hash` from the **engine** `doctrine.toml` at append time (content-addressed envelope).

**A3 — No advisory authority.** GHOST output is **non-authoritative** for privileged execution; ceremony + operator process is authoritative.

**A4 — Explicit engine root.** `engine_root` must be set in `config/shell.toml` (no hidden discovery of engine path).

## Privilege classes

| Class | Definition | Approval |
|-------|------------|----------|
| `ledger_only` | State change confined to ledgers / files under AO | Engine verify + ritual |
| `external` | Any effect outside AO’s tree (network, cloud APIs, system) | Above + **ceremony file** |

## Ceremony file

Minimum viable line:

```text
OPERATOR_APPROVED=1
```

The shell logs `ceremony_content_sha256` when a ceremony path is supplied to `agent.act`.

## Hyperion / transport

Future peers must authenticate **outbox** messages against shell ledger hashes (design position; wire protocol TBD when Hyperion activates).
