"""I14A-C1C2-ERRATUM mutation driver (arms M1-M4, oracle.md §6).

Each arm runs exactly one frozen case through the SAME independent checker
(``harness/run_probe_cases.py:verify_case``) that produces the card's verdicts,
so a mutation arm can only go green/red through the frozen expectations.

  m1  no sampling            E0 + ``--rss-sampler none`` (the unmodified probe)
  m2  launcher-only pids     E1c with a probe whose process-tree walk is removed
  m3  long-lived F4 + probe  E0 with the sleeping fixture AND the launcher-only probe
  m4  long-lived F4 control  E0 with the sleeping fixture and the UNMODIFIED probe

Exit code: 0 = arm green, 1 = arm red (both outcomes are evidence; nothing here
fabricates a result).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
HARNESS = ATTEMPT / "harness"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SPEC = _load("fixture_spec", HARNESS / "fixture_spec.py")
RUNNER = _load("run_probe_cases", HARNESS / "run_probe_cases.py")

BASE_TOOL = ATTEMPT / "iso" / "slo_probe_patched.py"
LAUNCHER_ONLY_TOOL = ATTEMPT / "mutations" / "probe_launcher_only_patched.py"
SLEEP_F4 = ATTEMPT / "mutations" / "fixtures" / "instant_exit_sleep04.py"


def main() -> int:
    ap = argparse.ArgumentParser(description="I14A-C1C2-ERRATUM mutation arms")
    ap.add_argument("--arm", required=True, choices=["m1", "m2", "m3", "m4"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tool = BASE_TOOL
    case = "E0-baseline-F4"
    mutation = "none"

    # IMPORTANT: the checker module loads its OWN copy of fixture_spec, so every
    # spec-level mutation must be applied to RUNNER.SPEC (the instance the checker
    # actually reads).  Patching the local SPEC here is a no-op — the first run of
    # this driver made exactly that mistake and is kept, unedited, under
    # evidence/mutations/<arm>/run1_driver_bug/ as a disclosed false-green.
    TARGET = RUNNER.SPEC

    if args.arm == "m1":
        mutation = "sampler disabled (no sampling at all)"
        TARGET.CASES[case]["extra_argv"] = ["--rss-sampler", "none"]
    elif args.arm == "m2":
        mutation = "probe process-tree walk removed (launcher pid only)"
        tool = LAUNCHER_ONLY_TOOL
        case = "E1c-F3-alive-allocate"
    elif args.arm == "m3":
        mutation = "F4 lifetime 0.4 s + probe process-tree walk removed"
        tool = LAUNCHER_ONLY_TOOL
        TARGET.FIXTURE_SCRIPTS["F4"] = SLEEP_F4
    elif args.arm == "m4":
        mutation = "F4 lifetime 0.4 s (control: unmodified probe)"
        TARGET.FIXTURE_SCRIPTS["F4"] = SLEEP_F4

    out_dir = Path(args.out) / case
    result = RUNNER.run_case(Path(tool), out_dir, case, None)
    verdict = result["verdict"]
    payload = {
        "arm": args.arm,
        "mutation": mutation,
        "tool": str(tool),
        "tool_sha256": __import__("hashlib").sha256(Path(tool).read_bytes()).hexdigest(),
        "fixture_script": str(TARGET.FIXTURE_SCRIPTS[TARGET.CASES[case]["fixture"]]),
        "case": case,
        "probe_raw_returncode": result["raw_returncode"],
        "runner_all_ok": verdict["all_ok"],
        "failed_checks": verdict["failed_checks"],
        "checks": verdict["checks"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if verdict["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
