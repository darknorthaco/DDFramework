"""T — Phase 6 doctrine_diff classifier and diff schema.

Covers the five fixtures required by the Phase 6 plan plus targeted
extras for the rules that share a severity tier:

- identical doctrines              -> impact = patch, all lists empty
- text-only clarification          -> impact = patch (no semantic change)
- added invariant                  -> impact = minor
- removed invariant                -> impact = major
- weakened invariant (severity)    -> impact = major
- removed ritual (pure removal)    -> impact = breaking
- doctrine_version regression      -> impact = breaking
- ritual renamed (added+removed)   -> impact = major
- ordered_summary determinism      -> sorted, stable across runs

The tests parse the same canonical ``BASE`` doctrine string (loosely
modelled on the engine's real doctrine.toml shape) and apply small
edits to drive each classification. They are pure: no filesystem, no
ledger writes.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DDF_CORE = HERE.parent

if str(DDF_CORE) not in sys.path:
    sys.path.insert(0, str(DDF_CORE))

from simulation import doctrine_diff  # noqa: E402


BASE = """
[meta]
doctrine_version = "0.7.0"

[invariants.I1]
name = "append-only-ledger"
description = "Ledger entries are never edited or deleted."
severity = "fatal"

[invariants.I2]
name = "content-addressed-artifacts"
description = "Every artifact is referenced by its SHA-256 hash."
severity = "fatal"

[rituals]
registered = ["verify", "deploy", "ghost-advise"]
"""


class DoctrineDiffTest(unittest.TestCase):
    def test_identical_doctrines_yield_patch(self):
        r = doctrine_diff.run(BASE, BASE)
        self.assertEqual(r["added_invariants"], [])
        self.assertEqual(r["removed_invariants"], [])
        self.assertEqual(r["added_rituals"], [])
        self.assertEqual(r["removed_rituals"], [])
        self.assertEqual(r["impact"], "patch")
        self.assertEqual(r["version_delta"], "patch")
        self.assertEqual(r["ordered_summary"], [])

    def test_text_only_clarification_is_patch(self):
        new = BASE.replace(
            'description = "Ledger entries are never edited or deleted."',
            'description = "Ledger entries are never edited or deleted (append-only)."',
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["added_invariants"], [])
        self.assertEqual(r["removed_invariants"], [])
        self.assertEqual(r["added_rituals"], [])
        self.assertEqual(r["removed_rituals"], [])
        self.assertEqual(r["impact"], "patch")
        self.assertEqual(r["ordered_summary"], [])

    def test_added_invariant_is_minor(self):
        new = BASE + (
            "\n[invariants.I9]\n"
            'name = "future-invariant"\n'
            'description = "Reserved."\n'
            'severity = "fatal"\n'
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["added_invariants"], ["I9"])
        self.assertEqual(r["removed_invariants"], [])
        self.assertEqual(r["impact"], "minor")
        self.assertEqual(r["version_delta"], "minor")
        self.assertIn("added_invariant:I9", r["ordered_summary"])

    def test_removed_invariant_is_major(self):
        new = BASE.replace(
            '[invariants.I2]\n'
            'name = "content-addressed-artifacts"\n'
            'description = "Every artifact is referenced by its SHA-256 hash."\n'
            'severity = "fatal"\n',
            "",
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["removed_invariants"], ["I2"])
        self.assertEqual(r["added_invariants"], [])
        self.assertEqual(r["impact"], "major")
        self.assertEqual(r["version_delta"], "major")
        self.assertIn("removed_invariant:I2", r["ordered_summary"])

    def test_weakened_invariant_severity_is_major(self):
        new = BASE.replace(
            '[invariants.I1]\n'
            'name = "append-only-ledger"\n'
            'description = "Ledger entries are never edited or deleted."\n'
            'severity = "fatal"',
            '[invariants.I1]\n'
            'name = "append-only-ledger"\n'
            'description = "Ledger entries are never edited or deleted."\n'
            'severity = "warning"',
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["added_invariants"], [])
        self.assertEqual(r["removed_invariants"], [])
        self.assertEqual(r["impact"], "major")
        self.assertIn("weakened_invariant:I1", r["ordered_summary"])

    def test_removed_ritual_is_breaking(self):
        new = BASE.replace(
            'registered = ["verify", "deploy", "ghost-advise"]',
            'registered = ["verify", "ghost-advise"]',
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["removed_rituals"], ["deploy"])
        self.assertEqual(r["added_rituals"], [])
        self.assertEqual(r["impact"], "breaking")
        self.assertEqual(r["version_delta"], "breaking")
        self.assertIn("removed_ritual:deploy", r["ordered_summary"])

    def test_doctrine_version_regression_is_breaking(self):
        new = BASE.replace(
            'doctrine_version = "0.7.0"',
            'doctrine_version = "0.6.0"',
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["impact"], "breaking")
        self.assertEqual(r["version_delta"], "breaking")
        self.assertIn("version_regression:0.7.0->0.6.0", r["ordered_summary"])

    def test_renamed_ritual_is_major(self):
        new = BASE.replace(
            'registered = ["verify", "deploy", "ghost-advise"]',
            'registered = ["verify", "network-discover", "ghost-advise"]',
        )
        r = doctrine_diff.run(BASE, new)
        self.assertEqual(r["added_rituals"], ["network-discover"])
        self.assertEqual(r["removed_rituals"], ["deploy"])
        self.assertEqual(r["impact"], "major")
        self.assertEqual(r["version_delta"], "major")
        self.assertIn("added_ritual:network-discover", r["ordered_summary"])
        self.assertIn("removed_ritual:deploy", r["ordered_summary"])

    def test_ordered_summary_is_sorted_and_deterministic(self):
        new = BASE.replace(
            'registered = ["verify", "deploy", "ghost-advise"]',
            'registered = ["a-new-ritual", "verify", "deploy", "ghost-advise"]',
        ) + (
            "\n[invariants.I9]\n"
            'name = "I9"\n'
            'description = "Reserved."\n'
            'severity = "fatal"\n'
        )
        r1 = doctrine_diff.run(BASE, new)
        r2 = doctrine_diff.run(BASE, new)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["ordered_summary"], sorted(r1["ordered_summary"]))
        self.assertEqual(r1["added_invariants"], sorted(r1["added_invariants"]))
        self.assertEqual(r1["added_rituals"], sorted(r1["added_rituals"]))
        self.assertEqual(r1["impact"], "minor")


if __name__ == "__main__":
    unittest.main()
