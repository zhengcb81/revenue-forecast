# FC-1203 WU 卡片 — 模块边界和 API 收敛（dead helper 清零 + extractive summarizer 注册裁决）

> 创建 2026-08-12。Owner: 三仓（主体 company-wiki）。前置：FC-1202 accepted（registry 依赖）。无 execution lock。
> Scope 决策：Interpretation A（findings 59）——只做「删除 + API 收敛 + 注册裁决」，生产热路径函数拆分归 FC-1204 复杂度 ratchet；R9/R2-R5 资产禁删。

## 1. 删除清单（全部经 AST+grep 验证零生产调用者）

| 符号 | 位置 | 被替代者 | 测试处置 |
|---|---|---|---|
| `evaluate_candidate` | admission.py:244 | `evaluate_admission`（scanner 消费的生产入口） | 从 3 个测试删除用法 |
| `validate_normalized_filing` | normalized_meta.py:57 | 零调用者（canonical_hash 仍生产使用，保留） | 删对应测试 |
| `entity_resolver.py` 整模块 | entity_resolver.py | 零生产 import | 删模块 + 测试 |
| `restore.py` 整模块 | restore.py | `store.restore_document` + CLI restore（生产路径） | 删模块 + 测试（先验证 store 路径测试齐全） |
| `validate_flag_state` / `atomic_rollback` | flags.py:41/59 | runtime_policy.py CAS（FC-202/203） | 删函数 + test_policy_and_flags/test_rollback_drills 中旧机制用例；wu905 一次性脚本同步清理调用 |
| `reuse_latest_policy.py` 整模块 | reuse_latest_policy.py | close_gap 自带 policy binding（实施时验证） | 删模块 + 测试 |

## 2. extractive summarizer 裁决：注册 + v2 元数据（不删）

- 事实（findings 59）：`summarize_catalog` 有生产 CLI 入口（service.py:155 → CLI summarize + run pipeline），但产物因三重缺陷永不可绑定：INSERT 缺 schema_version 列值、generator 未注册、created_at 非 ISO-Z。
- 交付（FC-906-a 同构模式）：① GENERATOR_REGISTRY 注册 `source_catalog_extractive_summary`（版本取 models.py）；② INSERT 写 schema_version 列 + metadata 双写；③ created_at → `strftime('%Y-%m-%dT%H:%M:%SZ','now')`；④ 新 contract 测试（summarize 产物 validate_artifact REUSABLE）；⑤ 合同文档 `03_change_contract_fc1203.md` 记录裁决与理由。

## 3. 新门测试（mutation 目标）

`tests/contract/test_fc1203_dead_helpers_absent.py`：断言已删符号**不存在**（模块导入后 `not hasattr` / 模块 import 失败为预期）。M 类变异 = 复活任一死 helper → 门测试红。删除行为本身由全量套件锁定（删除对象零生产调用者 = 行为零变化）。

## 4. 禁删清单（本卡记录，防误删）

- R2/R3 资产：policy_2x.py（v2 cutover 等待发布波次）
- R3-R5 资产：canary_registry.py、dropbox_governance.py（+replay 工具）
- R9 backlog（FC-1201 frozen allowlist）：backfill_v2.run_backfill、portfolio_promoter.py、v1 scanner
- 证据/历史：`_replay` 工具、drift_patrol.py、54 个一次性脚本、wu905 脚本（仅清对已删函数的调用）
- revenue：generate_input_template.py FIXME 占位符（模板设计）

## 5. exit gate 判定（Interpretation A）

- 关键 dead helper=0（6 组删除 + 门测试钉住）✓
- API 收敛核实：service↔resolver 方向、filing 薄客户端、revenue 无 import 环——已在 HEAD 成立，记录不改 ✓
- extractive summarizer 产物可绑定（注册 + v2 元数据 + REUSABLE 测试）✓
- 行为零变化（删除对象零生产调用者；注册裁决只使已有 CLI 产物可复用）✓
- 生产热路径拆分 = FC-1204 范围（ratchet 驱动），本卡明确 ✓

## 6. TDD 步骤

1. RED：门测试（符号尚存在 → 红）；summarizer 绑定测试（产物 unreusable → 红）。
2. GREEN：删除 + 注册修复。
3. MUTATION：M1~M6 逐个复活死 helper → 门测试死；M7 摘注册 → 绑定测试死。
4. 全量 wiki 套件零新失败（pre-existing 2×PORT-01 除外）；filing/revenue 如受影响跑对应 targeted。
5. schema-2.0 receipt → 干净 worktree 独立 reviewer（F-6 规则）→ can_accept。

## 7. 不变式

- 「绝不伪造」：删除必须基于「零生产调用者」的机器证据（grep 交叉验证），不凭印象。
- 删除即永久：删前记录符号完整签名 + 测试证据（本卡），rollback = revert commit。
- 生产数据零写入/删除；worker 无需重启（本次不动 producer 写路径——summarizer 由 CLI 按需调用）。
