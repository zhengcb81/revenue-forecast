# I-10-A independent_adaptation_review.md — 独立复核准备单（PENDING · 未签署）

> **本文件由实现者起草，不是复核意见，也不含任何签署。** 复核结论（accepted_scoped /
> changes_required / blocked / not_applicable_with_reason）只能由**独立行业/会计 reviewer**
> （N=1，未参与本卡实现）书写；实现者从不签署验收（`implementer_signed=false`、
> `implementer_never_signs_acceptance=true`）。保险复杂口径：本轮无保险口径，精算 reviewer
> not_applicable_with_reason（AD-9）。独立验证者另需核对原文与历史收入（卡文 Owner 行）。

## 1. 复核范围（本卡授予什么、不授予什么）

- 待签署资格 = **disclosure_adaptation**（逐公司/分部/模型，6 个 case），仅限各自口径与期间。
- **不授予**：accuracy（unproven）、来源链资格（I-07-B 实测 zero-RevenueSourceRecord，F3 未解）、
  任何正式公司预测放行、三情景预测（探针仅为 historical_mapping_probe）。
- 公式资格（M01-M31 A–C, accepted_scoped）为前置，不因本卡提升或外推。

## 2. 逐 case 待签清单（6 项）

| case | 公司/分部/模型 | D | E | probe | 待签结论（reviewer 填） |
|---|---|---|---|---|---|
| ZJ-MIN-M09 | 紫金 矿产品分部 / resource(M09) | 8 实例×3 字段 | L1 对账 −2,032,271 元（0.00155%，容差 0.05%）+ L2 范围桥 partially_explained | 24 调用，low/base/high 同值 | PENDING |
| ZJ-SMT-M09 | 紫金 冶炼产品分部 / resource(M09) | 3 实例×3 字段 | −95,486 元（0.00005%）+ L2 桥 | 9 调用 | PENDING |
| XM-PHONE-M03 | 小米 智能手機 / unit_sales(M03) | 1 实例×4 字段 | −21,463,000 元（0.0115%，容差 0.05%） | 3 调用 | PENDING |
| XM-EV-M03 | 小米 智能電動汽車及AI等創新業務 / unit_sales(M03) | 1 实例×4 字段（other=28 億元） | +17,635,978 元（0.0166%，容差 0.10%） | 3 调用 | PENDING |
| MS-PBP-M05 | MSFT PBP / subscription(M05) | missing 标记（席位/ARPU 未披露） | **STOP_DISCLOSURE_ADAPTATION** | 未运行 | PENDING |
| MS-IC-M06 | MSFT IC / usage_platform(M06) | missing 标记（用量/费率未披露） | **STOP_DISCLOSURE_ADAPTATION** | 未运行 | PENDING |

## 3. 请独立验证者执行的复核动作（review_and_handoff.md 固定 9 步 + oracle 攻击面）

1. 先读 I-10 原义务、卡文、binding.json、oracle.md（冻结件，sha `5CDD7331…`）、decision.md、handoff.json；
   再读本单与 accounting_decision.md。
2. **先看原始输出再看结论**：run_log.jsonl（全部 argv/rc/时刻）、command_runs/**/stdout.txt、
   probe_runs/**/probe_result.json（含 call-spy 计数）。
3. **原文核对**（独立验证者义务）：任抽 ≥5 条 quote 比对 `source_extracts/*`：
   - 紫金/微软引文 → CN-ZIJIN-2025.txt / US-MSFT-2026.txt（行号=抽取行）；
   - 小米引文 → HK-XIAOMI-2025_decoded.txt（解码法=PDF 自带 HYQiHei-FES cmap 反查，28,873 字形，
     0 unmapped；封面对股=20579/份=7871/幣=11813 可复验）——并可对照 source_extracts/page_renders/*.png
     （6 页渲染件，hash 在 HK_render_manifest.json）与 pdfminer 原始 (cid:NNNN) 留档。
4. **历史收入核对**（独立验证者义务）：按 oracle §1 手算任一条 量×价 与四个残差，比对
   historical_reconciliation.json；核对 L2 范围桥 gap 数额（紫金 p.326 分部收入三行）。
5. 复算 ≥1 个本卡专属判据（review_and_handoff 第4条）：如 ZJ-MIN 银：430,254,000 克 × 6.88 元/克
   = 2,960,147,520 元 vs 披露 2,958,010,000 元（+0.0723%，价格半 ulp 界 0.0727%）。
6. 变异/负例复核：probe_runs/*/red_conv、mut_swap_ids、mut_swap、mut_omit_optional 四臂结果；
   注意 **F-I10A-2**（mut_omit_optional 在 other=0 的 case 存活=产品缺陷证据）与 **F-I10A-3**
   （值互换=等价变异体，乘法交换律；ID 互换臂 4/4 击杀）。
7. 保留变化案例（review_and_handoff 第5条）：建议以 **ZJ-SMT 冶炼产锌**（20,327 元/吨 整数价）
   或 **XM-EV**（other_revenue≠0 的唯一 case）为保留复验对象——两者均未被用于修复迭代。
8. 检查 allowlist 外改动：changes.diff 的 anchors_identical 断言（产品零变更）；生产/审计旧证据未覆写。
9. 检查资格诚实：grep 本文档集不得出现"准确性通过/三情景预测/企业适配通过（未签）"类表述；
   三句声明逐字 + overall_three_market_pass=false + zero-RevenueSourceRecord 必须在 handoff/qualification 中在场。

## 4. 已知未验证/开放项（诚实清单）

- AD-8：金锭披露价与隐含价不互洽（presentation-level），待 reviewer 确认单价统计基准。
- L2 范围桥 gap（紫金两分部）仅量化未逐项分解（披露未给主要产品表外明细）→ partially_explained。
- 小米解码链依赖 PDF 自带 FES cmap 的字形共享假设（已用封面干净文本 8 对字形+语句交叉验证；建议复核者再抽验）。
- MSFT 两分部的 E 缺口=披露缺口本身；如外部独立披露（如季度补充材料）可得，可另卡补 E。
- F-I10A-1（工具缺陷）：pdftotext 构建缺 Adobe-GB1/CNS1 字符集（0 CJK）；pdfminer 输出原始 CID——均已留档。
- 命令簿记偏差披露：CMD-I10A-DECODE-HK 首次运行先于其 commands.json 登记（decision.md J-2）；
  两次 web_fetch 取 Adobe cmap-resources 参考表（UniCNS-UTF16-H 截断副本 + GBK-EUC-H 完整副本）用于
  诊断性否定检验（0/8 对不匹配，最终解码不依赖它们）——decision.md J-3。

## 5. 签署区（留白 — 由独立 reviewer 书写；本文件创建时为空）

- reviewer 身份（N=1，未参与实现）：____________________
- 结论（accepted_scoped / changes_required / blocked / not_applicable_with_reason）：____________________
- 授予范围与未授予清单：____________________
- 保留复验案例与其预期：____________________
- 日期：____________________

（implementer_signed=false · implementer_never_signs_acceptance=true · 本文件起草：I-10-A 实现者 a20260923-01）
