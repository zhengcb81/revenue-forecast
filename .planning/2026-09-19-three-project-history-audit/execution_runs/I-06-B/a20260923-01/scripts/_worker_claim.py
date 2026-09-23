#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Subprocess worker for case D race phase (I-06-B a20260922-02).

Claims from the isolated candidate store and reports the EXACT outcome
shape: a result dict, or a structured exception record (type, text,
store-owned flag).  A bare `null` result on a losing claim is the P2-B
defect shape the suite must catch (never a bare None).
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cand-dir", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--demand-id", default=None)
    args = parser.parse_args()
    sys.path.insert(0, args.cand_dir)
    pds = importlib.import_module("processing_demand_store")
    store = pds.DurableDemandStore(Path(args.db))
    out: dict = {"owner": args.owner}
    try:
        if args.demand_id is not None:
            result = store.claim(owner=args.owner, demand_id=args.demand_id)
        else:
            result = store.claim(owner=args.owner)
        out["result"] = result
    except BaseException as exc:  # noqa: BLE001 — the shape itself is evidence
        out["exception"] = {
            "type": type(exc).__name__,
            "text": str(exc),
            "store_owned": isinstance(exc, pds.DemandStoreError),
        }
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
