# CI 反复失败根因与根治协议（2026-09-06）

> **2026-09-08活动路由**：本协议作为[R4计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)各阶段适用CI检查及D07的输入，保留真实required/失败/skip纪律。旧“同目录执行手册”是R3历史路由，不再叠加旧95门；不削弱发布所需测试，也不让全业务CI成为纯本地读取的运行门。下方原事件/批准保留，本次没有push、测试、运行或实施授权。

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> 目的：终止"本地绿 → 推送 → CI 红 → 事后补丁"的循环。本页是机制纪律，
> 不是一次性修复。凡推送任何三仓改动，必须走本协议。

## 1. 反复失败模式（实证记录 2026-09-02 ~ 09-06）

| 日期/事件 | 表面失败 | 根因 | 本地为何没拦住 |
|---|---|---|---|
| f2756ea | revenue ruff F601 | `--no-verify` 提交 | 绕过门（纪律） |
| 853dca2 (BR) | wiki 复杂度 ratchet 23>22 | dispatch 内联提升主函数复杂度 | 只跑受影响测试文件，**没跑 FC-1204 ratchet 元测试** |
| 853dca2/0fb7152 | wiki fc906a + extractor 测试 skipped | fixture 依赖无 ORDER BY 首行 fetch；legacy scanner 把 `.source.json` 自身注册为文档；Windows 目录枚举顺序掩盖 | 本地仅 Windows；单文件测试；**OS 差异无防御** |
| 289fb6b (R9) | revenue zr901 字节绑定 | quality.yml 改动未同步 ZR-105 契约哈希 | **不知道 workflow 有字节绑定测试**（改动类型→门面无映射） |
| --run-daily | 定时任务 exit 2 | 注册脚本生成 `--run-daily`，parser 只收位置子命令 | 测试测 parser，**没测注册脚本产物** |
| 0x800710E0 | 补跑被拒 | 默认电源条件 + 关机错过触发 | 非提权不可见（环境） |

## 2. 机制根因（三层）

1. **无 CI 等价推送门**：pre-commit 只有 ruff/mypy/config-doctor；复杂度/覆盖 ratchet、
   字节绑定、manifest 哈希、全契约套件全在 CI 才跑。
2. **改动类型 → 必跑测试无映射**：改 src 不知道要跑 ratchet；改 workflow 不知道有
   绑定测试；改 fixture 不知道有 OS 依赖。
3. **CI 反馈延迟**：push 后无人盯 CI，失败由 owner 报告（数小时~数天），且本机
   Windows ≠ CI Ubuntu（枚举顺序/大小写/行尾差异可掩盖 bug）。

## 3. 改动类型 → 必跑门面矩阵（推送前）

| 改动类型 | 必跑（本机） | 附加 |
|---|---|---|
| 任何改动 | `tools/pre_push_gate.py`（ruff 全树+compileall+unique symbols+mypy 契约集+元测试） | push 后自盯 CI |
| src/ 产品代码（任一仓） | 全契约/全量套件 + FC-1204 复杂度+覆盖 ratchet | — |
| workflow/config/manifest/registry | 字节绑定测试（revenue `test_zr901_pr_fanout.py`、`test_compatibility_manifest.py`）+ 同步契约 sha256 | — |
| 测试 fixture 新增 | **禁止无 WHERE 的首行 fetch**（`SELECT ... FROM documents` 不带 ORDER BY/条件 → 必须显式 `WHERE document_kind=...`）；LF-checkout 克隆（`autocrlf=false`）重跑 | — |
| 注册/调度脚本 | 测试注册脚本**产物**（mock subprocess 断言 Action 字符串），不只测 parser | — |
| workflow/CI 步骤变更（任一仓） | 该仓 `tools/pre_push_gate.py`；改动 doctor/检查步骤时，**同时验证它在 CI 实际布局下可运行**（见 §8） | 环境依赖型检查必须有 CI 侧强制项 |

## 4. 推送协议（每次）

1. 本地：受影响全量 + 元测试 + `pre_push_gate.py` → 全绿
2. `git push`
3. **立即自盯 CI**（GitHub API token 轮询直至 completed）：
   - green → 结束
   - red → 修**根因**；若本门漏掉该失败面 → **扩展本页矩阵与 pre_push_gate**（防再犯），再推
4. 禁止：`--no-verify`、只修表面断言不查根因、push 后不盯 CI

## 5. 环境差异防御

- 本地固定用 **LF checkout**（`git clone --config core.autocrlf=false`）跑契约套件
- fixture 中的文档选择永远显式（WHERE kind/document_id），禁依赖枚举/行序
- CI 矩阵设 `fail-fast: false`（wiki ci.yml）——三版本全跑完，一次暴露全部失败
- 新测试同时考虑 Windows/Linux 目录语义差异

## 6. 待办与执行记录（2026-09-07）

- [x] wiki 修复分支 d92f8bf 合并 → PR #1 merge（master f08116a）；CI #67/#68 全绿
- [x] wiki `ci.yml` matrix 加 `fail-fast: false`（wiki 279fa14；CI #69 三版本全绿）
- [x] wiki 版 pre-push gate `tools/pre_push_gate.py`（ruff 全范围+compileall+config_doctor+复杂度 ratchet+契约测试）
- [x] revenue 版 pre-push gate `tools/pre_push_gate.py`（6682ecf；CI #108 绿）
- [x] **filing 版 pre-push gate**（filing eceae2d）：此前 filing 无任何 CI 等价本地门，推送直达 GitHub；新增 `tools/pre_push_gate.py`（ruff/compileall/import smoke/mypy 契约/unique symbols/全 hermetic 套件/三仓 doctor/install-sync 信息性/plan claims/BOM 扫描）+ `.githooks/pre-push`（`#!/bin/sh`）+ `core.hooksPath=.githooks` + `/.githooks/** eol=lf`；`.githooks/pre-commit` 换为 pre-commit 框架 wrapper（旧自定义脚本未被 core.hooksPath 启用过）
- [x] **filing CI #42 环境依赖型检查根治**（filing 8660ac2，见 §8）
- [x] **覆盖率 ratchet 根治**（4beb38d）：删除结构性不可达代码（_classify_broker return None 与 role-None continue——正则与分类器共用同一 keyword dict，正则匹配的标题必然分类成功，实证验证）+ 补 _extract_sections_for_kind dispatch 双向测试 → section_extractor 覆盖率 86%→88%，基线 87% 保持不降。
- [ ] 两仓 README/planning 指向本协议
- [ ] 三仓完整验证闭环（全量回归 + 自盯 CI）

## 7. 生效范围

本协议适用于 revenue-forecast / company-wiki / filing-fetch 三仓的任何推送
（代码、配置、workflow、文档），由实施 agent 与 owner 共同执行。

## 8. 新增根因类：环境依赖型检查（2026-09-08，filing CI #42）

**现象**：filing-fetch CI #42（33d8b46）红在 `Config doctor (FC-1202)`：

```
CONFIG-PROBLEM: revenue config filing_fetch_root lacks scripts/fetch_filing.py:
/home/runner/Projects/filing-fetch
```

该提交只改 PLANNING_STATUS.md，与失败无关；#41（89c8bdb）同一步骤为绿，
故不是"改坏了"，而是**检查的激活条件变了**。

**根因链（环境依赖型检查）**：

1. `filing-fetch/tools/config_doctor.py` 的 revenue 检查**只在被检出的 revenue
   checkout 携带 `config/filing_fetch.json` 时才运行**（否则只打 NOTE 并跳过）；
2. #41 时 CI 检出的 revenue pin = `1b41d62`（早于 b34097d 引入该配置）→ 检查
   静默降级为 NOTE，CI 绿但**三仓检查实际没跑**；
3. 2026-09-03 pin 刷新（`5489acb` → revenue `599e057`，含该配置）→ 检查被激活；
4. 但 CI 用 `ci_checkout_siblings.py ... --skip filing` 跳过本仓，
   `$HOME/Projects/filing-fetch` 从未创建，而 revenue 配置正指向
   `${USER_PROFILE}/Projects/filing-fetch` → 环境不满足即红。

**根治**（filing 8660ac2 + eceae2d）：

- `quality.yml` 在 doctor 之前把 `$GITHUB_WORKSPACE` 符号链接到
  `$HOME/Projects/filing-fetch`：复刻本地布局，且校验的是**被测代码**本身；
- `config_doctor.py` 新增 `--require-revenue-config`（CI 使用）：revenue 缺配置
  由 NOTE 变 PROBLEM，检查**不可能再静默退化**；
- 失败文案点名 `CI must materialize it`，下次直接指向修法；
- 4 个回归测试同时固化"CI 布局成立"与"#42 失败签名"；
- filing 补齐 CI 等价 pre-push gate（§6），使该仓失败不再由 CI 首先发现。

**本类教训（可复用规则）**：任何"仅在特定检出/环境满足时才运行"的检查，都必须
配一个 CI 侧强制项；否则它会在 pin/环境变动时从"静默跳过"突然变成"环境不满足
即红"，看起来像回归，实则从未真正执行过。
