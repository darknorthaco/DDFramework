"""R004 — waivers expiring soon / expired.

Scans WAIVERS.md for entries like:

    ### W-YYYYMMDD-NN — <title>
    - Status: ...
    - Filed: YYYY-MM-DD
    - Expires: YYYY-MM-DD

Severity based on proximity to today (ctx.now.date()):
  - `Expires` <= today: critical (expired)
  - 0 < days_left <= 7: warn
  - 7 < days_left <= 30: info
  - days_left > 30: no advisory
"""

from __future__ import annotations
import re
from datetime import date

from ..model import Advisory, AdvisorContext

HEADER_RE = re.compile(r"^###\s+(W-\d{8}-\d{2})\s+—\s+(.+?)\s*$", re.MULTILINE)
EXPIRES_RE = re.compile(r"^-\s+Expires:\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def check(ctx: AdvisorContext) -> list[Advisory]:
    text = ctx.waivers_md_text
    if not text:
        return []
    today = ctx.now.date()
    advisories: list[Advisory] = []

    matches = list(HEADER_RE.finditer(text))
    for i, match in enumerate(matches):
        waiver_id = match.group(1)
        title = match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end]

        expires_match = EXPIRES_RE.search(section)
        if not expires_match:
            continue
        try:
            expires = date.fromisoformat(expires_match.group(1))
        except ValueError:
            continue

        days_left = (expires - today).days
        severity, action = _classify(days_left)
        if severity is None:
            continue

        advisories.append(
            Advisory(
                rule_id="R004_waiver_expiring",
                severity=severity,
                subject=(
                    f"Waiver {waiver_id} has expired"
                    if days_left <= 0
                    else f"Waiver {waiver_id} expires in {days_left} days"
                ),
                evidence={
                    "waiver_id": waiver_id,
                    "title": title.strip(),
                    "expires": str(expires),
                    "days_left": days_left,
                },
                recommended_action=action,
            )
        )
    return advisories


def _classify(days_left: int) -> tuple[str | None, str]:
    if days_left <= 0:
        return (
            "critical",
            "Renew the waiver via `phantom file-waiver --id <id> --waiver <path> --approve` "
            "or remove it from WAIVERS.md.",
        )
    if days_left <= 7:
        return (
            "warn",
            "Prepare a renewal ceremony now or plan to let the waiver expire.",
        )
    if days_left <= 30:
        return (
            "info",
            "No action required yet; monitor. Renewal will be due within 30 days.",
        )
    return (None, "")
