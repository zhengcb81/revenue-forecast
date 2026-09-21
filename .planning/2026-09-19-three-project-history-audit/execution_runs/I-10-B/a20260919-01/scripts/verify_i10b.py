"""I-10-B independent verifier — BEFORE (RED) and AFTER (GREEN) in one harness.

Runs against the ISOLATED copy at iso/rf/scripts/.  Never touches production.

Exit codes (START_HERE.md frozen legend):
  0 = pass        2 = negative correctly rejected / no verdict
  3 = expected red but green, or expected green but red
  1 = harness failure
"""

from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ISO_SCRIPTS = ATTEMPT / "iso" / "rf" / "scripts"
PHASE = sys.argv[1] if len(sys.argv) > 1 else "after"

RESULTS: list[dict] = []


def load():
    sys.path.insert(0, str(ISO_SCRIPTS))
    for mod in ("model_registry", "model_extensions"):
        sys.modules.pop(mod, None)
    return importlib.import_module("model_registry")


def rec(case, name, expected, actual, ok, kind="positive"):
    RESULTS.append({"case": case, "check": name, "kind": kind,
                    "expected": expected, "actual": actual, "ok": ok})
    print(f"[{'PASS' if ok else 'FAIL'}] {case} · {name}")
    print(f"        expected={expected!r}")
    print(f"        actual  ={actual!r}")


def main() -> int:
    m = load()
    MR = m.MODEL_REGISTRY

    # ---------------- defect 1: silent zero ---------------------------------
    # Find a model that has an optional driver WITHOUT an explicit default.
    target = None
    for mid, spec in MR.items():
        for d in spec.optional:
            if d not in spec.defaults:
                target = (mid, d, spec)
                break
        if target:
            break
    if target is None:
        print("harness failure: no optional-without-default slot found", file=sys.stderr)
        return 1
    mid, drv, spec = target
    print(f"# defect-1 probe model = {mid}, optional driver without default = {drv}")

    # build a minimal legal input: required drivers present, optional omitted
    years = [2027, 2028]
    drivers = {}
    for r in spec.required:
        drivers[r] = [1.0] * len(years)
    base = 100.0

    try:
        out = m.calculate_registered_model(mid, base, drivers, years)
        omitted = ("no raises", out)
    except m.ModelRegistryError as exc:
        omitted = ("ModelRegistryError", str(exc))
    except Exception as exc:  # noqa: BLE001
        omitted = (type(exc).__name__, str(exc))

    if PHASE == "before":
        rec("R-B1-N1",
            "BASELINE: omitted optional driver is SILENTLY filled (defect must be visible)",
            "silent fill (no raise)", omitted[0], omitted[0] == "no raises",
            kind="negative")
    else:
        rec("R-B1-N1", "omitted optional driver now RAISES ModelRegistryError",
            "ModelRegistryError", omitted[0], omitted[0] == "ModelRegistryError",
            kind="negative")

    # R-B1-N3: explicit 0.0 must still be accepted in BOTH phases
    drivers_zero = dict(drivers)
    drivers_zero[drv] = [0.0] * len(years)
    try:
        out0 = m.calculate_registered_model(mid, base, drivers_zero, years)
        explicit_zero = ("no raises", len(out0))
    except Exception as exc:  # noqa: BLE001
        explicit_zero = (type(exc).__name__, str(exc))
    rec("R-B1-N3", "explicit 0.0 for that driver is still ACCEPTED",
        "no raises", explicit_zero[0], explicit_zero[0] == "no raises")

    # R-B1-P1: omitting a default-bearing optional driver stays legal — but the
    # variable must be ISOLATED: if the model ALSO has an optional driver with
    # no default, omitting that one must still raise.  So supply every optional
    # driver EXCEPT the default-bearing one, and assert the call succeeds.
    dflt = None
    for mid2, spec2 in MR.items():
        for d in spec2.optional:
            if d in spec2.defaults:
                dflt = (mid2, d, spec2, spec2.defaults[d])
                break
        if dflt:
            break
    if dflt:
        mid2, drv2, spec2, dvalue = dflt
        drv2_in = {r: [1.0] * len(years) for r in spec2.required}
        # supply the OTHER optional drivers explicitly so only drv2 is omitted
        for other in spec2.optional:
            if other != drv2:
                drv2_in[other] = [1.0] * len(years)
        try:
            o2 = m.calculate_registered_model(mid2, 100.0, drv2_in, years)
            got2 = ("no raises", len(o2))
        except Exception as exc:  # noqa: BLE001
            got2 = (type(exc).__name__, str(exc))
        rec("R-B1-P1",
            f"omit default-bearing optional driver ({mid2}.{drv2} default={dvalue}) stays legal",
            "no raises", got2[0], got2[0] == "no raises")

        # and prove the omitted default is the value ACTUALLY used: compare
        # against the same call with the default passed explicitly.
        drv2_explicit = dict(drv2_in)
        drv2_explicit[drv2] = [dvalue] * len(years)
        try:
            o3 = m.calculate_registered_model(mid2, 100.0, drv2_explicit, years)
            same = (o3 == o2)
        except Exception:  # noqa: BLE001
            same = False
        rec("R-B1-P1b",
            "the declared default is the value actually used (omitted == explicit)",
            True, same, same)

    # ---------------- defect 2: name-based sign -----------------------------
    # locate models carrying the named drivers
    def bounds_for(driver):
        for mid3, s3 in MR.items():
            if driver in list(s3.required) + list(s3.optional):
                lo, hi = m.driver_value_bounds(mid3, driver)
                return mid3, lo, hi
        return None, None, None

    mid_f, lo_f, hi_f = bounds_for("franchise_system_sales")
    if mid_f:
        neg_ok = (lo_f == -math.inf)
        if PHASE == "before":
            rec("R-B2-N1",
                "BASELINE: franchise_system_sales is [0,inf) => negative injected must be REFUSED",
                "refused", "refused" if not neg_ok else "accepted", not neg_ok,
                kind="negative")
        else:
            rec("R-B2-N1",
                "franchise_system_sales accepted NEGATIVE (reversal-capable role)",
                "accepted (lower=-inf)", "accepted" if neg_ok else "refused", neg_ok,
                kind="negative")

    # R-B2-P1: quantity drivers must NOT leak signedness
    mid_q, lo_q, hi_q = bounds_for("closing_stores")
    if mid_q:
        rec("R-B2-P1", "quantity driver closing_stores keeps [0, inf)",
            (0.0, math.inf), (lo_q, hi_q), (lo_q, hi_q) == (0.0, math.inf))

    # R-B2-N2: an unknown driver must never gain a guessed sign.
    # Probe by asking bounds for a name that exists in NO model.
    ghost_name = "zzz_not_a_role_driver"
    try:
        m.driver_value_bounds(next(iter(MR)), ghost_name)
        ghost = "no raises"
    except m.ModelRegistryError:
        ghost = "ModelRegistryError"
    except Exception as exc:  # noqa: BLE001
        ghost = type(exc).__name__
    rec("R-B2-N2", "unknown driver name raises (never gains a guessed sign)",
        "ModelRegistryError", ghost, ghost == "ModelRegistryError", kind="negative")

    failed = [r for r in RESULTS if not r["ok"]]
    print()
    print(f"phase = {PHASE} | total = {len(RESULTS)} | passed = {len(RESULTS)-len(failed)} | failed = {len(failed)}")
    (ATTEMPT / f"verification_{PHASE}.json").write_text(
        json.dumps({"phase": PHASE, "checks": RESULTS,
                    "total": len(RESULTS), "failed": len(failed)},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    if PHASE == "before":
        # RED is EXPECTED before the fix; report rc=3 when the defect is visible
        return 3 if failed else 0
    return 3 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
