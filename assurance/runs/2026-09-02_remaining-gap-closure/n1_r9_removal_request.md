# N-1 授权申请：FC-1501~1505 关闭 + R9 legacy 分批删除执行

> **申请人**：MiMo-v2.5-pro（AI Agent，Xiaomi MiMo Team）
> **日期**：2026-09-03
> **状态**：待批准（执行前置 = 两个 ≥24h 零 hit 观测窗口，见 §5）
> **关联**：B-1 缺口（task_plan.md）、CA-304 部署动作（R9 真实删除）、ZR-1009 C3（N-1 批准目标）、FC-705 close-gate

## 1. 背景与机器状态

2026-09-02 剩余缺口计划的机器层已全部闭环（closure-report 实测）：

- **units**：machine_valid=112 / legacy=72 / incomplete=**0**；state.json **117/117 accepted、plan_status=completed**
- **scenarios**：197/197 passed、unsatisfied=**0**（含 LT/UJ 真实数据 E2E，wiki 50b44ba）
- **终局**：CA-306 terminal closure accepted；TERMINAL_NOTICE.json 在位（6 个旧计划目录 + 根级）
- **旧计划 verdict=incomplete 的剩余 reasons 全部属于本申请范围**：26 contradicted（successor 全 accepted，仅需确认）+ 5 pending closure items（FC-1501~1505，本申请 A 部分）+ R9 frozen（本申请 B 部分）+ legacy receipt sets（grandfathered 历史，迁移属 CA-304 范围，冻结不动）

## 2. 申请范围 A：FC-1501~1505 N-1 关闭确认

frozen `legacy_disposition.json` 中 5 个 closure items（class=P，旧计划自己的待办）映射如下，successor 全部已 accepted：

| FC-150x | successor | 状态 |
|---|---|---|
| FC-1501 | CA-107/CA-301 | accepted |
| FC-1502 | CA-108/CA-302 | accepted |
| FC-1503 | CA-109/CA-303 | accepted |
| FC-1504 | CA-304/CA-305 | accepted |
| FC-1505 | CA-306/CA-201 | accepted |

请求 owner 确认：旧计划 5 项待办由新链 successor 覆盖成立，**N-1 批准关闭**（旧目录冻结不改写，关闭只记录在 approval ledger）。

## 3. 申请范围 B：R9 legacy 分批删除执行授权

### 3.1 当前 legacy 残留（2026-09-03 legacy-gate 实测）

legacy-gate 三仓扫描 verdict=`callers_found`，findings 全部集中在 revenue `.github/workflows/quality.yml`：

| finding | tool | 位置 | 内容 |
|---|---|---|---|
| LEGACY-CALLER-001 | closure_gate | quality.yml L50/54/79/83/120/124/166 | `--ignore=tests/test_zr1101_closure_gate.py`、`tools/tests/test_closure_gate.py`（legacy 测试从 CI 豁免） |
| LEGACY-CALLER-002 | verify_closure_ledger | quality.yml **L133** | 真实调用 `python tools/verify_closure_ledger.py --ledger audit_review/.../closure_ledger.json`（旧计划语义门在 CI 执行） |
| LEGACY-CALLER-003 | closure_ledger | quality.yml L53/82/123/133/168 | `--ignore=tests/test_zr1105_closure_ledger.py` 等 |

### 3.2 删除批次（CA-304 部署动作，每批独立 commit + 全矩阵回归 + 可 revert）

- **批 1（CI 接线）**：quality.yml 移除 L133 真实调用 + 移除 closure_gate/closure_ledger 相关 `--ignore` 条目（L50/53/54/79/82/83/120/123/124/166）
- **批 2（revenue legacy 工具/测试）**：删除 `tools/verify_closure_ledger.py`、`tests/test_zr1101_closure_gate.py`、`tests/test_zr1105_closure_ledger.py`、`tools/tests/test_closure_gate.py`（及其 archive 需要时）
- **批 3（wiki 产品层，执行时以 final_ratchet/legacy-gate 复扫清单为准）**：`_scan_root_v1` 分支、legacy bridge/flags、无生产读者 backfill/promoter
- **冻结边界（不删除）**：`audit_review/` 6 个旧计划目录（CA-306 C2 稳定快照）、`closure_ledger.json` 历史文件本身、unified_completion receipts（CA-306 C2 历史不可变）

### 3.3 删除门（CA-304 C1/C3/C4 + FC-705）

- [ ] **两个连续 ≥24h 零 hit 观测窗口**（FC-705 close_gate_allowed，periods ledger 由 legacy_observer 逐期累积）
- [ ] **legacy-gate 复扫 verdict=无 findings**（批 1 后即应达成；ZR-1009 C1 门语义：callers_found = NOT-approved）
- [ ] **final_ratchet 零残留**（scan_legacy/scan_encoding/hardcode，当前树已零命中）
- [ ] 每批三仓 CI 全绿 + 相邻回归零回退

## 4. 风险与回滚

| 风险 | 级别 | 缓解 |
|---|---|---|
| 删除破坏 CI | 低 | 每批独立 commit；CI 全绿才继续下一批 |
| 删除后需恢复 | 低 | git revert 独立清理提交（批内可逆） |
| 观测窗口被污染 | 低 | 窗口未满前不执行任何删除（fail-closed） |
| 旧计划历史被误删 | 无 | 冻结目录/历史 JSON 明确排除在批次外 |

## 5. 执行前置状态（2026-09-03 实测）

- **观测窗口：尚未开始累积**。daily T2 调度存在注册参数缺陷（已修 revenue 3552795：注册任务裸 `--run-daily` 曾因 required 参数 argparse 失败 exit=2——窗口永远无法累积；修复后三参数默认生产路径，ZR-902 16 passed + 兄弟套件 52 passed）。任务注册状态在非提权会话不可见（schtasks 列表 202 个任务零命中；/tn 查询 Access denied）——**需 owner 提权确认/重注册**。
- **观测推进接线（已修 revenue 630b554）**：发现注册任务只跑 T2 runner、从不调用 legacy_observer（periods 账本写入者）→ 窗口仍永不累积。现 run-daily 自动推进 period（next_period_number max+1；fresh/corrupt 从 1 重启 fail-closed）+ 只读 observer 调用（mode=ro，仅写 assurance/runs/legacy_periods.json）。冒烟测试通过（periods 推进 + close-gate 评估正常）。
- **新发现阻塞（观测语义）**：真实 catalog 冒烟 = sample 接缝记录 **54/62 legacy_bridge_hits**，而 62 个采样文档中仅 32 个真正无 v2 覆盖（30 个已有 v2 normalized artifact 也被计 hit）→ sample 接缝用默认 `reader="v1"` + `legacy_bridge_allowed=True`，**不走生产快照门，高估 hits**；canary-matrix（生产 resolver 接缝 + 快照）= **0 hits**（4 canary 全 reused_exact）。→ 窗口在 sample 语义下永不为零，删除门正确 fail-closed。**下一缺口 = 快照门控 legacy_observer 的 sample pass**（reader/epoch/cohorts/legacy_bridge_allowed 取自 runtime_policy 快照，与 canary 路径同源）——完成后重测应得 0 hits（生产语义：bridge 已禁用，无实际流量）。
- **最早窗口满足时间**：任务确认注册 + 快照门控修复后，首个 03:30 运行起两个连续 ≥24h 零 hit 窗口 → 最早约 **修复后第 3 个 03:30 运行**具备删除资格。
- **N-1（范围 A）与执行授权（范围 B）批准后**：窗口满足即按 §3.2 分批执行，执行过程记录于本 run 的 progress.md。

## 6. 验收标准

- [ ] owner 批准记录（范围 A + B，见下）
- [ ] revenue_daily_t2 / revenue_weekly_t3 提权查询 registered；daily_manifest.json 首个 fresh 记录出现
- [ ] periods ledger 出现 ≥2 个 completed ≥24h 零 hit 窗口（close_gate_allowed=True）
- [ ] legacy-gate 复扫 findings=0；quality.yml L133 调用已移除
- [ ] R9 批 1~3 完成，三仓 CI 全绿，无冻结目录改动
- [ ] FC-150x N-1 关闭已记录

---

## 批准记录

- **批准人**：郑曾波（repo owner）
- **批准时间**：2026-09-03
- **批准内容**：**批准 A+B**——① FC-1501~1505 N-1 关闭确认（successor 链 CA-107~109/CA-201/CA-301~306 全 accepted，旧目录冻结不改写）；② R9 legacy 分批删除执行授权（批 1 quality.yml 移除 verify_closure_ledger L133 真实调用 + closure_gate/closure_ledger 相关 --ignore 条目；批 2 revenue legacy 工具/测试删除；批 3 wiki 产品层 _scan_root_v1/bridge/flags/无读者 backfill/promoter——以执行时 final_ratchet/legacy-gate 复扫清单为准）。每批独立 commit + 三仓 CI 全绿 + 可 revert；`audit_review/` 冻结目录与历史 closure_ledger.json 不删除。
- **执行前置（仍生效）**：B 的实际删除等到两个连续 ≥24h 零 hit 观测窗口满足后开始（最早 2026-09-06 03:30 后）；owner 已确认 revenue_daily_t2 / revenue_weekly_t3 任务已注册（2026-09-03，提权会话 query registered；非提权会话不可见属正常 ACL）；daily 任务 argparse 缺陷已修复（revenue 3552795，2026-09-03 推送）。
- **执行状态**：待观测窗口满足。当前阻塞 = 观测语义（sample 接缝 54/62 hits vs canary 生产语义 0 hits）——下一缺口为快照门控 observer sample pass（wiki 变更），完成后窗口方可为零；删除最早窗口 = 修复后第 3 个 03:30 运行后开始批 1。
