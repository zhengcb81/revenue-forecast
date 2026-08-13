"""Subprocess worker for cross-process concurrency tests (CA-001 acceptance:
10 rounds of concurrent mutation with no lost updates / no half-written
state).  Run via ``python worker_ops.py <mode> ...`` with PYTHONPATH pointing
at the ``uc`` package."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from uc.casfile import CASConflict, guarded_update
from uc.lock import LockConflict, acquire, release


def mode_cas_append(args: argparse.Namespace) -> int:
    target = Path(args.file)
    locks = Path(args.locks)

    def transform(data: bytes) -> bytes:
        obj = json.loads(data) if data else {"ops": []}
        ops = obj.setdefault("ops", [])
        if args.op not in ops:
            ops.append(args.op)
        return json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")

    for _attempt in range(400):
        try:
            guarded_update(
                locks, args.resource, args.owner, target, transform, ttl_seconds=120
            )
            print(f"APPENDED {args.op}")
            return 0
        except (CASConflict, LockConflict):
            time.sleep(0.005)
    print(f"GAVE-UP {args.op}")
    return 2


def mode_lock_try(args: argparse.Namespace) -> int:
    locks = Path(args.locks)
    try:
        record = acquire(locks, args.resource, args.owner, ttl=int(args.ttl))
    except LockConflict:
        print(f"CONFLICT {args.owner}")
        return 3
    time.sleep(0.1)
    release(locks, args.resource, args.owner, record.nonce)
    print(f"WIN {args.owner}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    p = sub.add_parser("cas-append")
    p.add_argument("--file", required=True)
    p.add_argument("--locks", required=True)
    p.add_argument("--resource", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--op", required=True)
    p.set_defaults(func=mode_cas_append)

    p = sub.add_parser("lock-try")
    p.add_argument("--locks", required=True)
    p.add_argument("--resource", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--ttl", default=60)
    p.set_defaults(func=mode_lock_try)
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(int(args.func(args)))
