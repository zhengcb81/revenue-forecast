# I-11-A 实现者自检报告（**不是验收结论**）

card_id: I-11-A · attempt_id: a20260919-01 · 角色：实现者（弱模型）
**本文件不包含 verdict 字段，也不授予任何资格。** `accepted_scoped` / `changes_required` /
`blocked` / `not_applicable_with_reason` 只能由未参与本卡的独立 reviewer 在独立审查后写入
（`review_and_handoff.md` 第 9 条；START_HERE 第 26 行"实现者不能自签 accepted"）。
为本 attempt 保留的 reviewer 结论位置见本文件 §5。

---

## 1. 一句话结论

本 attempt 把 8 条定性判断冻结为带来源、机制链、已注册 driver、时点、双计排除与可推翻条件的
命题，其中 6 条 `pending_professional_decision`、2 条 `unquantified`、**0 条 approved**；
14 个先冻结的反例全部按预期被拒；7 条算术恒等式用有理数精确复算差为 0；
生产三仓零改动。**本卡不产生任何参数幅度、不产生预测、不产生准确性证据。**

## 2. 自检数字（全部来自脚本输出，非手抄）

| 项目 | 值 | 来源 |
|---|---|---|
| 命题数 | 8 | `evidence/I-11-A/validation_report.json` → `counts.hypotheses` |
| `pending_professional_decision` / `unquantified` / `approved_frozen` | 6 / 2 / **0** | 同上 → `counts.states` |
| 来源类型 | company_disclosure 7；management_target 1 | 同上 → `counts.source_types` |
| independence_group | ZIJIN-AR2025 4；ZIJIN-MGMT-PLAN-2026 1；MSFT-10K-FY2026 3 | 同上 → `counts.independence_groups` |
| 参数（含附加） | 14 | 同上 → `counts.parameters` |
| 引用原值条目 | 46 | `evidence/I-11-A/source_map.json` → `counts.cited_values_total` |
| falsifier 阈值依据 | arithmetic_identity 4；professional_judgement_required 3；disclosure_definition 1（R2 新增第三类） | `counts.threshold_bases` |
| `refuted_by` 条目 | 24 | `counts.refuted_by_total` |
| 反例套件 | 21 例 / 21 例按预期被拒 / 0 例误接受（R2 由 14 例扩充，含 reviewer 指出的 5 个未拒绝变异） | `counterexample_summary` |
| 正例校验 | pass（0 errors） | `positive_case.verdict` |
| 算术 oracle | 7/7 pass（差 0；A4 为符号检验） | `evidence/I-11-A/extract/arithmetic_oracle.json` |
| 不可读来源 | 1（HK-XIAOMI-AR2025） | `source_map.counts.sources_not_readable` |
| 交付文件数 | 见 `attempt_hashes.json` 的 `file_count`（不含 `iso/venv` 与 `__pycache__`） | `evidence/I-11-A/attempt_hashes.json` |
| 最终自检 | `complete_for_review`（最后一次运行在**全部写入之后**；新增"两次捕获时间戳必须不同"的检查） | `evidence/I-11-A/final_selfcheck.json` |

## 3. 卡验收条件 → 证据对照（逐条）

卡正文验收："每命题有可追溯来源、机制、driver、时点、双计排除和明确 unquantified/approved 状态；
不要求全部强行量化。"

| 验收要素 | 本 attempt 的实现 | 可直接复核的证据 |
|---|---|---|
| 可追溯来源 | 每条命题 `source.doc_id` + 原始文件 sha256 + `page_index_basis` + `page_span` + `anchor_text` + `cited_value_key`；46 条引用原值逐条绑定原始串与页码/表号 | `hypotheses.json`、`source_map.json`、`extract/P1_zijin_pages.json`、`extract/P1_msft_tables.json` |
| 机制链 | 每条 4 环，末环为收入确认/期间归属；见 `mechanism_chain` | `hypotheses.json`；`mechanism_review.md` §2.3 |
| 落到模型 driver | 每条给出 `model_id` + `driver_name`，取值逐字来自 `model_cards.md` 的 31 个已注册模型；未注册名会被判 `E_UNKNOWN_MODEL`/`E_UNKNOWN_DRIVER` | `hypotheses.json`；`tools/validate_hypotheses.py` 的 `REGISTERED` 表 |
| 时点 | `published_at`/`available_at`/`as_of` 逐条填写；falsifier 带 `observation_date` | `hypotheses.json` |
| 双计排除 | 每条 `double_count_exclusion`；跨命题风险单列（命题 5） | `hypotheses.json`；`mechanism_review.md` §2.2 |
| 状态明确 | 五态状态机；本 attempt 无 approved（可执行检查 `E_STATE_APPROVED_BY_IMPLEMENTER`） | `validation_report.json` |
| 不强行量化 | 2 条 unquantified；"品牌/竞争力"类判断一律不进入命题；4 个拒绝对量化的理由 | `mechanism_review.md` §4 |
| 计数有脚本 | 所有计数由 `build_hypotheses.py` / `validate_hypotheses.py` / `hash_attempt.py` 产出 | `source_map.counts`、`validation_report.counts`、`attempt_hashes.file_count` |
| oracle 先冻结 | `oracle.md` §0–§9 先写（含 14 个错误码与 O-1…O-17 期望），并如实披露两项先于冻结发生的观测 | `oracle.md` §0.1 |
| 停止条件 | S1–S5；实际触发并登记 1 次（HK 不可读 → `STOP_EVIDENCE`） | `oracle.md` §8；`source_map.not_readable_in_this_attempt` |

## 4. 我自己发现的缺陷与限制（reviewer 应优先看这些）

1. **转写错误（已修，已披露）**：命题 2 初稿把推导值写成 `… ÷ 885,141 = 124,242.28`，
   该数无法由任何被引用原始串复算（正确值 `109977556345/885141 ≈ 124,248.63`）。
   已改为精确有理数，并在 `mechanism_review.md` §6.5 与 `decision.md` DEC-10 如实登记。
   这是"必须能复算"规则真正起作用的一次，不是形式主义。
2. **我自己的定位错误（已修，已披露）**：`verify_arithmetic.py` 首轮把 FY2024 的分部数据与抵销数
   定位到第 327 页（实际 328 页），A2/A3 被自动判 `rejected`；修正页号后通过。
3. **oracle 内部不一致（未改正文）**：`oracle.md` O-6 用了 prior artifact 的页号而未先测定偏移，
   实测 offset = +1。已按 OPEN-8 登记，未回改 oracle 正文（oracle 只能以 R2 附录修订）。
4. **港股来源不可读**：HK-XIAOMI-AR2025 在本 attempt 的两条路径下都无法读出可引用原文
   （415 个经典页对象可枚举、前 30 页内容流 30 条可解压但抽样页 0 字符、全文件仅 1 个经典字体带
   `/ToUnicode` 引用；`pdftotext` 输出 Adobe-CNS1 乱码），判 `STOP_EVIDENCE`，**零**条港股命题。
   （理由已按独立复核 P1-3 由实测重写，见 `mechanism_review.md` §5。）
5. **MSFT FY2027 分部口径不确定**：10-K 仍按 PBP/IC/MPC 编制（`Agents and Infra` 出现 0 次），
   as_of 之后的重分类 8-K 原文不在本地可核来源，故八线口径既未引用也未否定（OPEN-3）。
6. **取文器能力边界**：`tools/pdf_text.py` 不做表格结构还原，同排相邻字段会被拼接
   （例如 `109110.45`）。**禁止**用它做列对齐级引用；引用一律以字段级原始串为准。
7. **页面索引口径未规范化**：本 attempt 用 `pdf_leaf_1based` / `table_index_0based`，
   与 schema 层枚举的关系未定（OPEN-4）。
8. **占位阈值**：3 条 falsifier 阈值标 `professional_judgement_required`，**未审定**（OPEN-6）；
   另有 1 条（Microsoft Cloud 聚合口径）在 R2 改判为 `disclosure_definition`（判定式而非幅度）。
9. **校验器强度有限（R2 新增，复核 P2-5）**：首版校验器对机制链末环语义、观察日、O-11 唯一参数
   规则、`threshold_basis` 诚实性**无机器检查**，reviewer 自造 7 个变异中 5 个当时未被拒绝；
   R2 已补 4 类检查、反例套件扩到 21 例，但**仍不完备**（只覆盖已写下的规则）。
10. **状态捕获对的语义（R2 新增，复核 P1-1）**：两次捕获均已重做为时间戳不同的两次，但两者都在
   本 attempt 工作**期间**取得，**不能**作为"开工前基线"或"生产零改动"的独立证明；
   该结论由第三方复核与"本卡无生产写入路径"承载（DEC-13）。

## 5. 独立 reviewer 裁决（由实现者**转录**独立复核报告 §7；实现者未参与、未改写结论）

来源：独立复核报告 `%TEMP%\i11a-review-20260920-040601\REPORT.md`（46,451 B，
sha256 `e8b7d223e83c91128545e2b25b28b97ecba50cf2a5855e7366fabcaba16cafaf`；
同 hash 副本 `C:\i11a-rv\review\REPORT.md`）。以下为报告 §7 的裁决正文，逐字转录：

```
reviewer_verdict:            accepted_scoped
reviewer_identity:           独立 reviewer session（未参与 I-11-A 的编写；只读生产仓库；
                             全部复算使用自建取文/解析脚本，未导入 attempt/tools 下任何模块）
reviewer_recomputed_oracle:  用自建 PDF 取文（自写对象扫描 + ToUnicode CMap + 内容流解释器，含
                             Form XObject 下钻）与自写 MSFT HTML 表格解析，独立取得操作数后以
                             fractions.Fraction 精确复算：A1–A7 全部差 = 0；另自造三组清单外恒等式
                             （A3b: FY2024 总计和 − 抵销 = 303,639,957,153；A3c: 两年 × 四分部的
                             「对外 + 内部 − 总计」= 0，8/8；N1: FY2024 三旧分部与十个产品行
                             各自 = 245,122）同样差 = 0。109,977,556,345 ÷ 885,141 的精确商为
                             124248.62970419403，四舍五入 2 位 = 124,248.63，与自曝的更正一致；
                             自曝的 124,242.28 无法由任何被引用串复算，自曝属实。
                             46 条引用原值中 CN-ZIJIN 侧 30 条（25 + 5）已逐条在自建页码映射中
                             定位成功（页码 + 原始串均一致）；MSFT 侧 13 值 + 3 条叙述事实由自写
                             解析在 10-K 原文中命中（含 FY2024 交叉核对）。
reviewer_reserved_case:      审查前预先写死 7 个实现者未使用的反例（见 §2 P2-5）。结果：
                             page_index_basis 末尾加空格 → 被拒（E_BAD_PAGE_BASIS）；
                             doc_id 换成小米而保留紫金 sha256 → 被拒（E_SOURCE_HASH_MISMATCH）；
                             但 state=approved_frozen 配任意非黑名单 reviewer 名 → 被接受；
                             threshold_basis 冒充 arithmetic_identity（阈值文本为 ±7%）→ 被接受；
                             refuted_by = ["", "   "] → 被接受；mechanism_chain = ['a','b','c'] → 被接受；
                             observation_date = "TBD" → 被接受；两条同 parameter_id 的相同命题 → 被接受。
                             结论：14/14 反例有效但属有限测试；校验器对 oracle §3.3 末环语义、
                             §3.4 观察日、O-11 唯一参数规则、threshold_basis 诚实性均无机器检查。
qualifications_granted:      （1）I-11-A 的「定性 → 参数的可证伪命题（冻结契约提案）」这一
                             限定范围成立：8 条命题在结构上满足卡正文验收（来源 / 机制链 /
                             已注册 driver / 时点 / 双计排除 / 明确状态 / 预登记可推翻条件）；
                             （2）状态机与计数经独立重算确认（approved_frozen 0、
                             pending_professional_decision 6、unquantified 2、参数 14、refuted_by 24、
                             阈值依据 4+4）；
                             （3）卡片专属算术 oracle 独立复算通过（含三组自造恒等式）；
                             （4）STOP_EVIDENCE（HK-XIAOMI-AR2025）成立，零条港股命题，
                             无二手稿补位。
qualifications_not_granted:  formula = not_applicable_here（本卡不运行模型）；
                             disclosure_adaptation = NOT granted（属 I-10-A；本卡只做
                             「原文 → 原始串 / 页码 / 单位」的只读取证，且铜当量系数未披露，
                             该式判 STOP_DISCLOSURE_ADAPTATION 是正确的）；
                             accuracy = NOT granted（属 I-12）；
                             任何参数幅度 / low-base-high / 已批准参数 = NOT granted；
                             I-11-B / I-11-C / I-07-E = NOT unlocked（0 条 approved_frozen，
                             且 OPEN-2/3/5/6 阻塞参数校准与触发器生效）。
open_items_for_owner:        OPEN-1 建议「允许但降级为交叉核对路径，sha256 固定，禁止为取文升级 Git」；
                             OPEN-2/3/5/6 的裁定人分派（会计 + 矿业/软件行业 reviewer + 环境 owner）；
                             OPEN-8 本 reviewer 意见：接受「以择优规则为准」，不回改 oracle 正文；
                             OPEN-10 核实成立（目录 mtime 09:14:20 vs 目录内最新文件 mtime 10:05:32，
                             两者口径不同、并不矛盾）。
conditions_carried:          随签携带三条必修项（不改变 verdict）：
                             P1-1 before/after 两次捕获时间戳相同（2026-09-20T03:04:43+00:00），
                                  且该时点晚于本 attempt 目录创建时间（03:32:54），
                                  「生产零改动」结论由第三方复核支持而非由该对证据支持；
                             P1-2 changes.diff 有 7/93、attempt_hashes.json 有 2/93 条记录陈旧
                                  （含两者自指记录）；7 份交付件与 final_selfcheck 的 18 条记录
                                  则与现值完全一致；
                             P1-3 source_map/binding 关于小米的能力描述写错（实为 415 个经典页对象、
                                  0 个 ToUnicode CMap、抽样 3 页 0 字符、pdftotext 乱码），
                                  结论方向不受影响但理由必须改写。
                             另：P2-4 ~ P2-9 建议在 I-11-B 前修；P3-10 ~ P3-12 可随签携带。
```

**转录声明**：以上裁决由独立 reviewer 作出，实现者仅转录，**未**改动任何结论文字。
本节之外（§1–§4、§6–§7）仍是实现者的自检内容，不构成裁决。

### 5.1 复核后对 3 项必修与建议项的处置（实现者填，reviewer 可复验）

| 编号 | 处置 | 落点 |
|---|---|---|
| P1-1 | 已改：两次捕获重做为**时间戳不同**的两次，并在文件内声明为 `state_capture_1/2`（工作期间快照，非开工前基线）；`final_selfcheck` 改为先查"两次捕获是否同一时间戳"（相同即判 problem）并写入 `claim_boundary`；`changes.diff` 头部改为带**生成时点**的 porcelain 观测 + 明示 `ddc81ab`（2026-09-20 04:09 本地）已在复核时点把本 attempt 纳入 git | `tools/finalize_state.py`、`tools/final_selfcheck.py`、`tools/make_changes_diff.py`、`evidence/I-11-A/state_*.json`、`changes.diff`、`decision.md` DEC-13 |
| P1-2 | 已改：两张复合清单在**所有其他写入之后重生成**；`hash_attempt.py` / `make_changes_diff.py` 增加"自指不可自证 + 后写即陈旧"的头部声明；`.pyc` 与 `__pycache__/**` 明确列入 `excluded_from_manifest` | `changes.diff`、`evidence/I-11-A/attempt_hashes.json`、`tools/hash_attempt.py`、`tools/make_changes_diff.py` |
| P1-3 | 已改：新增 `tools/probe_xiaomi.py` 实测（415 个经典页对象、前 30 页 30 条内容流可解、字面串 3,264 / 十六进制串 2,756、抽样页 0 字符、5 个经典字体仅 1 个带 /ToUnicode 引用、pdftotext 乱码）；`source_map` 的理由与 `mechanism_review.md` §5 按实测重写并附 `measured_facts`；`binding.json` 的 `352→0` 措辞一并更正 | `tools/probe_xiaomi.py`、`evidence/I-11-A/extract/P1_xiaomi_content_probe.json`、`source_map.json`、`mechanism_review.md` §5、`binding.json` |
| P2-5 | 已改（并**显式承认仍不完备**）：校验器新增检查（`threshold_basis` 闭集+一致性、机制链末环语义与最短长度、观察日可解析、O-11 唯一参数规则、`approved_frozen` 身份与 `decision_sha256`）；反例套件 14 → **21**，reviewer 指出的未拒绝变异全部固化并现已被拒 | `tools/validate_hypotheses.py`、`oracle.md` §R2-1、`mechanism_review.md` §5 第 9 条、`decision.md` DEC-14 |
| P2-6 | 已改：改写为「系数 +1 吨/千克 ⇒ 当量分母 +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨」，并注明**两点差分不是偏导**（分母单独 +1 吨仅约 0.14 元/吨） | `hypotheses.json`（H-CN-ZIJIN-SEG-02 `conversion_formula`）、`mechanism_review.md` OPEN-2、`decision.md` OPEN-2 |
| P2-7 | 已改：探针按"文件级字节统计 / 全流统计 / **页面内容流**统计"三档分开报告，文档统一按内容流口径叙述 | `tools/probe_xiaomi.py`、`source_map.json`、`mechanism_review.md` §5 |
| P2-8 | 已改：命题 3 的阈值不再使用未披露的"期初库存"，改为"由上一期披露的期末库存取得期初库存 + 与库存量同比变动方向一致"的判定式，并新增 `observability_note`；跨期可得性登记为 OPEN-11 | `hypotheses.json`（H-CN-ZIJIN-VOL-03 `falsifier`）、`mechanism_review.md` §5 第 9 条、`decision.md` OPEN-11 |
| P2-9 | 已改：`plan_reviews` 改为**全量递归枚举**（path/byte_size/mtime_local）+ `newest_file` 字段，不再只存目录名样本 | `tools/capture_state.py`、`state_before.json`、`state_after.json` |
| P3-10 | 已改：`.pyc` / `__pycache__/**` 列入排除清单并在清单里写明原因 | `tools/hash_attempt.py`、`tools/make_changes_diff.py` |
| P3-11 | 已改：`commands.json` 与 `handoff.json` 的命令计数与 id 列表对齐 | `commands.json`、`handoff.json` |
| P3-12 | 已改：中间产物 `tmp_*.json` 归入 `evidence/I-11-A/scratch/`，交付目录只留被引用文件 | `evidence/I-11-A/scratch/` |


## 6. 本卡不授予的资格（明确声明）

- **formula**：本卡不运行任何模型，`not_applicable_here`；
- **disclosure_adaptation**：`not_granted`（属 I-10-A；本卡只做"原文 → 原始串/页码/单位"的取证）；
- **accuracy**：`not_granted`（属 I-12）；
- **发布/部署/自然观察**：不适用（本卡无产品改动）；
- **I-11-B / I-11-C / I-07-E 的解锁**：**未解锁**。本 attempt 产出 0 条 `approved_frozen`，
  且 OPEN-2/3/5/6 明确阻塞 I-11-B 的参数校准。

## 7. 生产仓库零改动的证明

- `evidence/I-11-A/state_before.json` 与 `state_after.json`：三仓 HEAD、porcelain 条目、
  关键文件 sha256 完全一致（`final_selfcheck.json` 的 `production_state_unchanged` 检查项）；
- revenue-forecast porcelain 中与本卡相关的条目只有一条
  `?? .planning/.../execution_runs/I-11-A/`（本 attempt 自身，未跟踪），
  其余 125 条为**本次工作之前已存在**的用户改动与其他卡的 attempt（before/after 一致）；
- 未执行 `git add` / `commit` / `restore` / `stash`；
- PLAN/reviews 未被写入：`state_before/after` 记录其 mtime；
  另经独立枚举确认 reviews 下 285 个文件中**没有**任何文件的最后写入时间晚于
  本 attempt 开始工作的时间（详见 handoff `current_source_hashes.plan_reviews_note`）。
  **注意一个与用户口径不符的既有事实**：`reviews` 目录的 LastWriteTime 实测为
  `2026-09-19 09:14:20`，而不是任务说明里的 `10:05`；本 attempt 无法改变它（未写入），
  该差异登记为 OPEN-10 供 owner 核对。
