# I-00-D 独立复核（reviewer: 独立，2026-09-19）

## 结论：accepted_scoped

限定申明：本卡仅授予活动指南消歧（company-wiki CLAUDE.md 顶部时代边界横幅、README.md 边界提示）与"退役研究 writer / 不得新增研究型 writer"边界的生效资格；不授予 worker 状态变更资格（desired_state 仍为 paused，改动或 resume 只能在授权窗口按 I-16 卡执行），不构成任何产品行为认证，也不授予同目录既有 dirty 文件（.coverage / coverage.json）任何验收含义。

## 复核证据（独立验证，非转抄 oracle）

1. diff 与当前文件一致：changes.diff 仅含 CLAUDE.md（新增时代边界横幅）与 README.md（新增 2026-09-19 边界提示）；当前文件已含逐字文案（CLAUDE.md:3-9、README.md:128-132）。重算 hash 与 handoff 一致：CLAUDE.md sha256=963869fa…4c23be，README.md sha256=302bd10b…8512。
2. diff 未触碰历史 planning / 收据文件，仅改两个活动指南，符合"只加导航关联、不改原结论"限制。
3. 既有 dirty 与本次改动分离：company-wiki git status 中 CLAUDE.md/README.md 为本次修改，.coverage/coverage.json 为既有 dirty，changes.diff 未纳入。
4. 四问均有指向当前代码/契约的独立依据（见下）。
5. DEPLOYMENT*/OPERATIONS*/使用说明书在 company-wiki 根、filing-fetch 技能根、revenue-forecast 根确实不存在，未为凑齐而创建 — 卡内项 NA 成立，且未发现卡片未列入的相关遗漏文件。

## 四问独立依据

- (a) 唯一入口：company-wiki 最高规范为 AGENTS.md"职责边界"（第 16/18/132/168/185 行），CLAUDE.md 横幅与 README 提示均显式指回 AGENTS.md；filing-fetch / revenue-forecast 技能入口为其各自 SKILL.md。
- (b) 旧研究 writer 退役：AGENTS.md:18 明确历史 Wiki 不得新增研究型 writer，AGENTS.md:132/185 历史 writer 仅解释不作为目标；CLAUDE.md 新增横幅重申"不因本文件存在而重建研究 writer"。
- (c) worker paused / 不得自 resume：.source_catalog/worker_control.json 实测 `desired_state: "paused"`；README.md:128-132 与 CLAUDE.md:8-9 明令代理不得自 resume，恢复仅在授权窗口（I-16 卡）；README、CLAUDE、oracle 均可交叉验证。
- (d) reuse-first：filing-fetch SKILL.md frontmatter description（"Reuses an existing filing if one is already indexed; otherwise, only when explicitly authorized, downloads"）、正文 v1.4.0 reuse-first（第 8-9 行）、Resolve(reuse) 第 3 条（18-19 行，"If found … no download"）、命令默认只读 reuse（60-61 行）四处独立成立；worker 用户暂停永不自动恢复的约定在 Required workflow 第 4 条（20-29 行），与 oracle 所述一致。

## 问题清单（均不阻塞本卡范围）

1. 卡片第 3 条"capture 真实获取日与 as-of 重建边界、schema 版本、review 恢复入口写条件和失败分支；未实现的命令标未实现"未在 attempt 中成文记录：oracle.md 与 open_questions 均未列出哪些入口"未写清/未实现"。当前契约中确有对应内容（filing-fetch SKILL.md: schema 1.1、hard gate "published_date ≤ as_of_date"），但 attempt 未把"已实现/未实现/NA"清点入册，留作文字缺口。
2. 关键未完成绑定横幅已用链接指向后续卡（I-16：resume 窗口；I-01/I-02：下载-恢复断链），卡片文件（card_I-16-A/B、card_I-01-A、card_I-02-A..E）确实存在，属允许做法，但后续卡完成前该边界提示仅为指向承诺，不构成恢复命令的实现认证。
3. minor：handoff.json input_hashes 的 pre-edit hash 为 null，属弱点但不影响复核（git 基线可回溯，本次只读验证未复跑 pre-edit 状态）。
