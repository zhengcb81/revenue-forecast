# M19 · implementer review record — gaming（活跃用户付费变现）

Card M19（`execution_v2/card_M19.md`），Parent I-10，model_id `gaming`，
attempt `execution_runs/M19/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`decision.md`、
`handoff.json` 一致。

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts and issue its own verdict.

## 1. 做了什么（可复核的清单）

| 步骤 | 结果 | 证据 |
|---|---|---|
| A 绑定 | 只读复制进本 attempt，副本与生产 hash 相等 | `binding.json`、`evidence/M19/source_manifest.json` |
| 冻结 | `oracle.md`（手算）→ `oracle.json`（独立 stdlib 脚本）→ 首次产品 stdout，mtime 顺序成立 | `source_manifest.json` → `mtime_ordering` |
| B 正例 | 实测 `[1010.0]` vs 手算 `[1010]`，abs_diff 0.0，容差 1.01e-06 | `evidence/M19/stdout.txt` |
| B 保真 | 扁平 `list`、长度 1 = `len(years)` = `len(expected)`、普通有限 `float` | `run_result.json` → `fidelity` |
| B 连续性 | 实测 `[1010.0, 1584.0]` vs 期望 `[1010, 1584]` | `run_result.json` |
| B 默认值 | 实测 `[1000.0]` vs 期望 `[1000]`（**不参与判定**） | `run_result.json` |
| C 负例 | 11/11 以 `ModelRegistryError` 拒绝 | `evidence/M19/negative_results.json` |
| 端点保真 | `OBS-PAYER-BOUNDARY`：`payer_conversion=[1.0]` → 实测 `20010.0` = 手算期望 | `run_result.json` → `observations` |
| 保真重生成 | `input/oracle/cases.json` 重生成后 sha256 **逐字节相同** | `evidence/M19/oracle_regen_proof.json` |
| 变异证明 | 副本篡改 → rc 3 / 3 / 2 / 1；未篡改 → rc 0；冻结件 hash 未变 | `evidence/M19/mutation_selfcheck.json` |
| 边界探针 | `active_users=[0]` → 实测 `10.0`，数量域含下端点 | `evidence/M19/extra_probes.json` |
| D/E/F | **未做**（D 需专业决策；E 属 I-10-A；F 需 I-12 冻结设计） | `decision.md`、`handoff.json` |

## 2. oracle 的独立性（本卡要害）

- 期望值来自 `scripts/oracle_M19.py`（stdlib only），`evidence/M19/oracle_selfcheck.json` 记录
  `product_import_present = false`。
- runner 只调用一个产品函数，期望只从 `evidence/M19/oracle.json` 读。
- 负例全部由新的内存 deepcopy 构造，不经 JSON 解析器；`PASS_rejected` 要求
  `isinstance(exc, ModelRegistryError)`，导入/文件错误记 FAIL。
- 卡片引用的行号（入口 308、注册 239）在隔离副本上逐行复核（两个 anchor 均为 true）。
- `OBS-PAYER-BOUNDARY` 测的是**卡片自己写的域**（L8「付费率0–1」）在实现里是否含端点：
  运行前把手算后果 20010 写进 oracle 脚本，运行后实测一致，因此"0–1"这句话在本实现下是被验证的，
  而不是被引用的。

## 3. 结果明细（含实际异常消息）

- registry formula：`revenue = active_users * payer_conversion * revenue_per_payer + other_revenue`
- required `['active_users', 'payer_conversion', 'revenue_per_payer']`；optional `['other_revenue']`；declared defaults `{}`
- effective bounds：`active_users [0.0, inf]`、`payer_conversion [0.0, 1.0]`、
  `revenue_per_payer [0.0, inf]`、`other_revenue ['-inf','inf']`（signed driver）
- 11 个负例消息：
  - `NEG-CARD`：driver gaming.payer_conversion must be between 0.0 and 1.0: FY2027
  - `N01a`：gaming.active_users.FY2027 must be numeric
  - `N01b/c/d`：gaming.active_users.FY2027 must be finite
  - `N02`：driver gaming.active_users must contain one value per forecast year
  - `N03`：missing drivers for gaming: active_users
  - `N04`：unsupported drivers for gaming: unknown_driver
  - `N05a/b`：gaming.years must contain fiscal years
  - `CONT-BREAK`：gaming.years must be consecutive and increasing
- 负例计数：`rejected_with_ModelRegistryError=11`、`not_rejected=0`、`wrong_exception_type=0`、
  `import_or_file_error=0`。
- 退出码：`B-product-run` 原始 rc = **0**（= 期望 0）；runner 回读校验
  `printed_matches_evidence_file: True`。

## 4. 观察项与探针（均**不**参与退出码）

- `OBS-BASE-IGNORED`：`base_revenue=999` → `[1010.0]`（`_rowwise` 丢弃 `base_revenue`）。
- `OBS-DEFAULT-EQUIV`：显式 `other_revenue=[0]` 与省缺相同（`[1000.0]`）。
- `OBS-PAYER-BOUNDARY`：`[20010.0]`，与冻结的数值期望一致。
- `PROBE-ACTIVE-ZERO`：`[10.0]`（数量域含 0 端点）。

## 5. 请 reviewer 优先攻击的点

1. **期间口径完全不可运行时拒绝。** DAU × 年度 ARPPU 这类错配在数值上"看起来正常"。
   请确认 `disclosure_adaptation = unmapped` 没被公式通过稀释（`DEC-M19-1`）。
2. **流水 ≠ 收入同样不可拒绝**。渠道费/递延不在模型内（`DEC-M19-2`）。
3. **`payer_conversion=1.0` 被接受**（实测 20010.0）：`[0,1]` 域内正确，但"100% 付费率"业务上可疑，
   属专业裁定。
4. **`other_revenue` 允许负数**（signed driver）。
5. **静默 0**：`other_revenue` 无显式 default，被静默补 0（`OQ-02`；注册表级 31 个可选 driver 同现象）。
6. **连续性用例的性质**：逐年独立模型，`CONT-BREAK` 只是财年不连续拒绝，不是存量桥证据。
7. **隔离绑定来源**：I-00-B 未物化 checkout，本 attempt 自行物化只读快照（hash 与生产相等），
   需 owner 裁定（`OQ-01`）。
8. **pytest 未安装**：`A0b` 离线探测 rc = 1（无本地 wheel、网络禁用）；本卡无命令需要 pytest。

## 6. 本卡**不**主张什么

- 不主张模型准确，也不主张一家公司的映射可外推（`accuracy = unproven`）。
- 不主张 `disclosure_adaptation`（D 未作，属专业决策）。
- 不重写公式（本卡零产品改动）。

## 7. 建议 reviewer 动作

1. 在 scratch 重跑 `scripts/oracle_M19.py --card M19 --out-root <scratch>`，逐字节比对冻结的三个文件。
2. 重跑 `scripts/run_card.py`（argv 见 `commands.json` 的 `B-product-run`），比对 `run_result.json`。
3. 确认隔离副本 hash 仍等于生产。
4. 复算一个本卡未使用的 oracle：建议 `active_users=[2500]`、`payer_conversion=[0.04]`、
   `revenue_per_payer=[12]`、`other_revenue=[0]`，手算 2500×0.04×12 = 1200，先冻结再运行。
5. 裁定 `evidence/M19/oq_rulings.json` 的 OQ-01…OQ-05。

---

退出码自检（本卡自带）：见 `evidence/M19/mutation_selfcheck.json`。

| case | 篡改（仅作用于 `recovery/selfcheck/` 的副本） | 实测 rc | 期望 rc | 证明 |
|---|---|---|---|---|
| A | `oracle.json` 正例期望每个值 +1 | **3** | 3 | 篡改的期望无法躲在 rc=0 后面 |
| B | `cases.json` 的 N04 驱动名换成已注册的 `other_revenue` | **3** | 3 | 未被拒绝的负例会被判为负 |
| C | 正例 `expected_float`/`tolerances` 各多一项 | **2** | 2 | 保真不符 → 拒绝给判定 |
| D | scratch 副本删除 `cases.json` | **1** | 1 | harness 失败与判定失败可区分 |
| F | `cases.json` 中 N02 的 `expected` 改成 `ValueError`（该例仍抛 `ModelRegistryError`） | **3** | 3 | 声明期望被**按精确类型名**强制：`ModelRegistryError` 是 `ValueError` 子类，若用 isinstance 就会漏过（`declared_expectation_mismatch=1`） |
| E | 未篡改副本 | **0** | 0 | 绿可恢复 |

冻结件在 A–F 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

### 记录收尾单元（不产生任何产品行为）

`H-write-handoff`（生成 `handoff.json`）与 `Z-close-attempt`（写 `commands.json` 与
`after/final_deliverable_hashes.json`）在测量流水线（A0…G，14 个单元）之后**单独**由
`scripts/run_closing.py` 执行，各有独立 command-run-id 记录：
`evidence/M19/runs/H-write-handoff/`、`evidence/M19/runs/Z-close-attempt/`。
`commands.json` 由 Z 自己写，所以 Z 自己的 rc.json 是在它返回**之后**才刷新的：`commands.json` 中
Z 的 `raw_rc`（当前为 0）来自**同 argv 的上一次执行**，该口径写在该单元的 `raw_rc_note` 里；
**最近一次执行**的 raw rc 始终在 `evidence/M19/runs/Z-close-attempt/rc.json`（自述其
stdout/stderr 的 sha256）与 `pipeline_run.json`。
`after/final_deliverable_hashes.json` 按构造排除它自己与 `runs/Z-close-attempt/**`
（原因见该文件的 `excluded_from_the_table`）。

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
- **P2-2 已按卡参数化**：本卡 **1 趟测量执行**（14 单元）+ **6 趟收尾执行**，与复核人的文件系统
  法证一致；C2 是**随模板交付的既有单元**（不是首趟之后新增）。两种口径都写在 `process_history.json`。
  本 r2 节所在的收尾趟之后，B/C2/E/G 因 P2-1 修复各**重新执行一次**。
- **P3-1 已补**（OQ-05 进入 `oq_rulings.json`，`requires_ruling_from: independent reviewer`）；
  **P3-2 不适用本卡**（属 M20）；**P3-3 已补**（`process_history.json` + handoff 指针）；
  **P3-4 随 P3-1 消解**。
- **批次级两项**已在 `execution_runs/M17-M20/a20260919-01/` 落地：rc 命名空间表 +
  **禁止未标注命名空间的跨卡 rc 聚合**；明示 `unmapped` = **零产出**。
- **本次仍未验证 / 原样承接**：M17 首趟与探针常量历史、`oracle.md` 跨趟未改写、M05–M08 与其它
  并发 session、`PLAN\reviews` 全树、真实披露对应关系、`_SIGNED_DRIVERS` 其余名字的业务正当性、
  `oracle_M19.py` 的逐行审阅、`iso\venv` 全树比对——均**未**由本批证实。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`（= **零产出**，不是部分完成）；
`accuracy = unproven`（完全未做评估）。实现者**未**自签 accepted。

---

## revision r2 review — 独立 reviewer 的 r2 判定（原文转录，不得改写）

判定：**changes_required**（四卡一致：M17 / M18 / M19 / M20）。
**范围严格限定**：本判定只针对 r2 交付物中的"审计元数据"，**不针对公式**。
公式资格的证据经 r2 复核**未发生变化、且仍然成立**：四卡 12 个冻结文件
（input.json / oracle.json / cases.json）的 sha256 与本 reviewer r1 记录逐一相同；
run_result.json 仍为 verdict=pass、rc=0、11/11 PASS_rejected、declared_expectation_mismatch=0；
runner 5307d2cc… 经注入测试证明按**精确类型名**比较声明期望（下详）。
因此：**完成下列 3 项 P2 与 2 项随附动作后，四卡 formula 可签 `accepted_scoped`（仅 formula）**，
且**不需要重跑任何产品测量**。
未授予：disclosure_adaptation 保持 `unmapped`（= 零产出，非部分完成）；accuracy 保持 `unproven`。
P1 = 0（无应拒被接受、无假绿、无公式反例）。

### 已闭合（r1 的 P2/P3）
- r1-P2-1 **闭合**：`run_card.py` 现按精确类型名比较 `cases.json` 的逐例 `expected`。
  本 reviewer 自建两组注入验证区分度：
  (a) 声明被篡改而实际类型正确（N02.expected:="ValueError"）→ rc=3、mismatch=1、FAIL_declared_expectation_mismatch（r1 时该注入为 rc=0）；
  (b) 声明正确而实际类型被替换为其**子类**（注入 `_ReviewerSubclassProbeError(ModelRegistryError)`，isinstance 仍为 True）→ rc=3、mismatch=1。
  第 (b) 组是决定性证据：若实现退回 isinstance 比较，该例会被误判为 PASS_rejected。第 6 变异臂 F 亦独立复现（rc=3）。四卡结果逐行相同。
- r1-P2-2 **闭合**：M18/19/20 的 OQ-05 现为按卡生成（"executed 1 time(s)"，C2 来源按卡区分），与 M18 review.md §5.6 一致，r1 的自相矛盾消除。
  M17 的"3 趟测量执行（声明）vs 2 个重写世代（法证可观测）"**并存处理诚实、可接受**：两个数各自标注口径、差异被显式解释（process_history.json 的 forensic_explanation 与 declared_vs_observed），且实现者明确拒绝把 3 改写成 2。本 reviewer 的 r1 法证只能给出"≥2 个写入世代"，与 3 相容但不能证实；不视为失真。
- r1-P3-1 **闭合**：四卡 oq_rulings.json 现含 OQ-01…OQ-05。
- r1-P3-2 **闭合**（M20）：改为公式化容差 + 带内/带外实测；其数值得本 reviewer 独立复现（1.2e-7 → [195.0, 240.00000024]；1.201e-7 → ModelRegistryError）。
- r1-P3-3 **闭合**：新增 P-write-process-history 单元与 process_history.json。
- r1-P3-4 **闭合**：随 P3-1 消解。
- **本 reviewer r1 明确要求的冻结件动作已正确完成**：M17 oracle.md 追加 `## 13. 修订 r2`，append-only。
  独立验证：截断到 11768 字节 → sha256 9c8021ee…（= 追加前 hash，逐位相同）；11768 前一个字节为 LF（真实行边界）；
  行 184/185 为空行、行 186 为 `## 13.` 标题；r2_sections_in_oracle_md=1（无重复追加）；
  失败首趟与成功趟的 post-append hash 均为 c9971428…（⇒ --repair-restore + 重新追加是无损往返，**无不可逆污染**）；
  M18/19/20 的 oracle.md 未变。失败趟的 rc=3 与原始 stdout/stderr 如实留档于 runs/R2-append-oracle-addendum/first_execution_failed/。
  本 reviewer 认可 `unchanged_since_generation=false` 是**正确**取值，其含义由 frozen_body_reproducible_by_truncation=true 精确限定。

### 必须修改（P2）
- **P2-A【四卡】两张 hash 清单表未达 drift=0，且相对 r1 是回归。**
  本 reviewer 逐条复算：after/final_deliverable_hashes.json 漂移 M17=25/151、M18=24/142、M19=24/142、M20=25/142；
  evidence/<CARD>/evidence_hashes.json 漂移 M17=14/100、M18=13/91、M19=13/91、M20=14/91。
  漂移项的 sha256 **与 size_bytes 同时不符**（例：M17 commands.json 声称 66917，实际 65909）。
  时序证据：表内 generated_utc = 03:16:24–03:16:28，而每一个漂移项的磁盘 mtime 均为 03:17:53
  ⇒ 表是"最后一次写盘之前"的快照。r1 时同一张表实测为 135/135、drift=0 ⇒ 这是 r2 引入的回归。
  因此简报中"修后两表逐条复算 drift=0"**不可复现，必须撤回或改述**。
  修法：让写表严格成为最后一次写盘；表内写 drift_count/verified_utc；收尾单元在 drift_count!=0 时非零退出；
  排除清单必须恰好覆盖自指文件（表自身、Z 自己的 capture 记录、recovery/closing_run.json、recovery/r2_run.json）；
  修完重跑一次收尾序列并给出实测 drift_count=0。
- **P2-B【批次】rc_namespace.json 不是合法 JSON。**
  本 reviewer 对四卡 attempt + 批次目录共 249 个 .json 做全量解析扫描，唯一失败者即此文件
  （Expecting value: line 11 column 29）：其 runner_sha256_note 使用了 Python 风格的括号内隐式字符串拼接，JSON 不允许。
  该文件是"禁止未标注命名空间的跨卡 rc 聚合"这条硬要求的机器可读副本，必须可被机器读取。
  修法：合并为单个字符串 + 单元内加 json.load 回读自检 + 把"249 个 JSON 全部可解析"作为实测输出。
- **P2-C【M17】两个追加记录文件互相矛盾，且各自含一个错值。**
  revision_r2.json 的 mechanism_proof.line_boundary_is_real = **false**（错，且与紧邻的 note 自相矛盾），
  而 oracle_addendum_record.json 的 boundary_is_a_real_line_boundary = **true**（对）；
  oracle_addendum_record.json 的 added_section_header_line_number = **184**（错），
  而 revision_r2.json 的 r2_section_locations[0].line_number = **186**（对；本 reviewer 实读文件确认行 186 为 `## 13.`）。
  根因定位到两行实现：pack_card.py:160 把"是否为真实行边界"误写成"该偏移是否指向 `## ` 标题"；
  append_oracle_addendum.py:155 用追加前前缀的换行数计算标题行号。
  影响：只读 revision_r2.json 的人会得出"追加前 hash 未能在真实行边界复现 ⇒ 冻结纪律被破坏"这一**错误且严重**的结论，而事实相反。
  修法：修正那两行；重生成这两个 JSON；**oracle.md 必须保持 c9971428… 不变、r2_sections_in_oracle_md=1**，
  不得再次追加或截断（若偏好 append-only，可在这两个 JSON 内追加 boundary_metadata_correction，但不得只修一个）。

### 随附（P3，应与 P2 同批处理）
- **P3-1**：`--repair-restore` 这次对冻结 oracle.md 的破坏性操作**没有独立命令记录**
  （commands.json 的 18 个单元中无任何 repair 条目）。结果状态我已独立验证（无损往返、纯追加），
  缺的是该次调用的 argv/rc/stdout 自证。请补记录，或写明 honest_gap。
- **P3-2**：`verdict_reasons` 把"声明不符"误报为 `negatives_not_rejected:<id>`
  （本 reviewer 的 I1/I2/I6/I7/I8 五组注入均如此，而那些例子里产品确实抛了 ModelRegistryError）；
  且 `declared_expectation_mismatch` 计入了"未抛异常"的情形（I5 注入：raised=None 而该计数=1），不是互斥分类。
  请把 reason 改为中性表述（如 negatives_failed:<ids>）并让两个计数互斥。
- **P3-3**：`cases.json` 缺少 `expected` 键时实测 rc=3/FAIL_declared_expectation_mismatch，
  而 oracle.md §11 与 rc_namespace.json 把"冻结期望缺失"定义为 rc=2。请二选一：
  代码上把负向声明缺失归入"无判定"，或把 rc=2 的适用范围明确限定为"仅正向冻结期望缺失"。
- **P3-4**：process_history.json 的 closing_passes 声明 6 趟（末趟 03:16:24.624 结束），
  但 **03:17:53 那一代写入未被任何一趟命名**（含 commands.json、handoff.json、recovery/closing_run.json、
  recovery/selfcheck_result.json、recovery/selfcheck/*、runs/{B,C2,E,G-pack,H,Z}/rc.json、12 个 evidence/MXX/*.json）；
  且 commands.json 中 Z 的 rc_recorded_utc = 03:15:17.812，早于最后一次 Z 执行（03:16:24.087）。
  请命名该代或写明 `additional_unnamed_generations >= 1` 的 honest_gap。
  另：`declared_vs_observed.reconciliation` 是跨卡常量，文案写 "differ for M17" 却被复制到 M18/19/20（那三卡 declared=1=observed=1），请按卡参数化。
- **P3-5**：`revision_r2.json.independent_review_received=true` /
  `independent_review_verdict_received="accepted_scoped (formula qualification only)"`
  是本 reviewer **r1 headline 的忠实转录**（不是自签，不算失实），但它省略了 r1 附带的两项 P2 条件，
  且在 r2 判定为 changes_required 之后会被读成"复核已签收"。
  请**追加**（勿覆盖）r2 结论字段；batch_handoff.md 第 7-8 行的同一表述也请补上 r2 结论。
- **P3-6（可选，一行）**：review.md §5.6 的 r1 正文仍叙述 2 趟，与 process_history.json 的 3 趟并存；
  r2 节已解释口径，建议加一句交叉引用。

### 跨批复用意见（应要求给出）
5307d2cc… 的"精确类型名"比较**可以作为跨批复用方案**：本 reviewer 扫描了**全部 31 张卡**的冻结 cases.json，
其声明集合**无一例外**恰好是 `'ModelRegistryError'`，故严格等值比较不会在任何现存卡上产生假红。前置条件四项：
(1) 保持精确类型名语义，不得退回 isinstance；
(2) 写入 schema 约束并登记"`expected` 只能是裸异常类型名"——本 reviewer 的 I8 注入证明把声明写成
    M20 卡片 L123 自己使用的复合写法 `"ModelRegistryError/continuity"` 会得到 rc=3（假红），
    今天 31 张卡都不是复合写法，故不是现存缺陷，但未来照抄卡片原文的卡会红；
(3) 先修 P3-2/P3-3，否则新批次继承这两个新问题；
(4) 逐批按 runner sha256 登记命名空间。实测当前各批 runner：
    M01–M04 b5fcc685（无声明强制）、M05–M08 fd3a11c9（无）、M09–M12 997c553b（无）、
    M13–M16 9e4a6450（有，机制不同）、**M17–M20 5307d2cc（有，精确类型名）**、
    M21–M24 d02057de（无）、M25–M28 eab01162（有，机制不同）、M29–M31 9ea69c72（无）。
    ⇒ 简报"那些批的副本仍是 fd3a11c9/9ea69c72"只对 **M05–M08 与 M29–M31** 成立，其余批次各有不同状况。

### 本次仍未验证 / 原样承接（不得当已证）
r1 的 11 条未验证项全部保留，另加：
1. M17 `measurement_pipeline_executions_declared=3` 无法独立证实（字节证据只给出"≥2 个写入世代"，3 与其相容但不可证；已正确标注为 declared）；
2. `closing_executions_declared=6` 与文件系统不一致（至少 03:17:53 那一代未被命名）；
3. 03:17:53 那一代写入的**触发者**无法确定（只证明其存在，不做推测性归因）；
4. `--repair-restore` 的原始输出未留档，其"双向校验通过"只有声称；我验证的是结果状态；
5. M13–M16/M25–M28 的声明一致性机制只做关键字级判别，未评估其等价性，也未评估这些批次任何交付质量；
6. M21–M24/M25–M28/M29–M31 的 rc 语义未核验，不推断；
7. M19/M20 的 r2 节我只读开头 1400 字符与关键字命中统计，未逐字读完；
8. M17/M18/M19 的探针列表未逐条重跑（仅重核 M20 的 BAND 一对数值）。

—— 独立 reviewer，2026-09-20T03:25Z，零写入模式（写入仅限 %TEMP%\m17m20-review-r2-20260920-041815\）


### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。要点：
①上方法庭级判定与"必须修改（P2）"三项、随附 P3-1…P3-6 已逐条处置，处置证据见本卡
`review.md` 的 r2 处置节、`evidence/M19/oq_rulings.json`、`evidence/M19/revision_r2.json`、
`process_history.json`、`after/final_deliverable_hashes.json`（含 `drift_count`/`verified_utc`）与
`evidence/M19/hash_table_selfcheck.json`；
②实现者**未**自签 accepted：`formula` 仍为 `review_pending`，等 reviewer 点审；
③§5.6 的 r1 正文写"2 趟"是 r1 当时的口径，与 `process_history.json` 的"声明 3 趟测量执行"并存，
两者口径已在 r2 节与 `process_history.json.forensic_explanation` 中显式说明（**交叉引用，不改写 r1 正文**）；
④`disclosure_adaptation = unmapped`（零产出）；`accuracy = unproven`。
