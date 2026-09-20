"""I-11-A: run both independent figure-text paths and archive the raw outputs.

P1 = tools/pdf_text.py  (pure standard library, this attempt's isolated interpreter)
P2 = pdftotext.exe      (Xpdf 4.00 bundled with Git for Windows; independent codebase)

Every invocation records argv, cwd, exit code, stdout/stderr and the sha256 of the
output file, so "the original text is readable" is a reproducible claim.

Usage:
  python -X utf8 -B tools/run_extraction.py <attempt_root> <commands_out.json> <ascii_log.txt>
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ZIJIN = (r"C:\Users\郑曾波\Projects\company-wiki\companies\紫金矿业\raw\financial_reports"
         r"\annual\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf")
XIAOMI = (r"C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports"
          r"\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf")
MSFT = (r"C:\Users\郑曾波\Projects\company-wiki\companies\MICROSOFT CORP\raw\financial_reports"
        r"\annual\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm")
PRIOR_ZIJIN = (r"C:\Users\郑曾波\Projects\revenue-forecast\audit_review"
               r"\2026-09-18_real_company_skill_audit\ZIJIN\annual_2025_selected_pages.json")
PDFTOTEXT = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"

ZIJIN_PAGES = "3,4,6,10,11,15,25,26,27,28,29,30,31,34,39,43,44,45,46,47,48,49,50,51,53,54,55,56,57,58,326,327,328,329"
ZIJIN_READABLE = "44,45,46,56,326,327,328,329,15,43,47,48"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, cwd, out_path, err_path, env=None):
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        proc = subprocess.run(cmd, cwd=cwd, stdout=out, stderr=err, env=env)
    return proc.returncode


def main() -> int:
    attempt, commands_out, ascii_log = sys.argv[1], sys.argv[2], sys.argv[3]
    ev = os.path.join(attempt, "evidence", "I-11-A", "extract")
    os.makedirs(ev, exist_ok=True)
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    tools = os.path.join(attempt, "tools")
    records = []

    def record(cid, purpose, argv, cwd, rc, expected, outputs):
        entry = {
            "id": cid,
            "purpose": purpose,
            "cwd": cwd,
            "argv": argv,
            "network": "disabled",
            "exit_code": rc,
            "expected_exit_code": expected,
            "outputs": [],
            "expected_business_result": "",
        }
        for o in outputs:
            if os.path.exists(o):
                entry["outputs"].append({"path": o, "byte_size": os.path.getsize(o),
                                         "sha256": sha256(o)})
            else:
                entry["outputs"].append({"path": o, "missing": True})
        records.append(entry)
        return entry

    # --- P1 on Zijin (own code path) ---
    p1_json = os.path.join(ev, "P1_zijin_pages.json")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "pdf_text.py"), ZIJIN,
              ZIJIN_PAGES, p1_json],
             cwd=attempt,
             out_path=os.path.join(ev, "P1_zijin.stdout.txt"),
             err_path=os.path.join(ev, "P1_zijin.stderr.txt"))
    record("I11A-01-p1-zijin", "own stdlib extractor: render the cited Zijin pages",
           [py, "-X", "utf8", "-B", os.path.join(tools, "pdf_text.py"), "CN-ZIJIN-AR2025.pdf",
            ZIJIN_PAGES, p1_json], attempt, rc, 0, [p1_json])

    # --- P1 cross-check against the prior independent extraction ---
    cc = os.path.join(ev, "P1_vs_prior_offset.json")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "page_offset_match.py"), p1_json,
              PRIOR_ZIJIN, cc],
             cwd=attempt,
             out_path=os.path.join(ev, "offset.stdout.txt"),
             err_path=os.path.join(ev, "offset.stderr.txt"))
    record("I11A-02-offset-crosscheck", "page-index offset and per-page numeric agreement between P1 and the prior independent extraction",
           [py, "-X", "utf8", "-B", os.path.join(tools, "page_offset_match.py"), "P1_zijin_pages.json",
            "PRIOR-EXTRACT-ZIJIN.json", cc], attempt, rc, 0, [cc])

    # --- P1 keyword page location for the cited statements ---
    figs = os.path.join(ev, "P1_zijin_figures.json")
    figs_txt = os.path.join(ev, "P1_zijin_figures.ascii.txt")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "zijin_figures.py"), ZIJIN, figs, figs_txt],
             cwd=attempt,
             out_path=os.path.join(ev, "figures.stdout.txt"),
             err_path=os.path.join(ev, "figures.stderr.txt"))
    record("I11A-03-locate-statements", "locate the cited Zijin statements by scanning all classic pages for anchor text",
           [py, "-X", "utf8", "-B", os.path.join(tools, "zijin_figures.py"), "CN-ZIJIN-AR2025.pdf",
            figs, figs_txt], attempt, rc, 0, [figs, figs_txt])

    # --- P2 pdftotext on Zijin (independent code path) ---
    zj_p2 = os.path.join(ev, "P2_zijin_44_48.txt")
    rc = run([PDFTOTEXT, "-f", "44", "-l", "48", "-enc", "UTF-8", ZIJIN, zj_p2], cwd=attempt,
             out_path=os.path.join(ev, "P2_zijin.stdout.txt"),
             err_path=os.path.join(ev, "P2_zijin.stderr.txt"))
    record("I11A-04-p2-zijin", "Xpdf pdftotext: independent second path over the same raw bytes",
           [PDFTOTEXT, "-f", "44", "-l", "48", "-enc", "UTF-8", "CN-ZIJIN-AR2025.pdf", zj_p2],
           attempt, rc, 0, [zj_p2])

    # --- P2 pdftotext on Xiaomi (readability test for the HK source) ---
    xm_p2 = os.path.join(ev, "P2_xiaomi_probe.txt")
    rc = run([PDFTOTEXT, "-f", "1", "-l", "12", "-enc", "UTF-8", XIAOMI, xm_p2], cwd=attempt,
             out_path=os.path.join(ev, "P2_xiaomi.stdout.txt"),
             err_path=os.path.join(ev, "P2_xiaomi.stderr.txt"))
    record("I11A-05-p2-xiaomi-probe", "readability probe for the HK source with the independent path",
           [PDFTOTEXT, "-f", "1", "-l", "12", "-enc", "UTF-8", "HK-XIAOMI-AR2025.pdf", xm_p2],
           attempt, rc, 0, [xm_p2])
    # P1 readability probe on Xiaomi (ObjStm-only document)
    xm_p1 = os.path.join(ev, "P1_xiaomi_probe.json")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "pdf_text.py"), XIAOMI, "1,2,3", xm_p1],
             cwd=attempt,
             out_path=os.path.join(ev, "P1_xiaomi.stdout.txt"),
             err_path=os.path.join(ev, "P1_xiaomi.stderr.txt"))
    record("I11A-06-p1-xiaomi-probe", "readability probe for the HK source with the stdlib path",
           [py, "-X", "utf8", "-B", os.path.join(tools, "pdf_text.py"), "HK-XIAOMI-AR2025.pdf",
            "1,2,3", xm_p1], attempt, rc, 0, [xm_p1])

    # --- US: HTML tables (no PDF path applies) ---
    msft_json = os.path.join(ev, "P1_msft_tables.json")
    msft_txt = os.path.join(ev, "P1_msft_tables.ascii.txt")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "msft_figures.py"), MSFT, msft_json, msft_txt],
             cwd=attempt,
             out_path=os.path.join(ev, "msft.stdout.txt"),
             err_path=os.path.join(ev, "msft.stderr.txt"))
    record("I11A-07-msft-tables", "parse the MSFT 10-K segment and product revenue tables with the stdlib HTML parser",
           [py, "-X", "utf8", "-B", os.path.join(tools, "msft_figures.py"), "US-MSFT-10K-FY2026.htm",
            msft_json, msft_txt], attempt, rc, 0, [msft_json, msft_txt])
    msft_scan = os.path.join(ev, "P1_msft_scan.ascii.txt")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "msft_scan_tables.py"), MSFT, msft_scan],
             cwd=attempt,
             out_path=os.path.join(ev, "msft_scan.stdout.txt"),
             err_path=os.path.join(ev, "msft_scan.stderr.txt"))
    record("I11A-08-msft-scan", "scan all 88 parsed MSFT tables for the revenue disaggregation rows",
           [py, "-X", "utf8", "-B", os.path.join(tools, "msft_scan_tables.py"), "US-MSFT-10K-FY2026.htm",
            msft_scan], attempt, rc, 0, [msft_scan])

    # --- arithmetic oracle (exact rationals) ---
    arith = os.path.join(ev, "arithmetic_oracle.json")
    rc = run([py, "-X", "utf8", "-B", os.path.join(tools, "verify_arithmetic.py"), arith],
             cwd=attempt,
             out_path=os.path.join(ev, "arithmetic.stdout.txt"),
             err_path=os.path.join(ev, "arithmetic.stderr.txt"))
    record("I11A-09-arithmetic-oracle", "recompute the frozen arithmetic identities A1-A7 with exact rationals",
           [py, "-X", "utf8", "-B", os.path.join(tools, "verify_arithmetic.py"), arith],
           attempt, rc, 0, [arith])

    with open(commands_out, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    lines = ["%s rc=%d expected=%d" % (r["id"], r["exit_code"], r["expected_exit_code"])
             for r in records]
    with open(ascii_log, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("wrote", commands_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
