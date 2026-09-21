#!/usr/bin/env python3
"""I-10-B seq 14 — mutation selfcheck (proof that the frozen after-oracle DETECTS regressions).

Arms:
  control  unmutated AFTER registry        -> all 7 oracle assertions must PASS (harness sanity)
  MUT-1    defect-1 fix reverted to the original silent zero-fill
           -> oracle assertion R-B1-N1 must FAIL  (mutation KILLED)
  MUT-2    defect-2 fix reverted to the original 9-name _SIGNED_DRIVERS lookup
           -> oracle assertion R-B2-N1 must FAIL  (mutation KILLED)
  MUT-3    dimension gate dropped from _is_reversal_capable (name-only remainder)
           -> expected SURVIVED: equivalent mutant on the CURRENT registry
              (every role-table driver is only declared under a qualifying
              dimension today), reported honestly; the gate is defense-in-depth
              for FUTURE declarations, exactly the R-B2-N2 oracle note.

Expectations are the FROZEN after-oracle literals (oracle.md / verification_after.json).
They are hard-coded here and are NOT derived from any run of the fixed function.

Everything runs from attempt-local copies.  No product file is read at run time,
nothing outside this attempt is written.
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
OUT = RUN / "command_runs" / "r2-mutation"
AFTER_REGISTRY = RUN / "iso" / "rf" / "scripts" / "model_registry.py"
EXTENSIONS = RUN / "iso" / "rf" / "scripts" / "model_extensions.py"

DEFECT1_BLOCK = '''        if driver not in drivers:
            if driver not in spec.defaults:
                raise ModelRegistryError(
                    f"missing driver for {model_id}: {driver} has no explicit default"
                )
            values: object = [spec.defaults[driver]] * len(years)
        else:
            values = drivers[driver]
'''
DEFECT1_ORIGINAL = '''        values = drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))
'''

DEFECT2_CALLSITE_NEW = (
    "    if _is_reversal_capable(driver, dimension):\n        return (-math.inf, math.inf)\n"
)
DEFECT2_CALLSITE_OLD = (
    "    if driver in _SIGNED_DRIVERS:\n        return (-math.inf, math.inf)\n"
)

GATE_LINE_NEW = (
    "    return dimension in _REVERSAL_CAPABLE_DIMENSIONS and driver in _REVERSAL_CAPABLE_DRIVERS\n"
)
GATE_LINE_OLD = "    return driver in _REVERSAL_CAPABLE_DRIVERS\n"


def mutate(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"mutation anchor not unique (count={count}): {old[:60]!r}")
    return text.replace(old, new)


def stage(name: str, registry_text: str) -> pathlib.Path:
    d = OUT / "arms" / name / "iso" / "rf" / "scripts"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    (d / "model_extensions.py").write_bytes(EXTENSIONS.read_bytes())
    (d / "model_registry.py").write_text(registry_text, encoding="utf-8")
    return d / "model_registry.py"


def load(path: pathlib.Path):
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(f"mut_{path.parent.parent.name}", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(path.parent))
    return mod


# ---------------------------------------------------------------- oracle arm
def run_oracle(m) -> list[dict]:
    """Evaluate the 7 frozen after-oracle assertions. Literals, not derived."""
    res: list[dict] = []
    MR = m.MODEL_REGISTRY
    years = [2027, 2028]

    # probe targets chosen by the SAME rule as scripts/verify_i10b.py
    target = None
    for mid, spec in MR.items():
        for d in spec.optional:
            if d not in spec.defaults:
                target = (mid, d, spec)
                break
        if target:
            break
    mid, drv, spec = target
    drivers = {r: [1.0] * len(years) for r in spec.required}

    # R-B1-N1 (negative): omitted optional-without-default must raise
    try:
        m.calculate_registered_model(mid, 100.0, drivers, years)
        got = "no raises"
    except m.ModelRegistryError:
        got = "ModelRegistryError"
    except Exception as exc:  # noqa: BLE001
        got = type(exc).__name__
    res.append({"case": "R-B1-N1", "expect": "ModelRegistryError", "actual": got,
                "ok": got == "ModelRegistryError", "kind": "negative"})

    # R-B1-N3 (positive): explicit 0.0 still accepted
    dz = dict(drivers)
    dz[drv] = [0.0] * len(years)
    try:
        m.calculate_registered_model(mid, 100.0, dz, years)
        got3 = "no raises"
    except Exception as exc:  # noqa: BLE001
        got3 = type(exc).__name__
    res.append({"case": "R-B1-N3", "expect": "no raises", "actual": got3,
                "ok": got3 == "no raises", "kind": "positive"})

    # R-B1-P1 / R-B1-P1b (positive): default-bearing omission legal and equal
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
        din = {r: [1.0] * len(years) for r in spec2.required}
        for other in spec2.optional:
            if other != drv2:
                din[other] = [1.0] * len(years)
        try:
            o2 = m.calculate_registered_model(mid2, 100.0, din, years)
            gotp = "no raises"
        except Exception as exc:  # noqa: BLE001
            gotp, o2 = type(exc).__name__, None
        res.append({"case": "R-B1-P1", "expect": "no raises", "actual": gotp,
                    "ok": gotp == "no raises", "kind": "positive"})
        din[drv2] = [dvalue] * len(years)
        try:
            o3 = m.calculate_registered_model(mid2, 100.0, din, years)
            same = (o3 == o2)
        except Exception:  # noqa: BLE001
            same = False
        res.append({"case": "R-B1-P1b", "expect": "True", "actual": repr(same),
                    "ok": same, "kind": "positive"})

    # R-B2-N1 (negative): franchise_system_sales is reversal-capable -> (-inf, inf)
    def bounds_for(driver):
        for mid3, s3 in MR.items():
            if driver in list(s3.required) + list(s3.optional):
                return mid3, m.driver_value_bounds(mid3, driver)
        return None, (None, None)

    mid_f, (lo_f, hi_f) = bounds_for("franchise_system_sales")
    n1 = lo_f == -math.inf and hi_f == math.inf
    res.append({"case": "R-B2-N1", "expect": "lower=-inf (accepted)", "actual": f"lower={lo_f}",
                "ok": n1, "kind": "negative"})

    # R-B2-P1 (positive): quantity keeps [0, inf)
    mid_q, (lo_q, hi_q) = bounds_for("closing_stores")
    res.append({"case": "R-B2-P1", "expect": "(0.0, inf)", "actual": f"({lo_q}, {hi_q})",
                "ok": (lo_q, hi_q) == (0.0, math.inf), "kind": "positive"})

    # R-B2-N2 (negative): unknown driver raises — never gains a guessed sign
    try:
        m.driver_value_bounds(next(iter(MR)), "zzz_not_a_role_driver")
        ghost = "no raises"
    except m.ModelRegistryError:
        ghost = "ModelRegistryError"
    except Exception as exc:  # noqa: BLE001
        ghost = type(exc).__name__
    res.append({"case": "R-B2-N2", "expect": "ModelRegistryError", "actual": ghost,
                "ok": ghost == "ModelRegistryError", "kind": "negative"})
    return res


ARMS = [
    ("control", None),
    ("MUT-1_revert_silent_zero", "mut1"),
    ("MUT-2_revert_name_sign", "mut2"),
    ("MUT-3_drop_dimension_gate", "mut3"),
]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    original = AFTER_REGISTRY.read_text(encoding="utf-8")

    report: dict = {"arms": {}, "verdict": {}}
    overall_ok = True
    for arm, kind in ARMS:
        if kind is None:
            text = original
        elif kind == "mut1":
            text = mutate(original, DEFECT1_BLOCK, DEFECT1_ORIGINAL)
        elif kind == "mut2":
            text = mutate(original, DEFECT2_CALLSITE_NEW, DEFECT2_CALLSITE_OLD)
            # faithful regression: restore the ORIGINAL 9-name set and remove the
            # whole semantic-role block (comment, tables, helper, alias) up to
            # the next top-level def, so nothing references the removed names.
            start = text.index("# --- I-10-B defect 2 fix (T1-22)")
            end = text.index("def driver_value_bounds")
            original_block = (
                "_SIGNED_DRIVERS = frozenset({\n"
                '    "contract_changes", "other_revenue", "fixed_revenue", "ancillary_revenue",\n'
                '    "milestone_revenue", "royalty_revenue", "service_revenue",\n'
                '    "performance_fee_revenue", "fee_revenue",\n'
                "})\n\n\n"
            )
            text = text[:start] + original_block + text[end:]
        else:
            text = mutate(original, GATE_LINE_NEW, GATE_LINE_OLD)

        p = stage(arm, text)
        changed = p.read_text(encoding="utf-8") != original
        m = load(p)
        checks = run_oracle(m)
        failed = [c for c in checks if not c["ok"]]
        killed = bool(failed)
        report["arms"][arm] = {
            "mutant_applied": changed,
            "checks": checks,
            "failed_cases": [c["case"] for c in failed],
            "killed": killed,
        }
        print(f"[{arm}] mutant_applied={changed} killed={killed} "
              f"failed_cases={[c['case'] for c in failed]}")

    report["verdict"] = {
        "control_all_pass": not report["arms"]["control"]["killed"],
        "MUT-1_killed_by": report["arms"]["MUT-1_revert_silent_zero"]["failed_cases"],
        "MUT-2_killed_by": report["arms"]["MUT-2_revert_name_sign"]["failed_cases"],
        "MUT-3_survived_equivalent_mutant": not report["arms"]["MUT-3_drop_dimension_gate"]["killed"],
        "mutation_proof_valid": (
            (not report["arms"]["control"]["killed"])
            and report["arms"]["MUT-1_revert_silent_zero"]["killed"]
            and report["arms"]["MUT-2_revert_name_sign"]["killed"]
        ),
    }
    overall_ok = report["verdict"]["mutation_proof_valid"]
    (OUT / "mutation_proof.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["verdict"], indent=1, ensure_ascii=False))
    return 0 if overall_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
