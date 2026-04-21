# ddf-core (Python)

The Python wrapper for the DDFramework kernel.

Binds to engine v0.7.0. Re-exports from `ghost-observer` and provides
the stable Python API surface that Application-Era applications
depend on.

## Install

During Engine-Era development the package is consumed in-tree. A wheel
build (`pip install .`) works from this directory. Runtime dependency
set: **none** (stdlib-only; `ghost-observer` is located at import time
via relative path).

## Usage

```python
import ddf

print(ddf.__version__)          # "0.1.0"  (kernel API version)
print(ddf.ENGINE_VERSION)       # "0.7.0"  (engine doctrine_version)

# Re-exported from ghost:
result = ddf.verify()                  # summary of the main ledger
advisories, run_id, head = ddf.advise()  # run the advisor

# Namespaced re-exports:
for entry in ddf.ledger.iter_entries(pathlib.Path("ledger/events.jsonl")):
    ...
```

## Relationship to ghost-observer

`ghost-observer` is legacy-named and stays frozen. `ddf` (this
package) is the stable name; it is thin and does not duplicate logic.

## CLI

```sh
python -m ddf                 # forwards to `python -m ghost`
python -m ddf advise          # forwards to `python -m ghost advise`
```
