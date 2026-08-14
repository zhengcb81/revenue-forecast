"""ZR-001: assemble ``drift_ledger.json`` from fresh replay evidence.

Reads the evidence files produced by the replay scripts, verifies their
triplet binding, classifies every production counterexample, validates
successor references against the frozen CA/ZR DAG, and writes the ledger
into ``receipts/ZR-001/drift_ledger.json`` with a canonical content hash.

Usage:  python -B assurance/unified_completion/replays/zr001_build_ledger.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "assurance" / "unified_completion"))

from uc.dag import load_dag  # noqa: E402

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
LEDGER_PATH = (
    REPO_ROOT
    / "assurance"
    / "unified_completion"
    / "receipts"
    / "ZR-001"
    / "drift_ledger.json"
)

FROZEN_TRIPLET = {
    "revenue": "dc41ef335b0c71fc22610201b235a33528d3e950",
    "filing": "83c638e76e40890262746cdf02b6df495dcb4031",
    "wiki": "ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875",
}

CLASSIFICATIONS = frozenset(
    {"still-failing", "already-satisfied", "superseded", "blocked"}
)

# The replay window's first evidence timestamp; frozen so ledger rebuilds are
# byte-deterministic and ``--verify`` can re-derive the exact same hash.
FROZEN_AT_UTC = "2026-08-14T02:19:00+00:00"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_evidence(name: str) -> dict:
    path = EVIDENCE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"evidence missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


_HEAD_TO_REPO = {
    "revenue_head": "revenue",
    "filing_head": "filing",
    "wiki_head": "wiki",
}


def check_triplet_binding(evidence: dict, key: str) -> None:
    head = evidence.get(key)
    repo = _HEAD_TO_REPO[key]
    if head != FROZEN_TRIPLET[repo]:
        raise ValueError(
            f"{key} drift in evidence: {head!r} != {FROZEN_TRIPLET[repo]!r}"
        )


def build_items() -> tuple[list[dict], dict[str, str], dict]:
    r1 = load_evidence("r1_generator_schema_drift.json")
    r2 = load_evidence("r2_validate_only_writes_registry.json")
    r3 = load_evidence("r3_draft_renderer_gate_mismatch.json")
    r4 = load_evidence("r4_publication_non_transactional.json")
    w1 = load_evidence("w1_catalog_read_path_writes.json")
    w2 = load_evidence("w2_artifact_lineage.json")
    w5 = load_evidence("w5_zijin_prompt_review.json")
    d1 = load_evidence("d1_sidecar_false_positives.json")
    d2 = load_evidence("d2_dayu_only_filings.json")
    d3 = load_evidence("d3_dropbox_summary_review_gap.json")
    f1 = load_evidence("f1_external_root_default_rejected.json")
    f2 = load_evidence("f2_lock_error_misclassified.json")
    snapshot = load_evidence("zr001_catalog_snapshot.json")

    check_triplet_binding(r1, "revenue_head")
    check_triplet_binding(r2, "revenue_head")
    check_triplet_binding(r3, "revenue_head")
    check_triplet_binding(r4, "revenue_head")
    check_triplet_binding(w1, "wiki_head")
    check_triplet_binding(f1, "filing_head")
    check_triplet_binding(f2, "filing_head")

    items: list[dict] = [
        {
            "id": "ZR001-R1",
            "family": "revenue_generator",
            "title": "官方 generator 骨架仍被 linter/engine 拒绝",
            "classification": "still-failing",
            "observed": (
                f"generator rc=0 且 schema_version={r1['generator_schema_version']!r}，"
                f"linter rc={r1['linter_rc']}，engine --validate-only rc={r1['engine_validate_rc']}，"
                f"{r1['engine_error_line_count']} 条违规（缺 management_targets、not_checked 状态、"
                "gate 以 TypeError: 'NoneType' object is not iterable 崩溃）。"
                "注：08-12 审计的 3.6/3.7 版本漂移已部分收敛（骨架现在输出 3.7），"
                "但 generator/lint 的 --help 仍自称 schema 3.6，且生成物仍不可用。"
            ),
            "evidence": "r1_generator_schema_drift.json",
            "successors": ["ZR-701", "ZR-702", "ZR-104"],
            "source_findings": ["rebaseline 发现 023", "08-12 发现 075"],
        },
        {
            "id": "ZR001-R2",
            "family": "revenue_validate_only",
            "title": "--validate-only 对有效输入返回 0 却创建 publication registry",
            "classification": "still-failing",
            "observed": (
                f"CLI rc={r2['cli_rc']} 输出 'valid'，但 registry 从无到有，"
                f"大小 {r2['registry_size_bytes']} bytes、{r2['registry_row_count']} 行。"
            ),
            "evidence": "r2_validate_only_writes_registry.json",
            "successors": ["ZR-704", "ZR-705", "CA-302"],
            "source_findings": ["rebaseline 发现 023", "current_state_audit §4.3"],
        },
        {
            "id": "ZR001-R3",
            "family": "draft_renderer",
            "title": "合法 draft 被公共 renderer 拒绝（draft gate_ids=[] vs formal gate 集合）",
            "classification": "still-failing",
            "observed": (
                f"run_forecast(mode='draft') 的 receipt gate_ids={r3['draft_gate_ids']!r}，"
                f"render_markdown 报 {r3['renderer_error']!r}。"
            ),
            "evidence": "r3_draft_renderer_gate_mismatch.json",
            "successors": ["ZR-704", "ZR-705"],
            "source_findings": ["rebaseline 发现 023", "current_state_audit §4.4"],
        },
        {
            "id": "ZR001-R4",
            "family": "revenue_publication",
            "title": "formal publication 先注册后写文件：失败留孤儿行，重复运行追加重复行",
            "classification": "still-failing",
            "observed": (
                f"注入输出写入失败时 rc={r4['fault_run_rc']}、输出未写、"
                f"registry 仍留 {r4['fault_run_orphan_registry_rows']} 行；"
                f"同一输入两次成功运行得 {r4['repeat_run_registry_rows']} 行（重复注册）。"
            ),
            "evidence": "r4_publication_non_transactional.json",
            "successors": ["ZR-710"],
            "source_findings": ["rebaseline 发现 023", "current_state_audit §4.5"],
        },
        {
            "id": "ZR001-W1",
            "family": "zijin_exact_reuse",
            "title": "读路径 CatalogStore 构造即写：不存在 DB 被创建、OS 只读 DB 上 resolve 失败",
            "classification": "still-failing",
            "observed": (
                f"构造不存在路径的 CatalogStore 创建 {w1['w1a']['db_size_bytes']} bytes、"
                f"journal_mode={w1['w1a']['journal_mode']}、{w1['w1a']['table_count']} 张表的库；"
                f"OS 只读文件上再次构造报 OperationalError: {w1['w1b']['error']!r}。"
            ),
            "evidence": "w1_catalog_read_path_writes.json",
            "successors": ["ZR-201", "ZR-202", "ZR-203", "ZR-206"],
            "source_findings": ["08-12 发现 036/038", "current_state_audit §2.1"],
        },
        {
            "id": "ZR001-W2",
            "family": "old_artifact",
            "title": "artifact lineage：completed normalized/summary 的 schema+source SHA 绑定覆盖率极低",
            "classification": "still-failing",
            "observed": (
                f"normalized 共 {w2['normalized_total']}、带绑定 {w2['normalized_with_binding']}；"
                f"summary 共 {w2['summary_total']}、带绑定 {w2['summary_with_binding']}（真实 catalog 只读统计）。"
            ),
            "evidence": "w2_artifact_lineage.json",
            "successors": ["ZR-304", "ZR-305", "CA-302"],
            "source_findings": ["current_state_audit §2.6", "08-12 发现 033/044"],
        },
        {
            "id": "ZR001-W3",
            "family": "old_artifact",
            "title": "shadow binding 无消费者：生产 bundle 读 artifacts，backfill 写 artifact_bindings",
            "classification": "still-failing",
            "observed": (
                "代码级：service.query_source_bundle/artifact 查询全部 FROM artifacts "
                "（service.py:410/495），artifact_bindings 只有 artifact_backfill.py 写入，"
                "无生产读取路径。"
            ),
            "evidence": "w1_catalog_read_path_writes.json",
            "successors": ["ZR-305"],
            "source_findings": ["current_state_audit §2.7"],
        },
        {
            "id": "ZR001-W4",
            "family": "old_artifact",
            "title": "producer telemetry 是 INSERT 触发器代理：按 artifact_role 推断 parser/LLM，无法表达 attempt/failure/retry/cache",
            "classification": "still-failing",
            "observed": (
                "代码级：trg_artifact_producer_event（store.py:339-356）在 artifacts INSERT 后"
                "按 artifact_role 归类 event_type=parser/llm/other，不记录真实调用边界。"
            ),
            "evidence": "w1_catalog_read_path_writes.json",
            "successors": ["ZR-304"],
            "source_findings": ["rebaseline 发现 021", "current_state_audit §2.8"],
        },
        {
            "id": "ZR001-W5",
            "family": "zijin_exact_reuse",
            "title": "紫金 FY2024/FY2025 年报无 prompt-injection review：复用成功但消费被 revenue 安全门拒绝",
            "classification": "still-failing",
            "observed": (
                f"真实 catalog：紫金标题文档共 {w5['zijin_docs_total']}、"
                f"带 prompt_injection_review 的 {w5['zijin_docs_with_review']}。"
                "08-12 第三轮生产路径因此报 not_reviewed 而 fail-closed（发现 070）。"
            ),
            "evidence": "w5_zijin_prompt_review.json",
            "successors": ["ZR-302", "ZR-303", "ZR-507"],
            "source_findings": ["08-12 发现 070/073", "rebaseline P06"],
        },
        {
            "id": "ZR001-F1",
            "family": "dropbox",
            "title": "外部 root handle 被默认拒绝：生产 validate_handle 调用未传 policy snapshot，退回 companies containment",
            "classification": "still-failing",
            "observed": (
                f"hermetic 生产函数重放：Dropbox 型 canonical handle 被拒 "
                f"({f1['message']!r})；调用点 fetch_filing.py:{f1['production_call_site']['line']} "
                "未传 policy_snapshot。"
            ),
            "evidence": "f1_external_root_default_rejected.json",
            "successors": ["ZR-401", "ZR-404", "ZR-405", "ZR-409", "ZR-806"],
            "source_findings": ["current_state_audit §3.1", "rebaseline P06"],
        },
        {
            "id": "ZR001-F2",
            "family": "zijin_exact_reuse",
            "title": "raw 'database is locked' 被标 fatal：retry 环只认结构化 catalog_locked",
            "classification": "still-failing",
            "observed": (
                "hermetic 分类重放：OperationalError('database is locked') → "
                f"code={f2['outcomes']['raw_sqlite_operational_error']['code']}、"
                f"retryable={f2['outcomes']['raw_sqlite_operational_error']['retryable']}；"
                "结构化 CatalogOperationLockedError 对照组正确映射 catalog_locked（retryable）。"
            ),
            "evidence": "f2_lock_error_misclassified.json",
            "successors": ["ZR-204", "ZR-205"],
            "source_findings": ["08-12 发现 037/039", "current_state_audit §3.6"],
        },
        {
            "id": "ZR001-D1",
            "family": "dropbox",
            "title": "sidecar 污染：.pdf.source JSON 被当作独立财报文档",
            "classification": "still-failing",
            "observed": (
                f"真实 catalog：标题以 '.pdf.source' 结尾的文档共 {d1['sidecar_titled_docs_total']}、"
                f"其中被归为 filing kind 的 {d1['sidecar_titled_as_filing_kinds']}、"
                f"published_date 为空的 {d1['sidecar_filing_kinds_with_null_published_date']}。"
            ),
            "evidence": "d1_sidecar_false_positives.json",
            "successors": ["ZR-501", "ZR-502", "ZR-509"],
            "source_findings": ["rebaseline 发现 018", "08-12 发现 035"],
        },
        {
            "id": "ZR001-D2",
            "family": "dropbox",
            "title": "dayu-only active filing 因 companies 默认 containment 在消费边界被拒",
            "classification": "still-failing",
            "observed": (
                f"真实 catalog：dayu_portfolio 独有 active filing 文档 {d2['dayu_only_active_filing_docs']}，"
                f"分布 {d2['by_kind']}。与 ZR001-F1 合成：这些文件今天无法从 filing/revenue 复用。"
            ),
            "evidence": "d2_dayu_only_filings.json",
            "successors": ["ZR-401", "ZR-402", "ZR-403", "ZR-405", "ZR-409", "ZR-806"],
            "source_findings": ["rebaseline 发现 018", "current_state_audit §2/3"],
        },
        {
            "id": "ZR001-D3",
            "family": "dropbox",
            "title": "Dropbox 已完成 LLM summary 的 prompt review 覆盖缺口（P0 隐私）",
            "classification": "still-failing",
            "observed": (
                f"真实 catalog：dropbox_stock active 文档 {d3['dropbox_active_location_docs']}、"
                f"带 completed summary 的 {d3['dropbox_docs_with_completed_summary']}、"
                f"其中带 prompt_injection_review 的 {d3['dropbox_docs_with_prompt_review']}；"
                f"generator 分布 {d3['summary_generators']}。"
            ),
            "evidence": "d3_dropbox_summary_review_gap.json",
            "successors": ["ZR-301", "ZR-302", "ZR-507", "CA-302"],
            "source_findings": ["rebaseline 发现 022", "rebaseline P06/P07"],
        },
        {
            "id": "ZR001-D4",
            "family": "dropbox",
            "title": "Dropbox-only 功能层全链不可达（旧 FC-505 canary 证据 superseded）",
            "classification": "still-failing",
            "observed": (
                "由 ZR001-W1 + ZR001-F1 + ZR001-D2 合成：物理排他的 Dropbox-only/dayu-only "
                "文件从 revenue 入口不可复用。旧 FC-505 回执声称的 REUSED_EXACT 走的是 "
                "companies 副本路径（08-12 发现 052 已复证），该旧证据只作历史证据，"
                "不得再作为 Dropbox-only 通过依据。"
            ),
            "evidence": "f1_external_root_default_rejected.json",
            "successors": [
                "ZR-401",
                "ZR-402",
                "ZR-403",
                "ZR-404",
                "ZR-405",
                "ZR-409",
                "ZR-806",
            ],
            "source_findings": [
                "rebaseline 发现 012/018",
                "completion_audit FC-501~505",
                "08-12 发现 052",
            ],
        },
    ]
    evidence_binding = {
        name: sha256_file(EVIDENCE_DIR / name)
        for name in sorted(
            {
                "r1_generator_schema_drift.json",
                "r2_validate_only_writes_registry.json",
                "r3_draft_renderer_gate_mismatch.json",
                "r4_publication_non_transactional.json",
                "w1_catalog_read_path_writes.json",
                "w2_artifact_lineage.json",
                "w5_zijin_prompt_review.json",
                "d1_sidecar_false_positives.json",
                "d2_dayu_only_filings.json",
                "d3_dropbox_summary_review_gap.json",
                "f1_external_root_default_rejected.json",
                "f2_lock_error_misclassified.json",
                "zr001_catalog_snapshot.json",
            }
        )
    }
    snapshot_binding = snapshot.get("catalog", {})
    replay_dir = Path(__file__).resolve().parent
    replay_binding = {
        name: sha256_file(replay_dir / name)
        for name in sorted(
            {
                "zr001_revenue.py",
                "zr001_wiki.py",
                "zr001_filing.py",
                "zr001_catalog_sql.py",
            }
        )
    }
    return items, evidence_binding, replay_binding, snapshot_binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        action="store_true",
        help="recompute the canonical hash and compare with the stored ledger",
    )
    args = parser.parse_args()
    items, evidence_binding, replay_binding, snapshot_binding = build_items()
    dag = load_dag(REPO_ROOT)
    problems: list[str] = []
    for item in items:
        if item["classification"] not in CLASSIFICATIONS:
            problems.append(
                f"{item['id']}: bad classification {item['classification']!r}"
            )
        unknown = [unit for unit in item["successors"] if unit not in dag]
        if unknown:
            problems.append(f"{item['id']}: unknown successors {unknown}")
    if problems:
        for problem in problems:
            print(f"LEDGER-GATE: {problem}", file=sys.stderr)
        return 2
    if snapshot_binding.get("unchanged_by_this_script") is not True:
        print(
            "LEDGER-GATE: real catalog size/mtime changed during read-only queries",
            file=sys.stderr,
        )
        return 2
    summary = {
        classification: sum(
            1 for item in items if item["classification"] == classification
        )
        for classification in sorted(CLASSIFICATIONS)
    }
    families = sorted({item["family"] for item in items})
    payload: dict = {
        "schema_version": 1,
        "unit": "ZR-001",
        "plan_id": "TRI-REPO-COMPLETION-2026-08-13-R1",
        "frozen_at_utc": FROZEN_AT_UTC,
        "triplet": {
            "revenue": FROZEN_TRIPLET["revenue"],
            "filing": FROZEN_TRIPLET["filing"],
            "wiki": FROZEN_TRIPLET["wiki"],
            "branches": {"revenue": "fcap", "filing": "fcap", "wiki": "fcap"},
        },
        "governance_reuse": (
            "README §7：ZR-001 的治理部分（计划锁、triplet 冻结、历史处置）由 "
            "CA-001~004 实现并已 accepted；本 ledger 只承载产品 drift 重放。"
        ),
        "replay_discipline": (
            "每项均为 2026-08-14 在冻结 triplet 上的新重放；旧 receipt 仅作来源发现引用。"
        ),
        "families": families,
        "items": items,
        "summary": summary,
        "evidence_binding": evidence_binding,
        "replay_binding": replay_binding,
        "catalog_fingerprint": snapshot_binding,
    }
    ledger_hash = canonical_sha256(payload)
    if args.verify:
        if not LEDGER_PATH.exists():
            print("LEDGER-GATE: ledger missing for verify", file=sys.stderr)
            return 1
        stored = json.loads(LEDGER_PATH.read_text(encoding="utf-8")).get(
            "ledger_sha256"
        )
        if stored != ledger_hash:
            print(
                f"LEDGER-GATE: drift — recomputed {ledger_hash} != stored {stored}",
                file=sys.stderr,
            )
            return 2
        print(json.dumps({"verify": "ok", "ledger_sha256": ledger_hash}, indent=2))
        return 0
    payload["ledger_sha256"] = ledger_hash
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps({"ledger": str(LEDGER_PATH), "ledger_sha256": ledger_hash}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
