# I-10-A decision.md — attempt a20260923-01（九步执行法 → review_pending）

实现者记录，不自签。所有判据运行的原始 rc 见 `evidence/I-10-A/run_log.jsonl` 与
`command_runs/**`（argv.json / stdout.txt / *result.json）。产品写入=0、CW 写入=0、git=0、
network=0（命令面）。判据运行全部发生在 oracle.md 冻结（sha `5CDD7331…`，2026-09-23T23:51:00 本地）
之后——creation-time 证据在 run_log.jsonl 的 ORACLE-FREEZE 记录与其后各 run 的 started_at。

## 0. 退出诚实块（卡文停止条款逐字 + 逐条实测评估）

卡文停止条款原文：

> - 实际采用清单不明确或来源不可读取→STOP_SELECTION_OR_EVIDENCE。
> - 任一实际采用模型公式资格未通过→STOP_FORMULA_DEPENDENCY。
> - 单位/会计/期初锚点/收入历史桥未解决→STOP_DISCLOSURE_ADAPTATION；允许其他已合格分部保留局部结果，但不放行整个公司正式预测。
> - 只有历史映射probe却声称真实三情景/准确性通过→STOP_QUALIFICATION_SCOPE。

实测评估：

- **STOP_SELECTION_OR_EVIDENCE：不触发**。采用清单已冻结（selected_model_manifest.json，6 case /
  26 not_selected 登记 / 31 model_id 全覆盖）；三份来源均**可读取**（绑定期重哈希 == 冻结 manifest；
  紫金/微软为文本可抽取原件；小米原件文本层无 ToUnicode，但已用原件自带 HYQiHei-FES cmap
  反查解码全文 272,511 字形 0 unmapped，页码原生、引文可复核——「可读取」成立）。
- **STOP_FORMULA_DEPENDENCY：不触发**。采用的 4 个模型（M09 resource / M03 unit_sales /
  M05 subscription / M06 usage_platform）公式资格均 accepted_scoped（M01–M31 31/31 面，
  deps/m31_qualification_sweep.json 实测 31/31 formula=accepted_scoped）。
- **STOP_DISCLOSURE_ADAPTATION：部分触发（US-MSFT-2026）**。MSFT 两分部的收入历史桥未解决
  （席位/ARPU、用量/费率均未按所需粒度披露；missing 保留、不补零、不倒推）⇒ 这两分部 E 未执行、
  probe 未执行。**按卡文：允许其他已合格分部保留局部结果（ZJ-MIN/ZJ-SMT/XM-PHONE/XM-EV 的 D/E/
  probe 成果保留），但不放行整个公司正式预测**——三家公司均未放行（本卡本就不授予预测放行）。
- **STOP_QUALIFICATION_SCOPE：不触发**。全部探针产物标 `historical_mapping_probe`、
  `NOT_a_three_scenario_forecast`、`NOT_accuracy_evidence`；验证器 R5 对全证据面扫禁语
  （「授予准确性资格/通过三情景/企业适配已通过/适配资格已签署/accuracy granted」）命中 0。

卡文验收语句执行结果（逐字对照）：「每个实际采用的公司/分部/模型完成M卡D/E专业适配与独立签署，
证据可复核，口径范围明确；未使用模型只标not_selected。该卡不授予准确性，不要求I-11或I-07-E产物。」
→ 6 个采用 case 的 M卡 D/E 产物齐备且口径范围明确（含 2 个 STOP 记录的 MSFT case：D 完成 missing 标记，
E 依停止条款记录未解决）；**独立签署未取得**（review_pending，复核另行进行）；未使用模型全部
not_selected+理由；accuracy=unproven；未消费任何 I-11/I-07-E 产物。

## 1. 逐 case 结果表（引用真实证据：文件/行号/sha）

| case | D（M卡D 逐字段） | E（M卡E 历史段对账） | 探针（M卡E/卡文4） | 结论 |
|---|---|---|---|---|
| ZJ-MIN-M09（紫金 矿产品分部 / M09 resource） | 8 实例 × 3 字段，引文=CN-ZIJIN-2025.txt p.44 L3958-4049（销售详情表：单价（不含税）/销售数量/金额（万元））、p.45 L4137-4192（分产品收入）；单位换算 ×1e3/×1e4（AD-5） | 复建 Σ=131,491,532,271 元 vs 同口径披露 131,489,500,000 元 ⇒ 残差 **−2,032,271 元（−0.00155%）**，容差 ±0.05%（冻结）**内**；五类分解齐（价=全额舍入互洽差，AD-8）；L2 范围桥 gap +6,782,172,956 元 partially_explained | 24 次 calculate_registered_model 实测（=8 实例×3 情景），low/base/high 同值且=手算值（probe_runs/ZJ-MIN-M09/normal/probe_result.json） | D/E/探针完成，**签署 PENDING** |
| ZJ-SMT-M09（紫金 冶炼产品分部 / M09） | 3 实例 × 3 字段，p.44 L4056-4090 / p.45 L4193-4213 | 复建 183,988,605,486 vs 183,988,510,000 ⇒ **−95,486 元（−0.00005%）**；L2 gap +5,695,369,295 partially_explained | 9 次实测，同值=手算 | 同上 |
| XM-PHONE-M03（小米 智能手機 / M03 unit_sales） | 1 实例 × 4 字段（units/unit_revenue/timing_factor/other_revenue），引文=decoded p.21 L1367-1437（收入/出貨量/ASP 叙述）+ p.337 L17789-17790（附註5 186,439,777 千元） | 复建 186,461,240,000 vs 186,439,777,000 ⇒ **−21,463,000 元（−0.0115%）**，容差 ±0.05% 内；量项舍入界 ±56,435,000 元、价项 ±8,260,000 元已量化 | 3 次实测，同值=手算 | 同上 |
| XM-EV-M03（小米 智能電動汽車及AI等創新業務分部 / M03） | 1 实例 × 4 字段（other_revenue=28 億元→2.8e9 元，p.22 L1618-1636 其他相關業務） | 复建 106,051,877,022 vs 106,069,513,000 ⇒ **+17,635,978 元（+0.0166%）**，容差 ±0.10% 内；other_revenue 億元舍入界 ±50,000,000 元 | 3 次实测，同值=手算 | 同上 |
| MS-PBP-M05（MSFT PBP / M05 subscription） | 4 字段全 missing 标记（zero_filled=false），missing 证据=p.35 L734（指标删除）、p.36 L745-756（仅增长率指标）、p.84 L4790 起（仅美元额） | **STOP_DISCLOSURE_ADAPTATION**（收入历史桥未解决；局部 D 结果保留；不放行公司正式预测） | 未运行（oracle §3 冻结预期=not_run + 理由） | D 完成·E 停止·**签署 PENDING** |
| MS-IC-M06（MSFT IC / M06 usage_platform） | 3 字段全 missing 标记，证据=p.36 L755-756（Azure 仅增长率）、L232（分部构成）、p.83 L4057（RPO 存量无 rollforward） | **STOP_DISCLOSURE_ADAPTATION**（同上） | 未运行 | 同上 |

not_selected 面：26 个未采用 model_id 全部登记理由（含 M23 保险=无保险分部 ⇒
actuarial_reviewer not_applicable_with_reason）；机制混合分部（ZJ-其他 / 小米互聯網服務 /
MSFT-MPC）记 AD-7 special_review 待独立 reviewer 裁定，**不宣称适配通过**。

## 2. 判据链（红→绿→变异，逐 case 非空转）

### 2.1 接线探针链（4 case × 4 臂，rc 按本批冻结码表）

| 臂 | ZJ-MIN | ZJ-SMT | XM-PHONE | XM-EV | 判定 |
|---|---|---|---|---|---|
| red_conv（换算错接 ×10） | rc2 | rc2 | rc2 | rc2 | 4/4 正确拒绝（错接被手算期望检出） |
| normal（正臂） | **rc0** | **rc0** | **rc0** | **rc0** | 4/4 通过：输出=冻结手算值（1e-9 内）、low/base/high 同值、spy 计数=24/9/3/3（冻结期望逐一相符） |
| mut_swap_ids（参数 ID 互换→维度错配） | rc2 | rc2 | rc2 | rc2 | 4/4 击杀（产品维度检查先拒，注册调用 0） |
| mut_swap（量价**值**互换） | rc3 | rc3 | rc3 | rc3 | **等价变异体存活**（F-I10A-3：乘法交换律 a×b=b×a，值互换不可区分） |
| mut_omit_optional（省缺 other_revenue） | rc3 | rc3 | rc3 | **rc2** | 3 存活/1 击杀 ⇒ 存活臂=**产品缺陷实证**（F-I10A-2）：forecast 入口 `_optional_series(default=0.0)` 静默补 0；XM-EV 被检出仅因 0≠2.8e9 的输出差 |

### 2.2 验证器链（R1-R12，5 规则族）

| 族 | RED（前适应骨架夹具） | GREEN（真实产物） | MUT（单缺陷变异体） |
|---|---|---|---|
| F-A R1/R7/R8/R10 | rc2 ✓ 检出 | rc0 ✓ | rc2 ✓ 击杀（签署位篡改） |
| F-B R2/R3/R12 | rc2 ✓ 检出 | 见下红→绿 | rc2 ✓ 击杀（换算公式破坏；首臂曾存活=验证器 R12 缺口，补实现后击杀） |
| F-C R4 | rc2 ✓ 检出 | rc0 ✓ | rc2 ✓ 击杀（容差篡改+类别删除） |
| F-D R5/R6 | rc2 ✓ 检出 | rc0 ✓ | rc2 ✓ 击杀（标签破坏+计数篡改） |
| F-E R9/R11 | rc2 ✓ 检出 | rc0 ✓ | rc2 ✓ 击杀（清单引用破坏） |

红→绿轨迹（真实产物面，全部留档不涂改）：
1. GREEN 首跑 rc3 = 红：14 项（R2 缺 optional missing 登记 ×2、R3 引文行域转写错 ×5、
   R9 清单路径文本错 ×6、R12 由此暴露的 XM-EV raw 形态错 ×1）。
2. 修复=**转写/簿记更正**（行域补正、missing 清单补 optional、清单路径改正、raw 改为原量形态
   28 億元×1e8）——不改任何数值结论、不改容差、不改冻结件。
3. GREEN-2 rc0（R12 补实现后 GREEN-3 曾再红 1 项=同一 XM-EV raw 形态，更正后）GREEN-4 rc0 终态。
4. 变异臂最终 5/5 击杀（MUT3 系列，与终态产物同源）。

## 3. Findings（产品缺陷=记账+路由，修非本卡面）

- **F-I10A-2（产品缺陷，high）**：`scripts/forecast/calc.py _optional_series(..., default=0.0)` +
  `segments.py:101-110` 在 **forecast 入口层**对无显式 default 的 optional driver 仍**静默补 0**——
  I-10-B 的「省缺即抛」修复只覆盖 `calculate_registered_model`（注册层），上层未覆盖。
  实证：mut_omit_optional 臂 3/4 存活（ZJ-MIN/ZJ-SMT/XM-PHONE 的 other_revenue 被静默填 0 而不报错）。
  **路由**：model_registry/forecast 入口契约（I-10-B 修复面扩展；其 E-1..E-7 勘误同族），交 owner 立卡。
- **F-I10A-3（等价变异体，info）**：M09/M03 量×价乘法下「值互换」变异体等价（交换律），4/4 存活
  为**预期等价性**而非检出缺口；已用 mut_swap_ids 臂补杀维度错配路径（4/4）。如实登记。
- **F-I10A-1（工具缺陷，medium）**：pdftotext（Git mingw64 poppler）缺 Adobe-GB1/CNS1 字符集，
  对两份中文 PDF 抽出 **0 个 CJK**；pdfminer 对无 ToUnicode 字体只输出 `(cid:NNNN)`；PyMuPDF 常规
  抽取把 glyph id 直接当码位（全文乱码）。证据留存 superseded_pdftotext/ 与解码 manifest。
  解决：以原件自带 HYQiHei-FES cmap 反查（28,873 字形）解码，封面对照 8 组字形+语句交叉验证。
- **F-I10A-4（口径发现，info）**：紫金金锭披露单价 810.17 元/克 与「金额÷销量」隐含价 810.1638
  非四舍五入关系（AD-8 presentation flag），残差全额可由此解释（−302,580 元 = −qty×价差），
  请 reviewer 确认单价统计基准。

## 4. Judgment calls（决策 J）

- **J-1 采用清单冻结口径**：以「披露可支持非循环 E 段复建」为纳入准则（M09/M03/M05/M06 六 case）；
  混合机制分部不硬塞单模型（AD-7）。拒绝的替代：按分部全覆盖硬映射（会制造不可识别参数）。
- **J-2 命令簿记偏差（披露）**：`CMD-I10A-DECODE-HK` 首次运行先于其 commands.json 登记（工具迭代中
  运行）；argv 与登记一致，运行证据全留 command_runs/ 与 run_log.jsonl。同 I-07-B J7 披露纪律。
- **J-3 网络面披露**：诊断期经 web_fetch 取回 Adobe cmap-resources 两张参考表
  （UniCNS-UTF16-H 截断副本、GBK-EUC-H 完整副本，已存 source_extracts/ref/ 并哈希），
  用作**否定检验**（GB1 值域与原件字形 0/8 对不匹配 ⇒ 排除该路径）；**最终解码不依赖任何外部表**
  （原件自带 cmap 自洽）。binding 的 network=disabled 面无命令网络调用；本项为 harness 工具面，
  如实记账不隐匿。
- **J-4 小米引文可核性路径**：文本层解码 + 6 页 PNG 渲染（page_renders/，哈希在册）双轨；
  复核者可任选其一核对原文（解码法可从原件字节复算）。
- **J-5 MSFT 不造数**：缺披露即 missing，不用 RPO/增长率倒推任何绝对量（R4b）；两分部 E 记
  STOP_DISCLOSURE_ADAPTATION 而非补数通过。
- **J-6 等价变异体处置**：mut_swap 保留为等价变异体登记（F-I10A-3），另增 mut_swap_ids 臂满足
  oracle §3 的维度错配预期；不删失败臂、不改 oracle。

## 5. 前后哈希（实测，after/hash_table_before_after.json）

- 产品锚（5 件）：before == after（anchors_identical=true，anchors_changed=[]）⇒ **产品零变更**。
- 三份来源 raw + sidecar：before == after（sources_identical=true）⇒ 未覆写任何原件。
- 冻结计划/依赖输入（12 件）：before == after（plan_inputs_identical=true）⇒ 未覆写旧审计证据。
- iso 产品副本（8 件）：before == after（iso_copies_identical=true）。
- 写入面=仅 `<attempt>/**`（changes.diff 列全部隔离面文件及 sha）。

## 6. 未验证/交复核清单（诚实）

1. 小米解码的字形共享假设（已 8 组对照+语句交叉验证，但全表未逐字形独立验证）。
2. AD-8 单价统计基准未定（presentation 不互洽）。
3. L2 范围桥 gap 未逐项分解（披露未提供主要产品表外明细）——partially_explained 是上限结论。
4. MSFT E 缺口是否可由外部独立披露（季度补充/指引）弥补——未查证（本卡信息面=三份原件）。
5. ZJ-MIN/ZJ-SMT 的 2024 对照列未纳入复建（本卡 E 面=单个已结束期间 FY2025；双期复建留 I-12 口径）。
6. mut_swap 等价性论证（交换律）未含 timing_factor≠1 情形（本轮 timing=1；若非 1 时值互换仍等价
   仅当 other 项不变——记为已知边界）。
7. 生产 model_registry.py（62f864b9…）为 I-10-B 修复后的晋级版——晋级本身是独立 owner 决策
   （I-10-B handoff 载明不授权），本卡按当前字节适配并锚定，未参与该决策。

## F-REV-I10A erratum (landing)

carrier-landing 簿记 pass（父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单之 delegated
subagent）在独立行业/会计复核裁定 **`accepted_scoped`**（carrier = `reviewer_report.md`，sha256
`6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb`，35164 B / 300 行，`.sha256`
侧车读回相等，verdict 在 L15）之后、三件落定写入**之前**追加本节。append-only：上文原文一字未改，
下列更正与原文并存留痕（原值留痕风格）。五条全部为簿记/文档类、**non-blocking**（carrier §6
F-REV-I10A-1..5，L206–L212）；不改变任何数值结论、容差、冻结件与红→绿轨迹。

- **F-REV-I10A-1（LOW·簿记｜两枚 63 位 sha pin，literal-unverifiable）**：
  `handoff.json current_source_hashes` 与 `changes.diff` 内两枚 pin 各缺 1 个十六进制字符、按字面
  不可验证（复核以删除位比对确认：`disclosure_mapping.json` 缺 index23 的 `f`；
  `model_DE_evidence_manifest.json` 缺 index15 的 `e`）。**真实文件完好**：两件实测 sha 均为 64 位，
  且 `model_DE_evidence_manifest.aggregate_files` 内部的 64 位 pin 与实测一致（本 pass 落定时只读
  重哈希独立复算 == 复核实测）。**更正 pin 值在此登记（取自复核实测，本 pass 独立复算一致）；
  原件（evidence 两件、handoff.current_source_hashes 原值、changes.diff）一律不回写**：
  - `evidence/I-10-A/disclosure_mapping.json` = `7e03ea748cb99d74038daeef3b529b824f1300c17ee841aaf8fc19b9f1501e0b`（64 位，corrected；现挂 63 位 pin `7e03ea748cb99d74038daee3b529b824f1300c17ee841aaf8fc19b9f1501e0b` 保留原样留痕）
  - `evidence/I-10-A/model_DE_evidence_manifest.json` = `c3e489c580cc7e9eae18efa5199456a013a04099ed07d3d03bbb4ceb5726ac95`（64 位，corrected；现挂 63 位 pin `c3e489c580cc7e9ae18efa5199456a013a04099ed07d3d03bbb4ceb5726ac95` 保留原样留痕）
- **F-REV-I10A-2（LOW·文档｜GREEN 首跑 14 项分类记述差 1 项）**：§2.2 红→绿轨迹第 1 条把 GREEN
  首跑 14 项记作「R2 缺 optional missing 登记 ×2、R3 引文行域转写错 **×5**、R9 清单路径文本错 ×6、
  **R12 由此暴露的 XM-EV raw 形态错 ×1**」；原始
  `command_runs/CMD-I10A-VALIDATE-GREEN/validate_result.json` 实为 **R2×2 + R3×6 + R9×6（首跑无
  R12 项）**，**R12 首次命中发生在 GREEN-3**（1 项，XM-EV raw 形态）。**总数 14 正确、红→绿轨迹
  与 rc 序列 3/0/3/0 不受影响**；原分类文字留痕，权威分类以本 erratum 为准。
- **F-REV-I10A-3（LOW·冻结件转写，−20,000）**：`evidence/I-10-A/oracle_expected.json` 中 ZJ-MIN
  `aggregate_tolerance_abs = 65,724,750`，而同文件 `0.0005 × 131,489,500,000 = 65,744,750`
  （差 **−20,000** / −0.03%）；其余 3 case 该字段自洽。该字段**在 harness 中只定义、不被任何门使用**
  （门全部用 `aggregate_tolerance_rel`），残差 −2,032,271 距任一值均有 30 余倍余量 ⇒ **不影响任何
  判定**；按冻结纪律**不回改**（oracle/oracle_expected 0 字节），登记为披露性转写差错。
- **F-REV-I10A-4（INFO·证据可枚举性）**：§3 F-I10A-1 与 §6.1 称「封面对照 **8 组字形**」，证据面
  只枚举到 **4 组**（`harness/decode_hk_text.py:159`：股=20579 / 份=7871 / 幣=11813 / 港=15857；
  `commands.json` 另记 年=11830）；其余 4 组未在案 ⇒ 「8 组」之说**部分可核**。**0-unmapped 与
  方法可复现性已硬证**（解码重跑逐字节相同、mapped 272,511 / unmapped 0），全表字形共享假设仍为
  开放项（见 unverified #2）。
- **F-REV-I10A-5（LOW·自指簿记）**：`changes.diff` 内 70 枚 pin 全量复算 = **68 中、2 不中**——
  `run_log.jsonl`（`96657544…` vs 实际/终态 `16e466c4…`）与 `README.md`（`f3551454…` vs 实际
  `c1c71491…`）。两者均为 changes.diff 生成**之后**又追加/更新的活文件（run_log 由命令自身追加、
  README 是 live working document），属**自指性时序、非篡改**；**handoff 的 run_log pin
  （`16e466c4…`）是正确终态**。隔离面清单完整性结论维持；后续批次把这两项标 `excluded (live file)`。

处置去向：五条在 `handoff.json bookkeeping.findings_disposition` 与
`evidence/I-10-A/qualification.json mirrors.f_rev_mirrors` 各留一面镜像；本节为唯一更正载体。
