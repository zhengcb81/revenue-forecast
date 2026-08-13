# CA-002 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。
> 全部实验只读或 scratch；产品代码、catalog、roots 零写。

## RED-A：current triplet 精确性无人验证——旧 gate 只查 ancestry

**目标缺陷**：验收应基于"精确 current triplet"；旧工具只验证 HEAD 是冻结 baseline
的后代，任何新组合都能过，且陈旧 pin 无人检测。

**证据（2026-08-13 实测）**：

| 事实 | 值 |
|---|---|
| compatibility/current.json pin revenue | `1b41d62f…`（2026-08-09 冻结） |
| 实际 revenue HEAD | `0815522a…`（含 CA-001 五笔提交） |
| pin filing / wiki | `592fae6…` / `f6eb584…`（均非当前 HEAD） |
| closure_gate 是否引用 current_triplet | **NO**（源码只读 `frozen_baseline_triplet`，行 99-107：`git merge-base --is-ancestor base HEAD`） |
| closure_gate --json 的 problems 中 triplet 相关项 | 无（三仓 HEAD 是旧 baseline 后代 → 绿，即使 pin 与实际全不符） |

**结论**：manifest pin 陈旧、sibling HEAD 改变均不被检出——`baseline descendant` 逻辑
放行任何新组合，违反 CA-002 验收"精确 equality gate"。

## RED-B：upstream 未设置、dirty 未登记，无任何环境冻结工具

**证据（2026-08-13 实测）**：

| 事实 | 值 |
|---|---|
| 三仓 fcap 的 upstream | 均无（`git rev-parse @{u}` 报 no upstream；origin 存在但未跟踪） |
| dirty 文件登记账本 | 不存在（revenue 7、filing 0、wiki 4 项仅存在于 git status，无机器账本） |
| 环境冻结工具（tools/ 全量盘点） | 不存在——`tools/` 无 triplet/upstream/dirty/toolchain/skills/config/catalog 指纹采集与 equality gate |
| compatibility/current.json 维护方式 | 手工静态 JSON，current_triplet 已陈旧三仓 |

**结论**：无 upstream、dirty 未登记、环境漂移均不可能被机器检测。

## 新工具对照（本卡实现）

`uc.cli env-freeze` 采集：三仓 40 位 HEAD/branch/upstream/remote_url/remote_ref_sha/
push_state/dirty allowlist、toolchain（python/git/node/sqlite3）、OS、21 个已安装
skills 的 SKILL.md hash、三仓 config 文件指纹、runtime_policy.json 指纹、catalog
（49.6GB）size/mtime/page1/schema hash 只读指纹；`env-verify` 做**精确 equality**
（任何字段漂移 → rc=1，不做 ancestor 判定）。local_only/pushed/unverifiable 三态
可验证分类；git dubious-ownership 分类为 infra_error（不伪装 ancestry failure）。

真实冻结：`assurance/unified_completion/environment/env_freeze.json`（sha256
`60919481…`），冻结后立即 env-verify = OK；测试覆盖每字段漂移检测（head 前移/
后移、dirty 增加、branch/upstream 变化、toolchain/skills/config/catalog 篡改）、
push_state 三态、infra 分类、freeze 幂等与 CAS 替换（`tests/test_envfreeze.py`，
12 个测试）。
