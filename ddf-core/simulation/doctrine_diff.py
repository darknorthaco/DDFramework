"""Doctrine diff — Phase 6 simulation module.

Computes a semantic diff between two ``doctrine.toml`` versions and
classifies the impact. Stdlib-only; pure function; no I/O; no ledger
or advisory writes. Honors invariant I5 (no ambient state): both
inputs are explicit TOML strings passed by the caller.

Classification rules
--------------------
- ``patch``    — text clarifications only; no semantic change detected.
- ``minor``    — new invariant added, or new ritual added.
- ``major``    — invariant removed, invariant weakened (severity
                 downgrade on an invariant that exists in both
                 documents), or ritual renamed (both removed and added
                 rituals present in the same diff).
- ``breaking`` — ritual removed with no compensating addition, or the
                 ``doctrine_version`` regresses (new < old by semver).

Precedence (highest wins): breaking > major > minor > patch.

Return schema
-------------
``run`` returns a ``dict`` with these stable keys:

- ``added_invariants``   — sorted list of invariant ids only in *new*.
- ``removed_invariants`` — sorted list of invariant ids only in *old*.
- ``added_rituals``      — sorted list of ritual names only in *new*.
- ``removed_rituals``    — sorted list of ritual names only in *old*.
- ``version_delta``      — one of ``patch|minor|major|breaking``
                           (same value as ``impact``; kept as a
                           separate key so callers can introduce a
                           true version-delta encoding later without
                           breaking the schema).
- ``impact``             — one of ``patch|minor|major|breaking``.
- ``ordered_summary``    — deterministic, sorted list of short
                           descriptors covering every detected change.
"""

from __future__ import annotations

import tomllib
from typing import Any

_SEVERITY_ORDER = {
    "info": 0,
    "warning": 1,
    "warn": 1,
    "error": 2,
    "fatal": 3,
}


def _parse_semver(s: str) -> tuple[int, int, int]:
    """Parse ``major.minor.patch``; tolerate trailing ``-pre`` / ``+build``.

    Non-numeric components and missing components are coerced to 0 so an
    unparseable or partial version compares less than any well-formed one.
    """
    if not isinstance(s, str) or not s:
        return (0, 0, 0)
    head = s.split("-", 1)[0].split("+", 1)[0]
    parts = head.split(".")
    out: list[int] = []
    for p in parts[:3]:
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    while len(out) < 3:
        out.append(0)
    return (out[0], out[1], out[2])


def _invariant_severity(table: dict[str, Any], inv_id: str) -> str | None:
    invs = table.get("invariants") or {}
    entry = invs.get(inv_id) or {}
    sev = entry.get("severity")
    return sev if isinstance(sev, str) else None


def _registered_rituals(table: dict[str, Any]) -> list[str]:
    rituals = table.get("rituals") or {}
    reg = rituals.get("registered") or []
    if not isinstance(reg, list):
        return []
    return [r for r in reg if isinstance(r, str)]


def _doctrine_version(table: dict[str, Any]) -> str:
    meta = table.get("meta") or {}
    v = meta.get("doctrine_version")
    return v if isinstance(v, str) else ""


def run(old_doctrine_str: str, new_doctrine_str: str) -> dict[str, Any]:
    """Compute a semantic diff of two doctrine TOML documents.

    Parameters
    ----------
    old_doctrine_str:
        TOML source of the *before* ``doctrine.toml``.
    new_doctrine_str:
        TOML source of the *after* ``doctrine.toml``.

    Returns
    -------
    dict
        The diff dict described in the module docstring. All list
        values are sorted; ``ordered_summary`` is sorted and stable.
    """
    old = tomllib.loads(old_doctrine_str)
    new = tomllib.loads(new_doctrine_str)

    old_invs = set((old.get("invariants") or {}).keys())
    new_invs = set((new.get("invariants") or {}).keys())
    added_invariants = sorted(new_invs - old_invs)
    removed_invariants = sorted(old_invs - new_invs)
    common_invariants = old_invs & new_invs

    old_rituals = set(_registered_rituals(old))
    new_rituals = set(_registered_rituals(new))
    added_rituals = sorted(new_rituals - old_rituals)
    removed_rituals = sorted(old_rituals - new_rituals)

    # Severity downgrade on an invariant common to both sides counts as
    # "weakened" -> major. Pure description-text edits with severity
    # unchanged are treated as text clarifications -> patch.
    weakened_invariants: list[str] = []
    for inv_id in sorted(common_invariants):
        old_sev = _invariant_severity(old, inv_id)
        new_sev = _invariant_severity(new, inv_id)
        if old_sev == new_sev:
            continue
        o = _SEVERITY_ORDER.get((old_sev or "").lower(), -1)
        n = _SEVERITY_ORDER.get((new_sev or "").lower(), -1)
        if n < o:
            weakened_invariants.append(inv_id)

    old_ver = _doctrine_version(old)
    new_ver = _doctrine_version(new)
    version_regressed = (
        bool(old_ver)
        and bool(new_ver)
        and _parse_semver(new_ver) < _parse_semver(old_ver)
    )

    # Precedence: breaking > major > minor > patch.
    # A ritual is "renamed" (major) when the same diff shows both a
    # removal and an addition; pure removal with no addition is
    # breaking.
    pure_ritual_removal = bool(removed_rituals) and not added_rituals
    if version_regressed or pure_ritual_removal:
        impact = "breaking"
    elif (
        removed_invariants
        or weakened_invariants
        or (removed_rituals and added_rituals)
    ):
        impact = "major"
    elif added_invariants or added_rituals:
        impact = "minor"
    else:
        impact = "patch"

    summary: list[str] = []
    if version_regressed:
        summary.append(f"version_regression:{old_ver}->{new_ver}")
    elif old_ver and new_ver and old_ver != new_ver:
        summary.append(f"version_change:{old_ver}->{new_ver}")
    for inv_id in added_invariants:
        summary.append(f"added_invariant:{inv_id}")
    for inv_id in removed_invariants:
        summary.append(f"removed_invariant:{inv_id}")
    for inv_id in weakened_invariants:
        summary.append(f"weakened_invariant:{inv_id}")
    for ritual in added_rituals:
        summary.append(f"added_ritual:{ritual}")
    for ritual in removed_rituals:
        summary.append(f"removed_ritual:{ritual}")
    summary.sort()

    return {
        "added_invariants": added_invariants,
        "removed_invariants": removed_invariants,
        "added_rituals": added_rituals,
        "removed_rituals": removed_rituals,
        "version_delta": impact,
        "impact": impact,
        "ordered_summary": summary,
    }
