# Schema 3.6 → 3.7 迁移（revenue-forecast 4.0.0）

生效版本：4.0.0（2026-08-08）。规则 0.3.10 全额执行。

## 变更内容

| 变更 | 类型 | 说明 |
|------|------|------|
| 输入锚点绑定不变式 | 验证收紧（非输入契约） | `input_sha256` 必须等于被验证输入（嵌入或显式）的 canonical hash（R1.1）。旧合法工件（绑定自洽）不受影响。 |
| publication_receipt 新增 `attestation_status` 字段 | 输出契约（新增可选字段） | `host_signed` / `unattested`（R2.1）。无签名器环境产出 `unattested`，invest-* 默认拒绝。旧 receipt（无该字段）仍可通过结构验证。 |
| 发布登记处 | 输出侧新机制 | `artifacts/registry/publications.jsonl` append-only 登记（R1.2）。旧工件无登记记录 → invest 策略 `legacy_unregistered` 兼容（R1.2 迁移段）。 |
| 输出完整性检查 | 验证收紧 | current-schema 工件必须包含引擎全部产出键；历史序列必须有序；parameter_trace 必须与输入一致（R6.2，mutation patrol 发现）。 |

## 输入侧必填字段

3.6 → 3.7 **无新增输入必填字段**（`tests/test_input_contract_migration.py` 守卫验证）。
历史遗留：3.5 → 3.6 的 `host_receipt`（capture 必填）为无迁移路径的破坏性变更
（v3.10.0 时代，N-08）；4.0.0 起由输入契约守卫显式红着并标注，禁止再发生同类变更。

## 迁移路径

- 输入文档：`"schema_version": "3.6"` → `"3.7"`（无字段改动）。
- 旧 3.6 工件（engine 3.10.0）：read-only 验证支持（`schema_compatibility.py`
  emit 矩阵含 3.10.0/4.0.0）；不能作为新 formal 产出。
- 生成器：`generate_input_template.py` 自动输出 3.7。

## 回滚

`git revert` 版本 bump 提交；schema 常量回到 3.6 即恢复（3.7 工件不再被验证，
但 3.7 未被发布到外部，无兼容负担）。
