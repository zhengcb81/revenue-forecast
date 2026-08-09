# 计划结构自审

- `task_plan.md` 定义 16 个阶段：Phase 0 仅完成计划与基线固化，Phase 1–15 全部保持待实施。
- 计划拆分 71 个 FC 工作单元；实施时每单元均须有责任仓库、前置条件、红灯测试、变更边界、测试层级、证据、回滚和独立复核。
- `scenario_matrix.md` 定义 95 个强制场景，覆盖精确复用、Dropbox、缺失下载、最新性、衍生工件、安全失败、控制面、运维、Windows 中文路径、index/文件生命周期、组合用户旅程、动态审核自证和迁移恢复。
- `execution_matrix.md` 明确每阶段的主责、依赖、授权边界、必测层级、交付物和立即停线条件，防止跳阶段或把半成品当成完成品。
- 六项目标均映射到专门阶段和 Phase 15 终局验收；任何 `pending`、真实层 `skip`、陈旧收据、短哈希、仅 mock 证据或未解释的生产旁路都会阻止关闭。
- `work_unit_registry.md` 对 71 个 FC 逐项登记 owner、依赖、主测试和出口证据；`command_registry_plan.md` 禁止实施者自行缩减“完整测试”；`independent_review_protocol.md` 禁止自我验收。
- `fc_execution_packet_template.md` 将每个 FC 固定为 preflight→RED→变更合同→分层测试→副作用对账→回滚→双回执→机器关闭；`dynamic_assurance_plan.md` 和 `code_quality_plan.md` 分别细化目标 4 与目标 6。
- 本轮只创建和更新审计计划文档，没有修改三个仓库的产品代码、运行配置、数据库、CI 或测试实现。
- r2 初版机器校验：14 份计划文档、16 个 Phase、71 个 FC、95 个唯一场景；主计划与 FC registry 集合完全相等，内部 Markdown 链接无缺失。
- 历史计划对账后新增 `legacy_plan_disposition.md`；旧项目已分类为 historical complete、superseded、cancelled、deprioritized 或 archived，当前只保留 r2 一个实施队列。
- 当前计划文件数为 15；最终交付前须重新运行链接、FC、scenario、空框处置和三仓 diff 校验。
