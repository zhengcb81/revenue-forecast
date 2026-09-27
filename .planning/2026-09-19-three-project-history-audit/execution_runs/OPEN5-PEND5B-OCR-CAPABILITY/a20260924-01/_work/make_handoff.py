"""Emit handoff.json for OPEN5-PEND5B-OCR-CAPABILITY (a20260924-01)."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def meta(rel: str) -> dict:
    p = os.path.join(ATTEMPT, rel)
    return {"path": rel, "bytes": os.path.getsize(p), "sha256": sha256_file(p)}


def load(rel: str):
    with open(os.path.join(ATTEMPT, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    prov = load("provenance.json")
    agg = load(os.path.join("_work", "hk_probe_aggregate.json"))
    receipts = load(os.path.join("_dl", "build_receipts.json"))
    verify = load(os.path.join("_dl", "verify.json"))
    cn = agg["self_check_on_readable_sample"]
    hk = agg["hk_probe"]

    written = [
        meta("capability_report.md"),
        meta("provenance.json"),
        meta(os.path.join("_work", "hk_probe_aggregate.json")),
        meta(os.path.join("_work", "cn_selfcheck.json")),
        meta(os.path.join("_work", "hk_probe.json")),
        meta(os.path.join("_work", "hk_probe2.json")),
        meta(os.path.join("_work", "hk_probe3.json")),
        meta(os.path.join("_work", "hk_probe4.json")),
        meta(os.path.join("_work", "build_env.py")),
        meta(os.path.join("_work", "probe_ocr.py")),
        meta(os.path.join("_work", "aggregate.py")),
        meta(os.path.join("_work", "make_provenance.py")),
        meta(os.path.join("_shim", "sitecustomize.py")),
        meta(os.path.join("_dl", "build_receipts.json")),
        meta(os.path.join("_dl", "install_report.json")),
        meta(os.path.join("_dl", "verify.json")),
    ]

    doc = {
        "card": "OPEN5-PEND5B-OCR-CAPABILITY",
        "attempt": "a20260924-01",
        "role": "capability_landing",
        "authorized_by": "OWNER_DECISIONS §二十六 #2",
        "authorization_verbatim": "owner 首答「1，授权，2，要」→ 父澄清提问 → owner 答「两项都要（PEND-5b 装 + E1 交会计面）」 ⇒ 第2行 = PEND-5b 装 OCR 引擎（「要」）",
        "parent_agent_id": "session-19074bf0-0205-4315-af73-9db57597275a",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "conclusion": "CAPABLE",
        "selected_backend": {
            "ocr": "rapidocr 3.9.2 (PP-OCRv6 det/rec + cls models bundled, 3 onnx, 31749509 B, offline)",
            "runtime": "onnxruntime 1.30.0 (CPU)",
            "renderer": "pypdfium2 5.13.0",
            "python": "3.13.9 (card venv)",
            "why": "pure-pip, small, offline-capable; rapidocr-onnxruntime 1.4.4 rejected (requires_python<3.13 vs only interpreter 3.13.9); easyocr/paddleocr rejected (>200MB-class deps); tesseract-class NOT installed (system binary forbidden -> would be BLOCKED-NEEDS-SYSTEM-BINARY, not needed)",
            "system_binary_required": False,
        },
        "install_scope": {
            "venv": "venv/ (this card's attempt only)",
            "site_packages": "venv/Lib/site-packages",
            "mechanism": "urllib download + direct wheel extraction (pip network unusable in sandbox: temp-dir Errno13 + index-fetch hang, 3 bounded attempts)",
            "system_level": {
                "path_modified": False,
                "windows_packages": False,
                "global_site_packages_writes": 0,
                "system_python_packages": 0,
            },
            "download_packages": receipts["count"],
            "download_total_bytes": receipts["total_bytes"],
            "download_largest_single_bytes": receipts["largest_single_bytes"],
            "download_any_over_200mb": receipts["any_over_200mb"],
            "all_sha256_verified": all(d.get("sha256_match") for d in receipts["downloads"]),
            "models_downloaded_separately": 0,
            "verify_all_imports_ok": verify["all_ok"],
        },
        "self_check_on_readable_sample": {
            "gate_ran_before_hk_probe": True,
            "file": cn["file"],
            "sha256": cn["sha256"],
            "bytes": cn["bytes"],
            "page": cn["page"],
            "anchors": cn["anchors"],
            "anchor_hit_pages": cn["anchor_hit_pages"],
            "anchors_hit_count": sum(1 for v in cn["anchor_hit_pages"].values() if v),
            "passed": cn["gate_passed"],
            "ocr_ms": cn["ocr_ms"], "ocr_chars": cn["ocr_chars"], "score_mean": cn["score_mean"],
        },
        "hk_probe": {
            "file": hk["file"],
            "sha256": hk["sha256"],
            "bytes": hk["bytes"],
            "read_only": True,
            "pages_probed": hk["pages_probed_count"],
            "page_count": hk["page_count"],
            "coverage_fraction": hk["pages_probed_fraction_of_doc"],
            "anchors_hit": hk["anchors_hit"],
            "anchors_missed": hk["anchors_missed"],
            "ocr_anchor_page_hits": hk["ocr_total_anchor_hits"],
            "text_layer_anchor_page_hits": hk["text_layer_total_anchor_hits"],
            "ocr_error_count": hk["ocr_error_count"],
            "total_ocr_chars": hk["total_ocr_chars"],
            "ocr_ms_per_page_mean": hk["ocr_ms_per_page"]["mean"],
            "confidence_score_mean": hk["confidence_score_mean_over_pages"],
            "anchor_hit_pages_union": hk["anchor_hit_pages_union"],
            "note": "origin text layer = 0 anchor hits on the same 43 pages (root cause RC-1); OCR outputs are ocr_reconstruction, never origin text",
        },
        "cover_counter_test": {
            "text_layer_chars": hk["cover_counter_test"]["text_layer_chars"],
            "text_layer_excerpt": hk["cover_counter_test"]["text_layer_excerpt"],
            "ocr_excerpt": hk["cover_counter_test"]["ocr_excerpt"],
            "verdict": "OCR reproduces the readable cover line AND reads content the text layer cannot provide; combined with body TL=0 vs OCR hits => font-mapping root cause + OCR bypass demonstrated",
        },
        "ocr_reconstruction_disclaimer": True,
        "written_files": written,
        "write_face": "only execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/",
        "git_diff_non_planning": 0,
        "git_untracked_non_planning_by_this_card": 0,
        "git_writes": 0,
        "product_repo_writes_by_this_card": 0,
        "unlocks_nothing": True,
        "does_not": [
            "no system-level install (PATH / Windows packages / global site-packages untouched)",
            "no writes outside .planning (company-wiki/filing-fetch/revenue-forecast untouched by this card)",
            "OPEN-5 not released; I-11-B / I-07-B not unblocked; no ACCEPT / no status change",
            "OCR output never treated as primary disclosure (all tagged ocr_reconstruction)",
            "no S3 re-evidence / S4 dual-path cross-check / S5 grading (those stay with orchestrator + professional reviewers)",
            "full 415-page sweep not executed (43-page probe only)",
        ],
        "file_format": {
            "encoding": "UTF-8",
            "bom": False,
            "line_ending": "LF",
            "json_reparse": "ok",
        },
        "note": "handoff.json does not include its own hash",
    }

    out = os.path.join(ATTEMPT, "handoff.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(out, "r", encoding="utf-8") as f:
        json.load(f)
    with open(out, "rb") as f:
        head = f.read(3)
    print("wrote", out, "bom=", head == b"\xef\xbb\xbf",
          "written_files=", len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
