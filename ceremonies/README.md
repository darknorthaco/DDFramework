# Ceremony Manifests

Each TOML file in this directory declares a single ritual per the
contract template in [`../RITUALS.md`](../RITUALS.md) §0.

## Registration

A ritual is registered (and therefore executable by `phantom`) when
**all** of:

1. A manifest file `NNNN-<name>.toml` exists here.
2. The name is listed in [`../doctrine.toml`](../doctrine.toml)
   `[rituals].registered`.
3. `ddf-exec-core` has an implementation for the subcommand.

A manifest without implementation is a *declaration* — the contract
exists; the executor does not yet.

## Naming

- File name format: `NNNN-<kebab-name>.toml` (zero-padded 4-digit id).
- Id is monotonically increasing and never reused.
- Name uses lowercase-kebab (`lan-scan`, not `lan_scan`).

## Fields

Every manifest declares:

- `id`, `name`, `status` (`declared` | `implemented`)
- `purpose`, `inputs`, `outputs`, `side_effects`
- `invariants_upheld`, `inverse`, `ledger_event_kind`
- `failure_modes` (optional until status=implemented)

## Amendment

Adding, removing, or materially changing a manifest is a **Tier 1**
change and requires a full Constellation Loop with a ledger entry.
