# 执行矩阵：阶段依赖、授权边界与停线条件

> 本文件是 `task_plan.md` 的执行索引，不替代各工作单元（FC-*）中的详细步骤与验收标准。实施者必须同时阅读 `implementation_runbook.md`、`work_unit_registry.md`、`fc_execution_packet_template.md`、`command_registry_plan.md`、`independent_review_protocol.md`、`dynamic_assurance_plan.md`、`code_quality_plan.md`、`scenario_matrix.md` 和 `architecture_target.md`。

## 1. 使用规则

1. 只能按依赖顺序推进；上游阶段未留下可验证的通过证据，下游不得开始。
2. “测试通过”必须能定位到命令、退出码、日志、输入样本和仓库提交；口头判断不算通过。
3. T2 生产只读测试不得产生写入；T3/T4 涉及真实下载、生产目录或生产数据库写入时，必须逐次取得用户明确授权。
4. 任一阶段发现契约漂移、隐式回退、来源不可解释、非预期写入、测试误跳过或基线不一致，立即停线，回到最近通过的阶段。
5. 阶段放行只表示本阶段通过，不代表六项总目标完成；只有 Phase 15 的完整闭环才能宣告完成。

## 2. 阶段执行矩阵

| 阶段 | 前置条件 | 主责仓库 | 必测层级 | 默认允许生产写入 | 必须交付的结果 | 立即停线条件 |
|---|---|---|---|---|---|---|
| Phase 0 计划与基线 | 无 | 三仓库 | 只读检查 | 否 | 固定三仓库基线、现状证据、目标架构、场景矩阵、执行规则 | 基线与远端不一致；存在未识别的并行修改 |
| Phase 1 契约与治理 | Phase 0 | revenue-forecast 牵头，三仓库共同 | T0 | 否 | 版本化跨仓契约、兼容矩阵、失败语义、证据规范 | 同一字段在三仓定义不一致；旧消费者静默兼容失败 |
| Phase 2 激活、epoch 与回滚控制面 | Phase 1 | company-wiki | T0、T1；经授权后 T4 | 否；生产激活/回滚需授权 | 单一权威激活状态、epoch 钉住、可验证回滚、失败关闭 | 双控制面；读取半旧半新；回滚后结果不可重现 |
| Phase 3 RootPolicy、适配器与扫描解耦 | Phase 2 | company-wiki | T0、T1、T2 | 否 | 新 root 仅靠配置和通用适配器接入；扫描器无 root 名称分支 | 加 root 仍需改 Python；路径名参与业务身份；未知适配器被静默接受 |
| Phase 4 catalog/provenance 迁移 | Phase 3 | company-wiki | T0、T1；生产迁移需授权 | 否；迁移应用需授权 | schema 2.x、来源绑定、幂等迁移、影子校验、回滚证据 | 丢失资产/来源；重复绑定；迁移不可重跑或不可回滚 |
| Phase 5 Dropbox 功能闭环 | Phase 2、3、4 | company-wiki 主责；另两仓消费 | T1、T2、T4 | 否；专用真实样本或目录写入需授权 | Dropbox 被发现、归一化、解析、复用；精确复用零下载；无唯一真实样本时明确阻塞 | 仅“扫描到”但不可解析/复用；以删文件伪造唯一命中；写回 Dropbox |
| Phase 6 companies/dayu 等价接入 | Phase 3、4 | company-wiki | T1、T2 | 否 | companies 与 dayu 经过同一解析面，优先级/去重/冲突规则可解释 | 为某 root 保留隐藏旁路；同一资产选择不稳定 |
| Phase 7 统一 resolver 与跨仓入口 | Phase 1、2、5、6 | 三仓库 | T0、T1、T2 | 否 | 生产调用链真正使用统一 resolver/bundle；精确复用有可观测证据 | 适配器仍无生产调用者；测试专用 API 冒充生产闭环；非法状态可被解析 |
| Phase 8 最新性与受控下载 | Phase 7 | filing-fetch | T0、T1、T3；生产下载需授权 | 否；真实下载需授权 | 精确复用、缺失补齐、过期补齐、下载后再解析；调用次数可审计 | “latest”只靠文件名；已有最新仍下载；失败时静默返回陈旧结果 |
| Phase 9 衍生工件复用 | Phase 4、7 | company-wiki + revenue-forecast | T0、T1、T2 | 否 | md/摘要/分析按源哈希、处理器版本与参数复用；陈旧工件拒绝并解释 | 未绑定工件仍被直接信任；内容变更后缓存未失效；为命中率牺牲正确性 |
| Phase 10 真实场景 E2E 体系 | Phase 5、7、8、9 | 三仓库 | T1、T2、T3；T4 需授权 | 默认否 | 95 个场景按适用层级自动执行并校验副作用；真实层不以 skip 冒充 pass | 只断言返回值；未校验下载/写入/解析/LLM 次数；真实场景长期跳过 |
| Phase 11 动态审核与持续保证 | Phase 10 | revenue-forecast 牵头 | T0、T1、定时 T2；授权后 T4 | 默认否 | PR、夜间、周期、发布前四层动态审核；结果可查询、可阻断、可追责 | 审核仅生成报告不阻断；旧收据可重复放行；基线漂移未报警 |
| Phase 12 硬编码清理与代码质量 | Phase 7、10 | 三仓库 | T0、T1、回归 T2 | 否 | 逐类消除路径/root/provider/schema/测试数据硬编码；复杂度、重复实现、错误语义改善 | 机械“大重写”无行为护栏；配置化后失去校验；删除兼容层前无使用证据 |
| Phase 13 可观测性、健康度与性能 | Phase 7、10 | company-wiki 主责 | T0、T1、T2 | 否 | 扫描健康进入放行条件；查询/扫描/迁移性能基线和预算；结构化追踪 | error/interrupted 扫描仍视为健康；性能退化无预算；日志含敏感路径/内容 |
| Phase 14 渐进发布 | Phase 1–13 全部通过 | 三仓库 | R0–R9，按波次含 T2/T3/T4 | 每次真实动作单独授权 | 影子→小流量→单 root→多 root→全消费者→去旧路径；每波可回滚 | 指标不达标仍扩流；回滚演练失败；用户未授权的生产写入/下载 |
| Phase 15 总验收与关闭 | Phase 14 | 三仓库共同 | 全层级证据汇总 | 仅既定授权范围 | 六项目标逐项为真；收据、哈希、日志、场景、回滚和未决项完整闭合 | 任一目标用推断代替证据；存在 pending/skip/stale receipt；删除遗留前无零调用证明 |

## 3. 工作单元依赖主链

以下是最小主链。并行工作只有在同一行内互不修改共享契约、数据库 schema、公共 fixture 或 CI 门禁时才允许。

```text
FC-101 → FC-102/103/104
FC-201 → FC-202 → FC-203 → FC-204 → FC-205
FC-301 → FC-302 → FC-303 → FC-304 → FC-305
FC-401 → FC-402 → FC-403 → FC-404 → FC-405
FC-501 → FC-502 → FC-503 → FC-504 → FC-505
FC-601 → FC-602 → FC-603 → FC-604
FC-701 → FC-702 → FC-703 → FC-704 → FC-705
FC-801 → FC-802 → FC-803 → FC-804 → FC-805
FC-901 → FC-902 → FC-903 → FC-904 → FC-905 → FC-906
FC-1001 → FC-1002 → FC-1003 → FC-1004 → FC-1005
FC-1101 → FC-1102 → FC-1103 → FC-1104 → FC-1105
FC-1201 → FC-1202 → FC-1203 → FC-1204 → FC-1205
FC-1301 → FC-1302 → FC-1303 → FC-1304
Phase 14 R0 → R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 → R9
FC-1501 → FC-1502 → FC-1503 → FC-1504 → FC-1505
```

跨链硬依赖：

- FC-501 之前必须完成 FC-201、FC-301、FC-401；否则 Dropbox 的“配置接入”只是表面接入。
- FC-701 之前必须完成 FC-501 与 FC-601；否则统一 resolver 无法证明 root 无关。
- FC-801 之前必须完成 FC-701；否则 filing-fetch 仍可能绕过统一 catalog。
- FC-901 之前必须完成 FC-401 与 FC-701；否则衍生工件无法可靠绑定来源和解析结果。
- FC-1001 之前必须完成 FC-501、FC-701、FC-801、FC-901；否则 E2E 只能验证半成品。
- Phase 14 之前必须完成 FC-1105、FC-1205、FC-1304；动态审核、代码质量和运行健康不能在发布后补票。

## 4. 每阶段统一放行包

每个 Phase 结束必须产生一个不可歧义的放行包：

```text
phase_release/
  phase_id
  baseline_triplet.json
  work_unit_receipts/
  executed_scenarios.json
  test_commands.json
  side_effect_ledger.json
  codegraph_impact.json
  unresolved_findings.json
  rollback_evidence.json
  independent_review.json
  release_decision.json
```

`release_decision.json` 只能是 `pass`、`blocked` 或 `fail`。不得使用 `mostly_passed`、`acceptable_risk`、`temporarily_skipped` 等模糊状态替代未完成。

## 5. 弱模型执行检查点

实施者在进入下一阶段前必须逐项回答，并把答案写入放行包：

1. 修改是否仅限本工作单元的文件 allowlist？超出范围是否已经停下并解释？
2. 红灯测试是否先失败，且失败原因正是目标缺陷？
3. 是否执行聚焦测试、仓库全量测试、跨仓测试和本阶段要求的真实层测试？
4. 是否对下载、写入、解析、LLM、缓存读取等副作用做了数值断言？
5. 是否存在 skip、xfail、mock-only、伪造成功、旧收据或短提交哈希？
6. 是否验证失败语义、回滚路径和重复执行的幂等性？
7. 是否由独立审查者从证据重放，而不是接受实现者的结论？
8. 是否仍有任何“代码存在但生产入口不调用”的半成品？

任一答案为“不确定”即按 `blocked` 处理。
