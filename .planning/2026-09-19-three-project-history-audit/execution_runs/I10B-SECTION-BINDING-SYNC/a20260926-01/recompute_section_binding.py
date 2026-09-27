#!/usr/bin/env python3
"""只读复算 `execution_v2/validate_execution_pack.py` L21–L36 的**段绑定**判定式。

纪律：
- **不 import、不 exec、不运行** `validate_execution_pack.py`（它会覆写 `execution_v2/validation.json`）；
- 本脚本**不写任何文件**（无 open(...,'w')、无 json.dump 落盘）；
- 判定式逐行照抄原脚本 L21–L36，一字不改（仅把 `errors.append(...)` 换成等价计数）；
- rc 语义与原脚本同形：`raise SystemExit(1 if errors else 0)` ⇒ 有错 rc=1，无错 rc=0。

用法：python recompute_section_binding.py <execution_v2目录>
输出：JSON（段数 / stale 列表 / clone 列表 / 全部错误 / 逐卡指纹），stdout。
"""
import hashlib
import json
import re
import sys
from pathlib import Path


def recompute(P: Path) -> dict:
    errors = []
    read = lambda p: json.loads(p.read_text(encoding="utf-8-sig"))
    d = read(P / "dispatch.json")
    cards = d["cards"]
    by = {c["id"]: c for c in cards}
    details = []
    for c in cards:
        # --- 原脚本 L21–L36 逐行照抄 ---
        source = (P / c["source_document"]).read_text(encoding="utf-8-sig")
        own = [x for x in cards if x["source_document"] == c["source_document"]]
        headings = []
        for other in own:
            match = re.search(r"^#{2,3} " + re.escape(other["id"]) + r"(?=\s|[·—:：]).*$", source, re.M)
            if match:
                headings.append((match.start(), other["id"]))
        headings.sort()
        positions = [i for i, x in enumerate(headings) if x[1] == c["id"]]
        if len(positions) != 1:
            errors.append("cannot uniquely bind source heading " + c["id"])
            continue
        i = positions[0]
        start = headings[i][0]
        end = headings[i + 1][0] if i + 1 < len(headings) else len(source)
        section = source[start:end].strip() + "\n"
        expected = hashlib.sha256(section.encode("utf-8")).hexdigest()
        stale = expected != c["source_section_sha256"]
        if stale:
            errors.append("stale extracted card source " + c["id"])
        clone_text = (P / c["document"]).read_text(encoding="utf-8-sig").split("\n\n", 1)[-1]
        clone = clone_text != section
        if clone:
            errors.append("single-card body differs from source " + c["id"])
        # --- 照抄结束 ---
        details.append({
            "id": c["id"],
            "source_document": c["source_document"],
            "is_last_heading": i == len(headings) - 1,
            "section_bytes": len(section.encode("utf-8")),
            "section_sha256": expected,
            "dispatch_source_section_sha256": c["source_section_sha256"],
            "card_body_chars": len(clone_text),
            "stale": stale,
            "clone": clone,
        })
    stale_ids = [x["id"] for x in details if x["stale"]]
    clone_ids = [x["id"] for x in details if x["clone"]]
    by_source = {}
    for x in details:
        g = by_source.setdefault(x["source_document"], {"bindings": 0, "last_heading_card": None, "errors": 0})
        g["bindings"] += 1
        if x["is_last_heading"]:
            g["last_heading_card"] = x["id"]
        if x["stale"] or x["clone"]:
            g["errors"] += 1
    return {
        "bindings_by_source_document": by_source,
        "predicate": "validate_execution_pack.py L21-L36 (verbatim copy, read-only)",
        "target": str(P),
        "cards": len(cards),
        "section_bindings": len(details),
        "stale_count": len(stale_ids),
        "clone_count": len(clone_ids),
        "stale_ids": stale_ids,
        "clone_ids": clone_ids,
        "error_count": len(errors),
        "errors": errors,
        "mismatch_details": [x for x in details if x["stale"] or x["clone"]],
        "last_binding_card": details[-1]["id"] if details else None,
    }


def main() -> int:
    P = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[4] / "execution_v2"
    out = recompute(P)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if out["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
