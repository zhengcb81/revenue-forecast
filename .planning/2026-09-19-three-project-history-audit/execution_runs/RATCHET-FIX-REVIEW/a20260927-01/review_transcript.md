# 复核记录 — `RATCHET-FIX-REVIEW/a20260927-01`
独立复审工位（FC-1204 complexity ratchet 净 delta）。只读公司仓；写入面 = 本产出目录。

---

## 0. 工位边界

| 项 | 值 |
|---|---|
| 被审对象 | `company-wiki` 工作区**未提交** 4 文件 diff |
| 自算命令 | `git -C C:\Users\郑曾波\Projects\company-wiki -c core.quotepath=false diff HEAD -- <4 files>`（只读） |
| 产出目录 | `...\execution_runs\RATCHET-FIX-REVIEW\a20260927-01\` |
| 写入面 | 本目录（报告 + 脚本 + 证据日志） |
| 产品码 | **只读**，未改一字节 |
| git | 禁写；**禁 `git status`**（全程只用 `diff`/`show`/`log -S`） |
| 其他 | 禁联网；`dayu` 零接触；未写五份计划文件；未写卡状态 |

---

## 1. 上游载体读取（只读）

- `RATCHET-FIX-C/a20260927-01/`：`oracle.md` · `split_report.md` · `handoff.json` · `pre_image/` · `post_image/` · `probe_pre/post.json` · `verification_output.txt`
- `RATCHET-FIX-A/a20260927-01/handoff.json`：`files_fixed = 0`；scope 4 文件（`adapters/parity.py`/`lock.py`/`prompt_injection.py`/`store.py`），其中 parity/lock 已由父还原；**不含 archive**。
- `RATCHET-FIX-B/a20260927-01/handoff.json`：3 文件（`producer_events.py`/`identity_cli.py`/`artifact_read_model.py`），**不含 archive**。
- **父口径勘误已核**：门禁 `_max_complexity` 不计 `IfExp`，故派单"实际"列（含 IfExp 的 M 口径）多算 8 处误报；真违规 4 处（archive/observability/prune/narrative）。本 delta 含前 3 处（narrative 为并发未跟踪新文件）。
- ⇒ **`archive_retired_evidence.py` 在 A/B/C 三载体中均无归属、亦无 `pre_image/`** ⇒ 记为 `P3-2`，以 `git show HEAD:` 作前像替代。

---

## 2. diff 自算（hunk 清单）

```
git -C <wiki> -c core.quotepath=false diff HEAD --stat -- <4 files>
 .../source_catalog/archive_retired_evidence.py     | 195 +++++++-----
 src/company_wiki/source_catalog/observability.py   |  96 +++---
 src/company_wiki/source_catalog/prune_retired_evidence.py | 344 +++++++++++--------
 tests/contract/test_observability.py               |  15 +
 4 files changed, 421 insertions(+), 229 deletions(-)
```

| 文件 | hunks | + | − |
|---|---|---|---|
| `archive_retired_evidence.py` | 4 | 122 | 73 |
| `observability.py` | 4 | 61 | 35 |
| `prune_retired_evidence.py` | 7 | 223 | 121 |
| `tests/contract/test_observability.py` | 2 | **15** | **0** |

---

## 3. 五项复核 — 执行与结论

### 复核① 裁决行 + 发现清单
见 `report.md` §1。结论：4 文件 17 hunk 全在授权面内；无越权写入。

### 复核② 测试弱化核（最重要）
- `test_observability.py` diff = **2 hunk / +15 / −0**；`Select-String "^-"`（排除 `---`）**零命中** ⇒ 无删除、无修改行。
- HEAD 98 行 → 现值 113 行；既有 7 个测试函数逐字未动。
- hunk1：import 新增 `redact_text`（纯新增）。
- hunk2：新增 `test_obs08_redaction_preserves_adjacent_diagnostic_fields`，形态为 **`assert redacted == <完整期望串>`**（全串等值，非 `in`/`startswith`）。
- **咬合验证**：现值与 HEAD 版 redactor 各自实跑该断言均 `True` ⇒ 断言锁的是拆分前后共有的不变量，非过拟合。
- **结论：合法（跟随拆分 + 净收紧），无弱化。**

### 复核③ 行为保持核
见 `report.md` §3。抽样 hunk 清单：
- `archive`：`@@ -127,24 +135,17 @@`（`_validate_required_now`+`_target_paths`）、`@@ -166,68 +266,17 @@`（`_write_snapshot_rows`/`_check_reconciliation`/`_verify_and_publish`/`_write_manifest`）
- `observability`：`@@ -378,42 +382,14 @@`（键回扫/值回扫/引号处理 6 helper）、`@@ -459,16 +479,22 @@`（walrus 化 `_next_unseen_cause`）
- `prune`：`@@ -213,6 +213,96 @@`（11 级验证梯）、`@@ -417,27 +462,10 @@` + `@@ -546,6 +570,84 @@`（入口 27→6）

**四类独立证据**（非仅"自读"）：
1. **脱敏面差分模糊**：HEAD(27) vs 现值(6) 400,000 条对抗输入逐字节相同；36 条定向结构化输入相同；命中率轴 18,418 vs 18,418（现值从不更弱）。harness 自检：闭包 6 符号全取自 HEAD、HEAD 副本门禁值实测 27、模块常量逐一相同 → 自检不过则拒绝出结论（`behaviour_checks.py` B1）。
2. **字符串常量多重集**：`observability` 596→596（丢 0/增 0）、`prune` 147→157（短常量丢 0）、`archive` 63→69（短常量丢 0；唯一"丢"项为被扩写的模块 docstring）⇒ 无错误/拒绝/收据/problem 文案遗失（B2）。
3. **archive 端到端**：补 `now=` 后 pre 体 vs 现值体各真跑 6 行导出，report/行序/gz 文本 sha/字节数/文件名形态/目录形态/manifest 载荷全同；manifest sha 与已发布字节双向一致；负路径（自校验篡改、对账不符）异常类型+文案全同、零发布零残留（B3）。
4. **静态结构**：公开签名 HEAD vs 现值逐字相同；删除顶层函数 0；新增 helper 无一不可达；既有函数无一变为不可达（`lineage_checks.py` C1/C2）。

**脱敏分支逐一核（4 条全在位）**：非分隔符不消费 / `boundary_ok` / `not (key and boundary_ok and key_is_credential(key))` 含"无键"路径 / `value_end <= value_start` 无值不消费；未闭合引号吞尾保留；C13 单 token 收束（停于 `_VALUE_STOP_CHARS` 或任意空白含换行）保留。

### 复核④ 门禁口径复核
- 度量来源：`importlib` 直接导入 `tests/contract/test_fc1204_complexity_ratchet.py`，调用其 `_max_complexity`（**非重实现**）。
- 现值 **7 / 6 / 12** ≤ 冻结 **7 / 6 / 12**（archive 19→7、observability 27→6、prune 27→12）。冻结表未改动。
- 17 场景 prune 探针产物 sha256 复核：`probe_pre.json` == `probe_post.json` == `6DB7D1FA262C5BD224AED6EAE036DC4566040BFFA2B9BA2E63DE8ED5585F5E57`。
- worktree == 载体 `post_image`（LF 归一）：`observability` ✅、`prune` ✅。

### 复核⑤ 相关测试
- `pytest tests -q -k "archive_retired or observability or prune_retired"` ⇒ **5 failed, 8 passed**。
- `pytest tests -q -k redact` ⇒ **9 passed**；`tests/contract/test_observability.py` ⇒ **8 passed**。
- 5 红 = 2 archive + 3 prune，**全为 `TypeError: ... missing 1 required keyword-only argument: 'now'`**，绑定级证明非本 delta 所致（见 `report.md` §5）。
- `pytest tests/contract/test_fc1204_complexity_ratchet.py -q` ⇒ **1 failed, 1 passed**（`frozen` PASS；`new_files` FAIL = `narrative_evidence.py 363 > 10`，非本 delta）。
- `py_compile` 4 文件 exit=0；3 产品模块 import OK。

---

## 4. 本工位 harness 自身缺陷与更正（留痕）

复审脚本首轮出现 3 处**自身**缺陷，均已定位、修复并留痕（避免误判被审对象）：

| # | 缺陷 | 症状 | 更正 |
|---|---|---|---|
| H1 | `exec` HEAD 定义时**跳过 `_` 前缀函数** | `head_assign is obs._redact_assignments == True` ⇒ 实为 worktree-vs-worktree 自比，假 PASS | 改为 exec **全部**顶层 def 到独立命名空间；加硬自检（副本门禁值须 ==27、须非同一对象），不过则 abort |
| H2 | 未加 `if __name__ == "__main__":` 守卫 | company-wiki `scan/normalize` 在 Windows 用 multiprocessing，spawn 子进程重导入 `__main__` 重跑整脚本 ⇒ 父报 `spans=0`、子报 `spans=6`，首轮 archive 端到端**实际 0 行**（未触达 manifest 路径） | 加 `__main__` 守卫 + `main()`；加 `harness_retired_spans > 0` 断言，为 0 则判 harness 无效 |
| H3 | manifest sha 大小写 + gzip mtime 误比 | 3 条假 FAIL | 规范化大小写；排除易变字段（`archive_path`/`archive_sha256`），改为断言"manifest sha == 已发布字节真实 sha" |

另：`behaviour_checks.py` 首轮曾用 SRC 拼测试文件路径致 `FileNotFoundError`，已修为相对路径。

**CRLF 勘误**：`observability.py` 工作区含 CRLF（934 对）。其**裸字节** sha = `18DDCEC4…`、**LF 归一** sha = `C2622DC3…`；与载体 `post_image` 相等的是 **LF 归一**值（git checkout 归一化）。C 组 `handoff.json` 自述方向相反 ⇒ `report.md` §4 已记勘误，不改结论（两值 TEST 均 = 6）。

---

## 5. 原始证据文件

| 文件 | 内容 |
|---|---|
| `metric_out.txt` | 门禁度量自算（现值 / HEAD / 载体前后像 / worktree-vs-post_image） |
| `behaviour_out.txt` | B1 差分模糊 + B2 常量多重集 + B3 端到端与负路径 |
| `lineage_out.txt` | C1 绑定证明 + C2 legacy-fork 检查 |
| `pytest_gate_out.txt` | `test_fc1204_complexity_ratchet.py -q` 全文 |
| `pytest_related_out.txt` | `-k "archive_retired or observability or prune_retired"` 全文 |
| `diag_out.txt` | archive 0 行根因诊断（守卫修复后 6 行） |
| `recompute_metric.py` | 只读；导入门禁 `_max_complexity` 自算 + 双 hash（裸字节 / LF 归一） |
| `behaviour_checks.py` | 只读；B1/B2/B3，含 harness 自检 |
| `lineage_checks.py` | 只读；C1 绑定证明 + C2 fork 检查 |
| `diag_archive_rows.py` | 只读；archive 夹具行数诊断 |

---

## 6. `unverified` 汇总
`U1` 未重跑 C 组 17 场景 prune 探针（改复算产物 sha256）。`U2` archive 前像以 `git show HEAD:` 替代（载体无留痕）。`U3` 未核其他模块是否 re-export 被拆分符号。`U4` 未在真实生产目录树跑 prune。`U5` 未对 `observability` 做变异测试。

`VERDICT: ACCEPT`（无 `P1`；`P2-1` + `P3-1..4`；本 delta 未提交、未推送，未改工作区）
