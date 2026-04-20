"""Append-only, hash-chained advisory writer.

Writes to `advisories/stream.jsonl`. This is the ONLY file-write
module in the ghost package — and it never opens `ledger/events.jsonl`.
Shrike I8 is enforced by construction here.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import time

from .model import Advisory

ZERO_HASH = "sha256:" + "0" * 64


def canonical_bytes(obj: dict) -> bytes:
    """RFC-8785-subset canonical form: sorted keys (recursive), no whitespace, UTF-8."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


class AdvisoryWriter:
    """Append-only NDJSON writer for the advisory stream.

    Never accepts writes to paths ending in `events.jsonl` — a defensive
    guard against accidental misuse. (The correct guard is structural:
    this class is only constructed for the advisory path.)
    """

    def __init__(self, path: pathlib.Path) -> None:
        if path.name == "events.jsonl":
            raise ValueError(
                "AdvisoryWriter refuses to write to the main ledger path "
                "(Shrike I8). Use a dedicated advisories/stream.jsonl path."
            )
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def is_empty(self) -> bool:
        return not self.path.exists() or self.path.stat().st_size == 0

    def current_head(self) -> str:
        if self.is_empty():
            return ZERO_HASH
        last = None
        with open(self.path, "rb") as f:
            for raw in f:
                if raw.strip():
                    last = raw
        if last is None:
            return ZERO_HASH
        entry = json.loads(last.decode("utf-8"))
        stored = entry.get("advisory_hash")
        if stored is None:
            raise ValueError("advisory stream head is missing advisory_hash")
        return stored

    def append(
        self,
        advisory: Advisory,
        run_id: str,
        ledger_tail_hash: str,
        timestamp: str | None = None,
    ) -> str:
        ts = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prev = self.current_head()
        entry = {
            "timestamp": ts,
            "rule_id": advisory.rule_id,
            "severity": advisory.severity,
            "subject": advisory.subject,
            "evidence": advisory.evidence,
            "recommended_action": advisory.recommended_action,
            "ledger_tail_hash": ledger_tail_hash,
            "run_id": run_id,
            "prev_advisory_hash": prev,
        }
        advisory_hash = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
        ordered = dict(sorted(entry.items()))
        ordered["advisory_hash"] = advisory_hash
        line = json.dumps(ordered, separators=(",", ":"), ensure_ascii=False) + "\n"
        with open(self.path, "ab") as f:
            f.write(line.encode("utf-8"))
        return advisory_hash


def verify_chain(path: pathlib.Path) -> tuple[bool, int, str, str | None]:
    """Walk the advisory stream and validate the hash chain.

    Returns (ok, count, head_hash, error_message).
    """
    if not path.exists():
        return (True, 0, ZERO_HASH, None)

    prev = ZERO_HASH
    count = 0
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f, start=1):
            if not raw.strip():
                return (False, count, prev, f"line {lineno}: blank line")
            try:
                entry = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                return (False, count, prev, f"line {lineno}: invalid JSON: {exc}")

            stored = entry.pop("advisory_hash", None)
            if stored is None:
                return (False, count, prev, f"line {lineno}: missing advisory_hash")
            recomputed = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
            if recomputed != stored:
                return (
                    False,
                    count,
                    prev,
                    f"line {lineno}: advisory_hash mismatch "
                    f"(stored={stored} recomputed={recomputed})",
                )
            stored_prev = entry.get("prev_advisory_hash")
            if stored_prev != prev:
                return (
                    False,
                    count,
                    prev,
                    f"line {lineno}: broken chain "
                    f"(expected prev={prev} stored prev={stored_prev})",
                )
            prev = stored
            count += 1

    return (True, count, prev, None)
