# I-16-A oracle（先冻结）— 绑定拟部署完整组合（生产变更不执行）

- card：`execution_v2/card_I-16-A.md`（13 行，判据权威）
- attempt：`execution_runs/I-16-A/a20260926-01/`
- role：`implementer_i16a`（部署负责人）；parent：`session-19074bf0-0205-4150-…`（见 handoff.parent_agent_id）
- 冻结时刻：2026-09-26T21:0x UTC（本文件写入即冻结；后续只读复核，不得回改以贴合结果）
- 状态：`planned → implementing`；**生产变更不执行**；实现者**不自签**

---

## §0 门 0 自探留档（原始输出，逐字）

```
=== GATE0 BEGIN (I-16-A/a20260926-01) ===
utc=2026-09-26T21:06:58.9099667Z
cwd_attempt=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-16-A\a20260926-01
readback=gate0 probe I-16-A a20260926-01 write-readback-delete
deleted_gone=True
sha256 .planning\2026-09-19-three-project-history-audit\execution_runs\I-11-A\a20260919-01\evidence\I-11-A\hypotheses.json = f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28 bytes=51697
sha256 .planning\2026-09-19-three-project-history-audit\execution_runs\OPEN2-C2-REGISTRATION\a20260926-01\hypotheses_v3.json = b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff bytes=61231
git_diff RF total=3830 non_planning=0
git_diff CW total=1 non_planning=1
git_diff DAYU total=1 non_planning=1
=== GATE0 END ===

--- GATE0 RECHECK (after transient CW diff=1 observed during gate0; concurrent git activity suspected) ---
utc=2026-09-26T21:08:07.2794266Z
git_diff RF HEAD=b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb exit=0 total=3830 non_planning=0 staged=0
git_diff CW HEAD=bf0c8b27e83c3ee7e533c6031fefad8e27e5e121 exit=0 total=9 non_planning=9 staged=1
git_diff DAYU HEAD=2115c86d5a9027bb51cbbc8a4d0175080732e4e6 exit=0 total=1 non_planning=1 staged=1
```

> 登记 `u-I16A-0`：门 0 首次读到 CW `total=1`（与 8 分钟前的 9 不一致），复测稳定为 9 并附 `exit=0`；
> 判定为**并发 git 活动期的一次瞬时读**（CW 索引内已有 `staged` 文件，见 §6.2）。**原始输出不删改**，只追加复测段。

---

## §1 授权（逐字回源）

### §三十八 裁定一（`OWNER_DECISIONS.md` L879-L886，逐字）

> ### 裁定一：`I-16-A` 开工门槛 —— **「授权开工（建议）」**
> **依据卡文**：`card_I-16-A.md` L5 `依赖：I-07-E、I-07-D、I-08、I-09、I-13、I-14、I-15`。
> **开工判据（owner 明文改判，`§三十四` 同款）**：
> 1. **已 `accepted`**：`I-07-D` · `I-07-E` · `I-09` · `I-13-A` · `I-13-BC` · `I-15-A` ✓
> 2. **`I-08-A`**：按 `task_plan` 清单 **`[x]`** 视为满足（其 `review_pending` 是复审明令「`not-granted` 项 3 禁写 `accepted`」的**刻意状态**，非未完成）
> 3. **`I-14` 家族**：`A/B/C/D` 已落（`D` 的 `R2` 凭证修复 2026-09-26 `accepted_scoped`）；**`E` 被 `OpenProcess` 环境阻断 ⇒ 以 `unverified` 登记，不作开工阻断**
> 4. **红线（不因开工而放宽）**：`I-16-A` 自身动作 3「**不能证明恢复则 `blocked`，不以关闭严格门回滚**」**维持 fail-closed**；动作 4「真正未授权影响再向用户说明具体请求」**维持**
> 5. **不授予**：不代 `I-14-E` 出结论 · 不解 `TESTSIDE` 环境阻断 · 不放行参数 · 产出仍须独立复审

### §三十七（`OWNER_DECISIONS.md` L852-L862，关键句逐字）

> **本会话内编排层（父）的一切沙箱提权操作，owner 一次性常设授权**，**无需逐次审批**。
> 覆盖：`dayu-agent` / `company-wiki` / `revenue-forecast` 三仓全部读写 · `OpenProcess` 等系统调用 · 任意目录的文件创建/修改（含 `raw/`、`tools/` 落点）· 网络取证。
> **边界（授权 ≠ 免除纪律）**：1. 纪律 16/17/18/19/20 全部继续有效 … 2. **生产零未授权改动** 的纪律不变 … **`commit/push` 仍须 owner 另批**；3. **产品仓提交（`git add/commit/push`）不在本授权内** —— 仍归 owner 逐次决定。

**本次实际使用面**：零提权（全部读 + 本 attempt 目录普通写 + `.planning` 内隔离副本）；网络 = 0；git 写 = 0；`git status` 未跑。

---

## §2 卡文判据（`card_I-16-A.md` 逐字，sha256 于 §8）

- **L6**：`允许写：部署提案与隔离安装目录；生产变更尚不执行。`
- **L8（动作 1）**：`列三仓源commit+dirty内容hash、安装副本hash、解释器/依赖、config/policy/flags/schema版本及真实加载模块；不能只比较仓库HEAD。`
- **L9（动作 2）**：`在新进程检查加载路径，与安装副本及预期组合一致；用旧加载模块的负例证明能发现版本错配。`
- **L10（动作 3）**：`记录上个可恢复完整组合、迁移是否可逆、raw/registry/catalog兼容边界。不能证明恢复则blocked，不以关闭严格门回滚。`
- **L11（动作 4）**：`对部署影响范围列出具体写入、停止/重启进程和恢复步骤；按既有授权执行可逆准备，真正未授权影响再向用户说明具体请求。`
- **L13（退出）**：`退出：提案与恢复演练在隔离环境通过；资格仅"可进入具体部署窗口"，尚非已部署。`

**派单逐字（本卡硬性纪律）**：oracle 先冻结（L6 + L13 + 动作逐字 + 变异 ≥3）+ 门 0 自探留档 · 写入面 = 本 attempt 目录 + `.planning` 内隔离目录，**产品三仓只读**（`git diff HEAD --name-only` 只读、**禁 `git status`**、零 git 写）· `I-14-E` 环境阻断以 `unverified` 登记不作开工阻断 · `OPEN-2` 红线（`124,248.63` 只登记不消费）· 封盘 `f2178768…` 零字节 · 不放行参数 · 不自签 · 落定父直写 · 禁五份计划文件 · 禁 `.planning` 外写 · 禁联网 · fail-closed · 不派 `I-16-B`。

---

## §3 上游 handoff（仅 sha / 状态；开工授权已由 §三十八 给出，不复核 7 项依赖）

| 卡 | attempt | handoff.json sha256 | status | status_authority.carrier_sha256 | three_way_match |
|---|---|---|---|---|---|
| I-07-D | a20260923-01 | `82bb03aca1756d0cec155d039150e930d7b2a885659ad73d5a94e1c032d09e13` | `accepted_scoped` | （该代 handoff 无 `status_authority` 字段） | n/a |
| I-07-E | a20260926-01 | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` | `accepted_scoped` | `6b48a2f5e2085f70c29315b4da1537ba80006833ef721468d9c11a87d714cca2` | true |
| I-13-A | a20260926-01 | `0b466621ff964c8e3347cc96033bf7abd1f800eaf9eda75c3555209ac60a2f97` | `accepted_scoped` | `7f0c379c61c75de131c4b87b8fe58f285fb64aafef33f37cba85ac40ccf75d62` | true |
| I-13-BC | a20260926-01 | `2dfa7a0918a75c862fdf5b378bb50523cf94ff56a48e3b31353d5f0b724f8dfa` | `accepted_scoped` | `b4c4ae2127b266602bea68330d2d43adb2c023da26edb9f0efe4ec78c67e5248` | true |

---

## §4 冻结预期（正例 P1–P6；全部在本文件冻结后运行，不调用被测物生成 expected）

三仓（路径绑定）：
- RF = `C:\Users\郑曾波\Projects\revenue-forecast`
- CW = `C:\Users\郑曾波\Projects\company-wiki`
- DAYU = `C:\Users\郑曾波\Projects\dayu-agent\dayu-agent`（外层 `dayu-agent` **不是** git 仓库，`git rev-parse` exit=128）

| id | 判据（冻结值） | 期望 |
|---|---|---|
| P1 | 三仓源 `commit`：RF `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb` · CW `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121` · DAYU `2115c86d5a9027bb51cbbc8a4d0175080732e4e6`；`git diff HEAD --name-only` 只读计数与 dirty/untracked 文件 **内容 sha256** 一并绑定（**不止 HEAD**） | 三仓 HEAD 与绑定一致；dirty 层内容 hash 逐文件绑定进 manifest |
| P2 | 安装副本：`company-wiki==0.1.0`、`dayu-agent==0.1.4` 均为 **editable**（`direct_url.json dir_info.editable=true`）；CW 目标 `…\company-wiki\src`；DAYU 目标 `…\dayu-agent\dayu-agent`（Miniconda 与 DAYU `.venv` 两处安装**同源**）；安装层文件（`.pth` / finder / `direct_url.json` / `RECORD` / `METADATA`）逐个 sha256 | 安装层 hash 全部可读并绑定；editable 映射目标 = 源仓路径 |
| P3 | 解释器/依赖：主 `C:\Miniconda\python.exe` `3.13.9`（= `worker_runtime.executable`）；适配器 `…\dayu-agent\dayu-agent\.venv\Scripts\python.exe` `3.14.2`；关键依赖 `PyYAML 6.0.3` / `requests 2.34.2` / `httpx 0.28.1` / `pydantic 2.13.4`；两处 `dayu-agent 0.1.4`、`company-wiki 0.1.0` | 新进程实测值与冻结值一致 |
| P4 | config/policy/flags/schema：`RF/config/company_wiki.json` `schema_version=2.0` · `RF/config/filing_fetch.json` `1.0` · `CW/config/source_catalog.yaml` `1.0` · `CW/config/source_catalog_worker.yaml` `1.3` · `contracts.constants.FORECAST_SCHEMA_VERSION=3.7` · `OPT_IN_SCHEMA_VERSION=3.8` · `CONFIDENCE_POLICY_VERSION=1.0` · `company_wiki.automation.migrations.SCHEMA_VERSION=1` · `SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION="1.0.0"` | 常量与文件 hash 双绑定一致 |
| P5 | **新进程**加载路径：`sys.executable` = 冻结解释器；`company_wiki.__file__` 落在 CW editable 目标；`dayu.__file__` 落在 DAYU editable 目标；RF `contracts.constants.__file__` = `RF\scripts\contracts\constants.py`；各**真实加载模块**文件 sha256 == 源仓同名文件 sha256 | 加载路径与安装副本、预期组合三者一致 |
| P6 | 恢复演练（隔离）：快照→隔离还原 **逐文件 sha256 相等**；DB `backup→migrate→restore` **字节相等**；更高 `user_version` **fail-closed 且文件字节不变** | 全部通过 ⇒ 恢复可证 |

## §4b 负例与变异（**≥3**；每臂独立目录、原件字节不动、before/after sha 比对）

| id | 变异（只作用于 `_mut/Mx` 副本） | 期望被检出的不变量 | 期望 rc |
|---|---|---|---|
| M1 | **旧加载模块**：把 CW `source_catalog/evidence_query.py` 的 **git HEAD（旧）字节**放进隔离 site，新进程 `PYTHONPATH` 指向它 → 新进程真实加载到旧模块 | J3（新进程加载模块 sha ≠ 冻结的源仓 sha） | `3` |
| M2 | config 漂移：`config/company_wiki.json` 副本 `schema_version 2.0 → 1.9` | J5 | `3` |
| M3 | schema 常量漂移：`scripts/contracts/constants.py` 副本 `FORECAST_SCHEMA_VERSION 3.7 → 3.6`，新进程从隔离 site 加载 | J5（经新进程实测常量） | `3` |
| M4 | 解释器错配：用 DAYU `.venv` 的 `python 3.14.2` 跑探针（生产组合要求 `3.13.9`） | J4 | `3` |
| M5 | 安装副本漂移：`__editable__.company_wiki-0.1.0.pth` 副本内容改写 | J2 | `3` |
| G | 绿臂（live，真实当前组合） | 全部 J1–J8 | `0` |
| G2 | 定稿后复跑绿臂 | 全部 J1–J8 | `0` |

**不变量编号（verifier `_verify_combo.py`）**
- J1 三仓源：HEAD + dirty/untracked 内容 hash（live == 绑定 manifest；`git status` 不跑）
- J2 安装副本：dist-info / pth / finder / RECORD / METADATA / direct_url hash + editable 映射
- J3 新进程加载路径与**真实加载模块** hash（安装副本 == 源仓 == 预期）
- J4 解释器/依赖版本
- J5 config/policy/flags/schema 文件 hash 与常量值
- J6 上个可恢复完整组合 + 迁移可逆 + raw/registry/catalog 兼容边界（恢复演练证据）
- J7 影响范围清单存在性（写入/停重启/恢复步骤）
- J8 边界：`.planning` 外写=0、git 写=0、`git status`=未跑、网络=0、封盘零字节、store 参数未放行

## §4c exit_code_legend（本批冻结；自描述）

| rc | 含义 | 判据 |
|---|---|---|
| `0` | 通过 | 命令正常结束且全部不变量成立 |
| `1` | harness 失败 | 脚本/绑定/路径错误，无法给出裁决 |
| `2` | 无裁决 | 冻结期望缺失/不可用，在任何判定前发出 |
| `3` | 未达预期（不变量违例） | 命中具名 Jx 不变量违例；红臂据此证明"能发现版本错配" |

> 聚合方**必须**先读本 legend；历史批 rc 语义不回改、不套用。

---

## §5 红线（不因开工放宽）

1. **`OPEN-2`**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` base `124,248.63`（真值 `38,175.95`）**只登记不消费**；本卡不引用为部署输入。
2. **封盘**：`I-11-A hypotheses.json` sha256 `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B）**零字节变化**；store `b2063ac8…`（61,231 B）零字节变化。
3. **不放行参数**：`low/base/high` 全 `null`、`_PLACEHOLDER` 维持；本卡不产生任何参数放行。
4. **不自签**：`status=review_pending`、`implementer_signed=false`；落定走父直写。
5. **写入面**：仅本 attempt 目录 + `.planning` 内隔离目录；**产品三仓零写**、**禁 `git status`**、零 git 写（`add/commit/push/stash/checkout` 一律不跑）、禁 `.planning` 外写、禁联网。
6. **不代 `I-14-E` 出结论**：`OpenProcess` `DENIED` → `TESTSIDE` 三臂不可证，以 `unverified` 登记，**不作开工阻断**。
7. **不派 `I-16-B`**；不触发任何 falsifier/自动动作；不修改五份计划文件。
8. **fail-closed**：恢复组合证不了 ⇒ `STOP` 判 `blocked`（合格交付）；**不以关闭严格门回滚**。

---

## §6 开工前只读探明的事实（供 §4 判据取值；均为读操作）

### 6.1 三仓 git（只读；`git status` 未跑）

| 仓 | HEAD | 提交时间/主题 | `diff HEAD --name-only` | staged | untracked（`ls-files --others --exclude-standard`，只读） |
|---|---|---|---|---|---|
| RF | `b7a6a116…` | 2026-09-23T19:51:01+01:00 audit(planning): batch-9 | 3830（**non-planning = 0**） | 0 | 10512（non-planning = 48，多为 `.tmp-*`） |
| CW | `bf0c8b27…` | 2026-09-23T13:08:16+01:00 fix(F-EE1 / FC-704-class) | 9（全 non-planning） | **1**（`src/company_wiki/source_catalog/dayu_cli_adapter.py`） | 42（`docs/plans/…`） |
| DAYU | `2115c86d…` | 2026-05-04T18:01:35+08:00 fix/cn download (#156) | 1（`dayu/fins/downloaders/sec_downloader.py`） | **1**（同文件） | 1（`docs/architecture_report.html`） |

> 登记 `u-I16A-0`（并发写活动）：CW/DAYU 索引中存在 **staged** 文件 ⇒ 组合在本卡运行期间**并非静默不变量**；定稿时须复测并在 handoff 记录前后一致性。

### 6.2 安装层（只读）

- `C:\Miniconda\Lib\site-packages\company_wiki-0.1.0.dist-info\direct_url.json` = `{"dir_info": {"editable": true}, "url": "file:///C:/…/Projects/company-wiki"}`；`__editable__.company_wiki-0.1.0.pth` → `<CW>\src`
- `C:\Miniconda\Lib\site-packages\dayu_agent-0.1.4.dist-info\direct_url.json` = editable → `file:///C:/…/Projects/dayu-agent/dayu-agent`；`__editable___dayu_agent_0_1_4_finder.py` `MAPPING = {'dayu': '<DAYU>\dayu'}`
- DAYU `.venv\Lib\site-packages\dayu_agent-0.1.4.dist-info\direct_url.json` 同为 editable 指向同一目录 ⇒ **两解释器同源**
- `top_level.txt`：`company_wiki` / `dayu`（**包名是 `dayu`，不是 `dayu_agent`**）
- `~\.claude\skills\revenue-forecast` 是 **Junction → `~\.agents\skills\revenue-forecast`**，该目标目录在本会话**读取被拒**（ACL/沙箱），见 §7

### 6.3 真实加载模块（生产 worker 自报，只读）

`CW\config\.source_catalog\worker_runtime.json`：`executable=C:\Miniconda\python.exe`、`worker_status=waiting`、`pid=15596`（**当前已不存在**）、`heartbeat_at=1786182069.8367717` = **2026-08-08T09:41:10Z**、`code_version=21860fd`、`loaded_code_fingerprint=12a0bcbea3810ab8388553e376c361c457443f9847622b7591262eec98f46b69`、`loaded_code_files` 10 条（逐条 sha256）。

**对账（只读，本卡执行）**：10 条中 **5 条 == 当前工作树**、**5 条 ≠**（`store.py`/`normalizer.py`/`llm_summarizer.py`/`service.py`/`admission.py`）。进一步：
- `code_version 21860fd` = commit `21860fd4c6bff55bdf13fb9fd5b3b40a4acab692`（2026-08-07，HEAD 祖先，`merge-base --is-ancestor` exit=0）
- 5 条不符项在**该路径全部历史修订**中检索 sha256：仅 `admission.py` 命中 rev `cb2305ce…`；`store.py`(14 revs)/`normalizer.py`(22)/`llm_summarizer.py`(8)/`service.py`(21) **全部未命中**
- 进一步在 CW 磁盘（排除 `.git/.venv/__pycache__`，扫描 669 个 `.py/.bak/.orig`）检索 4 个缺失 sha：**全部未命中**

⇒ 登记 `u-I16A-1`：**2026-08-08 那次运行的组合字节已不可重建**（4 个模块的字节既不在 git 历史也不在磁盘）⇒ 该运行态**不得**作为恢复目标；本卡的"上个可恢复完整组合"另按 §4 P6 指定并以演练证明。

### 6.4 数据/配置锚点（只读）

- 生产 catalog：`CW\.source_catalog\catalog.sqlite3`（3,055,796,224 B）；`CW\config\.source_catalog\`（188,416 B 库 + `worker_state.json` / `worker_runtime.json` / `worker_runs.jsonl`）
- `CW\config\source_catalog.yaml`：`catalog_dir: ${PROJECT_ROOT}/.source_catalog`；`reusable_root_kinds: [company_raw, dayu_portfolio, directory]`；roots：`company_raw`→`companies`、`dayu_portfolio`→`../dayu-agent/workspace/portfolio`、`dropbox_stock`、`future_lake(read_only)`
- `worker_control.json` **不存在**（`control.py:662` 按需创建）⇒ desired_state 未被本卡改变
- `RF\config\company_wiki.json` 适配器：`cn`→`python -m src.company_wiki_adapter_cli`；`hk`/`us`→**DAYU `.venv\Scripts\python.exe`** `-m dayu.cli`

---

## §7 本会话环境限制（登记，非开工阻断）

| id | 现象 | 处置 |
|---|---|---|
| `I14-E-unverified` | `Get-CimInstance Win32_Process` → `拒绝访问`（`OpenProcess` DENIED），无法读取运行中进程命令行 | 按 §三十八 逐字以 **`unverified`** 登记，**不作开工阻断**；不代 `I-14-E` 出结论 |
| `u-I16A-skillcopy` | `~\.claude\skills\revenue-forecast`（Junction→`~\.agents\skills\revenue-forecast`）枚举/读取被拒；同目录 `filing-fetch` 可读 | 该"skill 安装副本 hash"子项标 **`unverified`**，不冒充已核；提案中列为部署窗口必检项 |
| `u-I16A-0` | 门 0 期间 CW diff 瞬时读为 1（复测 9），CW/DAYU 索引有 staged 文件 | 原始输出不删改，追加复测；定稿前二次复测 |

---

## §8 本 attempt 输入文件 sha256（冻结）

| 文件 | sha256 |
|---|---|
| `execution_v2/card_I-16-A.md` | （定稿时按 `Get-FileHash` 记入 `verification.json.upstream_inputs`） |
| `execution_v2/common_root_cards.md` | 同上 |
| `execution_v2/START_HERE.md` | 同上 |
| `OWNER_DECISIONS.md`（§三十七/§三十八 所在） | 同上 |
| 上游 4 份 handoff.json | 见 §3 |
| 封盘 `I-11-A/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| store `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` |

---

**冻结声明**：以上正例/负例/变异/期望 rc 在任何验证运行前写定；运行结果只能被记录，不得回改本文件。
