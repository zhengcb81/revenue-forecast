#!/usr/bin/env python3
"""live_round2.py — round-2 live scan under oracle CORRECTION 1 + old/new diff.

Reads the round-1 detections (evidence/live/live_scan.json, untouched), runs the
corrected checker on the three plan carriers (read-only), and writes:
  evidence/live/round2_live_scan.json   (raw corrected-checker --json stdout)
  evidence/live/round2_live_scan.txt    (raw corrected-checker text stdout)
  evidence/live/round2_diff.txt         (disappeared/cause, remained, new)
  evidence/live/round2_summary.json     (counts)

Cause labels for disappeared lines: D8 / D9 / D10a / file-drift / unexplained.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
PLAN = ATTEMPT.parents[2]
PY = sys.executable or "python"

# round-1 (pre-CORRECTION) lexicon, replicated here for cause labelling only
OLD_EN = [
    r"(?<![A-Za-z])only(?![A-Za-z])",
    r"(?<![A-Za-z])all(?![A-Za-z])",
    r"(?<![A-Za-z])none(?![A-Za-z])",
    r"(?<![A-Za-z])every(?![A-Za-z])",
    r"(?<![A-Za-z])whole family(?![A-Za-z])",
    r"(?<![A-Za-z])zero cost(?![A-Za-z])",
]
OLD_CJK = ["只有", "全部", "没有", "整个族", "零代价", "无一", "每一个"]
OLD_DOM = [
    r"域", r"(?i)domain\s*[:=]", r"在[^。；;\n]{1,40}上", r"\d+\s*个",
    r"(?i)\d+\s*(?:cases?|rows?|probes?|characters|chars?|entries|lines?|files?"
    r"|cards|tests|runs?|trees|forms?|instances|samples|words?|tokens?|bytes"
    r"|sites|revisions?|rounds?)(?![A-Za-z])",
    r"×\s*\d+", r"(?<![A-Za-z])N\s*=\s*\d+",
]

TARGETS = ["task_plan.md", "findings.md", "progress.md"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_corrected_module():
    path = ATTEMPT / "tools/check_domain_assertions.py"
    spec = importlib.util.spec_from_file_location("chk", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    live = ATTEMPT / "evidence/live"

    # ---- round-1 reference (raw, untouched) --------------------------------
    r1 = json.loads((live / "live_scan.json").read_text(encoding="utf-8"))
    r1_map = {
        (e["path"], v["line"]): v
        for e in r1["files"]
        for v in e["violations"]
    }
    # resolve relative path -> plan file for hashing + line-text reads
    def plan_rel(display_path):
        name = Path(display_path).name
        return PLAN / name

    hashes_now = {n: sha(PLAN / n) for n in TARGETS}
    manifest = json.loads(
        (ATTEMPT / "evidence/corpus_manifest.json").read_text(encoding="utf-8")
    )
    hashes_extract = {
        Path(k).name: v["sha256_at_extraction"]
        for k, v in manifest["source_files"].items()
        if Path(k).name in TARGETS
    }

    # ---- round-2 scan with the corrected checker ---------------------------
    import os
    child_env = dict(os.environ)
    child_env["PYTHONUTF8"] = "1"  # Windows pipes default to ANSI; CJK stdout needs UTF-8
    cmd = [PY, "-B", str(ATTEMPT / "tools/check_domain_assertions.py"), "--json",
           *[str(PLAN / n) for n in TARGETS]]
    proc = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", cwd=str(ATTEMPT), env=child_env)
    (live / "round2_live_scan.json").write_bytes(proc.stdout.encode("utf-8"))
    cmd_txt = [PY, "-B", str(ATTEMPT / "tools/check_domain_assertions.py"),
               *[str(PLAN / n) for n in TARGETS]]
    proc_txt = subprocess.run(cmd_txt, capture_output=True, encoding="utf-8",
                              errors="replace", cwd=str(ATTEMPT), env=child_env)
    (live / "round2_live_scan.txt").write_bytes(proc_txt.stdout.encode("utf-8"))
    if proc.returncode not in (0, 1):
        print(f"FATAL: checker rc={proc.returncode}: {proc.stderr}", file=sys.stderr)
        return 2
    r2 = json.loads(proc.stdout)
    r2_map = {
        (Path(e["path"]).name, v["line"]): v
        for e in r2["files"]
        for v in e["violations"]
    }

    # round-1 keys normalised to bare file names
    r1_norm = {(Path(k[0]).name, k[1]): v for k, v in r1_map.items()}

    chk = load_corrected_module()

    def old_markers(text):
        hits = [p for p in OLD_CJK if p in text]
        hits += [p for p in OLD_EN if re.search(p, text, re.I)]
        return hits

    def old_domain(text):
        return any(re.search(p, text) for p in OLD_DOM)

    disappeared, remained = [], []
    for key, v in sorted(r1_norm.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        name, lineno = key
        if key in r2_map:
            remained.append((key, r2_map[key]))
            continue
        try:
            lines = (PLAN / name).read_bytes().decode("utf-8", errors="replace").split("\n")
            text = lines[lineno - 1]
        except Exception:
            text = None
        if text is None:
            cause = "unreadable"
        elif not old_markers(text):
            cause = "file-drift (round-1 marker no longer on that line)"
        elif old_domain(text):
            cause = "file-drift (line gained an old-lexicon domain)"
        else:
            new_mk = chk.find_markers(text)
            dom = chk.find_domains(text)
            if not new_mk:
                cause = "D10a (identifier/underscore boundary — marker dropped)"
            elif "D8" in dom:
                cause = "D8 (same-line numeral+classifier count)"
            elif "D9" in dom:
                cause = "D9 (subject/enumeration qualifier)"
            elif dom:
                cause = f"domain {dom} (unexpected pre-existing)"
            else:
                cause = "unexplained (needs owner review)"
        disappeared.append((key, v, cause))

    new_keys = sorted(set(r2_map) - set(r1_norm))

    # ---- diff file ---------------------------------------------------------
    out = []
    out.append("# round2_diff.txt — round-1 (214 detections) vs round-2 under oracle CORRECTION 1")
    out.append(f"# plan hashes at diff time   : " + json.dumps(hashes_now, ensure_ascii=False))
    out.append(f"# plan hashes at corpus extract: " + json.dumps(hashes_extract, ensure_ascii=False))
    out.append(f"# identical={hashes_now == hashes_extract} (drift would taint cause labels)")
    out.append("")
    out.append("## SUMMARY")
    out.append(f"round1={len(r1_norm)} round2={len(r2_map)} disappeared={len(disappeared)} "
               f"remained={len(remained)} new={len(new_keys)}")
    cause_hist = {}
    for item in disappeared:
        cause = item[2] if len(item) == 3 else "?"
        cause_hist[cause] = cause_hist.get(cause, 0) + 1
    out.append("disappeared-by-cause: " + json.dumps(cause_hist, ensure_ascii=False))
    out.append("")
    out.append("## DISAPPEARED (cleared by CORRECTION 1)")
    for item in disappeared:
        key, v = item[0], item[1]
        cause = item[2] if len(item) == 3 else "?"
        out.append(f"{key[0]}:{key[1]} [{cause}] markers=[{','.join(v['markers'])}] "
                   f"{v['excerpt'][:100]}")
    out.append("")
    out.append("## REMAINED (narrowed candidate set for owner re-adjudication)")
    for key, v in sorted(remained, key=lambda kv: (kv[0][0], kv[0][1])):
        out.append(f"{key[0]}:{key[1]}:[{','.join(v['markers'])}] {v['excerpt'][:110]}")
    out.append("")
    out.append("## NEW (must be empty: corrections only shrink the violation set)")
    for key in new_keys:
        v = r2_map[key]
        out.append(f"{key[0]}:{key[1]}:[{','.join(v['markers'])}] {v['excerpt'][:110]}")
    (live / "round2_diff.txt").write_text("\n".join(out) + "\n", encoding="utf-8")

    summary = {
        "round1_total": len(r1_norm),
        "round2_total": len(r2_map),
        "disappeared": len(disappeared),
        "remained": len(remained),
        "new": len(new_keys),
        "disappeared_by_cause": cause_hist,
        "per_file_round2": {
            Path(e["path"]).name: len(e["violations"]) for e in r2["files"]
        },
        "plan_hashes_unchanged_since_extraction": hashes_now == hashes_extract,
        "checker_version": chk.VERSION,
    }
    (live / "round2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
