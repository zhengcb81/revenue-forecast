"""Lock protocol: single writer, TTL, ownership, expiry break, races."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

import pytest

from uc.lock import (
    LockConflict,
    LockMissingError,
    LockOwnershipError,
    acquire,
    lock_path,
    release,
    status,
)

T0 = datetime(2026, 8, 13, 0, 0, 0, tzinfo=timezone.utc)


def test_acquire_release_roundtrip(tmp_path):
    locks = tmp_path / "locks"
    record = acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    assert record.owner == "owner-A"
    assert record.is_expired(T0) is False
    assert status(locks, "plan") is not None
    release(locks, "plan", "owner-A", record.nonce)
    assert status(locks, "plan") is None


def test_conflict_while_held(tmp_path):
    locks = tmp_path / "locks"
    acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    with pytest.raises(LockConflict) as exc:
        acquire(locks, "plan", "owner-B", ttl=100, now_utc=T0)
    assert "owner-A" in str(exc.value)


def test_impersonation_release_refused(tmp_path):
    locks = tmp_path / "locks"
    record = acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    with pytest.raises(LockOwnershipError):
        release(locks, "plan", "owner-B", record.nonce)
    with pytest.raises(LockOwnershipError):
        release(locks, "plan", "owner-A", "wrong-nonce")
    assert status(locks, "plan").owner == "owner-A"


def test_release_missing_lock_refused(tmp_path):
    locks = tmp_path / "locks"
    with pytest.raises(LockMissingError):
        release(locks, "plan", "owner-A", "nonce")


def test_same_owner_renew_keeps_nonce(tmp_path):
    locks = tmp_path / "locks"
    first = acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    renewed = acquire(locks, "plan", "owner-A", ttl=200, now_utc=T0)
    assert renewed.nonce == first.nonce
    assert renewed.ttl_seconds == 200
    assert renewed.is_expired(T0) is False


def test_expired_lock_is_breakable(tmp_path):
    locks = tmp_path / "locks"
    acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    later = datetime(2026, 8, 13, 0, 5, 0, tzinfo=timezone.utc)
    winner = acquire(locks, "plan", "owner-B", ttl=100, now_utc=later)
    assert winner.owner == "owner-B"


def test_expired_break_race_exactly_one_winner(tmp_path):
    locks = tmp_path / "locks"
    acquire(locks, "plan", "owner-0", ttl=100, now_utc=T0)
    later = datetime(2026, 8, 13, 0, 5, 0, tzinfo=timezone.utc)
    barrier = threading.Barrier(2)
    results: list[tuple[str, str]] = []
    errors: list[str] = []

    def attempt(name: str):
        barrier.wait()
        try:
            record = acquire(locks, "plan", name, ttl=100, now_utc=later)
            results.append(("win", record.owner))
        except LockConflict:
            results.append(("conflict", name))
        except Exception as exc:  # never die silently inside a thread
            errors.append(repr(exc))

    threads = [threading.Thread(target=attempt, args=(f"owner-{i}",)) for i in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    winners = [name for kind, name in results if kind == "win"]
    assert len(winners) == 1
    assert status(locks, "plan").owner == winners[0]


def test_corrupt_lock_record_is_breakable_not_fatal(tmp_path):
    locks = tmp_path / "locks"
    corrupt = lock_path(locks, "plan")
    corrupt.parent.mkdir(parents=True, exist_ok=True)
    corrupt.write_text("not json at all", encoding="utf-8")
    record = acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    assert record.owner == "owner-A"
    assert status(locks, "plan").owner == "owner-A"


def test_invalid_resource_name_rejected(tmp_path):
    locks = tmp_path / "locks"
    with pytest.raises(ValueError):
        acquire(locks, "bad resource name!", "owner-A", ttl=100, now_utc=T0)


def test_nonpositive_ttl_rejected(tmp_path):
    locks = tmp_path / "locks"
    with pytest.raises(ValueError):
        acquire(locks, "plan", "owner-A", ttl=0, now_utc=T0)


def test_status_reports_expiry(tmp_path):
    locks = tmp_path / "locks"
    acquire(locks, "plan", "owner-A", ttl=100, now_utc=T0)
    later = datetime(2026, 8, 13, 0, 5, 0, tzinfo=timezone.utc)
    record = status(locks, "plan")
    assert record is not None and record.is_expired(later) is True
