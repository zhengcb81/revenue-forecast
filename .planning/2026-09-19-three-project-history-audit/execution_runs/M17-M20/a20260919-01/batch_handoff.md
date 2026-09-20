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

---

## 8. r2 复核结论（独立 reviewer，原文转录）

四卡 r2 判定：**changes_required**，范围**严格限定**于 r2 交付物中的审计元数据，
**不涉及公式**。公式证据经 r2 复核未变且成立（12 个冻结文件 hash 与 r1 逐一相同；rc=0、11/11、
declared_expectation_mismatch=0；runner 5307d2cc… 经注入证明按精确类型名比较声明）。
完成 P2-A（两张 hash 清单表重生成并让"drift=0"成为被测量的输出）、
P2-B（rc_namespace.json 修为合法 JSON + 自检）、P2-C（修正 pack_card.py:160 与
append_oracle_addendum.py:155 后重生成两个 M17 追加记录；oracle.md 保持 c9971428… 不变）
以及 §3 的 P3-1…P3-6 后，四卡 formula 可签 `accepted_scoped`（仅 formula），**无需重跑任何产品测量**。
本表第 1 节的 rc 命名空间规则**有效且必须继续遵守**；但请注意：rc_namespace.json 当前无法被
JSON 解析器读取（P2-B），在修好之前请只使用本文件第 1 节的人读表格。
本表第 3 节把 after/final_deliverable_hashes.json 描述为"全部产物 hash"——该表当前有 24–25 条
与磁盘不符（P2-A），修好前不得据此宣称"产物复算 0 drift"。
未授予：disclosure_adaptation = unmapped（零产出）；accuracy = unproven。


### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。第 8 节的 rc 命名空间规则继续
有效；`rc_namespace.json` 已修为**合法 JSON**（由 `scripts/batch_tools.py write-rc-namespace` 生成，
并对批次目录 + 四卡 attempt 的全部 `.json` 做解析回读自检，实测失败数见
`batch_json_validation.json`）。`after/final_deliverable_hashes.json` 与
`evidence/<CARD>/evidence_hashes.json` 现均带 `drift_count`/`verified_utc`，并由收尾后的
`V-verify-hash-tables` 单元再测一次；修好之前的"产物复算 0 drift"主张**已撤回**（见各卡 review.md 的
r2 处置节）。

另：第 6 节末行"收尾序列共执行 6 趟"是**当时**的数字；r2 定点再复核之后又执行了第 7 趟
（单元 `R2b,R2c,G,P,T,H,Z,V`），`process_history.json.declared_execution_history.closing_passes`
已含第 7 趟，并对 03:17:53 那一代写入登记了 `additional_unnamed_generations = 1` 的 honest_gap。

---

## 9. 实现者附注之二：冻结基线的源码漂移（**不是**本批写入，需 owner 处置）

本节由 M17-M20 attempt 的实现 session 追加（append-only）。它**不是** reviewer 的原文，也不构成任何
acceptance。

**事实**：生产仓库 `C:\Users\郑曾波\Projects\revenue-forecast\scripts\model_registry.py` 在
**2026-09-20 04:35:32（本地时间）** 被改写为

```
sha256 1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86   (19703 bytes)
```

而本批绑定的锚点是 `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`。
`scripts/model_extensions.py` 仍等于锚点 `9939480b…`。

**不是本批所为的证据**：①四卡 attempt 的 `before/state.json` 与 `after/state.json` 中
`watched_hashes["scripts/model_registry.py"]` **都**等于锚点；②四卡的
`iso/checkout_scripts/model_registry.py` 仍是逐字节等于锚点的只读副本，而本批**全部**产品测量都跑在
这份副本上；③本批的写入范围限于自己的 attempt 目录（见各卡 `binding.json` 的 allowlist 与
`changes.diff`）。

**后果与边界**：
1. 本批四卡的全部测量证据对**锚点版本**成立（隔离副本 hash 可核）；本批**不主张**对
   `1f2639e1…` 成立。
2. 按 `START_HERE.md` 的源码漂移分支，任何**新的**卡运行必须重新绑定新 hash，并重核 oracle、负例与
   `registry_enumeration.json`（枚举结果可能因这次产品改动而变化）。
3. 下游卡（I-10-A / I-11 / I-12 及各消费 M17-M20 的卡）接手前应确认自己引用的是哪个修订。
4. 各卡 `evidence/<CARD>/integrity.json` 中"生产 hash 等于锚点"是 **pack 时刻**的事实陈述，现已过期；
   该文件**未被改写**（不改历史记录），其时间范围由该文件的 `packed_utc` 与本节共同界定。
5. 本批**无法确定**这次生产改动由谁、依据哪张卡执行（本 session 未参与，也不做推测性归因）。

### 9.1 追加更正（同一日的复查，append-only）

上一段的漂移是**暂时性**的：本 session 在 **2026-09-20 04:40:53（本地）** 复查时，
`scripts/model_registry.py` 已回到锚点

```
sha256 9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f   (26446 bytes, mtime 2026-09-20 04:40:53)
```

**观察记录（两个状态都留档，不删改上文）**：

| 观察时刻（本地） | sha256 | 字节数 |
|---|---|---|
| 本批 before/after 捕获（卡运行期间） | `9ec65295…`（锚点） | 26446 |
| 2026-09-20 04:35:32 | `1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86` | 19703 |
| 2026-09-20 04:40:53 | `9ec65295…`（锚点，等于本批绑定值） | 26446 |

**结论**：本批绑定的**锚点**在最终验证时刻重新成立，因此 §9 第 1 条的"证据对锚点版本成立"
不留悬置；但生产仓的 `model_registry.py` 在这段时间内**被改写过至少两次**（写、回退），
说明该文件**正在被别的 session 改动**。这不是本批写入（证据见 §9），但它是**批次级风险**：

- 任何**新的**运行仍必须按 `START_HERE.md` 重新绑定 hash 并重核 oracle/负例/枚举；
- 引用"M17-M20 的测量"时，必须同时写明被测副本的 hash（本批 = 上面那一行的锚点值）；
- 本批的 hash 清单表（`after/final_deliverable_hashes.json`、`evidence/<CARD>/evidence_hashes.json`）
  只覆盖**本 attempt 目录内**的文件，**不**覆盖生产仓；生产仓的状态由本节与各卡
  `before/`+`after/state.json` 记录。

### 9.2 机制更正与新纪律（编排层已查明；append-only 追加）

本节**追加**并更正 §9/§9.1 的"触发者本 session 无法确定"表述；上文一字未改。

**机制（已确认）**：仓库自带的 pre-commit/pre-push 门在每次提交时 ①把未暂存改动导出为补丁
（`…\.cache\pre-commit\patch<epoch>-<pid>`）；②执行 `git checkout -- .` 清空未暂存改动；③hook 跑完后
**回放**该补丁。**2026-09-20 04:35:31（本地）** 那一次第 ② 步因 3 个被并发占用的 scratch 文件
`unable to unlink … Invalid argument` **返回 255**，hook 抛错退出 ⇒ 第 ③ 步从未执行 ⇒ **生产工作树被重置到
HEAD**。这同时解释了：`scripts/model_registry.py` 由锚点 `9ec65295…`/26446 B 变为 HEAD 版
`1f2639e1…`/19703 B；`revenue_core.py` / `contracts/constants.py` / `revenue_report.py` /
`tests/test_backtest.py` / `SKILL.md` / `CHANGELOG.md` / `assurance/runs/*` / `e2e/expected/*` /
`references/backtesting.md` 同时"变干净"；以及**本 attempt 树内**出现的"我未触发的改写与截断"
（stash/checkout 会重写被并发写入的文件，表现为 size 变小/截断）——03:17:53 那一代与 04:35:32 属同一机制的
更早/后续实例。
**措辞限定**：机制已确认；**具体某个实例的执行者与受影响文件清单未逐条取证**。

**时点限定（重要）**：在该窗口内，任何 `production_hashes_unchanged=false` 或 hash 不一致读数都是**正确告警**，
不是校验器错误；必须带时点记录并上报，**不得压制**。

**恢复后的锚点（编排层复算，逐文件一致）**：

```
scripts/model_registry.py    9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f   26446 B
scripts/model_extensions.py  9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911
revenue_core.py 1821fd2a…   contracts/constants.py 278e3e02…   revenue_report.py a85fb484…
tests/test_backtest.py d0972e23…   SKILL.md 45e4e343…（与 I-00-A 基线一致）   CHANGELOG.md bcba3dd5…
```

恢复方式：用该次补丁的 `--exclude=.planning/*` 子集 `git apply`（`--check`/`--apply` 均 exit 0）。
并发诱因同源：`.planning` 下 3 个 attempt scratch 仓库内嵌 `.git`（使父仓库 `fatal: bad object HEAD`），
已在 `execution_runs/.gitignore` 兜底（**未删除任何文件**）。完整记录：
`execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`。

**新纪律（已写入各卡 `handoff.json.discipline`、`process_history.json` 的
`additional_unnamed_generations.mechanism_confirmed_appended`、`integrity.json` 的
`anchored_hash_claim_is_time_scoped`，并在此登记）**：凡验收依据含"生产文件 hash"的卡，必须把它当作
**可被外部 git 操作改变的量**：

1. 每一条生产 hash 主张都是**时点限定**的，必须带观察时间；
2. 发现不一致时**先记录漂移与时点并上报编排层**（本批正是如此）；
3. **永不靠改期望/冻结件/拒绝条件去适配漂移**——漂移意味着**新运行必须重新绑定**，不意味着 oracle 该动；
4. 引用本批结论时必须同时写明**被测副本**的 hash（本批 = `9ec65295…` 的隔离副本）。

**同批自查中发现并已修的一处相关缺陷**：`integrity.json` 的 `anchored_hashes_match` 原为**硬编码 True**，
而 03:40Z 那几次 pack 记录的观察值恰是 HEAD 版 `1f2639e1…`（即字段会与自身内容矛盾）。现已改为
**由观察值与任务锚点比较得出**，并新增 `observed_matches_task_anchor_by_file`、
`anchored_hashes_match_rule`、`anchored_hash_claim_is_time_scoped`；重跑后四卡该字段为 True 且观察值 = 锚点。
