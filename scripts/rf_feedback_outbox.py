"""RF's durable transport for feedback-observation/1; no business operations live here."""
from __future__ import annotations

from contextlib import closing, contextmanager
import json
import os
from pathlib import Path
import sqlite3
from time import monotonic, sleep
from uuid import NAMESPACE_URL, uuid5

from urllib.parse import quote

from owner_atomic_io import native_path, open_regular_file, replace_file_bytes
from owner_file_lock import OwnerFileLock
from rf_local_diagnostics import record_local_error, state_dir


_SINGLE_FILE_LOCK_WAIT_SECONDS = 2.0
_SINGLE_FILE_LOCK_RETRY_SECONDS = 0.02


def _json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


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
    """Verify one exact original observation in the configured owner outbox."""
    key, event, _ = _packet(row)
    dest = Path(event["target"])
    data = (_json(row) + "\n").encode("ascii")
    try:
        if event["single"]:
            with open_regular_file(dest) as stream:
                return any(line == data for line in stream)
        # Directory delivery acknowledges by consuming the ready marker.
        # The deterministic packet itself remains the original owner bytes.
        with open_regular_file(dest / f"feedback-{key}.jsonl") as stream:
            return stream.read(len(data) + 1) == data
    except OSError:
        return False


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


def _deliver(key, event):
    dest = native_path(Path(event["target"]))
    row = event["row"]
    data = (_json(row) + "\n").encode("ascii")
    if event["single"]:
        # A previous process may have written and fsynced this row before it acknowledged delivery.
        with _single_file_lock(dest), open_regular_file(dest, append=True) as stream:
            stream.seek(0)
            for line in stream:
                try:
                    if json.loads(line) == row:
                        return
                except (ValueError, UnicodeError):
                    continue
            if stream.seek(0, os.SEEK_END):
                stream.seek(-1, os.SEEK_END)
                if stream.read(1) != b"\n":
                    # Preserve an interrupted legacy record while giving this occurrence a complete line.
                    stream.write(b"\n")
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return
    path = dest / ("feedback-" + key + ".jsonl")
    replace_file_bytes(path, data)
    marker = {name: row[name] for name in ("owner", "run_id", "attempt_id", "step_id")}
    replace_file_bytes(path.with_suffix(".ready"), (_json(marker) + "\n").encode("ascii"))


def _send(key):
    with _connection() as db:
        db.execute("BEGIN IMMEDIATE")
        found = db.execute("SELECT body FROM pending WHERE id=?", (key,)).fetchone()
        if found:
            _deliver(key, json.loads(found[0]))
            db.execute("DELETE FROM pending WHERE id=?", (key,))


def publish(row, detail=None):
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
            _deliver(key, event)
        except OSError as exc:
            record_local_error("feedback_delivery", code="fallback_unavailable", exception_type=type(exc).__name__)
        return
    try:
        _send(key)
    except (OSError, ValueError, sqlite3.Error) as exc:
        # The owner can retransmit the original journal row without calling a business entry.
        record_local_error("feedback_delivery", code="outbox_delayed", exception_type=type(exc).__name__)


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


def get_failure(identifier):
    from uuid import UUID
    if UUID(hex=identifier).hex != identifier:
        raise ValueError("invalid RF feedback occurrence")
    path = native_path(state_dir() / "feedback.sqlite3")
    if path.is_file():
        # Path.as_uri treats the Windows device prefix as a remote authority. SQLite
        # accepts the percent-encoded native filename with its genuine read-only mode.
        uri = "file:" + quote(str(path), safe="") if os.name == "nt" else path.absolute().as_uri()
        with closing(sqlite3.connect(uri + "?mode=ro", uri=True)) as db:
            found = db.execute("SELECT body FROM failures WHERE id=?", (identifier,)).fetchone()
        if found:
            return json.loads(found[0])
    dest, single = _destination()
    fallback = native_path((dest.parent if single else dest) / ".rf-evidence" / (identifier + ".json"))
    return json.loads(fallback.read_bytes()) if fallback.is_file() else None
