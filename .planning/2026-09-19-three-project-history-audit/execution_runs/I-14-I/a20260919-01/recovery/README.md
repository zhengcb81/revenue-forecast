# recovery/ — 恢复规则与实测回退（I-14-I）

## 卡片规定的恢复动作

> 恢复：回退 `:202` 类型护栏与派生字段改动；保留本次全 14-case 门落盘报告与
> I-14-H 的 xfail 原始记录（作为"修复前确实过不了"的证据）。

本 attempt 的起点就是**字节可复现**的：`before/natural_window.i14b-after-2.py`
（sha256 `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`）
即修复前的 `iso/natural_window.py`。回退 = 把该文件复制回 `iso/`。

为免"回退后是否真能复现修复前状态"只靠自述，本轮**已实测**：`before/natural_window.i14b-after-2.py`
被直接当作 SUT 跑完整 rider 套件，得到 25 failed / 20 passed（rc 1），
其中含 list/dict 的容器行以 `TypeError` 失败、5 个派生键用例以 `AssertionError` 失败
（见 `before/CMD-I14I-RED-SUITE-PREFIX/stdout.txt`）。即回退目标件本身**仍带有**本卡所修的两个缺陷，
回退可用且被验证过。

## 回退清单（本卡引入的全部改动）

改动只有 4 个 hunk，全部在 `iso/natural_window.py`（见 `changes.diff`）：

| # | 位置（修复后行号） | 改动 | 回退 |
|---|---|---|---|
| 1 | 模块 docstring `:29-66` | 增加 J16b 说明与 r3 变更说明 | 恢复原 docstring 段 |
| 2 | `:113-145` | 新增 `_basis_kind()` / `_basis_repr()` 两个 helper | 删除 |
| 3 | `:255`（原 `:202`） | `if basis not in BASIS_REGISTRY:` → `if basis_kind != "str" or basis not in BASIS_REGISTRY:` | 恢复原单条件 |
| 4 | `:296,301-307`（原 `:241,246-248`） | 两个键改为派生；`basis` 改经 `_basis_repr`；新增 `basis_kind` | 恢复 `False` 字面量与裸 `basis` 回填 |

**未改动**：`SUT_VERSION`、任何判定（J1–J16）的语义、`BASIS_REGISTRY` 成员、
`main()` 的 rc 约定、CLI 参数。

## 不得随回退删掉的证据

- `after/CMD-I14I-GATE-CASES14/gate/cases_report.json`（rc 0，mismatch 0）
  及其在 `I-14-H/a20260919-01/evidence/I-14-I/` 的落盘副本；
- I-14-H 的 xfail 原始记录：`harness/archive_test_i14h_original.py`
  （sha256 `147cdc1c…`，与 I-14-H 的 `test_i14h_natural_window.py` 字节相同）
  及其在修复版上的 XPASS 证据 `after/CMD-I14I-GREEN-I14HSUITE/stdout.txt`；
- `before/` 全部原始输出（修复前确实过不了）。

## 异常恢复

本卡处理的被测物是**纯函数**（无 I/O、无状态、无并发、无锁、无持久化）：
`classify()` 只吃 case dict、吐 verdict dict。故"崩溃后重启/重试/最终持久化"
一类检查**不适用（NA）**，理由是纯函数无中间状态可残留；
卡片允许"纯函数可说明 NA"（`review_and_handoff.md` 最小目录注释）。

唯一有 I/O 的环节是 CLI 写报告文件。本卡在其上发现并修掉了一个真实缺陷：
`basis` 为 `set` 时 `json.dumps(report)` 抛 `TypeError`，即**裁决已定但报告写不出来**。
修复后 `computed` 的 `basis` 字段只可能是字符串或 `null`（`_basis_repr`），
并由 `test_container_basis_does_not_break_report_serialisation[set]` 与
`harness/audit_postfix.py` 的"报告整体可 JSON 往返"检查**双重**钉住。

## 隔离

全部写入限于 `execution_runs/I-14-I/a20260919-01/**`，外加卡片明示的落盘目标
`execution_runs/I-14-H/a20260919-01/evidence/I-14-I/**`（新增子目录，未改 I-14-H 既有文件）。
未创建 venv。生产树只读（`scripts/` 的 `git status --porcelain` 为 0 字节）。
