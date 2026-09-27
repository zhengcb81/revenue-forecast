# REGISTRY-CLOSURE oracle — 全清单冻结（frozen BEFORE any closure action）

- attempt：`execution_runs\REGISTRY-CLOSURE\a20260923-01`
- 冻结时点：2026-09-23（本文件写毕即钉 sha256 入 `oracle.sha256` / `binding.json`；冻结后本文件不改——新增事实一律入 `decision.md` 与 `evidence\`）
- 冻结对象 = **处置项全清单 + 每项闭合判据**（什么证据算闭）；**处置判定（class/结论）不在本文件**，在 `decision.md`（避免 oracle 与判定互相污染）。
- 语料来源（全部只读）：`REMEDIATION_REGISTER.md`（1570 行态）、`AUDIT-GOAL\a20260923-01\audit_report.md` + `evidence\report_SA-REM.md` + `evidence\report_SA-DEFECT.md`、I-14-D r5/r6/r7 复审载荷、I-14-F-R1 `decision.md`、I-14-I `handoff.json`、I-10-B `handoff.json`、M14 `oracle.md`、`OWNER_DECISIONS.md`、`company-wiki\tests\contract\test_short_basetemp_convention.py`。
- 项目纪律：修复走九步协议（隔离副本+oracle 先冻结+独立复审+生产零合并）；封存载体不回改（勘误走登记册/外部 superseded 注记）；登记册只许追加式单节处置汇总、不改历史行。

---

## A 组 — AUDIT-GOAL 判「10 行零处置」（其 §3.3 原文清单：REM-05/06/07/08（修卡"B2"未跑，register:100）、16/17（"B4"未跑，:102）、25（owner 选择未落，:51）、30（F-5 不在 ERR-I14FR1 勘误集内，:56）、35（措辞修正无下文，:62）、67①③（:263 明写"未处理"））

行文本逐字（REMEDIATION_REGISTER.md）：

| # | 行 | 逐字行文本（问题+修法+状态列节录） | 闭合判据（本卡接受的闭法） |
|---|---|---|---|
| A1 | **REM-05**（I-14-D F-REV-D-02，MEDIUM，register:16） | 「`_VALUE` 在两棵树中都是**死代码** ⇒ 头条 `_BARE_VALUE` 收窄**无运行时效果**；真正生效的是 scanner-loop hunk。晋升隐患：未来"清理"删掉死常量会误以为修复仍在」修法「删除死代码或加注释说明其非承重地位」状态「待修」 | (a) 最新世代树内死代码删除/注释的可核修面（changes.diff+判据证据）；或 (b) B2a 工作卡规格；或 (e) 证明后续世代已删/已注 |
| A2 | **REM-06**（F-REV-D-03，MEDIUM，:17） | 「收窄后**暴露既有 atom 表缺口**：`token=<A> token2=<B>` 中 `<B>` 现在明文留下；`token2/secret2/password2/api_key2` 不是凭据键（而 `refresh_token/access_token/token_2` 是）」修法「补 rule-table 行 + 扩展凭据键集合」状态「待修」 | (b) 工作卡规格（键集扩展+双仪器行+过度脱敏定价，行为面）；或 (e) 后续世代已扩键的证据 |
| A3 | **REM-07**（F-REV-D-04，LOW，:18） | 「无值 `Authorization:` + 换行仍吞掉下一个 token（`Authorization:\ndoc=17` → `doc=17` 丢失、出现伪 `<redacted>`）；退出条款在 auth 路径**部分**满足」修法「作为 C13 子案例继续跟踪并修」状态「待修」 | (b) 挂入既有 I-18-A（C13）卡轨道即算路由闭（须指出轨道证据）；或真修证据 |
| A4 | **REM-08**（F-REV-D-05，LOW，:19） | 「`binding.json` 谎称 `harness/tests/conftest.py` 有"一行改树指向"；实际与 I-14-C 逐字节相同（`783b1774…`）」修法「更正 `binding.json` 表述」状态「待修」 | (a) 勘误式闭（封存载体不回改 → 登记册/外部 superseded 注记给出正确表述）；或载体内已有更正 |
| A5 | **REM-16**（I-10-B F-R1，P3，:32） | 「`command_runs/` 有 7 个子目录而 `evidence_paths` 只列 6（`r2-verify-before/` 未列）」修法「补登记（结论未缺）」状态「待修」 | (a) 补登记（7 目录清单落 evidence + 处置行）即闭 |
| A6 | **REM-17**（I-10-B F-R2/OQ-1，P3，:33） | 「MUT-3（dimension 闸门）是**等价变异体**，注册表层不可观察；未独立枚举 31 个模型的 dimension 声明」修法「补"角色表名字 × 不合格 dimension"声明级负例」状态「待修」 | (b) B4a 工作卡规格（声明级负例测试）；或已有补测证据 |
| A7 | **REM-25**（I-14-F R-1，MEDIUM，:51） | 「`GENERATION_RESERVE = 124` 是 **child** 节点的最长后缀；**logon 节点的实为 150**…docstring 算术自相矛盾（31+13+79=123≠124；child 实为 125）」状态「待修（**需 owner 选**：reserve 150 ⇒ 阈值 60，或保留 86 但记录真实数字）」 | (c) owner 选择落案 + 应用证据；（注意：OWNER_DECISIONS §16 E-1 与 I-14-F-R1 可能已构成此闭——须核） |
| A8 | **REM-30**（I-14-F F-5，LOW，:56） | 「单测注释误述 4/7 用例长度（实为 174,154,119,84,82,360,78）；86/87 边界对未 pin」状态「待修」 | (a)/(e) 注释更正+边界对 pin 的证据（注意：I-14-F-R1 decision §3 称 "F-5 … fixed directly"——须核盘） |
| A9 | **REM-35**（I-14-I reviewer F-1，MEDIUM，:62） | 「**实现者 claim 4 的一半为假**…⇒ **下游不得把"gate rc 0"读作"派生已被门证明"**」状态「**待更正措辞**（`handoff.json.derived_keys_discharge.discrimination_inside_the_frozen_gate` 属过度陈述）」 | (a) 该字段措辞已更正的证据；或勘误式闭 |
| A10 | **REM-67 ①③**（I-14-D r3，LOW，:243；:263 明写「**未处理**」） | 行文本三款：「①源码注释「breaks stay OUTSIDE the match」为假且与下一段自相矛盾；②scheme 类要求**首字母**，比其所引 ABNF 窄…；③break 后首字符为值分隔符时不脱敏（有界、非回归）」——②已由 r4 闭（:262），①③开 | ①: 注释已按事实改写（r4/r5）→ 勘误式补「正式更正」即闭；③: (b) 工作卡/registered_open 裁定/真修证据 |

## B 组 — 10 行隐式闭环（SA-REM §4.3 原文清单：`09/10/21/24/56/59/60/61/64/78`——"disposed only under other ids/cards/commits; rows stale or absent"）

| # | 行 | 逐字行文本节录 | 闭合判据 |
|---|---|---|---|
| B1 | **REM-09**（I-14-H CF-I14H-2，:20） | 「`natural_window.py` 两个键是**硬编码字面量**（恒 False）且**与事实相反**…改为派生值」状态「**修复中**（I-14-I）」 | 显式回填：I-14-I 收口证据（载体+复审） |
| B2 | **REM-10**（I-14-H RIDER，:21） | 「容器 basis（list/dict）抛 `TypeError: unhashable` ⇒ 整批 abort（rc 4）…重跑 14 例到 rc 0」状态「**修复中**（I-14-I）」 | 同上（14 例门 rc 0 证据） |
| B3 | **REM-21**（§13 跨批 runner 推广，:42） | 「把"逐例 `expected` 精确类型名比较"回填 M05–M16、M21–M31…」状态「**待派**（owner 已授权，四项前置须先满足）」 | 显式回填：B5 实测执行 + M01-M04-PROPAGATE 臂表证据 |
| B4 | **REM-24**（I-10-B OQ-I10B-2，:45） | 「M14 OQ-03 的 D/E 层追认」状态「待修（与 REM-18 同批）」 | 须核：E1E7 的 M14 追加节是否**裁**了 D/E 层（还是只登记）——若只登记则非闭环 |
| B5 | **REM-56**（:157） | 「r3 产物…已在盘，但 `handoff.json`（21:22）/`review.md`（21:18）**仍是 r2 世代**；**无 r3 载体、无 r3 reviewer 报告**」状态「**待接续**」 | 显式回填：REM-62 落地（r3 载体）+ r3 复审回收证据 |
| B6 | **REM-59**（:170） | 「r3 注释块写「see `r3_fix_record.md`」，而 **该文件不存在**…」状态「**待补**（属 r3 实现者记录，编排层不代写）」 | 显式回填：随 REM-62 合并落地（:190-192 明示 59/60/61 = r3 缺口三个面）证据 |
| B7 | **REM-60**（:171） | 「**F-REV-R2-02** 的…陈述**未加**；**F-REV-R2-03** 的**三处假声明全在**…；**F-REV-R2-04** 的 `binding.json` 括注**未改**」状态「**待修**（r3 迭代内）」 | 显式回填：三项在 r3 落地的证据 |
| B8 | **REM-61**（:172） | 「r3 的**代码修复 + 残留登记 + 测量**已完成…但 **`handoff.json`/`review.md` 仍是 r2 世代**…**迭代无载体**」状态「**待收口**」 | 显式回填：载体收口（handoff_r3.json 等）证据 |
| B9 | **REM-64**（:222） | 「源注释的悬空引用欠一次更正 —— …注释仍写「see `r3_fix_record.md`」…更正须落在**下一个源码世代**」状态「**待下个世代**」 | 显式回填：r5 注释块重写（REM-73 修复）已含该指针更正的证据 |
| B10 | **REM-78**（:331） | 「**「结论句必须带域」这条规则已被证伪三次**…**待机制化**：含「只有/全部/没有/整个族/零代价」的句子须带可解析域字段，生成脚本断言其存在」（:353 状态「🟡…**仍欠机制化**」） | 显式回填：机制化证据（检查器+RED/GREEN/变异+实战）——注意与 REM-79 编号混用（D 组） |
| — | **REM-79**（:332，对照） | 「**「放宽一个类」的判据缺了一半**…**待机制化**：类变更须扫 `old \ new` 与 `new \ old` 两个差集」（:352 状态「✅**已实际使用**」） | 与 B10/D 组合处置 |

## C 组 — 16 项「登记未修」（SA-DEFECT §2 末行逐字：「16（F-REV-D-02/03/04/05、REM-62、R3-02/03/05/06-10、R5-03…08、REM-17/18/24、I-04-C E1/E2、F12）」；AUDIT-GOAL §5.168 变体逐字：「②登记未修 16 项（F-REV-D-02…05、R3-02/03/05/06-10、R5-03…08、REM-17/18/24、I-04-C E1/E2、F12）」——两清单差 = 是否计 REM-62，本卡两录并核）

| # | 项 | 逐字缺陷文本（载体出处） | 闭合判据 |
|---|---|---|---|
| C1 | F-REV-D-02 = **REM-05**（=A1） | 「`_VALUE` 死代码 ⇒ 头条收窄无运行时效果（晋升隐患）」（SA-DEFECT REG:16） | 同 A1 |
| C2 | F-REV-D-03 = **REM-06**（=A2） | 「atom 表缺口：`token2/secret2/password2/api_key2` 非凭据键」 | 同 A2 |
| C3 | F-REV-D-04 = **REM-07**（=A3） | 「无值 `Authorization:`+换行吞掉下一个 token（C13 子案例）」 | 同 A3 |
| C4 | F-REV-D-05 = **REM-08**（=A4） | 「`binding.json` 谎称 conftest 有一行改树指向」 | 同 A4 |
| C5 | **REM-62**（register:198→:215） | 「**r3 世代从未被写出。**…载体（`handoff.json`/`review.md`/`decision.md`/新的哈希表）不存在」 | (e) 已落地证据（:215 声称 handoff_r3.json 新增 + 四载体前缀保全追加——须盘核） |
| C6 | **F-REV-R3-02**（=REM-66，:242） | 「载体引用已不可复现的「overall PASS」核验（夸大）」（task_plan:1741 族） | :242 称「已登记（review.md 与 Round 71 节均已按「注明可复现前提」改写引用方式）」——若引用改写属实即闭 |
| C7 | F-REV-R3-03（=REM-67①，=A10①） | 「源码注释自相矛盾（"breaks stay OUTSIDE the match"）」 | 同 A10① |
| C8 | F-REV-R3-05（=REM-67③，=A10③） | 「break 后值分隔符形态不脱敏（有界、非回归）」 | 同 A10③ |
| C9 | F-REV-R3-06…10（5 项 INFO，=REM-68，:244） | 逐字（register:244）：「①机制句描述错常量；②`both_marker_and_non_marker` 承诺两件只交付一件；③**r3 源码 delta 无登记 diff**、且 `binding.json` 的追加**不是字面前缀保全**；④rule-table harness 在存在登记残留时**无法再返回 rc 0**；⑤字节钉表**不覆盖 r3 世代自己的载体**」状态「**已登记**」 | 逐项 ID↔处置对接（R5-07 指出 REM-68 未按 ID 记）+ 各项 known-limitation/won't-fix/superseded 裁定 |
| C10 | F-REV-R5-03…08（6 项，载体 = `reviewer_report_r5.md` L471-554） | R5-03（LOW）：修正 F-REV-R4-01 的那句注释**本身歧义且一读为假**（`observability.py:315-316` "The breaks are consumed by the match; the indentation and the keys on the lines AFTER the redacted one are not."）——要求改写为唯一读法；R5-04（LOW）：`oracle.md` C2.2（:260-262）留着同一族假句未更正未点名 SUPERSEDED（项目惯例 C3.5/C5.3 式点名）；R5-05（LOW）：`handoff_r5.json` 的 `site` 行号陈旧（应为 `observability.py:324` 与 `290-323`）×4 载体；R5-06（INFO）：`_review_i14d_r5_20260922/` 目录未入 git（r3/r4 同类目录已入）；R5-07（INFO）：REM-68 以实质枚举登记五项 INFO 而未用 F-REV-R3-06…-10 ID（ID↔处置不可 join）；R5-08（INFO）：`credential_leaks == []` 看不到已登记 two-token 形态的 **marker 形**（两仪器各值一行） | 逐项：修面已小者 (a) changes.diff/勘误闭；登记对接类 (a) 处置行即闭；仪器行类 (b) 工作卡；git 跟踪类路由父批 |
| C11 | **REM-17**（=A6） | 「MUT-3 等价变异体…未独立枚举 31 个模型的 dimension 声明」 | 同 A6 |
| C12 | **REM-18**（:34；§16:472 声称「已完成」） | 「追加式勘误清单**待编排层落地**：M05/M14/M20/M24 oracle defaults 相位翻转、M14 `OBS-SUPPLY-BOUND`、M14 OQ-03 D/E 追认、`signed_driver_probe`」修法「按 T1-12 ① 形态追加落地」 | (e) E1E7-ERRATA-LANDING 落地证据（4/4 前缀证明 + 复审 accepted）；残留（JSON 载体 GAP-2、D/E 追认）另行归属 |
| C13 | **REM-24**（=B4） | 「M14 OQ-03 的 D/E 层追认」 | 同 B4 |
| C14 | **I-04-C E1**（progress:438 登记） | 「review.md:24 计时数字错」 | (a) 勘误式闭（封存 review.md 不回改）或已有更正 |
| C15 | **I-04-C E2**（progress:438 登记） | 「`cases_timeout.py:206-216` 链式比较恒 False（断言失效）」 | (a) 小码修 changes.diff + 判据证据；或 (b) 工作卡 |
| C16 | **F12**（register:592；SA-DEFECT：「断管归一化｜断言在返回后开火」OPEN_IN_ACCEPTED_SCOPE） | I-09-C 复审裁定原文（:592）：「**C1/F12 裁定**：归因链 sound…**双轨归属**（数值域=owner/I-09-A 勘误、断管归一化=I-09-B 产品修）、**F12 保留不阻断验收**、非阻断小缺陷 `probe_f12.py:65` C.stderr 误标 B 陈旧 err（rc 归因不受影响，随 F12 轨修复）」 | 双轨各自闭合证据（I-09-A 勘误落案 + I-09-B 产品修）；否则按轨路由 |

## D 组 — REM-78/79 编号混用注记（AUDIT-GOAL §3.3 编号混用 MEDIUM；父 §75 已注「以行文本为准」）

判据：一条**消歧注记**载明——REM79-MECHANIZATION 机制化的是**带域断言规则 = REM-78 行文本**的要求；REM-78 行 :353「仍欠机制化」= 陈旧行文；REM-79 行文本（类变更双向差集）由 r6「已实际使用」（:352）+ 该判据进后续测量纪律——两行各自的真实终态与证据出处写清即闭。

## E 组 — 无 REM 号路由 2 项（AUDIT-GOAL §5.168-③；父 §75 已立号 REM-95/96）

| # | 项 | 逐字文本 | 闭合判据 |
|---|---|---|---|
| E1 | **REM-95**（=F-REV-1/=C1（I-07-C），register:1311） | 「`adapter_dispatch._to_scanner_candidate` 丢弃 `sidecar.py:6-7` 承诺的补救原因 → `locations.error=NULL`（角色级显式、原因级不可观测）——REMEDIATION 轨道。」 | (b) 产品修工作卡规格（或已有修复） |
| E2 | **REM-96**（=F-REV-7，register:1312） | 「合格非夹具公司无法达 reuse（∩https=0）——REMEDIATION/数据轨。」（域：10,596 件中 criterion-(i) 合格 ∩ https-source_url-capable = 0） | (d) 外部/数据轨路由（上游数据形态不可由本仓修） |

## F 组 — 复核要求（本卡另立的核验义务，非处置项）

- F1（sweep）：不信审计员清单——对登记册 REM-01…86 全部行 + REM-93…96 自扫一遍，验证每行处置真实在盘，另抓审计员**漏掉**的静默丢行/误判行。
- F2（16 项计数核）：SA-DEFECT 与 AUDIT-GOAL 两版 16 项清单差异（REM-62 有无）与分组计数（R3-06-10=5、R5-03-08=6、E1/E2=2 如何折算出 16）须显式对账。

—— 以下空白；冻结后追加事实只入 decision.md/evidence/ ——
