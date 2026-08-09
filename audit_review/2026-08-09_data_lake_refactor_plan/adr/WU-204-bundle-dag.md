# ADR WU-204：SourceBundle 与 ArtifactHandle v2（artifact DAG 契约）

> 计划版本：2.1-full-refactor-execution-cards | 状态：冻结（contract_frozen）

## DAG

```
normalized ← markdown ← summary ← consumer_analysis
normalized ← sections
```

## 失效规则（最小重算集合，确定性）

| 变化 | 失效 |
|---|---|
| 原文 hash 变 | 全部 artifact |
| normalized producer/schema 变 | normalized + 全部下游 |
| summary producer/prompt/model/config 变 | summary + 依赖 summary 的下游（不重跑 PDF parser） |
| evidence binding / section schema 变 | 仅依赖该 binding/section 的角色 |
| filing retired/quarantined/missing | 全部不可复用 |

## 选择规则

- selected/rejected 各自确定性排序 + 拒绝 reason；不隐藏旧工件。
- input_document_hash 不匹配、status 非 completed、unknown schema → 拒绝。
- filing 与 artifact 的 catalog snapshot 不一致 → STALE_BUNDLE。

## 校验

```bash
python -m pytest audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_artifact_dag.py -q
# 11 passed（B-01~12 vectors）
```
