"""RF's durable transport for feedback-observation/1; no business operations live here."""
from __future__ import annotations

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import sqlite3
from time import monotonic, sleep
from uuid import NAMESPACE_URL, UUID, uuid5

from urllib.parse import quote

from owner_atomic_io import native_path, open_regular_file, replace_file_bytes, separate_partial_line
from owner_file_lock import OwnerFileLock
from rf_local_diagnostics import find_local_error, public_diagnostic, record_local_error, state_dir, traceback_facts


_SINGLE_FILE_LOCK_WAIT_SECONDS = 2.0
_SINGLE_FILE_LOCK_RETRY_SECONDS = 0.02


def _json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _line(value: dict) -> bytes:
    return (_json(value) + "\n").encode("ascii")


@contextmanager
def _connection():
    root = native_path(state_dir())
    root.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(root / "feedback.sqlite3", timeout=2.0)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS pending(id TEXT PRIMARY KEY,body TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS failures(id TEXT PRIMARY KEY,body TEXT NOT NULL)")
        with db:
            yield db


def _destination():
    single = os.environ.get("RESEARCH_FEEDBACK_OUT")
    dest = Path(single or os.environ.get("RESEARCH_FEEDBACK_DIR") or state_dir() / "observations").absolute()
    return dest, bool(single)


def _packet(row):
    dest, single = _destination()
    event = {"row": row, "target": str(dest), "single": single}
    encoded = _json(event)
    return uuid5(NAMESPACE_URL, encoded).hex, event, encoded


def was_published(row: dict) -> bool:
    """Check the same observation across historical and sanitized delivery."""
    projected = public_diagnostic(row)
    return _was_published(row) or (projected != row and _was_published(projected))


def _was_published(row: dict) -> bool:
    key, event, _ = _packet(row)
    dest = Path(event["target"])
    try:
        if event["single"]:
            data = _line(row)
            with open_regular_file(dest) as stream:
                return any(line == data for line in stream)
        return _directory_published(dest / f"feedback-{key}.jsonl", row)
    except (OSError, ValueError):
        return False


def _marker(row: dict) -> bytes:
    marker = {name: row.get(name) for name in ("owner", "run_id", "attempt_id", "step_id")}
    if not all(isinstance(value, str) and value for value in marker.values()):
        raise ValueError("missing RF transport coordinates")
    return _line(marker)


def _directory_published(path: Path, row: dict) -> bool:
    data = _line(row)
    try:
        with open_regular_file(path) as packet:
            if packet.read(len(data) + 1) != data:
                return False
    except FileNotFoundError:
        return False
    # Receivers can process a complete unmarked packet, and may have already
    # removed its marker. An existing conflicting marker is a delivery fault.
    expected = _marker(row)
    try:
        with open_regular_file(path.with_suffix(".ready")) as marker:
            if marker.read(len(expected) + 1) != expected:
                raise ValueError("feedback marker does not match its original packet")
    except FileNotFoundError:
        return True
    return True


@contextmanager
def _single_file_lock(destination: Path):
    # Keep the mutex beside the ledger so configured directory aliases share it.
    # A fixed-length name also works when the ledger name is already long.
    key = uuid5(NAMESPACE_URL, os.path.normcase(destination.name)).hex
    lock = OwnerFileLock(destination.with_name(f".rf-feedback-{key}.lock"))
    deadline = monotonic() + _SINGLE_FILE_LOCK_WAIT_SECONDS
    while not lock.acquire():
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise TimeoutError("feedback output is busy")
        sleep(min(remaining, _SINGLE_FILE_LOCK_RETRY_SECONDS))
    try:
        yield
    finally:
        lock.release()


def _append_sidecar(dest: Path, data: bytes, original: bytes) -> None:
    # Check and append under one lock, including an old write before SQLite ACK.
    delivered = {data, original}
    unterminated = {line[:-1] for line in delivered}
    with _single_file_lock(dest), open_regular_file(dest, append=True) as stream:
        stream.seek(0)
        for line in stream:
            if line in delivered:
                return
            if line in unterminated:
                # Only the separator was interrupted. Do not publish an alias.
                separate_partial_line(stream)
                break
        else:
            separate_partial_line(stream)
            stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _dispatch(key, event):
    """Project at the dispatch boundary without modifying a retained SQLite body."""
    if (not isinstance(event, dict) or not isinstance(event.get("row"), dict)
            or not isinstance(event.get("target"), str) or type(event.get("single")) is not bool):
        raise ValueError("invalid retained RF delivery")
    dest = native_path(Path(event["target"]))
    original = event["row"]
    row = public_diagnostic(original)
    if event["single"]:
        _append_sidecar(dest, _line(row), _line(original))
        return
    if row != original:
        if _directory_published(dest / f"feedback-{key}.jsonl", original):
            return
        key = uuid5(NAMESPACE_URL, _json({**event, "row": row})).hex
    path = dest / ("feedback-" + key + ".jsonl")
    replace_file_bytes(path, _line(row))
    replace_file_bytes(path.with_suffix(".ready"), _marker(row))


def _send(key):
    with _connection() as db:
        db.execute("BEGIN IMMEDIATE")
        found = db.execute("SELECT body FROM pending WHERE id=?", (key,)).fetchone()
        if found:
            _dispatch(key, json.loads(found[0]))
            db.execute("DELETE FROM pending WHERE id=?", (key,))


@dataclass(frozen=True)
class Delivery:
    durable: bool
    code: str | None = None
    cause_chain: list[dict] = field(default_factory=list)


def publish_outcome(row, detail=None) -> Delivery:
    """Keep one occurrence in the outbox or deliver it without a second owner event."""
    row = public_diagnostic(row)
    detail = public_diagnostic(detail) if detail is not None else None
    key, event, encoded = _packet(row)
    dest, single = Path(event["target"]), event["single"]
    try:
        with _connection() as db:
            if detail is not None:
                db.execute("INSERT OR IGNORE INTO failures VALUES(?,?)", (detail["id"], _json(detail)))
            db.execute("INSERT OR IGNORE INTO pending VALUES(?,?)", (key, encoded))
    except (OSError, sqlite3.Error):
        # Keep diagnostics available at a working public destination even when local state is read-only.
        try:
            if detail is not None:
                directory = dest.parent if single else dest
                replace_file_bytes(directory / ".rf-evidence" / (detail["id"] + ".json"), _json(detail).encode("ascii"))
            _dispatch(key, event)
        except (OSError, TypeError, ValueError, sqlite3.Error) as exc:
            return Delivery(False, "fallback_unavailable", traceback_facts(exc))
        return Delivery(True)
    try:
        _send(key)
    except (OSError, ValueError, sqlite3.Error) as exc:
        # The owner can retransmit the original journal row without calling a business entry.
        return Delivery(True, "outbox_delayed", traceback_facts(exc))
    return Delivery(True)


def publish(row, detail=None) -> bool:
    delivery = publish_outcome(row, detail)
    if delivery.code is not None:
        saved = record_local_error("feedback_delivery", code=delivery.code, cause_chain=delivery.cause_chain,
                                   run_id=row.get("run_id"), attempt_id=row.get("attempt_id"))
        return delivery.durable or saved
    return delivery.durable


def flush():
    if not native_path(state_dir() / "feedback.sqlite3").is_file():
        return {"found": 0, "remaining": 0}
    with _connection() as db:
        keys = [r[0] for r in db.execute("SELECT id FROM pending ORDER BY rowid")]
    for key in keys:
        try:
            _send(key)
        except (OSError, ValueError, sqlite3.Error):
            continue
    with _connection() as db:
        remaining = db.execute("SELECT COUNT(*) FROM pending").fetchone()[0]
    return {"found": len(keys), "remaining": remaining}


def _read_detail(data):
    payload = json.loads(data)
    return public_diagnostic(payload) if isinstance(payload, dict) else None


def _stored_failure(identifier: str) -> dict | None:
    path = native_path(state_dir() / "feedback.sqlite3")
    if not path.is_file():
        return None
    # Path.as_uri treats the Windows device prefix as a remote authority. SQLite
    # accepts the percent-encoded native filename with its genuine read-only mode.
    uri = "file:" + quote(str(path), safe="") if os.name == "nt" else path.absolute().as_uri()
    try:
        with closing(sqlite3.connect(uri + "?mode=ro", uri=True)) as db:
            found = db.execute("SELECT body FROM failures WHERE id=?", (identifier,)).fetchone()
        return _read_detail(found[0]) if found else None
    except (OSError, ValueError, sqlite3.Error):
        # A damaged optional delivery store does not block the local original.
        return None


def get_failure(identifier):
    if UUID(hex=identifier).hex != identifier:
        raise ValueError("invalid RF feedback occurrence")
    stored = _stored_failure(identifier)
    if stored is not None:
        return stored
    dest, single = _destination()
    fallback = native_path((dest.parent if single else dest) / ".rf-evidence" / (identifier + ".json"))
    try:
        if fallback.is_file() and (detail := _read_detail(fallback.read_bytes())) is not None:
            return detail
    except (OSError, ValueError):
        # The original local row remains independently addressable.
        pass
    return find_local_error(identifier)
