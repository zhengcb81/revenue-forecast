# I-16-A 部署提案 —— 绑定拟部署完整组合（**生产变更不执行**）

- 卡：`execution_v2/card_I-16-A.md`（sha256 `fa2884fa30678085ccb8a4c9f08035817b45a9200de02b6a5ebf3d71852f535c`，13 行）
- attempt：`execution_runs/I-16-A/a20260926-01/`；绑定时刻 `2026-09-26T21:30:57Z`
- 授权：`OWNER_DECISIONS §三十八 裁定一`（逐字见 `oracle.md §1`）；`§三十七` 沙箱常设授权（本卡零提权使用）
- 角色：`implementer_i16a`（部署负责人）；**不自签**、**不放行参数**、**不派 `I-16-B`**
- 写入面：仅本 attempt 目录 + `.planning` 内隔离副本；**产品三仓零写**、`git status` 未跑、零 git 写、零网络

> **退出判据（卡文 L13）**：`提案与恢复演练在隔离环境通过；资格仅"可进入具体部署窗口"，尚非已部署。`
> 本提案即"提案"，`recovery_drill.json` 即"恢复演练"；**本卡未执行任何生产变更**。

---

## 动作 1：三仓源 commit + dirty 内容 hash、安装副本 hash、解释器/依赖、config/policy/flags/schema、真实加载机器

### 1.1 三仓源（不止 HEAD：commit + dirty/untracked **内容** sha256 一并绑定）

| 仓 | 路径 | `commit` (HEAD) | `diff HEAD --name-only` | staged | untracked(non-planning) | dirty 内容条数 | **dirty 内容 digest (sha256)** |
|---|---|---|---|---|---|---|---|
| RF | `C:\Users\郑曾波\Projects\revenue-forecast` | `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb` | 3830（**non-planning = 0**） | 0 | 48 | 48 | `f41d1a3f0046dd89246fb16447ab85c8e617825406713b23a23d281608bdda8d` |
| CW | `C:\Users\郑曾波\Projects\company-wiki` | `dbe474504a6187e22c37918743d17fe59c85a0a8` | 8（全 non-planning） | 0 | 51 | 59 | `3630bfae2a391b95c4d9f03c327ea2775df46dc56e1015378246a57fa1aaceba` |
| DAYU | `C:\Users\郑曾波\Projects\dayu-agent\dayu-agent` | `2115c86d5a9027bb51cbbc8a4d0175080732e4e6` | 1 | 0 | 1 | 2 | `8d2b7c1da188f3b8799d72af1ca05544cd49937d1d94f19376e5b1a498d748e6` |

- **外层 `dayu-agent` 不是 git 仓库**（`git rev-parse` exit=128）；真实仓库在嵌套目录，已按嵌套目录绑定。
- 逐文件 dirty/untracked 清单 + 每文件 sha256：`combo_manifest.json.repos.<仓>.dirty_content`（RF 48、CW 59、DAYU 2，共 109 条）。
- `dirty_content_digest` = 对 `state|path|sha256` 排序后整体再 sha256，可复算比对。
- 命令均为只读：`git rev-parse HEAD` / `git diff HEAD --name-only` / `git diff --cached --name-only` / `git ls-files --others --exclude-standard`；**`git status` 未跑**；**零 git 写**。

> ⚠ **并发漂移登记 `u-I16A-0`（组合在本卡运行期间被外部写入方改动）**
> - 门 0（21:06–21:08Z）：CW = `bf0c8b27…`、dirty 9、**staged 1**；DAYU staged 1。
> - 绑定（21:23Z 起各轮）：CW = `dbe47450…`（**外部会话已提交**）、staged 0；DAYU staged 0。
> - 期间实测到 `CW: scripts/narrative_evidence_pilot.py`、`CW: tests/unit/test_narrative_evidence.py` 内容在两次校验之间变化，CW untracked 50 → 51。
> - 处置：**不回改 oracle**；原始输出保留在 `gate0_raw.txt`（含追加复测段）；本提案以**最终绑定**为准，并在 `handoff.open_questions` 中要求复审者在安静时刻复跑 `J1`；若复跑仍红 ⇒ 组合不稳定，**不得开部署窗口**（owner 裁定）。

### 1.2 安装副本（editable 安装层逐文件 hash）

| 组件 | 位置 | 关键事实 | 证据字段 |
|---|---|---|---|
| `company-wiki==0.1.0` | `C:\Miniconda\Lib\site-packages\company_wiki-0.1.0.dist-info` | `direct_url.json` → `{"dir_info":{"editable":true}}`，目标 `…\Projects\company-wiki`；`__editable__.company_wiki-0.1.0.pth` → `…\company-wiki\src` | `install.company_wiki` + artifact `inst_cw_*` |
| `dayu-agent==0.1.4`（Miniconda） | `…\dayu_agent-0.1.4.dist-info` | editable → `…\Projects\dayu-agent\dayu-agent`；`__editable___dayu_agent_0_1_4_finder.py` `MAPPING={'dayu': '…\dayu-agent\dayu-agent\dayu'}` | `install.dayu_agent_miniconda` + `inst_dayu_*` |
| `dayu-agent==0.1.4`（DAYU `.venv`） | `…\dayu-agent\dayu-agent\.venv\Lib\site-packages\…` | **同源 editable**（同一目录）⇒ 两个解释器加载同一份源 | `install.dayu_agent_venv` + `inst_dayu_venv_*` |
| 入口 shim | `C:\Miniconda\Scripts\dayu-cli/render/web/wechat.exe` | 由 `RECORD` 逐条记录 sha256（可复核） | `install.*.files.RECORD` |

- 12 个安装层 artifact 的 sha256 全部绑定在 `combo_manifest.json.artifacts`（`inst_*` 组）。
- `top_level.txt`：`company_wiki` / **`dayu`**（包名是 `dayu`，不是 `dayu_agent`）。
- **skill 安装副本子项 = `unverified`**：`~\.claude\skills\revenue-forecast` 为 Junction → `~\.agents\skills\revenue-forecast`，该目标在本会话**读/列目录被拒**（同目录 `filing-fetch` 可读）⇒ 不冒充已核，列为部署窗口必检项（`oracle §7`）。

### 1.3 解释器 / 依赖

| 用途 | 解释器 | 版本 | 关键依赖（实测） |
|---|---|---|---|
| 主解释器（= 生产 worker `executable`） | `C:\Miniconda\python.exe` | **3.13.9** | `company-wiki 0.1.0`、`dayu-agent 0.1.4`、`PyYAML 6.0.3`、`requests 2.34.2`、`httpx 0.28.1`、`pydantic 2.13.4` |
| 适配器解释器（`RF/config/company_wiki.json` hk/us → `-m dayu.cli`） | `…\dayu-agent\dayu-agent\.venv\Scripts\python.exe` | **3.14.2** | `dayu-agent 0.1.4`、`requests 2.34.2`、`httpx 0.28.1`、`PyYAML 6.0.3` |

⇒ **组合是双解释器的**：主链 3.13.9，hk/us 适配链 3.14.2；两者对 `dayu` 的安装都 editable 指向同一源目录。

### 1.4 config / policy / flags / schema 版本

| 项 | 值 | 来源 |
|---|---|---|
| `RF/config/company_wiki.json` `schema_version` | **2.0**（含 cn/hk/us adapters、`timeout_seconds=1800`） | 文件 hash + 解析 |
| `RF/config/filing_fetch.json` `schema_version` | **1.0** | 同上 |
| `CW/config/source_catalog.yaml` `schema_version` | **1.0**（`catalog_dir=${PROJECT_ROOT}/.source_catalog`；roots：`company_raw`/`dayu_portfolio`/`dropbox_stock`/`future_lake(read_only)`） | 同上 |
| `CW/config/source_catalog_worker.yaml` `schema_version` | **1.3**（`scan/export=60min`、`prune_retention_days=90`、`normalize_batch_size=3`） | 同上 |
| `contracts.constants.FORECAST_SCHEMA_VERSION` | **3.7** | 新进程实测常量 |
| `contracts.constants.OPT_IN_SCHEMA_VERSION` | **3.8** | 同上 |
| `CONFIDENCE_POLICY_VERSION` | **1.0** | 同上 |
| `company_wiki.automation.migrations.SCHEMA_VERSION` | **1** | 同上 |
| `SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION` | **"1.0.0"** | 同上 |
| 生产 catalog `PRAGMA user_version` | **0**（18 表；文件 3,055,796,224 B） | 只读打开 |
| 小库 `config/.source_catalog/catalog.sqlite3` `user_version` | **0**（15 表；188,416 B） | 只读打开 |

逐文件 sha256 见 `combo_manifest.json.config_policy_flags_schema_files`（5 件）与 `.artifacts`（`cfg_*`、`mod_*` 组）。

### 1.5 真实加载模块（新进程实测 + 生产 worker 自报）

**新进程探针** `_probe_newprocess.py`（`python -X utf8 -B`，独立进程）：

| 模块 | 加载方式 | 真实加载路径 | 文件 sha256（前 12） |
|---|---|---|---|
| `company_wiki` | import | `…\company-wiki\src\company_wiki\__init__.py` | 见 `combo_manifest.expected_modules` |
| `company_wiki.automation.migrations` | import | `…\src\company_wiki\automation\migrations.py` | 同上 |
| `company_wiki.source_contract.compatibility` | import | `…\src\company_wiki\source_contract\compatibility.py` | 同上 |
| `company_wiki.source_catalog.evidence_query` | import | `…\src\company_wiki\source_catalog\evidence_query.py` | 同上 |
| `contracts.constants` | import | `…\revenue-forecast\scripts\contracts\constants.py` | 同上 |
| `confidence_policy` | import | `…\revenue-forecast\scripts\confidence_policy.py` | 同上 |
| `dayu` / `dayu.cli` | find_spec（解析子模块会执行父包 `dayu/__init__`，不执行 `dayu.cli` 本体） | `…\dayu-agent\dayu-agent\dayu\__init__.py`、`…\dayu\cli\__init__.py` | 同上 |

⇒ **加载路径 = 安装副本 = 源仓 = 预期组合**（editable 三者同源），`J3` 全绿。

**生产 worker 自报的真实加载组合**（`CW\config\.source_catalog\worker_runtime.json`，只读）：
`executable=C:\Miniconda\python.exe`、`worker_status=waiting`、`pid=15596`（**当前进程不存在**）、
`heartbeat=2026-08-08T09:41:09Z`、`code_version=21860fd`、`loaded_code_fingerprint=12a0bcbe…`、`loaded_code_files` 10 条。
对账：**5/10 == 当前工作树**；5 条不符（`store.py`、`normalizer.py`、`llm_summarizer.py`、`service.py`、`admission.py`）——详见动作 3。

---

## 动作 2：新进程加载路径验证 + **旧加载模块负例**

### 2.1 正例（live，独立新进程）

`_probe_newprocess.py` → `_live/probe_final.json`；`_verify_combo.py`（live 模式）**rc = 0**，`J1..J8` 全部 `ok=true`（`_live/result_final.json`）。

### 2.2 变异（`_run_mutations.py`；原件字节前后 sha256 一致，`original_artifacts_untouched=true`）

| 臂 | 变异（只作用于副本/隔离 site） | 期望 | 实测 rc | 具名命中 |
|---|---|---|---|---|
| G | 无（live 绿臂） | 0 | **0** | — |
| **M1** | **旧加载模块**：隔离 site 内放 CW `evidence_query.py` 的 **git HEAD 旧字节**，新进程 `PYTHONPATH` 指向它 | 3 | **3** | `J3_new_process_load_path` |
| M2 | `config/company_wiki.json` 副本 `schema_version 2.0→1.9` | 3 | **3** | `J5_config_policy_flags_schema` |
| M3 | `scripts/contracts/constants.py` 副本 `FORECAST 3.7→3.6`，新进程从隔离 site 加载 | 3 | **3** | `J5`（并连带 `J3`） |
| M4 | 用 DAYU `.venv` 的 `python 3.14.2` 跑探针（组合要求 3.13.9） | 3 | **3** | `J4_interpreter_deps`（并连带 `J3`/`J5`） |
| M5 | `__editable__.company_wiki-0.1.0.pth` 副本改写 | 3 | **3** | `J2_install_copy` |
| G2 | 副本操作后复跑 live 绿臂 | 0 | **0** | — |

`all_rc_match=true`、`all_expected_violations_present=true`、`original_artifacts_untouched=true`
⇒ **用旧加载模块的负例确实能发现版本错配**（M1 具名命中 J3，且旧/新字节不同已记录：`old_module_sha256` vs `current_module_sha256`）。

---

## 动作 3：上个可恢复完整组合、迁移可逆、raw/registry/catalog 兼容边界

### 3.1 上个可恢复完整组合（**恢复目标 C0**）

**C0 = 本卡最终绑定**（RF `b7a6a116…` + CW `dbe47450…` + DAYU `2115c86d…` + 三仓 dirty/untracked 内容层 + editable 安装层 + 3.13.9/3.14.2 双解释器 + §1.4 配置/schema 值 + 生产库锚点）。

**为什么它是"上个"**：生产 worker 自 2026-08-08 起未再运行（`pid` 已消亡、`worker_control.json` 不存在、desired_state 未被本卡改动），此后三仓只发生**源码提交与工作树演进**，无可运行的新部署态 ⇒ 当前磁盘态即"上一个（也即当前）完整组合"。

**可恢复性证明（隔离演练，`recovery_drill.json` 五项全绿）**

| 项 | 结果 |
|---|---|
| **R1** dirty/untracked 层：`snapshot/` 109 文件 → `drill_restore/` 逐文件 sha256 相等 | ✅ `restored=109, mismatch=[]` |
| **R2** DB：`backup → migrate(v0→v1) → 二次 migrate 只读校验 → 从备份 restore` | ✅ `sha_after_restore == sha_before`（字节相等）；二次 migrate 不改字节 |
| **R3** 更高 `user_version=99` | ✅ 抛 `UnsupportedSchemaVersionError`，**文件字节不变** |
| **R4** v1 结构漂移（额外建表） | ✅ 抛 `SchemaDriftError`，校验过程**不再改文件** |
| **R5** registry 前向边界 | ✅ `user_version 0→1` 自动 bump；`user_version=9` **被静默接受、不建表不报错** |

**⇒ 恢复可证（`recovery_provable=true`）⇒ 不触发 `blocked`**（且**未**用"关闭严格门"回滚）。

**已执行的可逆准备**（卡文 L11「按既有授权执行可逆准备」）：
1. `snapshot/` + `snapshot_manifest.json`：三仓 dirty/untracked 层字节快照（**读产品 → 写本目录**；删除即回到未准备状态，产品零改动）；
2. `_iso_baseline/artifacts/**`：31 个组合 artifact 的隔离安装副本；
3. 生产 catalog **只读锚点**：`3,055,796,224 B`、`sha256=63c359aa4b09545a540a05f8d32d66ac3c9dbd4ccf696470d55cb38a31f6dcfc`、`mtime=2026-09-26T17:48:22Z`、`user_version=0`、18 表（部署窗口须复核一致）。

### 3.2 迁移是否可逆

- **可逆（已证）**：`company_wiki.automation.migrations` 的 v0→v1 迁移为单事务 + `backup_hook` 前置备份；备份失败则文件字节不变；恢复 = 从备份覆盖，R2 已证**字节相等**。
- **前向 fail-closed**：`user_version > 1` → `UnsupportedSchemaVersionError`，且**不修改文件**（R3）；结构漂移 → `SchemaDriftError`（R4）。
- **不可逆/不可重建的历史态（登记 `u-I16A-1`，**不是**恢复目标）**：2026-08-08 worker 那次运行组合
  - `code_version=21860fd` = commit `21860fd4c6bff55bdf13fb9fd5b3b40a4acab692`（HEAD 祖先）；
  - 10 条记录加载模块中 5 条 ≠ 当前工作树；在**该路径全部历史修订**里检索（14/22/8/21 rev）仅 `admission.py` 命中 rev `cb2305ce…`，`store.py`/`normalizer.py`/`llm_summarizer.py`/`service.py` **未命中**；
  - 再在 CW 磁盘检索（排除 `.git/.venv/__pycache__`，669 个 `.py/.bak/.orig`）：**4 个缺失 sha 全部未命中**。
  - ⇒ 该运行态字节**已不可重建**，**禁止**用作回滚目标；由此产生的风险已在 §4 恢复步骤中改为"回退到 C0 + 外部提交按 commit 恢复"。

### 3.3 raw / registry / catalog 兼容边界

| 层 | 边界（实测/源码） | 部署含义 |
|---|---|---|
| **catalog（automation 库）** | `>SCHEMA_VERSION` fail-closed 且文件不变；`==` 只读校验；`<` 单事务迁移 + 备份（R2/R3/R4） | 迁移必须带 `backup_hook`；不得以"降级"回滚 |
| **catalog（source_catalog 主库）** | `config/source_catalog.yaml` `catalog_dir=${PROJECT_ROOT}/.source_catalog`；当前 `user_version=0`、18 表、3.05 GB | 部署窗口只读复核锚点；任何写入须先备份 |
| **registry（`source_registry`/`question_registry`/`run_store`）** | `user_version < 1` → CREATE + bump 到 1；**`> 1` 无守卫、静默接受、不建表**（R5 实测） | **前向兼容不 fail-closed = 边界风险**：部署/回滚前必须先备份 registry 文件 |
| **raw** | 由 acquisition 追加写入（`reusable_root_kinds: [company_raw, dayu_portfolio, directory]`；`future_lake` `read_only: true`）；本卡**零写** | 部署步骤不触碰 raw 字节；恢复不涉及 raw |

---

## 动作 4：部署影响范围（清单 + 可逆准备 + 未授权影响）

> 完整结构化清单：`impact_scope.json`（`production_change_executed=false`、`unauthorized_impact=false`）。

### 4.1 具体写入

- **本卡已写（全部在 `.planning` 内）**：`execution_runs/I-16-A/a20260926-01/**`（oracle、清单、校验、演练、变异、`snapshot/`、`_iso_baseline/`、`_mut/`、`drill_*`）。
- **部署窗口将写、本卡未执行**：安装层（`site-packages` 的 pth/finder/dist-info + `Scripts\dayu-*.exe`）· config/policy 文件 · 数据层（`catalog.sqlite3` + `-wal/-shm`、registry 库）· worker 状态文件。逐项与回滚方式见 `impact_scope.json.writes.planned_in_deployment_window_NOT_executed_here`。

### 4.2 停止 / 重启进程

- 当前实测：source-catalog worker **未运行**（`pid=15596` 已消亡、`worker_status=waiting`、`worker_control.json` 不存在）；本机可见 10 个 `python.exe`，但**命令行不可读**（`Get-CimInstance` 拒绝访问 = `OpenProcess DENIED`）⇒ 与 `I-14-E` 同一环境阻断，以 **`unverified`** 登记，**不作开工阻断**。
- 窗口计划（见 `impact_scope.json.stop_restart`）：先记录原 `desired_state` → 仅在明确窗口内 pause → 部署 → **按记录的原意图恢复，不因工具退出无条件 resume**（`card_I-16-B` L8）→ dayu 4 个 entry point 为短命令，部署后仅需版本类复验（本卡未执行）。

### 4.3 恢复步骤

1. 代码层：回到冻结 HEAD（**需 git 写 ⇒ owner 另批**；本卡零 git 写）；
2. dirty/untracked 层：用 `snapshot/` 还原（R1 已证逐文件 sha256 相等）；
3. 安装层：按 `combo_manifest.install` 的 pth/finder/direct_url/RECORD 哈希复原；
4. 数据层：迁移前备份 → restore（R2 字节相等）；更高版本 fail-closed（R3）；**registry 先备份**（R5 无守卫）；
5. 进程层：按部署前记录的 `desired_state` 恢复；
6. **恢复不可证 ⇒ `STOP` 判 `blocked`，不以关闭严格门回滚。**

### 4.4 未授权影响

**无**（`unauthorized_impact=false`）。若窗口内出现以下任一项，**停下来向用户报具体请求**，不自行执行：
`git add/commit/push`（owner 另批）· 停止他人进程 · 改 `raw/` 或 registry 生产数据 · 联网 · 放行任何参数。

---

## 复现命令（只读/隔离）

```powershell
$d = '.planning\2026-09-19-three-project-history-audit\execution_runs\I-16-A\a20260926-01'
python -X utf8 -B $d\_probe_newprocess.py --out $d\probe_bind.json
python -X utf8 -B $d\_bind_combo.py    --probe $d\probe_bind.json --hash-catalog
python -X utf8 -B $d\_recovery_drill.py --manifest $d\combo_manifest.json
python -X utf8 -B $d\_run_mutations.py
python -X utf8 -B $d\_verify_combo.py  --probe $d\_live\probe_final.json --out $d\_live\result_final.json
```

## 未满足项 / 登记项（不隐藏）

| id | 内容 | 处置 |
|---|---|---|
| `I14-E-unverified` | `OpenProcess` DENIED ⇒ `TESTSIDE` 三臂不可证、进程命令行不可读 | 按 §三十八 逐字以 `unverified` 登记，**不作开工阻断**；不代其出结论 |
| `u-I16A-skillcopy` | `~\.claude\skills\revenue-forecast` 目标目录读/列被拒 | 该子项 `unverified`，列部署窗口必检 |
| `u-I16A-0` | 三仓组合在绑定期间被外部写入方改动（HEAD `bf0c8b27→dbe47450`、CW 两文件内容变化、untracked 50→51） | 原始输出不删改；以最终绑定为准；**复审者须在安静时刻复跑 `J1`，仍红则不得开窗** |
| `u-I16A-1` | 2026-08-08 worker 运行组合的 4 个模块字节已不可重建 | 禁止用作恢复目标；恢复目标 = C0 |
| `u-I16A-2` | 一次 drill 重跑出现 `R1=False`（对着**过期** snapshot 清单），随后整轮重绑 + 三次 drill 全绿 | 登记为过期清单导致的假红；以最终 `recovery_drill.json` 为准 |
| `OPEN-2` | `124,248.63`（真值 `38,175.95`）**只登记不消费** | 本卡未引用为部署输入 |

## 结论（对照卡文 L13）

- 动作 1–4 全部完成，产物四件齐备；
- 提案 + 隔离恢复演练**通过**（R1–R5 全绿；红绿变异 7 臂全符合冻结期望）；
- 资格 = **可进入具体部署窗口**（并附 `u-I16A-0` 复核前置条件）；**尚非已部署**，本卡**未执行任何生产变更**。
