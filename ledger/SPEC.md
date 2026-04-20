# Ledger Specification

The ledger is the system of record. Every ritual, every amendment,
every waiver writes here. It is append-only, hash-chained, and
committed to version control so history is auditable.

## 1. Format

- **File:** `ledger/events.jsonl`
- **Encoding:** UTF-8
- **Framing:** NDJSON (one JSON object per line, separated by `\n`)
- **One event per line.** No trailing whitespace. File must end with
  `\n`.
- **Never rewritten.** Editing or removing any existing line is a
  doctrine violation (Constellation §13, Shrike I1).

## 2. Blob Store

- **Location:** `ledger/blobs/<first-two-hex>/<remaining-hex>`
  (e.g. `ledger/blobs/ab/cdef...`)
- Any artifact too large or non-textual to embed in a ledger entry
  is written as a blob and referenced by its SHA-256 from the entry.
- Blobs are immutable once written.

## 3. Required Fields (every entry)

| Field | Type | Meaning |
|---|---|---|
| `timestamp` | string | RFC 3339 / ISO 8601 UTC, e.g. `2026-04-20T22:14:00Z` |
| `event` | string | lowercase-snake identifier, e.g. `doctrine_amendment` |
| `version` | string | SemVer of whatever is being changed |
| `change` | string | one-sentence human summary |
| `domain` | string | one of `obvious`, `complicated`, `complex`, `chaotic` |
| `integrity_check` | bool | did the change pass conceptual-integrity review? |
| `regenerative_check` | bool | did the change pass regenerative review? |
| `simulation_required` | bool | was a simulation required, per Constellation §7? |
| `disruption_considered` | bool | was Christensen disruption analysis applied? |
| `doctrine_hash` | string | `sha256:<hex>` of `doctrine.toml` at entry time |
| `prev_entry_hash` | string | `sha256:<hex>` of the previous line's `entry_hash`, or `sha256:0000…` for the genesis entry |
| `entry_hash` | string | `sha256:<hex>` of this entry in canonical form (see §5) |

## 4. Optional / Event-Specific Fields

Events may include additional fields specific to their kind. The
ritual contracts in [`RITUALS.md`](../RITUALS.md) define those.

## 5. Canonical Form for Hashing

`entry_hash` is computed as follows:

1. Take the JSON object **without** the `entry_hash` field.
2. Serialize in canonical form:
   - Sort keys lexicographically (recursive for nested objects)
   - No insignificant whitespace (no spaces after `:` or `,`)
   - UTF-8 encoding
   - No trailing newline
3. `entry_hash = "sha256:" + hex(sha256(canonical_bytes))`
4. Write the entry back with `entry_hash` as the **last** field for
   readability, then append `\n` and the line to
   `ledger/events.jsonl`.

This canonical form is compatible with
[RFC 8785 (JSON Canonicalization Scheme)](https://datatracker.ietf.org/doc/html/rfc8785)
for the subset we use. Readers that only need to verify the chain
may use any RFC 8785 implementation.

## 6. Hash Chain

- The first entry (genesis) has
  `prev_entry_hash = "sha256:0000000000000000000000000000000000000000000000000000000000000000"`.
- Every subsequent entry sets `prev_entry_hash` to the `entry_hash`
  of the immediately previous line.
- `phantom verify` recomputes the chain from genesis. Any mismatch
  halts the ritual with `status = "ledger-tampered"`.

## 7. Event Kinds (growing registry)

| `event` | Purpose | Origin |
|---|---|---|
| `doctrine_amendment` | Ratifies or updates a doctrine document | Amendment ceremony |
| `verify.result` | Records the outcome of `phantom verify` | Ritual `0001-verify` |
| `deploy.applied` | Records a deployment mutation | Ritual `0002-deploy` |
| `lan.scan.result` | Records a LAN discovery scan | Ritual `0003-lan-scan` |
| `waiver.filed` | Records a new waiver | Waiver protocol |
| `waiver.expired` | Records automatic expiration | Ledger keeper |
| `postmortem` | Records a blame-free retrospective | Constellation §6 |

New event kinds are added as rituals are registered. A new kind is
itself a Tier-1 change: it must be added in a doctrine amendment.

## 8. Reading the Ledger

Tools that read the ledger must:

- Be read-only (Shrike I8, Constellation §3 integrity).
- Verify the hash chain before trusting content.
- Report chain breaks as warnings, never silently repair.

`ghost-observer` is the reference reader; any custom tool should
behave identically with respect to chain verification.

## 9. Backup and Recovery

- The ledger is tracked in git. Its history *is* the system's history.
- A corrupted ledger is recovered by `git checkout` of the last
  known-good commit, followed by a `phantom verify` run whose
  `verify.result` entry is the next line written.
- Never edit history. If a past entry was incorrect, the correction
  is a new entry with `event = "ledger_correction"` and a reference
  back to the entry being corrected. The old entry stays.
