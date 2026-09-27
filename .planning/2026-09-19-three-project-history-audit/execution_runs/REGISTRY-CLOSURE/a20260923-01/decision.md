# REGISTRY-CLOSURE decision — 逐项处置表（per-item disposition）

- attempt：`execution_runs\REGISTRY-CLOSURE\a20260923-01`｜清单=冻结 `oracle.md`（A–F 组 40 项 + 拆分后 42 条处置行）｜判定时点 2026-09-23
- 纪律：封存载体零回改（勘误走登记册/处置记录）；本卡对目标仓/历史 attempt **零写入**（唯一写入=本 attempt + 登记册追加式单节）；代码修只出 `changes.diff` 不落盘。
- **计数**：CLOSED-NOW 16｜SUPERSEDED（他处已修/已被取代）13｜WORK-CARD-NEEDED 11（其中 F12 带 owner 子路由）｜OWNER-BLOCKED 2（REM-24 + F12 数值域半）｜EXTERNAL-BLOCKED 1。合计 42 条处置行（A10 拆①③、F12 拆双轨；C7/C8 系 A10①③ 的台账别名，交叉引用不另计）。
- **登记册回填**：全部 42 条经**单一追加式处置汇总节**入册（本文件末"汇总节预览"）；**不改任何历史行**。

---

## A 组 — 10 行零处置（AUDIT-GOAL §3.3）逐项处置

| # | 行（逐字关键文，全文=oracle A 组） | class | 处置 / 闭合证据 / 路由 | 行回填 |
|---|---|---|---|---|
| A1 | **REM-05**：「`_VALUE` 在两棵树中都是**死代码**…晋升隐患：未来"清理"删掉死常量会误以为修复仍在」 | **CLOSED-NOW**（修复交付） | 行修法二选一之「加注释说明其非承重地位」已交付 = `changes.diff` J1（r6 树 + 生产各一 hunk，纯注释）。判据证据：AST 三树复算 `_VALUE` 1 赋值/0 引用（DEAD-CODE-CONFIRMED）、20 形态 `redact_text` 行为恒等（all_identical=true）、py_compile OK（`evidence/rem05_behavior_identity.txt`）。**落盘应用=随下一批晋升/修批**（本卡不改树）。 | ✅ 汇总节 |
| A2 | **REM-06**：「`token2/secret2/password2/api_key2` 不是凭据键…」修法「补 rule-table 行 + 扩展凭据键集合」 | **WORK-CARD**（WC-1） | 当前态实测未修（r6 树 `_SINGLE_ATOMS/_PAIR_ATOMS` 无数字后缀键；95 行 rule table 无该族行；live probe `token2` 明文留存）。行为面修复（扩键+双仪器行+过度脱敏定价）超"tiny"界 → 立卡规格 WC-1（见下）。 | ✅ 汇总节（路由） |
| A3 | **REM-07**：「无值 `Authorization:` + 换行仍吞掉下一个 token…作为 C13 子案例继续跟踪并修」 | **WORK-CARD**（WC-2=I-18-A 细化） | 未修且**比记录更糟**（新发现）：r6 放宽 `_AUTH_PREBREAK_TOKEN=[^\s]+` 后三行输入 `Authorization:\ndoc=17\nstage=summarize` 两键全吞（handoff.json:144「narrowing saves stage=summarize」在 r6 树上为假——陈旧记录，随汇总节勘误）。C13 轨=task_plan:1176 已名 I-18-A；WC-2=该卡细化规格。 | ✅ 汇总节（路由+勘误） |
| A4 | **REM-08**：「`binding.json` 谎称 conftest 有一行改树指向」 | **SUPERSEDED** | **已修**（r2 轮、盘上核）：`binding.json:72` 现文=「r2/F-REV-D-05 correction: an earlier version…claimed 'one-line tree-pointing change'. It never did…」；conftest 重算 `783b1774…bb7a9`/275B 与更正后表述相符；reviewer_report_r2.md:136-140 VERIFIED。审计员"待修"系读旧状态。 | ✅ 汇总节 |
| A5 | **REM-16**：「`command_runs/` 有 7 个子目录而 `evidence_paths` 只列 6（`r2-verify-before/` 未列）」修法「补登记（结论未缺）」 | **CLOSED-NOW** | 修法即补登记 → `evidence/rem16_command_runs_registration.txt`（7 目录实测清单 + 第 7 目录 `r2-verify-before/` 正式补登记）。封存 handoff 不回改（惯例）。结论面无缺（行自述"结论未缺"、verification_before/after 在 evidence_paths）。 | ✅ 汇总节（本条即补登记） |
| A6 | **REM-17**：「MUT-3…是**等价变异体**…未独立枚举 31 个模型的 dimension 声明」修法「补"角色表名字 × 不合格 dimension"声明级负例」 | **WORK-CARD**（WC-3=B4a） | 测试面新增（31 模型声明级负例）非 tiny → 立卡规格 WC-3。 | ✅ 汇总节（路由） |
| A7 | **REM-25**：「…**需 owner 选**：reserve 150 ⇒ 阈值 60，或保留 86 但记录真实数字」 | **SUPERSEDED** | **owner 已选且已落地**：OWNER_DECISIONS:365 原话「E-1: 150/60」、:375 裁行（GENERATION_RESERVE=150 ⇒ 阈值 60）→ `I-14-F-R1\a20260922-01` 应用（decision.md §1-§3；210/124/86→210/150/60；docstring 真数字重写=F-1 直修）→ 复审 accepted_scoped（audit §3.1 行）。审计员"选择未落"为**误判**（漏读 §16）。残差=机器/年代标定 caveat（I-14-F-R1 §9.7 携带）。 | ✅ 汇总节 |
| A8 | **REM-30**：「单测注释误述 4/7 用例长度…86/87 边界对未 pin」 | **SUPERSEDED** | **已修**（I-14-F-R1 直修）：其 decision.md:189-191「F-5's comment misstatements and unpinned boundary are **fixed directly** in this attempt's test file」；盘核 `company-wiki\tests\contract\test_short_basetemp_convention.py` 头注 + 新边界对 **60/61 双 pin**（unit+sweep 两层，decision §2/§5）。审计员"勘误集不含 F-5"为**误判**（F-5 不在勘误集恰因它被直修）。 | ✅ 汇总节 |
| A9 | **REM-35**：「…**下游不得把"gate rc 0"读作"派生已被门证明"**…**待更正措辞**」 | **SUPERSEDED** | **措辞已更正**（落定时按 reviewer F-1）：`I-14-I\handoff.json` 该字段现文自记「CORRECTED BY THE CARRIER-LANDING PASS per reviewer finding F-1…CORRECT STATEMENT: …the gate's rc 0 must NOT be read as 'the derivation is gate-proven'」。审计员"无下文"为**误判**。 | ✅ 汇总节 |
| A10① | **REM-67①**（=F-REV-R3-03）：「源码注释「breaks stay OUTSIDE the match」为假且与下一段自相矛盾」（:263「正式更正未做」） | **CLOSED-NOW** | 注释本体 r5 已按事实改写（r6 树 L310-328 现文核；假句仅存于冻结 scratch/harness 历史副本=按纪律不动）；**所欠"正式更正"记录即本处置行**（F-REV-R3-03 formal correction，2026-09-23，域=r6 世代树+生产注释块）。 | ✅ 汇总节（本条即正式更正） |
| A10③ | **REM-67③**（=F-REV-R3-05）：「break 后首字符为值分隔符时不脱敏（有界、非回归）」 | **WORK-CARD**（WC-1 子项） | 实测仍无任何仪器行覆盖该族（N5f–N5w/R7a–R7d 全为 pre-break token/quoted/line-3/控制空白形；`\n,<secret>` 形无行）→ 并入 WC-1（补行+修/registered_open 裁定）。 | ✅ 汇总节（路由） |

## B 组 — 10 行隐式闭环 → 显式回填

| # | 行（逐字关键文） | class | 处置 / 闭合证据 | 行回填 |
|---|---|---|---|---|
| B1 | **REM-09**（状态「**修复中**（I-14-I）」） | **CLOSED-NOW** | 显式回填：I-14-I 全链收口（`I-14-I\a20260919-01` handoff `accepted_scoped`/64897B + reviewer_report + review.md + evidence/artifact_hashes.txt；git `980c9b7a`「I-14-I complete (14-case gate rc 0)」）。派生键改 derived 值（handoff `derived_keys_discharge.now`）。 | ✅ |
| B2 | **REM-10**（同上） | **CLOSED-NOW** | 同一卡收口（14 例门 rc 0 证据在 handoff/commit；xfail 去除随卡）。 | ✅ |
| B3 | **REM-21**（「**待派**」） | **CLOSED-NOW** | 显式回填：B5 内按实测执行（register:64「已在 B5 内按实测执行」）+ B5-fix/M01-M04-PROPAGATE 臂表（register:941：E=0/F=3/G=2+declared_expectation_missing/S=1/B=0，20/20 冻结符）→ REM-80 四批门缺口补齐（:939）。 | ✅ |
| B4 | **REM-24**（「M14 OQ-03 的 D/E 层追认」「与 REM-18 同批」） | **OWNER-BLOCKED** | **审计员"隐式闭环"为反向误判**：E1E7 的 M14 追加节 ②-c 逐字明载「**D/E 层是否追认由 owner 决定**」`status: carried_not_resolved`「本节只登记，不代裁」（M14 oracle.md 尾节）。⇒ 登记落地≠D/E 追认；该项只 owner 可裁。路由：owner（数值/会计约定判断位）。 | ✅（状态改判 owner-blocked） |
| B5 | **REM-56**（「无 r3 载体、无 r3 reviewer 报告」「**待接续**」） | **SUPERSEDED** | r3 载体与复审均已存在（register:215 落地 + :240 回收 `reviewer_report_r3.md` 44008B/c617c43a）。 | ✅ |
| B6 | **REM-59**（`r3_fix_record.md` 悬空引用「**待补**」） | **SUPERSEDED** | 并入 REM-62 落地（:190-192 明示三面归一）：`fix_record.md` 追加 CORRECTION 3（:162）承载 r3 记录；源注释悬空引用由 r5 注释块处置（见 B9）。 | ✅ |
| B7 | **REM-60**（R2-02/03/04 三项「**待修**（r3 迭代内）」） | **SUPERSEDED** | r3 世代落地（handoff_r3.json `r3_corrections`；SA-DEFECT 亦记「全 FIXED（r3）」；REM-62 行 :215 四载体追加证据）。 | ✅ |
| B8 | **REM-61**（「迭代无载体」「**待收口**」） | **SUPERSEDED** | `handoff_r3.json` 在盘（9788B，2026-09-22 00:28）+ review.md `## r3` 节（:78/:109）。 | ✅ |
| B9 | **REM-64**（注释悬空引用「**待下个世代**」） | **SUPERSEDED** | r5 注释块重写已落实（register:311；r6 树现文：「The companion that reproduction names, `r3_fix_record.md`, was never written and is deliberately NOT substituted for…」——引用已改为如实指认）。 | ✅ |
| B10 | **REM-78**（「**待机制化**…生成脚本断言其存在」；:353「仍欠机制化」） | **CLOSED-NOW** | 机制化**已完成**（借 REM79-MECHANIZATION 名下——编号混用见 D1）：`tools/check_domain_assertions.py` v1.2.0-correction2（stdlib、exit 0/1/--json）+ RED/GREEN/3 变异 PROTOCOL_SATISFIED + 三轮词表迭代（214→48→2，真阳 0）+ 五轮实战自扫 + AUDIT-GOAL §10 自查 0 违规。:353「仍欠机制化」=陈旧行文。 | ✅ |

## C 组 — 16 项「登记未修」逐项处置（两份审计清单并录；**计数对账见 F2**）

| # | 项（逐字关键文） | class | 处置 / 闭合证据 / 路由 | 行回填 |
|---|---|---|---|---|
| C1–C4 | F-REV-D-02/03/04/05 = **REM-05/06/07/08** | 同 A1–A4 | 交叉引用（不另计）：CLOSED-NOW / WORK-CARD WC-1 / WORK-CARD WC-2 / SUPERSEDED。 | — |
| C5 | **REM-62**（「r3 世代从未被写出」） | **SUPERSEDED** | 落地证据同 B8（register:215 声称经盘核全真：handoff_r3.json + oracle.md:366/fix_record.md:162/binding.json:114/review.md:78 四处 CORRECTION 3/r3 节）。主审已裁「REM-62=已闭环」；SA-DEFECT 残留其 16 项清单系读 :198 旧快照。 | ✅ |
| C6 | **F-REV-R3-02**（=REM-66）：「载体引用已不可复现的「overall PASS」核验（夸大）」 | **CLOSED-NOW**（带披露） | register:242 处置=引用方式改写（"注明可复现前提"）已落 review.md/Round-71 节；**本卡独立核**：review.md 现文 `overall PASS` 0 命中（活载体无未限定夸大引用）；残余=封存 `handoff_r3.json:13` 历史串（按纪律不改，由 :242 更正覆盖）。披露：review.md 内「可复现前提」字样未逐字命中——其实质条件（活载体引用无夸大）已核，措辞形态存疑不影响结论。 | ✅ |
| C9 | **F-REV-R3-06…10**（=REM-68 五项 INFO）逐 ID 对接（此对接即 R5-07 之修）： | | | |
| C9a | R3-06=①机制句描述错常量 | **CLOSED-NOW** | INFO 级记录瑕疵：登记即处置（known-limitation，封存记录不回改）；r5 注释块重写（REM-73）已消其源注释面。ID↔处置对接=本行。 | ✅ |
| C9b | R3-07=②`both_marker_and_non_marker` 承诺两件只交付一件 | **WORK-CARD**（WC-1 子项） | 半交付面并入 WC-1（补全或按实改承诺+双仪器行）。 | ✅（路由） |
| C9c | R3-08=③r3 delta 无登记 diff 且 binding 追加非字面前缀 | **CLOSED-NOW**（won't-fix 登记） | 流程类历史瑕疵：r3 delta 无 diff=记录形态限制（后续世代已改走 changes.diff 纪律）；binding 追加=JSON 重排非字面前缀（handoff_r3.json:92 自记「appended, not a rewrite; the original string is left in place」）。裁定：登记不修（封存件），后续 JSON 追加一律走"新键承载"形态。 | ✅ |
| C9d | R3-09=④rule harness 自 r3 起 rc=3（负 verdict 属设计） | **CLOSED-NOW**（by-design 已知限制） | 已裁定为设计（REM-82「已知，随 r7 处理」+ 禁引「91 行 rc 0」纪律）；r7 双载荷行落地后 rc=3 语义仍如实（audit §10 族核）。登记为永续已知限制（disclosure rule 在效）。 | ✅ |
| C9e | R3-10=⑤字节钉表不覆盖 r3 世代自身载体 | **WORK-CARD**（已路由 BOOKKEEP-REPAIR #6） | 钉覆盖面缺口与父 §75「I-14-D r2-r5 四报告无 pin」同物 → 已在飞 **BOOKKEEP-REPAIR** 卡 #6 承接；本行路由对接（无新卡）。 | ✅（路由） |
| C10 | **F-REV-R5-03…08**（载体 `reviewer_report_r5.md` L471-554）逐项： | | | |
| C10a | R5-03（LOW）修正句歧义（一读为假） | **CLOSED-NOW**（修复交付） | reviewer 给定唯一读法改写已交付 = `changes.diff` J2（两目标各一 hunk，纯注释，compile OK）。 | ✅ |
| C10b | R5-04（LOW）`oracle.md` C2.2 假句未点名 SUPERSEDED | **CLOSED-NOW**（勘误式） | 封存 oracle 不回改 → **本处置行即点名**：I-14-D `oracle.md` **C2.2（:260-262）= SUPERSEDED**（其 scheme 枚举 r3 已删、break 为 run 非"exactly one"、break+缩进在 match 内=N5d 25 字符；以 C5.4/N5d 行文为准）——满足项目"点名取代"惯例（C3.5/C5.3 同形）。下世代追加轮可把本行转录为 CORRECTION。 | ✅ |
| C10c | R5-05（LOW）`site` 行号陈旧（×4 载体） | **CLOSED-NOW**（勘误式） | 正确 site 值就此立档：**`observability.py:324`**（r5 `_AUTH_PREBREAK_TOKEN`）与 **`290-323`**（r5 注释块）；handoff_r5.json / review.md `## r5` / register §18.2 / task_plan Round 74 四处旧值（317 / 290-325）**以此为准**（封存/历史行不回改——本条即 append-only 更正形态）。 | ✅ |
| C10d | R5-06（INFO）`_review_i14d_r5_20260922/` 未入 git | **WORK-CARD**（已路由 BOOKKEEP-REPAIR） | git 跟踪类记账 → 并入在飞 **BOOKKEEP-REPAIR** 卡（补提交该目录，与 #6 同批）；本行路由对接。 | ✅（路由） |
| C10e | R5-07（INFO）REM-68 未按 ID 记（不可 join） | **CLOSED-NOW** | 修复=ID↔处置对接：本表 C9a–C9e 即 F-REV-R3-06→-10 的逐 ID 处置映射，随汇总节入册。 | ✅ |
| C10f | R5-08（INFO）`credential_leaks` 看不到 two-token 形 marker 行 | **WORK-CARD**（WC-1 子项） | r7 双载荷行只闭自家族（review.md:395/412 域限定）；C10 对（R3a/R3b）marker 行仍缺 → 并入 WC-1「每仪器各一行」。 | ✅（路由） |
| C12 | **REM-18**（「追加式勘误清单**待编排层落地**」） | **SUPERSEDED** | E1E7-ERRATA-LANDING 已落地：4/4 卡前缀证明（M05 14790→18889 / M14 19339→28088 / M20 13074→17692 / M24 26216→31200，difflib 纯插入）→ 复审 accepted 落定（§44:1080）；盘核 M14 oracle 尾节 E-2/E-5/E-6/E-7 全文在。残留按裁定各归其位：JSON 载体=GAP-2（随晋升卡）、E-6 D/E 追认=B4（owner）、日期标签 F2/GAP-4/5=留置登记。SA-DEFECT「登记未修」系读 :34 旧行。 | ✅ |
| C14 | **I-04-C E1**（「review.md:24 计时数字错」） | **SUPERSEDED** | 追加式勘误已在案（review.md:28-35「E1 更正…9.782719/13.386 ⇒ **9.78 s / 13.4 s**（9.87 系末两位换位转录错）…原行一字未删」+ decision.md:477/oracle.md:216/handoff.json:36,279/recovery §6.2 四镜像；权威 `evidence/phase-wall.txt:9`）。SA-DEFECT「五文档中未见后续收口」系检索面外（收口在 I-04-C attempt 内）。 | ✅ |
| C15 | **I-04-C E2**（「`cases_timeout.py:206-216` 链式比较恒 False（断言失效）」） | **SUPERSEDED** | **已修**（r5，唯一副本在盘）：`lease in successful_ids is False` 恒假子句与字面 `True` 断言均已替换为真全称量词+真断言（现 L205-232 带 `# r5 E2` 修记）；变异证据 16/16（evidence/r5-assertion-mutation.txt）；哈希迁 cc07aa36→bfca707a（recovery §6.3）。 | ✅ |
| C16 | **F12**（断管归一化；frozen rc∈{0,2} vs 实测 **120**）双轨 | **WORK-CARD**（WC-4）+ **OWNER-BLOCKED**（数值域半） | 实测双半皆未执行：I-09-B 无产品修（其 attempt 无 changes.diff、零断管内容）；I-09-A/owner 数值域勘误未记（errata.md E-1…E-13 不涉 F12；OWNER_DECISIONS 0 命中）。路由：**WC-4**（产品半：断管退出归一化 + 随修 `probe_f12.py:65` C.stderr 误标）+ **owner**（半：冻结数值域 {0,2} vs 120 的勘误/判据决定——I-09-A oracle 权）。机制勘误：SA-DEFECT「断言在返回后开火」措辞不准——实为产品 CLI 解释器 finalization 段 stdio flush 失败（Errno 22）自报 rc=120（I-09-C handoff:54 原文）。 | ✅（双路由） |

## D 组 — REM-78/79 编号混用

| # | 项 | class | 处置 | 行回填 |
|---|---|---|---|---|
| D1 | 编号混用注记（AUDIT-GOAL §3.3 MEDIUM） | **CLOSED-NOW** | **消歧注记（本条即闭）**：`REM79-MECHANIZATION` 机制化的规则=**REM-78 行文本**（结论句带域+生成脚本断言）；register 自 :435 起以「REM-79」记功系**误标**；REM-78 行 :353「仍欠机制化」=陈旧。REM-79 行文本之判据（类变更双向差集）由 r6 **实际使用**（:352，结论因之异于 r5）。父 §75「以行文本为准」+ 本注记 = 该 MEDIUM 的正式处置。 | ✅ |
| D2 | REM-79 之「**待机制化**：类变更须扫 `old \ new` 与 `new \ old` 两个差集」残余 | **WORK-CARD**（WC-5） | 判据已实用（r6）但**无常设工具**（checker=词文域检查器，非差集扫描）→ 立卡规格 WC-5。 | ✅（路由） |

## E 组 — 原无 REM 号 2 项（父 §75 已立 REM-95/96）

| # | 行（逐字） | class | 处置 / 路由 | 行回填 |
|---|---|---|---|---|
| E1 | **REM-95**（register:1311）：「`adapter_dispatch._to_scanner_candidate` 丢弃 `sidecar.py:6-7` 承诺的补救原因 → `locations.error=NULL`…——REMEDIATION 轨道。」 | **WORK-CARD**（WC-6） | 产品修面（原因级持久化）→ 立卡规格 WC-6。 | ✅（路由） |
| E2 | **REM-96**（register:1312）：「合格非夹具公司无法达 reuse（∩https=0）——REMEDIATION/数据轨。」 | **EXTERNAL-BLOCKED** | 数据形态缺口（10,596 件语料中合格∩https=0）非本仓可修 → 路由**数据轨/上游**（filing-fetch 语料形态改造=外部依赖）；holdout 证据 `dfeb7c54…` 随 I-07-C 载体。 | ✅（路由） |

---

## 工作卡规格（prompt-sized，可直接派单）

**WC-1｜I-14-D r8 残差一轮（覆盖 REM-06 / REM-67③ / R5-08 / R3-07）**
基=iso 复制 `product_narrow_r6`（pin `2f644994…`）；oracle 先冻结。①凭据键集扩数字后缀族（token2/secret2/password2/api_key2；参照 `_PAIR_ATOMS` 分词规则），rule-table+oracle 各补行，**过度脱敏定价**（monkey/oauth/secretary 等对照行必绿）；②break 后值分隔符族（`\n,<secret>` 等 6 形）补行——修脱敏或按 C10 先例 `registered_open`（须域内声明）；③C10 对（R3a/R3b）补 marker 载荷行（每仪器一行）；④核 `both_marker_and_non_marker` 半交付：补全或改承诺。红绿+变异+双向差集判据（`old \ new`/`new \ old`）+独立复审。

**WC-2｜I-18-A 细化：无值 `Authorization:` 吞 token（REM-07/C13）**
修 `authorization\s*[:=]\s*` 跨行吞词（`Authorization:\ndoc=17` 须保 `doc=17` 且无伪 `<redacted>`）；须同时处理 r6 放宽后 `stage=summarize` 复吞回归（本卡勘误记录的陈旧 handoff 声明一并更正）；红绿+变异+独立复审。

**WC-3｜B4a 声明级负例（REM-17）**
「角色表名字 × 不合格 dimension」声明级负例测试：独立枚举 31 模型 dimension 声明，MUT-3 等价变异体改可观察（注册表层可见）。

**WC-4｜F12 断管归一化产品修（+probe_f12.py:65）**
产品 CLI broken-pipe 退出归一化至冻结域 {0,2}（Errno 22 finalization flush 路径）；随修 probe_f12.py:65 C.stderr 误标；**前置**=owner 对数值域勘误的裁决（见路由）。

**WC-5｜REM-79 差集判据机制化**
常设工具：字符类变更必扫 `old \ new` 与 `new \ old` 双差集并输出登记行（挂 rules harness）。

**WC-6｜REM-95 补救原因持久化**
`adapter_dispatch._to_scanner_candidate` 传递 `sidecar.py:6-7` 补救原因 → `locations.error` 非 NULL（角色级+原因级双可观测）。

**已路由既有卡（不立新）**：R3-10→BOOKKEEP-REPAIR #6（I-14-D 报告补 pin）；R5-06→BOOKKEEP-REPAIR（`_review_i14d_r5_20260922/` 补入 git）。

**owner 路由（2）**：①REM-24——M14 OQ-03 D/E 层追认（内部冲减是否需 signed 约定）；②F12——冻结数值域 {0,2} vs 实测 120 的 oracle 勘误/判据决定。
**external 路由（1）**：REM-96——数据轨/上游语料形态。

---

## F 组核验结果（审计员清单不信自核 + 反向 sweep）

- **F1 sweep**：REM-01…86 全 86 行 + REM-93…96 状态自扫。**新发现静默丢/误判 5 例**：①REM-25（实为 owner 已裁已落地，审计判 OPEN=误）；②REM-30（F-5 已直修，审计判 OPEN=误）；③REM-35（措辞已更正，审计判"无下文"=误）；④REM-24（审计判"隐式闭环"，实为 carried_not_resolved **owner 位**——反向误判，最危险一类）；⑤REM-08/REM-18/REM-62/REM-16 各有程度不一的过期状态读取（已逐项处置）。另 2 条记录级新发现：⑥REM-07 在 r6 树上**劣化**于 handoff 记载（stage=summarize 复吞，"narrowing saves"句=陈旧记录）；⑦SA-DEFECT 对 F12 的机制措辞（"断言在返回后开火"）与盘上机制不符（实为 finalization flush rc=120）。**未再发现其它零处置行**（其余 86-10 行的处置证据抽核在盘）。
- **F2 十六项计数对账**：两份审计的"16 项"清单逐项枚举均**不等于 16**——SA-DEFECT 版=25 个单元（含 REM-62、R3-06…10 计 5、R5-03…08 计 6），AUDIT-GOAL §5.168 版=24 个单元（无 REM-62）；"16"与任一枚举都对不上（分组折算未披露）。本卡按**全部 25 个单元**逐一处置（上表 C 组 17 条处置行 + C1-C4/C7/C8/C11/C13 交叉引用 8 条 = 25）。已修/已取代 13、闭-今 8（含 2 交叉）、工作卡 5（含 3 交叉）、owner 2（含 1 交叉）、external 1——以逐条行为准，不以合计数为准。

## 变化文件（changes.diff）逐项理由

见 `changes.diff` 头注 J1/J2：仅 2 个注释级修复 × 2 目标。J1=REM-05 行修法原文二选一（注释形态）；J2=F-REV-R5-03 复审给定措辞。皆行为恒等/编译过（判据证据在 evidence\）。**其余一切未修项均超 tiny 界或属 owner/external 位——如实路由，不塞补丁**。

## 汇总节预览（即将追加入 REMEDIATION_REGISTER.md 的单节节标题与首行）

> `## 七十九、【REGISTRY-CLOSURE 处置汇总（AUDIT-GOAL ③ 残留排干：10 零处置行 + 10 隐式行 + 16 登记未修 + REM-78/79 编号注记 + REM-95/96）】2026-09-23 深夜`
> （卡指定代号"七十六"；因父侧 §76–§78 已占用该编号，本节取下一空号——沿用 §35 已登记的"引用带节标题消歧"纪律，避免重蹈 §11–§20 重复编号缺陷。）
> 表体 = 上文 A/B/C/D/E 42 条处置行的压缩版（行号/逐字关键文/class/证据或路由/日期）。

---

## F-R erratum (landing)

> append-only 勘误，carrier-landing 记账追加（2026-09-23/24）；转录独立复核 `reviewer_report.md`（sha256 `b7790be7f3f9d42995790af71f2310b6a06d7193f3951ab8efff5f2cebd78a05`，pin `reviewer_report.sha256`，verdict=§0 L7-14 / findings=§8 L92-101）§8 F-R1..F-R5。本文件既有字节（处置表/预览/规格）一字未改；本节=该次落地对本文件的唯一追加；封存件与登记册零写入。

1. **F-R1（MEDIUM — merge-wave precondition；不拦判定，仅拦 `git apply` 落地路径）** —— 复核原文逐字（§8 表行 F-R1）：「`changes.diff:20` 首文件头 = `#--- a/…` ⇒ 原样 `git apply --check` rc=128。内容已证完全有效（单行修正后 check/apply 双 rc=0 + compile OK×2 + 纯注释 PASS）。｜合并波落地**前置**：应用前把该行改回 `--- `（或走 commands.md 既有"手插"回退）；作为 J1 落地清单第一条。」失败输出逐字（§6）：`error: patch fragment without header at line 22: @@ -284,6 +284,15 @@`（rc=128；根因恰一行 `changes.diff:20 = "#--- a/iso/…"`，而 :39/:58/:72 三个文件头均为裸 `--- ` 正常）。修正=**恰 1 处替换** `#--- `→`--- ` → `--check rc=0` → `apply rc=0` → `py_compile OK ×2`（%TEMP% 镜像内完成，复核实证；纯注释 +11/−2×2、added_non_comment=0/removed_non_comment=0）。**行动 = J1/J2 合并波清单第一条：apply 前先修该 1 行**（或 commands.md 手插回退）；4 hunk 内容本身零改。

2. **F-R2（LOW — stale section numbers）**：本文件 `:120`「汇总节预览」heading 写 `## 七十九、…`、`handoff.md:30` 写「登记册本节号=七十九」；**实际入册 = §八十四**（`commands.md` 步骤 21 正确记「先扫节号（父侧并发至 §83）→ 取空号**八十四**」；§79 已被父侧占用）。两处陈旧引用以本 erratum 立档（erratum-style，append-only）；处置表/封存行零改；登记册本体无须动——heading `## 八十四、…` 恰 1 次（register:1655）、计数行 :1658 与本表三处一致（16/13/11/2/1）、§85/§86 撞号更正在案（:1731/:1741）。

3. **F-R3（INFO）**：F12/C16 物理为**单行双 class**（本文件 `:5` 成因句「F12 拆双轨」与物理行形不完全同构）；class 标签和 43 = 42 行 + 1，计数闭合、无丢行——下游按「行 42 / class 标签 43（F12 双计）」读；无需改表。
   **F-R4（INFO）**：行号引用随父侧并发追加漂移 +1——oracle/decision 引 `register:1311/1312`（REM-95/96），复核实测在 **:1312/:1313**；`register_sha256_at_freeze=468dc316…` 因登记册 append-only **不可事后重算（设计如此，非缺陷）**。下游引用以行文本为锚；无动作。
   **F-R5（INFO）**：`oracle.sha256` sidecar 写于批末（mtime 22:55:22，与 binding 同批，`commands.md` 步骤 20 如实并列记录），晚于内容冻结（`oracle.md` mtime 22:37:42）；**内容冻结先行**已由 mtime + hash 一致性（`16e4f2a0…` 落地复算 MATCH）证明；无动作（下卡可同批钉，惯例提示）。
