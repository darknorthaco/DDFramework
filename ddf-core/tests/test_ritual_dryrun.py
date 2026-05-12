"""T — Phase 6 ritual_dryrun static validator.

Covers:
- by canonical id ("0001"), by short id ("1"), and by name ("verify")
- registered + implemented + complete args -> ok = True
- declared (not yet implemented) -> ok = False, status surfaced
- not registered in doctrine.toml -> ok = False, error reported
- missing required arg -> ok = False, listed
- unknown arg -> ok = False, listed
- unresolvable id -> empty report, error reported
- deterministic ordered_summary

Fixtures are synthesized into ``tmp_path``; no engine ledger or live
ceremony manifests are read.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent

if str(DDF_CORE) not in sys.path:
    sys.path.insert(0, str(DDF_CORE))

from simulation import ritual_dryrun  # noqa: E402


DOCTRINE_BASE = '''
[meta]
doctrine_version = "0.7.0"

[rituals]
manifest_dir = "ceremonies"
registered   = ["verify", "deploy", "ghost-advise"]
'''

VERIFY_MANIFEST = '''
id     = "0001"
name   = "verify"
status = "implemented"

purpose = "Confirm repository state matches doctrinal expectations."

[inputs]
root = { flag = "--root", default = ".", required = false, doc = "Repo root." }

[outputs]
ledger_event_kind = "verify.result"

[side_effects]
reads  = ["doctrine.toml", "constellation.toml", "ledger/events.jsonl"]
writes = ["ledger/events.jsonl"]
network = false

[invariants_upheld]
I5 = "no ambient state"
I7 = "no silent mutation"

inverse = "self (idempotent, read-only)"
'''

DEPLOY_MANIFEST = '''
id     = "0002"
name   = "deploy"
status = "declared"

purpose = "Install a Phantom-built artifact onto a node."

[inputs]
artifact = { flag = "--artifact", required = true, doc = "SHA-256 of artifact." }
target   = { flag = "--target",   required = true, doc = "Target node id." }
manifest = { flag = "--manifest", required = true, doc = "Deployment manifest path." }

[outputs]
ledger_event_kind = "deploy.applied"

[side_effects]
reads  = ["ledger/blobs/<sha256>"]
writes = ["ledger/events.jsonl"]
network = true

[invariants_upheld]
I1 = "append-only"
I7 = "ledger write precedes side effect"

inverse = "rollback"
'''

ORPHAN_MANIFEST = '''
id     = "0099"
name   = "orphan-ritual"
status = "declared"

purpose = "Not in doctrine.toml registered list."

[inputs]

[outputs]
ledger_event_kind = "orphan.event"

[side_effects]
reads  = []
writes = []
network = false

[invariants_upheld]
I5 = "no ambient state"

inverse = "self"
'''


def _fixture_dir() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ddf-dryrun-"))
    ceremonies = tmp / "ceremonies"
    ceremonies.mkdir()
    (ceremonies / "0001-verify.toml").write_text(VERIFY_MANIFEST, encoding="utf-8")
    (ceremonies / "0002-deploy.toml").write_text(DEPLOY_MANIFEST, encoding="utf-8")
    (ceremonies / "0099-orphan-ritual.toml").write_text(ORPHAN_MANIFEST, encoding="utf-8")
    (ceremonies / "README.md").write_text("ignored by scanner\n", encoding="utf-8")
    doctrine = tmp / "doctrine.toml"
    doctrine.write_text(DOCTRINE_BASE, encoding="utf-8")
    return tmp, ceremonies, doctrine


class RitualDryRunTest(unittest.TestCase):
    def setUp(self):
        self.root, self.ceremonies, self.doctrine = _fixture_dir()

    def test_implemented_registered_no_args_is_ok(self):
        r = ritual_dryrun.run("verify", None, self.ceremonies, self.doctrine)
        self.assertEqual(r["ritual_id"], "0001")
        self.assertEqual(r["ritual_name"], "verify")
        self.assertEqual(r["ritual_status"], "implemented")
        self.assertTrue(r["registered"])
        self.assertTrue(r["manifest_found"])
        self.assertTrue(r["ok"])
        self.assertEqual(r["missing_required_args"], [])
        self.assertEqual(r["unknown_args"], [])
        self.assertEqual(r["would_be_event_kind"], "verify.result")
        self.assertEqual(r["declared_invariants"], ["I5", "I7"])
        self.assertIn("doctrine.toml", r["reads"])

    def test_resolves_by_canonical_id(self):
        r = ritual_dryrun.run("0001", None, self.ceremonies, self.doctrine)
        self.assertEqual(r["ritual_id"], "0001")
        self.assertTrue(r["ok"])

    def test_resolves_by_unpadded_numeric_id(self):
        r = ritual_dryrun.run("1", None, self.ceremonies, self.doctrine)
        self.assertEqual(r["ritual_id"], "0001")
        self.assertTrue(r["ok"])

    def test_declared_ritual_is_not_ok(self):
        r = ritual_dryrun.run(
            "deploy",
            {"artifact": "sha256:aa", "target": "node1", "manifest": "m.toml"},
            self.ceremonies,
            self.doctrine,
        )
        self.assertEqual(r["ritual_status"], "declared")
        self.assertTrue(r["registered"])
        self.assertTrue(r["manifest_found"])
        self.assertEqual(r["missing_required_args"], [])
        self.assertFalse(r["ok"])
        self.assertTrue(r["network"])

    def test_missing_required_args_flagged(self):
        r = ritual_dryrun.run(
            "deploy",
            {"artifact": "sha256:aa"},
            self.ceremonies,
            self.doctrine,
        )
        self.assertEqual(r["missing_required_args"], ["manifest", "target"])
        self.assertFalse(r["ok"])
        self.assertIn("missing_required_arg:manifest", r["errors"])
        self.assertIn("missing_required_arg:target", r["errors"])

    def test_unknown_arg_flagged(self):
        r = ritual_dryrun.run(
            "verify",
            {"bogus": True},
            self.ceremonies,
            self.doctrine,
        )
        self.assertEqual(r["unknown_args"], ["bogus"])
        self.assertFalse(r["ok"])

    def test_orphan_manifest_not_registered_is_not_ok(self):
        r = ritual_dryrun.run("0099", None, self.ceremonies, self.doctrine)
        self.assertTrue(r["manifest_found"])
        self.assertFalse(r["registered"])
        self.assertFalse(r["ok"])
        self.assertIn("not_registered:orphan-ritual", r["errors"])

    def test_unresolvable_id_returns_empty_report(self):
        r = ritual_dryrun.run("not-a-real-ritual!!", None, self.ceremonies, self.doctrine)
        self.assertIsNone(r["ritual_id"])
        self.assertFalse(r["ok"])
        self.assertTrue(any(e.startswith("unresolved_ritual:") for e in r["errors"]))

    def test_ordered_summary_is_sorted_and_deterministic(self):
        r1 = ritual_dryrun.run("verify", None, self.ceremonies, self.doctrine)
        r2 = ritual_dryrun.run("verify", None, self.ceremonies, self.doctrine)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["ordered_summary"], sorted(r1["ordered_summary"]))

    def test_readme_and_non_manifest_files_ignored(self):
        # Adding an unrelated file should not perturb resolution.
        (self.ceremonies / "notes.txt").write_text("ignored", encoding="utf-8")
        r = ritual_dryrun.run("verify", None, self.ceremonies, self.doctrine)
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main()
