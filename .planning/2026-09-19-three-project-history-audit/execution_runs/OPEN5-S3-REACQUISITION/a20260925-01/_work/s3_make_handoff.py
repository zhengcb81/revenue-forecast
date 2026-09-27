"""OPEN5-S3-REACQUISITION · build handoff.json (counts/shas computed, not typed)."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

DEC8 = (
    "**恢复规则**：可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的\n"
    "`not_readable` 判定改成\"已验证\"。"
)
S3_DEF = (
    "**新建 attempt 重新取证**（卡文 DEC-8 恢复规则）：在**全新 attempt** 中对 HK 原文重新取文；"
    "**封盘 attempt `I-11-A/a20260919-01` 与本次 `not_readable` 判定一律不动** | 执行方：编排层派单的实现者（新 attempt） | "
    "失败分支：新 attempt 仍不可读 ⇒ 记 `not_readable`（新记录），**旧判定原样**，回到 S1"
)
BOUNDARY = (
    "ruling.md L174-L179：S3 明文要求\"新建 attempt\"，恢复取证发生在新 attempt，"
    "本载体与封盘 attempt 都不产生任何\"已验证\"字样；即使 S2 自检显示\"某路径能读出锚词\"，"
    "在 S3/S4/S5 走完之前仍按不可读处置（港股命题零产出、参数维持 `_PLACEHOLDER`）"
)


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--ws-root", required=True)
    ap.add_argument("--git-diff-total", type=int, required=True)
    ap.add_argument("--git-diff-non-planning", type=int, required=True)
    ap.add_argument("--untracked-non-planning", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = os.path.abspath(args.attempt_root)
    ws = os.path.abspath(args.ws_root)
    reacq = load(os.path.join(root, "reacquisition.json"))
    pa = load(os.path.join(root, "_work", "pathA_probe.json"))
    pb = load(os.path.join(root, "_work", "pathB_probe.json"))
    mb = load(os.path.join(root, "_work", "manifest_before.json"))
    ma = load(os.path.join(root, "_work", "manifest_after.json"))

    rel = lambda p: os.path.relpath(os.path.abspath(p), ws).replace("\\", "/")  # noqa: E731

    written = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            fp = os.path.join(dirpath, name)
            if os.path.abspath(fp) == os.path.abspath(args.out):
                continue
            written.append(
                {"path": rel(fp), "bytes": os.path.getsize(fp), "sha256": sha256_file(fp)}
            )
    written.sort(key=lambda x: x["path"])

    manifest_check = []
    for b, a in zip(mb["dirs"], ma["dirs"]):
        manifest_check.append(
            {
                "dir": b["dir"],
                "files": b["files"],
                "bytes": b["bytes"],
                "aggregate_sha256_before": b["aggregate_sha256"],
                "aggregate_sha256_after": a["aggregate_sha256"],
                "identical": (
                    b["aggregate_sha256"] == a["aggregate_sha256"]
                    and b["files"] == a["files"]
                    and b["bytes"] == a["bytes"]
                ),
            }
        )

    a = reacq["paths"]["A_ocr"]
    b1 = reacq["paths"]["B1_origin_textlayer"]
    b2 = reacq["paths"]["B2_substitute_attempt04"]
    b28 = reacq["paths"]["B2prime_substitute_attempt08"]

    handoff = {
        "card": "OPEN-5",
        "step": "S3",
        "attempt": "OPEN5-S3-REACQUISITION/a20260925-01",
        "role": "implementer_s3",
        "generated_utc": utc_now(),
        "authorized_by": {
            "dispatch": "编排层派单（ruling.md L164 执行方 = 编排层派单的实现者（新 attempt））",
            "decision_rule_DEC8": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "execution_runs/I-11-A/a20260919-01/decision.md L227-L228",
                "quote": DEC8,
            },
            "S3_definition_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L164",
                "quote": S3_DEF,
            },
            "boundary_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L174-L179",
                "quote": BOUNDARY,
            },
            "owner_authorization": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "OWNER_DECISIONS.md §二十六 #1/#2",
                "quote": "#1 PEND-5a owner 原话「授权」；#2 PEND-5b owner 原话「要」"
                "→ 澄清答「两项都要（PEND-5b 装 + E1 交会计面）」",
            },
            "capability_reused_read_only": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/capability_report.md",
                "conclusion": "CAPABLE",
            },
            "substitutes_reused_read_only": {
                "source": ".planning/2026-09-19-three-project-history-audit/"
                "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/acquisition_report.md",
                "conclusion": "attempt04 港交所原站 4/5；attempt08 英文年报 5/5",
            },
        },
        "readability_result": reacq["readability_result"],
        "readability_basis": reacq["readability_basis"],
        "paths_run": {
            "A_ocr": {
                "rc": a["rc"],
                "engine": a["engine"],
                "renderer": a["renderer"],
                "pages_run": a["pages_run"],
                "anchor_hit_count": a["anchor_hit_count"],
                "anchors": a["anchor_hits"],
                "origin_text_layer_same_pages_anchor_hits": a[
                    "origin_text_layer_anchor_hits_on_same_pages"
                ],
                "ocr_errors": a["ocr_errors"],
                "verdict": a["verdict"],
                "ocr_reconstruction": True,
            },
            "B1_origin_textlayer": {
                "rc": pb["rc"],
                "pages_scanned": b1["page_count"],
                "chars": b1["full_doc_chars"],
                "anchor_hit_count": len(b1["anchor_hit_words"]),
                "anchors": b1["anchor_counts"],
                "verdict": "not_readable_alone",
            },
            "B2_substitute_attempt04": {
                "rc": pb["rc"],
                "fitz": {"hit_count": len(b2["fitz"]["anchor_hit_words"]), "hit_words": b2["fitz"]["anchor_hit_words"], "counts": b2["fitz"]["anchor_counts"]},
                "pdfminer": {"hit_count": len(b2["pdfminer"]["anchor_hit_words"]), "hit_words": b2["pdfminer"]["anchor_hit_words"], "counts": b2["pdfminer"]["anchor_counts"]},
                "both_libs_agree": b2["both_libs_hit_words_agree"],
                "verdict": b2["verdict"],
                "substitute_not_origin": True,
            },
            "B2prime_substitute_attempt08": {
                "rc": pb["rc"],
                "cn_hit_count": len(b28["cn_anchor_hit_words"]),
                "en_hit_count": len(b28["en_anchor_hit_words"]),
                "en_anchor_counts": b28["en_anchor_counts"],
                "substitute_not_origin": True,
            },
        },
        "ocr_reconstruction": True,
        "ocr_reconstruction_policy": "路径 A 全部文本字段为图像→文本重建，永不冒充 origin 文本",
        "external_retrieval_not_local": False,
        "retrieval_method": {
            "A": "local_bytes_no_external_retrieval_this_attempt (render+OCR)",
            "B": "local_readonly_reuse_of_prior_attempt_bytes",
        },
        "sealed_attempt_untouched": all(m["identical"] for m in manifest_check),
        "prior_not_readable_preserved": True,
        "prior_not_readable_verdict_changed": False,
        "releases_nothing": True,
        "does_not_claim_I11A_acceptance": True,
        "open5_released": False,
        "still_dispositioned_not_readable_until_S4_S5": True,
        "placeholder_params_released": False,
        "accept_produced": False,
        "evidence_grading_done": False,
        "read_only_manifest_check": manifest_check,
        "read_only_manifest_files": [
            rel(os.path.join(root, "_work", "manifest_before.json")),
            rel(os.path.join(root, "_work", "manifest_after.json")),
        ],
        "s4_staging": reacq["s4_staging"],
        "written_files": {
            "count": len(written),
            "total_bytes": sum(x["bytes"] for x in written),
            "self_excluded": "handoff.json (self-reference impossible)",
            "files": written,
        },
        "git_diff_total": args.git_diff_total,
        "git_diff_non_planning": args.git_diff_non_planning,
        "untracked_non_planning": args.untracked_non_planning,
        "git_write_ops": 0,
        "git_status_used": False,
        "write_surface": "only .planning/2026-09-19-three-project-history-audit/"
        "execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/",
        "not_done": [
            "未改 I-11-A 封盘任何字节",
            "未把本次 not_readable 判定改成「已验证」",
            "未改 S1 两站（PEND-5a/PEND-5b）任何字节",
            "未解除 OPEN-5（S4/S5 前仍按不可读处置）",
            "未放行港股参数（维持 _PLACEHOLDER）",
            "未产生 I-11-B 的 ACCEPT、未代签",
            "未写五份计划文件",
            "未判会计证据等级（归 S5）",
            "未下 S4 双路径一致性结论（只铺路）",
            "未写 .planning 之外任何路径（含 company-wiki 产品仓）",
            "零 git 写、未使用 git status",
        ],
        "next_station": "S4 双路径复核 + provenance（实现者 + 独立 reviewer）；S5 行业复裁 + 会计定级",
    }

    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(handoff, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.out, "r", encoding="utf-8") as f:
        json.load(f)
    print(
        json.dumps(
            {
                "wrote": args.out,
                "readability_result": handoff["readability_result"],
                "sealed_attempt_untouched": handoff["sealed_attempt_untouched"],
                "written_files_count": len(written),
                "git_diff_non_planning": args.git_diff_non_planning,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
