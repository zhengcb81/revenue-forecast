# 隔离事件记录（实施者上报）：生产 `scripts/model_registry.py` 在 r3 追加期间被回退到未挂载扩展模型的状态

- 记录时间：2026-09-20（r3 追加作业期间，发现于最后一次生产 hash 复核）
- 记录人：M25–M28 卡的实现者（本会话）
- 状态：**已上报，未处置**（不回退、不修改生产任何文件）
- 影响：**M25/M26/M27/M28 四卡的 r2 `accepted_scoped` 判定触发其自身"失效条件"，现已失效，须重新复核**

## 1. 事实（可复核）

| 项 | 值 |
|---|---|
| 生产文件 | `C:\Users\郑曾波\Projects\revenue-forecast\scripts\model_registry.py` |
| 磁盘 sha256 | `1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86` |
| 磁盘 size / mtime | 19703 B / `2026-09-20 04:35:32` |
| 锚定值（全计划基线 + 本批四卡） | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`（26446 B） |
| git HEAD | `cc78c5298acd5a5ff8b898d9aa237fc5a8559979`（`2026-09-20 04:27:52` "audit(planning): round-3 continued …"） |
| `HEAD:scripts/model_registry.py` blob | `c80075c4dadbed827aac0937ed84b8f820978c0c`（19703 B） |
| 工作树 blob（`git hash-object`） | `c80075c4dadbed827aac0937ed84b8f820978c0c` —— **与 HEAD 完全相同** |
| `git status --porcelain -- scripts/model_registry.py` | **空**（该文件相对 HEAD 无改动） |
| 该文件最后一次进入历史的提交 | `4a8b454e 2026-07-25 14:49:36 feat: add reserve_depletion model … (v3.9.0)` |
| 锚定 blob `9ec65295…` 是否存在于任何提交 | **否**（`git log --all --find-object=…` 0 命中）；它从来只是一个**工作树状态** |

## 2. 内容差异（锚定状态 → 当前状态）

`git diff --no-index` 锚定快照（`iso/checkout_scripts/model_registry.py`，= 生产锚定态）与当前生产文件：**265 diff 行**（20 增 / 127 删）。关键差异：

1. **删除扩展挂载**：`from model_extensions import build_extension_specs` 被删除，`MODEL_REGISTRY` 的
   `] + list(build_extension_specs(ModelSpec, ModelRegistryError))` 被删除 ⇒ 注册表只剩 23 个模型。
2. **四个被本批判定的模型消失**：当前生产文件中**完全不存在** `installed_base_aftermarket`、
   `store_cohorts`、`renewable_generation`、`aum_fee_bridge` 任何一个 id。
3. **`driver_bounds` 机制整体消失**：`ModelSpec.driver_bounds` 字段、其 `__post_init__` 校验、
   `_spec(..., driver_bounds=...)` 参数、`driver_value_bounds()` 函数全部不存在。
   ⇒ 本批依赖的 `driver_value_bounds` 语义（`store_cohorts.new_store_productivity = (0, inf)`、
   `market_change = (None, None)` 等）在当前生产**不存在**。
4. 其他被回退项：`project_backlog` 去掉 `backlog_remeasurements`；
   `reserve_depletion` 去掉 `reserve_revisions`；`cohort_subscription` 的暴露公式回退为
   `(opening+ending)/2`；多处 `math.fsum` 回退为普通加法。

`scripts/model_extensions.py` **未被改动**：仍在，sha256 = `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`（与锚定值一致），blob = `9a40b464099a64b7c1522ac32f6f1842954aa20d`，mtime `2026-09-18 08:27:53`。即：扩展模型的**定义**还在，但**注册表不再挂载它们**。

**关键补充证据（决定了整件事的性质）**：`git status --porcelain -- scripts/model_registry.py scripts/model_extensions.py`
返回 `?? scripts/model_extensions.py` —— 即 **`model_extensions.py` 在本仓库里是未跟踪文件（untracked）**。
因此"扩展模型注册"这一整套依赖（`model_extensions.py` 的存在 + `model_registry.py` 里那两行挂载）
**从来只是一个未提交的工作树状态**：挂载行写在未提交的 `model_registry.py` 里，而被挂载的模块本身也不在版本控制中。
任何把工作树重置到 HEAD 的操作（提交、reset、checkout、clean 之外的等价动作）都会同时抹掉这两半。

## 3. 归因

- **不归因本实现者**：本会话对三个生产仓的写入为 0。可核证据：四卡 `iso/checkout_scripts/model_registry.py`
  的 sha256 仍为锚定值 `9ec65295…`（本会话只**读取**生产文件并**复制**它）；本会话最后一次主动读取该文件时
  （r2 收尾与 r3 追加的 `final_pass`）hash 仍为锚定值；变化发生在 r3 追加期间。
- 已知与该时间窗重合的外部动作：父计划的提交 `cc78c529`（`04:27:52`）。该提交把工作树里那份
  **未提交的**扩展版 `model_registry.py` 替换/还原成了已提交的历史版本（`4a8b454e`，2026-07-25），
  于是"扩展模型注册"这一**从未提交**的工作树状态消失。
- 结论：这是一次**工作树状态被提交动作带走**的事件（与 `_isolation_incidents/20260920-prereg-expectations-leak`
  的 I-4 同类：提交动作改变了非提交内容的可见性）。确切执行者与意图**未确定**，登记为 provenance gap。

> **注意**：上面第 3 节写于根因查明**之前**，其中"确切执行者与意图未确定"的表述已被下面的第 7 节取代；
> 本节文字按 append-only 保留原文，不改写。

## 4. 后果

1. **四卡 r2 判定自动失效**：reviewer 明示失效条件包含 "`iso/checkout_scripts/{model_registry,model_extensions}.py`
   （须恒等于生产 `9ec65295…/9939480b…`）发生任何变化"。生产侧锚定指纹已变 ⇒ 条件触发。
2. **四卡被测入口在当前生产上不再存在**：`calculate_registered_model(model_id="installed_base_aftermarket" | …)`
   在当前生产会立刻抛 `ModelRegistryError: unsupported revenue model: <id>`（`MODEL_REGISTRY[model_id]` KeyError 分支）。
   本批的 A–C 公式资格证明的是**锚定态**下的行为，不能移植到当前生产态。
3. **本批冻结证据本身未被污染**：四卡冻结四件套（`input/oracle/cases/run_result.json`）与 r2 判定时逐字节相同
   （见各卡 `evidence/<CARD>/revision_r3.json` 的 `frozen_four_piece.identical_to_r2 = true`）；
   `iso/checkout_scripts/` 两份快照仍等于各自锚定值。即"证据没坏，但**靶子没了**"。

## 5. 处置与建议（不由实现者决定）

- **本实现者未做任何处置**：未回退 `model_registry.py`，未 `git checkout/restore`，未写生产任何文件，
  未改四卡任何冻结件。四卡 `status` 保持 `review_pending`，实现者**不自签**、也不自行宣布失效之外的动作。
- **需 owner 裁定（二选一）**：
  1. 若"扩展模型版 `model_registry.py`"才是应有状态：需由 owner 把该工作树状态**重新建立并提交**
     （使其有 blob 可锚定），随后四卡按其原始资格口径**重新复核**（预期结论不变，因为被测字节仍是
     `9ec65295…`；但必须重新绑定生产指纹）。
  2. 若回退才是应有状态（即扩展模型本批次不应存在）：四卡公式资格**失去对象**，
     应改判 `blocked`（缺样本/前提：被测模型在当前生产未注册），并另开卡决定扩展模型是否重新引入。
- 无论哪种，**不要**把本批冻结件（`input/oracle/cases/run_result.json`、`oracle.md`、`binding.json`、
  `qualification.json`、`handoff.json`）改写以"适配"新生产状态 —— 那会销毁唯一有效的锚定态证据。

## 6. 本轮（r3）已完成、且不受本事件影响的追加

- 四卡 `review.md` **只追加**转录了 reviewer 的 r2 裁决正文（append-only，前缀字节哈希已实测等于追加前哈希）；
- 四卡 `evidence/<CARD>/append_record_r3.json`（追加证明）与 `revision_r3.json`（r3 台账 + P3 A–D 只追加更正）。

这两项记录的是"r2 判定在**其作出时点**有效"，与本事件不冲突：失效是**时点之后**由外部生产变化触发的。

---

## 7. 处置与恢复（owner 裁定：选项 1；本节由实现者按 owner 转达**追加**，上文一字未改）

### 7.1 根因（编排层自身，非任何 attempt）

父 agent 上一轮的 `git add/commit/push` 作业触发了仓库自带的 **pre-commit / pre-push 门**：

1. 该门在 **04:35:31** 把未暂存改动导出为补丁 `C:\Users\郑曾波\.cache\pre-commit\patch1789875331-33652`
   （557,924 B）；
2. 随后执行 `git checkout -- .` 回滚其自动修复；
3. 该命令在 **3 个被并发占用的 scratch 文件**上以 `unable to unlink ... Invalid argument` 失败并
   **返回 255**，补丁因此**未被回放**；
4. 结果：生产工作树被重置到 HEAD（相关文件 mtime 全部为 `04:35:32`）。

同一根因也解释了 I-08-B 复核独立发现的另外 5 个文件在同一秒"变干净"：
`scripts/revenue_core.py`、`scripts/contracts/constants.py`、`scripts/revenue_report.py`、
`tests/test_backtest.py`、`SKILL.md`。

因此第 3 节"确切执行者与意图未确定"的表述**已被本节取代**：执行者是编排层的 git 门（非用户、非本实现者、
非任何 attempt），意图是常规提交作业，失控点是那个返回 255 的 `git checkout -- .`。

### 7.2 恢复方式（选项 1：重建扩展模型版）

以**同一补丁**的**非 `.planning` 子集**恢复（避免把本计划的证据文件一并回放）：

```
git apply --check --exclude=.planning/* <patch1789875331-33652>   → exit 0
git apply         --exclude=.planning/* <patch1789875331-33652>   → exit 0
```

### 7.3 恢复后实测（实现者独立复算，非转述）

| 文件 | 恢复后 sha256 | size | mtime |
|---|---|---|---|
| `scripts/model_registry.py` | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` = **锚定值** | 26446 B | 04:40:53 |
| `scripts/model_extensions.py` | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` = **锚定值**（仍为 untracked） | 14475 B | 08:27:53（未动） |
| `scripts/revenue_core.py` | `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae` | 14136 B | 04:40:53 |
| `scripts/contracts/constants.py` | `278e3e02df15e556f4851b46711a2f36aac5b7e6a9820c27e0ca31b02858d0ae` | 5063 B | 04:40:53 |
| `scripts/revenue_report.py` | `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f` | 69765 B | 04:40:53 |
| `tests/test_backtest.py` | `d0972e238066f40e4c52d25806683749ddfa2c84e7f6652f38ff44f3b7efc16e` | 17665 B | 04:40:53 |
| `SKILL.md` | `45e4e343eba4f6e766cdb163d21c35a7f7beeb603d3c8b237339de440dc47806` = **I-00-A 冻结基线** | 26378 B | 04:40:53 |
| `CHANGELOG.md` | `bcba3dd50278b677ef0af63725a5d635763a40bd9f92089dfc37ff17529c0a8e` | 19601 B | 04:40:53 |

扩展挂载与四模型已回归当前生产：`model_registry.py:10` `from model_extensions import build_extension_specs`、
`:244` `] + list(build_extension_specs(ModelSpec, ModelRegistryError))`、`:272` `driver_value_bounds(...)`。
四卡 `iso/checkout_scripts/{model_registry,model_extensions}.py` 与生产**重新逐字节一致**
（`9ec65295…` / `9939480b…`）⇒ reviewer 的失效条件**已消除**，四卡 r2 `accepted_scoped` **继续有效**，
不改判 `blocked`。

### 7.4 时点限定（重要，供所有下游引用）

- 在窗口 **`04:35:31` – `04:40:53`（含 `04:5x` 的复核读取）** 内，生产确实**不是**锚定态。
- 因此**任何记录该窗口内 `production_hashes_unchanged=false` 的产物都是正确告警**，
  包括本实现者在 r3 收尾时读到 `model_registry.py = 1f2639e1…` 的那一次复核。
- **不得**据该窗口内的告警去改动任何期望值、阈值或冻结件；**不得**把该窗口内的哈希当作新基线。
- 引用生产哈希时须**带时点**：`9ec65295… / 9939480b…` 是 `04:40:53` 之后（以及 `04:35:31` 之前）的值。

### 7.5 残余风险（未处置，交 owner）

`scripts/model_extensions.py` **仍是 untracked**（`git status --porcelain` 显示 `?? scripts/model_extensions.py`），
而 `scripts/model_registry.py` 在工作树里 import 它。即：挂载关系现在虽然存在，但其中一半仍不受版本控制，
下一次任何 `git checkout -- .` / `reset --hard` / `clean` 都可能再次造成同一故障。
建议 owner 把 `model_extensions.py` 纳入版本控制（连同挂载行一起提交），使该状态有 blob 可锚定、
可被 `git status` 保护。本实现者**未**代为 `git add`（越权）。
