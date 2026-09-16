# B08 **隔离读取第②级**执行报告（G8 第②级：隔离根下**只读**引用真实文件）

> **授权依据**：[owner-directive-2026-09-16.md](owner-directive-2026-09-16.md)（owner「继续做，直到全部完成」→ 2026-09-13 裁定表里标为「另批」的
> G8 第②级在**只读**范围内本批执行）。第①级机制层报告见 [b08-mechanism-report.md](b08-mechanism-report.md)。
> **工具**：`evidence/choose_resolved_real_root.py`、`evidence/b08_isolated_env.py build-level2`、`evidence/b08_level2_run.py`、`evidence/b08_level2_probe.py`
> **原始证据**：`evidence/b08-real-root-choice.json`、`evidence/b08-level2-evidence.json`、`evidence/b08-level2-probe.json`
> **边界（已执行的自我约束）**：**没有**任何生产写入/删除/移动/改名；**没有**复制真实语料到仓库；**没有**打开/查询/哈希生产 catalog 主库；
> **没有**下载任何文件；所有写入只落在 `%TEMP%` 下的隔离根。真实文件只被**读**（读字节 + 读元数据）。

## 1. 实际执行（按顺序，全部可复跑）

| 步骤 | 命令 | 结果 |
|---|---|---|
| 选真实根（只读，基于 A05-2b 输出） | `choose_resolved_real_root.py` | 最小且**有实体**的真实目录：2 文件 / 1 候选 / 1 有实体；目录名 `annual`（len 6），路径 sha256[:16] `465769c177228b0d`（不外泄 CJK 路径） |
| 建第②级隔离根 | `b08_level2_run.py --min-candidates 1 --isolated-root %TEMP%\b08-level2-resolved` | 真实目录登记为 `directory` 类**只读**根（`read_only=true`、`canonical_write_target=null`），真实 sidecar adapter 扫描：`sources 2 / documents 2 / locations 2 / artifacts 0 / evidence_spans 0` |
| 真实字节探针 | `b08_level2_probe.py --isolated-root %TEMP%\b08-level2-resolved` | **4 例全过**（§2）；退出码 0 |
| 零副作用观察 | 同上两步内置 | 真实目录 before/after **逐文件一致**；生产 catalog 三文件**元数据一致**（§4） |

## 2. 核心验收：真实字节读到的 4 例

解析链（先立身份再读，不跳步）：
`query_filing_candidates` → 1 个真实候选 → `SourceResolver.resolve` → **`REUSED_EQUIVALENT` / `one_existing_source_satisfies_semantic_request`**，
`matches=1`、`entity_gate_rejected=0`、trace `2026財務年度報告: matched`、`handle.document_id ==` 该 catalog 行 ✓。
请求身份取自**文档自己的 sidecar**（`company_name`，sha256[:16] `8d264e7eb4150881`，len 6），`mode=latest_as_of`、`as_of_date=2026-12-31`，
`request_id=urn:company-wiki:source-request:sha256:05272e59…`。

| # | 用例 | 期望 | 实测 |
|---|---|---|---|
| 1 | 第一次 `resolve → read_verified_bytes(expected=目录摘要)` | 返回真字节且摘要相符 | **`verified`** / 4,172,424 B / sha256 `e39fbf9c…fb350` / `bytes_source=handle` |
| 2 | 第二次同一路径重开（幂等） | 同上 | **`verified`** / 4,172,424 B / 同一摘要 |
| 3 | 篡改探测：`expected_content_sha256 = 0×64` | **显式失败且不返回字节** | **`unavailable` / `expected_version_mismatch` / 0 B**（`no_bytes_returned=true`） |
| 4 | 真实文件被**另一个 reader** 占用（`rb` 句柄持有）时再读 | 仍返回可核验字节 | **`verified`** / 4,172,424 B / 摘要相符 |

**这两行才是第②级的要点**：
- 第 1/2 例的 `digest_in_real_root_snapshot = true` —— 服务出来的字节摘要等于**独立哈希真实文件**（构建时 before/after 快照）得到的摘要，
  不是"我自己的 catalog 这么声称"。真实文件：PDF 4,172,424 B / sha256 `e39fbf9c…`；sidecar 2,576 B / sha256 `386487167b74b3b3…`。
- 第 3 例证明 B03 的"要么给核验过的字节、要么显式失败"**在真实字节上成立**（0 字节返回）。
- 第 4 例是**读者的**占用共存；**写者**占用（B-DR-07 的写者边界）需要以写方式打开生产文件，**本授权不含**，因此**不声称**覆盖。

## 3. L01–L12：第②级把哪几条推到了哪里（逐条，不夸）

| L | 第①级（机制层） | **第②级（本次）** | 仍然缺什么 |
|---|---|---|---|
| L01 位置等价四副本 | 覆盖（r4b01/r4b02） | 不变 | 真实四副本同时存在（需真实语料布局；本轮只挂 1 个真实根） |
| L02 独立既有根覆盖组 | 不覆盖 | **部分**：真实目录 + 真实 sidecar adapter 在隔离根下建索引，真实候选可解析、可读 | 多真实根**同时**覆盖同一组（需 G7 语料范围扩大） |
| L03 撤首选/移动改名/同 hash | 部分（r4b04） | 不变 | 真实文件的移动/改名 = **生产写**，未授权 ⇒ 第②级也到不了 |
| L04 第五 root/未知 adapter/deny | 部分 | 不变 | 真实第五 root 注册（需 owner 指定的真实根） |
| L05 打开后替换/TOCTOU/symlink 逃逸 | 部分 | **部分（增强）**：真实字节上"内容与请求版本不符"被显式拒绝（0 字节） | 真实**并发替换**（写）+ symlink 逃逸用例（本机 `test_dbx05_symlink_escape_rejected` **skip**，无法造出符号链接） |
| L06 占用/ACL/云占位/损坏/超大 | 部分 | **部分（增强）**：真实文件被另一 reader 持有时仍可核验读取 | 写者占用、真实 ACL、真实云占位、超大文件（均需写权限或本机不可得的环境） |
| L07 搬目录重索引/旧 locator | 部分 | 不变 | 真实"修订对同时存在"（需真实语料 + 可能的写） |
| L08 同 source 两 root/矛盾字段 | 覆盖（r4b05） | 不变 | 真实两 root 同源 |
| L09 preview vs 正式输入 | 覆盖（r4b06） | 不变 | 真实**缺 URL** 的本地 PDF（本样本 sidecar 带 URL） |
| L10 逐能力许可 | 部分 | 不变 | 真实原文/sections/summary 产物：A05-5 实测 **85 个候选里 0 个有 sections 产物** ⇒ 本机语料到不了 |
| L11 协议版本/N-1/缺 policy | 覆盖（r4b07） | 不变 | filing/revenue **真实入口调用**（跨仓，属 B.AR/B10 范围） |
| L12 **真 query→open 两次 + 旁观** | 不覆盖 | **覆盖（真实读取 + 文件/DB 旁观）**：真实 query → resolve → **两次**核验读取 + 真实目录 before/after 一致 + 生产 catalog 元数据一致 | **OS 级进程旁观**（谁打开了什么）本机不可得；G5 已证明 `-shm` 不能归属 ⇒ 该半条**登记为不可得**，不假装覆盖 |

**读法**：第②级把 **L12 的真实读取半边**和 **L02/L05/L06 的"真实字节"半边**推到了授权内可达的位置；
**L03/L07/L10 的真实半边仍不可达**（分别因为：需要生产写、需要真实修订对、本机语料缺 sections 产物）。
**不把本报告读作"B08 通过"**——独立复审（B.VR-b08l2）通过前，B08 状态是"第①+第②级已执行，待复审"。

## 4. 零副作用证据（数字可查，不是声明）

| 观察对象 | before | after | 判定 |
|---|---|---|---|
| 真实目录 2 个文件 | bytes / `mtime_ns` / sha256 逐文件记录 | **完全相同** | `real_root_unchanged = true` |
| 生产主库 `catalog.sqlite3` | 49,677,344,768 B / mtime `2026-09-08T21:23:21.072747Z` | 同 | 未变（该 mtime 比授权窗口早 8 天） |
| `-wal` | 0 B / mtime `2026-09-16T20:44:52.235839Z` | 同 | 未变（0 字节 ⇒ 无待落盘写） |
| `-shm` | 32,768 B / mtime `2026-09-16T20:48:14.252430Z` | 同 | 本次窗口内**未移动**；但按 G5 它在**别的**窗口移动过 ⇒ **不据此归属**任何打开 |
| 隔离写入 | — | 仅 `%TEMP%\b08-level2-resolved\`（`catalog.sqlite3` + 锁文件） | 仓库与生产目录**无新增文件** |

生产 catalog 只被读**元数据**（`stat`），**从未**被打开、查询或哈希（`_production_state()` 的 `note` 字段即该约束）。

## 5. 发现（含我自己的错误）与残留

| # | 发现 | 证据 | 处置 |
|---|---|---|---|
| F1 | **我的前两版探针是 vacuous 的**：① 用编造的实体 `r4b08`；② 用 catalog 里那行 `Unresolved (...)` 实体 —— 两次都得到 `MISSING / 0 matches`，读路径**根本没跑**，却"看起来像跑过了" | 两次运行输出（`resolution_status=MISSING`） | 已修：请求身份改取**文档自身 sidecar** 的 `company_name`。**纪律**：探针必须锚定被测对象的真实身份，否则"没跑"会被读成"通过" —— 与 B05 那次 vacuous 断言同一类错误，已写入 findings |
| F2 | **非 `company_raw` 根下的实体归属**：叶子目录挂成 `directory` 根时，扫描器只按**路径**推实体（`scanner._infer_company` 的名字集合只从 `company_raw` 根收集），于是实体记为 `Unresolved (r4b08_real_sample)` —— 尽管 sidecar 里明明有 `company_name`。resolver 的实体门仍能经 metadata（`ticker`/`security_id`/`company_name`）锚定，所以读取成功 | `entities` 表 1 行 = `Unresolved (...)`；请求改锚 sidecar 后 `entity_gate_rejected=0` 且 matched | **未修**（属产品行为、超出本批授权）。登记为**待 owner 决策**项：若要把 sidecar 的 `company_name` 作为实体回退来源，需独立立项（含用例 + 变异证明 + 复审） |
| F3 | **叶子挂载会把 `.source.json` 当独立文档**：非 focus 分支对每个 supported 文件建 primary ⇒ 真实 1 份 PDF 得到 `sources=2 / documents=2`（PDF + sidecar）。生产 `companies` 根走 focus 分支（routes），不受影响 | `isolated_counts` 与 `locations=2` | **未修**，登记（影响面仅限叶子/外部挂载的计数口径，报告类产物需知道这一点） |
| F4 | **L07/L10 的真实半边第②级也到不了**：需要真实"修订对"与真实 sections 产物；A05-5 实测 85 个候选 **0** 个有 sections 产物 | `a05-readonly-manifest-run.json` A05-5 | 登记为 G7 语料范围残留（不是 B08 可自行解决的） |
| F5 | **写者占用/并发替换/symlink 逃逸不可测**：前两者需以写方式打开生产文件，后者本机造不出符号链接（既有用例 skip） | 授权边界 + `test_dbx05_symlink_escape_rejected` skip | 登记为**能力边界**；报告与 L 表都不得声称覆盖 |

## 6. 复跑（三条命令，路径为 ASCII）

```
python assurance/runs/2026-09-11_r4-phase-b/evidence/choose_resolved_real_root.py
python assurance/runs/2026-09-11_r4-phase-b/evidence/b08_level2_run.py --min-candidates 1 --isolated-root %TEMP%\b08-level2-resolved
python assurance/runs/2026-09-11_r4-phase-b/evidence/b08_level2_probe.py --isolated-root %TEMP%\b08-level2-resolved
```

（第三条会覆盖 `evidence/b08-level2-probe.json`；重跑后 `real_root_unchanged` 与 `production_catalog_unchanged` 必须仍为 `true`，否则**停**。）

## 7. 复审与状态

- 本报告 + 三个脚本 + 两份 JSON 证据 → **独立只读复审**（记录 `reviews/`，编号 B.VR-b08l2）。
- 复审通过前：B08 = **第①级 + 第②级已执行、待复审**；**不**得在 task_plan / checkpoint 里记为"通过"。
- 与 B09/B.AR 的关系：B.AR 用的是**只读 CLI**（不同路径）；两者共享的"零副作用"观察口径一致（真实目录 + 生产 catalog 元数据 before/after）。
