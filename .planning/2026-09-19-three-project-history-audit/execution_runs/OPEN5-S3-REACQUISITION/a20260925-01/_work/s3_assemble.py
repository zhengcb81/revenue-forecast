"""OPEN5-S3-REACQUISITION · assemble reacquisition.json + provenance.json.

Reads the two probe JSONs and the S4 comparison scaffold, applies the frozen
oracle criteria (oracle.md §4) and emits the two machine-readable deliverables.
Nothing outside this attempt directory is written.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]

DEC8_QUOTE = (
    "**恢复规则**：可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的\n"
    "`not_readable` 判定改成\"已验证\"。"
)
S3_QUOTE = (
    "**新建 attempt 重新取证**（卡文 DEC-8 恢复规则）：在**全新 attempt** 中对 HK 原文重新取文；"
    "**封盘 attempt `I-11-A/a20260919-01` 与本次 `not_readable` 判定一律不动**"
)
L179_QUOTE = (
    "即使 S2 自检显示\"某路径能读出锚词\"，在 S3/S4/S5 走完之前**仍按不可读处置**"
    "（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。"
)


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p: str):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def make_rel(attempt_dir: str):
    root = os.path.abspath(attempt_dir)

    def rel(p: str) -> str:
        try:
            r = os.path.relpath(os.path.abspath(p), root)
        except ValueError:
            return p
        return r if not r.startswith("..") else p

    return rel


def find_ws_root(start: str) -> str:
    cur = os.path.abspath(start)
    while True:
        if os.path.basename(cur) == ".planning":
            return os.path.dirname(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start)
        cur = parent


def make_wsrel(ws_root: str):
    root = os.path.abspath(ws_root)

    def wrel(p: str) -> str:
        ap = os.path.abspath(p)
        if ap.lower().startswith(root.lower() + os.sep):
            return os.path.relpath(ap, root).replace("\\", "/")
        return p

    return wrel


def dump(p: str, obj) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(p)) or ".", mode=0o777, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(p, "r", encoding="utf-8") as f:
        json.load(f)
    return sha256_file(p)


def first_evidence(rec: dict, word: str) -> dict | None:
    hits = rec.get("ocr_anchor_hits", {}).get(word) or []
    return hits[0] if hits else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--attempt", required=True)
    ap.add_argument("--out-reacq", required=True)
    ap.add_argument("--out-prov", required=True)
    args = ap.parse_args()

    pa = load(os.path.join(args.work, "pathA_probe.json"))
    pb = load(os.path.join(args.work, "pathB_probe.json"))
    pc = load(os.path.join(args.work, "path_compare.json"))

    attempt_root = os.path.dirname(os.path.abspath(args.work))
    ws_root = find_ws_root(attempt_root)
    wrel = make_wsrel(ws_root)

    def ws_hash(ws_rel_path: str) -> str:
        return sha256_file(os.path.join(ws_root, ws_rel_path.replace("/", os.sep)))

    def relwalk(o):
        """Rewrite display paths (file/path keys) to workspace-relative form."""
        if isinstance(o, dict):
            for k in ("file", "path", "png", "ocr_text_file"):
                if isinstance(o.get(k), str):
                    o[k] = wrel(o[k])
            for v in o.values():
                relwalk(v)
        elif isinstance(o, list):
            for v in o:
                relwalk(v)
        return o

    relwalk(pb)
    relwalk(pc)

    # ---------- oracle application (frozen criteria, oracle.md §4) ----------
    a_hit_words = pa.get("anchor_words_hit", [])
    a_count = len(a_hit_words)
    a_pass = a_count >= 3 and pa["rc"] == 0 and pa["pdf_sha_matches_expected"]
    a_verdict = "A-pass" if a_pass else ("partial" if a_count > 0 else "A-fail")
    readability = "readable" if a_pass else "not_readable"

    b1_hit_words = sorted(w for w, v in pb["b1_origin_textlayer"]["fitz"]["anchors"].items() if v["count"] > 0)

    f4 = pb["b2_attempt04"]
    fitz_hits = f4["fitz"]["hit_words"]
    pm_hits = f4["pdfminer"]["hit_words"]
    b_pass = len(fitz_hits) >= 3 and len(pm_hits) >= 3 and f4["both_libs_hit_words_agree"]

    r8 = pb["b2prime_attempt08"]["fitz"]
    cn8_hits = r8["cn_hit_words"]
    en8_hits = r8["en_hit_words"]

    # ------------------------- reacquisition.json -------------------------
    per_page = []
    for rec in pa["pages"]:
        ev = {w: first_evidence(rec, w) for w in ANCHORS}
        per_page.append(
            {
                "page": rec["page"],
                "render_ms": rec["render_ms"],
                "png": wrel(rec["png"]),
                "png_bytes": rec["png_bytes"],
                "png_sha256": rec["png_sha256"],
                "img_size": rec["img_size"],
                "ocr_ms": rec["ocr_ms"],
                "ocr_chars": rec["ocr_chars"],
                "ocr_lines": rec["ocr_lines"],
                "ocr_score_mean": rec.get("ocr_score_mean"),
                "ocr_error": rec.get("ocr_error"),
                "ocr_text_file": wrel(rec["ocr_text_file"]),
                "ocr_text_file_sha256": rec["ocr_text_file_sha256"],
                "ocr_anchors": rec["ocr_anchors"],
                "ocr_anchor_hits": rec["ocr_anchor_hits"],
                "ocr_first_evidence": {w: v for w, v in ev.items() if v},
                "origin_text_layer": {
                    "chars": rec["text_layer_chars"],
                    "sha256": rec["text_layer_sha256"],
                    "anchors": rec["text_layer_anchors"],
                    "file": wrel(rec["text_layer_file"]),
                    "file_sha256": rec["text_layer_file_sha256"],
                },
                "ocr_reconstruction": True,
            }
        )

    reacq = {
        "card": "OPEN-5",
        "step": "S3",
        "attempt": args.attempt,
        "role": "implementer_s3",
        "generated_utc": utc_now(),
        "oracle": {
            "file": "oracle.md",
            "sha256": sha256_file(
                os.path.join(os.path.dirname(os.path.abspath(args.work)), "oracle.md")
            ),
            "frozen_before_any_probe": True,
            "anchors": ANCHORS,
            "pass_line": "path A >= 3/5 anchors on the origin bytes (sha-verified); "
            "path B2 both libs >= 3/5",
        },
        "target": {
            "id": "HK-XIAOMI-AR2025",
            "path": pb["inputs"][0]["path"],
            "bytes": pb["inputs"][0]["bytes"],
            "sha256": pb["inputs"][0]["sha256"],
            "sha_matches_frozen_baseline": pb["inputs"][0]["matches_frozen_baseline"],
            "page_count": pa["page_count"],
            "access": "read_only",
            "retrieved_utc": None,
            "retrieval_method": "local_bytes_no_external_retrieval_this_attempt",
            "external_retrieval_not_local": False,
        },
        "paths": {
            "A_ocr": {
                "definition": "pypdfium2 render (200dpi) -> rapidocr OCR -> anchor probe; "
                "origin text layer recorded as contrast on the same pages",
                "engine": pa["ocr_engine"],
                "renderer": pa["renderer"],
                "engine_source": "read-only reuse of "
                "OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/venv (not modified)",
                "retrieval_method": pa["retrieval_method"],
                "external_retrieval_not_local": False,
                "rc": pa["rc"],
                "pages_run": [p["page"] for p in pa["pages"]],
                "pages_run_count": len(pa["pages"]),
                "ocr_errors": pa["totals"]["ocr_errors"],
                "ocr_reconstruction": True,
                "anchor_hit_count": a_count,
                "anchor_hits": pa["anchor_hit_pages"],
                "origin_text_layer_anchor_hits_on_same_pages": pa["text_layer_anchor_hit_pages"],
                "verdict": a_verdict,
                "per_page": per_page,
            },
            "B1_origin_textlayer": {
                "definition": "PyMuPDF full 415-page text-layer scan of the origin bytes (contrast only)",
                "rc": pb["rc"],
                "engine": pb["b1_origin_textlayer"]["fitz"]["engine"],
                "page_count": pb["b1_origin_textlayer"]["page_count"],
                "full_doc_chars": pb["b1_origin_textlayer"]["fitz"]["full_doc_chars"],
                "extract": pb["b1_origin_textlayer"]["fitz"]["full_doc_extract"],
                "anchor_counts": {
                    w: v["count"]
                    for w, v in pb["b1_origin_textlayer"]["fitz"]["anchors"].items()
                },
                "anchor_hit_words": b1_hit_words,
                "hit_pages_union": pb["b1_origin_textlayer"]["fitz"]["hit_pages_union"],
                "sample_pages": pb["b1_origin_textlayer"]["fitz"]["sample_pages"],
                "note": "0 anchors across the whole document = RC-1 root cause re-confirmed; "
                "this path alone is NOT readable",
            },
            "B2_substitute_attempt04": {
                "definition": "readable substitute text layer (PEND-5a corpus, read-only reuse)",
                "input": pb["inputs"][1],
                "substitute_not_origin": True,
                "rc": pb["rc"],
                "fitz": {
                    "chars": f4["fitz"]["chars"],
                    "extract": f4["fitz"]["extract"],
                    "anchor_counts": {w: v["count"] for w, v in f4["fitz"]["anchors"].items()},
                    "anchor_hit_pages": {w: v["hit_pages"] for w, v in f4["fitz"]["anchors"].items()},
                    "anchor_hit_words": fitz_hits,
                    "first_hits": {
                        w: v["first_hit"] for w, v in f4["fitz"]["anchors"].items() if v["first_hit"]
                    },
                },
                "pdfminer": {
                    "chars": f4["pdfminer"]["chars"],
                    "extract": f4["pdfminer"]["extract"],
                    "anchor_counts": {
                        w: v["count"] for w, v in f4["pdfminer"]["anchors"].items()
                    },
                    "anchor_hit_pages": {
                        w: v["hit_pages"] for w, v in f4["pdfminer"]["anchors"].items()
                    },
                    "anchor_hit_words": pm_hits,
                    "first_hits": {
                        w: v["first_hit"]
                        for w, v in f4["pdfminer"]["anchors"].items()
                        if v["first_hit"]
                    },
                },
                "both_libs_hit_words_agree": f4["both_libs_hit_words_agree"],
                "anchor_hit_count": len(fitz_hits),
                "verdict": "B-pass" if b_pass else "B-fail",
                "substitute_readable": bool(b_pass),
                "note": "substitute is a FY2025 results announcement (different document type "
                "from the annual report); grading is S5's job",
            },
            "B2prime_substitute_attempt08": {
                "definition": "annual-report EN edition text layer (PEND-5a corpus, read-only reuse)",
                "input": pb["inputs"][2],
                "substitute_not_origin": True,
                "rc": pb["rc"],
                "chars": r8["chars"],
                "extract": r8["extract"],
                "cn_anchor_counts": {w: v["count"] for w, v in r8["cn_anchors"].items()},
                "cn_anchor_hit_words": cn8_hits,
                "en_anchor_counts": {w: v["count"] for w, v in r8["en_anchors"].items()},
                "en_anchor_hit_words": en8_hits,
                "first_hits_en": {
                    w: v["first_hit"] for w, v in r8["en_anchors"].items() if v["first_hit"]
                },
                "note": "Chinese anchors 0/5 (English body); recorded for S4/S5, "
                "never used as a Chinese-readable conclusion",
            },
        },
        "readability_result": readability,
        "readability_basis": (
            f"path A on the sha-verified origin bytes: {a_count}/5 anchors hit "
            f"({', '.join(a_hit_words)}) on pages "
            f"{sorted({p for w in a_hit_words for p in pa['anchor_hit_pages'][w]})}; "
            "origin text layer on the same pages = 0/5 (contrast). "
            "Per oracle §4.3 this is an S3 observation only."
        ),
        "prior_not_readable_preserved": True,
        "sealed_attempt_untouched": True,
        "open5_released": False,
        "still_not_readable_disposition_until_s4_s5": True,
        "s4_staging": {
            "file": wrel(os.path.join(args.work, "path_compare.json")),
            "sha256": sha256_file(os.path.join(args.work, "path_compare.json")),
            "method": pc["method"],
            "summary": pc["summary"],
            "verdict_left_to": pc["summary"]["verdict_left_to"],
        },
    }
    reacq_sha = dump(args.out_reacq, reacq)

    # --------------------------- provenance.json ---------------------------
    def entry(eid, kind, path, utc, sha=None, quote=None, note=None, **extra):
        d = {"id": eid, "kind": kind, "path": path, "utc": utc}
        if sha:
            d["sha256"] = sha
        if quote:
            d["quote"] = quote
        if note:
            d["note"] = note
        d.update(extra)
        return d

    base = ".planning/2026-09-19-three-project-history-audit/execution_runs"
    entries = [
        entry(
            "auth-01",
            "authorization",
            f"{base}/I-11-A/a20260919-01/decision.md",
            "2026-09-19T00:00:00Z",
            quote=DEC8_QUOTE,
            note="DEC-8 recovery rule, verbatim (L227-L228)",
        ),
        entry(
            "auth-02",
            "authorization",
            f"{base}/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md",
            "2026-09-24T00:00:00Z",
            quote=S3_QUOTE,
            note="S3 definition, verbatim (L164)",
        ),
        entry(
            "auth-03",
            "authorization",
            f"{base}/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md",
            "2026-09-24T00:00:00Z",
            quote=L179_QUOTE,
            note="S2/S3 boundary, verbatim (L179)",
        ),
        entry(
            "auth-04",
            "authorization",
            ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md",
            "2026-09-24T00:00:00Z",
            quote="§二十六 #1 owner 原话「授权」(PEND-5a) / #2 owner 原话「要」→ 澄清「两项都要（PEND-5b 装 + E1 交会计面）」",
            note="two-path authorization, verbatim",
        ),
        entry(
            "auth-05",
            "capability_report",
            f"{base}/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/capability_report.md",
            "2026-09-25T21:00:00Z",
            quote="结论：`CAPABLE` … 实测 5/5 锚词命中、origin 文字层同页 0 命中",
            sha=ws_hash(
                f"{base}/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/capability_report.md"
            ),
        ),
        entry(
            "auth-06",
            "acquisition_report",
            f"{base}/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/acquisition_report.md",
            "2026-09-25T20:43:08Z",
            quote="attempt04 港交所原站 … 4/5 … attempt08 … 英文锚词 5/5",
            sha=ws_hash(
                f"{base}/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/acquisition_report.md"
            ),
        ),
        entry(
            "in-01",
            "origin_file",
            pb["inputs"][0]["path"],
            "n/a_local_bytes",
            sha=pb["inputs"][0]["sha256"],
            note="HK-XIAOMI-AR2025, read-only, sha verified before OCR",
            external_retrieval_not_local=False,
            retrieval_method="local_bytes_no_external_retrieval_this_attempt",
        ),
        entry(
            "in-02",
            "substitute_file",
            pb["inputs"][1]["path"],
            pb["inputs"][1]["retrieved_utc"],
            sha=pb["inputs"][1]["sha256"],
            note="read-only reuse of PEND-5a corpus (attempt04)",
            external_retrieval_not_local=False,
            retrieval_method=pb["inputs"][1]["retrieval_method_per_prior_station"],
            substitute_not_origin=True,
        ),
        entry(
            "in-03",
            "substitute_file",
            pb["inputs"][2]["path"],
            pb["inputs"][2]["retrieved_utc"],
            sha=pb["inputs"][2]["sha256"],
            note="read-only reuse of PEND-5a corpus (attempt08 EN)",
            external_retrieval_not_local=False,
            retrieval_method=pb["inputs"][2]["retrieval_method_per_prior_station"],
            substitute_not_origin=True,
        ),
        entry(
            "in-04",
            "ocr_engine_env",
            f"{base}/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/venv/",
            "2026-09-24T00:00:00Z",
            note=f"read-only reference; {pa['ocr_engine']}; {pa['renderer']}; "
            "PYTHONDONTWRITEBYTECODE=1, no write into that venv",
            read_only_reference=True,
        ),
    ]
    for p in per_page:
        entries.append(
            entry(
                f"out-a-p{p['page']:04d}",
                "ocr_page_render",
                p["png"],
                pa["finished_utc"],
                sha=p["png_sha256"],
                quote=(p["ocr_first_evidence"].get("小米") or p["ocr_first_evidence"].get("年度報告") or {}).
                get("line", ""),
                ocr_reconstruction=True,
                page=p["page"],
            )
        )
    out_paths = {
        "reacquisition.json": args.out_reacq,
        "reacquisition_report.md": os.path.join(attempt_root, "reacquisition_report.md"),
        "oracle.md": os.path.join(attempt_root, "oracle.md"),
        "pathA_probe.json": os.path.join(args.work, "pathA_probe.json"),
        "pathB_probe.json": os.path.join(args.work, "pathB_probe.json"),
        "path_compare.json": os.path.join(args.work, "path_compare.json"),
    }
    for name, full in out_paths.items():
        if not os.path.exists(full):
            continue
        entries.append(
            entry(
                f"out-{name}",
                "probe_or_deliverable",
                wrel(full),
                reacq["generated_utc"],
                sha=sha256_file(full),
            )
        )

    prov = {
        "attempt": args.attempt,
        "role": "implementer_s3",
        "generated_utc": utc_now(),
        "authorization": {
            "step": "S3 (ruling.md L164)",
            "decision_rule": "DEC-8 (decision.md L227-L228)",
            "owner_authorization": "OWNER_DECISIONS.md §二十六 #1/#2",
            "hard_bounds_verbatim": [
                S3_QUOTE,
                DEC8_QUOTE,
                L179_QUOTE,
            ],
        },
        "write_surface": f"{args.attempt}/ only; nothing outside .planning written",
        "self_hash_note": "provenance.json cannot list its own sha256 (self-reference); "
        "it is hashed in handoff.json written_files",
        "entries": entries,
        "entry_count": len(entries),
        "counts": {
            "inputs": 4,
            "ocr_page_renders": len(per_page),
            "deliverables": 4,
        },
    }
    prov_sha = dump(args.out_prov, prov)

    print(json.dumps({
        "reacquisition_sha256": reacq_sha,
        "provenance_sha256": prov_sha,
        "readability_result": readability,
        "a_verdict": a_verdict,
        "a_hit_words": a_hit_words,
        "b1_hit_words": b1_hit_words,
        "b2_verdict": "B-pass" if b_pass else "B-fail",
        "b2_fitz_hits": fitz_hits,
        "b2_pm_hits": pm_hits,
        "attempt08_cn": cn8_hits,
        "attempt08_en": en8_hits,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
