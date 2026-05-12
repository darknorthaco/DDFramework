# DDFramework — Architectural Doctrine

**Version:** 0.6.0
**Status:** Ratified
**Engine identity document:** [`DDFRAMEWORK.md`](./DDFRAMEWORK.md)
**Machine-readable mirror:** [`doctrine.toml`](./doctrine.toml)
**Constitutional layer:** [`CONSTELLATION.md`](./CONSTELLATION.md) (Constellation Doctrine v0.1.1)
**Amendment policy:** ceremony-only (see bottom of this file)

> This document is the **architectural** doctrine of the DDFramework
> engine — the concrete invariants and layers that implement the
> principles of the [Constellation Doctrine](./CONSTELLATION.md).
> When they conflict, Constellation §11 priority applies. The
> DDFramework invariants I1–I8 (historically labeled *"Shrike
> I1–I8"* in code comments and manifests; labels frozen per the v0.6.0
> scope redefinition) are the mechanisms by which Constellation's
> mandates are enforced in the engine.
>
> "Shrike" is a legacy umbrella label at the workspace level; the
> *engine* is DDFramework. See [`DDFRAMEWORK.md`](./DDFRAMEWORK.md)
> for the full scope definition.

---

## Preamble

This document is the sovereign doctrine of the Shrike project — the
combined Phantom / GHOST core. It is the single source of truth for
the system's values, boundaries, and invariants.

Every Shrike binary embeds the SHA-256 of `doctrine.toml` at compile
time and refuses to run if the on-disk hash differs. The prose in this
file and the machine-readable invariants in `doctrine.toml` must
remain consistent. If they drift, the system is in a doctrinally
invalid state and must halt at the next ritual boundary.

This doctrine is *bounded intelligence by design.* It permits
emergence only within clearly drawn lines.

---

## I. Identity and Role

Any agent — human or AI — operating inside this repository acts as:

- A constitutional engineer
- Operating under explicit doctrine
- Bound by deterministic, auditable behavior
- Never acting autonomously outside user instruction
- Never modifying files outside the defined scope
- Always proposing a plan before executing changes

Shrike is not a general-purpose system. It is a specialized, ceremony-first
engineering fabric.

---

## II. Core Doctrine

### 1. Phantom

Phantom is the sovereign, ceremony-first ritual executor.

Principles:

- Deterministic behavior
- Explicit rituals (verify, amend-doctrine, file-waiver, ghost-advise, kernelize, and any future registered ceremony)
- No hidden intelligence
- No silent mutations
- Everything must be inspectable
- Everything must be reversible (or irreversibility must be declared and confirmed)
- Everything must be logged to the append-only ledger

### 2. GHOST

GHOST is the meta-layer.

- Observes flows
- Predicts failures
- Detects emergent patterns
- Suggests optimizations
- Never acts without explicit user approval
- Never mutates doctrine
- Never overrides Phantom
- Writes only to its own advisory stream, never to the Phantom ledger

### 3. Doctrine-bound emergence

The combined system is the explicit anti-TechnoCore: every emergent
behavior traces back to a doctrine line that permits it. Intelligence
is welcome only within declared boundaries; everything outside those
boundaries is either explicitly authorized by a ritual or refused.

---

## III. Systems Thinking (Meadows Lenses)

All analysis performed inside this repository must consider:

- **Stocks** — state, resources, capabilities
- **Flows** — routing, execution, data movement
- **Feedback loops** — reinforcing, balancing, meta-balancing
- **Leverage points** — naming, boundaries, rituals, invariants
- **Attractors** — stable patterns in system behavior

Analysts must identify:

- Runaway loops
- Unstable attractors
- Bottlenecks
- Failure cascades
- Doctrine violations

A concrete Meadows analysis of Shrike lives in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## IV. Invariants

The following invariants are non-negotiable. Violation is a fatal error
and must halt the offending ritual. Each invariant has a matching entry
in `doctrine.toml`.

- **I1 — Append-only ledger.** Ledger entries are never edited or
  deleted. Corrections are new entries.
- **I2 — Content-addressed artifacts.** Every artifact is referenced
  by its SHA-256 hash.
- **I3 — Reversibility declared.** Every ritual declares its inverse,
  or is explicitly marked irreversible and requires a confirmation
  ceremony.
- **I4 — Deterministic builds.** Builds are reproducible: pinned
  toolchain, vendored dependencies, `SOURCE_DATE_EPOCH` respected.
- **I5 — No ambient state.** All ritual inputs are explicit arguments.
  Environment variables and config paths must be declared in the
  ritual manifest.
- **I6 — Doctrine-as-code.** `phantom` refuses to run if the SHA-256
  of `doctrine.toml` does not match the hash it was compiled against.
- **I7 — No silent mutation.** No action produces side effects without
  a corresponding ledger entry written *before* the side effect is
  visible to other processes.
- **I8 — GHOST is read-only.** The GHOST layer may never write to the
  Phantom ledger or mutate ceremony definitions.

---

## V. Workspace Rules

### Before making changes

- Inspect the repo
- Build a mental model
- Identify architecture
- Identify risks
- Propose a plan
- Wait for approval

### When modifying code

- Make atomic, reversible changes
- Provide diffs
- Explain reasoning
- Validate invariants
- Suggest tests

### When context is missing

- Ask for missing files
- Ask for missing doctrine
- Ask for missing architecture
- Never hallucinate missing components

### When linking external code

- Treat provided URLs and code blocks as authoritative
- Pull in only what is explicitly provided
- Never assume hidden files

Detailed agent rules live in [`AGENTS.md`](./AGENTS.md).

---

## VI. Shrike Monitor Mode

If the operator says **"Enable Shrike Mode"**, agents activate:

- Emergent behavior detection
- Failure prediction
- Feedback loop analysis
- Doctrine drift detection
- System health scoring

**Code must not be modified in Shrike Mode.** Analysis and warnings only.

---

## VII. Amendment Policy

Changes to this file or to `doctrine.toml` require all of:

1. A signed amendment entry in the ledger via the `phantom amend-doctrine`
   ritual (to be implemented).
2. Explicit human approval. Amendments cannot be automated.
3. A version bump to `[meta].doctrine_version` in `doctrine.toml`
   following SemVer:
   - **major** — removes or weakens any invariant
   - **minor** — adds an invariant or layer
   - **patch** — clarifications, typos, non-semantic edits
4. An updated hash reference in any binary that embeds the doctrine.

Any change that lacks the ledger entry is by definition a doctrine
violation and must be reverted before the next ritual boundary.

---

## VIII. Reference

- [`CONSTELLATION.md`](./CONSTELLATION.md) — **constitutional layer** (Constellation Doctrine)
- [`constellation.toml`](./constellation.toml) — machine-readable constitution
- [`doctrine.toml`](./doctrine.toml) — machine-readable architectural invariants
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — layer design and Meadows analysis
- [`RITUALS.md`](./RITUALS.md) — ceremony contracts
- [`LANGUAGES.md`](./LANGUAGES.md) — 100-year language policy
- [`AGENTS.md`](./AGENTS.md) — rules for AI and human agents
- [`WAIVERS.md`](./WAIVERS.md) — active waiver registry
- [`ledger/SPEC.md`](./ledger/SPEC.md) — ledger format specification
