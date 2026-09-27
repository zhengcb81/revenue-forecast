# evidence_erratum_20260923.md — D1b 勘误：登记为 evidence 的 `before/production_anchors.txt` 从未产出

- by：BOOKKEEP-REPAIR / a20260923-01（父派单 #15；AUDIT-DESIGN **D1b**〔现最高项〕、AUDIT-DESIGN 追补 A4、登记册 §77）
- 对象：`execution_runs/B1-I08C-product-fixes/a20260921-01/commands.json` 的 **B1-c0** 条目
- 形态：**追加式勘误文件**（本文件新建）；`commands.json` 原行**一字不改**。
- **铁律（明记）**：**不得创建 `production_anchors.txt`**——不事后补件冒充当时证据。本 pass **未**创建该文件（今后也不得）。

## 1. 声明（逐条）

1. **登记原文（留痕引用）**：
   - `commands.json:35`：`"evidence": ["before/production_anchors.json", "before/production_anchors.txt"]`
   - `commands.json:27`（argv）：`"<ATTEMPT>/before/production_anchors.txt"`（B1-c0 的声明输出位）
   - `commands.json:38`（条目自注，近自陈）：「the anchors were first captured by an inline hashing step whose raw output is before/production_anchors.json; B1-c0 records the reproducible scripted equivalent, which produces the same table plus the git-status block.」
2. **勘误事实**：`before/production_anchors.txt` **未产出（never produced）**——被登记为 evidence 的 `.txt` 交付件自始不存在；**登记时点即缺**（非其后丢失）。`.json` 等价物**存在**：`before/production_anchors.json`（2782 B，sha256 `01e7ab52c637f8a030de0e7ddc2eda6b36f9f130d2317446851b148af236d7a0`，2026-09-23 实测）。
3. **性质**：evidence 登记**过度申报**（登记 2 件、实产 1 件）——违反 `review_and_handoff.md:21-31` 交付最小目录精神（原始输出须按登记留存）、`:33`「不能仅交文件名/hash」。**非捏造**：所登记的 `.json` 真实存在，条目自注已近乎自陈该 `.txt` 系脚本化等价物；但登记面未标注「未产出」，构成 D1b。

## 2. 实测搜证（本 pass 自行复核，方法与边界如实）

| # | 方法 | 范围 | 结果 |
|---|---|---|---|
| 1 | `before/` 目录全量列名+字节数 | `B1-I08C-product-fixes/a20260921-01/before/`（22 件） | `production_anchors.json`（2782 B）在；**`production_anchors.txt` 不在** |
| 2 | `Get-ChildItem -Filter production_anchors.txt` 递归检索 | ①`execution_runs/B1-I08C-product-fixes/` 全树 ②plan 根目录文件 ③`outward_requests/` ④`execution_runs/` 顶层 | **0 hits** |
| 3 | 独立先证（引用） | AUDIT-DESIGN 报告 v2 **D1b**：「`production_anchors.txt` 在**整个计划树与 RF 仓树均不存在**（其 `.json` 兄弟件存在）」 | 独立审查员全树检索同结论 |
| 4 | 全树 `production_anchors.txt` glob（本 pass 尝试） | 计划树全域 | **方法边界披露**：该 glob/递归检索在超大树（iso/venv 等）上超时，未完成全域枚举——故本条以方法 1–3 收束；AUDIT-DESIGN 的全树检索（方法 3）为全域先证 |

⇒ `production_anchors.txt`：**未产出、登记时点即缺、全树无留存位**（与 D1 的「字节有留存位」情形**不同类**——本条不可复现、不可补）。

## 3. 处置（按 AUDIT-DESIGN 处置方向 + 父铁律）

- 该 evidence 条目**以本勘误改述为**：`before/production_anchors.txt` = **未产出（仅 .json 等价物存在）**；原登记行保留原值（原值留痕），本文件为行级更正载体。
- **不**事后补文件、**不**改写 `commands.json`、**不**冒充当时证据。
- 0 字节写入 `commands.json`、`before/` 任何既有件、任何 reviewer 载体、任何产品树、任何 git 状态。
- 登记行（供父折入 `REMEDIATION_REGISTER.md`）：**D1b 收口（勘误式）**——`production_anchors.txt` 未产出/登记时点即缺/不补件（`evidence_erratum_20260923.md`，实测搜证 3+1 方法在案）。
