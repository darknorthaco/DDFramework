"""Ritual dry-run — Phase 6 simulation module.

Validate a ritual invocation **without** running the executor and
**without** writing to the ledger. Returns a structured report
describing what would happen if the ritual were invoked with the
provided arguments against the given ceremony directory and doctrine.

Stdlib-only; pure function; read-only on all ledger / advisory
streams (it does not read them at all). Honors invariant I5 (no
ambient state): the ceremony directory and the doctrine path are
explicit arguments passed by the caller.

The dry-run answers these questions, statically, from the manifests:

- Is this ritual registered in ``doctrine.toml`` ``[rituals].registered``?
- Does a ceremony manifest exist for it under ``ceremony_dir``?
- Is the manifest's ``status`` ``implemented`` (executor exists) or
  ``declared`` (contract only)?
- Are the provided ``args`` consistent with the manifest's ``[inputs]``
  (no missing required, no unknown extras)?
- What event kind, side effects, invariants, and inverse does the
  ritual declare?

It does **not** invoke ``phantom`` and **does not** simulate ritual
side effects beyond surfacing the manifest contract.
"""

from __future__ import annotations

import pathlib
import re
import tomllib
from typing import Any


_ID_RE = re.compile(r"^(\d{1,4})$")
_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_MANIFEST_NAME_RE = re.compile(r"^(\d{4})-([a-z][a-z0-9-]*)\.toml$")
_INVARIANT_ID_RE = re.compile(r"^I\d+$")


def _canonical_id(ritual_id: str) -> str | None:
    """Accept ``'0001'`` / ``'1'`` (numeric forms only).

    Returns the 4-digit canonical form, or ``None`` if the input isn't a
    numeric id. Names are resolved separately against the manifest scan.
    """
    if not isinstance(ritual_id, str):
        return None
    s = ritual_id.strip()
    m = _ID_RE.match(s)
    if not m:
        return None
    n = int(m.group(1))
    if n <= 0 or n > 9999:
        return None
    return f"{n:04d}"


def _scan_manifests(ceremony_dir: pathlib.Path) -> dict[str, dict[str, Any]]:
    """Return a map of canonical 4-digit id -> parsed manifest table.

    Files that do not match ``NNNN-<name>.toml`` are ignored (e.g.
    ``README.md``). Files that fail TOML parsing are surfaced via a
    sentinel entry with key ``__parse_errors__``.
    """
    out: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    if not ceremony_dir.is_dir():
        return out
    for entry in sorted(ceremony_dir.iterdir()):
        if not entry.is_file():
            continue
        m = _MANIFEST_NAME_RE.match(entry.name)
        if not m:
            continue
        try:
            data = tomllib.loads(entry.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError) as exc:
            errors.append(f"{entry.name}: {exc}")
            continue
        data["__source_filename__"] = entry.name
        out[m.group(1)] = data
    if errors:
        out["__parse_errors__"] = {"errors": errors}
    return out


def _id_from_name(manifests: dict[str, dict[str, Any]], name: str) -> str | None:
    for ritual_id, data in manifests.items():
        if ritual_id == "__parse_errors__":
            continue
        if data.get("name") == name:
            return ritual_id
    return None


def _registered_rituals(doctrine: dict[str, Any]) -> list[str]:
    rituals = doctrine.get("rituals") or {}
    reg = rituals.get("registered") or []
    return [r for r in reg if isinstance(r, str)] if isinstance(reg, list) else []


def _input_spec(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inputs = manifest.get("inputs") or {}
    return inputs if isinstance(inputs, dict) else {}


def run(
    ritual_id: str,
    args: dict[str, Any] | None,
    ceremony_dir: pathlib.Path,
    doctrine_path: pathlib.Path,
) -> dict[str, Any]:
    """Dry-run a ritual: return a structured static-validation report.

    Parameters
    ----------
    ritual_id:
        Canonical 4-digit id (``"0001"``), unpadded numeric (``"1"``),
        or ritual name (``"verify"``).
    args:
        Caller-supplied arguments mapped by flag short name (the key
        of each entry under ``[inputs]`` in the manifest). ``None`` is
        treated as the empty dict.
    ceremony_dir:
        Directory containing ``NNNN-<name>.toml`` manifests.
    doctrine_path:
        Path to ``doctrine.toml`` whose ``[rituals].registered`` list
        gates which rituals are considered active.

    Returns
    -------
    dict
        See module docstring; stable keys with sorted list values and
        a deterministic ``ordered_summary``.
    """
    provided = dict(args or {})
    errors: list[str] = []

    manifests = _scan_manifests(pathlib.Path(ceremony_dir))
    parse_errors = manifests.pop("__parse_errors__", None)
    if parse_errors:
        for e in parse_errors["errors"]:
            errors.append(f"manifest_parse_error:{e}")

    try:
        doctrine = tomllib.loads(pathlib.Path(doctrine_path).read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        doctrine = {}
        errors.append(f"doctrine_parse_error:{exc}")

    canonical = _canonical_id(ritual_id)
    if canonical is None and isinstance(ritual_id, str) and _NAME_RE.match(ritual_id.strip()):
        canonical = _id_from_name(manifests, ritual_id.strip())
    if canonical is None:
        errors.append(f"unresolved_ritual:{ritual_id!r}")
        return _empty_report(ritual_id, errors)

    manifest = manifests.get(canonical)
    manifest_found = manifest is not None
    if not manifest_found:
        errors.append(f"manifest_missing:{canonical}")

    ritual_name = (manifest or {}).get("name") or ""
    ritual_status = (manifest or {}).get("status") or "unknown"

    registered_list = _registered_rituals(doctrine)
    registered = bool(ritual_name) and ritual_name in registered_list
    if ritual_name and not registered:
        errors.append(f"not_registered:{ritual_name}")

    inputs = _input_spec(manifest or {})
    required = sorted(
        name for name, spec in inputs.items()
        if isinstance(spec, dict) and spec.get("required") is True
    )
    optional = sorted(
        name for name, spec in inputs.items()
        if isinstance(spec, dict) and spec.get("required") is not True
    )
    provided_keys = sorted(provided.keys())
    missing_required = sorted(set(required) - set(provided_keys))
    unknown_args = sorted(set(provided_keys) - set(inputs.keys()))
    for name in missing_required:
        errors.append(f"missing_required_arg:{name}")
    for name in unknown_args:
        errors.append(f"unknown_arg:{name}")

    outputs = (manifest or {}).get("outputs") or {}
    would_be_event_kind = outputs.get("ledger_event_kind") if isinstance(outputs, dict) else None

    side_effects = (manifest or {}).get("side_effects") or {}
    reads = sorted(side_effects.get("reads") or []) if isinstance(side_effects, dict) else []
    writes = sorted(side_effects.get("writes") or []) if isinstance(side_effects, dict) else []
    network = bool(side_effects.get("network")) if isinstance(side_effects, dict) else False

    # Real engine manifests place ``inverse`` and ``irreversibility_confirmation``
    # *after* a blank line below ``[invariants_upheld]``. Per TOML grammar that
    # nests them inside that table rather than promoting them back to top level.
    # Accept both layouts and filter the invariant set to keys that look like
    # invariant ids (``I1``, ``I2``, ...).
    invariants_block = (manifest or {}).get("invariants_upheld") or {}
    if not isinstance(invariants_block, dict):
        invariants_block = {}
    declared_invariants = sorted(
        k for k in invariants_block.keys() if isinstance(k, str) and _INVARIANT_ID_RE.match(k)
    )

    inverse = (manifest or {}).get("inverse")
    if not isinstance(inverse, str):
        inverse = invariants_block.get("inverse") if isinstance(invariants_block.get("inverse"), str) else None
    irreversibility_confirmation = (manifest or {}).get("irreversibility_confirmation")
    if not isinstance(irreversibility_confirmation, str):
        nested = invariants_block.get("irreversibility_confirmation")
        irreversibility_confirmation = nested if isinstance(nested, str) else None

    ok = (
        manifest_found
        and registered
        and ritual_status == "implemented"
        and not missing_required
        and not unknown_args
        and parse_errors is None
    )

    summary: list[str] = []
    summary.append(f"ritual:{canonical}:{ritual_name or '?'}")
    summary.append(f"status:{ritual_status}")
    summary.append(f"registered:{str(registered).lower()}")
    if would_be_event_kind:
        summary.append(f"would_be_event_kind:{would_be_event_kind}")
    if missing_required:
        for n in missing_required:
            summary.append(f"missing_required_arg:{n}")
    if unknown_args:
        for n in unknown_args:
            summary.append(f"unknown_arg:{n}")
    if reads:
        summary.append(f"reads_count:{len(reads)}")
    if writes:
        summary.append(f"writes_count:{len(writes)}")
    summary.append(f"network:{str(network).lower()}")
    summary.append(f"ok:{str(ok).lower()}")
    summary.sort()

    return {
        "ritual_id": canonical,
        "ritual_name": ritual_name,
        "ritual_status": ritual_status,
        "registered": registered,
        "manifest_found": manifest_found,
        "would_be_event_kind": would_be_event_kind,
        "inverse": inverse if isinstance(inverse, str) else None,
        "irreversibility_confirmation": (
            irreversibility_confirmation if isinstance(irreversibility_confirmation, str) else None
        ),
        "declared_invariants": declared_invariants,
        "reads": reads,
        "writes": writes,
        "network": network,
        "required_args": required,
        "optional_args": optional,
        "provided_args": provided_keys,
        "missing_required_args": missing_required,
        "unknown_args": unknown_args,
        "ok": ok,
        "errors": sorted(errors),
        "ordered_summary": summary,
    }


def _empty_report(ritual_id: Any, errors: list[str]) -> dict[str, Any]:
    """Skeleton report for the case where the ritual id can't be resolved."""
    return {
        "ritual_id": None,
        "ritual_name": "",
        "ritual_status": "unknown",
        "registered": False,
        "manifest_found": False,
        "would_be_event_kind": None,
        "inverse": None,
        "irreversibility_confirmation": None,
        "declared_invariants": [],
        "reads": [],
        "writes": [],
        "network": False,
        "required_args": [],
        "optional_args": [],
        "provided_args": [],
        "missing_required_args": [],
        "unknown_args": [],
        "ok": False,
        "errors": sorted(errors),
        "ordered_summary": sorted([f"unresolved_ritual:{ritual_id!r}", "ok:false"]),
    }
