# owner 口径（2026-09-18）：R3 的落地方式与第五根的形状

> 这份文件是 R3 的**授权依据落盘物**。此前它只存在于会话里（harness 的 `authorisation_basis`
> 与 [evidence/b-ar-fifth-root-isolated.md](evidence/b-ar-fifth-root-isolated.md) §0），
> 触发独立复审 `B.VR-r3` 的 **F-R3-02（P2）**：*"increment 的授权只写在被它授权的产物里"*。
> 现在收口在这里。

## 1. 我问的两个问题（原文）

背景：[b-ar-record.md](b-ar-record.md) §5 的「第五 root」一行当时是 **未做**，原因是
"注册 = 写 catalog"，而原目标禁止「生产 catalog 写入」。我在会话里写明：注册一个 root 必须
（a）改配置 **且**（b）跑一次 scan；scan 的注册动作只会写
`company-wiki/.source_catalog/catalog.sqlite3`（49,677,344,768 B），并列出我需要 owner 给的三样：
真实目录路径、`kind`、以及**写哪里（生产 or 隔离副本）**。

1. **「第五 root 的注册，写进哪里？」**
   - A. **隔离副本**（我推荐）：用临时 `catalog_dir` 注册并跑通 `query → open → consumer`，生产
     46.3 GiB 库零改动。
   - B. 生产 catalog：真扫一次并写 `roots` 行，需明确批准一次生产写入。
   - C. 先不做 R3。
2. **「第五 root 指向什么？」**
   - 用配置里已声明的 `future_lake` 占位（我按 yaml 的定义建目录并注册，
     `kind=directory` + `sidecar_filing_v1`、只读）。
   - 由 owner 另指定一个真实目录。
   - 先不定。

## 2. owner 的选择（原文答案）

| 问题 | 选择 |
|---|---|
| 写哪里 | **A. 隔离副本** |
| 指向什么 | **用配置里已声明的 `future_lake` 占位** |

## 3. 我据选择所做的**一处更正**（必须留痕）

第 2 个问题的选项**是我自己写坏的**：`future_lake` **不是**待用的空位，它**已经是第四根**
（生产 config 的四条 root 之一；`company-wiki/future_lake/README.md:1` 写的是
"ZR-409 **fourth-root** fixture (EX-08)"）。把它当"第五根"会重演既有审计已经否掉的口径
（`company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/filing-audit.md:49`：
"future_lake 为空占位 + 合成测试不等于真实第四 root"）。

因此落地方式是：**沿用 `future_lake` 的形状**（`kind: directory` + 已注册的 `sidecar_filing_v1`
适配器 + `read_only: true` + `reusable_for_filing: true`），但用**新 id `r4_fifth_root`**、指向
隔离工作根下的真样例目录。这条更正只影响**隔离副本内的 fixture 命名**，不影响 owner 的实际选择
（隔离 + 用那个形状）；已在 [evidence/b-ar-fifth-root-isolated.md](evidence/b-ar-fifth-root-isolated.md)
§0 写明。

## 4. 这份口径**授权**什么、**不**授权什么

- **授权**：在 `%TEMP%` 下的隔离项目根里，用临时 `catalog_dir` 注册一个新 root 并做最小读取
  （`query → open → consumer`），含负向腿（未知适配器 / deny / 未注册 root id）。
- **不授权**（原样保留）：
  - **任何生产 catalog 写入**（`company-wiki/.source_catalog/catalog.sqlite3` 及 `-wal`/`-shm`）；
  - 任何产品文件写入/删除、任何未批准的写命令；
  - 把生产四根的数据复制进隔离副本（46.3 GiB，会同时吃掉本机 63 GB 可用空间的一大半）——
    因此"生产四根 + 第五根**共存**"这一层**仍未验证**；
  - `dropbox_stock` 云目录的字节核验（读它可能**水合**占位文件）——仍待 owner 表态（R5）；
  - 跨仓（filing-fetch / revenue-forecast 真实入口）端到端调用——仍待 owner 确认命令（R4）。

## 5. 时间与复跑

- 选择时间：**2026-09-18**（本机时钟；会话内发生）。此前 harness 记录里写的 `2026-09-17` 是
  **我写错了一天**，已更正为 `2026-09-18`。
- 复跑：`evidence/run_bar_fifth_root_isolated.py`（主跑 / `--mutations` / `--verify`），
  命令与输出见 [evidence/b-ar-fifth-root-isolated.md](evidence/b-ar-fifth-root-isolated.md) §1。
