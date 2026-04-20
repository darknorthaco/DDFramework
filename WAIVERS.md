# Waiver Registry

Active waivers against the Constellation Doctrine or Shrike invariants.

A waiver is the **only** legitimate way to skip a doctrine requirement.
Undocumented deviations are violations. See
[`CONSTELLATION.md`](./CONSTELLATION.md) §14.

## 1. How to File a Waiver

1. Copy the schema below into a new entry in this file.
2. Fill every field. Missing fields invalidate the waiver.
3. Write a corresponding `waiver.filed` entry to
   `ledger/events.jsonl` with the same content hash.
4. Obtain Human Architect approval.
5. Link the ledger entry hash back into this file.
6. A waiver is only in force once both this file and the ledger
   reflect it and the approval has been recorded.

## 2. Waiver Schema

```
### W-YYYYMMDD-NN — <short title>

- Status:             proposed | approved | expired | withdrawn
- Filed:              YYYY-MM-DD
- Expires:            YYYY-MM-DD
- Filed by:           <name>
- Approved by:        <Human Architect name> (or: pending)
- Impacted principles: [list from CONSTELLATION.md §1-§9]
- Impacted invariants: [list from doctrine.toml, e.g. I5, I7]
- Domain classification: obvious | complicated | complex | chaotic
- System map:         <path to system map, or inline summary>
- Simulation:         required=yes/no; if yes, link to prediction log
- Rationale:          <written rationale>
- Expected consequences:
    - <bullet>
    - <bullet>
- Rollback plan:      <how we recover if the waiver was a mistake>
- Ledger entry hash:  sha256:...
- Renewal policy:     never | operator-review-at-expiry
```

## 3. Active Waivers

*(none)*

## 4. Expired Waivers

*(none)*

## 5. Rules

- **Waivers expire.** No waiver is indefinite.
  ([`CONSTELLATION.md`](./CONSTELLATION.md) §14.)
- **Principles 1–3 of Constellation §11 cannot be waived.**
  (100-Year Computing, Regenerative Design, Conceptual Integrity.)
- **Shrike's invariants I1, I6, I7 cannot be waived** — they are the
  substrate on which the waiver system itself depends (append-only
  ledger, doctrine-as-code, no-silent-mutation).
- Renewal of a waiver is itself a new ceremony with its own ledger
  entry. Silent re-approval is forbidden.
