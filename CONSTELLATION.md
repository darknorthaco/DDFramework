# The Constellation Doctrine

**Version:** 0.1.1 — Binding Until Superseded
**Status:** Ratified
**A Unified Framework for Designing Long-Horizon, Regenerative, Coherent Systems**
**Machine-readable mirror:** [`constellation.toml`](./constellation.toml)

---

## 0. Purpose

The Constellation Doctrine defines the governing principles, invariants,
and enforcement mechanisms for designing systems that must endure across
decades, adapt across complexity, regenerate rather than deplete, and
remain coherent under pressure.

**This doctrine is binding.**
It governs all architectural, organizational, and strategic decisions.
It is the constitution of the system.

---

## 1. Reality Is Systems

**Principle.** All technology exists within interconnected systems
governed by stocks, flows, delays, feedback loops, and leverage points.

**Mandates:**

- Every major decision begins with a system map.
- Stocks, flows, and feedback loops must be explicitly identified.
- Delays must be surfaced; hidden delays are treated as risks.
- Leverage points must be documented and protected.
- System boundaries must be defined and justified.

**Invariant.** No design, feature, or policy is accepted without a
systems model.

---

## 2. Context Governs Action (Cynefin)

**Principle.** Different domains require different modes of action.
Misclassification is a primary source of failure.

**Mandates:**

- Every initiative must declare its domain:
  - **Obvious**
  - **Complicated**
  - **Complex**
  - **Chaotic**
- The method must match the domain:
  - Obvious → best practices
  - Complicated → analysis + expertise
  - Complex → probe–sense–respond
  - Chaotic → act–sense–respond
- Domain drift must be logged in the ledger.

**Invariant.** No "one-size-fits-all" method is permitted.

---

## 3. Conceptual Integrity Above All

**Principle.** Conceptual integrity is the single most important quality
of a system. A coherent system outlives and outperforms a feature-rich
but incoherent one.

**Mandates:**

- Architectural decisions are moral decisions.
- Prefer small, orthogonal primitives over sprawling abstractions.
- Every subsystem must have a single, clear purpose.
- Interfaces must be minimal, explicit, and stable.
- Reject any design that harms long-term clarity.

**Invariant.** If a design harms conceptual integrity, it is rejected
regardless of short-term benefit.

---

## 4. 100-Year Computing (Alan Kay)

**Principle.** Systems must be designed to be understood, rebuilt, and
extended by future generations.

**Mandates:**

- All core artifacts must be plain text or plain-text-addressable.
- Toolchains must be open, reconstructable, and documented.
- No foundational component may rely on proprietary formats.
- Designs must pass the 100-year test: *can a future engineer rebuild
  this from scratch with minimal assumptions?*

**Invariant.** If it cannot be rebuilt in 100 years, it cannot be
foundational.

---

## 5. Regenerative Design (Wahl)

**Principle.** Systems must regenerate more than they deplete —
technically, socially, and ecologically.

**Mandates:**

- Every design must identify what it regenerates and what it depletes.
- Net-negative designs are prohibited unless explicitly waived.
- Nested scales must be respected:
  **Individual → Team → Organization → Ecosystem → Biosphere**
- Regeneration must be measurable or observable.

**Invariant.** Every design must answer: **"What does this heal?"**

---

## 6. Organizations Are Systems (Senge)

**Principle.** Teams and organizations are living systems with mental
models, feedback loops, and learning cycles.

**Mandates:**

- Every project must include a learning loop:
  *hypothesis → action → observation → reflection → doctrine update*.
- Mental models must be surfaced and challenged.
- Shared vision must be explicit and documented.
- Blame-free retrospectives are mandatory after significant events.

**Invariant.** No system evolves faster than the learning rate of the
organization that builds it.

---

## 7. Simulate Before You Scar Reality (Sterman)

**Principle.** Complex systems behave in counterintuitive ways.
Simulation is mandatory before intervention.

**Mandates:**

- Any change affecting a core loop must be simulated.
- Simulations must include delays, nonlinearities, and second-order
  effects.
- Predictions must be logged in the ledger.
- Outcomes must be compared to predictions.

**Invariant.** No core-loop change is deployed without simulation or
explicit waiver.

---

## 8. Disruption Is a System Pattern (Christensen)

**Principle.** Disruption is predictable and must be intentionally
managed.

**Mandates:**

- Maintain at least one deliberately disruptive track.
- Protect exploratory teams from the core's efficiency-driven immune
  system.
- Design for low-end and new-market threats.
- Be willing to build the thing that kills the current product.

**Invariant.** If we do not disrupt ourselves, someone else will.

---

## 9. Doctrine as Law, Code as Enforcement

**Principle.** Doctrine is the human-readable constitution.
Machine-readable doctrine enforces it.

**Mandates:**

- All doctrine must exist in:
  - `DOCTRINE.md` / `CONSTELLATION.md` (human)
  - `doctrine.toml` / `constellation.toml` (machine)
- Code must enforce doctrine invariants where possible.
- Doctrine changes require ceremony:
  *proposal → rationale → review → ledger entry → version bump.*

**Invariant.** No unspoken rules. If it matters, it is written and
enforced.

---

## 10. The Constellation Loop (Unified Method)

Every major decision must pass through this loop:

1. **Map the system** (Meadows)
2. **Classify the domain** (Snowden)
3. **Choose the method** (Cynefin)
4. **Architect for integrity** (Maier & Rechtin)
5. **Check regenerative impact** (Wahl)
6. **Embed learning loops** (Senge)
7. **Simulate critical policies** (Sterman)
8. **Stress-test against disruption** (Christensen)
9. **Encode and enforce doctrine** (Kay + all)

**Invariant.** Skipping steps requires a formal waiver.

---

## 11. Conflict Resolution Rule (Doctrine Priority)

When principles conflict, the following precedence applies:

1. 100-Year Computing
2. Regenerative Design
3. Conceptual Integrity
4. Systems Reality
5. Simulation Before Deployment
6. Context-Aware Action
7. Organizational Learning
8. Disruption Strategy
9. Doctrine as Law

**Invariant.** Principles 1–3 cannot be overridden.

---

## 12. Scoping Tiers (Enforcement Burden Mitigation)

### Tier 1 — Core System Changes (Full Loop Required)

Architecture, protocols, ledger format, security boundaries, scaling
policies.

### Tier 2 — Significant Feature Work (Abbreviated Loop)

System map, domain classification, integrity check, regenerative check.

### Tier 3 — Minor Changes (Lightweight Check)

Domain classification + integrity check.

**Invariant.** No change is exempt from doctrine — only the scope
varies.

---

## 13. Ledger Rules

- **Format:** NDJSON
- **Encoding:** UTF-8
- **One event per line**
- **Hashing:** SHA-256
- **Location:** `ledger/events.jsonl`
- **Blobs:** `ledger/blobs/<sha256>`
- **Append-only**
- **Mutations require a waiver**

Format details and hash-chain framing: [`ledger/SPEC.md`](./ledger/SPEC.md).

---

## 14. Waiver Protocol

A waiver requires:

- Written rationale
- Domain classification
- System map of affected area
- Simulation (if applicable)
- Approval by the Human Architect
- Ledger entry with:
  - `timestamp`
  - `rationale`
  - `impacted_principles`
  - `expected_consequences`
  - `expiry_date`

**Invariant.** Waivers expire unless renewed.

Active waivers are tracked in [`WAIVERS.md`](./WAIVERS.md).

---

## 15. Canonical Ledger Entry Example

```json
{
  "timestamp": "2026-04-20T22:14:00Z",
  "event": "constellation_doctrine_update",
  "version": "0.1.1",
  "change": "Adopted Constellation Doctrine v0.1.1",
  "domain": "complicated",
  "integrity_check": true,
  "regenerative_check": true,
  "simulation_required": false,
  "disruption_considered": true,
  "doctrine_hash": "sha256:TO_BE_FILLED_AFTER_COMMIT"
}
```

The canonical form used for hashing and the required extension fields
(`prev_entry_hash`, `entry_hash`) are specified in
[`ledger/SPEC.md`](./ledger/SPEC.md).

---

## 16. Closing Principle

> We design systems that endure.
> We design systems that regenerate.
> We design systems that remain coherent under pressure.
> We design systems that future generations can rebuild.
> We design systems that learn.
> We design systems that last.
>
> This is the Constellation Doctrine.
> This is binding law.

---

## 17. Relationship to the DDFramework Architectural Doctrine

Constellation is the **constitution**. It governs principle.
The DDFramework [`DOCTRINE.md`](./DOCTRINE.md) is the **architecture** —
the specific instantiation that implements those principles as
ritual-first, ledger-backed, invariant-enforced code.

When they conflict, Constellation §11 priority order applies.
In practice no DDFramework invariant (I1–I8, historically labeled
*"Shrike I1–I8"*) contradicts any Constellation principle; the
invariants are the concrete mechanisms by which Constellation's
mandates are enforced in this engine.

Amendments to either document require the same ceremony and the same
ledger. For the engine's identity and scope definition see
[`DDFRAMEWORK.md`](./DDFRAMEWORK.md).
