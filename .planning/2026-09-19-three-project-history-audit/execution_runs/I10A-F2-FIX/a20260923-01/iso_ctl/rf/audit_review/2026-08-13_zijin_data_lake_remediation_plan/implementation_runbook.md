# 弱模型安全实施与审查手册

> 本手册是未来实施者的强制流程。本轮不执行其中命令。

## 1. 状态与单元

唯一工作单元编号为 `ZR-*`。生命周期：

```text
pending
 -> preflight_locked
 -> drift_classified
 -> red_proved
 -> implemented
 -> focused_green
 -> owner_repo_green
 -> triplet_green
 -> real_tier_green（适用时）
 -> rollback_green（适用时）
 -> independent_review
 -> accepted
```

- 只有 closure validator 可写 `accepted`；实施者最多到 `independent_review`。
- “代码看起来已有”不能直接 completed：先运行本单元 mandatory tests。若全部当前即绿色且 mutation/fault oracle 有效，生成 `already_satisfied` receipt，再由 reviewer accepted。
- blocked 不能用 skip/xfail 替代；必须给外部条件、三次不同尝试、owner 和解除条件。

## 2. planning-with-files 并发纪律

- 一个任务使用一个唯一计划目录；不得编辑其他任务计划来同步状态。
- 每次写计划/registry/receipt 前保存目标 `path + size + mtime + SHA256`；提交补丁前再次检查。
- hash 变化即释放工作单元锁、记录 `concurrent_plan_write`，重新读取并三方合并；禁止整文件覆盖。
- scenario registry、command registry、contract schema、migration journal、release manifest 各自单 writer；不同代码文件可以并行，但合并点串行。
- 子 agent 默认只读；需要写时必须分配互不重叠的文件 allowlist。

## 3. 每个 ZR 工作单元固定 20 步

1. 重读本计划 `task_plan.md`、本手册、`work_unit_registry.md`、前置 receipts。
2. 运行五问重启检查：目标、当前 phase、已知事实、剩余任务、证据位置。
3. 冻结三个 40 位 HEAD、branch、dirty allowlist、plan/registry/command hashes；验证没有 floating sibling。
4. 获取工作单元和共享资源锁；锁持有者、TTL、base triplet 写入 preflight。
5. 对照最新代码做 plan-drift：`still_missing / already_satisfied_candidate / superseded / blocked`。
6. 用 CodeGraph context/impact/callers 固化生产可达性；literal/文档查询才使用 `rg`。
7. 声明 allowed files、forbidden files/roots、最大 diff/复杂度预算、side-effect budget。
8. 从 scenario registry 生成或选择 RED；确认失败是目标行为而非环境/fixture/语法错误。
9. 加至少一个正例、一个负例；关键安全/复用任务另加故障注入和 mutation。
10. 独立 oracle 先于实现：事件 journal、hash、row count、root fingerprint、registry before/after。
11. 只实现本单元最小行为；禁止顺手清理、跨 phase schema、降低断言、删/skip/xfail 测试。
12. focused tests；然后关联旧测试，确认没有把旧正确行为改成新错误期望。
13. owner repo 冻结命令：format/lint/type/compile/unit/contract/integration/coverage/complexity。
14. affected sibling repos 和 current-triplet T1；三进程 trace 必须出现三个实际进程边界。
15. 适用时 T2/T3/T4；没有授权则在执行前 blocked，不能部分运行后伪 pass。
16. 重放 fault、critical mutation、幂等第二次调用和 concurrency race。
17. 有数据/路由变化时执行副本 dry-run→shadow diff→apply/rollback 演练；生产根零写指纹。
18. 生成 implementer receipt，包含完整命令、collected/passed/skipped、duration、stdout/stderr hash、事件账本。
19. 独立 reviewer 在干净 checkout/worktree 重放，不读取实施者未入 receipt 的临时文件。
20. closure validator 检查依赖、triplet、场景、新鲜度、diff、mutation、rollback 后标 accepted；随后才能解锁下一个依赖单元。

## 4. 工作单元卡片必填模板

```markdown
### ZR-NNN：标题
- Objective / non-goals：
- Owner repo / collaborating repos：
- Base triplet / plan hash：
- Dependencies / decision records：
- Current-state drift verdict：
- Allowed files / forbidden files and roots：
- Max diff / complexity budget：
- Production callers before / expected edge delta：
- Contract/schema compatibility：
- Scenario IDs / real tier：
- RED command and exact expected failure：
- Independent oracle：
- Atomic implementation steps：
- Focused / owner / sibling / triplet commands：
- Negative / fault / mutation / race：
- Side-effect budget：
- Migration, idempotence and rollback：
- Evidence paths：
- Acceptance criteria：
- Stop conditions / handoff notes：
```

任何字段空白都不能进入 `red_proved`。

## 5. 测试阶梯与不可替代性

| 层 | 内容 | 不可替代规则 |
|---|---|---|
| T0 | unit、schema、pure contract、property | 不能证明跨仓接线 |
| T1 | 临时三 roots、真实三进程、provider/LLM 边界 spy | 必须从 revenue 用户入口；单 helper 不算 E2E |
| T2 | 真实 catalog/companies/dayu/Dropbox，只读 | T1 不能替代；每个 root 有 unique sample |
| T3 | 真实 provider、临时 wiki、首次下载+二次零下载 | 网络/凭据缺失是 blocked，不是 pass |
| T4 | 经授权生产最小 cohort | 必须 before/apply/after/rollback/restored |

每个层级单独 receipt。`T1/T2` 场景不能因 T1 绿而自动把 T2 标绿。

## 6. 独立 oracle 与副作用账本

必须记录：

- `identity/resolve/freshness/safety/artifact/semantic/consumer` 阶段结果；
- provider discover/fetch、canonical/external-root writes；
- parser/LLM calls 按 role；artifact reads 按 role；
- processing demand enqueue/dedupe/complete；
- DB schema/data writes、migration batches、lock waits；
- publication registry writes；
- root before/after file count、bytes、mtime/hash set；
- output/trace/receipt hashes。

计数只能来自 spy/journal/OS fingerprint；不得写 `0 if returned_handle else 1` 一类推断。

## 7. 弱模型禁止动作

| 跑偏 | 硬拦截 |
|---|---|
| 在 resolver 新增 `if Dropbox/dayu/companies` | AST forbidden-pattern gate |
| 给 CatalogStore 加布尔 read_only 但仍调用 initialize | READ mutation + OS read-only E2E |
| `except Exception` 把锁全部改 retryable | error taxonomy contract + non-lock fatal cases |
| 用文件名直接确认研报实体/日期 | BR identity negative cases |
| 把 PDF 转纯文本后称表格保真 | table row/column/footnote golden oracle |
| 把资源量写成储量或再次乘权益 | MINE basis/invariant tests |
| 用产量×价格直接称逐矿收入 | accounting-bridge reconciliation gate |
| 2028目标支撑2030参数 | temporal coverage mutation |
| generator 只通过 linter | REV real-engine compile/run gate |
| validate-only 运行 formal 再回滚文件 | before/after write syscall/registry gate |
| 测试 import 真实 sibling/用户目录 | AST + sandbox denial collection gate |
| 真实样本缺失改为 skip | sample registry gate returns blocked |
| reviewer 复用实施者工作树或摘要 | clean checkout + identity receipt gate |

## 8. 计划漂移与旧完成项处理

- 当前行为已经满足：保留 regression tests，生成 `already_satisfied` 证据，取消产品改动但不取消门禁。
- 实现被更好方案替代：标 `superseded`，说明替代单元/场景；旧任务不直接删除。
- 仅文档/行号过时：更新 locator，目标不变。
- 目标已不再需要：必须有架构决策记录证明用户目标仍全部覆盖，方可 cancel/deprioritize。
- 任何旧 accepted receipt 若 current triplet 用户旅程失败，只能作为历史证据，不能豁免重验。

## 9. 独立审查

Reviewer 必须：

1. 验证干净 checkout、准确 result triplet 和 plan/registry hashes；
2. 重算 CodeGraph reachability/impact；
3. 读取 RED 首败并确认 oracle 有效；
4. 重跑所有 mandatory 命令与 fault/mutation；
5. 检查 diff allowlist、旁路、硬编码、测试孤岛和计数伪造；
6. 对账真实 side effects 与授权；
7. 对迁移/路由执行同一 request 的 before→after→rollback→restored；
8. 只给 `accepted / changes_required / blocked / rejected`；不能帮实施者改代码后直接批准。

## 10. 立即停线条件

- 未授权 provider fetch、生产 catalog 写入或外部 root 写入；
- root fingerprint 变化、重复 canonical commit、错误实体/期间复用；
- source/hash/provenance 冲突被静默吞并；
- migration 无 journal/rollback 或 batch integrity 失败；
- mandatory test collected 数下降、出现 skip/xfail/expected-failure；
- shadow diff 无法逐条解释；
- p95/p99 或锁等待超过冻结预算；
- plan/registry/receipt 被并发修改；
- 用户 dirty file 被纳入 diff；
- 需要改变权限、数据模型、下载目标或用户可见语义但没有 decision record。

## 11. 完成声明格式

单元或 phase 的完成信息必须回答：

- 哪个用户目标被推进；
- 哪个真实失败先变红、后变绿；
- current triplet 与证据 hashes；
- 正/负/故障/mutation/真实层结果；
- side effects 和 rollback；
- 尚存 data gaps 与动态证据新鲜期。

禁止用“测试都通过”“代码已重构”“reviewer accepted”替代上述事实。
