
---

## 八十四、【REGISTRY-CLOSURE 处置汇总（AUDIT-GOAL ③ 残留排干：10 零处置行 + 10 隐式行 + 16 登记未修 + REM-78/79 编号注记 + REM-95/96）】2026-09-23 深夜

> 卡指定代号「七十六」；因父侧 §76–§83 已占号，本节取下一空号——沿 §35 纪律「引用带节标题消歧」，不重蹈 §11–§20 重复编号缺陷。载体=`execution_runs\REGISTRY-CLOSURE\a20260923-01`（oracle 冻结 `16e4f2a0…` / decision / changes.diff / evidence）；本节=**全部 42 条处置的唯一行级回填**（历史行一字未改，append-only）。
> **计数**：CLOSED-NOW 16｜SUPERSEDED 13｜WORK-CARD 11（WC-1..6）｜OWNER-BLOCKED 2｜EXTERNAL-BLOCKED 1。class 细目与逐字行文见 decision.md。

### A 组——10 行零处置（AUDIT-GOAL §3.3）处置

| 行 | 处置（2026-09-23） |
|---|---|
| **REM-05**（_VALUE 死代码） | **CLOSED-NOW**：行修法「加注释说明非承重地位」已交付 changes.diff J1（r6 树+生产，纯注释）；AST 三树证 1 赋值/0 引用 + 20 形态行为恒等 + 编译过（evidence/rem05_behavior_identity.txt）；落盘随下批。 |
| **REM-06**（token2 等非凭据键） | **WORK-CARD WC-1**（扩键+双仪器行+过度脱敏定价）——当前态实测未修（95 行 rule table 无该族）。 |
| **REM-07**（无值 Authorization 吞 token） | **WORK-CARD WC-2=I-18-A 细化**；⚠新发现：r6 树上劣化于 handoff:144 记载（`stage=summarize` 复吞，「narrowing saves」句=陈旧记录，勘误以此行为准）。 |
| **REM-08**（binding.json 假称） | **SUPERSEDED**：r2 已更正（binding.json:72 correction 行；conftest `783b1774…` 复算相符；reviewer_report_r2 VERIFIED）。 |
| **REM-16**（evidence_paths 6/7） | **CLOSED-NOW**：补登记=attempt `evidence/rem16_command_runs_registration.txt`（第 7 目录 `r2-verify-before/` 正式入册；封存 handoff 不回改）。 |
| **REM-17**（MUT-3 等价变异） | **WORK-CARD WC-3=B4a**（31 模型声明级负例）。 |
| **REM-25**（reserve 124/150 需 owner 选） | **SUPERSEDED**：owner §16 E-1「150/60」已裁（OWNER_DECISIONS:365/375）→ I-14-F-R1 已应用（210/124/86→210/150/60，doc 真数字直修）+ accepted_scoped。审计「选择未落」=误判。 |
| **REM-30**（注释长度/86-87 未 pin） | **SUPERSEDED**：F-5 已在 I-14-F-R1 **直修**（decision.md:189-191；测试头注真值 174/154/119/84/82/360/78 + 新边界 60/61 双 pin）。审计「勘误集不含 F-5」=误判（不在集内恰因直修）。 |
| **REM-35**（gate rc 0 过度陈述） | **SUPERSEDED**：措辞已更正（I-14-I handoff 该字段现文自记「CORRECTED BY THE CARRIER-LANDING PASS…must NOT be read as gate-proven」）。 |
| **REM-67 ①/③** | ① **CLOSED-NOW**：注释 r5 已改写（假句仅存冻结历史副本）；本行=所欠 F-REV-R3-03 **正式更正**。③ **WORK-CARD WC-1 子项**（break 后值分隔符族无任何仪器行覆盖，实测 N5f–N5w/R7a-R7d 均非该形）。 |

### B 组——10 行隐式闭环 → 显式回填

| 行 | 处置（2026-09-23） |
|---|---|
| **REM-09 / REM-10** | **CLOSED-NOW**（显式回填）：I-14-I 全链（handoff accepted_scoped + reviewer_report + 14 例门 rc 0；git `980c9b7a`）。 |
| **REM-21** | **CLOSED-NOW**：B5 按实测执行 + M01-M04-PROPAGATE 臂表（E0/F3/G2+S1/B0，20/20 冻结符）→ REM-80 门缺口补齐（:939）。 |
| **REM-24** | **⚠改判 OWNER-BLOCKED**（审计"隐式闭环"=反向误判）：E1E7 M14 节 ②-c 逐字「D/E 层是否追认由 owner 决定」`carried_not_resolved`「只登记，不代裁」。**路由 owner**。 |
| **REM-56** | **SUPERSEDED**：r3 载体+复审已在盘（:215 落地 / :240 `reviewer_report_r3.md` 44008B/c617c43a）。 |
| **REM-59** | **SUPERSEDED**：并 REM-62 落地（fix_record.md:162 CORRECTION 3 承载 r3 记录）。 |
| **REM-60** | **SUPERSEDED**：R2-02/03/04 随 r3 落地（handoff_r3 `r3_corrections`）。 |
| **REM-61** | **SUPERSEDED**：handoff_r3.json 在盘（9788B）+ review.md `## r3`。 |
| **REM-64** | **SUPERSEDED**：r5 注释块重写已改悬空指针为如实指认（r6 树现文核）。 |
| **REM-78** | **CLOSED-NOW**：机制化已完成（借 REM79-MECHANIZATION 名=编号混用，见 D1）：check_domain_assertions.py v1.2.0-correction2 + RED/GREEN/3 变异 + 三轮词表（214→48→2 真阳 0）+ AUDIT-GOAL §10 自查 0。:353「仍欠机制化」=陈旧行文。 |

### C 组——16 项登记未修（逐单元；计数对账：两审计"16"实为 25/24 单元，均对不上——以逐条为准）

| 项 | 处置（2026-09-23） |
|---|---|
| F-REV-D-02..05 | = REM-05/06/07/08（A 组）：CLOSED-NOW / WC-1 / WC-2 / SUPERSEDED。 |
| **REM-62** | **SUPERSEDED**：:215 声称经本卡盘核全真（handoff_r3 + 四载体 CORRECTION 3/r3 节）。 |
| **F-REV-R3-02**（=REM-66） | **CLOSED-NOW**（带披露）：:242 引用改写已落；活载体 `overall PASS` 0 命中；残余=封存 handoff_r3:13 历史串由 :242 覆盖。 |
| **F-REV-R3-03 / R3-05** | = REM-67①/③（A 组）：CLOSED-NOW（正式更正=本行）/ WC-1 子项。 |
| **F-REV-R3-06…10**（=REM-68①-⑤，逐 ID 对接=R5-07 之修） | ①R3-06 **CLOSED-NOW**（INFO 登记即处置）；②R3-07 **WC-1 子项**（both_marker_and_non_marker 半交付）；③R3-08 **CLOSED-NOW won't-fix 登记**（r3 delta 无 diff=历史形态限制；binding 追加非字面前缀=JSON 形态，后续一律新键承载）；④R3-09 **CLOSED-NOW by-design**（rule harness rc=3 负 verdict 属设计+禁引「91 行 rc 0」纪律）；⑤R3-10 **已路由 BOOKKEEP-REPAIR #6**（I-14-D 报告补 pin）。 |
| **F-REV-R5-03…08**（逐字在 reviewer_report_r5.md L471-554） | R5-03 **CLOSED-NOW**（复审给定唯一读法改写=changes.diff J2 交付）；R5-04 **CLOSED-NOW**（本行点名：I-14-D `oracle.md` **C2.2(:260-262)=SUPERSEDED**，以 C5.4/N5d 为准——项目点名取代惯例达成）；R5-05 **CLOSED-NOW**（正确 site 立档：`observability.py:324` 与 `290-323`；handoff_r5/review.md##r5/§18.2/task_plan R74 四处旧值以此为准）；R5-06 **已路由 BOOKKEEP-REPAIR**（`_review_i14d_r5_20260922/` 补入 git）；R5-07 **CLOSED-NOW**（ID↔处置对接=上列 R3-06..10 行）；R5-08 **WC-1 子项**（C10 对 R3a/R3b 补 marker 载荷行，每仪器一行）。 |
| **REM-17 / REM-18 / REM-24** | REM-17=WC-3；**REM-18=SUPERSEDED**（E1E7-ERRATA-LANDING 4/4 前缀证明+accepted 落定；残留按 GAP-2/D-E 各归其位）；REM-24=owner（B 组）。 |
| **I-04-C E1 / E2** | 均 **SUPERSEDED**：E1 追加式勘误在案（review.md:28-35 等 5 处，9.87/13.2→**9.78s/13.4s**，权威 phase-wall.txt:9）；E2 **已修**（r5 直修 cases_timeout.py：恒假链式比较+字面 True 断言→真量词+真断言，变异 16/16，cc07aa36→bfca707a）。 |
| **F12** | **WORK-CARD WC-4 + OWNER-BLOCKED（数值域半）**：产品半（断管退出归一化至 {0,2}，随修 probe_f12.py:65）立 WC-4；冻结数值域 {0,2} vs 实测 120 的勘误=owner/I-09-A 权。机制勘误：「断言在返回后开火」措辞不准——实为 CLI finalization flush 失败（Errno 22）自报 rc=120。 |

### D 组——REM-78/79 编号混用

**D1 注记（即闭）**：REM79-MECHANIZATION 机制化的规则=**REM-78 行文本**（带域断言）；register 自 :435 以「REM-79」记功系误标；:353「仍欠机制化」陈旧。**REM-79 行文本**（类变更双向差集）=r6 已实用（:352），其「待机制化」残余 **WC-5**（常设差集扫描工具）。父 §75「以行文本为准」+ 本注记=该 MEDIUM 正式处置。

### E 组——REM-95/96（原无号路由 2 项）

**REM-95**（adapter_dispatch 丢补救原因→locations.error=NULL）**WC-6**（原因级持久化产品修）。**REM-96**（合格∩https=0）**EXTERNAL-BLOCKED**→数据轨/上游语料形态（holdout `dfeb7c54…`）。

### 工作卡规格（可直接派单）

- **WC-1｜I-14-D r8 残差轮**（REM-06+REM-67③+R5-08+R3-07）：iso 基=product_narrow_r6(`2f644994…`)；扩数字后缀键族+双仪器行+过度脱敏定价；break 后值分隔符族补行（修或 registered_open 带域）；C10 对 marker 行；both_marker 半交付补全/改承诺；红绿+变异+双向差集+独立复审。
- **WC-2｜I-18-A 细化**（REM-07）：无值 `Authorization:` 跨行吞词修复（保 `doc=17`、无伪 `<redacted>`），并处理 r6 放宽后 `stage=summarize` 复吞回归。
- **WC-3｜B4a**（REM-17）：31 模型「角色表名字 × 不合格 dimension」声明级负例。
- **WC-4｜F12 产品修**：断管退出归一化至 {0,2} + probe_f12.py:65（前置=owner 数值域裁）。
- **WC-5｜REM-79 机制化**：`old \ new`/`new \ old` 常设扫描工具。
- **WC-6｜REM-95**：补救原因持久化至 `locations.error`。

### 路由汇总

owner 2：REM-24（M14 OQ-03 D/E 追认）｜F12 数值域勘误。external 1：REM-96（数据轨）。既有卡承接 2：R3-10→BOOKKEEP-REPAIR #6、R5-06→BOOKKEEP-REPAIR。changes.diff=仅 J1（REM-05 注释）+J2（R5-03 注释）×2 目标，行为恒等判据在 attempt evidence。

### sweep 新发现（不信审计清单的自扫结果，7 条）

①REM-25 实为 owner 已裁已落地（审计 OPEN=误）②REM-30 F-5 已直修（审计 OPEN=误）③REM-35 措辞已更正（审计"无下文"=误）④**REM-24 审计"隐式闭环"=反向误判，实为 owner 位（最危险一类）**⑤REM-08/18/62/16=过期状态读取（逐项已处置）⑥REM-07 在 r6 树劣化于 handoff 记载（陈旧记录勘误）⑦SA-DEFECT 对 F12 机制措辞与盘上机制不符。**其余 86 行处置证据抽核在盘、无新增零处置行**（REM-87…92=编号空档非丢行，全库 0 命中）。
