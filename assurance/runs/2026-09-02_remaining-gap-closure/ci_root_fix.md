# CI 反复失败根因与根治协议（2026-09-06）

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
- [x] **覆盖率 ratchet 根治**（4beb38d）：删除结构性不可达代码（_classify_broker return None 与 role-None continue——正则与分类器共用同一 keyword dict，正则匹配的标题必然分类成功，实证验证）+ 补 _extract_sections_for_kind dispatch 双向测试 → section_extractor 覆盖率 86%→88%，基线 87% 保持不降。
- [ ] 两仓 README/planning 指向本协议
- [ ] 三仓完整验证闭环（全量回归 + 自盯 CI）

## 7. 生效范围

本协议适用于 revenue-forecast / company-wiki / filing-fetch 三仓的任何推送
（代码、配置、workflow、文档），由实施 agent 与 owner 共同执行。
