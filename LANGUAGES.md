# DDFramework — Language Policy (100-Year Horizon)

The DDFramework engine (historically labeled *Shrike*; label frozen
per the v0.6.0 scope redefinition) is designed to be buildable and
runnable a century from ratification. This document records the
language palette, the rationale, and the discipline required to make
the 100-year target plausible. For engine identity and scope see
[`DDFRAMEWORK.md`](./DDFRAMEWORK.md).

## 1. The Palette

| Language | Tier | Role |
|---|---|---|
| **C (ISO C11)** | core | FFI boundary, raw syscalls, minimal primitives |
| **Rust (stable)** | core | `phantom-core` and any future concurrent or networked binary |
| **Python 3 (stdlib-heavy)** | meta | `ghost-observer`, tooling, scripts |
| **Zig** | reserved | future C++-successor slot when Zig reaches 1.0 |
| **Ada / SPARK** | reserved | future safety-critical components only |
| **Carbon** | excluded | pre-1.0, single-vendor, experimental |

## 2. The 100-Year Test

A language passes the test if, to a reasonable probability, a source
tree written in it today can still be built and run in 2126.

Failure modes to avoid:

- **Runtime churn** — the Python 2 → 3 migration is the canonical
  warning. Minimize runtime dependency.
- **Single-vendor languages without standardization** — fate of the
  language is tied to the fate of one company.
- **Pre-1.0 languages** — no stability guarantee.
- **Languages whose standard library includes the universe** —
  bitrot surface is the size of the stdlib.

## 3. Rationale by Language

### 3.1 C (ISO C11)

C code from the 1970s still compiles. The ISO standard is publicly
documented and reproducible. `c-primitives/` exists for three purposes:

- Raw syscalls where Rust's stdlib is insufficient
- A stable ABI that anything else can link against for 100 years
- Minimal tools whose complexity does not justify a full Rust crate

Discipline:

- Target **ISO C11** only. No GNU extensions unless guarded by
  `#if defined(__GNUC__)` and provably non-load-bearing.
- Warnings-as-errors with `-Wall -Wextra -Wpedantic`.
- No third-party libraries in `c-primitives/`. Any vendoring must be
  documented here.

### 3.2 Rust (stable)

Rust is the principal language of `phantom-core`. Memory safety and
the type system make it the best available choice for a deterministic
ritual executor.

Risk: Rust is younger than C and not ISO-standardized. Mitigations:

- **Stable channel only.** No nightly. No `#![feature(...)]`.
- **Edition pinned** in `Cargo.toml`.
- **Toolchain pinned** in `rust-toolchain.toml` to a specific
  `stable-YYYY-MM-DD`.
- **Dependencies vendored** (`cargo vendor`) and committed.
- **Minimal dependency surface.** Every crate added must be justified
  in this file.
- **No build scripts that fetch from the network.** All sources must
  be present at commit time.
- **Reproducible builds** target: two clean checkouts on two
  machines produce byte-identical binaries given a pinned
  `SOURCE_DATE_EPOCH`.

Approved dependencies:

- *(none — v0.3.0 ships with zero third-party Rust crates.
  SHA-256, canonical JSON, RFC 3339 timestamps, and the ledger
  reader/writer are all hand-rolled under ~500 LOC in
  `phantom-core/src/`.)*

### 3.3 Python 3 (stdlib-heavy)

Python lives at the meta layer only. `ghost-observer` is read-only by
design — if in 30 years a Python runtime is inconvenient, we can
reimplement it in Rust against the ledger spec with no data loss.

Discipline:

- Target the earliest still-supported Python 3.x minor at
  implementation time; declare it in the package metadata.
- Prefer `stdlib` over third-party packages. Each third-party
  dependency requires a justification entry here.
- No ambient config. Read the doctrine-declared paths only.
- GHOST must never import anything from `phantom-core`; it
  communicates only via the ledger file (I8).

Approved third-party dependencies:

- *(none — `ghost-observer` v0.3.0 is stdlib-only. Test framework is
  `unittest` from stdlib, not pytest.)*

### 3.4 Zig (reserved)

Zig is the most promising C / C++ successor in the systems space:
deterministic builds, excellent C interop, no hidden allocations. It
is **not yet 1.0**. Including it in a 100-year fabric today is
premature.

Reservation: when Zig reaches 1.0 with a stability guarantee, a future
amendment may promote it to `core` for the `c-primitives/` layer or
for an additional native binary. Until then, Zig code is not written
in this repository.

### 3.5 Ada / SPARK (reserved)

Ada has 40+ years of proven longevity in aerospace and defense. SPARK
provides formal verification. If Shrike ever grows a safety-critical
component (medical, aerospace, industrial control), Ada/SPARK is the
expected language. Not used in the bootstrap.

### 3.6 Carbon (excluded)

Carbon is Google's experimental C++ successor. As of this doctrine
(v0.1.0) Carbon:

- Is pre-1.0
- Has no ISO standard
- Has a single-vendor governance model
- Explicitly does *not* guarantee stability

Including it in a 100-year fabric is the inverse of the doctrine.
**Excluded.** A future amendment may revisit this if Carbon reaches
1.0 with a multi-stakeholder standardization track.

## 4. Formats, Not Just Languages

100-year survivability depends as much on file formats as on source
languages:

- **Source control:** git (20 years old, ubiquitous, object format is
  plain)
- **Docs:** Markdown (plain text, GFM is widely documented)
- **Config:** TOML (ISO-equivalent via RFC-equivalent spec, stable)
- **Ledger:** NDJSON (plain text, line-oriented, recoverable with
  `grep`, `awk`, any future text editor)
- **Binary artifacts:** stored as content-addressed blobs, format
  declared per-artifact in its manifest

Avoided:

- Proprietary binary formats
- Serialization frameworks that require their own runtime to read
  (e.g. raw protobuf blobs without `.proto` files committed alongside)
- YAML (too many dialects, too much spec surface)

## 5. Discipline Checklist (per binary)

- [ ] Toolchain pinned in-repo
- [ ] Dependencies vendored in-repo
- [ ] Reproducible build documented
- [ ] No network access during build
- [ ] No runtime reflection / dynamic code loading
- [ ] No ambient state reads (I5)
- [ ] Every dependency addition recorded in this file

## 6. Amendment

Changes to the palette follow the doctrine amendment policy
(DOCTRINE.md §VII). Adding a language is a minor bump. Removing a
language is a major bump. Adding a third-party dependency is not a
doctrine amendment but must be recorded in this file with
justification.
