# hyperion-net / c-primitives

Phase 2 status: **shape-only**. No code is compiled or linked from
Rust yet. These files reserve the FFI surface for later phases.

## Why this layer exists (100-year rationale)

From `LANGUAGES.md` §3.1: C is the longest-lived binary contract we
have access to. Hyperion's lowest-level socket/syscall primitives
live here so that:

1. If the Rust crate above evolves or is rewritten, the C ABI stays
   stable.
2. If in 80 years Rust is supplanted, any future language with a C
   FFI can still consume these primitives.
3. The surface is small (two functions in Phase 2), audited, and
   written in ISO C11 with no GNU extensions.

## Files

- `sockets.h` — FFI declarations. Reviewable design intent.
- `sockets.c` — stubs that return `SHRIKE_SOCK_ERR_UNSUPPORTED`.

## Build (when needed)

This host did not have `cc` or `gcc` available during Phase 2. That
is fine because nothing links this code yet. When a future phase
needs it, build with:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -c sockets.c -o sockets.o
```

Or add a `build.rs` in `hyperion-net/` that uses `std::process::Command`
to invoke the system C compiler (no build-dep crate). Per LANGUAGES.md
we avoid build-script crate dependencies.

## Phase gate to activation

Activation (writing real socket code) is a **Tier 1** change. It will
require a full Constellation Loop, an amendment adding a
`[palette].c_compiler_required = true` entry to doctrine.toml, and a
ledger entry recording the decision.
