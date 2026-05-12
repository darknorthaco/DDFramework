# DDFramework Simulation Layer (Phase 6 wave 1)

Phase 5 established the kernel boundary; Phase 6 wave 1 lands the
simulation capabilities so Constellation §7 (*Simulate Before You
Scar Reality*) can be automated rather than honor-system. **All
five modules below are implemented** and exercised by the
``ddf-core/tests`` suite, including live-engine sanity tests against
the real ``ledger/events.jsonl``, ``advisories/stream.jsonl``, and
ceremony manifests in this repository.

## Modules

| Module | Purpose | Status |
|---|---|---|
| `doctrine_diff.py` | Semantic diff of two doctrine.toml versions: added/removed invariants, added/removed rituals, version delta, impact classification, ordered summary | implemented |
| `ritual_dryrun.py` | Validate a ritual invocation against its manifest and `[rituals].registered`; report would-be event kind, side effects, declared invariants, and arg validation — without invoking the executor | implemented |
| `ledger_replay.py` | Walk `events.jsonl` from genesis, recompute the canonical hash chain per `ledger/SPEC.md` §5, and report entry count, event-kind counts, timestamp monotonicity, chain integrity, and head hash | implemented |
| `advisory_replay.py` | Walk `advisories/stream.jsonl` from genesis, recompute the canonical hash chain per `advisories/SPEC.md` §4, count by `rule_id` / `severity` / `run_id`, and confirm each `ledger_tail_hash` resolves to a real ledger entry | implemented |
| `drift_simulation.py` | For a given scenario (`doctrine_drift` / `constellation_drift` / `binary_stale` / `all`), decide whether the corresponding GHOST rule (R001 / R002 / R003) would fire **right now** given the on-disk state of `doctrine.toml`, `constellation.toml`, and the main ledger | implemented |

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

### `ledger_replay.run(ledger_path) -> dict`

Implemented as of Phase 6 wave 1. Read-only audit walk of
``ledger/events.jsonl``. The file is opened ``"rb"``; the function
never writes anywhere. Canonical form matches ``ledger/SPEC.md`` §5
byte-for-byte (validated against the live engine ledger in
``tests/test_ledger_replay.py::test_live_engine_ledger_replays_cleanly``).

Returned dict (stable keys):

| Key | Type | Description |
|---|---|---|
| `ledger_exists` | `bool` | The file is present on disk. |
| `entry_count` | `int` | Number of well-formed entries walked before the first break (or to EOF if `chain_ok`). |
| `chain_ok` | `bool` | Every entry's recomputed hash matched and every `prev_entry_hash` linked back correctly to genesis. |
| `chain_break_at_line` | `int \| None` | 1-indexed line where the chain first broke, if any. |
| `chain_error` | `str \| None` | Machine-readable descriptor of the first break (`json_parse_error`, `missing_entry_hash`, `entry_hash_mismatch`, `chain_link_broken`, `blank_line`, `ledger_missing`). |
| `event_kind_counts` | `dict[str,int]` | Per-event-kind counts in key-sorted order. |
| `event_kinds` | `list[str]` | Sorted unique event kinds. |
| `first_entry_ts` / `last_entry_ts` | `str \| None` | RFC 3339 timestamps. |
| `timestamps_monotonic` | `bool` | RFC 3339 timestamps are non-decreasing line over line. |
| `timestamp_regression_at_line` | `int \| None` | First regression line, for R006-style audit. |
| `genesis_prev_hash` | `str \| None` | Should be `sha256:0…64`. |
| `head_hash` | `str` | `entry_hash` of the last walked entry; `sha256:0…64` if empty/missing. |
| `errors` | `list[str]` | Sorted machine-readable error descriptors (currently a singleton when chain breaks). |
| `ordered_summary` | `list[str]` | Deterministic short descriptors of the chain audit. |

### `advisory_replay.run(advisory_path, ledger_path) -> dict`

Implemented as of Phase 6 wave 1. Read-only audit walk of
``advisories/stream.jsonl``, with the ``ledger_path`` consulted
only to confirm each advisory's ``ledger_tail_hash`` resolves to a
known ledger ``entry_hash``. Both files are opened ``"rb"``; the
module writes nothing. Canonical form matches
``advisories/SPEC.md`` §4 (same rules as ``ledger/SPEC.md`` §5
with ``advisory_hash`` replacing ``entry_hash``); validated against
the live engine advisory stream in
``tests/test_advisory_replay.py::test_live_engine_advisory_stream_replays_cleanly``.

The ledger's own chain is **not** re-verified by this function — to
audit both, compose with ``ledger_replay`` separately.

Returned dict (stable keys):

| Key | Type | Description |
|---|---|---|
| `advisory_path_exists` / `ledger_path_exists` | `bool` | Files present on disk. |
| `advisory_count` | `int` | Advisories walked before the first break (or to EOF if `chain_ok`). |
| `chain_ok` | `bool` | Every advisory's recomputed hash matched and every `prev_advisory_hash` linked back to genesis. |
| `chain_break_at_line` | `int \| None` | 1-indexed line where the chain first broke. |
| `chain_error` | `str \| None` | First break descriptor (`json_parse_error`, `missing_advisory_hash`, `advisory_hash_mismatch`, `chain_link_broken`, `blank_line`, `advisory_stream_missing`). |
| `rule_id_counts` | `dict[str,int]` | Per-rule counts (key-sorted). |
| `severity_counts` | `dict[str,int]` | Per-severity counts (key-sorted). |
| `run_ids` | `list[str]` | Sorted unique `run_id`s. |
| `run_count` | `int` | `len(run_ids)`. |
| `tail_hashes_present_in_ledger` | `int` | Advisory `ledger_tail_hash`s that resolved against the ledger entry-hash set. |
| `tail_hashes_missing` | `int` | Count whose tail did not resolve. |
| `tail_hash_missing_lines` | `list[int]` | Sorted 1-indexed lines that referenced an unknown tail. |
| `head_hash` | `str` | Last walked `advisory_hash`; zero hash if empty/missing. |
| `genesis_prev_hash` | `str \| None` | Should be `sha256:0…64`. |
| `errors` | `list[str]` | Sorted machine-readable error descriptors. |
| `ordered_summary` | `list[str]` | Deterministic short descriptors of the audit. |

### `drift_simulation.run(ledger_path, doctrine_path, constellation_path, scenario) -> dict`

Implemented as of Phase 6 wave 1. Decides, statically and without
running GHOST, whether **R001 / R002 / R003** would fire given the
provided files. ``scenario`` must be one of:

| `scenario` | Rules evaluated |
|---|---|
| `"doctrine_drift"` | R001 only |
| `"constellation_drift"` | R002 only |
| `"binary_stale"` | R003 only |
| `"all"` | R001 + R002 + R003 |

Rule semantics (matching ``ghost-observer/ghost/rules`` R001–R003):

- **R001 doctrine_drift** — `sha256(doctrine.toml, LF-normalized)` differs from the latest amendment entry's `doctrine_hash`.
- **R002 constellation_drift** — same comparison on `constellation.toml` against the latest amendment's `constellation_hash`.
- **R003 binary_stale** — the latest `verify.result` entry's `doctrine_hash` differs from the latest amendment's `doctrine_hash` (executing binary embeds a stale doctrine hash).

The amendment lookup matches both legacy `event = "doctrine_amendment"`
(bootstrap-era) and current `event = "doctrine.amended"`. The file
hash form is the LF-normalized SHA-256 (read bytes, strip `\r`,
SHA-256) — byte-compatible with what phantom records and with what
`ghost.reader.sha256_file_normalized` computes.

Returned dict (stable keys):

| Key | Type | Description |
|---|---|---|
| `scenario` | `str` | Echo of the input. |
| `scenarios_checked` | `list[str]` | Sorted rule ids actually evaluated (empty if `scenario` was unknown). |
| `would_fire` | `dict[str, bool]` | Per-rule decision. Rules outside `scenarios_checked` are always `false`. |
| `doctrine_hash_on_disk` | `str \| None` | LF-normalized SHA-256 of `doctrine.toml`. |
| `latest_amendment_doctrine_hash` | `str \| None` | From the last amendment entry. |
| `constellation_hash_on_disk` | `str \| None` | LF-normalized SHA-256 of `constellation.toml`. |
| `latest_amendment_constellation_hash` | `str \| None` | From the last amendment entry. |
| `latest_verify_doctrine_hash` | `str \| None` | From the last `verify.result` entry. |
| `latest_amendment_line` / `latest_verify_line` | `int \| None` | 1-indexed lines in the ledger. |
| `ledger_entry_count` | `int` | Total well-formed JSON lines walked. |
| `errors` | `list[str]` | Sorted descriptors (`unknown_scenario`, `doctrine_file_missing`, `constellation_file_missing`, `no_doctrine_amendment_in_ledger`, `no_constellation_hash_in_latest_amendment`, `no_verify_result_in_ledger`). |
| `ordered_summary` | `list[str]` | Deterministic short descriptors of the decision set. |

Composes naturally with `ledger_replay` and `advisory_replay`: those
functions verify chain integrity end-to-end, while this one focuses
on the three drift conditions GHOST itself watches for.

## Contract (upheld by every module)

Each module exposes a pure `run(...)` function that:
- Takes explicit paths or strings as arguments (Shrike I5: no ambient state).
- Returns a structured result with stable keys and sorted lists.
- Is read-only on all ledger / advisory streams (and on every other input).
- Is stdlib-only.
- Produces a deterministic `ordered_summary` suitable for inclusion in
  audit reports or future simulation ledger entries.

## History

This layer was scaffolded as stubs during Phase 5 (engine kernelization,
v0.7.0) to reserve the namespace under the kernel boundary, signal intent
to downstream embedders, and let Phase 6 land as additive changes without
structural churn. Phase 6 wave 1 (the work documented above) lifted every
stub to a real implementation without weakening invariants I1–I8.
