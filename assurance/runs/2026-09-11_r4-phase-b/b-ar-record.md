# B.AR（B09）执行记录：按**只读** command-manifest 执行 + 从原文独立重核身份与 hash

> **授权依据**：[owner-directive-2026-09-16.md](owner-directive-2026-09-16.md)（owner「继续做，直到全部完成」→ manifest 中**只读**命令本批执行）。
> **原始证据**：`evidence/a05-readonly-manifest-run.json`（逐命令 argv/退出码/输出字节/输出 sha256 + 每条 stdout 落盘）、
> `evidence/b-ar-identity-hash.json`（从**原始文件**重算的逐文档结论）。
> **工具**：`evidence/run_a05_readonly_manifest.py`（执行器）、`evidence/b_ar_verify_identity_hash.py`（独立重核器）、`evidence/summarise_a05_run.py`。

## 0. 先讲清一处**状态字段不一致**（不掩盖）

manifest 文件自身的状态字段写的是 `NOT APPROVED - awaiting owner confirmation`（那是 2026-09-13 owner 说「命令逐条批」时的状态）。
本次执行的授权**不来自**那个字段，而来自 owner 后来在会话内的直接指令；执行器把两件事都记进证据里：

- `manifest_status_at_run` = `NOT APPROVED - awaiting owner confirmation (gate G4 … gate G7 …)`（**原样保留**，未改 manifest 文件）
- `approval_basis` = `owner in-session instruction 2026-09-16: "继续做，直到全部完成" answering the request to approve the read-only manifest; the writing/network commands in explicitly_excluded stay unapproved and were not run`

**含义**：被批准的是 **manifest 里的只读子集**；写/网络/破坏性条目仍**未获批**且**未执行**（§2 逐条列出）。

## 1. 实际执行的 10 条只读命令（可复跑，输出全量落盘）

| id | 命令 | 退出码 | stdout 字节 | stdout sha256[:16] | 备注 |
|---|---|---|---|---|---|
| A05-1 | `status` | 0 | 206 | `c74996c6a1896819` | 计数：23,530 documents / 43,112 sources / 27,199,666 evidence_spans / 4,984 normalized / 2,969 summary / 2,734 llm_summary / 25,046 active_locations / **missing_locations 6** |
| A05-2 | `query --limit 20` | 0 | 114,913 | `edb92c010925ac41` | 跨 root 的候选页 |
| A05-2b | `query --document-kind annual_report --limit 100` | 0 | 504,834 | `539d78dd7123c1e0` | 候选解析（**执行器追加**，非 manifest 原条目，已在证据里标注原因） |
| A05-3 | `duplicates` | 0 | 107,132 | `bd77a701ae03b587` | 同内容副本组 |
| A05-4 | `evidence-list --document-id <doc> --limit 20` | 0 | 42,446 | `a321586981ae3a06` | **10 次尝试**（前 9 次 exit 1「no evidence spans」），第 10 次成功 |
| A05-4b | `evidence-list --document-id …e39fbf9c… --limit 20` | 0 | 43,585 | `a725350862da3730` | 1 次成功（B08 第②级用的同一份真实年报） |
| A05-5 | `sections-list --document-id <doc>` | **1** | 0 | — | **20 次尝试全部 exit 1**：`no sections artifact for document_id` |
| A05-5b | `sections-list --document-id <doc>` | **1** | 0 | — | **65 次尝试全部 exit 1**；与 A05-5 合计 **85 个候选、0 个有 sections 产物** |
| A06-1 | `size-report` | 0 | 212 | `7f1a322e47cd4e4a` | DB `49,677,344,768 B`、documents 23,530、retired 9,501、pages 12,128,258、freelist 9、`warnings: []` |
| A06-2 | `runtime-policy show` | 0 | 510 | `a0ce50c99bee075d` | `policy_hash c773099b…`、cohort `canary-2026-08-10`、flags：`v2_resolve_active=true`、`v2_bundle_active=false`、`legacy_bridge_enabled=false`、`v2_*_shadow=true`、`v2_persist_assertions=true` |

**退出码 1 不是失败**：A05-5/A05-5b 的 1 是"该文档没有 sections 产物"的**显式**回答（`error_type: fatal, retryable: false`），这正是要记录的事实（§4 F-BAR-5）。

**两处读数口径（避免误读证据）**：
- 输出为**空**的命令（A05-5 / A05-5b）**没有**落盘 side 文件（执行器只写非空输出）——那两条的证据是 `a05-readonly-manifest-run.json` 里各自的 `attempts` 数组（每条 `exit_code` / `stdout_bytes: 0` / `stderr_tail` 原文）。
- `a05-readonly-manifest-run.json` 内联的 `stdout` 字段被**截断到 2,000 字符**；**完整**输出在同目录 `…-<id>-stdout.txt`，其 `stdout_sha256` 已逐条记录 ⇒ 截断不隐藏任何东西，但**要核对全文必须读 side 文件**。

## 2. 明确**未执行**的条目（原样引用证据字段）

`ensure / close-gap`（网络 + staging）、`scan / normalize / summarize / run / worker*`（写 catalog 或起后台）、`identify --refresh`（网络 + 本地写）、
`derived-audit`（经 `reconcile_artifacts` 触碰 catalog）、`prune-retired-evidence / duplicate-recycle / focus-cleanup`（破坏性）、
`install-startup / uninstall-startup / activation apply|rollback / runtime-policy apply`（系统状态）、`export / policy-export / archive-retired-evidence`（写文件）、
以及**上述写命令的任何 `--dry-run`**。**一条都没跑。**

## 3. B.AR 的核心：从**原文**独立重核身份与 hash（不采信 catalog 自己的声明）

方法：把候选按 location 里的**真实 `root_id`** 分组 → 每个 root 最多抽 3 份、总计 ≤20 → **只读**哈希原始文件并与 catalog 的 `content_sha256`/`byte_size` 比对 →
**只读**读同目录 sidecar 重核身份字段 → 只读哈希派生产物并与 artifact 记录比对。生产 catalog 数据库**从未被打开**（输入是已落盘的 CLI stdout）。

| 项 | 结果 |
|---|---|
| 候选（去重后） | 66 份，按 root：`company_raw` **39**、`dayu_portfolio` **19**、`dropbox_stock` **4**、无 location **4** |
| 抽样并**实际哈希** | **6 份**，`digest_matches_catalog = 6/6`、`size_matches_catalog = 6/6`（含一份 **79,925,886 B** 的大年报） |
| 派生产物（normalized/summary） | **10 个**文件被哈希，`artifact digest = 10/10` 相符 |
| sidecar 身份重核 | sidecar 存在 **3** 份：身份字段**逐字段一致 3/3**（每份 2–8 个字段）；其中 2 份 sidecar 自带的 `content_sha256` 也等于磁盘摘要 |
| 实体归属 | 6 份被哈希文档**全部**有已解析实体（`company_raw_path` 或 `path_ticker`） |
| 未哈希（**并说明为什么**） | `dropbox_stock` 3 份**跳过**：读云占位会把它**水合**（真实的本地副作用）；无 location 3 份 → 归类 `no_canonical_location`（不是"文件丢了"） |

**诚实边界**：dropbox_stock 的 4 份候选**因此没有被独立核验**——它们的 catalog 声明在本记录里是**未验证**状态，不当作通过；
`dayu_portfolio` 的文档**没有**逐文档 sidecar（身份来自作品集路径的 ticker），所以那 3 份的身份是"与 catalog 的 `path_ticker` 一致"，而不是"与 sidecar 一致"。

## 4. 发现与残留

| # | 发现 | 证据 | 处置 |
|---|---|---|---|
| F-BAR-1 | **`.pdf.source` 被当作独立文档入库，且没有 location**：3 份这类文档（title 以 `.pdf.source` 结尾）`canonical_path` 为空、`locations` 为空，实体多为 `unresolved:dropbox_stock`；其中 1 份还有 `normalized` 产物（1,157 B） | `b-ar-identity-hash.json` 的 `no_canonical_location` 条目；`status` 的 `missing_locations: 6` | **未修**。与 B08 第②级 F3 **同源**（非 focus 根把每个 supported 文件当 primary，`.source.json` 也在内）。这**不是**本轮新引入，属产品既有行为；登记为**待 owner 决策**项（若清理需写 catalog = 本次未授权） |
| F-BAR-2 | `dayu_portfolio` 抽样 3 份中 **1 份 0 个 artifact**（另 2 份各 2 个）；该文档实体经 `path_ticker` 解析正常 | 同上 | 登记（可能是产物尚未生成/失败后未重跑）；**不改** |
| F-BAR-3 | **我自己的记账 bug**：重核器第一版把"超过 512 MB 上限而跳过"的文件计成 `digest_mismatch`（首跑报 1 例"摘要不符"）。**先复现**（确认该文件是 79,925,886 B 的年报，跳过来自上限而非内容不符）后修正：跳过项不再计入 match/mismatch，上限提高到 512 MB 并重跑 → 该文件被完整哈希且**摘要相符** | 首跑 totals `digest_mismatch: 1` vs 修后 `digest_match: 6` | 已修（工具内），并把"跳过项不得计成不符"写进代码注释 |
| F-BAR-4 | **云占位不可核验**：`dropbox_stock` 的候选在被读取时可能被水合 ⇒ 本记录**不**哈希它们（宁可不核验，也不制造本地副作用） | `skipped_cloud_sync: 3` + 工具里的 marker 检查 | 能力边界；若 owner 要核验，需要一条"只读且不水合"的手段（本机不可得） |
| F-BAR-5 | **sections 层覆盖为 0**：85 个真实候选**全部**没有 sections 产物（20 + 65 次 `sections-list` 全 exit 1，`error_type=fatal`） | `a05-readonly-manifest-run.json` 里 A05-5 / A05-5b 的 `attempts` 数组（输出为空 ⇒ 无 side 文件，见 §1 口径） | 这不是缺陷、是**事实**：任何依赖 sections 的验收（含 B08 L10）在本机语料上**到不了**；已在 B08 第②级报告的 F4 引用 |
| F-BAR-6 | `status` 报 `missing_locations: 6`（有文档但无 location），与 F-BAR-1 同类 | A05-1 stdout | 登记（数量小、性质同 F-BAR-1） |

## 5. B09/B.AR 验收状态（对照 [test-acceptance-map.md](test-acceptance-map.md)）

验收原文要求："真实四 root + 第五 root 端到端；独立 AR 从原文重新核身份与 hash；仅隔离副本变化，不改用户原文件"。

| 要求 | 本次到哪一步 | 还缺什么 |
|---|---|---|
| 独立 AR 从**原文**重核**身份 + hash** | **达成**（有界样本）：6/6 摘要相符、10/10 派生产物相符、3/3 sidecar 身份一致；未采信 catalog 声明 | 样本扩大（本轮 6 份；上限是执行预算而非能力） |
| **不改用户原文件** | **达成**：全部动作只读；未哈希云占位；未执行任何写/网络命令 | — |
| 真实**四 root** | **部分**：4 个真实 root 在 catalog 层各有真实候选（39/19/4/4），读取与核验在 `company_raw`+`dayu_portfolio` 完成 | `dropbox_stock` 因云占位未核验（F-BAR-4） |
| **第五 root** | **未做**：本轮只按 manifest 的只读命令读取既有 catalog，**未注册任何新 root**（注册 = 写 catalog） | 需 owner 指定第五 root 的路径/类别 |
| 端到端（filing/revenue 真实入口） | **未做**（属 L11/B10 范围） | 跨仓入口调用 |

**结论**：B.AR 的"独立性"半边（从原文重核）**已交付**；"四 root + 第五 root 端到端"半边**只到部分**，缺的两项都需要本轮**未获授权**的动作（写 catalog 注册第五 root / 跨仓入口）。

## 6. 复跑（只读；路径为 ASCII）

```
python assurance/runs/2026-09-11_r4-phase-b/evidence/run_a05_readonly_manifest.py --label round1
python assurance/runs/2026-09-11_r4-phase-b/evidence/b_ar_verify_identity_hash.py --per-root 3 --max-docs 20
```

（第一条会覆盖 `evidence/a05-readonly-manifest-run.json` 与逐命令 stdout；第二条会覆盖 `evidence/b-ar-identity-hash.json`。
重跑后必须仍是：写命令一条未跑、`digest_match` 无缺口；否则**停**并记录。）

## 7. 复审与状态

- 本记录 + 两个工具 + 两份 JSON → **独立只读复审**（编号 B.VR-bar，记录落在 `reviews/`）。
- 复审通过前：B09/B.AR = **部分执行、待复审**；**不**得记为"通过"，也不得据此宣称"四 root 端到端已完成"。
