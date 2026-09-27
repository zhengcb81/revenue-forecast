# T1-\* 独立子审查 — 独立审查员 M-T-REVIEW / N=1

**主规格**：`OWNER_DECISIONS.md` §13 T1 表行（207–234 行）+ 各卡 `decision.md` 逐字引用的裁定原文。
**方法**：每卡抽验 —— (a) 决定/handoff 时序；(b) hash 抽点（主验证 JSON + handoff + decision 对盘上值 + 卡内 pin 族）；
(c) 规格符合（裁定原文子句 3–5 条 vs `decision.md` 命题表 + 边界条款）；(d) 行为抽点（验证 JSON 的
propositions/overall 与自述一致 + golden-hash 族）。**未执行任何 harness**。
T1 卡普遍以「核验裁定落地形态」为性质、`不代签/不回改冻结件` 为边界；`status=planned/review_pending` 者
**本裁定即其缺失的独立验收**。

| # | attempt | 抽验要点 | 裁定 |
|---|---|---|---|
| T1-1 | T1-1-T1-2/a20260920-01 | 七命题 holds（裁定文本含请求身份=决定项；Round 41 落地候选 UNRATIFIED 未膨胀为已实现；`handoff.status=blocked` 界线完好）；`t1_1_t1_2_verification.json` `f93a1832…`；append-only 证明 round62 `cfa0fb92…`；卡自记两次判据错误并修正 | **accepted_with_conditions** |
| T1-2 | 同上 | OPEN-1 落地候选形态核验（CW migration 纪律复用）；OPEN-4/5/6 仍待他方签 —— 按裁定属 TIER-2，非本卡欠账 | **accepted_with_conditions** |
| T1-5 | T1-5/a20260920-01 | **交付面薄**：仅 `handoff.json`（无 decision.md、无验证 JSON、pin 族=4）；声明「regression committed and green」在产品侧抽点到引用面（`tests/test_industry_end_to_end.py:19` 导入 `test_model_extensions`）但 commit-green 本审查未复跑 | **accepted_with_conditions**（carried：验证面薄、green 主张未复跑） |
| T1-6 | T1-6/a20260920-01 | 选 (c) 已落地：新跨年用例（`opening_arr/closing_arr` 可达值）经冻结 runner 两阶段验证 `t16_verification.json` `2cd7efa9…` OVERALL=PASS 7/7，既有用例 verdict 不变、消息前缀差异如实登记；landing 报告 `4533fc59…` 证只加不改 | **accepted_with_conditions**（carried：§8 预存漂移登记未修——按边界正确） |
| T1-7 | T1-7/a20260920-01 | 四前提实证成立后出**立卡登记表**（不代建四卡、不编辑冻结件）；`t17_ruling_landing.json` `a6353411…`；append-only 证明 round60/61 在案 | **accepted_with_conditions**（carried：四张被立卡待各自 owner 开工） |
| T1-8 | a20260920-01/02/03（三次互补 attempt） | ①/④：精确类型名判据 vs isinstance 的分叉实证（八代 runner 按 sha256 指名）；③：「统一 rc 归类」被证为对产品 no-op 且若照办会引入「篡改从判负降级为无裁决」缺陷 —— **拒绝照抄裁定的前提错误**，处置正确；续查：裁定所引「不推广代价」括注为假且**低估**缺陷（毒化 11 声明仍 rc=0/11-11 PASS_rejected = fabricated green），如实上报；`t8_pre*` 三件 + append-only 证明 round58/59/60 在案；START_HERE 第 114–115 行反写待 T1-12 ① 形态勘误（本卡按边界不执行） | **accepted_with_conditions**（carried：START_HERE 勘误追加待编排层；裁定括注更正建议待 owner 知悉） |
| T1-10 | T1-10/a20260920-01 | 缺陷② 早已修 + 追加式 provenance 已在形态上（旧值 2220 保留于 `expected_superseded`）✅；**缺陷① 枚举校验已加但非全函数**：畸形 `basis` 可让 J16 整个裁决机关失灵（P-3–P-6 FAIL 于完全性），卡自记「未闭合的残留」 | **`changes_required`** —— owner 授权的修复① 未闭合：须补全覆盖（或立修卡并经独立验收）后方可收口；② 及 provenance 部分维持接受 |
| T1-13 | T1-13/a20260920-01 | 出处列三格修复 + 前像 hash + diff 齐（`t13_line80_verification.json` `5f97d54f…`）；只动出处列、数值/reviewer 字节未动 ✅；卡内自纠一次判据错误并如实登记 | **accepted_scoped** |
| T1-14 | T1-14/a20260920-01 | `pdftotext.exe` 交叉核对路径 + sha256 `252d2b34…` 入 binding、未为取文升级 Git（P-4 证据含限度声明）；`P1_vs_prior_offset.json` 择优不回改 oracle 正文 ✅；O-3 已满足被实证 | **accepted_scoped** |
| T1-15 | T1-15/a20260920-01 | M08 三步闭环核验：①读法 C 从源码独立读出 ✅ ②索引四处更正保留原文+前像 hash ✅ ③同 `code_root 9ec65295…` 复跑 `[50.0]`/11/11 转录 review.md ✅；八命题 holds；F-T1-15-01（P3）+ rerun_summary 字节数 4185 vs 4062 观察如实登记 | **accepted_with_conditions**（carried：F-T1-15-01 P3、字节数观察） |
| T1-16 | T1-16/a20260920-01 | 选 A（保持 fail-closed）前提实证：base=−5 实测被拒、两模型对照（S-1 用两模型而非只读源码 —— 判据正确）；S-5：冻结件零触碰、门仍登记 owner 保留（不回写 open_questions —— T1-21 口径正确）；自纠 harness 缺陷未误判产品缺陷 | **accepted_scoped** |
| T1-17 | T1-17/a20260920-01 | `lock_budget_for(x)=min(x,60)` 双载体落点齐、`worker-pause` 留锁内；门腿 9/9 子检查（owner_gates 登记 / blocks_signoff=false / 实现者未自裁）；自纠路径深度错位 | **accepted_scoped** |
| T1-18 | T1-18/a20260920-01 | 两半同验：冻结 `5s`/`5s` 落于推导带 `[1,86]s`（双独立界 L1/L2 实测）✅；**限度完好**——真实 30/60/120 仍 blocked、8/8 子检查、无「签字足以开窗」文本；未触碰 I-14-B | **accepted_scoped** |
| T1-19 | T1-19/a20260920-01 | rc 码表冻结入 `START_HERE.md`（90–115 行）：四值齐（0/1/2/3）、自描述 `exit_code_legend` + 「历史 rc 一律不动」、已知历史偏差两类登记；许可式写入、未回改历史 | **accepted_scoped** |
| T1-20 | T1-20/a20260920-01 | 书面追认三半逐半可验（I-00-B 只绑方案 / 物化由各 attempt 完成 / 各记来源 hash 且快照==生产逐字节）；四命题 holds；追认载于编排层记录而非被追认 attempt（正确载体选择）；一处限度如实登记 | **accepted_with_conditions**（carried：一处自记限度） |
| T1-21 | T1-21/a20260920-01 | 口径两形态：追加式 provenance（何时/为何/新 hash）在场 ✅、「从未编辑」回改不在场 ✅、事件被升级未被自裁 ✅；未修改任何被裁定对象 | **accepted_scoped** |
| T1-22 | T1-22/a20260920-01 | 两缺陷刻画实证（`:335` 静默补 0 = 31 槽位/24 模型精确复现——且卡自纠一次「差点上报的假缺陷」计数口径）；「立卡≠修复」边界守住（产品改动 0）；两张修卡草案已固化 | **accepted_with_conditions**（carried：两张修卡待开工 + T1-8 续查的 fabricated-green 风险应在修卡验收面内） |
| T1-23 | T1-23-T1-25/a20260920-01 | 勘误落地核验（纯文字、数值结论未动）；`t1_23_t1_25_verification.json` `4231bf05…` 八命题 holds、六负控全转红 | **accepted_scoped** |
| T1-24 | T1-24/a20260920-01 | 三条腿核验（M29–M31 逐字节重生成 ✅ / 生成器 hash 运行前落盘 ✅ / oracle.json mtime<stdout（记录态）✅）、被拒强主张不在场 ✅；按裁定未重跑；自纠一处判据错误 | **accepted_scoped**（注：第三腿的现盘复验已被 F-MT-02 灭失，以记录态为凭——不改本裁定） |
| T1-25 | 同 T1-23 attempt | R-1/R-2 清除实证（三卡 live `OQ-04.title` 与 `write_binding.py` 常量）、R-3/R-4 源上已修；`implementer_signed=false` 齐；「M31 正式关闭仍归其 reviewer」边界正确 | **accepted_scoped** |
| T1-26 | T1-26/a20260920-01 | 半授权形态两腿齐：许可腿（晋升流程启动、无产物）+ 保留腿（D1/D2/D3 三签仍属 TIER-2、signers 三键齐、禁拷 `iso/slo_probe_patched.py` 入 `RF/tools/`）；六命题含防「总批准膨胀为所有结论」的负控 | **accepted_scoped** |
| T1-27 | T1-27/a20260920-01 | 追加块存储缓解三分半全核（H-1 提交频率=已践行、H-2 提交后核对 `[INFO] Restored changes` 行、H-3 根因=工作树-only 追加块）；无编辑、纪律入册 | **accepted_scoped** |

## owner 裁决号登记（无 attempt —— `not_applicable_with_reason`，不裁定）

| # | 依据 | 登记 |
|---|---|---|
| T1-3 | OWNER_DECISIONS §13：暂不签、产品实施 blocked | 无 attempt 属实；改写后须数据恢复 reviewer **复签**方可生产 prune —— 独立验收对象尚未产生 |
| T1-4 | §13：提交 `5db4734a` 已落地、本批归档闭合 | 归档闭合项，无需 attempt；T1-5 补回归另计 |
| T1-9 | §13：暂不授权、维持 blocked | 被拒授权项，无验收对象 |
| T1-11 | §13：不授权再重冻 | 被拒授权项，无验收对象 |
| T1-12 | §13：采纳 ① 形态统一规则 | 规则采纳项（编排层直接落地）；其形态已被各卡引用遵守，本审查抽验中未见违反 |
| T1-28 | §13：十~十二节既有裁定全部维持 | 维持性登记，本批不重开 |

— 独立审查员 M-T-REVIEW / N=1，2026-09-23
