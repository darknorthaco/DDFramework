# ghost-observer

Read-only observer for the Shrike Phantom ledger.

Part of the Shrike fabric. See project-level
[`CONSTELLATION.md`](../CONSTELLATION.md) and
[`DOCTRINE.md`](../DOCTRINE.md).

## Invariants

GHOST is **read-only by construction** (Shrike I8, Constellation §3):

- No module in this package opens a file with write mode.
- No module imports anything from `phantom-core`, `hyperion-net`, or
  their build outputs.
- GHOST consumes the ledger file and emits human-readable advisories
  to stdout. Any advisories destined for disk go to a SEPARATE
  advisory stream, never to `ledger/events.jsonl`.

## Runtime dependencies

**None.** Python 3 standard library only. See
[`../LANGUAGES.md`](../LANGUAGES.md) §3.3.

## Usage

```sh
python -m ghost [path/to/events.jsonl]
```

Exits 0 on valid chain, non-zero on any chain break or parse error.
