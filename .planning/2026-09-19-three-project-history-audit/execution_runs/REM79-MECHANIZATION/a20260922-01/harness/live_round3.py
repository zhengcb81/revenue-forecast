#!/usr/bin/env python3
"""live_round3.py — round-3 live scan under oracle CORRECTION 2 + full old/new diff.

Baselines: round-1 JSON (214 detections) and round-2 JSON (48 residuals).
Runs the v1.2.0-correction2 checker on the three plan carriers (read-only) and
writes:
  evidence/live/round3_live_scan.json / .txt   (raw checker outputs)
  evidence/live/round3_diff.txt                (cause-labelled disposition)
  evidence/live/round3_summary.json
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
PLAN = ATTEMPT.parents[2]
PY = sys.executable or "python"
TARGETS = ["task_plan.md", "findings.md", "progress.md"]

# round-1 (pre-CORRECTION) lexicon, replicated for cause labelling
OLD_EN = [
    r"(?<![A-Za-z])only(?![A-Za-z])", r"(?<![A-Za-z])all(?![A-Za-z])",
    r"(?<![A-Za-z])none(?![A-Za-z])", r"(?<![A-Za-z])every(?![A-Za-z])",
    r"(?<![A-Za-z])whole family(?![A-Za-z])", r"(?<![A-Za-z])zero cost(?![A-Za-z])",
]
OLD_CJK = ["只有", "全部", "没有", "整个族", "零代价", "无一", "每一个"]
OLD_DOM = [
    r"域", r"(?i)domain\s*[:=]", r"在[^。；;\n]{1,40}上", r"\d+\s*个",
    r"(?i)\d+\s*(?:cases?|rows?|probes?|characters|chars?|entries|lines?|files?"
    r"|cards|tests|runs?|trees|forms?|instances|samples|words?|tokens?|bytes"
    r"|sites|revisions?|rounds?)(?![A-Za-z])",
    r"×\s*\d+", r"(?<![A-Za-z])N\s*=\s*\d+",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_module():
    path = ATTEMPT / "tools/check_domain_assertions.py"
    spec = importlib.util.spec_from_file_location("chk3", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    live = ATTEMPT / "evidence/live"
    r1 = json.loads((live / "live_scan.json").read_text(encoding="utf-8"))
    r2 = json.loads((live / "round2_live_scan.json").read_text(encoding="utf-8"))
    r1_set = {(Path(e["path"]).name, v["line"]): v for e in r1["files"] for v in e["violations"]}
    r2_set = {(Path(e["path"]).name, v["line"]): v for e in r2["files"] for v in e["violations"]}

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    cmd = [PY, "-B", str(ATTEMPT / "tools/check_domain_assertions.py"), "--json",
           *[str(PLAN / n) for n in TARGETS]]
    proc = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", cwd=str(ATTEMPT), env=env)
    (live / "round3_live_scan.json").write_bytes(proc.stdout.encode("utf-8"))
    cmd_txt = [PY, "-B", str(ATTEMPT / "tools/check_domain_assertions.py"),
               *[str(PLAN / n) for n in TARGETS]]
    proc_txt = subprocess.run(cmd_txt, capture_output=True, encoding="utf-8",
                              errors="replace", cwd=str(ATTEMPT), env=env)
    (live / "round3_live_scan.txt").write_bytes(proc_txt.stdout.encode("utf-8"))
    if proc.returncode not in (0, 1):
        print(f"FATAL checker rc={proc.returncode}: {proc.stderr}", file=sys.stderr)
        return 2
    r3 = json.loads(proc.stdout)
    r3_set = {(Path(e["path"]).name, v["line"]): v for e in r3["files"] for v in e["violations"]}

    chk = load_module()

    def old_markers(text):
        return [p for p in OLD_CJK if p in text] + [
            p for p in OLD_EN if re.search(p, text, re.I)]

    def read_line(name, lineno):
        try:
            return (PLAN / name).read_bytes().decode(
                "utf-8", errors="replace").split("\n")[lineno - 1]
        except Exception:
            return None

    cleared, remained = [], []
    for key in sorted(r1_set, key=lambda k: (k[0], k[1])):
        if key in r3_set:
            remained.append((key, r3_set[key]))
            continue
        name, lineno = key
        text = read_line(name, lineno)
        in_r2 = key in r2_set
        if text is None:
            cause = "unreadable"
        elif not old_markers(text):
            cause = "file-drift (round-1 marker no longer on that line)"
        else:
            cur = chk.find_markers(text)
            dom = chk.find_domains(text)
            if not cur:
                cause = "C2 marker-skip (D10b hyphen/code-call or D11 quote)" if in_r2 \
                    else "C1 marker-drop or drift"
            elif not in_r2:
                cause = "C1 " + (
                    "D8" if "D8" in dom else "D9" if "D9" in dom else
                    "D10a" if not cur else f"domain {dom}")
            elif "D8b" in dom:
                cause = "C2 D8b"
            elif dom:
                cause = f"C2 domain {dom}"
            else:
                cause = "unexplained (needs owner ruling)"
        cleared.append((key, r1_set[key], cause, in_r2))

    new_vs_r1 = sorted(set(r3_set) - set(r1_set))
    # disposition of the round-2 48
    r2_cleared = [k for k in r2_set if k not in r3_set]
    r2_remain = [k for k in r2_set if k in r3_set]

    hashes_now = {n: sha(PLAN / n) for n in TARGETS}
    manifest = json.loads((ATTEMPT / "evidence/corpus_manifest.json").read_text(encoding="utf-8"))
    hashes_extract = {Path(k).name: v["sha256_at_extraction"]
                      for k, v in manifest["source_files"].items() if Path(k).name in TARGETS}

    cause_hist = {}
    for item in cleared:
        cause_hist[item[2]] = cause_hist.get(item[2], 0) + 1

    out = []
    out.append("# round3_diff.txt — round-1 (214) and round-2 (48) vs round-3 under oracle CORRECTION 2")
    out.append("# plan hashes now: " + json.dumps(hashes_now, ensure_ascii=False))
    out.append("# plan hashes at corpus extract: " + json.dumps(hashes_extract, ensure_ascii=False))
    out.append(f"# identical_to_extraction={hashes_now == hashes_extract} (drift would taint cause labels)")
    out.append("")
    out.append("## SUMMARY")
    out.append(f"round1={len(r1_set)} round2={len(r2_set)} round3={len(r3_set)} "
               f"cleared_since_r1={len(cleared)} remained_since_r1={len(remained)} "
               f"new_vs_r1={len(new_vs_r1)}")
    out.append(f"round2 disposition: cleared_by_C2={len(r2_cleared)} still_flagged={len(r2_remain)}")
    out.append("cleared-by-cause: " + json.dumps(cause_hist, ensure_ascii=False))
    out.append("")
    out.append("## ROUND-2 RESIDUAL DISPOSITION (the 48 the parent adjudicated)")
    for key in sorted(r2_set, key=lambda k: (k[0], k[1])):
        state = "STILL-FLAGGED" if key in r3_set else "cleared-by-C2"
        v = r3_set.get(key, r2_set[key])
        out.append(f"{state} {key[0]}:{key[1]}:[{','.join(v['markers'])}] {v['excerpt'][:100]}")
    out.append("")
    out.append("## CLEARED since round-1 (cause-labelled)")
    for item in cleared:
        key, v, cause = item[0], item[1], item[2]
        out.append(f"{key[0]}:{key[1]} [{cause}] markers=[{','.join(v['markers'])}] {v['excerpt'][:90]}")
    out.append("")
    out.append("## REMAINED since round-1 (residual list for owner item-by-item ruling)")
    for key, v in sorted(remained, key=lambda kv: (kv[0][0], kv[0][1])):
        out.append(f"{key[0]}:{key[1]}:[{','.join(v['markers'])}] {v['excerpt'][:110]}")
    out.append("")
    out.append("## NEW vs round-1 (expect none on byte-stable files; drift noted above)")
    for key in new_vs_r1:
        v = r3_set[key]
        out.append(f"{key[0]}:{key[1]}:[{','.join(v['markers'])}] {v['excerpt'][:110]}")
    (live / "round3_diff.txt").write_text("\n".join(out) + "\n", encoding="utf-8")

    summary = {
        "round1_total": len(r1_set), "round2_total": len(r2_set),
        "round3_total": len(r3_set),
        "cleared_since_r1": len(cleared), "remained_since_r1": len(remained),
        "new_vs_r1": len(new_vs_r1),
        "round2_cleared_by_c2": len(r2_cleared), "round2_still_flagged": len(r2_remain),
        "cleared_by_cause": cause_hist,
        "per_file_round3": {Path(e["path"]).name: len(e["violations"])
                            for e in r3["files"]},
        "per_file_round2": {Path(e["path"]).name: len(e["violations"])
                            for e in r2["files"]},
        "plan_hashes_unchanged_since_extraction": hashes_now == hashes_extract,
        "checker_version": chk.VERSION,
        "correction3_opened": False,
    }
    (live / "round3_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
