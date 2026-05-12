# Shell ledger

`events.jsonl` is the **append-only** application ledger (same canonical hashing rules as the engine; see [`ledger/SPEC.md`](../ledger/SPEC.md)).

- **Track in git** for auditability (like the engine ledger policy).
- **Never rewrite** past lines; corrections are new events.
- Initialize with an empty file or a genesis ceremony line when bootstrapping a deployment.
