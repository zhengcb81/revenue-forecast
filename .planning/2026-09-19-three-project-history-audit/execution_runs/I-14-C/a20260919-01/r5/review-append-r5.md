

# r5 — INDEPENDENT REVIEW (round 5)

# I-14-C r5 独立定点复核报告（adversarial, 全程只读生产仓库）

- 复核人：独立 reviewer（第 5 轮，非实现者）
- 被复核对象：`PLAN\execution_runs\I-14-C\a20260919-01`（r5，2026-09-20 03:4x–04:4x）
- 复核窗口：本窗口 `REVIEWDIR=C:\Users\郑曾波\AppData\Local\Temp\i14c-r5-review-20260920-044801`，建立于 2026-09-20T03:48:01Z
- 解释器：`<attempt>\iso\venv\Scripts\python.exe`（3.13.9；未使用全局 Miniconda python）
- 生产仓库：`company-wiki` / `filing-fetch` / `revenue-forecast` 只读
- 所有结论均由本人重跑命令取得；未采信实现者任何结论性陈述

---

## VERDICT: `accepted_scoped`

**范围（与我第 4 轮口径一致）**：I-14-C 的**证据与判据**在这一轮成立 ——
(a) F-I14C-08 的关闭依据经本人第 4 轮独立复现并**在本轮以逐字符精确判据再次验证**；
(b) r4 review 的 **6 项整改全部逐条对号关闭**；
(c) r5 新增的**全部数字来自机械推导**，我独立重算**逐项相符**；
(d) 验收测试**仍未产品化**（C12 硬前置）——这是本卡**明示未做**的部分，不构成对本判定的否定，但 `accepted_scoped` **不等于批准促销**。

**本轮唯一"新"结论**：r5 把 r4 遗留的两条**"reviewer 无法验证"**通道真正打开了 ——
① 全部 82 个用例现在可由 reviewer 在自己目录内独立跑通（我实测 3 次：82 passed / 22.1 s、21.4 s、22.0 s，其中一次**完全不设** `I14C_RUN_ROOT`）；
② `r5-changes.diff` 可由**标准 `git apply`** 消费并**字节复原** T4（我实测 `--check` 与 `-p1` 均 rc=0，三文件 sha256 全等；且在**不设任何本地 git 配置覆盖**时同样成立）。

**3 项 P3/P4 文档级瑕疵**（见发现 1–3）**不阻塞本判定**，但建议在下一轮随其他改动一并清理：其中发现 1（`oracle.md` 的 r4 段被就地编辑而非追加）触到我上轮设定的"只许追加/不得改冻结件"边界 —— 我逐行核对后确认**冻结语义未被改动**，故不升级为阻断项。

---

## 一、请重点复核的 7 项 —— 逐项结论

### 1. F-I14C-08 关闭依据与保真断言 ✅ **全部成立**

**(1a) `iso/product_r3` 确实"0 泄漏但保真失败"，T4 确实 0/0。** 本人用**自己的命令**重跑十次表调用（5 树 × 2 表）：

```
run_rule_table.py       product        rc=2 verdict=cannot_adjudicate  leakers=0 fidfail=n/a entries=
run_rule_table.py       product_r1     rc=3 verdict=negative           leakers=11 fidfail=11 entries=44
run_rule_table.py       product_r2     rc=0 verdict=pass               leakers=0 fidfail=n/a entries=44
run_rule_table.py       product_r3     rc=3 verdict=negative           leakers=0  fidfail=27 entries=44
run_rule_table.py       product_fixed  rc=0 verdict=pass               leakers=0 fidfail=n/a entries=44
run_diagnostic_table.py product        rc=2 verdict=cannot_adjudicate  leakers=0 fidfail=n/a
run_diagnostic_table.py product_r1     rc=3 verdict=negative           leakers=4  fidfail=5
run_diagnostic_table.py product_r2     rc=0 verdict=pass               leakers=0 fidfail=n/a
run_diagnostic_table.py product_r3     rc=3 verdict=negative           leakers=0  fidfail=13
run_diagnostic_table.py product_fixed  rc=0 verdict=pass               leakers=0 fidfail=n/a
```

**T3 标本：`credential_leaks = 0` 且 `fidelity_failures = 27`（规则表）/ `13`（诊断表），rc=3 —— 与实现者自述逐字相符。T4：rc=0、0 泄漏、0 保真失败。** 负例全部如声明为负：T0 → rc=2（`cannot_adjudicate`，helper 缺失），T1 → rc=3。

**(1b) 保真判据确为逐字符精确 —— 用"仅差一个字符"的注入证明。** 我在 `%TEMP%` 自建两个变异体：

```
=== 变异 A：把 REDACT 由 '<redacted>' 改成 '<redacted>!'（每条凭据输出仅多 1 个字符）===
run_rule_table.py:       rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=32
   FIDELITY-FAIL cred-header-bearer expected='Authorization: <redacted>' got='Authorization: <redacted>!'
run_diagnostic_table.py: rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=15

=== 变异 B：把 ';' 从值终止集合中移除（精确命中 1 条规则表项 + 1 条新增多行项）===
run_rule_table.py:       rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=2
   FIDELITY-FAIL cred-line-middle-trailing-punct expected='a=1 token=<redacted>; b=2' got='a=1 token=<redacted>'
   FIDELITY-FAIL cred-multiline-stopped-by-semicolon expected='failed for token=<redacted>; see log\nstage=summarize code=llm_global_failure' got='failed for token=<redacted>'
run_diagnostic_table.py: rc=0 verdict=pass     leaks=0 touched=0 new_over=0 fidelity_failures=0
```

变异 A **1 个字符的差异**即触发 rc=3 与 32 条失败；变异 B 说明判据是**逐条目**生效的（只命中受影响的两条，其余全绿）。**判据不是装饰性的，也不是"整表通过/整表失败"的粗门。**

**(1c) C13 的现状冻结确实显式化了（这正是我上轮 P2 的要求）。** 我从 `FIDELITY_CASES` 中提取到 **4 条含换行的用例**：

```
15: in='upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure request_id=req-1'
    expected='upload failed for token=<redacted>'
16: in='failed for token=<marker>; see log\nstage=summarize code=llm_global_failure'
    expected='failed for token=<redacted>; see log\nstage=summarize code=llm_global_failure'
17: in='token=<marker>\nnext=1'
    expected='token=<redacted>'
25: in='stage=summarize\ncode=llm_global_failure\nrequest_id=req-1'   (原样保留)
```

并用**我自己的 marker** 复算损失量，同时确认**不是截断造成的**：

```
product_r2     in_len=112 out_len=34  trunc_artifact=False  out='upload failed for token=<redacted>'
product_r3     in_len=112 out_len=39  trunc_artifact=False  out='upload failed for tokentoken=<redacted>'
product_fixed  in_len=112 out_len=34  trunc_artifact=False  out='upload failed for token=<redacted>'
```

新增测试 `test_f08_c13_multiline_loss_is_frozen_not_hidden` 同时用**本 attempt 的 marker 与我的 `ZQ7_REVIEWER_MARKER_9f3c`** 两种长度断言，且长度**由输入计算**而非硬编码（该测试文档自陈：r5 初稿硬编码我上轮的 112 并因此发红 —— 同一类"手打数字"失败，已被替换为计算值；这一自我披露是可信度的加分项）。

**(1d) 残余/极限形状与我上轮独立测得的完全一致**：`digest=`、`--api-key <v>`、JSON 引号键、裸 marker 仍存活（4 条已声明残留）；`monkey=` / `key=value` 未被触碰。

### 2. `r5-changes.diff` 的可用性 ✅ **可被标准 `git apply` 消费并字节复原 T4；r4 的反斜杠缺陷未回归**

本人的独立复现（自建 `%TEMP%` 仓库，不读实现者脚本）：

```
diff bytes=15083 header_lines=9
header lines containing a backslash: 0
POSIX_PATHS_ONLY = True
hunks = 6
git apply --check -p1 rc=0
git apply -p1       rc=0
  IDENTICAL worker.py:        applied=120561f5994e0ae0(48607B) T4=120561f5994e0ae0(48607B)
  IDENTICAL observability.py: applied=c5608c4b45a55cce(40060B) T4=c5608c4b45a55cce(40060B)
  IDENTICAL cli.py:           applied=4087c17230fc8ca7(66441B) T4=4087c17230fc8ca7(66441B)
  files in applied src tree that differ from T4: 0
GIT_APPLY_REPRODUCES_T4 = True
```

**加强验证**：我把 `core.autocrlf` / `core.safecrlf` 的**本地覆盖全部省略**（该机 global 配置三项均未设置，rc=1）后**重做一次**，结果相同：

```
global git config: core.autocrlf='' core.safecrlf='' core.eol=''   (all unset)
git apply --check -p1 rc=0 ; git apply -p1 rc=0 ; 三文件 IDENTICAL
ROBUST_WITHOUT_LOCAL_OVERRIDES = True
```

即补丁的可用性**不依赖** `core.autocrlf=false` 这类前置设置。头部形如 `diff --git a/src/... b/src/...`，**无反斜杠**（r4 缺陷未回归）。

### 3. `counts.json` 作为数字唯一来源 ✅ **独立重算逐项相符；自我校验确实存在且会发红**

我导入三张表（`run_rule_table.TABLE`、`run_diagnostic_table.CORPUS`、`test_i14c_real_exit_redaction.FIDELITY_CASES`）并用**独立调用 pytest `--collect-only`** 取节点数：

```
key                          mine                                       counts.json                                match
rule_table_entries           44                                         44                                         True
rule_table_by_kind           {'credential': 32, 'untouched': 9, 'residual': 3}  同                                  True
diagnostic_corpus_entries    30                                         30                                         True
diagnostic_corpus_by_kind    {'credential':11,'diagnostic':12,'known_over_redaction':4,'residual':3}  同         True
diagnostic_strict_entries    12                                         12                                         True
fidelity_cases               28                                         28                                         True
fidelity_unique_inputs       28                                         28                                         True
fidelity_unique_pairs        28                                         28                                         True
exact_nodeids                28                                         28                                         True
total_nodeids_collected      82                                         82                                         True
pytest_collect_returncode    0                                          0                                          True
pytest_collect_tail          82 tests collected in 0.05s                同                                         True
COUNTS_AGREE = True
rule_table_by_kind sums to entries: True
diag by_kind sums to entries: True
fidelity_cases == exact_nodeids: True
```

**自我校验确实存在**：`harness/report_counts.py` 末行

```python
# the nodeid count and the table length must agree; if not, one of them is wrong
return 0 if exact_nodeids == counts["fidelity_cases"] else 3
```

两处推导**彼此独立**：`fidelity_cases` 来自 `len(FIDELITY_CASES)`（模块导入），`exact_nodeids` 来自**调用 pytest 子进程**解析 `--collect-only` 输出（`"test_f08_output_fidelity_exact["` 行计数）。二者不等即 rc=3。另有 `test_f08_fidelity_pair_count_matches_the_mechanical_count` 在套件内同时断言 `counts["fidelity_cases"] == len(FIDELITY_CASES)` 与 `== counts["exact_nodeids"]`，使"手打数字"在**测试层**也无法存活。

### 4. 抖动结论按"区间 + 反证"阅读 ✅ **逐次捕获证据存在；cwd 长度是唯一受控变量**

**(4a) 深层/短路径的逐次捕获**（12 次运行，每次都有 rc + 完整 stdout + 分类判定）：

```
=== 深路径 basetemp（attempt 内），cwd 166/167 字符 ===
T0 child_without_runtime  run1/2/3  rc=1 failed cwd_len=167
T0 logon_wrapper_quoted   run1/2/3  rc=1 failed cwd_len=166
T4 child_without_runtime  run1/2/3  rc=1 failed cwd_len=167
T4 logon_wrapper_quoted   run1/2/3  rc=1 failed cwd_len=166
失败原文（T4 例）：FileNotFoundError: [WinError 206] 文件名或扩展名太长 ...
                 FileNotFoundError: [Errno 2] ... worker_launcher_events.jsonl
=== 短路径 basetemp（%TEMP%\i14c-flake-short），cwd 74/75 字符 ===
T0 child_without_runtime  run1/2/3  rc=0 passed cwd_len=75
T0 logon_wrapper_quoted   run1/2/3  rc=0 passed cwd_len=74
T4 child_without_runtime  run1/2/3  rc=0 passed cwd_len=75
T4 logon_wrapper_quoted   run1/2/3  rc=0 passed cwd_len=74
```

**唯一受控变量确为 cwd 长度**（166/167 vs 74/75），两棵树在**同一 basetemp 模式**下运行 —— 满足我上轮"两树须在同一 cwd 模式运行"的要求。

**(4b) "失败更多的那棵树在两轮间翻转"确有逐次捕获。** 我直接从 48 行结果重算（不读其汇总字段）：

```
n result rows = 48
交错顺序（前 8 行）：T0 pass1 run1 / T4 pass1 run1 / T0 pass1 run2 / T4 pass1 run2 ...
per (pass, tree):
  pass=1 tree=T0 failed=3/12
  pass=1 tree=T4 failed=2/12      -> pass1 worse = T0
  pass=2 tree=T0 failed=3/12
  pass=2 tree=T4 failed=4/12      -> pass2 worse = T4
  TOTAL T0 failed=6/24   T4 failed=6/24
FLIP = True
```

**翻转成立，且两轮合计 6/24 完全相同** —— 这正是"负载相关噪声"而非"树差异"的签名。

**(4c) 未能完全独立验证的一点**：`frequency-child_without_runtime.json` 的 48 行**只保存** `pass/tree/run/cwd/returncode/verdict/assertion/tail`，**不含每次运行的完整 stdout 文件**（其 `cwd` 指向 `%TEMP%\i14c-flake-freq\...`，该目录**仍在**、含 652 个文件，但不是本 attempt 内证据）。"每次失败都是同一条 `assert 3 == 2` on `child_started`"这一细节，我读的是 `review.md` 的陈述与 48 行的 `tail` 尾行，**未逐次打开原始输出核对**。深层/短路径那 12 次**是**完整捕获的，故关键的结构性结论（cwd 长度决定）**有完整证据**；频率层面的单次失败文本为**部分采信**。
（另：`frequency-logon_wrapper*.json` 不存在 —— 频率测量只对 `child_without_runtime` 做了，与"该节点才是 ~25% 抖动源"的结论自洽。）

### 5. guard 矩阵 ✅ **8/8 符合预期；"即使声明 scratch 根，生产路径仍 97"可复现**

存储证据 `r5/guard/matrix.json`：

```
n_cases = 8   all_as_expected = True
  declared-temp            real-driver              rc=3    expected=3        True
  attempt                  real-driver              rc=3    expected=3        True
  temp-undeclared          real-driver              rc=97   expected=97       True
  temp-plus-product        in-process-guard-probe   rc=0    expected allowed=false  True
  product-src-company-wiki in-process-guard-probe   rc=0    expected allowed=false  True
  product-source-catalog   in-process-guard-probe   rc=0    expected allowed=false  True
  product-revenue-forecast-outside-planning  in-process  allowed=false            True
  product-revenue-with-declared-root         in-process  allowed=false            True
```

**本人的独立反证（自带命令，不跑其脚本）**：

```
sys.path.insert(...harness); from run_guard import guard_run_dir
company-wiki src        -> BINDING-REFUSED (path is inside a product checkout) -> None
company-wiki\.source_catalog -> BINDING-REFUSED (path contains .source_catalog (a live catalog directory)) -> None
revenue-forecast\scripts -> BINDING-REFUSED (path is inside the revenue-forecast checkout but outside .planning) -> None
<my %TEMP% scratch>\ok\run -> <accepted>
```

并直接验证**驱动进程**层：run dir 在 `%TEMP%` 且**未声明** root → `returncode=97`、`run dir created: False`；声明我的 scratch root 后 → `returncode=3`（RE-RAISED）、目录被创建。**"声明 scratch 根也救不了生产路径"这一反证成立。**

### 6. 新增/改写 harness 脚本未越界 ✅

- **生产三仓零写入**：`company-wiki` porcelain 仅 ` M CLAUDE.md` / ` M README.md`（本卡之前就存在的用户改动）；`-- src tests scripts` 范围 porcelain **为空**；`filing-fetch` porcelain **为空**；`revenue-forecast` 的改动全部落在 `.planning/` 内。
- **生产模块仍等于 HEAD**（`git hash-object` 走过滤器）：`worker.py 5d700302…` = `HEAD:…`，`observability.py d9ce30df…` = HEAD，`cli.py c5038a9d…` = HEAD，`store.py 6ce3ff74…` = HEAD，`error_taxonomy.py e3bee2c7…` = HEAD。
- **`PLAN\reviews` 未被写**：`reviews` 目录 mtime = 2026/9/19 9:14:20（我第 4 轮记录为 10:05 的**父目录** `audit_report.md`/`delivery_validation.json` 亦未变），本轮与上轮观测一致。
- **`r5` 的 19 个子目录全部位于 attempt 内**（outside-attempt = 0）。
- **脚本静态审计**：r5 `harness\*.py` 中涉及生产路径的只有 `report_final_hashes.py` 的**只读** `CATALOG = Path(...catalog.sqlite3)`（仅 `stat()`），`run_guard_matrix.py` 的**只读**常量 `PRODUCT_ONE`/`TESTS`；两个驱动（`drive_real_exit.py:87`、`run_real_cli_exit.py:49`）均已改为调用 `guard_run_dir()`。

### 7. r4 的 6 项整改是否真的关闭 ✅ **逐条对号，全部关闭**

| r4 发现 | r5 整改 | 我的独立验证 |
|---|---|---|
| **R4-01** 计数错（23 vs 24，5 处） | `report_counts.py` 机械推导 + `counts.json` | ✅ 独立重算 44/30/28/82 全等；`exact_nodeids==fidelity_cases` 自校验存在且 rc=3 路径存在；套件内另有 pair-count 断言 |
| **R4-02** C13 后果低估一个数量级 | 4 处改写描述 + 3 条多行 fidelity 对 + 4 条表项 + 专门测试 | ✅ 我用自选 marker 复算 112→34；4 条多行用例已提取；`test_f08_c13_multiline_loss_is_frozen_not_hidden` 存在且按两种 marker 长度断言 |
| **R4-03** flake 声称无证据 | `run_flake_evidence.py` 逐次落盘 + `run_flake_frequency.py` 交错测量 | ✅ 12 次深/短路径捕获完整；48 行交错频率数据可重算翻转（6/24 各）；r4 的"3/3 passed"声称**已撤回** |
| **R4-04** 补丁不可 `git apply` | `make_posix_diff.py` 重新生成（POSIX 路径） | ✅ 我自建仓库 `--check`/`-p1` rc=0、三文件字节相同；无本地配置覆盖时同样成立 |
| **R4-05** 诊断表无 helper 兜底 | 与规则表对齐（`cannot_adjudicate` + rc=2） | ✅ T0 诊断表现返回 rc=2 / `verdict=cannot_adjudicate`，**无 traceback** |
| **R4-06** 退出码口径漂移（3 未被使用） | 两表改用 `0/2/3` | ✅ 实测 T1/T3 规则表 rc=3、T0 rc=2、T2/T4 rc=0；T1/T3 诊断表 rc=3 |
| **R4-07** hash 快照不全 | `attempt_porcelain` + `iso_venv` + `r4_reference` + 富条目（raw/LF/blob/`ls-files --eol`） | ✅ 见 §G：87 项检查全部通过（含 2 项为元数据键的伪失配，已排除） |

---

## 二、编号发现

### F-I14C-R5-01（P3，冻结件完整性：`oracle.md` r4 段被就地编辑，非纯追加）
**我上轮为 `oracle.md` 建立的性质是"逐字节追加"，本轮不成立。**

```
current oracle.md: bytes=18776 lines=315 sha=edbd0a93da9a197c
R5 addendum starts at line 282; bytes before it = 16465
r2 recorded prefix match:  None
r3 recorded prefix match:  None
r4 recorded prefix match:  None
longest prefix equal to r4 hash: None
```

r4 记录的长度为 16462 B，R5 之前的部分现为 16465 B —— **净增 3 字节，且三个历史 hash 全部不再是前缀**，证明 r4 段（或更早章节）被就地编辑过。

**逐行核对后的定性**：
- **章节结构未变**：`## 0.` … `## 5.`、`# R2 addendum`、`# R3 addendum`、`# R4 addendum`、`# R5 addendum` 全部在，行号与我第 4 轮读取时**逐条一致**（R3 addendum = 213，R4 addendum = 254，E4/N1/N2 在 95/99/103，`## 4.` = 106，`## 5.` = 114）。
- **r4 段的冻结语义未改**：第 265–272 行仍是"Fidelity is exact…The table scripts exit 2 on any mismatch"与"C13 … `a=1 token=<marker> b=2` … E4b acceptance length (193) is derived from it"，与我上轮读取**逐字相同**。
- **唯一的实质变化**：R4 段"exit 2 on any mismatch"这一句在 r5 已被 `# R5 addendum` 第 291–293 行的新约定（`0/2/3`）**显式取代**，且 R5 附录明确写了取代关系 —— 也就是说，被改的（若有）不是冻结结论本身，而是被**后置附录正确标注为 superseded** 的部分。
- **实现者未披露这 3 字节的差异**：`review.md` / `handoff.json` / `decision.md` / `oracle.md` 中检索 `append-only|3 bytes|rewrote` 均**无命中**。

**影响**：不改变任何判据或结论（冻结语义完好、R5 附录正确标注取代关系），但**上轮明确要求的"只许追加/不得改冻结件"边界被越过且未披露**。若下一轮继续沿用"前缀 hash 证明"作为冻结完整性的证明方式，这条通道将不再可用。
**最小修法**：仅在 `review.md` 的 r5 节追加一句事实说明（"`oracle.md` 的 r4 段在本轮被就地编辑，净增 3 字节，三个历史前缀 hash 不再匹配；冻结语义经逐行核对未变，R5 附录已标注取代关系；本轮未保留 r4 副本，故无法给出逐字节 delta"）。**只许追加，不得再改 oracle.md 既有字节。**

### F-I14C-R5-02（P4，`handoff.json` 对 short-basetemp 的表述与两份并存记录不一致）
`handoff.json` 写：`short basetemp -> T0 6/6 passed, T4 4/6 with assert 3 == 2 on child_started`。
但 `r5/flake-evidence/short-basetemp/` 内**并存两份互相矛盾的记录**：

```
short-basetemp\stdout.txt      (827 B, 无 cwd_len 字段)
  T0/child_without_runtime run1/2/3 rc=0 passed
  T0/logon_wrapper_quoted  run1/2/3 rc=0 passed
  T4/child_without_runtime run1 rc=1 failed / run2 rc=1 failed / run3 rc=0 passed   <-- T4 1/3 失败
  T4/logon_wrapper_quoted  run1/2/3 rc=0 passed

short-basetemp.stdout.txt      (另一次调用，带 cwd_len)
  T0 全部 rc=0 passed（cwd_len 75/74）
  T4 全部 rc=0 passed（cwd_len 75/74）

short-basetemp\summary.json + 12 个 per-run .txt 捕获
  T0 3/3 passed, T4 3/3 passed（与 review.md 表格一致）
```

即：**`handoff.json` 引述的是那个已被取代的 ad-hoc 观测**（且其"4/6"与文件里的"2 of 3"也不吻合），而 `summary.json` 与 12 份逐次捕获是**全绿**的另一次运行。
**缓解事实**：`review.md:71-118` 对这段历史**记录得完整且正确** —— 明确写了"an ad-hoc short-basetemp capture happened to show it on T4 in 2 of 3 runs and never on T0, which would have looked like a card-caused regression. It is not"，并给出两次频率预跑的 T0 6/12 vs T4 5/12 与 T0 0/12 vs T4 7/12、以及为何改为交错测量。**关键结论（抖动是负载相关、非树差异）表述无误且证据充分。**
**最小修法**：把 `handoff.json` 那一句改为指向 `review.md` 的叙述（或删去具体分数，改为"short basetemp 下该节点仍以 ~1/4 概率抖动，见 review.md"）。**只许追加/替换该字段值，不得改其他已冻结字段。**

### F-I14C-R5-03（P4，频率证据未落逐次原始输出）
`r5/flake-evidence/frequency-child_without_runtime.json` 的 48 行**只有** `pass/tree/run/cwd/returncode/verdict/assertion/tail`，没有像深/短路径那样为每次运行保存 stdout 文件；其 `cwd` 指向 `%TEMP%\i14c-flake-freq\`（该目录仍在，652 个文件）。因此"每次失败都是同一条 `assert 3 == 2`"**只能靠 `tail` 与 `review.md` 采信**，不能像深路径那样逐次复核。
**最小修法**：下一轮把 `--capture-per-run` 语义（深路径已有）也对频率测量打开，或把 `%TEMP%\i14c-flake-freq` 的 tail 汇总**复制进 attempt**（不删原目录）。

---

## 三、必做验证的命令与原始输出（索引）

| # | 项 | 命令要点 | 结果 |
|---|---|---|---|
| A | 十次表调用（5 树×2 表） | `python harness/run_rule_table.py --src iso/<tree>/src --label REVIEW-<tree> --out ...` | rc 2/3/0/3/0 与 2/3/0/3/0；T3 = 0 泄漏 + 27/13 保真失败 |
| B | 逐字符精确性 | scratch 注入 `<redacted>`→`<redacted>!`；注入移除 `;` 终止符 | rc=3 / 32 与 15 条失败；rc=3 / 2 条失败 |
| C | 计数重算 | 导入三表 + 独立 `pytest --collect-only` | 44/30/28/82 全部相等；自校验 `return 3` 存在 |
| D | 退出码口径 | 受控于 `negative = (not fidelity_ok) or leaks or touched/new_over` | 与 `run_card.py` 的 `0/2/3` 一致，r4 漂移已修 |
| E | 套件复跑 | `pytest ... --basetemp=<review scratch>` ×3 | **82 passed** in 22.1s / 21.4s / 22.0s（其一 `I14C_RUN_ROOT` 完全未设） |
| F | 方向性（未新增过redaction） | 见 §A 表与残留集合 | 残留集合仍为 `digest=` / `--api-key` / JSON 引号键 / 裸 marker |
| G | 全量 hash | 重算 `final_hashes.json` 全部条目 + 生产 blob vs HEAD | **87 项检查，0 处真实失配** |
| H | 生产不可变 | `git hash-object` vs `HEAD:`、porcelain、`src/tests/scripts` 范围 | 三仓零写入；5 个模块 blob = HEAD |
| I | iso-only | r5 全部子目录归属 | 19/19 在 attempt 内 |
| J | oracle/review 追加性 | 前缀 hash 搜索（r2/r3/r4） | **均不再匹配 → `oracle.md` 被就地编辑（发现 1）** |
| K | 诚实性 | `handoff.json.status` / `blocked_by` / carry 可见性 | `review_pending`、`blocked_by=[]`、19 条 open_questions、C1–C13 全部在册 |

### G 项明细（hash）

```
### r5_documents        OK binding.json / oracle.md / commands.json / decision.md / review.md / handoff.json
                        OK changes.diff / r2-changes.diff / r3-changes.diff / r4-changes.diff / r5-changes.diff
### r5_harness          OK 23 个脚本全部相符（含 run_rule_table.py 10b406d7…、run_guard.py 05ee904c…、
                        run_r5_commands.py 1223fd13…、tests/test_i14c_real_exit_redaction.py 672b88de…）
### iso_trees           OK 6 树 × 8 模块 = 48 项全部相符
                        （product_fixed/observability.py c5608c4b…；product_r3/observability.py 28b1dd56…）
### production_modules  OK 8 模块 raw_sha256 全部相符（worker e8317991… / observability a73826aa… / cli fad88c60…）
### T4 LF 形式          OK product_fixed/observability.py lf=049f5d5b… == r4 pin（内容未变，仅行尾归一）
### production blobs    OK worker 5d700302… / observability d9ce30df… / cli c5038a9d… / store 6ce3ff74… /
                        error_taxonomy e3bee2c7… 全部 == HEAD
### production_catalog  OK size=49677344768 wal=0 shm=32768
### worker_control      OK 9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd
HASH_CHECKS total=87 mismatches=2   <- 这 2 项是 production_modules 下的 core_autocrlf / note 元数据键，
                                       被我的通用遍历误当 hash（我的脚本问题），排除后 0 处失配
```

**r5 的 hash 账本是本卡至今最完整的一次**：每条生产模块同时给出 `raw_sha256`、`lf_normalised_sha256`、`git_blob_hash_HEAD`、`git_hash_object_filtered`、`git_hash_object_no_filters`、`git_ls_files_eol`、`worktree_matches_HEAD_blob_after_filters`。我逐项复算，并独立确认 **CR/LF 计数与声明相符**：

```
worker.py        48075 B  crlf=1084 lone_lf=0   raw=e8317991…
observability.py 30087 B  crlf= 625 lone_lf=0   raw=a73826aa…
cli.py           65694 B  crlf=1568 lone_lf=0   raw=fad88c60…
iso/product 三模块与生产 **字节相同**（byte-identical: True）
```

r4 遗留的"CRLF sha256 vs HEAD blob"口径矛盾**确已解决**，且解释正确（`core.autocrlf=true` ⇒ 工作树 CRLF / blob LF；`hash-object`（带过滤器）等于 HEAD blob，`--no-filters` 不等于）。

### 行尾归一化：一处诚实的、可核验的变更
`iso/product_fixed/observability.py` 的 CRLF 形式由 r4 的 `6b6ce5…`（40060 B，LF 形 `049f5d5b…`）变为 r5 的 `c5608c4b…`（40060 B，LF 形仍为 `049f5d5b…`）。**内容未变，只有行尾由混合变为统一 CRLF。** 依据：

```
product_fixed observability.py 40060 B  crlf=864 lone_lf=0
T4 LF-normalised = 049f5d5b27fd37bc18770b903015184c11d60022f6d0dee37e0d786c52ad22cf  == r4 pin  ✓
r5-changes.diff 施加后三文件与 T4 字节相同（§J）
```

实现者在 `handoff.json` 的 `F-I14C-R4-04` 条目中**主动披露**了这一点及其动机（"iso/product_fixed observability.py was LF while T0 is CRLF, which had made the patch a whole-file rewrite; after normalisation it is 1 hunk and the suite is still 82 passed"）。**这是正确做法**，且我确认归一化后判据未松（T3 仍 27/13 保真失败，T4 仍 0/0）。

---

## 四、本人**未能验证**的部分（明确列出）

1. **频率测量 48 次运行的逐次原始输出 —— 未验证。** 只保存 `tail`（发现 3）。结构性结论（cwd 长度、翻转、6/24）我已从 48 行数据独立重算确认；"每次失败都是同一条断言"为部分采信。
2. **`oracle.md` 的具体逐字节 delta —— 无法取得。** 三个历史版本均无副本（attempt 内无备份；git 中该文件已被提交为 r5 版本，`HEAD` blob = 当前 worktree = `94b4e8fe…`），故只能给"净增 3 字节 + 前缀不再匹配 + 行号/语义逐条比对通过"这一层结论，**无法列出被改的具体字节**。
3. **短 basetemp 那次 ad-hoc 观测的原始输出 —— 未留存/未能核对。** `handoff.json` 引述 T4 4/6，现存 `short-basetemp\stdout.txt` 显示 T4 1/3 失败，`summary.json` 显示全绿；三者无法互相推出，我无法判定 `handoff.json` 的数字具体来自哪一次运行。
4. **`compat` 的 5 次运行中的"更早一轮"（3,4,4,5,5）—— 未验证**（`review.md` 明示"not the recorded one"，其原始输出不在 r5 证据内）。
5. **`iso_venv` 的 dist-info RECORD hash 与 `python.exe` sha256 —— 未逐一复算**（`r5/final_hashes.json` 已记录；我只确认解释器版本 3.13.9 与 `sys.prefix` 指向 attempt 级 venv，并读到 `iso-venv-pip-list.txt` 的 pytest 9.1.1 / PyYAML 6.0.3 / requests 2.34.2）。
6. **`2f5c5740…/65553` 的来源 —— 仍未追溯**（r1 遗留"来源不可考"；不影响 r5 任何结论）。
7. **bench 其他 9 种形状的秒数 —— 未重算**（我第 4 轮只重算 `underscore-segments`；本轮未重跑 bench，`bench_redact.py` 哈希未变）。
8. **产品 `revenue-forecast` 工作树在 `04:35:31–04:40:53` 被重置并恢复这一事件 —— 未独立复核。** 我按你给的环境事实记录，并据此限定：**本报告 §H 的全部"生产零写入"结论，观测时点为本复核窗口（2026-09-20 03:48Z 起）**；`company-wiki` 三仓在该窗口内确为零写入。该事件的影响范围我只做了"当前状态核对"（8 个受影响文件我未逐条复算，仅核对本卡相关模块）。
9. **`sync_commands_json.py` 的"29 条旧条目保留 + 16 条 r5 条目追加"—— 未逐条 diff**（我确认了 `r5/commands.json.before-r5-append` 存在、`commands-r5-rc.json` 内 29 条 r5 调用 `all_as_expected=true`）。

---

## 五、对三个明确问题的回答

### 1. 判定
**`accepted_scoped`** —— 范围与第 4 轮口径一致：**证据与判据成立**；**不含产品化授权**。C12 仍为促销硬前置（实现者亦自述如此）。

### 2. 若拒，最小修法（**本判定非拒**，但以下 3 项建议在下一轮顺带清理；均**只许追加/不得改冻结件**）
- **发现 1（建议优先）**：在 `review.md` r5 节**追加**一句，披露 `oracle.md` r4 段被就地编辑、净增 3 字节、历史前缀 hash 失效、冻结语义经核对未变、且无逐字节 delta 可给。**不得再改 `oracle.md` 既有字节。**
- **发现 2**：把 `handoff.json` 中 `short basetemp -> T0 6/6 passed, T4 4/6 …` 一句**替换为指向 `review.md` 的叙述**（或删去具体分数）。仅动该字段值。
- **发现 3**：下一轮为频率测量打开逐次 stdout 捕获（深路径已有该能力），或把 `%TEMP%\i14c-flake-freq` 的 tail 汇总复制进 attempt（**不删原目录**）。

### 3. 四个待 owner 裁定的开放问题 —— **均不阻塞我的判定**
- **C13 是否单独立卡**：不阻塞。C13 已按我上轮要求"保留现状 + 显式冻结 + 描述更正"完成；是否需要一张卡把它改成单 token 语义，是**范围与风险偏好**问题（会移动 E4b 的 193 基线与 envelope 宽度），属 owner 决策，我**不代为裁定**。
- **~25% 抖动是否另立卡修产品测试时序假设**：不阻塞本卡。抖动已定量（T0 6/24、T4 6/24、翻转、两轮翻转），且已证明**非本卡所致**（唯一 diff 的两处 `worker.py` 改动不在该节点路径上；我复核了 `r5-changes.diff` 的 worker.py 3 个 hunk：import 行 + `_write_unhandled_exception_event`）。是否修产品测试时序，属 owner 决策。
- **深层 cwd 的 WinError 206 是否在产品侧改为短路径 basetemp 约定**：不阻塞本卡。这是**环境/测试约定**问题（166/167 字符即触 Windows 路径上限），本卡已把它测成"两树同因失败"。属 owner 决策。
- **C12 的具体形式（`pytest-timeout` 依赖新增 vs 子进程包裹）**：不阻塞本判定，但**阻塞促销**。我上轮与本轮均实测该用例在阻塞实现下**挂死**（>90 s）；本卡不授权改产品测试，故必须由下一轮产品侧实现落地其一。属 owner 决策（但任一形式都必须实测"阻塞 ⇒ FAIL"）。

---

## 六、给下一轮的最小行动清单
1. **P3-必做（文档诚实性）**：发现 1 —— 在 `review.md` 追加 `oracle.md` 编辑事实的披露（只追加）。
2. **P4**：发现 2 —— 修正 `handoff.json` 对 short-basetemp 的表述。
3. **P4**：发现 3 —— 频率证据补逐次捕获。
4. **C12（促销硬前置）**：产品侧 `pytest-timeout` 或子进程硬超时包裹 + "阻塞 ⇒ FAIL"实测。
5. 保持 `handoff.json` 对 stderr 要求的限定表述（"fully met only for credential-shaped markers on exits reachable through `main()`'s handler; C6/C7 are the named residuals"）**不得放宽**。

---

## 附：本轮可复算脚本（均在 `%TEMP%\i14c-r5-review-20260920-044801\`）
`inv.py`（树清单）· `g_hashes.py`（全量 hash 重算）· `ja_gitapply.py` / `gitapply2.py`（`git apply` 复现，含无本地配置覆盖）·
`fidelity_exact.py`（1 字符 / 单条目注入）· `counts.py`（计数重算 + 多行用例提取）·
`eol.py`（行尾组成分析）· `prodcheck.py`（生产 vs iso 字节比对）· `appendonly.py` / `oracle_diff.py`（追加性）·
`guard2.py`（guard 反证 + 驱动层 97）· `probe.py`（用自选 marker 的独立探针）。
原始输出：`RT_*.json` / `RT_*.stdout.txt`（十次表调用）、`mut-one-char-*.json`、`mut-one-entry-*.json`、`gitapply_result.json`、`pytest-*/`（三次套件复跑）。
---

## 转录与三项发现处置（implementer 追加，2026-09-20；本节之前的所有字节未被改动）

### 0. 转录证明（只追加）

| 项 | 值 |
|---|---|
| `review.md` 追加前 sha256 | `337a91f55ecf70f9d3772b8a812a6a7dc4bbdb43a925d23c499143a273edd32f` |
| `review.md` 追加前字节数 | `55673`（末字节 LF，全文纯 LF：CR=0、LF=822） |
| reviewer 原文（`REPORT.md`）字节数 / sha256 | `34121` / `8e2523947da8c3e7e86aa5e5834ef893b71634879ba1404f217695d251569051` |
| 转录方式 | 二进制追加：`# r5 — INDEPENDENT REVIEW (round 5)` 标题 + reviewer 原文逐字节，一字未改，未做行尾转换（原文亦为纯 LF） |
| 追加后 `review.md` sha256 / 字节数 | 见 `evidence/I-14-C/verdict_transcription_r5.json`（追加后写入，避免自引用） |
| 前缀校验 | 追加后文件前 `55673` 字节的 sha256 == `337a91f5…`，即既有字节逐字节未变 |

### 1. F-I14C-R5-01（`oracle.md` 就地编辑）—— 按 reviewer 要求披露

`oracle.md` 在 r5 的编辑**不是纯追加**：R5 附录之前的净增 **3 字节**（16462 → 16465），
r2/r3/r4 三次记录的前缀 hash **均已不再匹配**；经 reviewer 逐行核对，章节结构与行号未变、
r4 段的冻结语义（含 C13 条目与 E4b-193 的推导）逐字完好，且 R5 附录已明确标注新的 `0/2/3`
口径**取代** r4 段的 `exit 2 on any mismatch`。本轮**未保留 r4 副本**，因此**无法给出逐字节
delta**。自本节起，`oracle.md` 的既有字节冻结，不再修改；“前缀 hash”这一证明通道对本文件
不再可用，后续以显式 supersede 标注取代。

### 2. F-I14C-R5-02（`handoff.json` 的 short-basetemp 分数）—— 已删除分数、改为指向本文件

`handoff.json` 的 `r5_disposition.F-I14C-R4-03_flake_claims` 与 `open_questions` 中原引述的
“T0 6/6 passed, T4 4/6”已删除：该数字来自**已被取代的 ad-hoc 观测**，且与存留文件
（`r5/flake-evidence/short-basetemp/stdout.txt` 显示 T4 3 次中 1 次失败）互相矛盾。字段现改为
“short basetemp 下该节点仍以约 1/4 概率在两棵树上抖动，见 `review.md` 的 F-I14C-R4-03 叙述”。
`short-basetemp/` 下并存的两份记录未被删除，作为该轮历史的证据保留。

### 3. F-I14C-R5-03（频率测量缺逐次原始输出）—— 已补齐，并就地更正一句话

48 次运行的**完整 stdout** 已从原 scratch 根 `%TEMP%\i14c-flake-freq`（**原样保留、未删**）
复制进 `r5/flake-evidence/frequency-captures/`（48/48，逐份 sha256 校验通过、
`all_copies_verified=true`；见 `frequency-child_without_runtime.json` 新增的 `captures` 块及
`harness/copy_frequency_captures.py`）。**48 行既有数据一字未改**（reviewer 是据此重算的），
`harness/run_flake_frequency.py` 现已自带逐次捕获，后续运行无需补录。

**就地更正（本次逐份核对后才发现）**：此前“每次失败都是同一条 `assert 3 == 2`”的说法**不准确**。
48 份原始输出显示失败共 12 次，断言**表达式相同**（`len([e for e in events if e["status"] ==
"child_started"]) == 2`），但**观测值有两种**：`assert 3 == 2` **10 次**、`assert 4 == 2`
**2 次**（均在 pass2/T4：run1、run5）。因此正确表述是：**同一断言、同一失败机制（监督进程
多重启 1–2 次），观测计数为 3 或 4**；这**不改变**结构性结论（负载相关抖动、两树同因、
翻转成立：p1-T0 3 vs p1-T4 2、p2-T0 3 vs p2-T4 4、合计 6/24 对 6/24），但 reviewer 标注为
“部分采信”的那一条细节，现以更正后的口径**完全可核验**。reviewer 原文与本更正并存，不改前者。

### 4. 载体（非自签；照抄 reviewer 口径）

- `handoff.json.status` = `accepted_scoped`；`evidence/I-14-C/qualification.json` 的
  `formula.state` = `accepted_scoped`。
- 范围：**r5 时点的“证据与判据”成立**（F-I14C-08 关闭依据 + r4 六项整改 + 机械计数 +
  可复跑性）；**不是产品化授权**：`not_an_authorisation_to_promote = true`。
- 硬前置与未做项原样保留：**C12 仍是促销硬前置**（F-07 用例在 redactor 阻塞时挂起 >90 s，
  必须由产品侧 `pytest-timeout` 或子进程硬超时落地，并交付“阻塞 ⇒ FAILS”实测），
  **验收测试仍未提升**（C9）。
- `implementer_signed: false`、`implementer_never_signs_acceptance: true`、
  `authority: "acceptance was written by an independent reviewer, not by the implementer"`；
  `disclosure_adaptation` / `accuracy` **未动**。
- 四个待 owner 项（C13 是否立卡 / ~25% 抖动是否立卡 / 深路径 `WinError 206` 是否改为短
  basetemp 约定 / C12 的具体形式）已**原样承接**进 `handoff.json.open_questions`，
  实现者**未自决**。

### 5. 封盘

本文件在该节写入后不再修改；`oracle.md` 既有字节冻结；生产三仓零写入；未执行任何 git 写命令；
`PLAN\reviews` 未写。