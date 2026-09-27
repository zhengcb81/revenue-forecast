# t1_review_flips.md — T1-\* 独立验收裁定块（附带件 · 供父按需落卡/登记）

T1 attempt 无 review.md；以下块供父 landing 批次**新建**各卡 `review.md`（追加形态）或登记入编排层记录。
出具：**独立审查员 M-T-REVIEW / N=1**，2026-09-23。详证 `../reviews/T1_rulings.md`。
通用未授予声明：本裁定只覆盖各卡自述范围（裁定落地形态核验/立卡/许可式写入）；不代签 TIER-2 专业方、
不授予晋升/生产执行/真实窗口开启。

## 接受块（accepted_scoped）— T1-13 / T1-14 / T1-16 / T1-17 / T1-18 / T1-19 / T1-21 / T1-23 / T1-24 / T1-25 / T1-26 / T1-27

```text
## 独立验收裁定（M-T-REVIEW · 2026-09-23）
- 结论：accepted_scoped —— 本卡裁定落地形态核验通过（命题表全 holds、边界条款未越、冻结件零触碰/许可式写入合规）。
- 逐卡 carried 与命题明细：execution_runs/M-T-REVIEW/a20260923-01/reviews/T1_rulings.md（对应行）。
- status_authority: { status: "accepted_scoped", reviewer_status: "independent acceptance (M-T-REVIEW N=1) 2026-09-23: accepted_scoped", carrier: "M-T-REVIEW/a20260923-01/reviews/T1_rulings.md + acceptance_rulings.md", implementer_signed: false }
— 独立审查员 M-T-REVIEW / N=1
```

## 接受块（accepted_with_conditions）— T1-1 / T1-2 / T1-5 / T1-6 / T1-7 / T1-8 / T1-15 / T1-20 / T1-22

```text
## 独立验收裁定（M-T-REVIEW · 2026-09-23）
- 结论：accepted_with_conditions（≡ accepted_scoped + carried）—— 本卡核验通过，携带下列在案余项。
- carried（逐卡）：T1-1/2 = OPEN-4/5/6 待 TIER-2 各当事方、候选件维持 UNRATIFIED/blocked；T1-5 = 交付面薄（无 decision.md/验证 JSON）、green 主张未复跑（产品侧引用面已抽点）；T1-6 = 预存漂移登记未修（按边界正确）；T1-7 = 四张被立卡待开工；T1-8 = START_HERE 114–115 行反写待 T1-12 ① 形态勘误追加、裁定「不推广代价」括注为假且低估缺陷（fabricated-green 风险）建议 owner 知悉；T1-15 = F-T1-15-01（P3）+ rerun_summary 字节数观察；T1-20 = 一处自记限度；T1-22 = 两张修卡待开工（含 T1-8 续查风险入验收面）。
- status_authority: { status: "accepted_with_conditions", reviewer_status: "independent acceptance (M-T-REVIEW N=1) 2026-09-23: accepted_with_conditions, carried items listed in reviews/T1_rulings.md", carrier: "M-T-REVIEW/a20260923-01/reviews/T1_rulings.md + acceptance_rulings.md", implementer_signed: false }
— 独立审查员 M-T-REVIEW / N=1
```

## 返修块（changes_required）— **T1-10**

```text
## 独立验收裁定（M-T-REVIEW · 2026-09-23）
- 结论：**changes_required** —— owner 授权的修复①（claim.basis 枚举校验）**未闭合**：校验已加但非全函数，
  畸形 basis 可使 J16 整个裁决机关失灵（本卡自记 P-3–P-6 FAIL 于完全性）——「护栏成为单点故障」。
- 接受部分（维持）：缺陷②（union_of_windows/sum_of_windows 计入 quick_check）已修且追加式 provenance 合规
  （旧值 2220 保留于 expected_superseded）。
- 返修要求：补全 claim.basis 校验覆盖面至全部入口（或立修卡并带畸形 basis 负例族 + 裁决机关不可被单例炸毁的负控），
  经独立验收后收口；建议同步纳入 T1-8 续查的 fabricated-green 负控。
- status_authority: { status: "changes_required", reviewer_status: "independent review (M-T-REVIEW N=1) 2026-09-23: changes_required — enum validation coverage incomplete (defect ① residual)", carrier: "M-T-REVIEW/a20260923-01/reviews/T1_rulings.md + acceptance_rulings.md", implementer_signed: false }
— 独立审查员 M-T-REVIEW / N=1
```

## 登记行（not_applicable_with_reason）— T1-3 / T1-4 / T1-9 / T1-11 / T1-12 / T1-28

```text
## 登记（M-T-REVIEW · 2026-09-23）：not_applicable_with_reason —— owner 裁决号无 attempt、无验收对象
（T1-3 暂不签待数据恢复 reviewer 复签 / T1-4 归档闭合 / T1-9 暂不授权 / T1-11 不授权 / T1-12 规则采纳
（本审查抽验中未见违反）/ T1-28 维持性登记）。不产生裁定、不计入 53 裁定数。
— 独立审查员 M-T-REVIEW / N=1
```
