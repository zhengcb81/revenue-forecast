# 弱模型安全实施手册

## 1. 最高优先级规则

1. 一次只执行一个 FC Work Unit（统一编号 `FC-*`）；禁止自建第二套 WU 编号，禁止跨阶段顺手重构。
2. 开始前重读 `task_plan.md`、本手册、`work_unit_registry.md` 和该 FC 的前置回执。
3. 先写 RED 测试并确认失败原因命中目标行为，再改产品代码。
4. 禁止把当前错误行为改写成绿色期望，禁止删测试、skip、xfail 或只降低断言强度。
5. 未获得显式批准不得写生产 catalog、companies、dayu、Dropbox 或调用真实下载。
6. 所有生产操作先在 catalog 副本演练；真实根始终只读，下载只写 canonical companies target。
7. 用户既有 dirty files 不得进入提交、stash、格式化或回滚范围。
8. 每个 FC 一个提交；提交前运行 allowlist diff gate。跨仓 FC 在三个仓库各自一个提交，并由同一 receipt 绑定 result triplet。
9. 实施者不能自我标记 `accepted`；独立 reviewer 必须验证命令、diff、mutation 和回滚。
10. 三次相同阻塞后停止，记录具体证据并请求用户，不得猜测。

## 2. FC 生命周期

```text
pending
 -> preflight_locked
 -> red_proved
 -> implemented
 -> focused_green
 -> repo_green
 -> cross_repo_green
 -> real_readonly_verified（如适用）
 -> rollback_verified（如适用）
 -> independent_review
 -> accepted
```

任何中间状态都不能被汇总为 complete。状态不能手工越级修改；validator 必须验证上一状态证据。`blocked` 必须包含不可自行解决的外部条件和三次不同尝试。

## 3. 每个 FC 的固定 16 步

1. 验证三仓 HEAD 等于该 FC receipt 的 `base_triplet`；读取 `work_unit_registry.md`，确认前置 FC 全部 accepted。
2. 验证工作区 dirty path 只包含已登记的用户文件和计划文件。
3. 获取 FC execution lock；同一 FC、共享 schema、registry、manifest 或 catalog writer 已被占用则停止。
4. 从冻结 command registry 解析命令；命令未登记或 hash 不匹配时不得自行缩减测试，状态为 blocked。
5. 用 CodeGraph 查询目标 symbol 的 callers/callees/impact，记录 production caller 数、预期新增/消失的调用边。
6. 把该 FC 的 scenario IDs 实现为 RED 测试，运行并保存“为什么失败”；若测试意外绿色，先证明是否已有实现或测试无效。
7. 检查 changed-file allowlist、forbidden paths 和最大 diff budget；超出即拆分计划或请求 review。
8. 只实现该 FC 的最小行为；不得同时清理无关代码或迁移下一阶段数据。
9. 跑 focused tests；禁止只跑新测试而不跑关联旧测试。
10. 跑 owner repo 的完整冻结命令和受影响 sibling repo 回归。
11. 跑当前 compatibility triplet 的相关 T1 E2E；适用时运行 T2/T3/T4，真实层未获授权只能 blocked。
12. 执行至少一个错误注入和一个关键 mutation，证明负向路径及核心断言有效。
13. 对生产相关 FC 跑副本数据库演练、root before/after fingerprint、幂等重跑和 rollback。
14. 生成机器可解析 implementer receipt，重新计算所有 hash；关闭 execution lock 前不得修改证据。
15. 独立 reviewer 从干净 checkout 按 `independent_review_protocol.md` 重跑，不信任实施者摘要，并生成独立 receipt。
16. closure validator 合并两份 receipt 并标记 accepted 后，才允许下一个依赖 FC 获取 execution lock。

## 4. WU 卡片模板

```markdown
### FC-NNN：标题
- Owner repo：
- Base triplet：
- Dependency receipts：
- Allowed files：
- Forbidden files/roots：
- Max diff budget：
- Preconditions：
- Production callers before：
- Expected call-edge delta：
- Scenario IDs：
- RED command / expected failure：
- Implementation steps：
- Focused commands：
- Repo commands：
- Cross-repo commands：
- Negative/fault-injection command：
- Mutation：
- Real-data tier：T0/T1/T2/T3/T4
- Side-effect budget：
- Evidence output paths：
- Rollback：
- Acceptance：
- Stop conditions：
```

## 5. Receipt 最小 schema

每个 mandatory FC 必须有合法 JSON；自由文本不能替代以下字段：

```json
{
  "schema_version": "2.0",
  "fc_id": "FC-NNN",
  "status": "independent_review",
  "base_triplet": {"revenue": "40hex", "filing": "40hex", "wiki": "40hex"},
  "result_triplet": {"revenue": "40hex", "filing": "40hex", "wiki": "40hex"},
  "plan_sha256": "64hex",
  "policy_sha256": "64hex-or-not-applicable",
  "allowed_files": [],
  "changed_files": [],
  "dependency_receipts": [],
  "command_registry_sha256": "64hex",
  "scenario_results": [{"id": "EX-01", "status": "passed", "trace_sha256": "64hex"}],
  "commands": [{"command": "...", "exit_code": 0, "output_sha256": "64hex"}],
  "side_effect_counts": {"downloads": 0, "external_root_writes": 0},
  "codegraph": {"production_callers_before": 0, "production_callers_after": 1},
  "mutation": {"id": "M-X", "killed": true},
  "rollback": {"required": true, "proved": true, "trace_sha256": "64hex"},
  "review": {"reviewer": "non-empty", "reviewer_receipt_sha256": "64hex", "decision": "accepted", "reviewed_at": "ISO-8601"}
}
```

工具必须拒绝：短 hash、占位 hash、未来时间、缺失 reviewer、pending decision、命令 exit 非零、triplet 漂移、场景 skip、真实层级过期或 closure ledger 指向不存在文件。

receipt 还必须拒绝：`fc_id` 不在 registry、依赖 receipt 未 accepted、implementer/reviewer 身份相同、changed files 超 allowlist、命令不在冻结 registry、T2 写入生产 catalog/source roots、side-effect counts 超预算、证据路径越出专用目录。

## 6. 测试与命令纪律

### 每仓最低命令

- company-wiki：ruff、compileall、unit、contract、integration、acceptance、coverage、architecture/mutation gates。
- filing-fetch：ruff、compileall、完整 tests（不排除 real tests；按 tier 显式选择）、coverage、isolated E2E。
- revenue-forecast：ruff、compileall、tests/tools tests、coverage、engine E2E、source-preparation cross-repo E2E、mutation。

### 跨仓命令

实施中应新增单一入口，例如：

```text
python tools/cross_repo_assurance.py --triplet compatibility/current.json --tier T1
python tools/cross_repo_assurance.py --triplet compatibility/current.json --tier T2 --read-only
```

命令必须 checkout/验证 manifest 指定的精确三仓 HEAD，不得静默使用 floating main、陈旧 pin 或开发者本机当前目录。

### Command registry 冻结规则

- Phase 1 先记录三仓现有 CI、测试、lint、type、coverage 和 E2E 的真实命令、工作目录、环境变量白名单、timeout、期望退出码与版本 hash。
- FC 卡片只能引用 command ID，不允许实施者临时手写一个更小的“等价命令”。新增或修改命令必须单独 review 并更新 registry hash。
- 测试选择器不得排除 mandatory scenario；`-k`/marker 只能用于 focused 阶段，repo/cross-repo 阶段必须使用 registry 的完整集合。
- 命令结果必须同时保存 stdout/stderr、exit code、duration、selected/collected/passed/skipped 数量。collected 数下降或 unexpected skip 即失败。
- 真实层命令必须显式声明授权 token、目标目录和写预算；没有 token 时命令应在开始前 blocked，不得运行一半后才退出。

## 7. 弱模型常见跑偏拦截

| 跑偏 | 强制拦截 |
|---|---|
| 新 helper 只被测试调用 | CodeGraph production caller gate 失败 |
| 用 root kind 新增特判 | forbidden-pattern architecture gate 失败 |
| 把 Dropbox MISSING 留作绿色 | DBX-01/EX-03 必须失败后再修复 |
| 用 handle 存在推断 download=0 | side-effect journal 对账失败 |
| latest 返回 GAP 就算完成 | LT-08/LT-09 跨进程场景失败 |
| selector 单测代替 artifact 消费 | AR-01 要求 parser/LLM spy 为 0 且 artifact_read>0 |
| 真实样本缺失就 skip | T2 sample registry freshness gate 阻断 |
| 改 CI pin 但未测组合 | triplet manifest trace 缺失即失败 |
| “回滚”只改 dict | CTRL-04 相同 request 响应未改变即失败 |
| reviewer 写字符串“accepted” | receipt validator 验证签名/hash/独立命令 |

## 8. 并行和文件冲突规则

- control-plane schema/flags/resolver WU 串行。
- scanner/adapter 可在不同文件并行，但 registry/config 合并必须由单一 owner。
- latest 与 artifact 可在 resolver contract 冻结后并行。
- CI/E2E 可在产品 contract 冻结后并行，但 scenario IDs 由单一 registry owner 维护。
- 同一 migration、生产 catalog 或 release manifest 任何时刻只允许一个 writer。

## 9. 生产变更停止条件

出现任一情况立即停止并回滚 cohort：

- shadow diff 无法解释；
- active request 缺 policy hash/epoch；
- external root fingerprint 改变；
- duplicate canonical write；
- download 超出 authorization；
- scan errors/interrupted 比率超过冻结阈值；
- p95 resolver/download 超 SLO；
- receipt/trace 无法复现；
- Windows/Linux 输出语义不同；
- 用户 dirty path 被触碰。

## 10. 单上下文交接纪律

- 一个实施会话只处理一个 FC；结束前必须更新 `progress.md`、receipt 和 registry 状态，不给下一会话留下仅存在于对话中的信息。
- 新会话先完成 planning-with-files 五问重启检查，再验证 triplet 和 plan hash；不直接相信前任“已完成”的自然语言。
- FC 因超出上下文、diff budget 或未知依赖而过大时，先在计划中拆成 `FC-NNN-a/b`，补依赖和场景映射，经 reviewer 批准后再实施；禁止暗中拆分或合并提交。
- 任一假设会改变数据模型、权限、写入目标、provider 或用户可见行为时，停止并记录 decision request，不由弱模型自行选择。
