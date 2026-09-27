# I-16-B `blocked` 具体请求清单（卡文前置不成立 ⇒ `STOP`；调度/卡文明令逐条列「具体请求」）

- attempt：`execution_runs/I-16-B/a20260926-01/`（新建）
- 结论：**前置不成立**（`C1 具体部署范围已获授权` = **false**；`C2 组合冻结` = true；`C3 恢复可用` = true）⇒ 依卡文 L6/L13 与调度 fail-closed 指令 **立即 `STOP`**，**未执行任何部署动作**，不造授权。
- 判定证据：`oracle.md §2`（先冻结判据）· `_inputs/G/result.json`（`verdict=NOT_ESTABLISHED, failed=[C1]`）· `OWNER_DECISIONS.md` 全文「部署」出现 **0 次**（sha `c905ea51…`，本会话 UTF-8 复算）。
- 原 worker 状态已按卡文 L8 动作 1 **只读记录**：`worker_state_observed.txt`（未启动/未停止/未暂停任何进程）。

---

## 具体请求（请 owner/编排层逐条裁定；全部落实后本卡可复派新 attempt）

### R1 —— 【必需】`具体部署范围`的明示授权（缺此不开工）

请在 `OWNER_DECISIONS.md` 新增一条覆盖 `I-16-B` 部署范围的裁定，**逐项**明确是否授权（现状：该文件 0 处提及「部署」；`§三十八 裁定一` 授权对象仅为 `I-16-A` 开工且附「不授予」清单；`§三十七` 为沙箱能力授权、边界明写「生产零未授权改动纪律不变」）：

1. **安装层**：`C:\Miniconda\Lib\site-packages\__editable__.company_wiki-0.1.0.pth`、`company_wiki-0.1.0.dist-info/{direct_url.json,METADATA,RECORD}`、`__editable__.dayu_agent-0.1.4.pth`、`__editable___dayu_agent_0_1_4_finder.py`、`dayu_agent-0.1.4.dist-info/*`、`C:\Miniconda\Scripts\dayu-{cli,render,web,wechat}.exe`（写入/复装；按 `combo_manifest.install` 哈希可逆）
2. **config/policy**：`RF/config/company_wiki.json`、`RF/config/filing_fetch.json`、`CW/config/source_catalog.yaml`、`CW/config/source_catalog_worker.yaml`
3. **数据层生产写入**：`CW/.source_catalog/catalog.sqlite3`（3,055,796,224 B，锚点 `63c359aa…`、`user_version=0`）迁移/备份 + registry 三库（`source_registry`/`question_registry`/`run_store`，R5 实测 `0→1` 自动 bump、`>1` 无守卫）**备份后再写**
4. **worker 状态与进程启停**：`CW/config/.source_catalog/{worker_state,worker_runtime}.json`、`worker_runs.jsonl`、`worker_control.json` 的写入；worker 启动/pause
5. **入口复验与测量**：从实际用户入口执行复验与 I-14 测量器测量

> 依据：`deployment_proposal.md §4.4` 逐字「若窗口内出现以下任一项，停下来向用户报具体请求：… 改 `raw/` 或 registry 生产数据 …」——绑定组合部署**必然**含第 3 项，故升级条款已触发。

### R2 —— 【必需】明确部署窗口（卡文明令「只在明确窗口启动已绑定版本」）

请给出窗口的**起止时间或触发条件**及窗口内允许动作清单。现无任何窗口记录；`impact_scope.stop_restart.deployment_window_plan` 只是步骤草案。

### R3 —— 【必需】原 worker 意图确认（不无条件 resume）

只读实测（2026-09-26T22:10:35Z）：`worker_runtime.json`（mtime `2026-08-08T09:41:09Z`，`pid=15596` 已消亡，`worker_status=waiting`，`code_version=21860fd`）；**`worker_control.json` 不存在**（desired_state 无任何记录）；`worker_state.json`/`worker_runs.jsonl` mtime `2026-08-08T09:40:58Z`。请明确部署后 worker 的**目标状态**（保持不运行 / 恢复等待 / 启动），以及原 `paused`/等待任务的处置意图。

### R4 —— 【开窗前置 P2-1】安静时刻复跑 `J1` 至绿

复审逐字「安静时刻复跑 J1，仍红则不得开部署窗口……本次复跑即为红 ⇒ 当前不得开窗」。本卡门 0 只读实测 CW `untracked(non-planning)=62`（绑定 51、复审 55）⇒ 并发工位仍在写入。需外部静默后由具备执行位的工位复跑 `_verify_combo.py` live 至绿。

### R5 —— 【开窗前置 P2-2】R1 演练目的地碰撞处置

`drill_restore` 按 basename 落盘 ⇒ 109 行仅 104 目的地、5 件同名覆盖；请按相对路径补跑 R1，或将声明收窄为「快照层字节完整性 + 逐行拷贝字节相等」。

### R6 —— 【裁定请求】registry 前向无守卫的处置

R5 实测 registry `user_version>1` 静默接受、不建表不报错 ⇒ 是否**强制**部署窗口「先备份 registry 再开库」，需 owner/复审明示（`I-16-A handoff.open_questions` 第 5 项仍未决）。

### R7 —— 【能力主体】部署写入的执行会话

本工位会话 DSH 沙箱 = **workspace-write**、**审批提示已禁用** ⇒ 上述第 1/3/4 项（`C:\Miniconda` 安装层、`company-wiki` 仓、生产 catalog/registry）写入将被策略拒绝且**无法在会话内提权**；另 `OpenProcess` 对他人进程拒绝访问（`I-14-E` 同源阻断，命令行不可读）。请指定具备该写入面/进程能力的主体（父会话 `§三十七` 提权语境，或另开具备写入面的会话）执行，或明确将相应动作改为该主体的派单。

### R8 —— 【绑定】I-14 已验证测量器的命令绑定

卡文 L10 要求「用 I-14 已验证测量器测业务失败率、时延和内存；sample 不足不作总体 SLO 推断」。请给出所指测量器的 `command-id / argv / nodeid / sample 预算`（按 `START_HERE` 命令不能猜，须 I-00-B 绑定），本卡不猜命令。

---

## 不请求 / 不做（边界）

- 不请求 `git add/commit/push`（`§三十七/§三十八 裁定三` 明示 owner 另批；本卡零 git 写、禁 `git status`）
- 不请求联网、不放行任何参数（`low/base/high` 全 `null` 维持）、不代 `I-14-E` 出结论、不解除 `TESTSIDE` 阻断
- 不以关闭严格门回滚、不重复生产故障注入、**禁用 `u-I16A-1`（2026-08-08 运行态）作恢复目标**（恢复目标 = C0）
- 不宣布持续服务通过（交 `I-17` 自然观察；**未派 `I-17-A`**）
