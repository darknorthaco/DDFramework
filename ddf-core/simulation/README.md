# DDFramework Simulation Layer (Phase 6 scaffolding)

Stubs only. Phase 5 establishes the kernel boundary; Phase 6 implements
the simulation capabilities so Constellation §7 (*Simulate Before You
Scar Reality*) can be automated rather than honor-system.

## Planned modules

| Module | Purpose | Status |
|---|---|---|
| `doctrine_diff.py` | Semantic diff of two doctrine.toml versions: added/removed invariants, added/removed rituals, version delta, impact classification, ordered summary | implemented |
| `ritual_dryrun.py` | Validate a ritual invocation against its manifest and `[rituals].registered`; report would-be event kind, side effects, declared invariants, and arg validation — without invoking the executor | implemented |
| `ledger_replay.py` | Replay the main ledger from genesis; verify chain and rerun each ritual's observable effects | stub |
| `advisory_replay.py` | Replay the advisory stream; recompute each advisory against the ledger tail it references | stub |
| `drift_simulation.py` | Synthesize "what if doctrine changed but amend-doctrine wasn't run" scenarios and confirm GHOST R001/R002/R003 fire as expected | stub |

### `doctrine_diff.run(old_doctrine_str, new_doctrine_str) -> dict`

Implemented as of Phase 6 wave 1. Takes two explicit TOML strings (I5:
no ambient state, no filesystem reads) and returns a dict with stable
keys:

| Key | Type | Description |
|---|---|---|
| `added_invariants` | `list[str]` | Sorted invariant ids present only in *new*. |
| `removed_invariants` | `list[str]` | Sorted invariant ids present only in *old*. |
| `added_rituals` | `list[str]` | Sorted ritual names registered only in *new*. |
| `removed_rituals` | `list[str]` | Sorted ritual names registered only in *old*. |
| `version_delta` | `str` | One of `patch \| minor \| major \| breaking`; mirrors `impact` today, kept distinct so a richer version encoding can be added later without breaking the schema. |
| `impact` | `str` | Same four-value classification. Precedence: **breaking > major > minor > patch**. |
| `ordered_summary` | `list[str]` | Deterministic, sorted list of short descriptors (`added_invariant:I9`, `removed_ritual:deploy`, `weakened_invariant:I1`, `version_regression:0.7.0->0.6.0`, …) covering every detected change. |

Classification rules:

- **patch** — text clarifications only; no semantic change detected.
- **minor** — at least one invariant or ritual added; nothing removed or weakened.
- **major** — an invariant was removed, an invariant was weakened
  (severity downgrade on an invariant common to both sides), or a
  ritual was renamed (both an addition and a removal in the same diff).
- **breaking** — a ritual was removed with no compensating addition,
  or `doctrine_version` regressed (new < old by semver).

### `ritual_dryrun.run(ritual_id, args, ceremony_dir, doctrine_path) -> dict`

Implemented as of Phase 6 wave 1. Static validator that answers
"could this ritual be invoked right now, with these arguments?"
**without** running the executor and **without** touching the
ledger. ``ritual_id`` accepts ``"0001"``, ``"1"``, or the kebab name
``"verify"``. ``args`` is the caller-proposed argument map. Both
``ceremony_dir`` (containing ``NNNN-<name>.toml`` manifests) and
``doctrine_path`` are explicit per I5.

Returned dict (stable keys; all list values sorted):

| Key | Type | Description |
|---|---|---|
| `ritual_id` | `str \| None` | Canonical 4-digit id, or `None` if unresolvable. |
| `ritual_name` | `str` | Manifest name; `""` if not found. |
| `ritual_status` | `str` | One of `implemented \| declared \| unknown`. |
| `registered` | `bool` | Name appears in `doctrine.toml [rituals].registered`. |
| `manifest_found` | `bool` | A matching `NNNN-<name>.toml` exists. |
| `would_be_event_kind` | `str \| None` | `[outputs].ledger_event_kind` from the manifest. |
| `inverse` | `str \| None` | Declared inverse ritual or self/none. |
| `irreversibility_confirmation` | `str \| None` | Confirmation gate, if irreversible. |
| `declared_invariants` | `list[str]` | Sorted `Ix` ids from `[invariants_upheld]`. |
| `reads` / `writes` | `list[str]` | Sorted side-effect paths from the manifest. |
| `network` | `bool` | Network-touching ritual per the manifest. |
| `required_args` / `optional_args` | `list[str]` | Sorted arg names per `[inputs]`. |
| `provided_args` | `list[str]` | Sorted keys of caller `args`. |
| `missing_required_args` | `list[str]` | Required args the caller omitted. |
| `unknown_args` | `list[str]` | Provided args not declared by the manifest. |
| `ok` | `bool` | All of: registered, manifest found, status implemented, no missing required, no unknown args, no manifest parse errors. |
| `errors` | `list[str]` | Sorted machine-readable error descriptors. |
| `ordered_summary` | `list[str]` | Deterministic short descriptors of the dry-run state. |

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
