# Engine checkout

The Constitutional Agent Shell depends on **DDFramework** at commit **b02ac4d** (or compatible **v0.7.0** kernel).

## Layout

Recommended when this repository is standalone (e.g. `github.com/darknorthaco/AO`):

```text
AO/
  engines/
    DDFramework/    # git clone of DDFramework; pin to b02ac4d or tag v0.7.x
  crates/ca-shell/
```

Then set `engine_root` in `config/shell.toml` to `engines/DDFramework` (relative path is fine).

## Path dependency

`crates/ca-shell/Cargo.toml` defaults to the kernel crate **inside the same repository tree** as the `AO/` folder:

```toml
ddf = { path = "../../../ddf-core/ddf" }
```

That resolves when `AO/` is a subdirectory of the DDFramework workspace (this layout).

When **AO** is its own git repository, clone the engine under `engines/DDFramework` and change the dependency to:

```toml
ddf = { path = "../../engines/DDFramework/ddf-core/ddf" }
```

## Binaries

Build the engine per DDFramework `README.md` so `ddf-exec` is on `PATH` or set `DDF_EXEC_BIN`. For advisories, ensure `python` can import `ghost-observer` from the engine tree (the shell’s `engine-advise` command sets `PYTHONPATH` to `engine_root/ghost-observer`).
