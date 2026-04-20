"""Rule-level tests for each GHOST advisor rule.

Each rule has (at minimum) a fires-when-dirty test and a silent-when-clean
test. Stdlib unittest only.
"""

from __future__ import annotations
import pathlib
import sys
import unittest
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

from ghost.model import Advisory, AdvisorContext  # noqa: E402
from ghost.rules import (  # noqa: E402
    r001_doctrine_drift,
    r002_constellation_drift,
    r003_binary_stale,
    r004_waiver_expiring,
    r005_unknown_event_kind,
    r006_timestamp_regression,
    r007_ledger_staleness,
)


NOW = datetime(2026, 4, 20, 23, 0, 0, tzinfo=timezone.utc)


def mk_ctx(
    ledger=None,
    doctrine="sha256:d",
    constellation="sha256:c",
    waivers="",
    now=NOW,
) -> AdvisorContext:
    return AdvisorContext(
        ledger_entries=ledger or [],
        doctrine_hash=doctrine,
        constellation_hash=constellation,
        waivers_md_text=waivers,
        now=now,
    )


class R001DoctrineDrift(unittest.TestCase):
    def test_fires_when_drifted(self):
        ctx = mk_ctx(
            ledger=[{"event": "doctrine.amended", "doctrine_hash": "sha256:old", "timestamp": "2026-04-20T00:00:00Z"}],
            doctrine="sha256:new",
        )
        out = list(r001_doctrine_drift(ctx))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].rule_id, "R001_doctrine_drift")
        self.assertEqual(out[0].severity, "warn")

    def test_silent_when_matching(self):
        ctx = mk_ctx(
            ledger=[{"event": "doctrine.amended", "doctrine_hash": "sha256:same", "timestamp": "2026-04-20T00:00:00Z"}],
            doctrine="sha256:same",
        )
        self.assertEqual(list(r001_doctrine_drift(ctx)), [])

    def test_silent_when_no_amendment(self):
        ctx = mk_ctx(ledger=[], doctrine="sha256:new")
        self.assertEqual(list(r001_doctrine_drift(ctx)), [])


class R002ConstellationDrift(unittest.TestCase):
    def test_fires_when_drifted(self):
        ctx = mk_ctx(
            ledger=[{"event": "doctrine.amended", "constellation_hash": "sha256:old", "timestamp": "2026-04-20T00:00:00Z"}],
            constellation="sha256:new",
        )
        out = list(r002_constellation_drift(ctx))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "warn")

    def test_silent_when_matching(self):
        ctx = mk_ctx(
            ledger=[{"event": "doctrine.amended", "constellation_hash": "sha256:same", "timestamp": "2026-04-20T00:00:00Z"}],
            constellation="sha256:same",
        )
        self.assertEqual(list(r002_constellation_drift(ctx)), [])


class R003BinaryStale(unittest.TestCase):
    def test_fires_when_verify_predates_amendment(self):
        ctx = mk_ctx(
            ledger=[
                {"event": "doctrine.amended", "doctrine_hash": "sha256:new", "timestamp": "2026-04-20T00:00:00Z"},
                {"event": "verify.result", "doctrine_hash": "sha256:old", "timestamp": "2026-04-20T01:00:00Z"},
            ],
        )
        out = list(r003_binary_stale(ctx))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "warn")

    def test_silent_when_verify_matches_latest_amendment(self):
        ctx = mk_ctx(
            ledger=[
                {"event": "doctrine.amended", "doctrine_hash": "sha256:new", "timestamp": "2026-04-20T00:00:00Z"},
                {"event": "verify.result", "doctrine_hash": "sha256:new", "timestamp": "2026-04-20T01:00:00Z"},
            ],
        )
        self.assertEqual(list(r003_binary_stale(ctx)), [])


class R004WaiverExpiring(unittest.TestCase):
    WAIVERS_TEMPLATE = """### W-20260601-01 — Test waiver

- Status: approved
- Filed: 2026-01-01
- Expires: {exp}

More text.
"""

    def _ctx(self, expires):
        return mk_ctx(
            waivers=self.WAIVERS_TEMPLATE.format(exp=expires),
            now=NOW,  # 2026-04-20
        )

    def test_expired_is_critical(self):
        out = list(r004_waiver_expiring(self._ctx("2026-04-01")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "critical")

    def test_within_7_days_is_warn(self):
        out = list(r004_waiver_expiring(self._ctx("2026-04-25")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "warn")

    def test_within_30_days_is_info(self):
        out = list(r004_waiver_expiring(self._ctx("2026-05-15")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "info")

    def test_beyond_30_days_is_silent(self):
        out = list(r004_waiver_expiring(self._ctx("2026-07-01")))
        self.assertEqual(out, [])

    def test_no_waivers_is_silent(self):
        out = list(r004_waiver_expiring(mk_ctx(waivers="")))
        self.assertEqual(out, [])


class R005UnknownEventKind(unittest.TestCase):
    def test_fires_on_unknown(self):
        ctx = mk_ctx(ledger=[{"event": "imaginary.event", "entry_hash": "sha256:e1"}])
        out = list(r005_unknown_event_kind(ctx))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "warn")
        self.assertIn("imaginary.event", out[0].subject)

    def test_silent_on_known(self):
        ctx = mk_ctx(ledger=[
            {"event": "doctrine_amendment", "entry_hash": "sha256:a"},
            {"event": "verify.result", "entry_hash": "sha256:b"},
            {"event": "doctrine.amended", "entry_hash": "sha256:c"},
        ])
        self.assertEqual(list(r005_unknown_event_kind(ctx)), [])

    def test_one_advisory_per_unknown_kind(self):
        ctx = mk_ctx(ledger=[
            {"event": "imaginary.event", "entry_hash": "sha256:1"},
            {"event": "imaginary.event", "entry_hash": "sha256:2"},
            {"event": "another.one", "entry_hash": "sha256:3"},
        ])
        out = list(r005_unknown_event_kind(ctx))
        kinds = sorted(a.evidence["event_kind"] for a in out)
        self.assertEqual(kinds, ["another.one", "imaginary.event"])


class R006TimestampRegression(unittest.TestCase):
    def test_fires_on_regression(self):
        ctx = mk_ctx(ledger=[
            {"event": "a", "timestamp": "2026-04-20T00:00:02Z", "entry_hash": "sha256:a"},
            {"event": "b", "timestamp": "2026-04-20T00:00:01Z", "entry_hash": "sha256:b"},
        ])
        out = list(r006_timestamp_regression(ctx))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "critical")

    def test_silent_when_monotonic(self):
        ctx = mk_ctx(ledger=[
            {"event": "a", "timestamp": "2026-04-20T00:00:01Z", "entry_hash": "sha256:a"},
            {"event": "b", "timestamp": "2026-04-20T00:00:02Z", "entry_hash": "sha256:b"},
        ])
        self.assertEqual(list(r006_timestamp_regression(ctx)), [])

    def test_silent_on_equal(self):
        ctx = mk_ctx(ledger=[
            {"event": "a", "timestamp": "2026-04-20T00:00:01Z", "entry_hash": "sha256:a"},
            {"event": "b", "timestamp": "2026-04-20T00:00:01Z", "entry_hash": "sha256:b"},
        ])
        self.assertEqual(list(r006_timestamp_regression(ctx)), [])


class R007LedgerStaleness(unittest.TestCase):
    def _ctx(self, last_ts):
        return mk_ctx(ledger=[{"event": "verify.result", "timestamp": last_ts}])

    def test_silent_when_fresh(self):
        self.assertEqual(list(r007_ledger_staleness(self._ctx("2026-04-20T12:00:00Z"))), [])

    def test_info_when_30_to_90_days(self):
        out = list(r007_ledger_staleness(self._ctx("2026-02-20T12:00:00Z")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "info")

    def test_warn_when_90_to_365(self):
        out = list(r007_ledger_staleness(self._ctx("2025-09-01T12:00:00Z")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "warn")

    def test_critical_when_over_365(self):
        out = list(r007_ledger_staleness(self._ctx("2024-04-20T12:00:00Z")))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "critical")


if __name__ == "__main__":
    unittest.main()
