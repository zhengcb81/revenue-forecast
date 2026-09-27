# R9 执行包 — v1/legacy 代码删除（预置 RED 门测试，窗口满足后执行）

> 进入条件：WU-1500 close gate `close_allowed=true`（2 个连续 ≥24h 零 hit 窗口；period 6 已入账首个零 hit，预计 08-15T05:28Z 后满足）。
> 执行协议：RED 门测试先行（本包已预置）→ 删除 → GREEN → 全量 → mutation（复活删除对象必须红）→ receipt → 独立 reviewer → can_accept。

## 1. 删除清单（全部在 v2 全 active 生产态下无调用者）

| 对象 | 位置 | 依据 |
|---|---|---|
| `_scan_root_v1` + v1 分派分支 | scanner.py（FC-1201 卡：L170/181/283/377/452/981/984 七处） | v2_scan_shadow=true 生产生效；v1 只读回退不再需要（bridge 已关） |
| scanner facade 的 v1 默认分支 | scanner.py:1357-1360（"Default = v1"） | 同上——默认改 v2 |
| `backfill_v2.py`（run_backfill/classify_bucket 被 dropbox_governance 引用需核对） | 整模块 | architecture_gate R9 backlog |
| `portfolio_promoter.py` + CLI import-portfolio | 整模块 + cli 接线 | R9 backlog |
| `visibility_bridge.py` legacy bridge 循环 | 整模块（resolver._source_metadata 的 bridge 路径 + flags.legacy_bridge_enabled） | bridge OFF；_source_metadata 的 legacy_bridge_allowed 参数路径删除 |
| `legacy_close_gate.py` + observer 的 close-gate 部分 | 整模块（observer 在 R9 后退役） | WU-1500 使命完成 |
| flags.py `legacy_bridge_enabled` 依赖链 | FLAGS/REQUIRES/EXCLUDES 条目 | bridge 删除后不再有该 flag |

## 2. 预置 RED 门测试（本包提交，R9 执行时转绿）

`company-wiki/tests/contract/test_r9_v1_removal_gate.py`（FC-1203 dead-helper 门同款）：
- 模块不可导入：backfill_v2 / portfolio_promoter / visibility_bridge / legacy_close_gate
- 属性不存在：scanner._scan_root_v1
- flags.FLAGS 无 legacy_bridge_enabled
- architecture_gate `_ROOT_HARDCODE_ALLOWED_FILES` 收缩：scanner.py 移出（v1 分支删除后 token-free）

## 3. 级联核对（执行时逐项）

- resolver._source_metadata 的 legacy_bridge_allowed 参数 → 删除后调用者（resolver 内部 + tests）更新
- dropbox_governance 对 classify_bucket 的 import → 删除 backfill 后内联或迁移
- cli.py import-portfolio 删除 → parser 移除 + 相关测试删除
- observer 的 close-gate 块 → observer 保留 canary matrix 部分还是整体退役（R9 后无需观察）
- FC-1201 frozen ratchet 更新（allowlist 只缩）

## 4. 完成后

- 全量 wiki 套件零新失败
- 门测试转绿 + mutation（复活任一删除对象 → 红）
- schema-2.0 receipt + 独立 reviewer + can_accept
- Phase 14 波次账本 R9 → COMPLETE → Phase 15 解锁
