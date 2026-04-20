# Advisory Stream Specification

The advisory stream is GHOST's write surface. It is **physically
separate** from the main ledger to uphold Shrike invariant I8:
**GHOST never writes to `ledger/events.jsonl`.**

## 1. Format

- **File:** `advisories/stream.jsonl`
- **Encoding:** UTF-8
- **Framing:** NDJSON (one JSON object per line, separated by `\n`)
- **One advisory per line.** No trailing whitespace.
- **Append-only.** Editing or removing any existing line is a doctrine
  violation (Constellation §13, by analogy with the main ledger).

## 2. Blob store

- **Location:** `advisories/blobs/<first-two-hex>/<remaining-hex>`
- For evidence too large to embed inline.

## 3. Required fields (every advisory)

| Field | Type | Meaning |
|---|---|---|
| `timestamp` | string | RFC 3339 UTC |
| `rule_id` | string | e.g. `R001_doctrine_drift` |
| `severity` | string | `info` \| `warn` \| `critical` |
| `subject` | string | one-line summary |
| `evidence` | object | rule-specific diagnostic data (may nest) |
| `recommended_action` | string | human-readable next step |
| `ledger_tail_hash` | string | `entry_hash` of the main ledger head observed |
| `run_id` | string | 16-hex-char token; groups advisories from one advisor run |
| `prev_advisory_hash` | string | `entry_hash` of previous advisory, or `sha256:0000…` |
| `advisory_hash` | string | `sha256:<hex>` of this advisory in canonical form |

## 4. Canonical form

Same rules as the main ledger (see `ledger/SPEC.md` §5):

1. Take the JSON object **without** `advisory_hash`.
2. Serialize with sorted keys (recursively for nested objects), no
   whitespace, UTF-8.
3. `advisory_hash = "sha256:" + hex(sha256(canonical_bytes))`.
4. Write with `advisory_hash` as the last field for readability.

## 5. Hash chain

- Genesis (first line) has `prev_advisory_hash = sha256:000…`.
- Every subsequent line links via `prev_advisory_hash = <previous line's advisory_hash>`.
- `python -m ghost verify-advisories` recomputes the chain and halts
  on any break.

## 6. Rule registry (Phase 4)

| Rule ID | Severity (max) | What it catches |
|---|---|---|
| `R000_bootstrap` | info | Advisory stream initialization — always first line |
| `R001_doctrine_drift` | warn | `doctrine.toml` on disk differs from last `doctrine.amended` hash |
| `R002_constellation_drift` | warn | `constellation.toml` on disk differs from last amendment hash |
| `R003_binary_stale` | warn | most recent `verify.result` has an older doctrine hash than latest amendment |
| `R004_waiver_expiring` | critical | waiver expired (or expiring soon; info / warn / critical by proximity) |
| `R005_unknown_event_kind` | warn | ledger contains an event not in `ledger/SPEC.md §7` |
| `R006_timestamp_regression` | critical | a ledger entry's timestamp is earlier than its predecessor |
| `R007_ledger_staleness` | critical | no ledger activity for a long time (info >30d, warn >90d, critical >365d) |

New rules are added by creating `ghost-observer/ghost/rules/rNNN_*.py`
and registering them in `ghost/rules/__init__.py`. Adding a rule is a
Tier 2 change (abbreviated loop).

## 7. Relationship to the main ledger

- GHOST reads `ledger/events.jsonl`. Never writes to it.
- Advisories reference `ledger_tail_hash` so you can locate the exact
  ledger state the advisory was about.
- If the main ledger is truncated or replaced, older advisories still
  stand as historical record — the evidence inside them is self-
  contained.

## 8. Reading advisories

Any tool that can parse NDJSON can read this file. The hash chain is
optional for readers; required for writers. Recommended reader
behavior: validate the chain first, fail loudly on breaks.
