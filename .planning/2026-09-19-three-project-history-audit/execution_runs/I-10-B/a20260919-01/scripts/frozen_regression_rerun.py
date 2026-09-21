#!/usr/bin/env python3
"""I-10-B — frozen-card regression re-run, BEFORE vs AFTER.

The card text requires the compatibility list to name WHICH M-card case is
affected, not merely which bound moved. A bound is only observable through a
card if the card either (a) feeds a value the bound would newly allow/refuse,
or (b) OMITS an optional driver and relies on the old silent-zero filler.

This script replays the four cards that touch a changed driver
(M05, M14, M20, M24) against BOTH registry variants and reports, per card,
per phase, whether the frozen outcome still holds.

Phases replayed, mirroring the card harness:
  positive               one-year positive drivers
  continuity_positive    two-year positive drivers
  defaults               the card's `defaults` block (optional drivers omitted)
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
SCRATCH = RUN / "_scratch_import"
EV = RUN.parent.parent

CARDS = {
    "M05": ("M05", "a20260919-01/evidence/M05/input.json"),
    "M14": ("M14", "a20260919-01/evidence/M14/input.json"),
    "M20": ("M20", "a20260919-01/evidence/M20/input.json"),
    "M24": ("M24", "a20260919-01/evidence/M24/input.json"),
}


def load(name, path):
    # model_registry.py does `from model_extensions import build_extension_specs`,
    # so the sibling directory must be importable while the module executes.
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(path.parent))
    return mod


def run_phase(reg, block):
    """Return ('ok', value) or ('raised', ExcName, message)."""
    try:
        out = reg.calculate_registered_model(
            block["model_id"],
            block.get("base_revenue", 0),
            {k: v for k, v in block["drivers"].items()},
            block["years"],
        )
        return {"outcome": "ok", "value": out}
    except Exception as e:  # noqa: BLE001 — the point is to classify the refusal
        return {"outcome": "raised", "exc": type(e).__name__, "message": str(e)}


def main() -> int:
    mb = load("reg_before_rr", SCRATCH / "before" / "model_registry.py")
    ma = load("reg_after_rr", SCRATCH / "after" / "model_registry.py")

    report = {"run": "I-10-B", "attempt": "a20260919-01", "cards": {}}
    any_flip = False

    for card, (d, rel) in CARDS.items():
        inp = json.loads((EV / d / rel).read_text(encoding="utf-8"))
        card_out = {"source": rel, "phases": {}}
        for phase in ("positive", "continuity_positive", "defaults"):
            block = inp.get(phase)
            if block is None:
                continue
            b = run_phase(mb, block)
            a = run_phase(ma, block)
            flipped = b != a
            any_flip = any_flip or flipped
            card_out["phases"][phase] = {
                "omitted_optional_drivers": sorted(
                    set(
                        d2
                        for d2 in mb.MODEL_REGISTRY[block["model_id"]].optional
                        if d2 not in block["drivers"]
                    )
                ),
                "before": b,
                "after": a,
                "flipped": flipped,
            }
        report["cards"][card] = card_out

    report["any_phase_flipped"] = any_flip
    (RUN / "frozen_regression_rerun.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    for card, co in report["cards"].items():
        print("=" * 68)
        print(card, co["source"])
        for phase, po in co["phases"].items():
            mark = "  <<< FLIPPED" if po["flipped"] else ""
            print(f"  {phase:22} before={po['before']['outcome']:7} after={po['after']['outcome']:7}{mark}")
            print(f"      omitted optional: {po['omitted_optional_drivers']}")
            if po["flipped"]:
                print(f"      before detail: {json.dumps(po['before'], ensure_ascii=False)[:200]}")
                print(f"      after  detail: {json.dumps(po['after'], ensure_ascii=False)[:200]}")
    print()
    print("ANY PHASE FLIPPED:", any_flip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
