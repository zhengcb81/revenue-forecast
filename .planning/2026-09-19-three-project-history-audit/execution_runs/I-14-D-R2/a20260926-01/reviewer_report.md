# I-14-D-R2 — 独立复审报告（凭证持久化回归修复轮）

| 项 | 值 |
|---|---|
| 卡 | `I-14-D`（派单轮次 `I-14-D-R2`，修复轮） |
| 被审 attempt | `execution_runs/I-14-D-R2/a20260926-01`（`status=review_pending`） |
| 复审工位 | **独立复审**（非实现者；未编辑任何实现者产物） |
| 复审时间 | 2026-09-26 21:0x–21:2x |
| 档位 | A 级全量档（产品安全修复） |
| 写入面 | **本目录 2 个新文件**：`reviewer_report.md` + `reviewer_report.sha256`；复审脚本与全部跑测输出隔离在 `%TEMP%\i14d_r2_review\`（`TEMP=C:\Users\郑曾波\AppData\Local\Temp\dsh-hrOhcq`） |
| 禁项 | 未写产品仓（`company-wiki` 只读）· 无 git 写 · 未跑 `git status` · 未联网 · **不写卡状态** |

---

## 0. 裁决行

**ACCEPT — `I-14-D-R2/a20260926-01` 通过独立复审。**

- 四项 P1 触发条件**全部未触发**：落盘探针显示**修复有效**（明文凭证不再落盘）· **4/4 变异全红且具名** · `changes.diff` **双向可逆且字节 round-trip** · **封盘/旧 attempt 0 字节被动**。
- 判据链自洽：oracle 冻结前缀 sha 可复算、追加结构成立、§3/§4 判据逐条手算复核无误、实现的修复与复审 RULING 2 原型**逐字节同款**。
- 带 **4 条 P3**（字段命名/冻结时点取证/A.3 无判据覆盖/词表外残留），均不构成 `changes_required` 依据。
- 本工位**只出报告，不写卡状态、不产生 ACCEPT 落卡、不放行任何参数**。

---

## 1. 被审四件 · 收尾复哈希

复审开始与结束各复算一次，两次一致（结束值如下）：

| 文件 | 字节 | sha256（复审收尾复算） | 与 handoff 一致 |
|---|---|---|---|
| `oracle.md` | 22,936 | `a3a0a5df41695ae5ac62239db716ae126d50823ef3b364dc6187f8b508f3fcf6` | ✅ `written_files` |
| `changes.diff` | 1,636 | `a4d6fad2da012125e1272d6aaa1021213e83cd8d0462d86fd2766978b3a7d733` | ✅ |
| `red_green_mutations.json` | 9,417 | `b0ec2738b4c48d8cd34421ff3cf3855a9b6e36cadf7d8808dfd8124a73ed77fa` | ✅ |
| `handoff.json` | 19,651 | `090dfc450db05697295007708e8070d4a355ff3717ce9df149a11c3379f1ed09` | 自指文件，handoff 声明不记自身 sha |
| `oracle.sha256`（sidecar） | 261 | `cb086754f4d565fde95e7e42f45ff997e88e484330e6f347e0a78d5234b20e60` | — |
| `before/observability.py.preimage` | 40,476 | `e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0` | ✅ |

**冻结前缀**：`oracle.md` bytes 1–18054 的 sha256 = `71cbff493122d1f0905fd0eb5b6bfed0b0d7d0128bcdf475748bf32750ab1383` ✅（与 sidecar 第 1 行、`handoff`、`red_green_mutations.oracle` 三处一致）；前缀末尾恰为 §8 第 5 条结尾 `…the independent reviewer is dispatched separately by the parent.\n`，其后才是 `\n---\n\n# APPENDIX …`，即**判据正文（§0–§8）整体落在冻结区，APPENDIX 完全在外**，追加部分只记录结果不改判据（我逐行读过 A.1–A.6，无新增通过条件）。

---

## 2. 回源核对（V2-4 只读清单）

| 引用 | 实测 | 结果 |
|---|---|---|
| 上游 `I-14-D/a20260919-01/reviewer_report.md` | 37,659 B / **583 行** / sha `499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b` | ✅ 与 handoff `input_hashes` 逐字一致 |
| `L18` | `**CHANGES_REQUIRED — the attempt is NOT accepted.**` | ✅ 逐字 |
| `L25-L30` 缺陷原文 | `…on iso/product_narrow the persisted event is "Authorization: <redacted>\n<SECRET>\ndoc=17" — the full credential is written to the append-only event log in plaintext.` | ✅ 逐字（含引用块） |
| `L56` 实测字节 | `product_narrow (deliverable) \| e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0 \| 40476 \| yes` | ✅ 与本轮 pre-image **同 sha 同字节** |
| `L283-L286` 要求的补救 | scheme-aware fail-closed + LF/CRLF/obs-fold/`authorization: token\n` 四行族 + 复跑 | ✅ 本轮 §3 即此四族 + 复跑 |
| `L479` 目标落盘值 | persists as `"Authorization: <redacted>\ndoc=17"` | ✅ 本轮实测达成（§3.2） |
| `L485-L488` 命名的代价 | `Authorization: Bearer\ndoc=17` 会被过度脱敏 | ✅ 已在 oracle A.3 / handoff `open_questions` 登记 |
| `L470-L472` 复审原型代码 | 与 `changes.diff` 新增的 `_AUTH_SCHEME_SPLIT` **逐字符相同**（同 9 词表、同 value 组次序） | ✅ 修复=复审自测原型 |
| 卡 `execution_v2/card_I-14-D.md` | 2,369 B / sha `5e5cdaaac186a4a7b6595e8ed33302b5c63ce4472256c2cbc8e5eaef64760114` | ✅ 与 handoff `card_face_verbatim` 一致 |
| `OWNER_DECISIONS.md §三十七` | sha `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d`，标题「全沙箱操作常设授权」，边界含「产品仓提交不在本授权内」 | ✅ 与 handoff 一致 |
| 旧 attempt 三件 | `oracle.md cfc09f99…`/49,714 · `handoff.json c1facfb1…`/22,407 · `changes.diff 4c0160b8…`/5,101 | ✅ 全部与 handoff `input_hashes` 一致（收尾复算亦一致） |

---

## 3. 五项全量复核

### 3.1 裁决行 + 发现清单

上游复审的发现清单（我按 `reviewer_report.md` 原文逐条核过等级）：

| id | 等级（原文） | 本轮状态 |
|---|---|---|
| **F-REV-D-01** | **BLOCKER (high)** — auth 路径把凭证明文写进 append-only 日志（L228） | **本轮修复对象 → 已闭环（§3.2 实证）** |
| F-REV-D-02 | MEDIUM（L288，`_VALUE` 死常量） | 未修，**已登记为 carry**（handoff `open_questions` 第 3 条） |
| F-REV-D-03 | MEDIUM（L305，digit-suffixed 凭证名原子表缺口） | 未修，已登记 carry |
| F-REV-D-04 | LOW（L320，`Authorization:\ndoc=17` 键侧换行，既有非回归） | 未修，已登记 carry |
| F-REV-D-05/06 | LOW 文档/表述（L335/L344） | 不在本派单范围 |
| F-REV-D-07 | INFO 外部漂移（L352） | 不在本派单范围 |
| 本轮新增登记 A.3（过度脱敏代价） | — | 披露、未修、**未被任何 §3/§4 判据覆盖**（→ P3-3） |
| 本轮新增登记 A.4（词表外 scheme 残留） | — | 披露、未修（→ P3-4） |

派单范围 = D-01（L283-L286 补救 + L479 目标），D-02/03/04 在复审原文中即为更低等级的独立条目，实现者按范围登记而非"顺手改绿"，**处理正确**。

实现者自报：`gate0_passed=true`、`secret_persistence_fixed=true`、红 3 / 绿 0 / 变异 `M1-M4` 全 3、`mutations_required=3`、`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`。以上我**独立复算全部成立**（下文）。

### 3.2 ⭐ 缺陷修复实证 —— 我自己的落盘探针（%TEMP% 隔离）

探针脚本 ` %TEMP%\i14d_r2_review\my_persist_probe.py`（**复审自写，非实现者 harness**）：直接以非绑定方法调用被测树里**真实的** `SourceCatalogWorker._write_unhandled_exception_event`（`worker.py:1050-1068`）→ `_write_process_event`（`worker.py:1070-1084`），`state_path` 指向 `%TEMP%`，把 2 条真实异常事件（39 字符合成凭证 + 21 字符 marker）**追加写进 `worker_process_events.jsonl` 再读回**。为防"导入到别的树"，每次运行打印 `observability.__file__` 校验。

| 树 | 模块实际加载路径 | 探针 rc | 读回的 `message_redacted` |
|---|---|---|---|
| `iso/product_pre`（`e8abd522…/40476`） | `…\iso\product_pre\src\company_wiki\source_catalog\observability.py` | **3** | `"Authorization: <redacted>\nghp_ZQ7ReviewerFakeCredential0123456789\ndoc=17"`（两行均带明文） |
| `iso/product_post`（`8dab63d9…/41304`，+828 B） | `…\iso\product_post\src\…\observability.py` | **0** | `"Authorization: <redacted>\ndoc=17"` |

- **pre 臂与复审 L30 的原文逐字节相同**（缺陷复现）；**post 臂与复审 L479 的目标逐字节相同**（secret 消失 **且** `doc=17` 存活，两半同时满足）。
- 判据 `secret_absent / has_redacted / doc17_kept / le_200` 四项 pre 全否、post 全是。
- 树级等价：`iso/product_pre` vs `iso/product_post` 均 **152 文件、路径零差异、内容差异恰 1 个** = `company_wiki/source_catalog/observability.py`（+11 行，CRLF 全保：pre 866 CRLF / post 877 CRLF / **lone-LF = 0**）。
- `iso/product_pre` 与只读旧 attempt 的 `iso/product_mut_authsplit/src` **152/152 字节全等**，源树 `observability.py` mtime 仍为 2026-09-21 21:00:15（**只读来源未被动**）。

### 3.3 变异复跑 —— 4/4 红且具名（原件 sha 不动）

复审自行复跑 `harness/run_oracle_r2.py`（28 判据：§4 A0-A17 + §3 P1-P11）与自写落盘探针：

| 变异 | 单点编辑（我 diff 出来的，每树与 `product_post` **仅 1 行、仅 1 文件**差异） | oracle rc | 具名失败行 | 继承 §4 | 我方落盘探针 rc |
|---|---|---|---|---|---|
| **M1** 只修 narrow 不修授权路径 | `_AUTH_PATTERN` value 组去掉 `\|_AUTH_SCHEME_SPLIT` | **3** | `P1,P2,P3,P4,P5,P6,P7,P8`（**8 行全部 secret_absent=false**） | 全绿 `[]` | **3**（明文落盘） |
| **M2** 去 bearer/token | 词表 → `(?:basic\|digest\|oauth\|jwt\|apikey\|api_key\|sso)` | **3** | `P1…P8`（8 行泄漏） | `[]` | **3** |
| **M3** 越行吞诊断 | token 变多行 run `(?:…\r?\n…)+` | **3** | `P1,P2,P8`（诊断被吞），**leak=[]** | `[]` | **3**（`doc=17` 丢失） |
| **M4** 仅 LF | `\r?\n` → `\n` | **3** | **`P6-crlf`**（唯一） | `[]` | **0**（探针输入为 LF，符合预测） |

- 派单硬要求「只修 `iso/narrow` 不修授权路径必须红」→ **M1 rc=3 且 P1-P8 全泄漏** ✅。
- 与 `red_green_mutations.json` 的 `predicted_failure` **逐行吻合**（`prediction_matched=true` 属实）；`oracle_rc {M1:3,M2:3,M3:3,M4:3}` 与我复跑一致。
- **原件 sha 不动**：4 个 `_mut/*/observability.py` = `a724850c…`/`29f6f860…`/`a9470c44…`/`d9281d1d…`（与 JSON `tree_sha256` 一致）；每树 152 文件与 `product_post` 相比路径 0 差异、内容差 1；`product_post` 本身在变异构建后仍由 `evidence/final_green_oracle.json`（20:54:09，晚于全部变异）复验 `verdict=pass`。
- 红臂同理：`iso/product_pre` = 继承 §4 全绿 + §3 P1-P8 泄漏 → `RED-auth-only`, rc 3（我复跑一致），与"缺陷仅在授权路径"的复审结论相符。

### 3.4 `changes.diff` 真实性与双向 round-trip

| 检查 | 结果 |
|---|---|
| 结构 | 1 个 hunk / **1 个文件** `src/company_wiki/source_catalog/observability.py` / POSIX 正斜杠 / `git apply --stat` → `1 file changed, 12 insertions(+), 1 deletion(-)`，`--numstat` → `12 1` |
| `git apply --check -p1`（正向，作用于 `iso/product_pre` 的副本） | **rc = 0** |
| `git apply --check -p1 -R`（反向，作用于 `iso/product_post` 的副本） | **rc = 0** |
| 反向 sanity（方向搞反必须失败） | 正向-check on post = rc1、反向-check on pre = rc1 ✅（说明 check 真在干活，不是恒 0） |
| 正向 apply 后整树 vs `iso/product_post` | **152/152 字节全等**，`observability.py` sha = `8dab63d9…` |
| 再反向 apply 后整树 vs `iso/product_pre` | **152/152 字节全等**，sha 回到 `e8abd522…` |
| **双向 round-trip 字节一致** | ✅ 成立（我方独立于实现者 `verify_diff_r2.py`） |
| `index` 头 `842d0cfbc7e3..ff9c65586cff` 真实性 | 我按 `sha1("blob <n>\0"+content)` 自算：pre = `842d0cfbc7e3941dd…`、post = `ff9c65586cffce2de…`，**前 12 位精确吻合** → 该 diff 确由这两个文件生成 |
| git 写 | 未 `--index`/`--cached`；`git --no-optional-locks diff --cached --name-only` → **0 entries**（index 未动）；`git --no-optional-locks -c core.quotepath=false diff HEAD --name-only` → 3,830 条、**non_planning = 0**（与 handoff `git_diff_measurement` 一致）；**全程未跑 `git status`** |

### 3.5 封盘 / 上游

| 检查 | 结果 |
|---|---|
| **`I-11-A hypotheses` 封盘** | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` = **`f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`**，51,697 B，mtime **2026-09-20 15:48:19** → **0 字节变动** ✅ |
| **旧 attempt `I-14-D/a20260919-01` mtime** | mtime ≥ 2026-09-26 00:00 的文件 = **0**；全树最新文件为 `iso/product_narrow_r6/…/__pycache__/observability.cpython-313.pyc`（2026-09-23 22:41，属更早会话）→ **本轮 0 写入** ✅ |
| 上游四件 sha | `reviewer_report.md`/`oracle.md`/`handoff.json`/`changes.diff` 开局与收尾两次复算全等（见 §1/§2） ✅ |
| 本 attempt 写入面 | 复审全程 `mtime ≥ 20:56` 的文件数 = **0**（我只读不写）；`iso/**`、`_mut/**` 无任何新 `__pycache__`（我以 `-B` + `PYTHONDONTWRITEBYTECODE=1` 跑） |

---

## 4. 实现者登记的 3 项披露 —— 逐条核验

| # | 披露 | 我的核验 | 结论 |
|---|---|---|---|
| ① | 旧 attempt 已演进到 `r7`，其 `iso/product_narrow` 已带授权分支，本卡按复审实测字节起算 | 旧 attempt `iso/` 实测：`product_narrow` = `2aa5ed1a219084a6…/41432`（L300 已有 `_AUTH_SCHEME_SPLIT`、L304 已并入 value 组），另有 `product_narrow_r3..r6`（`a551cc45/15446f4d/ca13fb81/2f644994`）与 `product_fixed = 2aa5ed1a…`；本轮 pre-image 取自 `product_mut_authsplit` = `e8abd522…/40476` = 复审 **L56 实测字节**，与旧树 152/152 字节全等 | ✅ **属实**，起算基线选择正当且只读 |
| ② | `scheme` 词表外残留（`Negotiate/AWS4/…`）仅登记未修 | 我实测 `iso/product_post`：`Authorization: Negotiate\nNEGO_MARKER_0001\ndoc=17` → `Authorization: <redacted>\nNEGO_MARKER_0001\ndoc=17`（**明文仍在**）；`Zzz` 同样；`Bearer/token` 族已修。`evidence/ruletable_product_post.json`：79 行表 `credential_leaks=2`（`cred-auth-generic-negotiate-marker`、`cred-auth-generic-scram-marker`）、`fidelity_failures=14`（**14 行在 pre 上同样失败，post-only = 0**，即非本轮回归；handoff「2 泄漏 + 12 保真行」= 14 减去那 2 个泄漏行，口径自洽）。`iso/product_pre` 对同输入**同样泄漏** → 既有状态 | ✅ **属实、已登记（oracle A.4 / `F-REV-R2-01`）、未伪称已修** |
| ③ | 复制版 pytest **68 passed / 18 errors（沙箱 WinError 5）不作证据** | `evidence/pytest_copied_suite_post.txt` 结尾原文 `68 passed, 18 errors in 1.11s`，18 个 error 全部为 `PermissionError: [WinError 5] 拒绝访问` 于 `tmp_path` **setup** 阶段；oracle §A.5 与 handoff `unverified` 均明确"不作证据" | ✅ **属实、未拿它当绿灯** |

---

## 5. P 清单

| 级别 | 项 | 说明 / 建议 |
|---|---|---|
| **P3** | P3-1 `red_green_mutations.json` 字段命名失准 | `arms.*.tree_sha256 / tree_bytes`、`post_tree_untouched_by_mutation_build.sha_before/after` 记的其实是 `observability.py` **单文件**的 sha/字节（`e8abd522…/40476`、`8dab63d9…/41304`），不是 152 文件整树哈希；handoff 的 `pre_image/post_image` 口径是对的。含义可自洽解释、且我已独立证明整树等价，故仅记表述问题 → 后续轮把字段改名 `file_sha256/file_bytes` |
| **P3** | P3-2 冻结时点缺独立时间戳证据 | 可核的：前缀 sha 三方一致、前缀边界恰在 §8 末、APPENDIX 无新判据、runner `harness/run_oracle_r2.py` mtime 20:32:45 **早于** 写入 20:34:14。不可核的：`oracle.md` 现 mtime=20:49:19（追加后），没有任何 ≤20:34 的产物内嵌 `71cbff49…`。→ 属取证限制而非造假迹象，建议以后冻结即写 `oracle.sha256` 并把首行 mtime 留痕 |
| **P3** | P3-3 A.3 代价零判据覆盖 | `Authorization: Bearer\ndoc=17` → `Authorization: <redacted>`（诊断被吞）。复审 L485-L488 已命名并接受、oracle A.3 与 `open_questions` 已披露，但 **§3/§4 没有任何一行判据钉住它**，下一轮改正则可能静默回归 → 建议补一行 `auth_keep/over` 判据 |
| **P3** | P3-4 词表外 scheme 仍明文落盘 | 危害类别与 F-REV-D-01 同类（未知名 scheme 后的凭证仍写进 append-only 日志），但**非本轮回归、超出派单范围、且实现的正是复审自己实测过的原型（同 9 词表）** → 保持登记在 `F-REV-R2-01`；**若 owner 要求"任意 scheme 词 fail-closed"，此项应升级 P2 并另开一轮** |

无 P1、无 P2。

---

## 6. 硬性纪律自查（本工位）

- 写入面 = **2 新文件**（`reviewer_report.md`、`reviewer_report.sha256`），全部跑测/脚本/日志隔离于 `%TEMP%\i14d_r2_review\`。
- 只读件**开局 + 收尾各复哈希一次**，全等（§1/§2）。
- **未**写产品仓（`C:\Users\郑曾波\Projects\company-wiki` 只读；我的导入均带 `-B`，且只在 `%TEMP%` 落日志）。
- **无 git 写**（仅 `git apply --check/apply/-R` 于 `%TEMP%` 副本、`git apply --stat/--numstat`、`git --no-optional-locks diff …` 只读）；**未跑 `git status`**；**未联网**。
- **不写卡状态**：`handoff.json` 我只读，仍为 `status=review_pending`、`implementer_signed=false`。

---

## 7. 没做的事（未取证 / 明确排除）

1. **未**复审旧 attempt 的 `r2..r7` 轮产物（`reviewer_report_r2..r7.md`、`fix_record.md`、`review.md`）—— 它们只作回源背景读取，不属于本卡。
2. **未**复跑复审原型当时的 **48 行**规则表（该版本已被旧 attempt 演进为 79 行表，不可复现）；本轮只用 79 行表作**交叉核对**，与 handoff `unverified` 口径一致。
3. **未**把 68 passed/18 errors 的复制版 pytest 当作任何判据（WinError 5 全在 `tmp_path` setup）。
4. **未**验证 `company-wiki/src` 那 9 个并发写入文件的归属（handoff 已登记为"并发写入方、非本轮"；我无归因手段，且产品仓只读）。
5. **未**处理 F-REV-D-02/03/04/05/06/07 与 A.3/A.4 残留（范围外，已登记 carry）。
6. **未**跑 crash-restart 类动态验证（`redact_text` 为纯函数、修复不引入状态，handoff `unverified` 已按 NA 声明）。
7. **未**产生任何放行/签字：本报告不构成 `ACCEPT` 落卡、不释放参数、不解任何 OPEN/BLOCKED 项、不派 `I-14-E`/`I-16-A`。
