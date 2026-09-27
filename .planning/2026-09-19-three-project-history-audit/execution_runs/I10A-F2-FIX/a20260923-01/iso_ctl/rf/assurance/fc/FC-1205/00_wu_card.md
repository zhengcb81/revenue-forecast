# FC-1205 WU 卡片 — 错误和编码一致性（PORT-01~03 关闭）

> 创建 2026-08-13。Owner: 三仓。前置：FC-1204 accepted（registry 依赖）。FCAP Phase 12 最后一个 FC。

## 1. PORT-01 两处机制（预检已定位）

| 站点 | 机制 | 修复 |
|---|---|---|
| wiki `tools/check_unique_test_symbols.py` | 工具打印含中文用户名（郑曾波）的路径，Windows 下子进程 stdout/stderr 按 GBK locale 编码，父测试 utf-8 解码 → UnicodeDecodeError（0xd4/0xa1）——2 个 pre-existing 测试失败 | 工具启动时 `sys.stdout/stderr.reconfigure(encoding="utf-8")`（fetch_filing 先例）；测试保持 utf-8 |
| revenue `tools/audit_baseline.py` | `subprocess.run(text=True)` 无 encoding → locale（GBK）解码 git 的 UTF-8 输出（中文文件名）炸 | `encoding="utf-8", errors="replace"` 两处（_git + version_of）+ 工具自身 stdio reconfigure |

- **PORT-02**：已由 FC-1004 关闭（空格路径 + 安装同步 + UTF-8 链）——本 FC 只做回归验证。
- **PORT-03**：Linux current-triplet golden trace——三仓 CI 均在 ubuntu-latest 运行（quality.yml/ci.yml），CI 绿 = 证据。本地 Windows 不可复现，诚实记录：CI workflow 定义 + GitHub Actions 运行结果为本场景证据（无本地伪造）。
- **worker_bootstrap 10s timing flake**（pre-existing，Windows 随机）：与 PORT-01 无关；本 FC 记录 + 观察，不作为 PORT 修复对象（属环境时序）。

## 2. 统一错误 schema / 日志 redaction 收尾核对（只验证不重写）

- 结构化错误（error_code/stage/retryable）：FC-702/704/filing_contracts 已建；FC-1205 只核对一致，不重写。
- 日志 redaction：wiki observability + policy export 已 redact 绝对路径（FC-701）；核对 worker/scanner 日志无绝对路径泄漏——发现即修，无发现即记录。

## 3. exit gate（Phase 12 汇总）

- forbidden hardcode=0（FC-1201 ratchet 承重）✓、重复 root policy=0（FC-1202）✓、关键 dead helper=0（FC-1203 门）✓、Windows 编码错误=0（本 FC）→ Phase 12 exit gate 全部满足。

## 4. TDD 步骤

1. RED：revenue audit_baseline 测试在干净环境复现失败（GBK 解码）——已复现；wiki 两测试隔离复现（已复现）。
2. GREEN：上述两处修复。
3. 全量：revenue `pytest tests/ tools/tests/` 期望 514 passed/0 failed（PORT-01 首次全绿）；wiki 全量期望 2230+ passed/0 failed（PORT-01 对首次消失，无 PYTHONIOENCODING 环境变量）。
4. MUTATION：M1 移除 wiki 工具 reconfigure → 两测试死；M2 移除 audit_baseline encoding → 测试死。
5. 三仓 CI 定义核对（ubuntu-latest = PORT-03 证据）。
6. schema-2.0 receipt → 独立 reviewer → can_accept → **Phase 12 COMPLETE**。

## 5. 不变式

- 修复在工具自身（child 侧），不改测试预期、不靠 PYTHONIOENCODING 环境规避。
- 零生产数据/写路径变化；worker 无需重启（不动 producer 代码）。
- PORT-03 不伪造本地证据——CI 定义 + 实际运行结果是唯一诚实证据。
