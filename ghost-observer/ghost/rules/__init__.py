"""GHOST rule registry.

Each rule lives in its own module and exports a `check(ctx) -> list[Advisory]`
function. `RULES` is the ordered list applied during every advisor run.

Adding a rule is a Tier 2 change (abbreviated Constellation Loop).
Removing a rule is Tier 1 (full loop).
"""

from typing import Callable, Iterable

from ..model import Advisory, AdvisorContext

from .r001_doctrine_drift import check as r001_doctrine_drift
from .r002_constellation_drift import check as r002_constellation_drift
from .r003_binary_stale import check as r003_binary_stale
from .r004_waiver_expiring import check as r004_waiver_expiring
from .r005_unknown_event_kind import check as r005_unknown_event_kind
from .r006_timestamp_regression import check as r006_timestamp_regression
from .r007_ledger_staleness import check as r007_ledger_staleness

RuleCheck = Callable[[AdvisorContext], Iterable[Advisory]]

RULES: list[RuleCheck] = [
    r001_doctrine_drift,
    r002_constellation_drift,
    r003_binary_stale,
    r004_waiver_expiring,
    r005_unknown_event_kind,
    r006_timestamp_regression,
    r007_ledger_staleness,
]
