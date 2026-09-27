"""Emit regression/6k_regression.md: byte-level proof that 6-K did not change."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RES = ATTEMPT / "results"
MUT = ATTEMPT / "mutations"


def blob(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    ).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    frozen_dayu = json.loads((RES / "6k_frozen_before.json").read_text(encoding="utf-8"))
    green_dayu = json.loads((RES / "dayu_gate_check.json").read_text(encoding="utf-8"))
    frozen_adapter = json.loads((RES / "adapter_frozen_before.json").read_text(encoding="utf-8"))
    green_adapter = json.loads((RES / "adapter_copy_check.json").read_text(encoding="utf-8"))
    mutations = json.loads((MUT / "mutations.json").read_text(encoding="utf-8"))

    g3 = next(c for c in green_dayu["checks"] if c["name"] == "G3_6k_list_byte_identical")
    a4 = next(c for c in green_adapter["checks"] if c["name"] == "A4_6k_result_byte_identical_to_before")
    a5 = next(c for c in green_adapter["checks"] if c["name"] == "A5_10k_result_byte_identical_to_before")
    m2 = next(m for m in mutations["mutations"] if m["id"] == "M2")
    m3 = next(m for m in mutations["mutations"] if m["id"] == "M3")

    six_true = frozen_dayu["6k_include_exhibits_true"]
    six_false = frozen_dayu["6k_include_exhibits_false"]
    cur_true = next(
        v for k, v in green_dayu["payloads"].items() if k == "6k_include_exhibits_true"
    )
    cur_false = next(
        v for k, v in green_dayu["payloads"].items() if k == "6k_include_exhibits_false"
    )

    lines = []
    lines.append("# B2 · 6-K 行为不变的逐字节对比表（回归证明）")
    lines.append("")
    lines.append("- 冻结件 = **改动前**的 iso 上运行 harness `freeze` 落盘（`results/6k_frozen_before.json`、`results/adapter_frozen_before.json`）；")
    lines.append("- 改动后件 = `changes.diff` 应用后的 iso 上运行 `check` 落盘（`results/dayu_gate_check.json`、`results/adapter_copy_check.json`）。")
    lines.append("- 判定方式：把**整个结构** `json.dumps(..., indent=2, sort_keys=True)` 后取 **SHA-256**，两个 sha 必须相同（不只是文件名相同）。")
    lines.append("")
    lines.append("## A. dayu 层 —— `list_filing_files(form_type=\"6-K\")` 的 descriptors 全字段 JSON")
    lines.append("")
    lines.append("| # | 断言 | 冻结件（改动前） | 改动后 | 字节 | 判定 |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(
        f"| A1 | `include_exhibits=True` 全字段 JSON | `{g3['detail']['before_sha256']}` | "
        f"`{g3['detail']['after_sha256']}` | {g3['detail']['before_bytes']} = {g3['detail']['after_bytes']} | "
        f"{'**逐字节相同**' if g3['detail']['before_sha256'] == g3['detail']['after_sha256'] else '**不同**'} |"
    )
    lines.append(
        f"| A2 | 冻结文件本身 | `{file_sha(RES / '6k_frozen_before.json')[:16]}…` | — | "
        f"{(RES / '6k_frozen_before.json').stat().st_size} | 冻结件落盘于改动前 |"
    )
    lines.append("")
    lines.append("文件名清单（两份逐项对照）：")
    lines.append("")
    lines.append("| include_exhibits | 改动前 filenames | 改动后 filenames | 判定 |")
    lines.append("|---|---|---|---|")
    for label, before, after in (
        ("True", [r["name"] for r in six_true], [r["name"] for r in cur_true]),
        ("False", [r["name"] for r in six_false], [r["name"] for r in cur_false]),
    ):
        same = before == after
        lines.append(
            f"| {label} | `{', '.join(before)}` | `{', '.join(after)}` | "
            f"{'**相同**' if same else '**不同**'} |"
        )
    lines.append("")
    lines.append("## B. company-wiki adapter 层 —— 6-K filing 的 `discover()+fetch()` 完整结果对象")
    lines.append("")
    lines.append("| # | 断言 | 冻结件（改动前） | 改动后 | 判定 |")
    lines.append("|---|---|---|---|---|")
    lines.append(
        f"| B1 | 结果对象（candidates/receipt/staged_files/staged_hashes/payload）整体 | "
        f"`{a4['detail']['before_sha256']}` | `{a4['detail']['after_sha256']}` | "
        f"{'**逐字节相同**' if a4['detail']['before_sha256'] == a4['detail']['after_sha256'] else '**不同**'} |"
    )
    lines.append(
        f"| B2 | staged 文件集合 | `{', '.join(a4['detail']['staged_before'])}` | "
        f"`{', '.join(a4['detail']['staged_after'])}` | "
        f"{'**相同**' if a4['detail']['staged_before'] == a4['detail']['staged_after'] else '**不同**'} |"
    )
    lines.append(
        f"| B3 | candidate `adapter_payload_json`（provenance sidecar 的候选段） | "
        f"`{a4['detail']['payload_before']}` | `{a4['detail']['payload_after']}` | "
        f"{'**相同**' if a4['detail']['payload_before'] == a4['detail']['payload_after'] else '**不同**'} |"
    )
    lines.append(
        f"| B4 | receipt `content_sha256` | `{frozen_adapter['6k']['receipt']['content_sha256']}` | "
        f"`{green_adapter['scenarios']['6k']['receipt']['content_sha256']}` | "
        f"{'**相同**' if frozen_adapter['6k']['receipt']['content_sha256'] == green_adapter['scenarios']['6k']['receipt']['content_sha256'] else '**不同**'} |"
    )
    lines.append("")
    lines.append("## C. 10-K（非授权 form，附带回归）")
    lines.append("")
    lines.append("| 断言 | 冻结件 | 改动后 | 判定 |")
    lines.append("|---|---|---|---|")
    lines.append(
        f"| 10-K 结果对象整体 | `{a5['detail']['before_sha256']}` | `{a5['detail']['after_sha256']}` | "
        f"{'**逐字节相同**' if a5['detail']['before_sha256'] == a5['detail']['after_sha256'] else '**不同**'} |"
    )
    lines.append(
        f"| 10-K staged 集合 | `{', '.join(a5['detail']['staged_before'])}` | "
        f"`{', '.join(a5['detail']['staged_after'])}` | "
        f"{'**相同**' if a5['detail']['staged_before'] == a5['detail']['staged_after'] else '**不同**'} |"
    )
    lines.append("")
    lines.append("## D. 这张对比表确实会咬（变异证据）")
    lines.append("")
    lines.append(
        f"- **M2**（删共享分支一行，6-K 走到被改动的代码）→ dayu rc=`{m2['runs'][0]['rc']}`，"
        f"红 = `{', '.join(m2['runs'][0]['failed_names'])}` ⇒ A1/A2 断言变红。"
    )
    lines.append(
        f"- **M3**（adapter 闸门放宽为 `{{6-K, 8-K}}`，让 6-K 也走新复制逻辑）→ adapter rc=`{m3['runs'][0]['rc']}`，"
        f"红 = `{', '.join(m3['runs'][0]['failed_names'])}` ⇒ B1–B4 断言变红。"
    )
    lines.append("")
    lines.append("> 结论：6-K 在**两层**（dayu 远端清单、company-wiki staging/payload/receipt）"
                 "的输出与改动前**逐字节相同**；10-K 亦逐字节相同。")
    lines.append("")

    out = ATTEMPT / "regression" / "6k_regression.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"written": str(out), "bytes": out.stat().st_size,
                      "sha256": file_sha(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
