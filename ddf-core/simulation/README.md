# DDFramework Simulation Layer (Phase 6 scaffolding)

Stubs only. Phase 5 establishes the kernel boundary; Phase 6 implements
the simulation capabilities so Constellation §7 (*Simulate Before You
Scar Reality*) can be automated rather than honor-system.

## Planned modules

| Module | Purpose | Status |
|---|---|---|
| `doctrine_diff.py` | Semantic diff of two doctrine.toml versions: added/removed invariants, changed versions, impact classification | stub |
| `ritual_dryrun.py` | Execute a ritual without writing to the ledger; return the would-be entry | stub |
| `ledger_replay.py` | Replay the main ledger from genesis; verify chain and rerun each ritual's observable effects | stub |
| `advisory_replay.py` | Replay the advisory stream; recompute each advisory against the ledger tail it references | stub |
| `drift_simulation.py` | Synthesize "what if doctrine changed but amend-doctrine wasn't run" scenarios and confirm GHOST R001/R002/R003 fire as expected | stub |

## Contract (Phase 6 target)

Each module exposes a pure `run(...)` function that:
- Takes explicit paths as arguments (Shrike I5: no ambient state).
- Returns a structured result without side effects.
- Is read-only on all ledger / advisory streams.
- Is stdlib-only.

## Why scaffolded in Phase 5

Creating the placeholders now:
1. Reserves the module namespace under the kernel boundary.
2. Signals intent to downstream embedders (*the engine will grow a
   simulation contract*).
3. Allows Phase 6 to land as additive changes without further
   structural churn.
