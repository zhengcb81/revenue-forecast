# R9 批 3（wiki 产品层）执行清单 — 2026-09-09 备妥，**待授权，不自动执行**

> 🔴 **2026-09-10 更正：3a 前提不成立，未执行任何删除。**
> 先前"`artifact_backfill.py` 零生产读者"的结论基于**过窄的 grep**（只查 src/scripts 的 import），**已证伪**。完整扫描（逐符号 + 计划语料 + 冻结卡 + ratchet）显示：
> ① 该模块自带**运维 CLI**：`python -m company_wiki.source_catalog.artifact_backfill --catalog … --mode dry-run|apply`（`artifact_backfill.py:305 def main()`，argparse 暴露 dry-run/apply），`assurance/fc/FC-901/11_implementer_receipt.json` 明确记载「run_artifact_backfill 的 production caller 就是**同模块的 CLI main()**」（FC-901 的 caller≥1 正是由此成立）；
> ② 被 **3 个契约测试**直接导入：`tests/contract/test_zr305_legacy_migration.py`、`test_zr1005_artifact_backfill.py`、`test_source_catalog_artifact_backfill.py`；
> ③ **FC-906 工作单元卡把它列为 Forbidden files**：`assurance/fc/FC-906/00_wu_card_a.md:24`「`artifact_backfill.py`（FC-901 工具，**不改**）」；
> ④ 冻结的 v5 基线 `baseline/plan/test_acceptance_plan.md` 有 **ZR1005-C1~C4** 验收行指向其测试；
> ⑤ 复杂度/覆盖率 ratchet 为其登记 `37` / `79`；`.github/workflows/ci.yml:53` 把 zr1005 测试列在 CI ignore 名单。
> → **按本清单自己的规则（"无替代路径的不删"、"冻结边界绝不触碰"），3a 不予执行。** owner 于 **2026-09-10 正式撤销 3a**（裁定：`artifact_backfill.py` 认定为受 FC-906 卡片保护的运维工具，不再是删除候选）。若将来确要退役该运维能力，那是**能力退役**（需同时处理 3 个测试、ratchet、FC-906 卡片与运维替代方案），不是死代码清理，且应与 v2 迁移收尾一并决定。**批 3 自此只剩 3b/3c。**

> 关联：[n1_r9_removal_request.md](n1_r9_removal_request.md)（owner A+B 批准原文）、[gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md) §6.2/§6.4、
> [progress.md](progress.md) 2026-09-06「批 3 延后（owner 决策）」。
> 本清单只做**执行前备料**：不改代码、不删文件、不注册任务、不跑生产。任何删除动作都需要届时 owner 明确再次确认。

## 1. 两道门（必须同时满足）

| 门 | 判据 | 当前（2026-09-09 22:00 运行后） | 预计满足 |
|---|---|---|---|
| **A 技术门（FC-705）** | 权威账本 `company-wiki/.source_catalog/legacy_periods.json` 的 `close_gate.close_allowed == true`：最后两个**已完成** period 连续、各 ≥24h、`legacy_bridge_hits == 0` | **false** —— 最后两个已完成 = P7（23:59:41 ✗）+ P8（24:00:11 ✓） | **2026-09-10 22:00 运行后**（P8+P9，P9 自 09-09T21:00:21Z 起） |
| **B owner 政策门** | owner 2026-09-06 决策：批 3 整体**延后**至 v2 迁移完全稳定，作为 architectural cleanup 再做 | **未批准执行** | 需 owner 届时明确确认 |

**任一门未满足 → 不执行任何删除。** 本清单不构成授权。

## 2. 范围再清点（2026-09-09 实测调用者，替换 09-02 的旧口径）

09-02 申请把批 3 写成「`_scan_root_v1` 分支、legacy bridge/flags、**无生产读者** backfill/promoter」。今晚逐符号实测后，**该口径只有一条仍然成立**：

| 候选 | 生产调用者（实测） | 判定 |
|---|---|---|
| `_scan_root_v1` | `scanner.py:272` 定义、`scanner.py:1401` 生产分派；`shadow_parity.py:94`、`trace_parity.py:206` 影子/追踪对账；`tests/contract/test_company_raw_adapter.py` | **非死代码**：v1 扫描路径仍是策略回退与对账基线 |
| `legacy_bridge_enabled` | `flags.py:26/37`、`resolver.py:322`、`architecture_gate.py:127/139/278` | **非死代码**：迁移期 bridge + 回滚机制，architecture gate 显式建模 |
| `backfill_v2` | `dropbox_governance.py:22` 导入 `classify_bucket`（生产治理链）；多个 ratchet/契约测试 | **有生产读者**：09-02 的「无生产读者」表述已过时 |
| `portfolio_promoter` | `cli.py:27` 导入（CLI 面）；`architecture_gate.py:181` | **有 CLI 读者** |
| `artifact_backfill` | **自带运维 CLI**（`artifact_backfill.py:305 main()` → `python -m …artifact_backfill --mode dry-run\|apply`，FC-901 收据记载其 production caller 即此 CLI）；**3 个契约测试**导入（zr305 / zr1005 / test_source_catalog_artifact_backfill）；**FC-906 卡片列为 Forbidden（"FC-901 工具，不改"）**；冻结 v5 基线有 ZR1005-C1~C4 验收行；ratchet 37/79 | 🔴 **2026-09-10 更正：不是零读者**（先前结论基于过窄 grep）。**不予删除**；退役属"能力退役"另议 |

**结论**：批 3 不是"按清单机械删除"，而是"先退役 v1 路径/迁移期机制的架构清理"。执行时必须：
1. 重新以 `legacy-gate` + `final_ratchet` 实测清单为准（§3）；
2. 对每一项给出「谁在调用 → 替代路径 → 回滚方案」，无替代路径的不删；
3. ~~`artifact_backfill.py` 可作为最小、独立、可 revert 的第一小步~~ → **2026-09-10 作废**：该模块有运维 CLI + 契约测试 + FC-906「不改」标注，**不构成最小死代码步**（证据见文首更正块）。目前**没有任何一项**满足"零读者 + 无冻结约束"的机械删除条件。

## 3. 执行前检查（只读，逐条留档输出）

```powershell
# 1) FC-705 技术门（权威账本）
python -c "import json;d=json.load(open(r'C:\Users\郑曾波\Projects\company-wiki\.source_catalog\legacy_periods.json',encoding='utf-8'));print(json.dumps(d['close_gate'],ensure_ascii=False));print([ (p['period'],p.get('started_at'),p.get('ended_at'),p.get('legacy_bridge_hits')) for p in d['periods']])"

# 2) legacy-gate 三仓复扫（期望 findings=0 / isolated=true）
cd C:\Users\郑曾波\Projects\revenue-forecast
python -c "import sys,json;sys.path.insert(0,'assurance/unified_completion');from pathlib import Path;from uc.legacy_gate import report;roots={'revenue':Path('.').resolve(),'filing':Path('../filing-fetch').resolve(),'wiki':Path('../company-wiki').resolve()};print(json.dumps(report(roots),ensure_ascii=False,indent=2))"

# 3) final_ratchet 零残留（scanners：legacy/encoding/hardcode）
python tools\final_ratchet.py --scanners-only --print-json

# 4) 逐符号调用者复扫（把结果贴进执行记录）
cd C:\Users\郑曾波\Projects\company-wiki
Select-String -Path src\**\*.py,scripts\*.py,tests\**\*.py -Pattern '_scan_root_v1','legacy_bridge_enabled','backfill_v2','artifact_backfill','portfolio_promoter'
```

门 A 通过后仍需门 B（owner 确认）才能进入 §4。

## 4. 执行顺序（仅在两道门都满足后）

1. **冻结基线**：记录三仓 HEAD、`legacy-gate`/`final_ratchet` 输出、批 3 每个候选的调用者清单。
2. **拆分批次**（2026-09-10 修订：3a 已由 owner 撤销）
   - ~~3a：`artifact_backfill.py`（零生产读者）+ 其测试/ratchet 条目~~ → **已撤销**（owner 2026-09-10）：该模块有运维 CLI、3 个契约测试、FC-906「不改」标注与冻结基线验收行（见文首更正块），**不是死代码**，不再作为删除候选；
   - 3b：`_scan_root_v1` + `shadow_parity`/`trace_parity` 的 v1 对账路径（需替代方案）；
   - 3c：`legacy_bridge_enabled` + `flags`/`resolver`/`architecture_gate` 的 bridge 分支（需回滚方案）。
   每小批**独立 commit**、独立 revert。**当前没有任何小批具备"零读者 + 无冻结约束"的机械删除条件**——3b/3c 都需要先给出替代路径与回滚。
3. **逐批验证**：wiki 全量 pytest（含 contract）→ 三仓 CI 全绿 → `legacy-gate` 复扫 findings=0 → `final_ratchet` 零残留。
4. **文档**：更新本清单、[progress.md](progress.md)、R4 侧 `r4-unit-remediation-map.md` 的 CA-304/ZR-1009 行（仅记退役，不从旧勾选领取）。

## 5. 冻结边界（绝不触碰）

- `audit_review/` 6 个旧计划目录（CA-306 C2 稳定快照）
- `audit_review/2026-08-08_adversarial_plan/closure_ledger.json` 等历史 JSON
- unified_completion receipts / 历史批准字节
- v5 冻结集（`docs/plans/source-catalog-worker-recovery-v5-2026-09-03/`，51 项）
- `legacy_periods.json` 历史 period 记录（只读）
- **FC-906 工作单元卡的 Forbidden 标注**：`artifact_handle.py`（绑定门，schema 契约已冻结）与 `artifact_backfill.py`（"FC-901 工具，不改"）——退役它们属于改写既有工作单元合同，不是清理

## 6. 回滚

每个小批一个 commit，`git revert <sha>` 即可；涉及数据/配置的（若有）单独写回滚步骤。批 3 预期**纯代码/测试**，无生产数据变更。

## 7. 验收

- [ ] 门 A：`close_gate_allowed == true`（实测输出留档）
- [ ] 门 B：owner 明确确认执行范围与拆分
- [ ] 每小批：三仓 CI 全绿 + `legacy-gate` findings=0 + `final_ratchet` 零残留
- [ ] 每小批可 revert 且已演练（至少确认 revert 后测试恢复）
- [ ] 冻结目录/历史字节零改动
- [ ] 退役记录写入 R4 映射表（CA-304/ZR-1009 行）

## 8. 明确不做

- 不因日历到期自动执行；不等同于"门 A 满足即可删"。
- 不删除仍有生产/CLI/对账调用者的模块（`_scan_root_v1`/`legacy_bridge_enabled`/`backfill_v2`/`portfolio_promoter`）——除非先给出替代路径与回滚。
- 不改冻结目录、不改历史 receipt、不重签批准、不恢复 worker。
