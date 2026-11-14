"""Add the package-checklist fields the handoff schema example requires.

The §7 handoff example carries `owner_job_id` (top level of the inputs entry is
`job_id`, but §5.5 asks for the owner job id), a `lint` verdict string, and the
source capture facts; this script adds them from the delivered artifacts instead
of retyping them, and records the package's compliance matrix plus every
deviation from a literal package requirement.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs/mongodb-fy2025-input.json"
HANDOFF = ROOT / "handoff.json"

COMPLIANCE = [
    {"clause": "§1 两份完整 schema 3.7 输入", "status": "PARTIAL", "detail": "MongoDB delivered; Alibaba NOT_RUN (acquisition blocker)"},
    {"clause": "§1 两份 rf-job/1 作业跑到终态", "status": "PARTIAL", "detail": "rfjob-20261108-eb9f2a3ed336 succeeded; Alibaba job not submitted"},
    {"clause": "§2.1 sources + 真实 capture（9 字段 + host_receipt）", "status": "PASS", "detail": "company-wiki verified read of the registered original, snapshot b3788068…, receipt recomputes; capture_method=local_document"},
    {"clause": "§2.2 每参数有 evidence claim；revenue_basis 可选", "status": "PASS", "detail": "31 parameters (4 reported_fact exact_value + 27 analyst_assumption rationale_support); revenue_basis declared"},
    {"clause": "§2.3 历史收入按年 + 口径声明", "status": "PASS", "detail": "FY2023/FY2024/FY2025 from Note 9 + consolidated statements; rf-revenue-basis/1 total/as_reported/fiscal_year"},
    {"clause": "§2.4 分段与披露一致 + 情景集一致", "status": "PASS", "detail": "Atlas-related / Other subscription / Services exactly the disclosed disaggregation; low/base/high match the job scenario_set"},
    {"clause": "§2.5 校验链 lint → fix_hashes → validate-only", "status": "PASS", "detail": "3/3 exit 0, 'valid'; evidence bound to input sha256 d82f9b45…"},
    {"clause": "§2.6 可比性声明（无对象则 null）", "status": "PASS", "detail": "business_boundary_id/comparison_group_id/basis_claim_ids deliberately undeclared; the engine's YoY 'comparability not verified' note is disclosed, not papered over"},
    {"clause": "§3.1 每家 ≤1.00 USD，limit 映射", "status": "PASS", "detail": "limits_ref=owner-approved-1usd, max_cost_usd='1.00', max_new_downloads=0, attempts=3; actual 0.00"},
    {"clause": "§3.2 不发明数字", "status": "PASS", "detail": "independent review: no fabricated number, receipt or hash; growth magnitudes labelled analyst assumptions"},
    {"clause": "§3.3 不改既有引擎", "status": "PASS", "detail": "git diff d347c4ab..HEAD touches only .planning/rf-input-prep-01/"},
    {"clause": "§3.4 不冒充已完成", "status": "PARTIAL", "detail": "Alibaba + catalog + management targets registered as NOT_RUN with causes; G-m5-EXT-01 explicitly not cleared"},
    {"clause": "§3.5 独立分支 + worktree，不碰 Dashboard", "status": "PASS", "detail": "codex/rf-input-prep-01 in its own worktree; no Dashboard or company-wiki file changed"},
    {"clause": "§4 rf-job/1 submit body 全字段", "status": "PASS", "detail": "schema_version/workflow/company_query/information_as_of/horizon_end_year/scenario_set/source_snapshot_ids/idempotency_key/limits_ref/forecast_input"},
    {"clause": "§4 catalog 登记走显式管理命令", "status": "NOT_RUN", "detail": "requires the B34 trusted research-admission package; not produced by a facade run"},
    {"clause": "§5.1 输入 + 三步校验留档", "status": "PASS", "detail": "inputs/… + evidence/mdb-{lint,fix-hashes,validate-only}.stdout.txt + evidence/mdb-validation-chain.json"},
    {"clause": "§5.2 两份真实作业终态 + JobView 留档", "status": "PARTIAL", "detail": "one succeeded JobView with cost 0.00 / known; Alibaba absent"},
    {"clause": "§5.3 失败样本（自然发生）", "status": "PASS", "detail": "v1 job source-1 failed with filing-fetch config_error, then resumed; failed JobView and stage stderr preserved"},
    {"clause": "§5.4 catalog 登记后 list-reports 可读 + 报告ID + result_sha256", "status": "NOT_RUN", "detail": "list-reports exit 2 owner_root_missing; result_sha256 available, catalog report id not"},
    {"clause": "§5.5 Dashboard 消费字段写入 handoff", "status": "PARTIAL", "detail": "owner_job_id/input hash/result hash present; catalog report id null"},
    {"clause": "§5.6 NOT_RUN 逐条带原因", "status": "PASS", "detail": "handoff.json not_delivered ×3 + findings F-01…F-14"},
    {"clause": "§6 分支/worktree/commit/commit 前 branch 校验/不推远端", "status": "PASS", "detail": "Conventional Commits; branch checked before every commit; no remote push"},
    {"clause": "§7 handoff.md + handoff.json 格式", "status": "PASS", "detail": "both present; fields added by this record (owner_job_id, lint, capture, limits, deviations)"},
    {"clause": "§8-1 独立重审 0 OPEN P1/P2", "status": "PASS", "detail": "three rounds; final P1=0 P2=0, P3=4 disclosed"},
    {"clause": "§8-2 PWF 更新", "status": "PASS", "detail": "task_plan/progress/findings updated per node"},
    {"clause": "§8-3 并线或显式交接任务", "status": "PASS", "detail": "main lacks the facade CLI; explicit merge task recorded with conditions and owner"},
]

DEVIATIONS = [
    {
        "id": "D1-base-commit",
        "package_rule": "§6 基线=你仓当前已发布主线HEAD",
        "actual": "base = codex/rf-job-facade-01 tip d347c4ab, not main 90c562ac",
        "why": "main does not contain scripts/rf_job_cli.py, so the §4 submission contract cannot run there; the facade handoff itself records that main cannot be safely merged yet",
        "needs_operator": True,
    },
    {
        "id": "D2-template-not-used",
        "package_rule": "§2 模板 generate_input_template.py",
        "actual": "input built by .planning/rf-input-prep-01/build_mdb_input.py (replayable) and then verified field-for-field against a freshly generated template",
        "why": "the template emits FIXME placeholders and hashes that must be replaced anyway; the raw build script keeps every value traceable to the filing",
        "verification": "template-vs-delivered key diff: only '_comment' absent (a template instruction string); no template field missing",
        "needs_operator": False,
    },
    {
        "id": "D3-capture-method",
        "package_rule": "§2.1 capture 必须来自真实抓取（browser_open/等既有机制）",
        "actual": "capture_method=local_document, tool=company-wiki-source-version-reader, action=verified_read",
        "why": "this is the revenue-forecast skill's documented source route (filing-fetch -> company-wiki verified open of a registered original); no browser session was involved",
        "needs_operator": False,
    },
    {
        "id": "D4-no-acquisition-limits",
        "package_rule": "§3.1 max_bytes/timeout_seconds 按既有部署惯例设保守值",
        "actual": "deployment request_template uses filing_intent=reuse_only, which forbids acquisition_limits; stage timeouts are 300/600/120 s and max_new_downloads=0",
        "why": "the filing-fetch contract rejects acquisition_limits on a reuse_only request; the Alibaba probe route that did ask for a download carried max_bytes 8,000,000 / 120 s / 0.00 USD",
        "needs_operator": False,
    },
    {
        "id": "D5-content-vs-handoff-commit",
        "package_rule": "§7 head_commit = <最终commit>",
        "actual": "head_commit/release_tag pin the self-contained content commit 1009258075…; the handoff record itself lives in later commits on the same branch",
        "why": "a commit cannot contain its own SHA; pinning the content commit keeps input, job artifacts and evidence resolvable from one commit",
        "needs_operator": False,
    },
]


def main() -> int:
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    capture = document["sources"][0]["capture"]
    payload = json.loads(HANDOFF.read_text(encoding="utf-8"))
    entry = payload["inputs"][0]

    ordered: dict = {}
    for key, value in entry.items():
        ordered[key] = value
        if key == "job_id":
            ordered["owner_job_id"] = value
        if key == "validation":
            ordered["lint"] = value["lint"]
        if key == "source_snapshot_sha256":
            ordered["source_capture"] = {
                "capture_method": capture["capture_method"],
                "tool_name": capture["tool_name"],
                "tool_call_id": capture["tool_call_id"],
                "captured_date": capture["captured_date"],
                "snapshot_sha256": capture["snapshot_sha256"],
                "receipt_sha256": capture["receipt_sha256"],
                "content_treatment": capture["content_treatment"],
                "prompt_injection_status": capture["prompt_injection_status"],
                "host_receipt_issuer": capture["host_receipt"]["issuer"],
                "host_receipt_action": capture["host_receipt"]["action"],
            }
    payload["inputs"][0] = ordered
    payload["limits"] = {
        "limits_ref": "owner-approved-1usd",
        "max_cost_usd": "1.00",
        "max_new_downloads": 0,
        "max_attempts_per_stage": 3,
        "stage_timeouts_seconds": {"source": 300, "compute": 600, "publication": 120},
        "actual_cost_usd": "0.00",
    }
    payload["deviations"] = DEVIATIONS
    payload["package_compliance"] = COMPLIANCE
    HANDOFF.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "inputs_owner_job_id": payload["inputs"][0]["owner_job_id"],
                "compliance": {s: sum(1 for row in COMPLIANCE if row["status"] == s) for s in ("PASS", "PARTIAL", "NOT_RUN")},
                "deviations": len(DEVIATIONS),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
