# ADR WU-203：复用与最新语义（exact/latest 状态机）

> 计划版本：2.1-full-refactor-execution-cards | 状态：冻结（contract_frozen）

## 不变量

1. **exact**：只解析指定 period/revision；命中有效 handle → REUSED，discovery=network=download=0，也不做 latest discovery。
2. **exact 未命中且无下载授权** → NOT_FOUND + gap reason；绝不"顺便"下载。
3. **latest**：先聚合全部允许 root 的现有覆盖，再只读 metadata discovery；gap = discovered − covered，covered 永不出现在 gap。
4. **旧财报永不因新财报删除**；同期间更正版按 revision/accepted_at 排序，保留 supersession 链。
5. **indexed ≠ reusable**：仅 active、capture-ready、路径存在、hash 正确、root policy 允许的 handle 可返回。
6. **下载授权绑定** immutable GapPlan hash + policy/config hash + 目标 canonical 路径 + 时效；计划变化后旧授权失效。

## 校验

```bash
python -m pytest audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_reuse_latest_policy.py -q
# 11 passed：exact 三态、latest 只补缺期、covered 不入 gap、授权 hash/过期失效、GapPlan 确定性 hash
```
