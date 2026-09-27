# I-16-B oracle（**先冻结**：写于任何前置判定脚本与变异运行之前）

- 卡：`execution_v2/card_I-16-B.md`（sha256 `9af3f671e26f3c132cb765e28ad5c044676cdbc7fb710f4b0e35d302ae3f315e`，1240 B，13 行）
- attempt：`execution_runs/I-16-B/a20260926-01/`（**新建**；卡文明令「运行生产步骤时另建新的 attempt」）
- 角色：`implementer_i16b`（部署负责人 / 实现者）；**不自签** · **不放行参数** · **不派 `I-17-A`**
- 冻结时刻：2026-09-26T22:0xZ（门 0 已留档 `gate0_raw.txt`；本文件写于 `_precondition_check.py` 首次运行之前）
- 写入面：仅本 attempt 目录（`.planning` 内）；**产品三仓零写**；`git status` 禁跑；零网络

---

## 0. 领取与绑定（固定九步 1–2）

- card-id `I-16-B` · parent `I-16` · 依赖 `I-16-A`（`accepted_scoped`）· parent agent `session-19074bf0-0205-4315-af73-9db57597275a`
- 复述本卡一个可观察结果：**「实际部署结果与恢复边界有记录；未运行 ⇒ `blocked`」**（卡文 L13）
- 解释器：`C:\Miniconda\python.exe` 3.13.9（只跑本 attempt 内自写只读脚本）；cwd = 本 attempt 目录
- 允许写目录：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-16-B/a20260926-01/**`（且仅此）
- 绑定命令（本次唯一产品侧命令 = 只读 git 计数，已在门 0 执行）：
  `git -C <repo> -c core.quotepath=false diff HEAD --name-only` / `diff --cached --name-only` / `ls-files --others --exclude-standard` / `rev-parse HEAD` —— **无 `git status`、无 git 写**
- 判定脚本（绑定 argv，输出只落本目录）：
  `C:\Miniconda\python.exe -X utf8 -B _precondition_check.py --inputs <arm-dir> --expect expectations.json --out <arm-out.json>`

---

## 1. 授权逐字（`authorized_by`；卡文 L7 + `I-16-A` 复审 sha + §三十八）

### 1.1 卡文前置（`card_I-16-B.md` L6，逐字）

> 前置：具体部署范围已获授权、组合冻结、恢复可用。运行生产步骤时另建新的attempt，不能把隔离绿灯当生产已完成。

### 1.2 `OWNER_DECISIONS.md §三十八 裁定一`（L879–L886，逐字）

> ### 裁定一：`I-16-A` 开工门槛 —— **「授权开工（建议）」**
> **依据卡文**：`card_I-16-A.md` L5 `依赖：I-07-E、I-07-D、I-08、I-09、I-13、I-14、I-15`。
> **开工判据（owner 明文改判，`§三十四` 同款）**：
> 1. **已 `accepted`**：`I-07-D` · `I-07-E` · `I-09` · `I-13-A` · `I-13-BC` · `I-15-A` ✓
> 2. **`I-08-A`**：按 `task_plan` 清单 **`[x]`** 视为满足（其 `review_pending` 是复审明令「`not-granted` 项 3 禁写 `accepted`」的**刻意状态**，非未完成）
> 3. **`I-14` 家族**：`A/B/C/D` 已落（`D` 的 `R2` 凭证修复 2026-09-26 `accepted_scoped`）；**`E` 被 `OpenProcess` 环境阻断 ⇒ 以 `unverified` 登记，不作开工阻断**
> 4. **红线（不因开工而放宽）**：`I-16-A` 自身动作 3「**不能证明恢复则 `blocked`，不以关闭严格门回滚**」**维持 fail-closed**；动作 4「真正未授权影响再向用户说明具体请求」**维持**
> 5. **不授予**：不代 `I-14-E` 出结论 · 不解 `TESTSIDE` 环境阻断 · 不放行参数 · 产出仍须独立复审

（其「执行映射 3」仅记：**`I-16-A` 的下一卡 `I-16-B` 依赖 `I-16-A`** —— 依赖顺序，非部署范围授权。）

### 1.3 `OWNER_DECISIONS.md §三十七`（L852–L863 关键句，逐字）

> **全沙箱操作常设授权：「给你授权所有的沙箱操作，不要再问我了」**（2026-09-26 17:5x，原话）
> - **本会话内编排层（父）的一切沙箱提权操作，owner 一次性常设授权**，**无需逐次审批**。
> - 覆盖：`dayu-agent` / `company-wiki` / `revenue-forecast` 三仓全部读写 · `OpenProcess` 等系统调用 · 任意目录的文件创建/修改（含 `raw/`、`tools/ 落点`）· 网络取证。
> ### 边界（**授权 ≠ 免除纪律**）
> 1. **纪律 16/17/18/19/20 全部继续有效** —— 提权是"许可"，不是"免检"：**破坏性操作仍须前像留痕+写后验证+fail-closed 回滚**；**派单仍须标能力主体**。
> 2. **生产零未授权改动** 的纪律不变 —— **本授权就是"已授权"的记账**：晋升/落点/施加均在授权范围内，**commit/push 仍须 owner 另批**（§三十二 先例）。
> 3. **产品仓提交（`git add/commit/push`）不在本授权内** —— 仍归 owner 逐次决定。

### 1.4 `I-16-A` 复审（carrier `reviewer_report.md`，sha256 `b0bc2ec547a3e7ab0c838d256d400b672f9eba4b5ad0dfa712d1574e57e6fe33`，19885 B，本会话复算一致）

- 裁决行逐字：`## VERDICT：`ACCEPT`（附 `P2×2` + `P3×5`；无 P1）`
- 资格口径逐字：`**资格口径（卡文 L13）**：仅「可进入具体部署窗口」，**尚非已部署**；本卡未执行任何生产变更`
- **P2-1 逐字（须在部署窗口前处置）**：`按实现者 u-I16A-0（high）与 owner 规则 —— 「安静时刻复跑 J1，仍红则不得开部署窗口」：本次复跑即为红 ⇒ 当前不得开窗。…须在并发工位静默后重跑 J1 至绿方可开窗。`
- **P2-2 逐字**：`R1 恢复演练目的地命名碰撞 … 声明强于实证范围。建议：以相对路径补跑一次 R1，或将声明收窄`
- `handoff.status = accepted_scoped`（`status_transition: review_pending -> accepted_scoped`，`by: landing_parent_v3`）

---

## 2. 前置自评判据（fail-closed；**本节先于判定冻结**）

卡文 L6 三条件，逐条可判定化；**任一不成立 ⇒ 整体不成立 ⇒ `STOP` 判 `blocked`**，不推断、不补授权（「不造授权」）。

### C1 —— 「具体部署范围已获授权」

- **成立的唯一形态（正向证据，缺一即不成立）**：在 **owner 决策权威载体 `OWNER_DECISIONS.md`** 中存在 ≥1 行同时含 `部署` 与 (`授权`|`批准`|`同意`|`放行`)，且语义覆盖 `I-16-B` 部署影响范围清单（安装层 / config 写入 / catalog+registry 生产数据 / worker 状态与启停 / 入口复验）。
- **反向判据（任一命中即不成立）**：
  1. `OWNER_DECISIONS.md` 全文 `部署` 出现次数 = 0（冻结事实：本会话实测 **0 次**）⇒ 无任何部署授权；
  2. `§三十八 裁定一` 授权对象 = `I-16-A` **开工门槛**，且自带「**不授予**」清单，未提部署范围；
  3. `§三十七` 是**沙箱能力**常设授权，边界明写「生产零未授权改动纪律不变」「commit/push 仍须 owner 另批」，**不构成部署范围批准**；
  4. `I-16-A/deployment_proposal.md §4.4` 逐字：`若窗口内出现以下任一项，停下来向用户报具体请求：git add/commit/push（owner 另批）· 停止他人进程 · 改 raw/ 或 registry 生产数据 · 联网 · 放行任何参数` —— 而绑定组合的部署**必然**含 registry/catalog 生产数据写入（`impact_scope.json` 数据层与 registry 条目；`recovery_drill R5` 实测 `user_version 0→1` 自动 bump）与 worker 启停（`stop_restart.deployment_window_plan`）⇒ **升级条款被触发**，需用户具体请求在先。
- **判定输出**：`C1=成立` / `C1=不成立（authorization_not_established）`。

### C2 —— 「组合冻结」

- 成立形态：`I-16-A/a20260926-01/handoff.json.status == "accepted_scoped"` **且** `combo_manifest.json` 存在（sha256 `a2b9147ade7e6f35336816512c1bcb7a11fc4288f1f83d922d156143004b5fe6`，64824 B）。
- **登记但不改判**（复审 P2/P3 项属窗口前处置事项，非本条件定义）：`P2-1` J1 复跑现红（开窗前须绿）、门 0 实测 CW untracked(non-planning)=62（绑定 51、复审 55）⇒ 组合 dirty 层仍在被外部工位写入；`u-I16A-0` CW HEAD=`dbe47450…` 为父授权提交（§三十八 裁定三），**非漂移**。

### C3 —— 「恢复可用」

- 成立形态：`recovery_drill.json.all_checks_ok == true` **且** `recovery_provable == true`（R1–R5 全绿）。
- 登记：`P2-2`（R1 目的地命名碰撞，复审判「须在部署窗口前处置」）；`u-I16A-1` 2026-08-08 运行态 4 模块字节不可重建 ⇒ **禁作恢复目标**（恢复目标 = C0）。

### 整体

`前置成立 ⇔ C1 ∧ C2 ∧ C3`。**fail-closed**：证据缺失、模糊、仅有间接授权 ⇒ 记 `不成立`。不成立 ⇒ `STOP`、`status=blocked`、`handoff.next_request` 逐条列具体请求（卡文明令）。

---

## 3. 卡文动作逐字（L8–L11、L13；**仅当前置成立才执行**）

> 1. 记录用户原worker状态；需要时只在明确窗口启动已绑定版本，原paused任务不能因工具退出无条件resume。
> 2. 安装/配置后从实际用户入口验证：已有复用、新文件摄取、适用工件失效最小重算。记录所加载组合，与I-16-A对照。
> 3. 用I-14已验证测量器测业务失败率、时延和内存；sample不足不作总体SLO推断。
> 4. 若失败执行冻结恢复方案，保留已取得raw/journal；核实回到上个可用组合和原worker意图，不重复生产故障注入。
>
> 退出：实际部署结果与恢复边界有记录；未运行则blocked。交I-17自然观察，不立即宣布持续服务通过。

---

## 4. 变异清单（≥3；期望先冻结）

判定脚本 `_precondition_check.py` 读取 4 个输入（`owner_decisions` 文本 · `I-16-A/handoff.json` · `I-16-A/recovery_drill.json` · `I-16-A/impact_scope.json`），输出 `C1/C2/C3` 与整体裁决。臂目录：`_inputs/G`（真实输入）与 `_inputs/M1..M4`（**只改本目录内副本，原件只读**）。

| 臂 | 输入扰动（副本） | 冻结期望 verdict | 冻结期望 rc |
|---|---|---|---|
| **G** | 无（真实输入） | `NOT_ESTABLISHED`，failed=`[C1]`（C1=false, C2=true, C3=true） | `0` |
| **M1** | `owner_decisions` 副本追加行使 `部署+授权` 命中（伪造授权注入） | `ESTABLISHED`（C1=true,C2=true,C3=true）——证明判定器**非恒红**，确实消费授权信号 | `0` |
| **M2** | `handoff.json` 副本 `status` 改 `review_pending`（冻结失效） | `NOT_ESTABLISHED`，failed=`[C2]` | `0` |
| **M3** | `recovery_drill.json` 副本 `all_checks_ok=false`（恢复失效） | `NOT_ESTABLISHED`，failed=`[C3]` | `0` |
| **M4** | M1 授权注入 **且** M3 恢复失效（AND 组合性） | `NOT_ESTABLISHED`，failed=`[C3]`（授权单独不放行） | `0` |

- **rc 判读（本批自述 `exit_code_legend`）**：`0` = 该臂输出与上表冻结期望**逐字段一致**；`3` = 与冻结期望不一致（判定失真）；`1` = harness 失败（脚本/输入错误）；`2` = 无裁决（缺输入无法判定）。
- 红臂数（M1–M4 扰动臂）= 4 ≥ 3 ✓；G 为绿臂。
- **本判定不调用被测产品函数生成 expected**：期望全部由本文件手工先冻结。

---

## 5. rc 码表（冻结；`START_HERE.md` L96–L102 逐字引用）

| rc | 含义 |
|---|---|
| `0` | 通过（命令正常结束且业务判定通过） |
| `1` | harness 失败 |
| `2` | 无裁决 / 预期拒绝 |
| `3` | 未达预期 |

跨批聚合前先读本批 `exit_code_legend`（见 §4），不得假设码表一致。

---

## 6. 红线（本 attempt 逐条遵守）

- `OPEN-2`：`124,248.63`（真值 `38,175.95`）**只登记不消费**，不作任何部署输入。
- 封盘 `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B）与 store `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff`（61,231 B，`low/base/high` 全 `null`）——**零字节变化**（门 0 已复算）。
- **不放行参数** · **不自签**（`implementer_signed=false`）· **落定父直写** · **禁五份计划文件** · **禁 `.planning` 外写** · **禁联网** · **禁 `git status`** · **产品仓 git 零写** · **不派 `I-17-A`**。
- 不重复生产故障注入；恢复目标 = C0，**禁用 `u-I16A-1` 的 2026-08-08 运行态**；原 `paused`/等待态任务**不因工具退出无条件 resume**。
- 隔离绿灯 ≠ 生产已完成：`I-16-A` 的隔离演练结果不得被记作生产部署结果。

## 7. 环境限制（登记，不作授权）

- 本会话 DSH 沙箱 = **workspace-write**（可写仅 `C:\Users\郑曾波\Projects\revenue-forecast`）；**审批提示已禁用** ⇒ 工作区外写入（`C:\Miniconda\Lib\site-packages` 安装层、`company-wiki`/`dayu-agent` 仓、生产 catalog/registry）**会被策略拒绝且无法在会话内提权**。
- `OpenProcess` 对他人进程拒绝访问（`I-14-E` 同源阻断）⇒ 进程命令行/TESTSIDE 三臂 `unverified`，不代其出结论。

## 8. 门 0 自探留档（`gate0_raw.txt`，2026-09-26T22:01:49Z，逐字要点）

```
=== GATE0 BEGIN (I-16-B/a20260926-01) ===
utc=2026-09-26T22:01:49.442Z
readback=gate0 probe I-16-B a20260926-01 write-readback-delete
（Remove-Item 后 Test-Path=False ⇒ 探针已删；标签含义见 gate0_raw.txt 尾注）
sha256 …I-11-A\hypotheses.json = f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28 bytes=51697
sha256 …OPEN2-C2-REGISTRATION\a20260926-01\hypotheses_v3.json = b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff bytes=61231
git_diff RF HEAD=b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb total=3830 non_planning=0 staged_total=0 untracked_non_planning=48
git_diff CW HEAD=dbe474504a6187e22c37918743d17fe59c85a0a8 total=8 non_planning=8 staged_total=0 untracked_non_planning=62
git_diff DAYU HEAD=2115c86d5a9027bb51cbbc8a4d0175080732e4e6 total=1 non_planning=1 staged_total=0 untracked_non_planning=1
git_status_run=false · git_writes=0
=== GATE0 END ===
```

## 9. 冻结输入 sha256（判定与复审复算用）

| 输入 | sha256 | bytes |
|---|---|---|
| `execution_v2/card_I-16-B.md` | `9af3f671e26f3c132cb765e28ad5c044676cdbc7fb710f4b0e35d302ae3f315e` | 1240 |
| `execution_v2/common_root_cards.md` | `f8127541c763859761eb6affdd9f3c898766e249205436ff164b73c2621cd260` | 530 |
| `execution_v2/START_HERE.md` | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` | 20436 |
| `execution_v2/review_and_handoff.md` | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` | 4005 |
| `OWNER_DECISIONS.md` | `c905ea515d4b5da1192e411fbb6b5d4fbb720cb5b9b20485b34fc402bd3e11e9` | 114027 |
| `I-16-A/…/handoff.json` | `8b6849109db11f962d5b3bb5fb0dd863ba200ad8bbfea1a2202f035835dca29f` | 14922 |
| `I-16-A/…/reviewer_report.md` | `b0bc2ec547a3e7ab0c838d256d400b672f9eba4b5ad0dfa712d1574e57e6fe33` | 19885 |
| `I-16-A/…/impact_scope.json` | `e0959fb90afc68b793fa3260bb553a2d1aa029dba0baf4c1b221be05603ac71f` | 6439 |
| `I-16-A/…/recovery_drill.json` | `7130a6e09a246abf7c685373d7401a1a57f4592e079e9c6f9c4eca38b30780fd` | 4606 |
| `I-16-A/…/deployment_proposal.md` | `f6427b7173f5e63fa56e48090deb24b34339a91587ea49b5f1ec1f7b2dd3686b` | 19037 |
| `I-16-A/…/combo_manifest.json` | `a2b9147ade7e6f35336816512c1bcb7a11fc4288f1f83d922d156143004b5fe6` | 64824 |

## 10. 退出判据（卡文 L13）与本卡状态形态

- `实际部署结果与恢复边界有记录；未运行则blocked` ⇒ 前置不成立而未运行时，**`blocked` 即合格交付**（卡文 L11 / 调度明令），`next_request` 逐条列具体请求。
- 交 `I-17` 自然观察；**不立即宣布持续服务通过**；不代 `I-14-E` 出结论。
