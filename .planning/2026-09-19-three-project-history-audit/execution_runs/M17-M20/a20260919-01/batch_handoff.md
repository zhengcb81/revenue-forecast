# M17–M20 批次级交接件（attempt a20260919-01）

本目录**只放批次级文档**（`batch_handoff.md`、`rc_namespace.json`），不含任何卡产物、不含 `binding.json`、
不是任何卡的 cwd。四张卡各自的 attempt 完全独立：`execution_runs/M17|M18|M19|M20/a20260919-01/`。
（同类先例：`execution_runs/M05-M08/a20260919-01/` 是那一批的批次目录。）

卡片状态：M17 / M18 / M19 / M20 —— 独立复核结论 **accepted_scoped（仅 formula 资格）**；
经 r2 处置后 **formula 仍为 `review_pending`**（实现者**不自签**，待 reviewer 点审 r2）；
`disclosure_adaptation = unmapped`；`accuracy = unproven`。

---

## 1. 硬要求一：rc 命名空间表（**禁止未标注命名空间的跨卡 rc 聚合**）

同一个整数在不同 runner 世代里含义不同。**严禁**在不注明 runner sha256 的情况下对 rc 求平均、
计数、比较或跨卡聚合。机器可读副本：`rc_namespace.json`。

| 卡 | runner | runner sha256 | rc=0 | rc=1 | rc=2 | rc=3 |
|---|---|---|---|---|---|---|
| M17–M20（本批，r2 修复后） | `scripts/run_card.py` | `5307d2cc31bad5731585d2f503341fe2b3d61425f369289eed261568883cbf05` | pass | **harness error** | **无判定**（期望缺失/保真不符） | 负判定（含"未被**按声明期望**拒绝"） |
| M17–M20（r1 修复前） | `scripts/run_card.py` | `9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd` | pass | 未定义 | harness 失败 | 负判定（**不**校验 `cases.json` 的逐例 `expected`） |
| M05–M08 | `scripts/run_card.py` | `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a` | pass | **未定义**（裸 1 不是 harness 信号） | **harness/记账失败** | 负判定（**不**校验逐例 `expected`） |
| M21–M31 | `scripts/run_card.py` | 本批未核对 | — | — | — | — |

- 优先级（本批）：`1 > 2 > 3 > 0`。
- M21–M31 的 rc 语义**未由本批核验**，不得从上面任何一行推断。
- 同批复核已独立发现"逐例 `expected` 未被强制"是**跨批共享 harness 缺口**；本批**只**修了
  M17–M20 四份副本（四份字节相同），**未**改动其它卡的冻结 runner。

## 2. 硬要求二：`unmapped` 的含义是**零产出**，不是部分完成

四卡的 `disclosure_adaptation = unmapped` 精确含义是：**一个披露类产物都没有**——
没有 `disclosure_mapping.json`、没有 `accounting_decision.md`、没有 `historical_reconciliation.json`、
没有 `forecast_integration.json`。这不是"做了 60%"，也不是"等补充"。

同理 `accuracy = unproven` 精确含义是：**一次评估都没做**（I-12 冻结设计不存在），
公式通过**不得**被读成准确性证据。

## 3. 每卡交付与入口

| 卡 | model_id | attempt 根 | 冻结 oracle（运行前） | 正例手算 → 实测 | 负例 |
|---|---|---|---|---|---|
| M17 | `licensing_commercial` | `execution_runs/M17/a20260919-01` | `oracle.md`（+ r2 §13 追加节） | 40×2+15+5+10=110 → `[110.0]` | 11/11 |
| M18 | `advertising` | `execution_runs/M18/a20260919-01` | `oracle.md`（未追加） | 1000000/1000×0.8×10+100=8100 → `[8100.0]` | 11/11 |
| M19 | `gaming` | `execution_runs/M19/a20260919-01` | `oracle.md`（未追加） | 1000×0.05×20+10=1010 → `[1010.0]` | 11/11 |
| M20 | `cohort_subscription` | `execution_runs/M20/a20260919-01` | `oracle.md`（未追加） | 桥120/暴露95→95×2+5=195 → `[195.0]` | 11/11 |

每卡读取顺序：`review.md`（含 r2 处置与攻击点）→ `handoff.json`（含 `next_step_number=4`、
`process_history_pointer`、`batch_handoff_pointer`）→ `decision.md` → `oracle.md` →
`evidence/<CARD>/`（`run_result.json`、`negative_results.json`、`mutation_selfcheck.json`、
`oracle_regen_proof.json`、`oq_rulings.json`、`revision_r2.json`、`extra_probes.json`）→
`commands.json`（每单元真实 argv + raw rc）→ `after/final_deliverable_hashes.json`（全部产物 hash）。

## 4. r2 处置清单（对象：独立复核的 P2-1/P2-2/P3-1…P3-4 + M17 §13 追加）

| 项 | 处置 | 证据 |
|---|---|---|
| P2-1 runner 不比较逐例 `expected` | 已按复核倾向 (b) 修：按**精确类型名**比较（非 isinstance），新增 `declared_expectation_mismatch` 计数；新增第 6 个变异臂 F | `scripts/run_card.py`、`evidence/*/mutation_selfcheck.json`、`negative_results.json` |
| P2-2 OQ-05 跨卡常量与 review.md 矛盾 | 已按卡参数化；两种口径（声明的执行次数 / 可观测的重写世代数）都写进 `process_history.json` | `process_history.json`、`handoff.json.open_questions` |
| P3-1 `oq_rulings.json` 缺 OQ-05 | 已补（含 `requires_ruling_from: independent reviewer`） | `evidence/*/oq_rulings.json` |
| P3-2 M20 容差探针低估 5 个数量级 | 已改为公式化 + 实测带内/带外两个探针 | `evidence/M20/extra_probes.json` |
| P3-3 无 passes/run_history | 已补 `process_history.json`（新增单元 P-write-process-history） | 同上 |
| P3-4 review.md 引用不存在的 OQ-05 | 随 P3-1 消解 | 同上 |
| M17 `oracle.md` §1 描述行错误 | **append-only** 追加 `## 13. 修订 r2`，§1 一字未改；追加前 hash 可在真实行边界截断复现；第一次执行失败与 `--repair-restore` 还原全过程留档 | `evidence/M17/oracle_addendum_record.json`、`revision_r2.json`、`runs/R2-append-oracle-addendum/` |

## 5. 需 owner / 专业角色拍板的 6 点（**复核意见原样转述，未自行采纳为决定**）

1. **I-00-B 绑定范围偏差属实**：复核直读 I-00-B 的 `binding.json`，其中只有 `isolated_binding_plan`
   与 `command_binding_rule`，**无任何 checkout 路径或物化副本 hash**，而卡片 L49 写"从 I-00-B 读取
   isolated checkout"。复核建议：owner 书面追认"物化由各 attempt 完成并记录来源 hash"，
   或以 I-00-B checkout 重跑 B/C/E（成本极低）。→ 本批未自行选择。
2. **静默补 0（`model_registry.py:335`，31 个槽位）**：复核认为是六点中最重的，
   主张**在进入 D 之前单独立卡**修掉（倾向"省缺且无显式 default 的 optional driver ⇒ 抛
   `ModelRegistryError`"，因为把隐式 0 变显式 0 仍无法区分"没找到"），并要求 D 卡前置硬规则
   "区分 `missing` 与 `0`，`missing` 不得进计算"。→ 本批只登记，未改产品。
3. **M17 §1 描述行**：已按复核明确要求追加 §13 更正（见上）。范围仅 M17。
4. **业务负例不可运行时拒绝**：复核完全同意本批处置，并特别肯定 M18 把卡片 L42 拆成
   "千次换算只做一次"（可测，`OBS-THOUSAND-ONCE`=16100）与"已填充曝光不再乘填充率"（不可测）两半。
5. **数值域边界接受行为正确**，业务可接受性归 D（M18 `fill_rate=1.0`→10100、M19
   `payer_conversion=1.0`→20010、M20 `timing_factor=0`→5、M20 桥带内/带外实测）。
6. **`_SIGNED_DRIVERS` 按"名字"而非"语义角色"决定符号**：复核判为真实产品级设计缺陷、与第 2 点同源，
   应立卡（建议 `dimension=="revenue"` 且作加项即 signed；`usage_revenue` / `franchise_system_sales` /
   `supply_revenue` / `recognized_performance_fees` 应转 signed）。本批"登记不改"正确，
   但复核建议在**共享位置**登记"9 个名字是跨模型不一致的根源"（现只在 M17 的 OQ-04 里）。

## 6. 复核已声明"未能验证"、本批**原样承接**（不得当已证）

① M17 第 1 趟（13 单元）的原始结果（`rc.json` 已被后续执行覆盖）；② `probe_extra.py` 常量确曾为
105.0（无版本历史）；③ `oracle.md` 在 r1 各趟之间未被改写（已可复核但不能排除"同字节改写+伪造
mtime"；r2 追加节另提供截断复现证据）；④ M05–M08 结论未评估；⑤ 其它并发 session 未评估
（porcelain 行数与各卡记录不同，未归因）；⑥ `PLAN\reviews` 全树扫描受权限限制；⑦ 四卡披露采集项
与真实公司披露的对应关系未评估；⑧ `_SIGNED_DRIVERS` 其余 5 个名字的业务正当性未评估；
⑨ `oracle_MXX.py` 未逐行审阅（独立性证据是行为层）；⑩ `iso\venv` 未与模板做全树 hash 比对。

**补充（本批自己声明的两个口径差异，供 reviewer 复核时不误读）**：

- 复核的法证口径"M17 = 2 趟测量"指的是**可观测的重写世代数**；实施 session 的记录是
  **3 趟测量执行**（13 单元 → 14 单元[探针常量 105.0] → 14 单元[常量更正为 90.0]）。
  本批**没有**把 3 改写成 2（那会与本 session 的命令记录不符），两个数字与各自口径都写在
  `process_history.json` 与各卡 `review.md` 的 r2 节。
- 收尾序列（P/H/Z）共执行 **6 趟**（每趟由一次记账性改动触发，argv 相同），
  被覆盖的更早执行只有目录时间戳可辨——这一 `honest_gap` 同样写在 `process_history.json`。

## 7. 未做项（不虚填）

- D（`[professional_decision_required]`）：未产出任何披露映射产物；E（I-10-A 先行）：未做；
  F（需 I-12 冻结设计）：未做。
- pytest 未安装：单元 `A0b-pytest-offline-availability` 实测 rc=1（`--no-index --no-cache-dir`，
  本地无 wheel、网络禁用）；本批无任何命令需要 pytest。
- 生产三仓零写入；未 `git add/commit/restore/stash`；`PLAN\reviews` 未被本批写入。

---

本文件由 M17–M20 attempt 的实施 session 编写；**不构成任何 acceptance**，也未替 owner 作任何决定。
