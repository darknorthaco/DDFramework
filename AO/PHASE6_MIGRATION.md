# Phase 6 simulation — migration plan

Constellation §7 (*Simulate Before You Scar Reality*) is partially satisfied today by human process. Phase 6 in the engine introduces **stdlib-only** Python modules under [`ddf-core/simulation/`](../ddf-core/simulation/) (`ritual_dryrun`, `ledger_replay`, `advisory_replay`, `doctrine_diff`, `drift_simulation`).

## Current state (AO v0.1.0)

- `agent.simulate` appends a **stub** ledger line (`simulation_stub = true`, `phase = 6-stub`).
- No automatic call into `ddf-core/simulation/` yet (APIs are stubs).

## Migration steps (when Phase 6 lands)

1. **Contract** — define a stable JSON result shape from `ritual_dryrun.run(...)` and `ledger_replay.run(...)` (engine work).
2. **Shell ritual** — extend `agent.simulate` to:
   - call `python -m ddf_core.simulation` (or packaged module path TBD) with explicit `--shell-root`, `--proposal-id`, `--scenario-id` per I5;
   - append ledger line including `simulation_report_sha256` referencing a blob under `AO/ledger/blobs/` if large.
3. **Gate external acts** — optionally require `agent.simulate` **before** `agent.act` with `effect_class = external` (operator policy; could be enforced in orchestrator code reading the shell ledger).
4. **Tests** — ledger replay tests: replay shell ledger + verify each line’s hash; integration tests: run dryrun on a fixture scenario directory.

## Non-goals

- Weakening engine I1–I8.
- Writing simulation output to the **engine** main ledger.
