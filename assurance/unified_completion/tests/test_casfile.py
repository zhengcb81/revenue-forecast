"""CAS primitives: atomicity, conflict detection, guarded (no-lost-update) path."""

from __future__ import annotations

import threading

import pytest

from conftest import UC_DIR  # noqa: F401  (ensures sys.path setup when imported directly)
from uc import casfile as cf
from uc.casfile import CASConflict, exclusive_publish


def test_sha256_helpers(tmp_path):
    path = tmp_path / "f.txt"
    path.write_bytes(b"abc")
    assert cf.sha256_file(path) == cf.sha256_bytes(b"abc")
    assert len(cf.sha256_bytes(b"abc")) == 64


def test_exclusive_publish_wins_exactly_once(tmp_path):
    target = tmp_path / "state.json"
    assert exclusive_publish(target, b"first") is True
    assert exclusive_publish(target, b"second") is False
    assert target.read_bytes() == b"first"


def test_exclusive_publish_leaves_no_half_file_on_refusal(tmp_path):
    target = tmp_path / "state.json"
    target.write_bytes(b"original")
    assert exclusive_publish(target, b"new") is False
    assert target.read_bytes() == b"original"
    assert [p.name for p in tmp_path.iterdir()] == ["state.json"]  # no temp litter


def test_cas_update_replaces_on_matching_base(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"base")
    new_hash = cf.cas_update(target, b"new", cf.sha256_bytes(b"base"))
    assert target.read_bytes() == b"new"
    assert new_hash == cf.sha256_bytes(b"new")


def test_cas_update_detects_concurrent_change(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"base")
    expected = cf.sha256_bytes(b"base")
    target.write_bytes(b"someone-else")  # concurrent modification
    with pytest.raises(CASConflict) as exc:
        cf.cas_update(target, b"new", expected)
    assert target.read_bytes() == b"someone-else"  # refused, nothing overwritten
    assert "concurrent modification" in str(exc.value)


def test_cas_update_missing_target_is_conflict(tmp_path):
    target = tmp_path / "absent.txt"
    with pytest.raises(CASConflict):
        cf.cas_update(target, b"new", "0" * 64)


def test_atomic_replace_fault_leaves_target_intact(tmp_path, monkeypatch):
    target = tmp_path / "f.txt"
    target.write_bytes(b"old")

    def broken_replace(src, dst):
        raise OSError("simulated crash before replace")

    monkeypatch.setattr(cf.os, "replace", broken_replace)
    with pytest.raises(OSError):
        cf.atomic_replace(target, b"new")
    assert target.read_bytes() == b"old"
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]  # temp cleaned up


def test_raw_concurrent_cas_is_atomic_never_half_written(tmp_path):
    """Two raw CAS writers racing on the same base: the final file must be one
    complete payload — atomicity holds even when both pass the pre-check."""
    target = tmp_path / "f.txt"
    target.write_bytes(b"base")
    expected = cf.sha256_bytes(b"base")
    payloads = [b"A" * 1000, b"B" * 1000]
    barrier = threading.Barrier(2)
    results: list[str] = []

    def writer(payload: bytes):
        barrier.wait()
        try:
            cf.cas_update(target, payload, expected)
            results.append("ok")
        except CASConflict:
            results.append("conflict")

    threads = [threading.Thread(target=writer, args=(p,)) for p in payloads]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert target.read_bytes() in payloads  # complete payload, never mixed


def test_guarded_update_two_writers_no_lost_updates(tmp_path):
    """The canonical write path (lock + CAS + post-write re-read): two writers
    with distinct owners both append; nothing is lost."""
    import json

    from uc.casfile import guarded_update
    from uc.lock import LockConflict

    locks = tmp_path / "locks"
    target = tmp_path / "journal.json"
    target.write_bytes(json.dumps({"ops": []}).encode())
    barrier = threading.Barrier(2)
    results: list[str] = []
    errors: list[str] = []

    def append(op_id: str, owner: str):
        barrier.wait()
        try:
            for _ in range(300):
                try:
                    guarded_update(
                        locks,
                        "journal",
                        owner,
                        target,
                        lambda data, op=op_id: json.dumps(
                            {"ops": sorted(set(json.loads(data)["ops"]) | {op})}
                        ).encode(),
                        ttl_seconds=60,
                    )
                    results.append(op_id)
                    return
                except (CASConflict, LockConflict):
                    pass
            results.append(f"gave-up:{op_id}")
        except Exception as exc:  # never die silently inside a thread
            errors.append(repr(exc))

    threads = [
        threading.Thread(target=append, args=("w1", "owner-1")),
        threading.Thread(target=append, args=("w2", "owner-2")),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    assert sorted(results) == ["w1", "w2"]  # completion order is nondeterministic
    assert json.loads(target.read_bytes())["ops"] == ["w1", "w2"]


def test_guarded_update_detects_rogue_writer(tmp_path, monkeypatch):
    """If a rogue writer replaces the file inside our write window, the
    post-write re-read must detect it (no silent lost update)."""
    from uc.casfile import guarded_update

    locks = tmp_path / "locks"
    target = tmp_path / "journal.json"
    target.write_bytes(b"{}")

    real_cas = cf.cas_update

    def rogue_cas(path, data, expected):
        real_cas(path, data, expected)
        cf.atomic_replace(path, b"rogue-overwrite")
        return cf.sha256_bytes(data)

    monkeypatch.setattr(cf, "cas_update", rogue_cas)
    with pytest.raises(CASConflict):
        guarded_update(locks, "journal", "owner-1", target, lambda data: b"ours")
