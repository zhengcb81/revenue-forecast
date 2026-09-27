#!/usr/bin/env python3
"""E1f honesty probe: is the station's OWN pdfminer re-extraction byte-stable?

Runs the extraction in separate OS processes (fresh PYTHONHASHSEED each time),
records every sha256 seen, and re-checks that the frozen verbatim quotes of
attempt08 are still found in each extraction. Writes _work/s5_extract_determinism.json.
Read-only against prior stations.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PLAN = Path(".planning/2026-09-19-three-project-history-audit")
RUNS = PLAN / "execution_runs"
PEND5A = RUNS / "OPEN5-PEND5A-HK-ACQUISITION/a20260924-01"
OUT = RUNS / "OPEN5-S5-ACCT-GRADING/a20260926-01"
WORK = OUT / "_work"
PDF_DEFAULT = PEND5A / "corpus/attempt08_irmi_xiaomi_ar2025_en.pdf"
EXT_DEFAULT = "ext-08"

CHILD = r'''
import hashlib, re, sys
from pdfminer.high_level import extract_text
from pathlib import Path
pdf = Path(sys.argv[1])
text = extract_text(str(pdf))
data = text.encode("utf-8")
norm_data = re.sub(r"\s+", "", text)
print("SHA " + hashlib.sha256(data).hexdigest())
sys.stdout.write("RAW " + ",".join(
    str(int(q.encode("utf-8") in data)) for q in sys.argv[2:]) + "\n")
sys.stdout.write("NORM " + ",".join(
    str(int(re.sub(r"\s+", "", q) in norm_data)) for q in sys.argv[2:]) + "\n")
'''


def main() -> int:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else PDF_DEFAULT
    ext_id = sys.argv[2] if len(sys.argv) > 2 else EXT_DEFAULT
    tag = sys.argv[3] if len(sys.argv) > 3 else ext_id
    quotes = []
    with open(PEND5A / "provenance.json", "r", encoding="utf-8") as fh:
        prov = json.load(fh)
    for q in prov["verbatim_quotes"]:
        if q["external_evidence_id"] == ext_id:
            quotes.append(q["text"])

    n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    runs = []
    for i in range(n):
        r = subprocess.run([sys.executable, "-c", CHILD, str(pdf)] + quotes,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        sha = raw = norm = None
        for line in r.stdout.splitlines():
            if line.startswith("SHA "):
                sha = line[4:]
            elif line.startswith("RAW "):
                raw = [h == "1" for h in line[4:].split(",")]
            elif line.startswith("NORM "):
                norm = [h == "1" for h in line[5:].split(",")]
        runs.append({"run": i, "sha256": sha,
                     "quotes_found_raw": raw,
                     "quotes_found_whitespace_normalized": norm,
                     "rc": r.returncode,
                     "stderr_head": (r.stderr or "")[:300]})

    shas = sorted({r["sha256"] for r in runs})
    out = {
        "purpose": "E1f（至少一条独立复核路径）的自我加严检查：本工位自抽工件是否字节稳定",
        "pdf": str(pdf),
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "external_evidence_id": ext_id,
        "engine": "pdfminer.six extract_text（独立进程 ×%d）" % n,
        "runs": runs,
        "distinct_shas": len(shas),
        "byte_stable": len(shas) == 1,
        "all_quotes_found_all_runs_raw": all(
            all(r["quotes_found_raw"] or []) for r in runs),
        "all_quotes_found_all_runs_whitespace_normalized": all(
            all(r["quotes_found_whitespace_normalized"] or []) for r in runs),
        "match_rule_note": (
            "s5_grade.py 的 E1f 命中判定用 whitespace 归一化（PDF 抽取器换行/空格不同），"
            "raw 为更严口径；两种口径都登记在此"),
        "interpretation": (
            "本探针只对 pdfminer 自抽文本做命中判定；s5_grade.py 的逐引文命中是按引文载体引擎配对的"
            "（fitz 引文对 fitz 自抽、pdfminer 引文对 pdfminer 自抽），权威结果在 "
            "s5_measure_*.json 的 quote_checks。sha 稳定 ⇒ 工件字节可复现；sha 不稳定但归一化引文仍全命中 ⇒ "
            "E1f 锚定「同一引文在自抽文本中命中」，不以工件字节全等为条件；E1d 的 sha256 针对 PDF 本体，不受影响"),
    }
    path = WORK / ("s5_extract_determinism_%s.json" % tag)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(path, "r", encoding="utf-8") as fh:
        json.load(fh)
    print(json.dumps({"tag": tag, "distinct_shas": len(shas),
                      "byte_stable": out["byte_stable"],
                      "raw": out["all_quotes_found_all_runs_raw"],
                      "normalized": out["all_quotes_found_all_runs_whitespace_normalized"],
                      "shas": shas}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
