"""Aggregate CN self-check + 4 HK probe rounds into one summary JSON."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    cn_path = os.path.join(base, "cn_selfcheck.json")
    hk_paths = [
        os.path.join(base, "hk_probe.json"),
        os.path.join(base, "hk_probe2.json"),
        os.path.join(base, "hk_probe3.json"),
        os.path.join(base, "hk_probe4.json"),
    ]

    def load(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    cn = load(cn_path)
    hks = [load(p) for p in hk_paths]

    union = {}
    tl_union = {}
    pages = []
    errors = []
    ocr_ms = []
    render_ms = []
    scores = []
    total_chars = 0
    total_wall = 0
    for j in hks:
        for a, ps in j["anchor_hit_pages"].items():
            union.setdefault(a, [])
            union[a] = sorted(set(union[a]) | set(ps))
        for a, ps in j["text_layer_anchor_hit_pages"].items():
            tl_union.setdefault(a, [])
            tl_union[a] = sorted(set(tl_union[a]) | set(ps))
        total_wall += j["totals"]["wall_ms"]
        total_chars += j["totals"]["ocr_chars"]
        for p in j["pages"]:
            pages.append(p["page"])
            if "ocr_error" in p:
                errors.append({"page": p["page"], "error": p["ocr_error"]})
            ocr_ms.append(p["ocr_ms"])
            render_ms.append(p["render_ms"])
            if p.get("ocr_score_mean") is not None:
                scores.append(p["ocr_score_mean"])

    cn_p = cn["pages"][0]
    out = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ocr_reconstruction": True,
        "self_check_on_readable_sample": {
            "file": cn["pdf"],
            "sha256": cn["pdf_sha256"],
            "bytes": cn["pdf_bytes"],
            "page": 1,
            "anchors": cn["anchors"],
            "anchor_hit_pages": cn["anchor_hit_pages"],
            "text_layer_anchor_hit_pages": cn["text_layer_anchor_hit_pages"],
            "ocr_chars": cn_p["ocr_chars"],
            "ocr_ms": cn_p["ocr_ms"],
            "score_mean": cn_p.get("ocr_score_mean"),
            "ocr_excerpt": cn_p["ocr_excerpt"],
            "text_layer_excerpt": cn_p.get("text_layer_excerpt"),
            "gate_passed": any(cn["anchor_hit_pages"].values()),
        },
        "hk_probe": {
            "file": hks[0]["pdf"],
            "sha256": hks[0]["pdf_sha256"],
            "bytes": hks[0]["pdf_bytes"],
            "page_count": hks[0]["page_count"],
            "dpi": hks[0]["dpi"],
            "rounds": [
                {
                    "json": os.path.basename(p),
                    "json_sha256": sha256_file(p),
                    "pages": j["pages"] and [x["page"] for x in j["pages"]],
                    "wall_ms": j["totals"]["wall_ms"],
                }
                for p, j in zip(hk_paths, hks)
            ],
            "pages_probed": sorted(pages),
            "pages_probed_count": len(pages),
            "pages_probed_fraction_of_doc": round(len(pages) / hks[0]["page_count"], 4),
            "anchor_hit_pages_union": union,
            "text_layer_anchor_hit_pages_union": tl_union,
            "text_layer_total_anchor_hits": sum(len(v) for v in tl_union.values()),
            "ocr_total_anchor_hits": sum(len(v) for v in union.values()),
            "anchors_hit": sorted([a for a, v in union.items() if v]),
            "anchors_missed": sorted([a for a, v in union.items() if not v]),
            "ocr_errors": errors,
            "ocr_error_count": len(errors),
            "total_ocr_chars": total_chars,
            "total_wall_ms": total_wall,
            "ocr_ms_per_page": {
                "min": min(ocr_ms),
                "max": max(ocr_ms),
                "mean": round(sum(ocr_ms) / len(ocr_ms)),
            },
            "render_ms_per_page": {
                "min": min(render_ms),
                "max": max(render_ms),
                "mean": round(sum(render_ms) / len(render_ms)),
            },
            "confidence_score_mean_over_pages": round(sum(scores) / len(scores), 4),
            "cover_counter_test": {
                "note": "page 1: origin text layer vs OCR reconstruction",
                "text_layer_chars": hks[0]["pages"][0].get("text_layer_chars"),
                "text_layer_excerpt": hks[0]["pages"][0].get("text_layer_excerpt"),
                "ocr_excerpt": hks[0]["pages"][0].get("ocr_excerpt"),
            },
            "sample_excerpts": {
                "p337_segment_note": next(
                    p["ocr_excerpt"] for p in hks[3]["pages"] if p["page"] == 337
                ),
                "p115_esg_materiality": next(
                    p["ocr_excerpt"] for p in hks[0]["pages"] if p["page"] == 115
                ),
            },
        },
        "source_jsons": [
            {"path": cn_path, "sha256": sha256_file(cn_path)},
            *[{"path": p, "sha256": sha256_file(p)} for p in hk_paths],
        ],
    }

    dest = os.path.join(base, "hk_probe_aggregate.json")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(dest, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", dest)
    print(json.dumps({
        "anchors_hit": out["hk_probe"]["anchors_hit"],
        "anchors_missed": out["hk_probe"]["anchors_missed"],
        "ocr_hits": out["hk_probe"]["ocr_total_anchor_hits"],
        "textlayer_hits": out["hk_probe"]["text_layer_total_anchor_hits"],
        "pages": out["hk_probe"]["pages_probed_count"],
        "errors": out["hk_probe"]["ocr_error_count"],
        "gate": out["self_check_on_readable_sample"]["gate_passed"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
