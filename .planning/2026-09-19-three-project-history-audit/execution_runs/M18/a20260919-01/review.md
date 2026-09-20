# M18 · implementer review record — advertising（曝光填充与CPM）

Card M18（`execution_v2/card_M18.md`），Parent I-10，model_id `advertising`，
attempt `execution_runs/M18/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`decision.md`、
`handoff.json` 一致。

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts and issue its own verdict.

## 1. 做了什么（可复核的清单）

| 步骤 | 结果 | 证据 |
|---|---|---|
| A 绑定 | 生产两文件只读复制进本 attempt，副本与生产 hash 相等 | `binding.json`、`evidence/M18/source_manifest.json` |
| 冻结 | `oracle.md`（手算）→ `oracle.json`（独立 stdlib 脚本）→ 首次产品 stdout，mtime 顺序成立 | `source_manifest.json` → `mtime_ordering` |
| B 正例 | 实测 `[8100.0]` vs 手算 `[8100]`，abs_diff 0.0，容差 8.1e-06 | `evidence/M18/stdout.txt` |
| B 保真 | 扁平 `list`、长度 1 = `len(years)` = `len(expected)`、普通有限 `float` | `run_result.json` → `fidelity` |
| B 连续性 | 实测 `[8100.0, 13500.0]` vs 期望 `[8100, 13500]` | `run_result.json` |
| B 默认值 | 实测 `[8000.0]` vs 期望 `[8000]`（**不参与判定**） | `run_result.json` |
| C 负例 | 11/11 以 `ModelRegistryError` 拒绝 | `evidence/M18/negative_results.json` |
| 千次换算保真 | `OBS-THOUSAND-ONCE`：曝光翻倍 → 实测 `16100.0` = 手算期望，`matches_expected=true` | `run_result.json` → `observations` |
| 保真重生成 | `input/oracle/cases.json` 重生成后 sha256 **逐字节相同** | `evidence/M18/oracle_regen_proof.json` |
| 变异证明 | 副本篡改 → rc 3 / 3 / 2 / 1；未篡改 → rc 0；冻结件 hash 未变 | `evidence/M18/mutation_selfcheck.json` |
| 边界探针 | `fill_rate=[1.0]` → 实测 `10100.0`，端点含入 | `evidence/M18/extra_probes.json` |
| D/E/F | **未做**（D 需专业决策；E 属 I-10-A；F 需 I-12 冻结设计） | `decision.md`、`handoff.json` |

## 2. oracle 的独立性（本卡要害）

- 期望值来自 `scripts/oracle_M18.py`（stdlib only），`evidence/M18/oracle_selfcheck.json` 记录
  `product_import_present = false`。
- runner 只调用一个产品函数，期望只从 `evidence/M18/oracle.json` 读。
- 负例全部在内存中由新的 deepcopy 构造，不经 JSON 解析器；`PASS_rejected` 要求
  `isinstance(exc, ModelRegistryError)`，导入/文件错误记为 FAIL。
- 卡片引用的行号（入口 308、注册 238）在隔离副本上逐行复核：
  `entry_point_anchor_ok=true`、`registration_anchor_ok=true`。
- **`OBS-THOUSAND-ONCE` 是本卡最重要的独立性证据**：卡片 L42 的"千次换算只做一次"原本只是文字，
  本 attempt 在运行前把它的数值后果（曝光翻倍 ⇒ 恰好多一个 8000 块 ⇒ 16100；若再除一次 1000 则为
  16.1）写进 oracle 脚本的 `observation_expected`，运行后实测 16100.0。这不是"跑过了"，
  而是"可区分的预测被证实"。

## 3. 结果明细（含实际异常消息）

- registry formula：`revenue = eligible_impressions / 1000 * fill_rate * revenue_per_thousand_impressions + other_revenue`
- required `['eligible_impressions', 'fill_rate', 'revenue_per_thousand_impressions']`；optional `['other_revenue']`；declared defaults `{}`
- effective bounds：`eligible_impressions [0.0, inf]`、`fill_rate [0.0, 1.0]`、
  `revenue_per_thousand_impressions [0.0, inf]`、`other_revenue ['-inf','inf']`（signed driver）
- 11 个负例消息：
  - `NEG-CARD`：driver advertising.fill_rate must be between 0.0 and 1.0: FY2027
  - `N01a`：advertising.eligible_impressions.FY2027 must be numeric
  - `N01b/c/d`：advertising.eligible_impressions.FY2027 must be finite
  - `N02`：driver advertising.eligible_impressions must contain one value per forecast year
  - `N03`：missing drivers for advertising: eligible_impressions
  - `N04`：unsupported drivers for advertising: unknown_driver
  - `N05a/b`：advertising.years must contain fiscal years
  - `CONT-BREAK`：advertising.years must be consecutive and increasing
- 退出码：`B-product-run` 原始 rc = **0**（= 期望 0）；runner 回读校验
  `printed_matches_evidence_file: True`。

## 4. 观察项与探针（均**不**参与退出码）

- `OBS-BASE-IGNORED`：`base_revenue=999` → `[8100.0]`（`_rowwise` 丢弃 `base_revenue`）。
- `OBS-DEFAULT-EQUIV`：显式 `other_revenue=[0]` 与省缺相同（`[8000.0]`）。
- `OBS-THOUSAND-ONCE`：`[16100.0]`，与冻结的数值期望一致。
- `PROBE-FILL-EXACT-1`：`fill_rate=[1.0]` → `[10100.0]`（ratio 域含上端点）。

## 5. 请 reviewer 优先攻击的点

1. **"已填充曝光不再乘填充率"不可运行时拒绝。** 计算器只拿到一个数字数组，无法判断
   `eligible_impressions` 是填充前机会还是已填充曝光。若输入口径错，公式照样给出"漂亮"的数。
   请确认 `disclosure_adaptation = unmapped` 的结论没有被公式通过稀释。
2. **`fill_rate=1.0` 被接受**（实测 10100.0）。这在 `[0,1]` 域内是正确行为，但业务上
   "填充率 100%" 是否需要复核属专业裁定（`DEC-M18-3`）。
3. **`other_revenue` 允许负数**（signed driver，`model_registry.py:265-269`）。请判定是否需要非负约束。
4. **静默 0**：`other_revenue` 没有显式 default，被 `spec.defaults.get(driver, 0.0)` 静默补 0
   （注册表级 31 个可选 driver 同现象，见 `registry_enumeration.json`；`OQ-02`）。
5. **连续性用例的性质**：本模型逐年独立，`CONT-BREAK` 只是财年不连续拒绝，不能当作存量桥证据。
6. **流程透明性**：本 attempt 只跑过一次流水线（14 个单元全绿）；`oracle.md` 自写定后未改，
   `oracle.json` 可逐字节重生成。与 M17 不同，本卡没有出现"重跑"。
7. **隔离绑定来源**：I-00-B 绑定的是隔离方案而非物化 checkout，本 attempt 自行物化只读快照
   （hash 与生产相等），需 owner 裁定（`OQ-01`）。
8. **pytest 未安装**：`A0b` 离线探测 rc = 1（无本地 wheel、网络禁用）；本卡无命令需要 pytest。

## 6. 本卡**不**主张什么

- 不主张模型准确，也不主张一家公司的映射可外推（`accuracy = unproven`）。
- 不主张 `disclosure_adaptation`（D 未作，属专业决策）。
- 不重写公式（本卡零产品改动）。

## 7. 建议 reviewer 动作

1. 在 scratch 重跑 `scripts/oracle_M18.py --card M18 --out-root <scratch>`，逐字节比对冻结的三个文件。
2. 重跑 `scripts/run_card.py`（argv 见 `commands.json` 的 `B-product-run`），比对 `run_result.json`。
3. 确认隔离副本 hash 仍等于生产。
4. 复算一个本卡未使用的 oracle：建议 `eligible_impressions=[2500000]`、`fill_rate=[0.4]`、
   `revenue_per_thousand_impressions=[7]`、`other_revenue=[0]`，手算 2500×0.4×7 = 7000，先冻结再运行。
5. 裁定 `evidence/M18/oq_rulings.json` 的 OQ-01…OQ-05。

---

退出码自检（本卡自带）：见 `evidence/M18/mutation_selfcheck.json`。

| case | 篡改（仅作用于 `recovery/selfcheck/` 的副本） | 实测 rc | 期望 rc | 证明 |
|---|---|---|---|---|
| A | `oracle.json` 正例期望每个值 +1 | **3** | 3 | 篡改的期望无法躲在 rc=0 后面 |
| B | `cases.json` 的 N04 驱动名换成已注册的 `other_revenue` | **3** | 3 | 未被拒绝的负例会被判为负 |
| C | 正例 `expected_float`/`tolerances` 各多一项 | **2** | 2 | 保真不符 → 拒绝给判定 |
| D | scratch 副本删除 `cases.json` | **1** | 1 | harness 失败与判定失败可区分 |
| F | `cases.json` 中 N02 的 `expected` 改成 `ValueError`（该例仍抛 `ModelRegistryError`） | **3** | 3 | 声明期望被**按精确类型名**强制：`ModelRegistryError` 是 `ValueError` 子类，若用 isinstance 就会漏过（`declared_expectation_mismatch=1`） |
| E | 未篡改副本 | **0** | 0 | 绿可恢复 |

冻结件在 A–F 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

---

## revision r2 — response to the independent review

Independent review of r1: **accepted_scoped（仅 formula 资格）**，附 2 项 P2、4 项 P3、1 项仅针对 M17
的追加动作。本节**只追加**（自检表新增 F 行）；冻结期望、容差、负例清单、拒绝条件一律未改；
产品仓零改动；**本卡的 `oracle.md` 未追加任何节**（复核确认其 §1 有效域行正确）。

- **P2-1 已修**：`scripts/run_card.py` 现在按**异常精确类型名**比较 `cases.json` 的逐例 `expected`
  （**不用 isinstance**），新增 `negative_counts.declared_expectation_mismatch`，
  `negative_results.json` 的 `frozen_expectation` 改为从冻结 `cases.json` 导出；
  rc=3 口径同步改为"未被**按声明期望**拒绝"；runner sha256 `9ea69c72…` → **`5307d2cc…`**。
  新变异臂 **F** 实测 rc=3 且 `declared_expectation_mismatch=1`；本卡真实运行
  `declared_expectation_mismatch=0`、11/11 `PASS_rejected`、`verdict=pass`、rc=0。
- **P2-2 已按卡参数化**：本卡 **1 趟测量执行**（14 单元）+ **6 趟收尾执行**，
  与复核人的文件系统法证一致（run 目录创建≈写入，毫秒级，无第二世代指纹）。
  C2 单元是**随模板交付的既有单元**（byte-identical 来自 M17 attempt），不是首趟之后新增。
  两种口径（"声明的执行次数"与"可观测的重写世代数"）都写在 `process_history.json` 里。
  本 r2 节所在的收尾趟之后，B/C2/E/G 因 P2-1 修复各**重新执行一次**，同样记入该文件。
- **P3-1 已补**：`oq_rulings.json` 的 `rulings` 现含 `OQ-05`（`requires_ruling_from: independent
  reviewer`，`pointer: process_history.json`），`decision.md §3` 与 §7.5 的引用成立。
- **P3-2 不适用本卡**（容差探针属 M20）；**P3-3 已补**：新增 `process_history.json`（单元
  P-write-process-history）与 `handoff.json.process_history_pointer`；**P3-4 随 P3-1 消解**。
- **批次级两项**已在 `execution_runs/M17-M20/a20260919-01/`（`rc_namespace.json` + `batch_handoff.md`）
  落地：按卡命名 rc 语义并**禁止未标注命名空间的跨卡 rc 聚合**；明示 `unmapped` = **零产出**。
- **本次仍未验证 / 原样承接**：M17 首趟与 `probe_extra.py` 常量历史、`oracle.md` 跨趟未改写、
  M05–M08 与其它并发 session、`PLAN\reviews` 全树、真实披露对应关系、`_SIGNED_DRIVERS` 其余名字的
  业务正当性、`oracle_M18.py` 的逐行审阅、`iso\venv` 全树比对——均**未**由本批证实。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`（= **零产出**，不是部分完成）；
`accuracy = unproven`（完全未做评估）。实现者**未**自签 accepted。

### 记录收尾单元（不产生任何产品行为）

`H-write-handoff`（生成 `handoff.json`）与 `Z-close-attempt`（写 `commands.json` 与
`after/final_deliverable_hashes.json`）在测量流水线之后**单独**由 `scripts/run_closing.py` 执行，
各有独立 command-run-id 记录：`evidence/M18/runs/H-write-handoff/`、`evidence/M18/runs/Z-close-attempt/`。
`commands.json` 由 Z 自己写，所以 Z 自己的 rc.json 是在它返回**之后**才刷新的：`commands.json` 中
Z 的 `raw_rc`（当前为 0）来自**同 argv 的上一次执行**，该口径写在该单元的 `raw_rc_note` 里；
**最近一次执行**的 raw rc 始终在 `evidence/M18/runs/Z-close-attempt/rc.json`（自述其
stdout/stderr 的 sha256）与 `pipeline_run.json`。第 5 节第 6 条所说"只跑过一次流水线"指的是
**测量流水线**（A0…G，14 个单元）；收尾单元是随后的独立记录步骤，不碰产品、不碰冻结证据。
`after/final_deliverable_hashes.json` 按构造排除它自己与 `runs/Z-close-attempt/**`
（原因见该文件的 `excluded_from_the_table`）。

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`；`accuracy = unproven`。
