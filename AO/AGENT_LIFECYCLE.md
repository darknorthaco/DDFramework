# Agent lifecycle

This document describes the **normative lifecycle** for a governed agent running on AO. It aligns with Constellation’s learning and simulation mandates without changing engine doctrine.

## States

1. **Idle** — no open `proposal_id`, or last cycle completed with `agent.reflect`.
2. **Proposed** — `agent.propose` appended; intent is public and hash-chained.
3. **Evaluated** — `agent.evaluate` appended after **engine verify** succeeds; verdict is binding for automation policy **only if** the operator’s playbook says so.
4. **Acting** — `agent.act` appended; external class additionally requires **ceremony approval**.
5. **Reflecting** — `agent.reflect` appended; captures post-hoc notes for audits.

## Happy path (human-first)

1. Operator or agent proposes work under `proposal_id`.
2. Operator runs **engine verify** (CI or local); if red, **stop** — no evaluate/act.
3. Evaluator (human or constrained automaton) records `verdict` (e.g. `accept`, `reject`, `needs-simulation`).
4. If external side effects: operator prepares ceremony file → `agent.act --effect external --ceremony …`.
5. Orchestrator may call tools **only after** the `agent.act` line exists (I7: ledger intent before visible side effects).
6. Reflection closes the loop.

## Domain (Cynefin)

Each shell line carries `domain` (`obvious` | `complicated` | `complex` | `chaotic`) per [`constellation.toml`](../constellation.toml). Drift of domain mid-cycle should be logged as a new `agent.reflect` or a new proposal, not silent edits.

## Failure modes

| Failure | Detection | Recovery |
|---------|-------------|----------|
| Engine verify fails | non-zero exit | fix engine workspace; do not append evaluate/act |
| Shell ledger chain break | `ddf::ledger::verify_chain` | treat as incident; append compensating human-reviewed entry (future ceremony) |
| Missing ceremony | `agent.act` rejected | operator creates approval file |
| GHOST critical advisory | rule output | human triage; advisories do not auto-block unless playbook wires them |

## Stubs

- **Phase 6:** `agent.simulate` records intent only; see [`PHASE6_MIGRATION.md`](./PHASE6_MIGRATION.md).
