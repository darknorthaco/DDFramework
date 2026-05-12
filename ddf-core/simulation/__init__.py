"""DDFramework simulation layer — Phase 6 waves 1 + 2.

All five modules in this package were implemented at engine v0.7.0
(wave 1) and exposed via the ``python -m ddf simulate`` CLI in wave 2;
ratified together at engine v1.0.0:

- ``doctrine_diff``       semantic diff of two ``doctrine.toml`` strings
- ``ritual_dryrun``       static validation of a ritual invocation
                          against its manifest + ``doctrine.toml``
- ``ledger_replay``       chain audit of ``ledger/events.jsonl``
- ``advisory_replay``     chain audit of ``advisories/stream.jsonl``,
                          cross-checked against the ledger's
                          ``entry_hash`` set
- ``drift_simulation``    decide whether GHOST R001 / R002 / R003 would
                          fire right now given on-disk state

Every module exposes a pure ``run(...)`` that is stdlib-only,
read-only on ledger / advisory streams, and takes explicit paths
(I5: no ambient state). Return values are dicts with stable keys
and deterministic ``ordered_summary`` lists. See
``ddf-core/simulation/README.md`` for the per-module return schema.
"""

__version__ = "1.0.0"
