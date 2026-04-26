# ao-shell (Python)

Thin **stdlib-only** wrapper around the `ca-shell` binary. The shell’s privileged path and ledger writes remain in Rust; Python is for operator automation and CI glue.

Install in editable mode from this directory:

```bash
pip install -e .
```

Then:

```bash
ao-shell --help
```

For ledger verification from Python, use the engine’s **`ddf`** package (`ddf-core/ddf_py`) from the same DDFramework checkout as in `config/shell.toml`.
