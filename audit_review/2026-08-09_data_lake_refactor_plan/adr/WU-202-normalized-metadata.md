# ADR WU-202：NormalizedFilingMetadata v2 契约

> 计划版本：2.1-full-refactor-execution-cards | 状态：冻结（contract_frozen）

## 必需字段

- schema_version（1.0/2.0 支持；unknown fail closed）
- 身份：canonical_entity_id + market + security_id（display_name 仅辅助）
- 文档：document_kind（annual/quarterly/semi_annual/regulatory_filing）、
  regulatory_form、fiscal_year、period_end、period_kind
- 来源：provider、provider_document_id、source_url（缺失需等价 provenance）、
  published_at、filed_at、accepted_at
- 修订：language、is_amended、revision_id、supersedes_document_id
- 完整性：content_sha256、metadata_sha256（= canonical semantic hash，绑定检测）
- 归一化：adapter_id、adapter_version、normalization_status
- 每字段 evidence：origin、source_pointer（必须可解析到字段）、asserted_value
  （冲突即拒）、assertion_method、confidence、observed_at

## 不进语义身份

root_id、绝对路径、来源名（company_raw/dayu/dropbox）、扫描时间——留在
location/source 记录；canonical hash 排除（NON_SEMANTIC）。

## 空值规则

- identity/kind/period/content hash 任一缺失 → 不 capture-ready。
- source_url 缺失但 provider_document_id+hash 组合可作等价 provenance（profile 明列）。
- 不可解析/冲突字段 → indexed + reason code，不静默猜测。

## 校验

```bash
python -m pytest audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_normalized_meta.py -q
# 14 passed（META-01~12 + hash 绑定 + canonical 排除）
```
