# N-1 授权申请：FC-1501~1505 关闭 + R9 legacy 分批删除执行

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> [当前状态总入口](../../../PLANNING_STATUS.md)

> **2026-09-09 状态修正**：GP-006（real-roots 阻断且绿）、GP-008（自然触发闭环）、GP-010（sections 7/7）、N-1/FC-150x、CI 协议两项已关闭；GP-009 monthly 1/1、drill 1/1、daily 3/7、weekly 0/2 自然累积中；FC-705 仍关（P7 窗口差 19 秒）。当前逐项结案与证据见 [gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md)。

## 2026-09-06 最新状态与领取规则（优先于下方全部旧覆盖/命令/批准摘要）

2026-09-08规划覆盖：用户只批准planning调整，不授权实施、重新注册、删除或运行。原痛点审计继续保留，活动整改使用[R4虚拟数据湖计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)及其测试矩阵/旧WP迁移表。A/B本地读取、C生产、D运维、M收入按实际依赖推进，不再叠加旧15包95门。本组只作历史执行/批准来源，不并行领取第二套队列，不把旧批准扩大为新动作许可。

- GP-008参数错误已在revenue HEAD `2ff20d9`修复，注册器现为`run-daily`。旧“代码仍阻塞/必须先改拼写”失效；部署Action及自然触发仍未独立闭环，不自动重注册。
- latest观测daily manifest=`20260905T194055Z`、period=2、ok=true，绑定旧`2cbd585`而非当前HEAD；legacy一个ended_at完成窗口、第二个未完成，close_allowed=false。旧9/3唯一run/零completed不再是最新状态，仍不可按预计日期放行。
- GP-010观测为normalized7/7、review7/7、summary6/7、sections5/7，安全拒绝保留，列表式缺口未闭。kind宽范围历史产物214份与精确7份cohort不是同一范围；按owner已有处置保留，不执行旧“DELETE+重扫即无外部副作用”的回滚说法。
- 117 accepted/197 passed不是原目标完成证明：9/6审计找到required tier、真实消费、业务计算、失败账本和发布等实质反例。历史receipt/批准原字节不改，禁止批量重签来制造当前资格。
- 新H01自动prune归档覆盖风险是worker恢复前置。当前整改全部NOT_IMPLEMENTATION_AUTHORIZED；旧授权不自动包含新scope/新版本。GP/R9历史批准保留，但继续执行需WP01/12/13/14相应门、真实数据E2E和当前精确授权。

以下9/2–9/5内容均为有日期的历史快照，不是新的可执行指令；若与本节冲突按本节及新计划处理。真实报告、完整观察、受控删除未完成，不以文档同步勾成完成。

## 2026-09-05 当前批准与执行状态（覆盖原申请快照）

- A+B已于9/3由owner批准，保留下文批准原文；“待批准”不再适用。
- 未执行删除。9/5已修电源/补跑/22:00条件并记录owner重注册，但daily注册器Action与CLI仍不匹配（--run-daily vs run-daily）；GP-008仍代码阻塞，重注册后的Action/自然触发未独立验证。
- 已有一次手动run与period1 observing，并非从未开始；completed窗口=0、close_allowed=false。撤回固定9/6门开预测，必须实际两个completed且各≥24h、hits=0才可判门。
- 批次唯一口径：revenue批1+2合为一个自洽commit；随后wiki批3独立commit；每个提交全矩阵回归/legacy复扫/可revert。旧“批1→2→3各自commit”被§3.2取代。
- §2历史映射需以下冻结legacy_disposition为准（不改冻结JSON）：FC-1501→CA-107/108/109；FC-1502→CA-301/303；FC-1503→CA-302；FC-1504→CA-206/304；FC-1505→CA-305/306。批准记录继续保留，但不根据错误解释表重签批准。
- 已满足的是owner批准记录；实际task运行验证、完整窗口、删除和最终CI/复扫均不能提前勾选。本次仅文档核对，不触发任何删除/重注册。

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

> **执行清点（2026-09-03，门开后按此机械执行）**：
> **批 1+2 必须合为单一 commit**——quality.yml 的 `--ignore` 条目与 windows job 运行列表（L50/53/54/79/82/83/120/123/124/166/168）引用待删测试文件：先删文件则 CI 引用缺失文件，先改 CI 则 legacy 测试在 windows job 裸跑（必红）。单 commit 自洽、可整体 revert。

- **批 1+2（revenue，单 commit）**：
  - 删除工具：`tools/closure_gate.py`、`tools/closure_ledger.py`、`tools/receipt_validator.py`、`tools/verify_closure_ledger.py`（与 uc/legacy_gate.py 的 LEGACY_TOOL_FILES 排除面一致；已核实 tools+tests 外零导入者）
  - 删除测试：`tests/test_zr1101_closure_gate.py`、`tests/test_zr1105_closure_ledger.py`、`tools/tests/test_closure_gate.py`、`tools/tests/test_receipt_validator.py`、`tools/tests/test_verify_closure_ledger.py`
  - quality.yml 重接线：删除 L103-133 整个 "Closure ledger gate (WU-10.2)" 步骤（verify_closure_ledger L133 真实调用 + PYTEST_LEDGER env 块）；删除 `--ignore` 条目 L50/53/54（pytest 块）、L79/82/83（coverage 块）、L120/123/124（ledger env 块）；删除 windows job 运行列表 L166/168（test_zr1101/test_zr1105）
  - 联动编辑：`tests/test_zr1102_adversarial_audit.py` L118-119 的 collect 节点含 test_zr1101_closure_gate.py → 换为存活测试文件（test-island 审计保持有效）
  - 保留（非 legacy，不动）：`tools/verify_plan_claims.py` + quality.yml L101-102（活 CI 步骤，不在 legacy-gate 注册表）；`compatibility/scenario_coverage.py` + `tests/test_scenario_coverage.py`（新计划门，仅名字与 legacy 注册表撞名）；`tests/test_zr1009_legacy_removal.py`（纪律测试，用 scratch trio 合成 fake closure_gate，不依赖真实工具）
  - 冻结边界：`audit_review/2026-08-08_adversarial_plan/closure_ledger.json` 历史文件不动（删除后仅失去其校验者，历史保持只读展示）
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
- **新发现阻塞（观测语义）**：真实 catalog 冒烟 = sample 接缝记录 **54/62 legacy_bridge_hits**，而 62 个采样文档中仅 32 个真正无 v2 覆盖（30 个已有 v2 normalized artifact 也被计 hit）→ sample 接缝用默认 `reader="v1"` + `legacy_bridge_allowed=True`，**不走生产快照门，高估 hits**；canary-matrix（生产 resolver 接缝 + 快照）= **0 hits**（4 canary 全 reused_exact）。→ 窗口在 sample 语义下永不为零，删除门正确 fail-closed。**已修（wiki 25a8eea）**：observe() 加载生产快照经 resolver_visibility 门控（无快照 = pre-FC-201 默认，与 SourceResolver 同源）；真实 catalog 复测 **sampled=62、legacy_bridge_hits=0**（reader=v2、bridge 禁用、snapshot c773099b）。
- **最早窗口满足时间（2026-09-04 修正）**：09-04 03:30 调度实测未触发（daily_manifest 停留在 09-03 21:11 手动 run1；无 alert 文件）→ owner 当日提权**重新注册** revenue_daily_t2/revenue_weekly_t3。快照门控修复（wiki 25a8eea，hits=0 实证）在位。时间线：**09-05 03:30 run2**（P2 开，P1=6.5h 短窗出局）→ 09-06 03:30 run3（关 P2，24h ✓）→ 09-07 03:30 run4（关 P3，24h ✓）→ **最早 ~09-07 03:30 后 close_gate_allowed=True**，随后开始 R9 批 1~3。
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
- **执行前置（仍生效，2026-09-04 更新）**：B 的实际删除等到两个连续 ≥24h 零 hit 观测窗口满足后开始（**最早 2026-09-07 03:30 后**，见 §5 时间线修正）；任务已于 2026-09-04 由 owner 提权重新注册（09-04 03:30 未触发的处置）；daily 任务 argparse 缺陷已修复（revenue 3552795）。
- **执行状态**：待观测窗口满足（最早 ~09-07 03:30 后 close_gate_allowed=True）。观测语义已清除（wiki 25a8eea，hits=0 实证）；随后按批 1→2→3 执行（每批独立 commit + 三仓 CI 全绿 + legacy-gate 复扫清零）。
