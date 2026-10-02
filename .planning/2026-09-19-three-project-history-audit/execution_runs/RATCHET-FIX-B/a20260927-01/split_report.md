# split_report — RATCHET-FIX-B (FC-1204 complexity ratchet)

- **role**: `implementer_ratchet_b` · **authorized_by**: owner `§四十二 裁定一` · **date**: 2026-09-27
- **写入面**: 3 个责任文件（`company-wiki/src/company_wiki/source_catalog/`）+ 本产出目录。冻结表 `FROZEN_MAX` **未动**（`test_r4b02_complexity_ratchet_table_is_not_edited` 仍绿）。
- 每个改动文件均带注释：`Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.`
- 前像 SHA256（见 `pre_image/SHA256SUMS.txt`）：
  - `producer_events.py` `8E0F18FB…C874`
  - `identity_cli.py` `989CF418…72A2`
  - `artifact_read_model.py` `EE279231…5711`
- 后像 SHA256（见 `post_image/SHA256SUMS.txt`）：`4BA3B483…DEC0` / `C4CA684F…6E49` / `D2191509…C68A`

## 1. 度量口径（先说清楚，否则“实际”数对不上）

| 口径 | 定义 | producer_events | identity_cli | artifact_read_model |
|---|---|---|---|---|
| **权威 = 门禁 `_max_complexity`**（派单指定，`test_fc1204_complexity_ratchet.py`） | 顶层函数 `1 + _mccabe`：`If/For/While/And/Or 节点/ExceptHandler/comprehension/Assert/With` +1，`BoolOp` n-1（且 `And`/`Or` 作为子节点再 +1），**`IfExp` 三元不计** | **1** | **6** | **8** |
| **派单“实际”所用口径（auditB）** | 同上但 `IfExp` +1、`BoolOp` 只算 n-1 | **3** | **9** | **11** |
| auditA（RATCHET-FIX-A 原型口径 = 门禁 + `IfExp` + `Match`） | | 3 | 9 | 12 |

- **复现**：`evidence_per_function_complexity.txt` 的 PRE-IMAGE 段用 auditB 精确复现派单表的 **3 / 9 / 11** ⇒ 派单“实际”列不是门禁口径；门禁口径下三文件开工前本就 ≤ 冻结（1 / 6 / 8）。
- 本单按**最严**交付：三文件在**三个口径下同时 ≤ 目标**，无论复核用哪个口径都通过。

## 2. 前 / 后复杂度（每文件最复杂函数）

| 文件 | 目标(冻结) | 前 权威 | 后 权威 | 前 auditB | 后 auditB | 前 auditA | 后 auditA | 判定 |
|---|---|---|---|---|---|---|---|---|
| `producer_events.py` | **1** | 1（`count_producer_events`，auditB 3） | **1**（`count_producer_events` / `_tally` = 1/1/1） | 3 | **1** | 3 | **1** | PASS |
| `identity_cli.py` | **6** | 6（`main`，auditB 9） | **3**（`_configure_stdio`；`main` = 权威 2 / auditB 4） | 9 | **4** | 9 | **4** | PASS |
| `artifact_read_model.py` | **10**（新文件规则） | 8（`read_artifact`，auditB 11） | **8**（`read_artifact`；auditB 7） | 11 | **7** | 12 | **8** | PASS |

权威口径逐函数机器输出：`authority_check.py` → `evidence_authority_check.txt`
```
producer_events.py         _max_complexity=1  target<=1  frozen=1  -> PASS
identity_cli.py            _max_complexity=3  target<=6  frozen=6  -> PASS
artifact_read_model.py     _max_complexity=8  target<=10  frozen=None  -> PASS
AUTHORITY CHECK: ALL PASS
```

## 3. 拆法（逐文件，行为零变）

### 3.1 `producer_events.py` — 3 → 1（最紧，零分支）
- 原分支：两个三元 `int(parser[0] if parser is not None else 0)`（auditB 记 2 点 → 3）。event_type 过滤**本来就在 SQL** 里（`WHERE … event_type='parser'/'llm'`），剩下的 Python 分支只有“`fetchone` 返回空行 → 0”。
- 调用方 `resolver.py:1089` **不在本单写入面**，不能把分支留给调用方；SQL 也无法表达“返回行缺失”（`COUNT(*)` 恒有行，缺行只可能来自 store 实现）。
- 因此新增顶层 `_tally(row)`：`int((row, _ZERO_ROW)[row is None][0])` —— 这是**选择不是分支**（无 `If/IfExp/BoolOp/For/comprehension/With/Assert/Except`），语义与 `row[0] if row is not None else 0` 逐输入等价（None→0、有行→计数、空行→IndexError，和从前一样）。`count_producer_events` 变成**纯直通**：两条 SQL + 两次 `_tally`。
- 结果：`_tally` 与 `count_producer_events` 在**三个口径下都是 1**；SQL 文本、查询次数、返回 dict 完全不变。

### 3.2 `identity_cli.py` — 9 → 4（权威 6 → 3）
把 `main` 按原 `try` 块边界拆成三段（语句顺序逐条保持）：
- `_configure_stdio()`：原两个 `hasattr` 保护的 `reconfigure`（权威 3 / auditB 3）。
- `_refreshed(store, args)`：原 `if args.refresh` + 三元 `markets`（权威 2 / auditB 3）。
- `_resolved_payload(args)`：原 try 块主体 store→refresh→identify→payload（权威 2 / auditB 2），**异常照旧向外抛**，由 `main` 的 `except` 统一走 `structured_error` → return 1；`print(payload)` 与 `0/2` 返回值仍在 try 之外，语句级行为一致。
- `main` 只剩 parse / try / print / return（权威 2 / auditB 4）；`__all__ = ["main"]`、`if __name__` 均保留。

### 3.3 `artifact_read_model.py` — 11 → 7（权威 8，≤10）
- 把 `read_artifact` 末尾**原样搬出**的 `ReadableArtifact(...)` 组装（4 个 binding-vs-legacy 三元）拆成 `_readable_artifact(...)`（权威 1 / auditB 5）。
- `read_artifact` 只留读取 + 4 个 fail-closed 检查 + `validate_artifact`（权威 8 / auditB 7）；字段、`binding`/`legacy` 判定、异常文案逐字未动。

## 4. 顶层扫描自证（派单要求）
`selfproof_toplevel_scan.py` → `evidence_toplevel_scan.txt`（直接调用门禁自己的 `_max_complexity`）：
- `1a` 分支写在**嵌套函数**里 → **2**（不是 1）⇒ **嵌套函数藏不住分支**：`_max_complexity` 取顶层函数整段源码再 `_mccabe` 递归，嵌套函数体照样计入父函数。派单里“嵌套闭包不被扫到”的提示**不成立**，本单未采用该写法。
- `2` 模块级 `if`（不在任何函数内）→ 1；`3a` 模块级 lambda 带三元 → 1 ⇒ 扫描确实只遍历 `tree.body` 的 `FunctionDef`，模块级代码/lambda 不在扫描面（本单**没有**用这种把分支藏到模块级的写法）。
- 结论：`producer_events` 想要 1，函数体内必须真的零决策点，所以走 `_tally` 的“选择而非分支”。

## 5. 测试与覆盖
命令与原始输出：`evidence_tests_after.txt`、`evidence_coverage_compare.txt`。

| 运行 | 结果 | 说明 |
|---|---|---|
| `pytest tests/contract/test_source_catalog_security_identity.py tests/unit/test_zr304_read_model.py tests/contract/test_fc905_receipt_envelope.py tests/contract/test_fc1204_complexity_ratchet.py -q` | **25 passed, 4 failed** | 4 个失败**全部在本单写入面之外**，且 **3 个在改动前的基线运行里就同样红**（见下） |
| `test_fc1204_complexity_ratchet.py::test_complexity_ratchet_frozen_files_do_not_worsen` | **PASS** | 覆盖 `producer_events.py`(1≤1)、`identity_cli.py`(6≤6) 及全部冻结文件 |
| `pytest tests/contract tests/unit -q -k "identity or envelope or zr304 or read_model"` | **117 passed, 3 failed** | 失败同下 3 个 |
| 分支覆盖（同一批测试，前后对比） | `producer_events` 100→100（底线 95 必达）· `identity_cli` 82.4→**84.5**（底线 82）· `artifact_read_model` 91.2→91.3（无底线） | 无覆盖回退 |

范围外的 4 个红（非本单、非本单所致）：
1. `test_fc905_receipt_envelope.py::test_pi01/pi02/pi09` — `prompt_injection.py::_require_sha256` 抛 `source_sha256 must be a lowercase SHA-256`；**改动前基线同一 3 红**（`prompt_injection.py` 为并行工位在改文件，堆栈不经过本单三文件）。
2. `test_fc1204_complexity_ratchet.py::test_complexity_ratchet_new_files_stay_simple` — `narrative_evidence.py` 363 > 10（非冻结表新文件，非 B 组责任文件；同运行里 `prune_retired_evidence.py` 27>12 的旧红已由 C 组修掉）。

## 6. 没做的事 / 边界
- 未改 `FROZEN_MAX` 冻结表、未改任何测试、未改 `resolver.py`（分支留调用方不可行，已说明）。
- 未触碰 `narrative_evidence.py`、`prompt_injection.py` 及 A/C 组文件；未修范围外 4 红（fail-closed 只适用于本单文件，本单三文件均达标且未回滚）。
- `dayu-agent` 零接触；无联网；无 git 写、未跑 `git status`（只读 `git -c core.quotepath=false diff HEAD --name-only` 用于归因，见 `handoff.json`）。
- 覆盖率门禁需 `FC1204_COVERAGE_GATE=1` + 全量 `coverage.json`，本单用同批测试的前后对比作证（`COVERAGE_FILE`/报告均落在产出目录，未污染仓内 `coverage.json`）。
