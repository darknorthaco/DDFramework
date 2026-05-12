"""CLI dispatcher for ``python -m ddf simulate <subcommand>``.

Thin argparse wrapper around the five Phase 6 simulation modules under
``ddf-core/simulation/``. The CLI is:

- pure stdlib (no external deps)
- read-only on every input path
- deterministic (JSON output uses ``sort_keys=True`` and a fixed indent)
- side-effect-free (no ledger writes, no advisory writes, no network)

Exit codes:

- ``0``  CLI invocation succeeded; the simulation finding itself may
        still be ``ok: false`` — that lives inside the JSON payload.
- ``1``  CLI / IO error (bad arguments, unreadable file, malformed JSON
        ``--args``).
- ``2``  reserved for unexpected internal errors (argparse already
        exits 2 on its own when invoked usage is wrong).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

_HERE = pathlib.Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[3]
_DDF_CORE = _REPO_ROOT / "ddf-core"
if str(_DDF_CORE) not in sys.path:
    sys.path.insert(0, str(_DDF_CORE))

from simulation import (  # noqa: E402  (sys.path bootstrap above)
    advisory_replay,
    doctrine_diff,
    drift_simulation,
    ledger_replay,
    ritual_dryrun,
)


_DEFAULT_LEDGER = _REPO_ROOT / "ledger" / "events.jsonl"
_DEFAULT_DOCTRINE = _REPO_ROOT / "doctrine.toml"
_DEFAULT_CONSTELLATION = _REPO_ROOT / "constellation.toml"
_DEFAULT_ADVISORY = _REPO_ROOT / "advisories" / "stream.jsonl"
_DEFAULT_CEREMONIES = _REPO_ROOT / "ceremonies"


def _emit(result: dict[str, Any], stream=None) -> int:
    out = stream if stream is not None else sys.stdout
    json.dump(result, out, sort_keys=True, indent=2, ensure_ascii=False)
    out.write("\n")
    return 0


def _doctrine_diff(ns: argparse.Namespace) -> int:
    try:
        old_text = pathlib.Path(ns.old).read_text(encoding="utf-8")
        new_text = pathlib.Path(ns.new).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ddf simulate doctrine-diff: {exc}", file=sys.stderr)
        return 1
    return _emit(doctrine_diff.run(old_text, new_text))


def _ritual_dryrun(ns: argparse.Namespace) -> int:
    try:
        args_dict = json.loads(ns.args) if ns.args else None
    except json.JSONDecodeError as exc:
        print(
            f"ddf simulate ritual-dryrun: --args is not valid JSON: {exc}",
            file=sys.stderr,
        )
        return 1
    if args_dict is not None and not isinstance(args_dict, dict):
        print(
            "ddf simulate ritual-dryrun: --args must encode a JSON object",
            file=sys.stderr,
        )
        return 1
    return _emit(
        ritual_dryrun.run(
            ritual_id=ns.ritual,
            args=args_dict,
            ceremony_dir=pathlib.Path(ns.ceremony_dir),
            doctrine_path=pathlib.Path(ns.doctrine),
        )
    )


def _ledger_replay(ns: argparse.Namespace) -> int:
    return _emit(ledger_replay.run(ledger_path=pathlib.Path(ns.ledger)))


def _advisory_replay(ns: argparse.Namespace) -> int:
    return _emit(
        advisory_replay.run(
            advisory_path=pathlib.Path(ns.advisory),
            ledger_path=pathlib.Path(ns.ledger),
        )
    )


def _drift_simulation(ns: argparse.Namespace) -> int:
    return _emit(
        drift_simulation.run(
            ledger_path=pathlib.Path(ns.ledger),
            doctrine_path=pathlib.Path(ns.doctrine),
            constellation_path=pathlib.Path(ns.constellation),
            scenario=ns.scenario,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ddf simulate",
        description=(
            "Run a Phase 6 simulation against on-disk state. "
            "Read-only; deterministic JSON output."
        ),
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    d = sub.add_parser(
        "doctrine-diff",
        help="Semantic diff of two doctrine.toml files.",
        description="Classify the impact (patch/minor/major/breaking) of a doctrine change.",
    )
    d.add_argument("--old", required=True, help="Path to the previous doctrine.toml.")
    d.add_argument("--new", required=True, help="Path to the new doctrine.toml.")
    d.set_defaults(func=_doctrine_diff)

    r = sub.add_parser(
        "ritual-dryrun",
        help="Static validation of a ritual invocation.",
        description=(
            "Resolve a ritual id/name, check registration, validate "
            "argument flags against the manifest, and report declared "
            "side effects and invariants — without executing the ritual."
        ),
    )
    r.add_argument(
        "--ritual",
        required=True,
        help="Canonical id (0001), unpadded numeric (1), or name (verify).",
    )
    r.add_argument(
        "--args",
        default="",
        help="JSON object of caller arguments mapped by manifest [inputs] key.",
    )
    r.add_argument(
        "--ceremony-dir",
        default=str(_DEFAULT_CEREMONIES),
        help="Directory containing NNNN-<name>.toml manifests.",
    )
    r.add_argument(
        "--doctrine",
        default=str(_DEFAULT_DOCTRINE),
        help="Path to doctrine.toml (used for [rituals].registered cross-check).",
    )
    r.set_defaults(func=_ritual_dryrun)

    lr = sub.add_parser(
        "ledger-replay",
        help="Chain audit of the main ledger.",
        description=(
            "Walk ledger/events.jsonl from genesis, recompute the canonical "
            "hash chain per ledger/SPEC.md §5, and report integrity."
        ),
    )
    lr.add_argument(
        "--ledger",
        default=str(_DEFAULT_LEDGER),
        help="Path to ledger/events.jsonl.",
    )
    lr.set_defaults(func=_ledger_replay)

    ar = sub.add_parser(
        "advisory-replay",
        help="Chain audit of the advisory stream.",
        description=(
            "Walk advisories/stream.jsonl, verify the hash chain per "
            "advisories/SPEC.md §4, and cross-check ledger_tail_hash "
            "references against the main ledger's entry_hash set."
        ),
    )
    ar.add_argument(
        "--advisory",
        default=str(_DEFAULT_ADVISORY),
        help="Path to advisories/stream.jsonl.",
    )
    ar.add_argument(
        "--ledger",
        default=str(_DEFAULT_LEDGER),
        help="Path to ledger/events.jsonl (for ledger_tail_hash cross-checks).",
    )
    ar.set_defaults(func=_advisory_replay)

    ds = sub.add_parser(
        "drift-simulation",
        help="Decide whether GHOST drift rules R001/R002/R003 would fire now.",
        description=(
            "Compare on-disk doctrine/constellation hashes against the "
            "latest amendment in the ledger and the latest verify result."
        ),
    )
    ds.add_argument(
        "--scenario",
        required=True,
        choices=["doctrine_drift", "constellation_drift", "binary_stale", "all"],
        help="Which rule(s) to evaluate.",
    )
    ds.add_argument(
        "--ledger",
        default=str(_DEFAULT_LEDGER),
        help="Path to ledger/events.jsonl.",
    )
    ds.add_argument(
        "--doctrine",
        default=str(_DEFAULT_DOCTRINE),
        help="Path to doctrine.toml.",
    )
    ds.add_argument(
        "--constellation",
        default=str(_DEFAULT_CONSTELLATION),
        help="Path to constellation.toml.",
    )
    ds.set_defaults(func=_drift_simulation)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    sys.exit(main())
