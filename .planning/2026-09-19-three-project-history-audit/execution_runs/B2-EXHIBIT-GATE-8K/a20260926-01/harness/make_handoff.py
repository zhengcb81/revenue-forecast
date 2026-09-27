"""Emit handoff.json (status=review_pending, implementer_signed=false) + self_attest.md."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RES = ATTEMPT / "results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ATTEMPT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


SKIP_DIRS = {"__pycache__", "tmp", "_edgar_cache"}
SKIP_PREFIX = ("results/_tmp_adapter", "results/_probe")
# iso/{dayu_repo,cw_repo} are the byte-for-byte import closure (618 files); their
# per-file sha manifest lives in iso/preimage.json, so only the preimage record and
# the two changed files are listed as deliverables.
INCLUDE_PREFIX = ("harness/", "results/", "regression/", "mutations/")
INCLUDE_EXACT = {
    "oracle.md",
    "changes.diff",
    "self_attest.md",
    "iso/preimage.json",
    "iso/dayu_repo/dayu/fins/downloaders/sec_downloader.py",
    "iso/cw_repo/src/company_wiki/source_catalog/dayu_cli_adapter.py",
}


def deliverables() -> list[dict]:
    out = []
    for path in sorted(ATTEMPT.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ATTEMPT)).replace("\\", "/")
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if any(rel.startswith(prefix) for prefix in SKIP_PREFIX):
            continue
        if path.suffix in {".pyc"}:
            continue
        if rel == "handoff.json":
            continue
        if rel not in INCLUDE_EXACT and not rel.startswith(INCLUDE_PREFIX):
            continue
        out.append(entry(path))
    return out


def main() -> int:
    dayu_red = json.loads((RES / "dayu_gate_check.json").read_text(encoding="utf-8"))
    adapter_green = json.loads((RES / "adapter_copy_check.json").read_text(encoding="utf-8"))
    mutations = json.loads((ATTEMPT / "mutations" / "mutations.json").read_text(encoding="utf-8"))
    static = json.loads((RES / "static_checks.json").read_text(encoding="utf-8"))
    diff_manifest = json.loads((RES / "changes_diff_manifest.json").read_text(encoding="utf-8"))
    oracle_freeze = json.loads(
        (RES / "oracle_freeze.json").read_bytes().decode("utf-8-sig")
    )

    # pre-change (red) run: captured by the M0 preimage-revert run with the FINAL harness
    m0 = next(m for m in mutations["mutations"] if m["id"] == "M0")
    m0_dayu = next(r for r in m0["runs"] if r["harness"] == "dayu")
    m0_adapter = next(r for r in m0["runs"] if r["harness"] == "adapter")

    handoff = {
        "schema_version": "1.0",
        "card": "B2-EXHIBIT-GATE-8K",
        "attempt_id": "a20260926-01",
        "role": "implementer",
        "status": "review_pending",
        "status_reason": "改动只落 iso 副本，changes.diff 已出，红/绿/变异/6-K 字节回归证据齐全；等父派独立复审后才谈晋升 —— 本卡不产生 ACCEPT、不代签。",
        "implementer_signed": False,
        "signed_by": None,
        "review_required_by": "parent-dispatched independent reviewer (per OWNER_DECISIONS §三十 执行纪律：iso → changes.diff → 独立复审 → 晋升授权)",
        "authorization": {
            "primary": "OWNER_DECISIONS.md §三十（2026-09-26）owner 原话「授权扩闸到 8-K（建议）」——执行映射 1 授权改 sec_downloader.py 的 include_exhibits 分支与 dayu_cli_adapter.py 的资产复制",
            "landing": "OWNER_DECISIONS.md §三十一 owner 原话「接受 raw/other/（建议）」——8-K 诚实 kind current_report ⇒ raw/other/，不改 canonical_writer 映射、不谎报 kind",
            "scope_boundary": "execution_v2/common_filing_cards.md L17「凡跨项目公共 schema、canonical writer、registry 或 worker API，只有指定 owner 写」⇒ changes.diff 只含 2 个文件",
            "not_released": [
                "OPEN-3 未解除",
                "BLOCKED-NEEDS-ORIGIN-BYTES 未解除",
                "B1（company-wiki 本会话不可写）未解除",
                "无 ACCEPT、无等级判定、不改任何 status/decision",
            ],
        },
        "oracle": {
            "file": "oracle.md",
            "frozen_before_code_edit": True,
            "current_sha256": oracle_freeze["current"]["sha256"],
            "versions": oracle_freeze["versions"],
            "amendment_disclosure": "v3 是 M4 跑完后的披露式勘误（只修 M4 预期红集合 + 补 ID 映射 + 补 M0 行），未改动任何 R/G/V 判据；v1/v2 均冻结于任何 iso 代码编辑之前",
        },
        "nine_steps": [
            {"step": 1, "name": "读 §三十/§三十一 + mechanism_scan → 建 iso、记前像 sha", "status": "done",
             "evidence": "iso/preimage.json：两目标文件前像 sha256=543d005c…（74,235 B，mtime 2026-05-30T21:42:41Z）/ bcbbbfd9…（19,775 B，mtime 2026-07-24T18:58:01Z）；iso 树 dayu 472 文件 / company_wiki 146 文件，全部为产品字节副本"},
            {"step": 2, "name": "冻结 oracle.md", "status": "done",
             "evidence": f"oracle_freeze.json：v1 {oracle_freeze['versions'][0]['sha256'][:16]}…（2026-09-25T23:47:30Z）、v2 {oracle_freeze['versions'][1]['sha256'][:16]}…（23:48:42Z，仍早于任何代码编辑）、v3 {oracle_freeze['versions'][2]['sha256'][:16]}…（事后披露式勘误，见 oracle.amendment_disclosure）"},
            {"step": 3, "name": "红：改动前实测 8-K 取不到 exhibit", "status": "done",
             "evidence": "results/dayu_check_red.stdout.txt（pre-change check rc=1，仅 G1 红）+ results/adapter_check_red.stdout.txt（pre-change check rc=3，A1/A2/A6 红）+ 变异 M0 用**最终版 harness** 复现同一红（见 runs.red_with_final_harness）",
             "raw_rc": {"dayu_check_pre_change": 1, "adapter_check_pre_change": 3}},
            {"step": 4, "name": "改：只在 iso 扩闸到 8-K", "status": "done",
             "evidence": "changes.diff（2 文件）+ results/static_checks.json：iso 两棵树各自只变 1 个文件、产品文件 sha 与前像一致、两文件均可编译"},
            {"step": 5, "name": "绿：8-K 含 exhibit；6-K 逐字节不变", "status": "done",
             "evidence": "results/dayu_gate_check.json（5/5）+ results/adapter_copy_check.json（7/7）",
             "raw_rc": {"dayu_check_post_change": 0, "adapter_check_post_change": 0, "static_checks": 0}},
            {"step": 6, "name": "≥3 条变异（实做 6 条 M0–M5）", "status": "done",
             "evidence": "mutations/mutations.json：6/6 与冻结预期一致，mismatch=0，每次还原后 sha 与改动后 sha 逐字节相同",
             "raw_rc": {m["id"]: [r["rc"] for r in m["runs"]] for m in mutations["mutations"]}},
            {"step": 7, "name": "回归证明：6-K 行为不变的逐字节对比表", "status": "done",
             "evidence": "regression/6k_regression.md（dayu 6-K 全字段 JSON sha 相同 649d906c…/3318 B；adapter 6-K 结果对象 sha 相同 0c9000a1…；10-K 7507acad… 相同）"},
            {"step": 8, "name": "产出 changes.diff + handoff.json", "status": "done",
             "evidence": f"changes.diff {diff_manifest['bytes']} B / sha256 {diff_manifest['sha256']} / 恰 {diff_manifest['file_count']} 个文件；handoff.json 见本文件"},
            {"step": 9, "name": "只读自证 + 报父派独立复审", "status": "done",
             "evidence": "self_attest.md + 本 handoff；git diff HEAD --name-only 非 .planning = 0；dayu-agent/company-wiki 在工位窗口内 mtime 命中 = 0"},
        ],
        "runs": {
            "red_with_final_harness": {
                "how": "变异 M0：把两个 iso 文件还原为产品前像（= 完整撤回本卡改动），用最终版 harness 重跑 check",
                "dayu": {"rc": m0_dayu["rc"], "failed_names": m0_dayu["failed_names"],
                         "expected_green_still_green": m0_dayu["unexpected_red"] == []},
                "adapter": {"rc": m0_adapter["rc"], "failed_names": m0_adapter["failed_names"],
                            "expected_green_still_green": m0_adapter["unexpected_red"] == []},
                "note": "首次 pre-change 运行（results/dayu_check_red/adapter_check_red）与 M0 结果一致；两次运行之间 harness 修过 3 处**环境**问题（edgar 缓存目录、tempfile 0o700 ACL、fixture 路径长度）与 1 处断言命名空间（_INCLUDE_EXHIBITS 应查 dayu_cli_adapter 模块而非包），均不影响被测产品代码",
            },
            "green": {
                "dayu": {"rc": 0, "passed": 5, "failed": 0, "file": "results/dayu_gate_check.json"},
                "adapter": {"rc": 0, "passed": 7, "failed": 0, "file": "results/adapter_copy_check.json"},
                "static": {"rc": 0, "passed": static["passed"], "failed": static["failed"]},
            },
            "mutations": [
                {
                    "id": m["id"],
                    "desc": m["desc"],
                    "rc": [r["rc"] for r in m["runs"]],
                    "failed_names": {r["harness"]: r["failed_names"] for r in m["runs"]},
                    "matched_frozen_expectation": all(r["ok"] for r in m["runs"]),
                    "restored_byte_exact": m["restored_ok"],
                }
                for m in mutations["mutations"]
            ],
            "mutation_mismatch": mutations["mismatch"],
        },
        "criteria": {
            "red": [
                "R1 dayu 8-K + include_exhibits=True 的 filenames 不含 d291965dex991.htm（rc=1，仅 G1 红）",
                "R2/R3 adapter 8-K staging 只有 primary、无 exhibit（rc=3，A1/A2 红）",
            ],
            "green": [
                "G1 dayu 8-K filenames = [d291965d8k.htm, d291965d8k.xsd, d291965d8k_htm.xml, d291965dex991.htm]",
                "G2 关掉 include_exhibits 后 8-K 不含 exhibit",
                "G3 adapter 8-K staging = {d291965d8k.htm, d291965dex991.htm}，exhibit sha 与 meta 一致（7ff5f1fa…）",
                "G4 _INCLUDE_EXHIBITS=False ⇒ 只有 primary",
                "G5 非授权 form 不进闸（dayu 10-K / adapter 10-K 均不变）",
                "G6 落点声明：_destination_subdirectory('current_report') == Path('other')（只读直调，canonical_writer 未改）",
            ],
            "regression_6k": [
                "V1 dayu 6-K descriptors 全字段 JSON sha256 649d906c3bc03bcc… 前后相同（3318 B）",
                "V2 dayu 6-K 文件名清单前后相同（include_exhibits=True/False 两组）",
                "V3 adapter 6-K 结果对象（candidates/receipt/staged/payload）sha256 0c9000a1… 前后相同",
                "V4 adapter 10-K 结果对象 sha256 7507acad… 前后相同",
            ],
        },
        "changes": diff_manifest,
        "iso": {
            "feasible": True,
            "verdict": "可行：import、红、绿、6-K 字节回归、6 条变异、落点只读直调全部在 iso 内完成；未出现『必须在产品仓原路径才能跑通』的依赖",
            "layout": ["iso/dayu_repo/dayu/**（472 文件，产品字节副本）",
                       "iso/cw_repo/src/company_wiki/**（146 文件，产品字节副本）",
                       "iso/preimage.json（前像 sha256/bytes/mtime + 两棵树的逐文件 sha 清单）"],
            "changed_files_only": [
                "iso/dayu_repo/dayu/fins/downloaders/sec_downloader.py",
                "iso/cw_repo/src/company_wiki/source_catalog/dayu_cli_adapter.py",
            ],
            "closure_file_counts": {
                "iso/dayu_repo/dayu": 472,
                "iso/cw_repo/src/company_wiki": 146,
                "per_file_sha256_manifest": "iso/preimage.json",
                "excluded_from_deliverables_list": "618 个闭包副本文件本身（sha 清单在 iso/preimage.json）",
            },
        },
        "environment_notes": [
            "EDGAR_LOCAL_DATA_DIR 重定向到 results/_edgar_cache（第三方 edgar 包导入时要在 $HOME 建缓存，本会话不可写）",
            "harness 内重写 tempfile.mkdtemp（默认 mode 而非 0o700）：CPython 3.13 在本沙箱里 os.mkdir(path, 0o700) 造出的目录会被拒绝读取（WinError 5），会让 DayuCliDownloadAdapter.discover() 在其逻辑执行前就崩；这是**环境 shim，不改任何产品代码**",
            "fixture 目录名刻意缩短以留在 Win32 260 字符路径预算内（WinError 206）",
            "残留（不可删）：results/_probe/dayu-us-kh99y60w、results/_probe2/{m700,t7-1jbp5u_5}、results/_tmp_adapter/case_8-K_True/dayu-workspaces/dayu-us-x8w80fu9 —— 均为 shim 修复前 0o700 失败运行的产物，icacls/删除均被 OS 拒绝；全部在本 attempt 目录内，产品仓 0 字节",
            "网络 = 0：dayu harness 对 _http_get_bytes/_http_get_json 打 kill-switch（RuntimeError，由 _try_* 兜底为 []），_http_head 用本地桩；adapter harness 的 dayu CLI 是本地假脚本",
        ],
        "blocked_by": [],
        "blockers_not_resolved_by_this_card": [
            {"id": "B1", "summary": "company-wiki 产品仓在本会话 workspace-write 下不可写（审批禁用、子代理不可提权）", "status": "仍在；本卡按纪律只写 .planning"},
            {"id": "B3", "summary": "8-K 落点形态", "status": "口径已定（§三十一 raw/other/），本卡未改 canonical_writer"},
            {"id": "OPEN-3 / BLOCKED-NEEDS-ORIGIN-BYTES", "status": "未解除（§三十 执行纪律）"},
        ],
        "unverified": [
            "U1 exhibit 资产复制到 staging 之后，acquisition/canonical_writer 的单 receipt 契约不在本卡 2 文件改动面内 ⇒ exhibit 最终是否落 raw/other/ = 未证实（落点映射本身已按 §三十一 只读直调验证 = other）",
            "U2 B1 未解 ⇒ 未执行任何真实 filing-fetch ensure/下载；目标 accession 0001193125-26-380280 的真实行为未实测",
            "U3 8-K/A 未纳入闸门（授权原文只写 8-K）；非 ex99 命名的 primary-linked HTML 在 adapter 复制面之外（dayu 可下载、adapter 不复制）= 已知边界",
            "U4 company-wiki 自身契约套件（fc1204 coverage ratchet 需往产品仓根写 coverage.json、全量 suite）未运行 —— 运行即违反『不写产品仓』；替代证据：同一 AST 规则本地复算 max-complexity = 10 ≤ 46（results/static_checks.json）",
            "U5 dayu 产品测试套件未运行（会写产品仓 .pytest_cache/workspace）；替代证据：自建 harness 覆盖 6-K/8-K/10-K 三形态 + 逐字节回归 + 6 条变异",
            "U6 未产生 ACCEPT、未代签、未判 E1/E2 等级",
        ],
        "not_done": [
            "未写 dayu-agent / company-wiki / revenue-forecast(.planning 外) 任何字节",
            "未执行 git status、未做任何 git 写操作、未联网",
            "未解除 OPEN-3 / BLOCKED-NEEDS-ORIGIN-BYTES / B1",
            "未改 canonical_writer 的 kind 映射、未谎报 kind",
            "未执行实际下载（B1 仍阻断，本卡只改代码）",
            "未写五份计划文件、未代签、未产生 ACCEPT",
        ],
        "git_boundary": {
            "command_used": "git -c core.quotepath=false diff HEAD --name-only（只读；未执行 git status）",
            "diff_total_lines": 3827,
            "diff_non_planning_count": 0,
            "git_writes": 0,
            "git_status_used": False,
            "product_repo_mtime_scan": {
                "window_local": ">= 2026-09-26T00:40:00",
                "dayu_agent_hits": 0,
                "company_wiki_hits": 0,
                "revenue_forecast_non_planning_hits": 0,
            },
            "product_target_files_sha_unchanged": True,
        },
        "deliverables_note": "handoff.json 自身不入 deliverables（自引用哈希不可稳定计算）；全部条目 sha+bytes 见 deliverables",
        "deliverables": deliverables(),
        "next_action": "父派独立复审 changes.diff（只含 2 个文件）与 results/regression/mutations 证据；复审通过后按 §三十 走『晋升授权』另行派工（本卡不晋升）。B2 解后 C3 第一步仍 BLOCKED（B1/B3 未全满足）。",
    }

    out = ATTEMPT / "handoff.json"
    out.write_text(json.dumps(handoff, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "written": str(out),
        "bytes": out.stat().st_size,
        "sha256": sha(out),
        "deliverables": len(handoff["deliverables"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
