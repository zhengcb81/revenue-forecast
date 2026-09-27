# I-16-B / a20260926-01 独立复审报告（前置 fail-closed 自评复核）

- 复审角色：`reviewer_i16b`（独立复审工位）；复审时刻 2026-09-26 23:2x–23:4x 本地（UTC+1）
- 被审 **4 件**：`oracle.md` · `blocked_request.md`（R1–R8）· `verification.json` · `handoff.json`
- 回源件（只读）：`execution_v2/card_I-16-B.md` · `OWNER_DECISIONS.md` · 上游 `I-16-A/a20260926-01/`（`accepted_scoped` + `reviewer_report.md` `ACCEPT(P2×2/P3×5)`）· 只读观测 `worker_state_observed.txt` · 变异臂 `_inputs/{G,M1..M4}/**`
- **写入面 = 本报告 2 文件**（`reviewer_report.md` + `reviewer_report.sha256`）；不写卡状态（`status` 维持 `blocked`，落定走父直写）；三仓只读（仅 `git diff HEAD --name-only` / `--cached` / `ls-files --others` / `rev-parse HEAD`，**未跑 `git status`**）；零 git 写；**禁联网**；未复跑被审脚本（会落盘，与写入面冲突）

---

## VERDICT：`ACCEPT`（附 `P2×2` + `P3×5`；**无 P1**）

> 判级依据（P1 三条件逐一排除）：
> ① **非误判**——`C1=false` 经我方独立复算成立（`OWNER_DECISIONS.md` 全文「部署」= **0 次**，且全文无任何覆盖 `I-16-B` 部署范围的裁定）⇒ 不存在「实际已有授权却判无」；
> ② **无未记录的部署动作**——运行窗口（本地 22:55–23:20）内 `C:\Miniconda` 安装层 / RF / CW / DAYU 三仓（排除 `.git/.planning`）改动文件数 = **0 / 0 / 仅外部并发 6 件 / 0**，生产 `catalog.sqlite3` mtime 仍为锚点 `2026-09-26T17:48:22Z`；
> ③ **红线未破**——封盘 `f2178768…`(51697 B) 与 store `b2063ac8…`(61231 B) 我方收尾复算**零字节一致**；RF `git diff HEAD` 非 `.planning` = 0、staged = 0、`git_status_run=false`；无联网、无参数放行、五份计划文件未动。
> 依卡文 L13「未运行 ⇒ `blocked`」，`blocked` 即本卡合格交付。

---

## 0. 收尾复哈希（写本报告前自算，逐件对台账）

| 文件 | 自算 bytes | 自算 sha256 | 台账/引用 | 结论 |
|---|---|---|---|---|
| `oracle.md` | 15350 | `04c2bac4c34f1f72616952d2f2266a8011dfe08bd390aa9f19479515e3d5c76d` | `handoff.written_files` | ✅ |
| `blocked_request.md` | 5960 | `3f75405d2871477a7e276fb4da56a1645a35f0bda36d03e5109790e58bdefbcb` | 同上 | ✅ |
| `verification.json` | 12578 | `4fe717194c9cc4ef42e3dfea4044cf2105d93051d721cd427aa1c4ad23f00990` | 同上 | ✅ |
| `handoff.json` | 18110 | `0e2fdeeb9013d980e1e95f55ae460ac0eddf9affed710ff705705f349ebb920a` | 声明「自身不入台账」 | ✅（缺口见 P3-4） |
| `worker_state_observed.txt` | 671 | `9b4b0760a47b925c6ae94c736a9f426018ee2dc92ee407e0eaa0a92914fbf8b6` | `verification.worker_state_observed` | ✅ |
| `gate0_raw.txt` | 1251 | `bb949f50a051034400cd96392d33550c90a80adb03e93090e8aae5dac7bc196c` | `verification.gate0_raw_sha256` | ✅ |
| `expectations.json` | 839 | `01332aee46727ca96275bf7a3bb61df17e65b2cb966b2ea5512b6d3d9d60a0b7` | `oracle §4` | ✅ |
| `execution_v2/card_I-16-B.md` | 1240 | `9af3f671e26f3c132cb765e28ad5c044676cdbc7fb710f4b0e35d302ae3f315e` | `oracle §9` | ✅ |
| `OWNER_DECISIONS.md` | 114027 | `c905ea515d4b5da1192e411fbb6b5d4fbb720cb5b9b20485b34fc402bd3e11e9` | `oracle §9` | ✅ |
| 上游 `I-16-A/reviewer_report.md` | 19885 | `b0bc2ec547a3e7ab0c838d256d400b672f9eba4b5ad0dfa712d1574e57e6fe33` | `oracle §1.4` | ✅ |
| 上游 `I-16-A/handoff.json` | 14922 | `8b6849109db11f962d5b3bb5fb0dd863ba200ad8bbfea1a2202f035835dca29f` | `oracle §9` | ✅（`status=accepted_scoped`，`status_transition=review_pending -> accepted_scoped`，`by: landing_parent_v3`，`status_authority.carrier` 逐字指向上表 sha） |
| 上游 `recovery_drill / impact_scope / deployment_proposal / combo_manifest` | 4606 / 6439 / 19037 / 64824 | `7130a6e0… / e0959fb9… / f6427b71… / a2b9147a…` | `oracle §9` | ✅ 4/4 |
| 封盘 `I-11-A/…/hypotheses.json` | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 红线 | ✅ 零字节 |
| store `OPEN2-C2-…/hypotheses_v3.json` | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 红线 | ✅ 零字节 |

⇒ **mismatches = 0**（台账未覆盖项见 P3-4）。

---

## 1. 裁决行 + 发现清单

| # | 发现 | 级别 |
|---|---|---|
| 1 | `C1=false` 独立复算**成立**；卡文 L6 前置三条件仅 C1 不成立 ⇒ `STOP`/`blocked` 正确，`blocked` 为合格交付 | 无发现（=ACCEPT 主依据） |
| 2 | R3 事实前提不完整：`desired_state 无任何记录` 仅对 `config/.source_catalog/` 成立，生产目录 `CW/.source_catalog/worker_control.json` **存在且 `desired_state="paused"`**，且上游 `combo_manifest` 已记 `worker_control_root_exists: true` | **P2-1** |
| 3 | 冻结期望自相矛盾：`expectations.json` M2/M3 同时要求 `C1=false` 与 `failed=["C2"]/["C3"]`，判定器 `failed` 必含 C1 ⇒ 两臂结构上永为 `rc=3`；`red_arms_ge_3` 仅在「扰动臂数=4」口径成立 | **P2-2** |
| 4 | R1⑤ 未逐字列出卡文 L9 的「已有复用 / 新文件摄取 / 适用工件失效最小重算」与「**记录所加载组合，与 I-16-A 对照**」 | P3-1 |
| 5 | 夹具副本 `_inputs/*/owner_decisions.md`（M1 `55932f93…`、attempt1 `db65638d…`）不在任何 sha 台账；变异证据可复算性略降 | P3-2 |
| 6 | 卡文行号口径：本 13 行文件中前置 = **L6**（`oracle/verification/handoff` 均引 L6，正确）；复审任务书所称 L7 为行号口径差异；L13 退出逐字一致 | P3-3 |
| 7 | `handoff.written_files` 不覆盖 `handoff.json` 自身（文件内已声明「不入台账」）——与 I-16-A P3-2 同类 | P3-4 |
| 8 | CW `untracked(non-planning)` 实测 **67**（门 0 62 → 收尾 63 → 写盘后 64 → 我方 67）：外部并发仍在写入 ⇒ R4 静默前置**仍未达成**（与工位登记一致） | P3-5 |

---

## 2. ⭐ C1 判定核验（自算次数）

**方法**：`[System.IO.File]::ReadAllBytes` → SHA-256 + UTF-8 显式解码 → `Regex.Matches` 全文计数（非工具 grep 摘要）。

**输入同一性**：`OWNER_DECISIONS.md` = **114027 B / `c905ea51…e11e9`**，与 `oracle §9`、`verification.input_hashes`、`handoff.input_hashes`、I-16-A `verification.input_hashes` 四处引用**全部一致**；`_inputs/G/owner_decisions.md` 副本 = 同 sha 同长度 ⇒ 判定器 G 臂确以原件为输入。

| 关键词 | 自算次数 |
|---|---|
| **`部署`** | **0** |
| `部署范围` | **0** |
| `部署｜deploy｜rollout` | **0** |
| `上线` / `投产` / `灰度` / `迁移` / `切换` | 0 / 0 / 0 / 0 / 0 |
| `安装` | 2（**同一行 L542**：`PEND-5b` OCR 引擎「安装只许落在本卡隔离 venv / 默认禁止系统级安装」，与 `I-16-B` 无关） |
| `发布` | 1（L55，`I-09` 请求计数语境，与 `I-16-B` 无关） |
| `I-16-B` | **仅 1 行 2 处（L910）**：「`I-16-A` 的下一卡 `I-16-B` 依赖 `I-16-A`；`I-17-A ← I-16-B + I-14-B`」= 依赖顺序 |

**逐字比对（我方自 `OWNER_DECISIONS.md` 直接打印 L845–L890 后与被审引用逐行核对）**：

- `§三十八 裁定一`（**L879–L886**）：标题「`I-16-A` 开工门槛 —— 「授权开工（建议）」」+ 5 条开工判据（`I-08-A` 按 `[x]`、`I-14-E` 阻断以 `unverified` 登记不作开工阻断、动作 3 fail-closed **不放宽**、动作 4 上报维持、**「不授予：不代 `I-14-E` 出结论 · 不解 `TESTSIDE` · 不放行参数 · 产出仍须独立复审」**）⇒ 与 `oracle §1.2`、`handoff.authorized_by.owner_decision_s38_verbatim` **逐字一致**；授权对象 = `I-16-A` **开工门槛**，无部署范围。
- `§三十七`（**L852–L862**）：「全沙箱操作常设授权」+ 覆盖三仓读写/`OpenProcess`/任意目录创建修改 + 边界 1/2/3（纪律 16–20 继续有效、**「生产零未授权改动的纪律不变」**、**「commit/push 仍须 owner 另批」**）⇒ 与 `oracle §1.3`、`handoff.authorized_by.owner_decision_s37_verbatim` **逐字一致**；属**沙箱能力**授权，边界自限，不构成部署范围批准。
- 反向佐证（我方自读原文）：`I-16-A/deployment_proposal.md §4.4` 逐字「**若窗口内出现以下任一项，停下来向用户报具体请求**，不自行执行：`git add/commit/push`（owner 另批）· 停止他人进程 · **改 `raw/` 或 registry 生产数据** · 联网 · 放行任何参数。」（原文 L192 区段）；`I-16-A/reviewer_report.md` L13 资格口径逐字「仅『可进入具体部署窗口』，**尚非已部署**」。

**判定输出**：**`C1=false` 成立** —— 「部署」实测 **0 次**、两节逐字如工位所述、且即使完全抛开关键词口径，全文也不存在覆盖 `I-16-B` 部署影响范围（安装层 / config / catalog+registry 生产写入 / worker 启停 / 入口复验）的任何裁定。判定器 G 臂 `rc=0, failed=[C1]` 与我方独立结论一致。

---

## 3. R1–R8 请求清单合理性

| 条目 | 具体 / 可执行 | 与卡文对照 | 复审意见 |
|---|---|---|---|
| **R1** | 逐项（安装层 6 类路径 + config 4 件 + catalog/registry 三库 + worker 状态/启停 + 入口复验），并引用 `§4.4` 升级条款 | L6「具体部署范围已获授权」+ L9 安装/配置 | ✅ 具体、逐项、可裁定；**缺一不可**（第 3 项为部署必然项）。缺 L9 三个子检查与「记录所加载组合对照」→ P3-1；`raw/` 未列属**无实质漏项**（I-16-A `compat_boundary.raw` 逐字「部署不改 `raw/` 字节」） |
| **R2** | 要求窗口起止/触发条件 + 窗口内允许动作清单 | L8「只在明确窗口启动已绑定版本」 | ✅ 必需，现无窗口记录属实 |
| **R3** | 要求部署后 worker 目标状态与原 `paused`/等待任务处置意图 | L8「原 paused 任务不能因工具退出无条件 resume」 | ⚠ 请求本身必需且方向正确（不无条件 resume），但**前提句「`worker_control.json` 不存在（desired_state 无任何记录）」不完整** → **P2-1** |
| **R4** | 外部静默后复跑 `_verify_combo.py` live(J1) 至绿 | 上游 P2-1 逐字「仍红则不得开部署窗口」 | ✅ 必需；我方实测 CW untracked 仍升至 67 ⇒ 该前置确未达成 |
| **R5** | 相对路径补跑 R1 演练，或将声明收窄 | 上游 P2-2 逐字 | ✅ 必需 |
| **R6** | registry 前向无守卫 ⇒ 是否强制「先备份再开库」 | 上游 `open_questions` 第 5 项未决 | ✅ 必需（`recovery_drill R5` 实测 `0→1` 自动 bump、`>1` 静默接受，我方在上游 `recovery_drill.json` 原文复核一致） |
| **R7** | 指定具备工作区外写入面/进程能力的执行主体 | `START_HERE` 派单标能力主体；本会话实测 workspace-write + 审批禁用 | ✅ 必需，且与我方本会话权限边界同源（我亦无法越权写 `C:\Miniconda`/两产品仓） |
| **R8** | I-14 测量器 `command-id/argv/nodeid/sample` 绑定 | L10「用 I-14 已验证测量器…；命令不能猜，须 I-00-B 绑定」 | ✅ 必需 |

**漏项复核（对比卡文 L8–L11 授权面）**：L6 三条件 → R1（C1）/C2 由 R4 兜底/C3 由 R5+R6 兜底；L8 → R2+R3；L9 → R1①②⑤（子检查未逐字 → P3-1）；L10 → R8；L11 → C3 已绿 + R5/R6；L13 → 已按 `blocked` 落地。**无阻断性漏项**；R1–R8 全部落实后本卡方具备复派条件，清单设计为「缺一不可」合理。

---

## 4. 零部署动作核

1. **`worker_state_observed.txt` 为只读记录**（逐行核）：`utc=2026-09-26T22:10:35Z`、明记「只读观测；未启动/未停止/未暂停任何进程；未写任何产品文件」、`git_status_run=false`；我方对同路径复测：`config\.source_catalog\worker_runtime.json` 2410 B / mtime `2026-08-08 10:41:09(+1)` = 记录 `2026-08-08T09:41:09Z` ✅、`worker_state.json` 2167 B ✅、`worker_runs.jsonl` 229881 B ✅、`worker_control.json` 在该目录 **ABSENT** ✅；`pid=15596` 记录为已消亡、`code_version=21860fd` ✅。⇒ 记录与盘面逐项一致，无伪造。
2. **无装/配/启停痕迹（窗口扫描，本地 22:55–23:20 = 卡运行窗）**：
   - `C:\Miniconda\Lib\site-packages`（含全部 `company_wiki`/`dayu_agent` pth·finder·dist-info）+ `C:\Miniconda\Scripts\dayu-*.exe`：**0 件**在窗口内被改（现存 mtime 最新为 `2026-07-11`，多数 `2026-05-30`）；
   - `revenue-forecast`（排除 `.git/.planning/.mypy_cache/.ruff_cache/.pytest_cache/.tmp-*`）：**0 件**；`dayu-agent`（排除 `.git/.venv/node_modules`）：**0 件**；
   - `company-wiki`（排除 `.git/.planning`）：窗口内 **6 件**，全部为 `docs/plans/narrative-evidence-pilot-2026-09-26/g1_{holdout,retest}_{manifest,metrics}_v*.json`（22:56–23:19）⇒ **外部并发工位**（与工位登记的 `u-I16A-0` 漂移同源），`config/`、`.source_catalog/`、`src/`、`raw/` **0 件**；
   - 四个 config 文件（`RF/config/{company_wiki,filing_fetch}.json`、`CW/config/{source_catalog,source_catalog_worker}.yaml`）mtime 分别为 `2026-07-26 / 2026-09-20 / 2026-09-03 / 2026-08-07` ⇒ 窗口内未动。
3. **数据层零改**：`CW/.source_catalog/catalog.sqlite3` = 3,055,796,224 B、mtime `2026-09-26 18:48:22(+1)` = `2026-09-26T17:48:22Z`（= I-16-A 锚点逐字段一致）、`user_version=0` 记录未变；`config/.source_catalog/catalog.sqlite3` 188416 B mtime `2026-08-08`；registry 三库与 `worker_*.json` 全部停留在 `2026-08-xx` ⇒ **窗口内无迁移、无备份、无 worker 写入/启停**。
4. **三仓 git 只读复算（未跑 `git status`）**：RF `HEAD=b7a6a116…` `diff=3830 / 非.planning=0 / staged=0`、untracked(非.planning)=**48**（门 0 同值）；CW `HEAD=dbe47450…` `8/8`；DAYU `HEAD=2115c86d…` `1/1` + untracked 1 —— 与 `verification.git.final_recount`、`gate0_raw.txt` **全部一致** ⇒ 归因本卡的产品仓改动 = **0**。
5. **变异 `attempt2`**：我方自读 `_inputs/*/result.json` 的 `rc` —— **G=0、M1=0、M2=3、M3=3、M4=0** ✅；`G: NOT_ESTABLISHED failed=[C1]`；**`M1: ESTABLISHED rc=0`**，其注入行（我方自 G/M1 副本 diff 得唯一新增行 L915）为「裁定X-M1注入（**测试夹具·伪造授权臂**）：授权 I-16-B 按 impact_scope.json 清单执行部署…」且仅存在于臂副本（114271 B，原件 114027 B sha 未变）⇒ **判定器消费授权信号、非恒红，判据真**；`M4: NOT_ESTABLISHED failed=[C3]` 证明授权单独不放行（AND 组合）。`attempt1` 三臂 `rc=1` 我方复核为 `harness_error: JSONDecodeError`（M2/M3/M4 的 `result_attempt1.json` 原文一致）⇒ 登记属实、未回改冻结件。

---

## 5. P 清单与 `unverified`

### P2（须在向 owner 报 R1–R8 / 下个 attempt 前处置）

- **P2-1｜R3 前提不完整（事实性）**：`control.py L662` 逐字 `self.control_path = self.catalog_dir / "worker_control.json"`，`config/source_catalog.yaml` 逐字 `catalog_dir: "${PROJECT_ROOT}/.source_catalog"` ⇒ 权威控制文件 = **`C:\Users\郑曾波\Projects\company-wiki\.source_catalog\worker_control.json`**，该文件**存在**（178 B，mtime `2026-08-20 22:43:32`），内容逐字 `{"desired_state": "paused", "paused_at": 1785095409.9560082, "schema_version": "1.0", "stop_requested_for": "8efeb3b1e30c4a70b8d6781ae7b1b226", "updated_at": 1787262212.3703358}`；且上游 `I-16-A/combo_manifest.json` 已并列记录 `worker_control_json_exists: false`（`config/.source_catalog`）与 **`worker_control_root_exists: true`**。⇒ R3 的「`worker_control.json` 不存在（desired_state **无任何记录**）」仅对所探的旧目录成立，**括注不成立**。**影响**：不改变 C1/blocked 判级（C1 独立成立），但若原样报 owner，可能被误读为「系统无任何意图记录」，从而把一个已有 `paused` 记录的问题当成空白裁定。**要求**：改为「两目录并存：`config/.source_catalog/` 无 control 文件（08-08 运行态）；根 `.source_catalog/` 有 `desired_state=paused`（08-20）」，并要求 owner 同时裁定「部署后以哪个 `catalog_dir` 为准 + 目标状态」。
- **P2-2｜冻结期望自相矛盾导致 2/5 臂永红**：`expectations.json` 中 `M2: {"C1":false,"failed":["C2"]}`、`M3: {"C1":false,"failed":["C3"]}` 与 `_precondition_check.py L84`（`failed` 必含所有 false 条件）不相容 ⇒ attempt2 `M2/M3 rc=3` 是**期望规格缺陷**，非判定失真；实现者已如实登记、**未回改冻结件**（纪律 ✓）。但 `verification.mutations.red_arms_ge_3=true` 只在「扰动臂 = M1–M4 = 4」口径成立，按 `rc=3` 口径实际为 **2**。**要求**：下个 attempt 重冻期望（`failed[]` 与条件位一致性纳入自检）并统一「红臂」定义；本 attempt 条件位 **15/15** 与冻结期望一致，判别力（G/M1/M4）证据充分，故不降为 P1。

### P3（记录，不阻断）

- **P3-1｜R1⑤ 漏 L9 逐字要件**：未列「已有复用 / 新文件摄取 / 适用工件失效最小重算」与「**记录所加载组合，与 I-16-A 对照**」；建议补入 R1⑤，否则复派工位可能只做入口连通性复验。
- **P3-2｜夹具副本未入台账**：`_inputs/{G,M1..M4}/owner_decisions.md`（G/M2/M3 = `c905ea51…`；M1/M4 = `55932f93…`；attempt1 期 M1 = `db65638d…`）无 sha 台账条目，两轮间 M1 副本 sha 变化未说明（PowerShell 文本轮写 → UTF-8 字节忠实重建），影响变异证据的可复算性。
- **P3-3｜行号口径**：卡文 13 行文件中**前置 = L6**（`oracle/verification/handoff` 全部引 L6，正确）；复审任务书称 L7 属行号口径差异；**L13**「未运行则 `blocked`」逐字一致。
- **P3-4｜台账缺口**：`handoff.written_files` 不含 `handoff.json` 自身（文件内已声明）；`blocked_request/verification/oracle` 之外的 `_inputs/*/result.json` 仅部分入账。
- **P3-5｜CW 漂移未收敛**：CW `untracked(non-planning)` 门 0 `62` → 收尾 `63` → 我方复测 **67**；窗口内 6 件外部写入全在 `narrative-evidence-pilot-2026-09-26/**` ⇒ **R4「安静时刻复跑 J1 至绿」仍未具备条件**（登记，不阻断本 `blocked` 交付）。

### `unverified`（保持未解除）

- `I14E-unverified`：`OpenProcess` DENIED ⇒ 进程命令行 / `TESTSIDE` 三臂不可证（我方同源受限，不代其出结论）。
- `u-I16A-skillcopy`：skill 安装副本（Junction 目标）读/列被拒 ⇒ hash 未核（开窗必检）。
- `u-I16A-0`：CW 组合并发漂移（实测仍在扩大，67）⇒ J1 live 复跑未做。
- 生产 `catalog.sqlite3` **3 GB sha256 未由我方复算**（成本）：以 `size 3,055,796,224 B + mtime 2026-09-26T17:48:22Z + 窗口内 0 写入` 作等价旁证；sha 层面**未独立复核**。
- 本卡「零进程启停」仅有工位记录 + 状态文件 mtime 旁证，**无进程级审计日志可回放** ⇒ 依记录采信。
- `_inputs/M2..M4/result_attempt1.json` 的编码损坏成因（PowerShell 文本轮写）按其 `reason` 字段采信，**未复现该写入路径**。

---

## 6. 没做的事（明确边界）

1. **未写卡状态**：`status` 维持 `blocked`；本报告不产生 `accepted/changes_required` 落定，落定走父直写。
2. **未复跑被审脚本**（`_precondition_check.py` / `_build_arm_inputs.py` 均会写 `_inputs/**`，与「写入面 = 2 新文件」冲突）⇒ 改为**只读自算等价复核**：`OWNER_DECISIONS` 全文计数与两节逐字、G/M1–M4 结果 JSON 自读、G↔M1 夹具 diff、三仓 git 只读计数、四仓+安装层窗口扫描、盘面 mtime/size 复核、收尾复哈希 17 件。
3. 未跑 `git status`、零 git 写、**零联网**、未动产品三仓与任何被审/上游文件、未解 `skill` 副本 ACL、未代 `I-14-E` 出结论、未放行任何参数、未派 `I-17-A`、未执行任何部署/安装/配置/启停/数据层写入。
4. 未核 `I-08/I-09/I-14` 依赖细项（§三十八 已授权免核）、未复算 3 GB 生产库 sha、未复跑 J1 live（须写盘，属开窗前置 R4）。
