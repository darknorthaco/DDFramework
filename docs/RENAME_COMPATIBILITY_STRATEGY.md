# Rename compatibility strategy (Phase 3)

Companion to [`RENAME_IMPACT_ANALYSIS.md`](./RENAME_IMPACT_ANALYSIS.md).

---

## POAM closure (mechanical naming and navigability)

**Status: CLOSED** for in-repository execution as of this revision.

**Delivered:** Phases 1–2 (glossary, kernel API map, operator vs implementor
reading paths, AGENTS naming guideline, Rust `doc(alias)` / Python docstring
clarity); Phase 3 through **Wave 1** (rename impact and strategy docs, Makefile
mechanical aliases, default `PYTHON=python3`); layer visuals
([`VISUAL_LAYERS.md`](./VISUAL_LAYERS.md) and `images/ddf-layers-stack.svg`).

**Deferred (event-driven):** Phase 3 **Wave 2** (install or packaging shims,
friendlier binary names on disk) when installers or operator training demand
it; **Wave 3** (crate or `python -m` module renames) only with a **major**
kernel or engine release, a written migration guide, and explicit
go-ahead — see Wave 2 and Wave 3 sections below.

**Not in scope without amendment:** Renaming **normative** mission vocabulary
inside `DOCTRINE.md`, `doctrine.toml`, or `CONSTELLATION.md` is **Phase 4** and
requires the **`amend-doctrine`** ritual (and constitutional process where
applicable), not a normal documentation-only pull request.

**Next recommended cycles:** **Phase 6 simulation** under `ddf-core/simulation/`
(Constellation mandate to simulate before scarring reality); **Application Era**
software that **consumes** this engine per [`DDFRAMEWORK.md`](../DDFRAMEWORK.md),
unless packaging or embedders force Wave 2 or Wave 3.

---

## Principles

1. **Protocol before polish** — ledger lines, `event` kinds, ceremony ids, and
   advisory hashes outrank ergonomic renames.
2. **Additive first** — new names appear **alongside** old names until embedders
   migrate.
3. **One wave, one revert** — each release wave must be reversible with
   `git revert` without rewriting ledger history.

---

## Wave 1 (repository-local, low risk)

**Done in engine repo:**

- Mechanical **Makefile** targets that alias existing behavior (`make advise`,
  `make ledger-summary`, …).
- **`PYTHON` default** prefers `python3` when `python` is absent (POSIX dev
  boxes). Override: `make test PYTHON=python`.

**Exit criteria:** `make help` lists both mission-style and mechanical targets;
`make test` passes with `python3` on PATH.

---

## Wave 2 (optional — install / distribution)

If product needs a friendlier **binary name** on disk:

- Ship **`phantom`** unchanged; add **`ritual-executor`** (or agreed name) as
  **copy or hard link** in packaging scripts **outside** this repo, **or**
- Document a shell alias in operator runbooks — zero engine code change.

**Deprecation:** if a true rename happens, keep `phantom` as a **stub** that
prints deprecation + `exec`s the new binary for **at least one major engine
version**.

---

## Wave 3 (crate / Python module rename)

**Preconditions:**

- Written migration guide for downstream `Cargo.toml` / imports.
- **Kernel API major bump** if `ddf` public paths change.
- Full test gate + advisory/ledger replay smoke on sample archives.

**Rollback:** maintain a branch or tag of last pre-rename release; do not rewrite
git history of `ledger/events.jsonl`.

---

## Environment variable policy

| Today | Future (if renamed) |
|-------|---------------------|
| `DDF_PHANTOM_BIN` | Accept `DDF_RITUAL_EXECUTOR_BIN` as alias **before** removing old name |

Implement alias support only when Wave 2+ is approved; do not add dead env vars
prematurely.

---

## Communication

- **Release notes:** every rename lists old → new command, env var, and sunset
  date.
- **Glossary:** keep [`../GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md)
  updated so operators see one mapping table.
