"""CA-001 acceptance: 10 rounds of concurrent mutation with no lost updates
and no half-written state, using real cross-process writers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import UC_DIR
from uc.lock import status

WORKER = Path(__file__).resolve().parent / "worker_ops.py"
ROUNDS = 10
WRITERS_PER_ROUND = 3


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(UC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _spawn_round(
    env: dict[str, str], argv: list[list[str]]
) -> list[tuple[list[str], subprocess.Popen]]:
    procs: list[tuple[list[str], subprocess.Popen]] = []
    for args in argv:
        proc = subprocess.Popen(
            [sys.executable, "-B", str(WORKER), *args],
            cwd=str(UC_DIR.parent),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        procs.append((args, proc))
    return procs


def test_ten_rounds_cas_no_lost_updates(tmp_path):
    locks = tmp_path / "locks"
    target = tmp_path / "journal.json"
    target.write_text('{"ops": []}', encoding="utf-8")
    env = _env()
    expected: set[str] = set()

    for round_index in range(ROUNDS):
        argv = []
        for writer_index in range(WRITERS_PER_ROUND):
            op = f"r{round_index}-w{writer_index}"
            expected.add(op)
            argv.append(
                [
                    "cas-append",
                    "--file",
                    str(target),
                    "--locks",
                    str(locks),
                    "--resource",
                    "journal",
                    "--owner",
                    f"owner-{writer_index}",
                    "--op",
                    op,
                ]
            )
        for args, proc in _spawn_round(env, argv):
            stdout, stderr = proc.communicate(timeout=120)
            assert proc.returncode == 0, (
                f"{args}: rc={proc.returncode} out={stdout} err={stderr}"
            )

    data = json.loads(target.read_text(encoding="utf-8"))
    ops = data["ops"]
    assert sorted(ops) == sorted(expected), "lost or duplicated update detected"
    assert len(ops) == ROUNDS * WRITERS_PER_ROUND


def test_ten_rounds_lock_exactly_one_winner(tmp_path):
    locks = tmp_path / "locks"
    env = _env()

    for round_index in range(ROUNDS):
        argv = [
            [
                "lock-try",
                "--locks",
                str(locks),
                "--resource",
                "single",
                "--owner",
                f"owner-{i}",
                "--ttl",
                "60",
            ]
            for i in range(WRITERS_PER_ROUND)
        ]
        winners = 0
        conflicts = 0
        for args, proc in _spawn_round(env, argv):
            stdout, _stderr = proc.communicate(timeout=120)
            assert proc.returncode in (0, 3), f"{args}: rc={proc.returncode}"
            if proc.returncode == 0:
                winners += 1
                assert "WIN" in stdout
            else:
                conflicts += 1
                assert "CONFLICT" in stdout
        assert winners == 1, f"round {round_index}: {winners} winners"
        assert conflicts == WRITERS_PER_ROUND - 1
        assert status(locks, "single") is None, "lock leaked after round"
