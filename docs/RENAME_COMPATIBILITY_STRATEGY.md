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

## Wave 2 — binary rename (EXECUTED at v1.0.0)

**Outcome:** the `phantom` binary was renamed to **`ddf-exec`** in a single
major release (no deprecation stub). The single in-repo consumer (AO) was
updated in the same commit chain. The cost of a deprecation window outweighed
the benefit given the known consumer set.

---

## Wave 3 — crate / lib rename (EXECUTED at v1.0.0)

**Outcome:** the `phantom-core` crate was renamed to **`ddf-exec-core`** with
lib name `ddf_exec_core`. Kernel API bumped to 1.0.0 in the same amendment
ceremony. Downstream `use phantom_core` paths were rewritten across the
workspace; the same commit updated AO's references.

**Rollback path retained:** the pre-rename state lives at the commit immediately
before the v1.0.0 amendment; `ledger/events.jsonl` history is frozen per I1 so
the old names remain readable in committed entries.

---

## Environment variable policy (EXECUTED at v1.0.0)

| Old | New |
|-------|---------------------|
| `DDF_PHANTOM_BIN` | **`DDF_EXEC_BIN`** (no alias; hard cut at v1.0.0) |

The `DDF_PYTHON` and `PYTHONPATH` env vars are unchanged.

---

## Communication

- **Release notes:** every rename lists old → new command, env var, and sunset
  date.
- **Glossary:** keep [`../GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md)
  updated so operators see one mapping table.
