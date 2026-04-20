"""Read-only ledger reader.

By construction:
- Opens files with mode "rb" only.
- Exposes no write method.
- Verifies hash chain from genesis before yielding entries.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
from dataclasses import dataclass
from typing import Iterator

ZERO_HASH = "sha256:" + "0" * 64


def canonical_bytes(obj: dict) -> bytes:
    """RFC-8785-subset canonical form: sorted keys, no whitespace, UTF-8."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


@dataclass(frozen=True)
class ChainResult:
    count: int
    head_hash: str
    ok: bool
    error: str | None = None


@dataclass(frozen=True)
class Entry:
    line_no: int
    data: dict
    entry_hash: str


def iter_entries(path: pathlib.Path) -> Iterator[Entry]:
    """Yield entries in order. Raises ValueError on chain break or parse error."""
    if not path.exists():
        return
    prev = ZERO_HASH
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f, start=1):
            if not raw.strip():
                raise ValueError(f"line {lineno}: blank line in ledger")
            try:
                entry = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {lineno}: invalid JSON: {exc}") from exc

            stored_hash = entry.pop("entry_hash", None)
            if stored_hash is None:
                raise ValueError(f"line {lineno}: missing entry_hash")

            recomputed = "sha256:" + hashlib.sha256(canonical_bytes(entry)).hexdigest()
            if recomputed != stored_hash:
                raise ValueError(
                    f"line {lineno}: entry_hash mismatch "
                    f"(stored={stored_hash} recomputed={recomputed})"
                )
            stored_prev = entry.get("prev_entry_hash")
            if stored_prev != prev:
                raise ValueError(
                    f"line {lineno}: broken chain "
                    f"(expected prev={prev}, stored prev={stored_prev})"
                )

            entry["entry_hash"] = stored_hash
            yield Entry(line_no=lineno, data=entry, entry_hash=stored_hash)
            prev = stored_hash


def verify(path: pathlib.Path) -> ChainResult:
    """Walk the ledger. Return ChainResult; never raises."""
    count = 0
    head = ZERO_HASH
    try:
        for e in iter_entries(path):
            count += 1
            head = e.entry_hash
    except ValueError as exc:
        return ChainResult(count=count, head_hash=head, ok=False, error=str(exc))
    return ChainResult(count=count, head_hash=head, ok=True)
