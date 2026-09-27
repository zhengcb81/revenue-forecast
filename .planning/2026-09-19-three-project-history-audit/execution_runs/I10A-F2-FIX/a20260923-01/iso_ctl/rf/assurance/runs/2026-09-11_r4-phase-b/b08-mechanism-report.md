# B08 **机制层**执行报告（G8 第①级；owner 2026-09-13 批准「两级」）

> 工具：[evidence/b08_isolated_env.py](b08_isolated_env.py)（`build` / `snapshot` / `compare` / `selftest`）
> 原始证据：[evidence/b08-side-effects-before.json](b08-side-effects-before.json)、[evidence/b08-side-effects-after.json](b08-side-effects-after.json)
> 边界：**只做机制层**——非生产路径的小 catalog + 前后观察。**未**复制/移动/打开生产数据，**未**涉及真实字节（G8 第②级未获批）。

## 1. 本次实际执行（按顺序，全部可复跑）

| 步骤 | 命令 | 结果 |
|---|---|---|
| 守卫自测 | `b08_isolated_env.py selftest` | **5/5 拒绝生效**、temp 根被接受（见 §4 的事故说明——这条自测是**事后补的**） |
| 建隔离根 | `build --root %TEMP%\b08-isolated-demo` | 21 张表、`schema_version=1.2.0`、形状哈希 `2529a26bd2060e49`、catalog 237,568 B；**幂等**（同根重建形状哈希相同） |
| 隔离根**小跑** | 同上 | 根内只有 `catalog.sqlite3` / `-wal` / `-shm`，无其他副作用 |
| **before** 快照 | `snapshot --label before --baseline-seconds 60` | `-shm` 基线 **平坦（0 次前移）**；主库 49,677,344,768 B / mtime 2026-09-08T21:23:21Z；`-wal` 0 B |
| 机制层用例重跑 | wiki 六个 F10 验收文件（见 §2） | **74 passed in 9.31s** |
| **after** 快照 | `snapshot --label after` | 主库**未变**、`-wal` **未变**、`-shm` **未移动** |
| 判定 | `compare --before … --after …` | `persisted_write_evidence=false`，结论 **"no write evidence and no observable open"** |

**这次比 phase A 更干净**：phase A 的"已知限制"是若干既有 wiki 用例在跑套件时会**只读打开**生产库；本次跑的这六个文件**连打开都没有**（`-shm` 在 60 s 平坦基线下前后一致）。

## 2. L01–L12：机制层**覆盖到哪、哪一半必须等第②级**（逐条，不夸）

本次跑的六个文件（`74 passed`）：
`test_r4b01_field_owner_alignment.py`、`test_r4b02_candidate_selection.py`、`test_r4b04_reference_stability.py`、`test_r4b05_metadata_provenance.py`、`test_r4b06_qualification.py`、`test_r4b07_version_contract.py`。
**未跑**（下一批）：`test_r4b03_stable_bytes.py`（L05 的字节硬门就在这里）等。

| L | 机制层（合成夹具） | 第②/③级（真实字节/真实 root/进程观察） |
|---|---|---|
| L01 位置等价四副本 | **覆盖**（候选选择 + 优先级交换，r4b01/r4b02） | 真实四副本与真实 adapter → 需真实 root |
| L02 独立既有根覆盖组 | **不覆盖** | **必须**真实 root + 真实 adapter（G7/G8 第②级） |
| L03 撤首选/移动改名/同 hash | **部分**（r4b04 参考稳定性） | 真实文件搬移/改名 → 需真实字节 |
| L04 第五 root/未知 adapter/deny | **部分**（注册与拒绝在合成 config 上） | 真实第五 root 注册 → 需真实 root |
| L05 打开后替换/TOCTOU/symlink 逃逸 | **部分**（r4b03 未纳入本次批次，**下一批**跑） | 真实并发替换 → 需真实字节 |
| L06 占用/ACL/云占位/损坏/超大 | **部分**（人工注入属机制层） | 真实云占位/真实 ACL → 需真实文件 |
| L07 搬目录重索引/旧 locator | **部分** | 真实修订对同时存在 → 需真实字节 |
| L08 同 source 两 root/矛盾字段 | **覆盖**（r4b05 逐列 provenance + 冲突保留） | 真实两 root 同源 → 需真实 root |
| L09 preview vs 正式输入 | **覆盖**（r4b06 资格标签；`preview` 不可达已登记） | 真实缺 URL 的本地 PDF → 需真实字节 |
| L10 逐能力许可 | **部分** | 原文/sections/summary 的真实产物 → 需真实语料（G7） |
| L11 协议版本/N-1/缺 policy | **覆盖**（r4b07 版本合同 + 外来版本拒绝） | filing/revenue 真实入口调用 → 跨仓 |
| L12 真 query→open 两次 + 旁观 | **不覆盖** | **必须**真实读取 + 进程/文件/DB 观察（B08 的验收核心） |

**读法**：机制层这半边**已经拿到**（合成夹具 + 零副作用证据）；**L02/L12 与各条的真实字节半边仍然被 G8 第②级挡住**——**不把本报告读作"B08 通过"**。

## 3. 副作用证据（不是声明）

- **生产主库**：`49677344768 B`，mtime `2026-09-08T21:23:21.072747Z` —— before/after **一致**，且比授权窗口还早 4 天。
- **`-wal`**：0 字节，前后一致。
- **`-shm`**：before 有 **60 s 平坦基线（0 次前移）**，after 与 before **一致** ⇒ 按 G5 协议（"基线平坦 + 未移动"）**连"发生过打开"都不成立**。
- **隔离根**：只在 `%TEMP%` 下，根内 3 个文件，`build` 幂等。

## 4. **事故与更正（必须记）**：我的守卫第一版没拦住，在生产目录里建了一个目录

- **发生了什么**：`_ensure_isolated()` 第一版把 `REPO` 算高了一层（`HERE.parents[2]` = `assurance/`，正确是 `parents[3]` = 仓库根），于是**三条路径拒绝全部指向不存在的目录、从不触发**。我用"守卫能否拦住生产路径"做验证时，`--root <prod>\.source_catalog\b08-test` **真的建成了**：`<prod>\.source_catalog\b08-test\catalog.sqlite3`（237,568 B，创建于 2026-09-15 23:12:43）。
- **我做了什么**：先核对（目录创建时间 = 刚建、内容仅我 builder 产出的 `catalog.sqlite3`、生产主库仍是 2026-09-08 mtime），确认是**我自己的事故产物**后**用 `Remove-Item -LiteralPath` 精确删除**，并复核 `.source_catalog` 目录列表已恢复原状、主库 mtime 未变。
- **修法**：① 修正路径层级；② 加**结构性**判据（路径中出现 `.source_catalog` 一律拒绝；只允许系统 temp 下的根）；③ 加 `selftest` 子命令——**5 条拒绝必须全部生效，否则该命令非零退出**。这三条都已跑过（5/5 生效，原漏洞路径现在 exit 1 且**不创建任何东西**）。
- **诚实的边界**：这次事故在生产目录里留下过一个**空壳目录 + 一个合成 catalog**（数分钟内删除），**没有**触碰生产主库/`-wal`/真实语料；但它**确实**是一次"未经批准的目录创建"，按纪律**如实登记**，并且是本项目"宣称的保护必须先证明它真的会触发"的又一例。

## 5. 状态与下一步

- 本报告 = **机制层已执行**；B08 的**验收未完成**（L02/L12 与真实字节半边在等 G8 第②级）。
- 下一批（仍在第①级内、不需新授权）：把 `test_r4b03_stable_bytes.py` 等剩余契约文件纳入同一条 before/after 观察，并把"每个 L 项 → 具体用例名"逐行补齐（现在只到文件级）。
- 需要 owner 的第②级授权才能做的：在隔离根下**只读**引用真实文件（L02/L07/L09/L10 的真实半边）。
- 独立复审（按 §11）：本步**尚未**复审；建议把"工具 + 自测 + 本次证据 + 事故登记"一起交给一个只读会话。
