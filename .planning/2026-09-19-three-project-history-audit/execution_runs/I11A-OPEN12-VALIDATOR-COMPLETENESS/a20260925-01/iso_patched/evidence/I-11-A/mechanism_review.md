# I-11-A 机制链审查包（交行业 reviewer；本文件不是验收结论）

card_id: I-11-A · attempt_id: a20260919-01 · 生成者：实现者（弱模型）· 状态：`review_pending`
本文件的服务对象是**行业 reviewer**（卡正文动作 4）。实现者不签署任何命题；下表"建议"列不是裁定。

计数来源：`evidence/I-11-A/validation_report.json` 与 `evidence/I-11-A/source_map.json` 的 `counts`
字段（由脚本统计，不手抄）。本次工作的所有数字都可在该两文件与
`evidence/I-11-A/extract/arithmetic_oracle.json` 中找到同值字段。

| 计数项 | 值 | 来源字段 |
|---|---|---|
| 命题数 | 8 | `validation_report.counts.hypotheses` |
| `pending_professional_decision` | 6 | `validation_report.counts.states` |
| `unquantified` | 2 | `validation_report.counts.states` |
| `approved_frozen` | **0** | `validation_report.counts.states`（oracle O-8 要求为 0） |
| 来源类型：company_disclosure / management_target | 7 / 1 | `validation_report.counts.source_types` |
| independence_group | ZIJIN-AR2025 4；ZIJIN-MGMT-PLAN-2026 1；MSFT-10K-FY2026 3 | `validation_report.counts.independence_groups` |
| falsifier 阈值依据：算术恒等式 / 需专业审定 / 披露定义 | 4 / 3 / 1 | `validation_report.counts.threshold_bases` |
| `refuted_by` 条目总数 | 24 | `validation_report.counts.refuted_by_total` |
| 参数（含附加）总数 | 14 | `validation_report.counts.parameters` |
| 引用原值条目总数 | 46 | `source_map.counts.cited_values_total` |
| 本 attempt 不可读的来源 | 1（HK-XIAOMI-AR2025） | `source_map.counts.sources_not_readable` |
| 反例套件 | 21 例，21 例按预期被拒（R2 由 14 例扩充） | `validation_report.counterexample_summary` |

> **R2 修订说明（2026-09-20，独立复核后）**：独立 reviewer 判定 `accepted_scoped` 并携带 3 项必修
> （见 `review.md` §5）。本文件已按意见更正：(a) 小米不可读的**理由**改为实测事实（415 个经典页对象、
> 30 页内容流 30 条可解、抽样页 0 字符、5 个经典字体中仅 1 个带 /ToUnicode 引用、pdftotext 乱码），
> 结论方向不变（P1-3）；(b) 「每 +1 吨/千克 ≈ 10,670.9 元/吨」改写为「系数 +1 吨/千克 ⇒ 当量分母
> +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨」并注明这是**两点差分不是偏导**（P2-6）；
> (c) 命题 3 的阈值不再依赖未披露的「期初库存」，改为可用现有披露判定的形式，并把跨期可得性
> 登记为需行业 reviewer 确认（P2-8）；(d) 校验器补齐 4 项机器检查、反例套件由 14 例扩到 21 例
> （P2-5，oracle §7 的 R2 扩充）。以上修订只**新增**字段与说明，未删除任何 reviewer 已复核的引用原值。

---

## 1. 命题清单（8 条；字段全文见 `hypotheses.json`）

| # | hypothesis_id | 主体 | model_id / driver_name | parameter_id | state |
|---|---|---|---|---|---|
| 1 | H-CN-ZIJIN-SEG-01 | 紫金·四分部对外收入合计 | direct_revenue / revenue（+3 附加） | ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027 等 4 个 | pending |
| 2 | H-CN-ZIJIN-SEG-02 | 紫金·矿产品单位实现收入 | resource / realized_price | ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 | pending |
| 3 | H-CN-ZIJIN-VOL-03 | 紫金·铜金可售量受产量与库存约束 | resource / saleable_volume（+1 附加） | ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027 等 2 个 | pending |
| 4 | H-CN-ZIJIN-PLAN-04 | 紫金·2026 产量计划=管理层目标 | resource / saleable_volume（+1 附加） | ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER 等 2 个 | pending |
| 5 | H-CN-ZIJIN-ELIM-05 | 紫金·内部抵销必须成对使用 | direct_revenue / revenue | ZIJIN_SEGMENT_RECONCILIATION_FY2027 | unquantified |
| 6 | H-US-MSFT-SEG-01 | 微软·三分部合计与分部差异 | direct_growth / growth_rate（+2 附加） | MSFT_PBP_REVENUE_FY2027 等 3 个 | pending |
| 7 | H-US-MSFT-SEG-02 | 微软·Microsoft Cloud 聚合口径 | direct_revenue / revenue | MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER | unquantified |
| 8 | H-US-MSFT-SEG-03 | 微软·产品/服务分解行与许可-云混合 | subscription / revenue_per_customer | MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027 | pending |

> `_PLACEHOLDER` 后缀是**故意的**：这两条命题的 parameter_id 已被占用但**尚未被批准可用于预测**，
> 加 `PLACEHOLDER` 是为了让 I-11-B 的脚本不可能把它误当成已审定参数。

---

## 2. 动作 4 逐条审查：可观测性 / 时间滞后 / 是否已在基期或其他 driver 反映

**这一节的结论全部是"待裁定"，不是裁定。** 行业 reviewer 需要逐行给出自己的判断；
实现者给出的是**判断所需的原始事实**与**建议提问**。

### 2.1 可观测性

| # | 观测量（原文可定位？） | 观察日 | 时间滞后（相对基期 FY2025） | 实现者建议 |
|---|---|---|---|---|
| 1 | 四分部"对外销售收入"行 + 合并利润表营业收入行 —— 是（p327/328、p43） | FY2026 年报（预计 2027-03） | 12 个月 | 建议 approved（恒等式类，无判断空间） |
| 2 | 分部对外收入 + 产销量表销售量 —— 是（p327、p44） | FY2026 年报 | 12 个月 | 需先裁定铜当量系数（见 §4） |
| 3 | 产销量表三列（生产/销售/库存）—— 是（p44） | FY2026 年报 | 12 个月 | 需先看存货明细（在产品/在途）是否披露 |
| 4 | 2026 产量计划的实现值 —— 计划在 p56 可定位；实现值属**未来披露**，本 attempt 不可得 | FY2026 年报 | 12 个月 | 目标类，不得作为独立证据（已强制） |
| 5 | 分部总计行 + 抵销列 —— 是（p327/328） | FY2026 年报 | 12 个月 | 建议 approved（恒等式类） |
| 6 | 三分部收入行与变动比例行 —— 是（table 74/14） | FY2027 10-K（预计 2027-07/08） | 12 个月 | 需先裁定分部重分类（见 §4 OPEN-3） |
| 7 | Microsoft Cloud 与产品行的映射 —— **否**（10-K 无对账表） | 需求出现于 FY2027 10-K | ≥12 个月 | 建议保持 unquantified |
| 8 | 云/许可拆分、平均付费席位、净 ARPU —— **否**（10-K 未披露） | FY2027 10-K | ≥12 个月 | 建议保持 pending |

### 2.2 是否已在基期/其他 driver 反映（双计排除的实现者判断）

| # | 双计风险 | 排除规则（已写入 `double_count_exclusion`） | 建议 |
|---|---|---|---|
| 1 | 分部对外收入 与 合并营业收入 是同一笔钱的两种呈现 | 只允许对外口径；内部销售 234,970,146,412 元只出现在抵销桥 | 排除 |
| 2 | 单位价格 × 数量 与 "分部收入直接外推" 会重复解释同一增量 | 价格与量分别落参数；量价之外的"额外收入"不得叠加 | 排除（但需裁定系数） |
| 3 | 产量增长 与 销量增长 被当作两个独立解释 | 生产/销售/库存三者各出现一次；权益产量不得与控股口径相加 | 排除 |
| 4 | 计划产量 既当产能上限又当收入基数 | 计划值只进情景对照，收入侧只允许一次转换 | 排除 |
| 5 | 584,049,229,264 与 349,079,082,852 同时作为基期 | 只用后者；前者仅在抵销桥中出现 | 排除 |
| 6 | 集团增长率 与 三分部增长率 同时计入 | 只允许三分部；集团数由分部相加得到 | 排除 |
| 7 | Microsoft Cloud 与 IC 分部收入并列 | 二者不得同时作为收入路径（Azure 在 IC 内） | 排除 |
| 8 | table 74 分部行 与 table 76 产品行相加 | 两套切分互斥；行内许可与云不得用两个故事解释同一增量 | 排除 |

### 2.3 机制链是否真的落到"收入确认"

8 条命题的 `mechanism_chain` 最后一环都写成期间归属/确认语义（例如"金属交付并转移控制权时确认，"
"分部收入按 ASC 606 在履约义务满足时确认"）。**实现者提醒 reviewer**：这四环链条的**第二环**
（经营驱动）在本 attempt 中**没有**任何内部成本/产能数据支撑，因此"产能利用率"这类中间量
未被量化——这正是本卡只陈述驱动、不做幅度校准的原因。

---

## 3. 算术 oracle 的复算结果（先手算，后复算）

`evidence/I-11-A/extract/arithmetic_oracle.json` 用 `fractions.Fraction` 精确复算，7/7 通过：

| 编号 | 恒等式 | 差值 |
|---|---|---|
| A1 | 紫金 FY2025 四分部对外收入之和 = 合并营业收入 349,079,082,852 | 0 |
| A2 | 四分部总计 584,049,229,264 − 抵销 234,970,146,412 = 349,079,082,852 | 0 |
| A3 | 紫金 FY2024 四分部对外收入之和 = 303,639,957,153 | 0 |
| A4 | 紫金 FY2025 四产品 销售量 > 生产量（金 +418 kg、铜 +6,763 t、锌 +3,914 t、银 +872 kg） | 符号检验通过 |
| A5 | 微软 FY2026 三分部 139,996+137,791+54,052 = 331,839 | 0 |
| A6 | 微软 FY2026 十个产品/服务行之和 = 331,839 | 0 |
| A7 | 微软 FY2025 两项分解各自 = 281,724 | 0 / 0 |

**A4 的边界**：它只证明"销量高于产量"，**不**证明存货桥闭合。库存量还受并购范围、在产品、
在途/寄售影响；把 A4 读成"库存桥成立"是超范围使用。

---

## 4. 明确拒绝的量化（"品牌好"类判断不强行加百分点）

本 attempt **拒绝**把下列内容写成参数（保留叙述，理由写在此处）：

1. **紫金铜当量换算系数**：公司未披露。命题 2 里被写成"1 千克金 = 24 吨铜当量"的**示意**系数
   会让单位收入从 124,248.63 变为 113,577.74（系数 +1 吨/千克时），差 10,670.89 元/吨铜当量。
   因此该系数**不是参数**，是待裁定项（OPEN-2）。
2. **产能利用率、回收率、品位**：需要矿山级披露，本 attempt 未取到逐矿数据，故命题 3 只写
   "可售量 ≤ 生产量 + 库存变动"的**上限约束**，不写利用率参数。
3. **Microsoft Cloud 的组成映射**：10-K 只有 KPI 定义与叙述值（FY2026 +27%、$214.4 billion），
   没有与分部/产品行的对账表，故命题 7 保持 `unquantified`，**不**给任何拆分比例。
4. **平均付费席位 / 净 ARPU / 广告曝光与 CPM / RPO 转收入比例**：10-K 未披露（RPO 仅披露
   余额 678 billion 与 +84%），故命题 8 不给单位经济学数值。
5. **"竞争力/品牌/管理层执行力"类判断**：无对应的可观测原始披露，一律不进入命题（卡正文
   "'品牌好'等不能量化的判断保留叙述"）。

---

## 5. 已知限制（reviewer 必须知道，且不得当作已解决）

1. **HK-XIAOMI-AR2025 在本 attempt 不可读**（判定依据：oracle O-7；理由已按 review P1-3 改写）。
   - 标准库路径：`tools/probe_xiaomi.py` 实测**可以**枚举出 **415 个经典 /Type /Page 对象**
     （原始字节扫描到 420 处 `/Type /Page`，差额为 `/Pages` 树节点），所以"枚举不到页对象"不是障碍；
     前 30 页的 `/Contents` 流 30 条全部可解压（0 条缺失），其中含 3,264 个字面串与 2,756 个十六进制串，
     但 `Page.fragments()` 对每个抽样页都返回 **0 字符**；全文件 5 个经典字体对象中只有 1 个带
     `/ToUnicode` 引用（对应原始字节里唯一一处 `/ToUnicode`），解码后 4 个 CMap 流含 bfchar/bfrange 块，
     而本读取器无法把它们与页面内容流里的字形码对上（工作字体是嵌入式子集、无可用映射）。
   - 独立路径 `pdftotext` 退出码 0，但输出为 Adobe-CNS1 乱码：已归档的第 1–12 页输出
     （`P2_xiaomi_probe.txt`，12,145 字节）不含 `小米`/`收入`/`年度報告` 任一字符串；
     reviewer 另跑全文件得 998,598 字节乱码输出，该次运行**未在本 attempt 归档**，只作为复核方证据转述。
   - 因此该来源标 `STOP_EVIDENCE`，**没有**任何来自小米年报的数值进入 `hypotheses.json`。
     不得用任何二手转述（含 revenue-forecast 审计目录中的研究稿）替代原文。→ OPEN-5。
   - **R2 更正登记**：初稿此处曾写"423 /ObjStm、0 个经典页对象"且 `binding.json` 写"352→0"
     （352 是紫金的页数）。该措辞错误由独立 reviewer 指出（P1-3），现已按上面的实测重写；
     当时被抽样的 3 页（obj 1/5/9）各 0 字符这一事实仍然成立，只是它**不是**因为枚举不到页对象。
2. **MSFT 的 FY2027 口径存在 as_of 之后的重大不确定性**：10-K（2026-07-29）仍按 PBP/IC/MPC 三报告
   分部编制，10-K 内 `Agents and Infra` / `Devices and Consumer` 出现 0 次；而审计目录中的研究稿
   （非本卡证据）记载 2026-09-02 的 8-K 披露了重分类与八条业务曲线。该 8-K 原文在本 attempt
   的本地可核来源中**不存在**，且本卡禁网，因此八线口径**未被引用、也未被否定**。→ OPEN-3。
3. **紫金 H 股英文版年报与 A 股版页码体系不同**：本次只用 A 股版（`01819e1c…`）。
   `pdftotext` 对同一 PDF 第 44 页输出的段落标题与 A 股版排版不同（内容一致），
   说明"页码 + 锚文本"必须成对引用，不能只给页码。
4. **页面索引口径尚未成为 schema 规范值**：本 attempt 使用 `pdf_leaf_1based`（PDF 物理页从 1 起）
   与 `table_index_0based`（HTML 表格序号从 0 起）。`common_model_cards.md` 要求披露字段含
   `page/table/span`，但未规定索引口径；若 I-10-A/I-07-E 采用别的口径（例如打印页码），
   本卡的 `page_span` 需要重映射。→ OPEN-4。
5. **取文器是对抗性不足的自制工具**：`tools/pdf_text.py` 只实现到"能读出被引用数值"的程度，
   不做表格结构还原。同一表格行内的相邻字段会被拼成 `109110.45` 这类串（见 §6），
   因此**禁止**用它的输出去做"表格列对齐"级别的引用；引用一律以字段级原始串为准。
6. **未做**：任何外部来源（本卡禁网）、任何 provider/LLM 调用、任何模型运行、任何幅度校准。
7. **与 oracle O-6 的方法学冲突（如实登记）**：`oracle.md` §2 的 O-6 用了 prior artifact 的**页号**
   去取 P1 文本，而当时的 offset 尚未测定；实测 offset = +1（prior 页号 = PDF 物理页 − 1），
   本节 §6 的交叉核对已按实测偏移进行，**O-6 的原始措辞在页号上不成立**。
   登记为 OPEN-8；独立 reviewer 的裁定意见是"接受以择优规则为准、不回改 oracle 正文"
   （如需留痕按 R2 附录加一行）。本次按该意见处理：oracle 正文未改。
8. **校验器强度是有限的（R2 新增披露，review 发现 P2-5）**：首版 `validate_hypotheses.py` 对
   oracle §3.3 的机制链末环语义、§3.4 的观察日、O-11 的"一个 parameter_id 只对应一条命题"、
   以及 `threshold_basis` 的诚实性**没有机器检查**；reviewer 自造的 7 个清单外变异中有 5 个
   当时未被拒绝（`approved_frozen` + 编造 reviewer 名、`threshold_basis` 冒充 `arithmetic_identity`、
   `refuted_by=["","   "]`、`mechanism_chain=['a','b','c']`、`observation_date="TBD"`、
   两条同 parameter_id 的相同命题）。R2 已补齐这四项检查并把反例套件由 14 例扩到 **21 例**
   （新增 7 例全部按预期被拒）。**但这仍不是完备性证明**：校验器只覆盖已写下来的规则。
9. **命题 3 的阈值原本不可观测（R2 已改，review 发现 P2-8）**：初稿阈值用了"期初库存"，
   而年报产销量表只披露**期末**库存量与三项同比变动；阈值已改写为"由上一期披露的期末库存
   取得期初库存 + 与库存量同比变动方向一致"的判定式，并把跨期可得性登记为待行业 reviewer
   确认的事项（不阻塞本卡）。若上一期数据缺失，该式不可判定，转 `STOP_DISCLOSURE_ADAPTATION`。

---

## 6. 提取器可信度的取证方式（为什么这些原文串可以信）

- **两条独立路径**：自制标准库取文器（P1）与 Xpdf `pdftotext`（P2，sha256
  `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0`）。二者无共享代码。
- **与既有独立提取件的交叉核对**：`P1_vs_prior_offset.json` 对 offset ∈ {−1,0,1,2} 全部试算，
  择优结果显示 prior artifact 的页号与 PDF 物理页相差常量 1；被引用页面上的被引用数值串
  在两侧文本中同时出现。该交叉核对**只用于验证取文器**，不构成任何命题的来源。
- **算术一致性反证**：A1–A7 用有理数精确复算差为 0（若取文器系统性错位，恒等式极难同时成立）。
- **自纠记录**：本 attempt 出现过两处由一致性检查抓出的**我自己的错误**，如实登记：
  1. 命题 2 初稿把推导值写成 `109,977,556,345 ÷ 885,141 = 124,242.28`。该结果无法由任何
     被引用原始串复算（正确值为 `109977556345/885141 ≈ 124,248.63`；885,141 这个分母也不是
     任何被引用的量）。已在 `hypotheses.json` 中改为精确有理数并写明系数敏感性。
     **这不是原文错误，也不是计算器的错误，而是我在写作时的转录错误**；因此本卡的
     `oracle.md` §5 要求"所有被引用数值必须能被复算"是必要的，而不是形式主义。
  2. `tools/verify_arithmetic.py` 首轮把 FY2024 的分部数据与抵销数定位到第 327 页
     （实际在第 328 页），导致 A2/A3 被自动判为 `rejected`；修正页号后通过。这说明
     "定位失败即拒绝"的规则确实在起作用。

---

## 7. 开放项汇总（编号 / 问题 / 裁定人 / 是否阻塞 I-11-A 签收）

| 编号 | 问题 | 裁定人 | 阻塞本卡签收？ |
|---|---|---|---|
| OPEN-1 | 是否允许在卡内使用仓库外的控制台工具 `pdftotext.exe`（Git for Windows 自带）作为第二条独立取文路径？本次使用已如实登记 argv/hash/输出 | PLAN owner（或环境规范制定者） | 不阻塞（作为已知方法登记）；若 owner 否决，需在 I-11-B 前改用别的独立路径 |
| OPEN-2 | 紫金矿产品单位实现收入的"铜当量换算系数"从何而来（披露/外部可比/专业假设）？结论对该系数高度敏感：系数 +1 吨/千克 ⇒ 当量分母 +83,161 吨 ⇒ 单位收入 **−10,670.89 元/吨铜当量**（两点差分，非偏导；见 hypotheses H-CN-ZIJIN-SEG-02 的 conversion_formula） | 会计 reviewer + 矿业行业 reviewer | 不阻塞本卡（命题仍为 pending）；**阻塞 I-11-B 对该参数的幅度校准** |
| OPEN-3 | FY2027 起微软的建模分部是否仍为 PBP/IC/MPC？（as_of=2026-09-18 之后的 8-K 重分类未进入本地可核来源） | 行业 reviewer（软件与云）+ 会计 reviewer | 不阻塞本卡（命题 6 已声明失效条件）；**阻塞 I-11-B/I-07-E 的微软分部选择** |
| OPEN-4 | 位置口径 `pdf_leaf_1based` / `table_index_0based` 是否需成为披露字段的规范枚举值（schema 层） | schema owner（I-10-A/I-07-E 的接口 owner） | 不阻塞本卡；阻塞跨卡页码复用 |
| OPEN-5 | HK-XIAOMI-AR2025 的原文可读性由谁解决（对象流解析能力/离线 PDF 库/合规的外部工具） | 环境/依赖 owner（I-00-B 侧）+ 行业 reviewer | 不阻塞本卡（该来源已判 STOP_EVIDENCE）；**阻塞任何港股份部的命题与 I-11-B 的港股参数** |
| OPEN-6 | 8 条命题的 `falsifier.threshold` 中 4 条标为 `professional_judgement_required`（±5%、0.9–1.1 计划达成区间等），阈值是否按此采用 | 行业 reviewer（矿业/软件各自） | 不阻塞本卡（已按 O-12 登记依据类型）；**阻塞 I-11-B/I-11-C 的触发器生效** |
| OPEN-7 | 命题 1/6 的分部集合是否就是 FY2027 的最小建模块（分部生命周期与并购范围可能变化） | 行业 reviewer | 不阻塞本卡 |
| OPEN-8 | oracle O-6 的措辞用了未测定的 prior 页号（实测 offset = +1）；是修订 oracle 正文（R2 附录）还是以择优规则为准 | 独立 reviewer（读 oracle 的人） | 不阻塞本卡；若不裁定，会让后续读者以为 O-6 的页号可直接使用 |
| OPEN-9 | I-11 参数模板是否升级为本卡的超集字段 | `common_research_cards.md` owner | 不阻塞本卡；影响跨卡 schema 一致性 |
| OPEN-10 | `PLAN/reviews` 的 LastWriteTime 实测 `2026-09-19 09:14:20`，与任务说明的 `10:05` 不符（本 attempt 未写入该目录）。reviewer 补充核实：目录内**最新文件** mtime 为 `2026-09-19 10:05:32`（`second_wave/final_review_checks.json`），两个口径都对、不矛盾，建议后续卡采用"最新文件 mtime"口径 | PLAN owner | 不阻塞本卡；影响后续卡对 reviews 只读基线的判断 |
| OPEN-11 | 命题 3 的库存判定式需要"上一期披露的期末库存"作为期初库存，跨期可得性由谁确认（R2 新增，review P2-8） | 矿业行业 reviewer | 不阻塞本卡；若不可得则该式不可判定，须转 STOP_DISCLOSURE_ADAPTATION |

---

## 8. 实现者给 reviewer 的最短阅读路径

1. `binding.json` → 三仓只读路径、解释器、允许写目录；
2. `oracle.md` §0–§9 + §R2 附录（先看 §7 的固定错误码，R2 已由 14 条扩到 21 条反例）；
3. `evidence/I-11-A/extract/commands_raw.json` → 命令的 argv/退出码/输出 sha256；
4. `evidence/I-11-A/extract/arithmetic_oracle.json` → A1–A7 的逐操作数定位结果；
5. `evidence/I-11-A/hypotheses.json` → 8 条命题全文；
6. `evidence/I-11-A/validation_report.json` → 正例通过 + 21/21 反例被拒 + 计数；
7. `evidence/I-11-A/extract/P1_xiaomi_content_probe.json` → 小米不可读的实测事实（P1-3）；
8. 本文件 §2 与 §5（含 R2 修订说明）。
