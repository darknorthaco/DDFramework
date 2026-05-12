# Rename impact analysis (Phase 3 inventory)

**Status:** living inventory for a **future** binary/crate rename program.  
**Policy:** ledger `event` strings, ceremony numeric ids, and committed ledger
lines are **protocol** — not renamed without a versioned migration and
constellation review.

For vocabulary without renames, see [`../GLOSSARY_ENGINE_NAMES.md`](../GLOSSARY_ENGINE_NAMES.md).

---

## 1. Binaries (user-facing CLI)

| Current name | Role | Blast radius if renamed |
|----------------|------|-------------------------|
| `phantom` | Ritual executor (verify, amend-doctrine, …) | `Makefile`, `ddf` crate (`phantom_bin_path`, `DDF_PHANTOM_BIN`), docs, operator muscle memory, CI if any invokes `phantom` |
| `ddf` | Kernel CLI dispatcher | `Makefile`, embedders invoking `ddf`, `ddf-core` tests |
| *(none at workspace root)* | Python advisor entrypoint is **`python -m ghost`** | Module name `ghost` inside `ghost-observer/` |

**Recommendation:** keep **`phantom`** and **`ddf`** until a deliberate release
labels a deprecation window. Optional **symlink or copy** install (e.g.
`ritual-executor` → `phantom`) is OS-specific; document in strategy doc instead
of repo-shipping symlinks unless packaging owns it.

---

## 2. Rust crates and lib names

| Current | Role | Blast radius |
|---------|------|--------------|
| Package `phantom-core`, lib `phantom_core` | Ledger + canonical + executor library | Workspace `Cargo.toml`, `ddf` path dep, all `use phantom_core`, tests |
| Package `ddf`, lib `ddf` | Kernel API | Downstream `ddf = …` in future apps |

**Recommendation:** crate renames are **Wave 3** only; require **major** kernel
API bump if `ddf` re-exports paths change. Prefer **leaving crate names** and
using glossary + `doc(alias)` (already done) for discoverability.

---

## 3. Python packages and module names

| Current | Role | Blast radius |
|---------|------|--------------|
| Directory `ghost-observer/`, package `ghost` | Advisor + ledger reader | `PYTHONPATH`, `python -m ghost`, `ddf` subprocess, `ddf_py` imports, tests that walk `ghost/` |

**Recommendation:** renaming `ghost` → `advisor` (or similar) is **high**
churn (import paths, `-m` module, test scanners). Defer unless bundled with a
packaging/version major.

---

## 4. Protocol and on-disk identifiers (do not rename casually)

| Artifact | Examples | Rule |
|----------|----------|------|
| Ledger `event` field | `verify.result`, `doctrine_amendment`, … | **Immutable** for existing lines; new kinds append only |
| Ceremony ids | `0001`, `0006`, … | Frozen in manifests and `RITUALS.md` |
| Advisory stream schema | per `advisories/SPEC.md` | Same as ledger: extend, do not rewrite history |
| Env vars | `DDF_PHANTOM_BIN`, `DDF_PYTHON` | Add **new** names in parallel before deprecating old (if ever) |

---

## 5. Documentation and marketing strings

| Area | Impact |
|------|--------|
| `README.md`, `DDFRAMEWORK.md`, `DOCTRINE.md`, `CONSTELLATION.md` | Search/replace risks doctrine drift; prose changes follow amendment where normative |
| `AGENTS.md`, `GLOSSARY_*`, `KERNEL_API_MAP.md` | Safe to evolve under Tier 3 / doc policy |

---

## 6. External consumers (unknown)

Downstream repos may invoke:

- `cargo install` / path to `phantom` / `ddf`
- `python -m ghost`

Any binary rename requires **release notes + deprecation period** (see
compatibility strategy).

---

## 7. Go / no-go summary

| Wave | Content | Go? |
|------|---------|-----|
| Wave 1 | Docs + Makefile **aliases** + `PYTHON` default | **Yes** (this repo) |
| Wave 2 | Install shims / duplicate binaries | Packaging decision |
| Wave 3 | Crate or `-m` module rename | **Major** migration; separate approval |
