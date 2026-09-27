"""DEF-I00C-GATE-NEG mutation testing (oracle §三.4): each mutation disables
exactly one check of the fix in a throwaway copy of the uc package and must
flip at least one negative from REJECTED to PASSTHROUGH — proving the frozen
criteria have killing power.  Production files are never touched.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
UC_SRC = pathlib.Path(r"C:\Users\郑曾波\Projects\revenue-forecast\assurance\unified_completion")
PROD_UC_ROOT = UC_SRC

SCEN = (HERE / "post_image" / "scenarios.py").read_text(encoding="utf-8")
CLOS = (HERE / "post_image" / "closure.py").read_text(encoding="utf-8")

M_EVIDENCE = '''    if not info.get("evidence_path"):
        problems.append("passed without evidence_path")
    if not info.get("fixture_hash"):
        problems.append("passed without fixture_hash")
'''

M_CAPABILITY = '''    required = info.get("required_capability")
    if required and required not in (info.get("covered_capabilities") or []):
        problems.append(
            f"required capability {required!r} not covered by evidence "
            f"(covered={info.get('covered_capabilities') or []})"
        )
'''

M_ORACLE = '''    oracle = info.get("oracle")
    if isinstance(oracle, dict):
        commands = oracle.get("validated_commands")
        invariants = oracle.get("invariants")
        if commands is not None and not commands:
            problems.append("oracle validated_commands is empty")
        if invariants is not None and not invariants:
            problems.append("oracle invariants is empty")
    elif isinstance(oracle, str) and not oracle.strip():
        problems.append("oracle is empty")
'''

M_NARROW = '''    # DEF-I00C-GATE-NEG (N6b): a narrowed successor card must be flagged and
    # must never silently satisfy the original (wider) obligation.
    narrowed = [
        row["fc_id"]
        for row in legacy.get("fc_entries", [])
        if str(row.get("fc_id", "")).endswith("-narrow")
    ]
    if narrowed:
        reasons.append(
            f"{len(narrowed)} narrowed successor card(s) flagged, not accepted "
            f"as substitutes: {narrowed} — original obligations stay pending "
            "until closed on their own scope"
        )
'''

MUTATIONS = [
    ("M1_drop_evidence_checks", "scenarios.py", M_EVIDENCE, "N1_all_passed_but_no_evidence"),
    ("M2_drop_capability_check", "scenarios.py", M_CAPABILITY, "N2_read10_wrong_capability_evidence"),
    ("M3_drop_oracle_emptiness", "scenarios.py", M_ORACLE, "N4_empty_commands"),
    ("M4_drop_narrow_flag", "closure.py", M_NARROW, "N6b_narrowed_successor_flagged"),
]

env = {**os.environ, "PYTHONUTF8": "1"}
report = []
all_killed = True

tmp = HERE / "tmp"
tmp.mkdir(exist_ok=True)

for name, target, block, expected_flip in MUTATIONS:
    assert block in (SCEN if target == "scenarios.py" else CLOS), f"{name}: mutation block not found"
    mut_root = tmp / f"mut_{name}"
    if mut_root.exists():
        shutil.rmtree(mut_root)
    shutil.copytree(UC_SRC / "uc", mut_root / "uc", ignore=shutil.ignore_patterns("__pycache__"))
    base = SCEN if target == "scenarios.py" else CLOS
    mutated = base.replace(block, "", 1)
    assert mutated != base
    (mut_root / "uc" / target).write_text(mutated, encoding="utf-8")
    r = subprocess.run(
        ["python", str(HERE / "run_nine_negatives.py"), "--uc-root", str(mut_root)],
        capture_output=True,
        env=env,
    )
    out = r.stdout.decode("utf-8")
    j = json.loads(out)
    flipped = [x["case"] for x in j["results"] if x["case"].startswith("N") and not x["rejected"]]
    killed = expected_flip in flipped and r.returncode == 3
    all_killed = all_killed and killed
    report.append(
        {
            "mutation": name,
            "file": target,
            "expected_flip": expected_flip,
            "killed": killed,
            "mutant_exit": r.returncode,
            "negatives_passthrough": flipped,
            "mutant_scenarios_py_sha256": j["combination"]["scenarios_py_sha256"],
            "mutant_closure_py_sha256": j["combination"]["closure_py_sha256"],
        }
    )
    print(name, "-> killed", killed, "| passthrough", flipped, "| exit", r.returncode)

(HERE / "mutation_results.json").write_text(
    json.dumps(
        {
            "mutation_count": len(report),
            "all_mutants_killed": all_killed,
            "production_files_touched": False,
            "mutations": report,
        },
        ensure_ascii=False,
        indent=1,
    ),
    encoding="utf-8",
)
sys.exit(0 if all_killed else 4)
