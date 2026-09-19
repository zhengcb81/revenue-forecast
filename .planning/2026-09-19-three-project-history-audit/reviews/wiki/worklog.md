# company-wiki 独立历史审计

## 2026-09-19：范围与状态

只读审计，未运行历史修复指令，未改变产品、配置、数据库、worker、raw。写入范围为本目录。根代理维护共享计划。

初版 inventory/company-wiki.json：发现 8,452 个 Markdown，选中 373 个，其中 web/docs 130 个为业务正文候选，须由总 scope manifest 明确排除。工程主线包括 v5 recovery 46 文件/11,728 行、旧 worker recovery 15/6,616、painpoint 32/3,478、planning-sync 13/1,432、FC assurance 29/2,164。根 task_plan 4,417 行，另有早期根计划/日志和 archive。数值为文件清单计数，绝不是已审查比例。

使用 planning-with-files 技能并显式解析本任务 PLAN_ID；CodeGraph 状态为 543 文件、10,545 节点。原审计目录冻结，不修改；仅引用其证据。

当前优先：v5 冻结/交接/worker 恢复承诺与实际生产接线。其 task_plan 已明确 V5-2 是未来实施输入，不授权 worker 恢复；数千 checker checks 不能被解释成产品已部署。任务页顶部 9/8 检查点仍称 V5-1/2/3 未完成，下面 9/9 三阶段已完成，存在时间切片并列，需依时间解释而非把旧段落当当前状态。

## 待分簇复审（不是完成）

- 根计划、早期 CW 与 docs/archive：根 task_plan、task_plan_cw_recovery_20260725、log 等逐承诺重建。
- painpoint/R4/FC assurance：验收范围、真实 outcome 与停用能力之间的继承。
- portfolio reuse/core extraction/catalog space/ADR/contracts：专项承诺与部署证据。
- v5 baseline 内容自身还有大量细项待逐条审；首先验证“冻结完整性”与“产品通过”是否混同。

任何尚未人工审阅的文件/条目均保留 pending，不用关键词数量冒充覆盖。

## 第一个证据检查点

- 已逐行读完 v5 baseline task_plan.md 829 行及 acceptance_thresholds.md 336 行；接下来将同义重复约束映射到独立承诺，再检查 DAG/315 个稳定测试 ID 的规划作用，不把它们视为已运行测试。
- 核心计划对性能分母、source rotation、取消 generation、LLM 不确定重试、分阶段 canary、zero-DDL、注册表并发和读写集合已提出具体合同；全部实施阶段总表仍 pending。因当前审计尚未验证每个能力的产品实现，不能把这些计划设计直接作生产符合性结论。
- 独立 hash 核验 51/51 冻结项一致；config doctor 真实 exit0/healthy，却漏检 runtime policy/root adapter 组合。三份生产控制/config 文件前后 SHA 相同。首次自写诊断脚本仅stdout GBK编码失败，输出证据已写；将子进程输出显式UTF-8后重跑成功，没有产品修改。
- 历史 GP002 同commit中测试人为配置adapter而生产未迁移；progress在生产日志待验证时关闭。已保存历史 Git blob 原文于 readonly_diagnostics.json。
- 21条手工ledger已形成，根/CW/archive及四专项已移交history_filing，painpoint/R4/FC由root负责。

- 本轮已读315生命周期映射全表与DAG剩余尾部；完整读traceability_matrix、plan_review_findings。独立结构检查115/315无结构错误；语义新候选WRITE-F01/02 G11J映射缺口记录于v5_semantic_notes，待核closure，不提前认定产品事故。

## 最终阅读完成及自我更正

已完成分区 103 份 Markdown 全文覆盖（87 直接读、15 全文版本映射、1 相同调查文本映射），另污染清单工程部分、1 raw/news 排除。v5 的 315 tests/115 nodes/RQ60/RK44/PR105 逐项规划语义审查完成；历史 91 concerns/173 状态保留。补充 43 工程路径形成 379 条记录，全部账本 1,263 条。不是运行测试总数。

更正此前“历史Git blob保存在readonly_diagnostics.json”：该 JSON 的 git 命令均 exit128；后来工具阅读没有可靠独立落盘证据，现新增 `historical_git_readonly.json`，单命令 safe.directory 参数、三次 exit0，配置与测试原文已核，原失败记录未覆盖。O1参数修复改判 supported_scoped，不用整个注册链失败否认其局部效果。完整范围、结果和限度见 review.md / read_coverage.json / ledger_validation.json。
