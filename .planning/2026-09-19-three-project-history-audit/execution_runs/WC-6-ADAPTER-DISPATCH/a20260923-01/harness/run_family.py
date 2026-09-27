"""WC-6 regression family runner: pytest over the mechanically selected family,
capturing raw rc, full output and a per-test outcome list (junit-xml based).

  python run_family.py <label> [--cwd iso|live]

<label> e.g. fam_before / fam_after / fam_live_before.
--cwd iso   -> cwd = <attempt>/iso/cw   (tests import <attempt>/iso/cw/src)
--cwd live  -> cwd = live CW            (READ-ONLY witness run; -B + no cache)
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from wc6_common import ATT, CW, EVID, ISO_CW, write_json


def main() -> int:
    argv = sys.argv[1:]
    label = argv[0]
    cwd_mode = "iso"
    if "--cwd" in argv:
        cwd_mode = argv[argv.index("--cwd") + 1]
    cwd = ISO_CW if cwd_mode == "iso" else CW

    fam = json.loads((EVID / "family_files.json").read_text(encoding="utf-8"))
    rels = sorted(fam["files"])
    missing = [r for r in rels if not (cwd / r).is_file()]
    if missing:
        print(json.dumps({"fatal": "family file missing in run tree",
                          "missing": missing}), file=sys.stderr)
        return 2

    xml_path = EVID / f"{label}_family.xml"
    if xml_path.is_file():
        xml_path.unlink()
    pytest_argv = [sys.executable, "-X", "utf8", "-B", "-m", "pytest",
                   "-q", "-p", "no:cacheprovider", "--no-header",
                   f"--junitxml={xml_path}"] + rels

    import os
    import subprocess
    import time
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env.setdefault("PYTHONPATH", str((cwd / "src")))
    started = time.time()
    proc = subprocess.run(pytest_argv, cwd=str(cwd), env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=3000)
    elapsed = round(time.time() - started, 3)
    out_txt = EVID / f"{label}_family.txt"
    out_txt.write_text(
        f"# cwd={cwd}\n# argv={' '.join(pytest_argv)}\n"
        f"# raw_rc={proc.returncode} elapsed_seconds={elapsed}\n"
        f"=== stdout ===\n{proc.stdout}\n=== stderr ===\n{proc.stderr}\n",
        encoding="utf-8")

    outcomes = []
    summary = {}
    if xml_path.is_file():
        tree = ET.parse(xml_path)
        for case in tree.getroot().iter("testcase"):
            status = "passed"
            if case.find("skipped") is not None:
                status = "skipped"
            elif case.find("failure") is not None:
                status = "failed"
            elif case.find("error") is not None:
                status = "error"
            elif case.find("rerun") is not None:
                status = "rerun"
            outcomes.append({
                "id": (case.get("classname") or "") + "::" + (case.get("name") or ""),
                "status": status,
            })
        outcomes.sort(key=lambda o: o["id"])
        for o in outcomes:
            summary[o["status"]] = summary.get(o["status"], 0) + 1

    write_json(EVID / f"{label}_family_outcomes.json",
               {"label": label, "cwd": str(cwd), "cwd_mode": cwd_mode,
                "argv": pytest_argv, "raw_rc": proc.returncode,
                "elapsed_seconds": elapsed, "summary": summary,
                "outcome_count": len(outcomes), "outcomes": outcomes})
    print(json.dumps({"label": label, "cwd_mode": cwd_mode,
                      "raw_rc": proc.returncode, "summary": summary,
                      "outcome_count": len(outcomes), "elapsed_seconds": elapsed}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
