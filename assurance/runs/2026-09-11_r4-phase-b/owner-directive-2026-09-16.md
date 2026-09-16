# Owner 指令记录（2026-09-16：「继续做，直到全部完成」）

> 本文件登记**本轮工作的授权依据**。它不是新的裁定表，而是把 owner 的一句直接指令落到可核对的**范围 / 边界**上，
> 避免以后把「另批」误读成「已批」，或把本指令读成一张新的空白授权。

## 1. 指令原文与上下文

- 原文（本会话，owner 直接输入）：**「继续做，直到全部完成」**。
- 上下文：此前 owner 已对十项裁定表整体回以「**批准**」（[owner-scope-decisions-2026-09-13.md](owner-scope-decisions-2026-09-13.md)），
  其中第 1 项把 G8 分两级、**第②级标注「另批」**；第 2 项（G7 命令 manifest）标注「**本次不批任何命令**」。
  本指令的作用是**把这两处「另批」变成本批执行**——各自边界不变。

## 2. 本指令授权的（= 本轮实际执行的范围）

| # | 事项 | 授权范围 | 同一条内**仍然排除** |
|---|---|---|---|
| 1 | B08 / G8 第②级 | 在**系统 temp** 下的隔离根里，用真实 sidecar adapter **只读引用**真实 filing 文件；读真实字节并核验摘要；前后记录真实目录与生产 catalog 的**元数据**状态 | 任何生产写入/删除/移动/改名；复制真实语料到仓库；打开/查询/哈希生产 catalog 主库 |
| 2 | B09 / B.AR | 按 A05 **只读** command-manifest 执行只读命令并出记录 | manifest 中的写/网络/数据命令：`ensure`/`close-gap`、`scan`/`normalize`/`summarize`/`run`/`worker*`、`identify --refresh`、`derived-audit`、`prune-retired-evidence`/`duplicate-recycle`/`focus-cleanup` |
| 3 | B10（前序门通过后） | 收敛到单一读取链、旧入口只留显式版本 adapter | 未过 B.AR 前**不动工** |

## 3. 与既有记录的衔接（防止误读）

- [owner-scope-decisions-2026-09-13.md](owner-scope-decisions-2026-09-13.md) §23「仍然被门挡住：B08 的真实字节部分（G8 第②级未批）」
  —— **该行自本指令起失效**，且**仅在只读范围内**失效。该文件 §28「未在本次裁定内、也不自行推进的事项」**继续有效**。
- 第 1 项边界原文「**未**授权任何生产 catalog 写入、**未**授权复制/移动真实语料」**继续有效**：
  本轮第②级**没有**写入生产 catalog，**没有**复制或移动任何真实语料，**没有**删除任何东西。
- 第 2 项「命令逐条批」→ 本指令只批 **manifest 中标为只读的那些命令**；其余条目仍留在 `explicitly_excluded` 且**未执行**
  （逐条清单与状态见 `evidence/a05-readonly-manifest-run.json`）。
- 本指令**不**授权：产品代码的行为改动（B05/B07 之外的新改动）、跨仓合同变更、三仓 CI 加门、任何 `--no-verify`。

## 4. 证据落点

| 事项 | 产物 |
|---|---|
| B08 第②级 | `evidence/b08-level2-evidence.json`（构建 + 前后状态）、`evidence/b08-level2-probe.json`（真字节 4 例 + 前后状态）、[b08-level2-report.md](b08-level2-report.md) |
| B.AR | `evidence/a05-readonly-manifest-run.json`（内含 `approval_basis`，引用本指令） |
| 指令本身 | 本文件；`findings.md` 的 R4 段同步登记 |
