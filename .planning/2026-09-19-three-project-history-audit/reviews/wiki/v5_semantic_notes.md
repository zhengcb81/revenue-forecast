# v5 独立语义复审工作底稿

> 阶段性工作底稿，以下 pending/候选反映当时进度。全部后续 closure 和旧版本现已完成阅读，最终结论及修正见 [review.md](review.md)、[item_ledger.jsonl](item_ledger.jsonl)。保留原轨迹，不把它作为当前未完成清单。

仅复审规划及历史证据；当前未实施 v5 的 315 测试与 115 节点，不以缺少实施当产品 bug。

## 已独立核验

- `readonly_diagnostics.json`：51 个规范文件当前字节与冻结 manifest 一致。历史 9,188 checks 是当时 checker 的合同完整性结果，不是 9,188 个生产能力测试。
- `plan_structure_checks.json`：115 节点唯一、无悬空前驱、无环，reviewer 人数与 role 数一致，OP 唯一映射；315 测试均唯一、引用合法节点/族、条件分支并集合致，均有正文出处。该脚本未判语义充分性。
- 已逐行读完 `plan_lifecycles_for_review.md` 全部 315 生命周期；完整阅读 baseline/plan 的 task_plan、acceptance_thresholds、gate_state_machine、test_acceptance_plan、ledger_validator_contract、traceability_matrix、plan_review_findings。其余文档和历史关闭记录仍在审。
- 计划设计覆盖 SQL 独立 oracle/规模性能、per-root checkpoint、长 SQL pause、持久失败预算、真实格式 parser、LLM 当前源绑定和未知计费、显式迁移、逐阶段真实 canary、长期运行合同；这些较常见的“单元测试全绿替代上线”问题在计划正文中已有明确防线。不能把此前生产失败全部归因于计划没有提及。

## 新发现候选：具名关卡要求未进入逐 ID 注册表

`baseline/plan/test_acceptance_plan.md:609` 明定 G11J 两 reviewer 验证 WRITE-F01/WRITE-F02；`traceability_matrix.md:105` 的 RQ-056 同样把两项映射 D11J/G11J/G10R。当前 `test_id_registry.v4.json:4352,4377` 两项 revalidate 列表却只有 G11B-A2/A3/BP/BFnn 与 G12A，未含 G11J/G10R。正文 :5 指明注册表是稳定测试唯一来源、:45-46 要机械展开精确生命周期；:227 规定 prose 与 registry 不一致 fail closed。

独立判断：这是规划阶段的同步遗漏，尚须检查最新 closure 是否明确替代该义务。不能据此声称已经发生生产 journal 故障；也不能只凭 315 个 ID 都合法就确认全部关卡覆盖。应将正文具名 Gate×Test 关系与机器注册表按语义核对，不只是查 token 是否存在。JRN-S01/02/03 虽独立覆盖 journal 合同，但文档没有声明它们替代 WRITE-F01/02 的 G11J 崩溃注入。

## 历史审查需保留的边界

`plan_review_findings.md` 保留 v1/v2/v3 三路 FAIL，105 个 PR 项为修订者 addressed/pending 记录；不能摘取“addressed”即作 CLOSED。后续 v5 closure 需逐项映射冻结版本与领域 reviewer，尤其 PR-070 的精确逐 ID 生命周期以及 PR-102 的 G11J 稳定义务。
