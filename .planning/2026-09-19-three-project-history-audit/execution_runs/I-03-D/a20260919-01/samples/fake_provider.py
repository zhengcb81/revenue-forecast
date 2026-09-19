"""I-03-D fake provider (attempt-internal ONLY; no network; URLs are
plain strings never dereferenced).

Scriptable surfaces per candidate id:
- metadata for discover() (period keys, filed dates, sizes, amended);
- chunk streams: scripted sequences, lying declared sizes, exceptions,
  empty lists, single chunks that exceed the whole allowance;
- a consumed-chunk sequence log for the "stream stopped" proof;
- an in-memory/on-disk minimal catalog is NOT here — registration uses
  the registrar store shell in close_gap.py (attempt-local only).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CHUNK = 60  # the card's scripted chunk size


class Candidate:
    def __init__(
        self,
        *,
        provider="test",
        pid,
        url,
        filed,
        period_start,
        period_end,
        fiscal_year,
        amended=False,
        remote_size=None,
        document_kind="annual_report",
    ):
        self.provider = provider
        self.provider_document_id = pid
        self.source_url = url  # string only
        self.filing_date = filed
        self.period_start = period_start
        self.period_end = period_end
        self.fiscal_year = fiscal_year
        self.amended = amended
        self.remote_size = remote_size
        self.document_kind = document_kind
        self.accepted_at = None
        self.revision = None


class FakeProvider:
    """Dead-simple scriptable provider driven from the harness."""

    def __init__(
        self,
        *,
        catalog_candidates,
        local_handles=(),
        provider_error=None,
        policy_hash="",
        chunk_bytes=CHUNK,
    ):
        self._catalog = {c.provider_document_id: c for c in catalog_candidates}
        self.candidates = list(catalog_candidates)
        self.local_handles = list(local_handles)
        self.provider_error = provider_error
        self.policy_hash = policy_hash
        self.chunk_bytes = chunk_bytes
        # per-id scripts: list of (kind, value); kinds:
        #  ("chunks", payload_bytes_list) — one item per scripted chunk
        #  ("lie", declared_size int)     — declared remote_size to report
        #  ("raise", exc)                 — stream raises
        #  ("empty", None)                — stream yields nothing
        self.scripts: dict[str, list[tuple[str, Any]]] = {}
        self.consumed: dict[str, int] = {}  # chunks actually yielded
        self.discover_counts = 0

    def script(self, pid: str, *actions):
        self.scripts[pid] = list(actions)

    def discover_snapshot(self) -> dict[str, Any]:
        """Snapshot consumed by close-gap rediscover (metadata only)."""
        self.discover_counts += 1
        return {
            "remote_candidates": list(self.candidates),
            "local_handles": list(self.local_handles),
            "provider_error": self.provider_error,
            "policy_hash": self.policy_hash,
        }

    def declared_size(self, pid: str):
        for kind, val in self.scripts.get(pid, []):
            if kind == "lie":
                return val
        return None

    @staticmethod
    def _payload(pid: str, seq_index: int) -> bytes:
        marker = b"FAKE-BYTES::%s::#%03d" % (pid.encode(), seq_index)
        return marker

    def stream(self, cand: Any):
        """Generator of chunk bytes honoring the script; records each
        yielded chunk in ``consumed`` for the stream-stop proof."""
        pid = cand.provider_document_id
        script = self.scripts.get(pid, [])
        seq_index = 0
        for kind, value in script:
            if kind == "raise":
                raise value
            if kind == "empty":
                return
        for kind, value in script:
            if kind != "chunks":
                continue
            for payload in value:
                seq_index += 1
                self.consumed[pid] = self.consumed.get(pid, 0) + 1
                yield payload


def write_fixtures(dir_path: Path) -> dict[str, Any]:
    """Persist the scripted candidate manifest (audit trail)."""
    dir_path = Path(dir_path)
    data = {
        "chunk_bytes": CHUNK,
        "note": "fake provider candidates are created by the harness",
    }
    (dir_path / "fake_provider_manifest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data
