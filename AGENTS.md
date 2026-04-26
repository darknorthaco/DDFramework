# DDFramework — Rules for Agents

This file governs the behavior of any agent — human or AI — operating
inside this repository. It is the operational counterpart to the
doctrine stack: [`DDFRAMEWORK.md`](./DDFRAMEWORK.md) (engine identity),
[`CONSTELLATION.md`](./CONSTELLATION.md) (constitution) and
[`DOCTRINE.md`](./DOCTRINE.md) (architecture).

> **Scope reminder (ratified at v0.6.0):** this repository is the
> **DDFramework engine**. Applications — including the future Shrike
> Monitor — are out of scope until Phase 5+. Do not add application
> logic, application-specific rituals, or new "Shrike" branding to
> engine code.

If you are an AI coding assistant reading this because you were
dropped into the DDFramework workspace, **read `DDFRAMEWORK.md` first,
this file second, `CONSTELLATION.md` third, `DOCTRINE.md` fourth, and
propose a plan before any edit.**

## 1. Absolute Rules

1. **Read the doctrine before acting.** Any action taken without
   reading `DOCTRINE.md` and `doctrine.toml` is a doctrine violation.
2. **Propose a plan. Wait for approval.** No edits to tracked files
   until the operator approves the plan. "The floor is yours" is a
   grant of scope, not a bypass of the plan-then-approve loop.
3. **No silent mutations.** If you change something, say what and why,
   in the session and in the commit message.
4. **No hallucinated components.** If a file, library, or doctrine
   section is missing, ask. Do not invent it.
5. **Atomic, reversible changes.** One concept per commit. Every
   commit must be revertable with `git revert` without corrupting
   state.
6. **Never modify doctrine outside an amendment ceremony.**
   `DOCTRINE.md` and `doctrine.toml` are only edited via the
   `amend-doctrine` ritual.
7. **Never bypass invariants.** If an invariant is in your way, stop
   and raise it. Do not work around it.
8. **Never auto-install dependencies.** New dependencies require an
   entry in `LANGUAGES.md` with justification.

## 2. Session Protocol

Every session with an AI agent follows this shape:

1. **Acknowledge doctrine.** State that you have read
   `CONSTELLATION.md`, `DOCTRINE.md`, `doctrine.toml`, and
   `constellation.toml`. Name the current `constitution_version`
   and architectural `doctrine_version`.
2. **Restate the operator's goal** in your own words.
3. **Classify the change tier** (see §3 below). Declare it.
4. **Inspect** only as much of the repo as is needed to build a
   mental model.
5. **Run the Constellation Loop** at the required depth (full /
   abbreviated / lightweight) per tier.
6. **Identify risks** explicitly.
7. **Propose a plan**, phased if large. Declare what files will
   change, what invariants are load-bearing, and what tests will
   cover it.
8. **Wait for approval.**
9. **Execute the approved plan** atomically.
10. **Write ledger entry** with the canonical-form hash.
11. **Report** diffs, reasoning, invariant validation, ledger entry
    hash, and suggested tests. Propose the next step.

## 3. Change Tiers (Constellation §12)

Every change must be classified. Every session must declare the tier
before acting.

### Tier 1 — Core System Changes (Full Constellation Loop)

Architecture, protocols, ledger format, security boundaries, scaling
policies, doctrine amendments, new ritual registrations.

Required steps: all 9 of the Constellation Loop
([`CONSTELLATION.md`](./CONSTELLATION.md) §10).

### Tier 2 — Significant Feature Work (Abbreviated Loop)

Adding a non-foundational feature, refactoring an existing ritual,
introducing a new dependency.

Required steps: system map, domain classification, integrity check,
regenerative check.

### Tier 3 — Minor Changes (Lightweight Check)

Typo fixes, doc polish, comment improvements, non-behavioral
reformatting.

Required steps: domain classification, integrity check.

**Invariant.** No change is exempt from doctrine — only the scope
varies. Skipping a required step at any tier requires a formal
waiver per [`WAIVERS.md`](./WAIVERS.md).

## 3. Commit Discipline

- One concept per commit.
- Commit message format:
  ```
  <component>: <imperative summary>

  <body: why, not just what>
  <body: invariants touched>
  <body: reversibility note>
  ```
- Components: `doctrine`, `architecture`, `phantom-core`,
  `hyperion-net`, `ghost-observer`, `ceremonies`, `ledger`, `tooling`,
  `foundation`.
- Never force-push a shared branch.
- Never amend a pushed commit.
- Never commit secrets, credentials, or `.env` files.

## 4. Editing Guardrails

### 4.0 Naming — mission vs mechanism (kernel and new code)

- **Mission names** (Phantom, GHOST, Hyperion, Constellation) stay in
  constitution, operator docs, and frozen protocol identifiers unless
  changed by an explicit governance / kernel migration.
- **New** Rust/Python public API and **new** modules should prefer
  **mechanical** vocabulary in identifiers and primary docstrings:
  *ritual*, *ledger*, *advisor*, *append-only*, *verify*, *transport*.
- The canonical decoder ring is [`GLOSSARY_ENGINE_NAMES.md`](./GLOSSARY_ENGINE_NAMES.md);
  the kernel symbol table is [`ddf-core/KERNEL_API_MAP.md`](./ddf-core/KERNEL_API_MAP.md).
- When adding or renaming **kernel API symbols**, **rituals**, **ledger event
  kinds**, or **`DDF_*` env vars**, update the glossary and kernel map in the
  same change (see **Maintaining this glossary** in `GLOSSARY_ENGINE_NAMES.md`).

When modifying code:

- Use exact, minimal diffs.
- Preserve indentation style of the surrounding file.
- Do not reformat files you did not come to edit.
- Do not add narration comments (`// increment counter`). Comments
  explain non-obvious intent only.
- Do not introduce runtime reflection.
- Do not introduce network calls during build.

When creating files:

- Prefer editing existing files over creating new ones.
- New markdown files must be linked from `README.md` or another
  already-linked doc.
- New code files must belong to an existing crate/package, or
  creating the crate/package itself must be part of the approved
  plan.

## 5. Shrike Mode

If the operator says **"Enable Shrike Mode"** (or equivalent), switch
to analysis-only behavior:

- No file writes.
- No commits.
- Output observations, warnings, system-health scoring.
- Doctrine-drift detection is required in every Shrike-Mode report.

Exit Shrike Mode only on explicit operator instruction.

## 6. When You Are Stuck

- Stop.
- Describe what you observed, what you tried, and why you believe
  you are blocked.
- Propose two or more options with trade-offs, or request specific
  missing information.
- Do not thrash. Do not retry the same failing action with cosmetic
  changes.

## 7. When the Operator and the Doctrine Conflict

The doctrine outranks casual operator preference. If the operator
asks for something that violates an invariant:

1. Name the invariant.
2. Quote the offending instruction back.
3. Offer a compliant alternative, or propose an amendment ceremony
   if the operator genuinely intends to change the doctrine.

Explicit amendment ceremonies always win; casual overrides never do.
