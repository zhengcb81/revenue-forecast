# 复审报告 — FC-1204 complexity ratchet 净 delta（棘轮拆分）
**工位**: 独立复审 · `RATCHET-FIX-REVIEW/a20260927-01` · 2026-09-27
**被审对象**: `company-wiki` 工作区**未提交** 4 文件 diff（`git diff HEAD -- <4 files>`，只读）
**授权**: owner `§四十二 裁定一` · **未改工作区一个字节、禁 git 写、未用 `git status`、无联网、`dayu` 零接触**

---

## VERDICT：`ACCEPT`（为将来可提交背书；本 delta 未提交、未推送，未改工作区）
无 `P1`。可带 `P2/P3` 提交；提交前建议按 §4 处理 `P2-1` 的路径选择。

---

## 1. 裁决行 + 发现清单

被审对象 = **4 文件 / 17 hunk**，全部落在 `§四十二 裁定一` 授权面内：

| 文件 | hunks | + | − | HEAD → 现值（门禁口径） | 冻结 | 判定 |
|---|---|---|---|---|---|---|
| `archive_retired_evidence.py` | 4 | 122 | 73 | **19 → 7** | 7 | ✅ |
| `observability.py` | 4 | 61 | 35 | **27 → 6** | 6 | ✅ |
| `prune_retired_evidence.py` | 7 | 223 | 121 | **27 → 12** | 12 | ✅ |
| `tests/contract/test_observability.py` | 2 | 15 | **0** | —（测试面） | — | ✅ |

**发现清单（按级）**

| ID | 级 | 发现 |
|---|---|---|
| `P2-1` | P2 | 本 delta 内含 **5 条既有红契约测试**（archive 2 + prune 3）；C 组 handoff 只记了 3 条 prune 红，漏记 archive 2 条。经 §3 绑定证明**非本 delta 所致**，但提交后这 5 条仍红 ⇒ 提交者须显式选路径（接受红 / 另单修测试 / 单独提交）。 |
| `P3-1` | P3 | C 载体 `pre_image/observability.py` 非真正入手前像：其内容 == 拆分后态（仅 LF/CRLF 不同），是拆分体副本。不影响结论（该文件本轮仅加注释），但载体自称"前像"失真。 |
| `P3-2` | P3 | `archive_retired_evidence.py` 在 A/B/C 三个载体中**均无 `pre_image/` 留痕**。本报告以 `git show HEAD:` 作前像替代（该文件不在 A、B 的 4/3 文件清单内，归属不明）。 |
| `P3-3` | P3 | 门禁 `new_files` 红（`narrative_evidence.py 363 > 10`）——非本 delta，属并发工位。 |
| `P3-4` | P3 | 未重跑 C 组 17 场景 prune 探针（夹具成本），改为复算其产物 sha256（§3）。 |

---

## 2. ⭐ 测试弱化核（最重要）— 逐 hunk

`git diff HEAD -- tests/contract/test_observability.py` = **2 hunk，+15 / −0（零删除行，零修改行）**。与 `HEAD` 版对照：HEAD 98 行 → 现值 113 行，**原有 7 个测试函数全部逐字未动**。

| hunk | 内容 | 判定 |
|---|---|---|
| `@@ -16,6 +16,7 @@` | import 块新增 `redact_text`（原先只 import `MetricsCollector/REDACT/REASONS/validate_reason`） | **非弱化** — 纯新增 import，无既有符号被删/改名 |
| `@@ -96,3 +97,17 @@` | 文件尾新增 `test_obs08_redaction_preserves_adjacent_diagnostic_fields`（14 行） | **非弱化 — 是收紧** |

**新增 test_obs08 是收紧而非放宽**，三条独立证据：
1. **断言形态是等值全串比对**（`assert redacted == <完整期望串>`），不是子串/`in`/`startswith` 之类可被放宽的形态；且逐字段锁死 `cmd:`、`doc=17`、URL query、带引号值、`status=failed` 相邻字段。
2. **它是一个真会咬的测试**：我用现值与 HEAD 版红actor各自实跑该断言 — 现值 `True`、HEAD 版亦 `True`；即该断言**不是过拟合于本次拆分**，而是同时锁住拆分前后行为的独立不变量（正因如此它对本次拆分不构成"随改"借口，反而增厚安全面）。
3. 该断言覆盖 4 类脱敏分支：`--token=`（`=` 形）、URL `?token=&stage=`（非空格定界）、`token = "quoted secret"`（带引号 + 空格形）、以及**未脱敏的相邻诊断字段必须存活**（`doc=17`、`status=failed`）。

**结论：0 处放宽、0 处删除、0 处条件弱化。测试面结论 = 合法（跟随拆分更新断言 + 净收紧）。**

---

## 3. 行为保持核

### 3.1 三源文件各抽 ≥2 处 hunk 自读（均**只搬移、不改逻辑**）

**`archive_retired_evidence.py`（4 hunk，19→7）**
- hunk@`@@ -127,24 +135,17 @@`（`_validate_required_now` + `_target_paths` 抽出）：`now` 类型/tzinfo 校验、异常 `TypeError` 与文案、`moment/day/token/out_dir/out_path/tmp_path` 计算序、`FileExistsError` 分支逐字保留；新 `_target_paths` 返回 4 元组而非原 `nonlocal` 赋值 —— 等价。
- hunk@`@@ -166,68 +266,17 @@`（流式写出 / 对账 / 自校验 / 发布 / manifest 抽出）：`_write_snapshot_rows` 保留 `last_id` 游标两分支 SQL 与 `BATCH_SIZE`、gzip `wt/newline="\n"`、`_row_digest` 记账、`progress` 回调时机；`_check_reconciliation` 文案 `archive reconciliation failed: wrote {n}, catalog reports {t}; snapshot not published` 逐字；`_verify_and_publish` 保留 `_fsync_file → _verify_snapshot → 比对 count+digests → _publish` 序；`_write_manifest` 保留 `MANIFEST_SCHEMA`、`sorted(verified_digests)`、`row_digests` 键排序、`problems: []`、`ok: True`、`_atomic_write_text`。原 `archive_sha256` 局部变量被内联进 dict —— 该变量只被该 dict 使用，等价。`published = True` 仍在 `_publish` 之后、manifest 之前 → `finally` 清理路径不变。

**`observability.py`（4 hunk，27→6）— ⭐ 脱敏安全面逐一核**
- hunk@`@@ -378,42 +382,14 @@`：内联键回扫/值回扫/引号处理 → `_credential_key_before_separator` / `_scan_left_over` / `_is_credential_key` / `_assignment_value_start` / `_assignment_value_end` / `_unquoted_assignment_end`。
- hunk@`@@ -459,16 +479,22 @@`：`while True/break` → `while (nxt := _next_unseen_cause(...)) is not None`。
- **脱敏分支无遗失（4 条原分支逐一在位）**：① `separator_at` 处 `text[index] not in "=:" → append(char); index+=1; continue`（非分隔符不消费）；② `cursor == 0 or text[cursor-1] not in _KEY_CHARS → boundary_ok`；③ `not (key and boundary_ok and key_is_credential(key)) → append(char)`（含"无键"路径，等价搬入 `_is_credential_key` 的 `bool(key and ...)`）；④ `value_end <= value_start → append(char)`（无值不消费）。未闭合引号 `closing == -1 → value_end = length` 保留；C13 单 token 收束（停于 `_VALUE_STOP_CHARS` 或任意空白含换行）保留。
- 新增独立证据：**HEAD 版（27）与现值（6）差分模糊 400,000 条对抗输入逐字节相同**，另 36 条定向结构化输入（未闭合引号/`::`/`==`/空值/跨行/`$(...)`/反引号等）全部相同；红action 命中率轴 HEAD 18,418 vs 现值 18,418（**现值从不更弱**）。harness 自检：闭包 6 个符号全部取自 HEAD、HEAD 副本门禁值实测 27、模块常量逐一相同 —— 自检未过则拒绝出结论。
- **字符串常量多重集：`observability.py` 前像 596 → 现值 596，"丢失/减少"计数 = 0，新增 = 0** ⇒ 无任何脱敏规则或提示串遗失。

**`prune_retired_evidence.py`（7 hunk，27→12）**
- hunk@`@@ -213,6 +213,96 @@`（`_load_verified_archives` 16→4）：11 级验证梯拆 `_verify_one_manifest` + `_manifest_decl_problem` + `_archive_bytes_problem` + `_verified_archive`。**检查顺序逐条不变**（read/parse → `schema_version` → `ok is not True` → `_resolve_archive_path is None` → `st_size` vs `archive_bytes` → `_sha256_file` OSError → sha vs `archive_sha256` → `_read_snapshot` 四类异常 → `rows_in_archive` → `row_digests` → `verified_completed_at`）；**11 条 problem 文案逐字保留**，异常元组 `(OSError, json.JSONDecodeError)`、`OSError`、`(OSError, EOFError, ValueError, json.JSONDecodeError)`、`(TypeError, ValueError)` 一一对应。
- hunk@`@@ -417,27 +462,10 @@` + `@@ -546,6 +570,84 @@`（入口 27→6）：`_select_plan`（`plan is None` 两分支、`PrunePlan.compute_hash` 不匹配 → `PruneRefused("frozen plan hash does not match its contents")`）、`_due_and_oldest`（`due` 的 `bool(...) and any(...)`、`oldest` 的 `min(key=(_parse_utc(...), archive_path))`）、`_pre_delete_check`（absent/not-retired/changed 三拒 + 两段 `PruneRefused` 文案）、`_delete_batch`（单事务内读回+复核+删除，三条 `PruneRefused` 文案，`max(batch_rows, 0)`）、`_pending_receipt`（10 键键序与值逐字，含 `committed_ids: []`、`deleted_rows: 0`）全部等价搬移。
- **字符串常量多重集：`prune_retired_evidence.py` 前像 147 → 现值 157，"丢失/减少"计数 = 0**（新增 10 条全为 docstring）。
- **`archive` 端到端（补 `now=`，IN-REPO 测试做不到，见 §4）**：pre-image 体 vs 现值体各真跑一次，6 行真导出 —— 行数/`ok`/行序（span_id 序列）/gz 文本 sha（`2630C649…`）/压缩字节数/文件名形态/目录形态/无 `.partial` 残留 **全部相同**；manifest 载荷逐字段相同；`manifest.archive_sha256` 与**已发布文件真实字节** sha 双向一致（大小写规范化后）；`archive_bytes`/`rows_in_archive` 与实物一致。
- **fail-closed 负路径身份相同**：自校验篡改 → 两边均 `RuntimeError("archive self-verification failed: snapshot not published")`；对账不符（流式途中删 1 span）→ 两边均 `RuntimeError("archive reconciliation failed: wrote 5, catalog reports 6; snapshot not published")`；两边均**零发布、零 `.partial` 残留**。
- **C 组 17 场景 prune 探针产物复核**：`probe_pre.json` 与 `probe_post.json` sha256 **均为 `6DB7D1FA262C5BD224AED6EAE036DC4566040BFFA2B9BA2E63DE8ED5585F5E57`**（逐字节相同，与 handoff 自述一致），17 个场景键俱在（11 条坏 manifest 梯 / 冲突授权 / 保留期内外 / 冻结 plan / 幂等二跑 / 4 类 PruneRefused / naive-now TypeError / 收据内容）。
- **门禁口径签名核**：两函数公开签名 `HEAD` vs 现值**逐字相同**（`now: datetime` 无默认、keyword-only）⇒ 拆分未改公开契约。
- **"遗留旧体"排查**：三文件 **删除的顶层函数 = 0**；新增 helper **无一不可达**；既有函数**无一变为不可达** ⇒ 无 legacy fork / 无死代码残留。

---

## 4. 门禁口径复核

**用门禁自带度量**（`tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity`，经 `importlib` 直接导入该模块，非重实现）自算：

| 文件 | 冻结(须≤) | **现值** | HEAD | 最复杂函数（现值） | 判定 |
|---|---|---|---|---|---|
| `archive_retired_evidence.py` | 7 | **7** | 19 | `_write_snapshot_rows`=7 | ✅ |
| `observability.py` | 6 | **6** | 27 | `key_is_credential`/`_is_credential_key`/`_next_unseen_cause`=6 | ✅ |
| `prune_retired_evidence.py` | 12 | **12** | 27 | `_build_plan`=12 | ✅ |

三文件均 **≤ 冻结，无超标**。冻结表 `FROZEN_MAX` **未被改动**（三者表值 7/6/12 与派单一致，已核）。

`pytest tests/contract/test_fc1204_complexity_ratchet.py -q` ⇒ **`1 failed, 1 passed`**，与预期完全一致：
- `test_complexity_ratchet_frozen_files_do_not_worsen` ⇒ **PASSED**（`frozen` 组全绿）；
- `test_complexity_ratchet_new_files_stay_simple` ⇒ **FAILED**：`new file narrative_evidence.py has max complexity 363 > 10` — **该条非本 delta**（未跟踪新文件，不在 4 文件写入面）。

**worktree == 载体 `post_image`（LF 归一后）**：`observability.py` ✅、`prune_retired_evidence.py` ✅。
**sha 对照（前像 / 现值）**：
- `prune`：前像 `0C99BBE0C5F4EF16E7F84BA8AAE0548EF6F59A0080274D5BD1CE83A7D37990B0`（TEST 27）→ 现值 `70CC807A2FA59883E503DE0F43B21951A16408BD4F30AFCAE0632E747907334C`（TEST 12）
- `observability`：前像 `563CDF1D95817665F91BED01FEA76C2D632E082F3C4751316EE0FF87D818993E`（TEST 6）→ 现值 **裸字节** `18DDCEC4F8FE207C0E4E65C6AA31F30CC09ABA93B11BB935E5D9B03BCC75BCCE` / **LF 归一** `C2622DC31C912B1E9B4ABDF86E5EF8BA29C2A1E66D457623C487F8981D9639EF`（TEST 6）
- `archive`：HEAD 即前像（载体无留痕）`→` 现值 `4CD950CAA0C53042D15F03A00BD197DB457A4E0B8AA7F09181B8DAE01E87C1AC`（TEST 7）
- 测试面：`tests/contract/test_observability.py` = `699AA419B9E119FCDA00F628B8C4F9BD187F14507B73BB42AA860DB3CD496373`

> ⚠ **CRLF 勘误（供载体更正）**：`observability.py` 工作区为 CRLF（934 对）；前述 `18DDCEC4…` 是 **C 组按 LF 归一（`read_text`）** 报出的值。**裸字节 hash 才是 `18DDCEC4…`，LF 归一是 `C2622DC3…`** —— 与 C 组 `handoff.json` 自述方向相反。二者皆 TEST=6，不改结论，但载体该字段名实不符。

---

## 5. 相关测试

`pytest tests -q -k "archive_retired or observability or prune_retired"` ⇒ **`5 failed, 8 passed`**（13 selected）。

| 组 | 结果 |
|---|---|
| `tests/contract/test_observability.py`（含新 `test_obs08`） | **8 passed** ✅ |
| `tests/contract/test_source_catalog_archive_retired.py` | 2 **failed** |
| `tests/contract/test_source_catalog_prune_retired.py` | 3 **failed** |
| 另跑 `-k redact` | **9 passed** ✅ |

**5 条红全部为 `TypeError: <fn>() missing 1 required keyword-only argument: 'now'`，且已证非本 delta 所致**（三条独立绑定证明）：
1. 公开签名 `HEAD` vs 现值**逐字相同**（§3.1）⇒ 拆分未引入该 kwarg；
2. `git log -S "now: datetime"` 唯一命中 **`ac4ebd0`**（2026-09-22），而两测试文件最后改动为 `b838a85`/`b6c97b8`（更早），且文件内 `now=` 出现次数 **= 0** ⇒ 自 `ac4ebd0` 起即红；
3. **绑定证明**：把 pre-image/pre-HEAD 体与现值体载入同一进程、发同一调用 ⇒ **两边抛完全相同的 `TypeError`**。异常在 **call binding** 处抛出，**函数体从未进入** ⇒ 对本 delta **逻辑上不可能**由 body 改动导致。

`archive_retired_evidence.py` 的 2 条红**同样**受此覆盖（其 `now:` 亦为 HEAD 既有）。

**py_compile 4 文件 exit=0；3 个产品模块 import OK，三个公开入口点均 callable。**

---

## 6. 没做的事 / `unverified`

**没做的事**
1. **未写任何卡状态**（本工位只写复审报告）。
2. **未改产品码一个字节**：未 edit/write 4 文件或其任何同仓文件；未 `git add/commit/stash/checkout`；**全程未用 `git status`**（只用 `git diff` / `git show` / `git log -S` 只读）。
3. **未改动工作区**：本 delta 仍未提交、未推送（owner 令 `cw` 不强推）；`ACCEPT` 仅为"将来可提交"背书。
4. **未提交、未推送、未打标签、未触发门禁流水线**。
5. **未修 5 条既有红**（测试文件不在本工位写入面）。
6. **未处理 `narrative_evidence.py`**（并发工位，非本 delta）。
7. 未联网；`dayu` 零接触；未写五份计划文件；未触碰冻结表。

**`unverified`**
- `U1` **未重跑 C 组 17 场景 prune 探针**（需其夹具）；改为复算 `probe_pre/post.json` 的 sha256 恒等 + 场景键齐全。
- `U2` **archive 前像**非载体留痕，以 `git show HEAD:` 代替（§1 `P3-2`）。
- `U3` 未核 `RB` 之外模块（如 `source_catalog/__init__.py`）是否 re-export 了被拆分符号；仅核了三文件自身公开签名与 import 可用性。
- `U4` 未核 prune 在**真实生产目录树**上的行为，仅核 17 场景探针产物与静态等价。
- `U5` 未对 `observability` 做**变异测试**（未验证 test_obs08 能杀死具体错误实现），仅验证其断言形态为全串等值且拆分前后均通过。

**产出（本工位 2 文件 + 原始证据日志）**
`report.md`（本报告）· `review_transcript.md`（复核记录与原始命令/输出）
证据日志：`metric_out.txt` · `behaviour_out.txt` · `lineage_out.txt` · `pytest_gate_out.txt` · `pytest_related_out.txt` · `diag_out.txt`
脚本（只读、可复跑）：`recompute_metric.py` · `behaviour_checks.py` · `lineage_checks.py` · `diag_archive_rows.py`
