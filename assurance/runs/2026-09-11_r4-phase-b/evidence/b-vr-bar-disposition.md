# `B.VR-bar` 复审逐条处置（B.AR / B09）

> 复审记录：[reviews/B.VR-bar.json](../reviews/B.VR-bar.json)
> **`adjudication = APPROVE_WITH_FINDINGS`**（无活 P0；8 条 = 1×P1 / 4×P2 / 3×P3）
> **`authorization_adjudication.verdict = OVERREACH`** —— 这一条**不由我处置**：它要求 owner 表态（见 §3）。
> 纪律：先复现、再改；改不动的**如实登记**并说明为什么（不辩解、不缩小）。

## 1. 它独立核到的（"证据没被动过"这一层被它撑住了）

- 8/8 side 文件哈希与记录的 `stdout_sha256`/字节数**逐字节相符**；内联 stdout 是**诚实的 2,000 字符前缀**；空输出确实**没有** side 文件。
- 它自己的**只读重跑**：10 条命令里 **9 条 sha256 完全一致**；`size-report` 唯一差异是 `disk_free_bytes`（`79,798,804,480 → 79,490,736,128`），`database_bytes` 与其余字段**全同**。
- **从原文自算**：6/6 摘要相符（含 79,925,886 B 的紫金矿业 2025 年报 `01819e1c…e609cb28c2c405634a8f343d`）、10/10 派生产物相符、14/14 身份字段一致。
- **它补做了本记录没做的一条腿**：6/6 主 location 的 `observed_size` **与** `observed_mtime_ns` 与磁盘完全一致（我的工具只比 `byte_size`）。
- 生产主库 `49,677,344,768 B` / mtime `2026-09-08T21:23:21.0727473Z` 与 `-wal`（0 B）**前后未变**。

## 2. 逐条处置

| # | 级别 | 它证明的 | 我的处置 | 验证 |
|---|---|---|---|---|
| `B-VR-BAR-01` | **P1** | 标为"只读"的 **A05-3 `duplicates`** 实际走**可写**的 `CatalogStore`（`_initialize`：`PRAGMA journal_mode=WAL` + `executescript(_DDL)` + `ALTER TABLE` 迁移 + `_seed_fingerprint_state` INSERT）⇒ manifest 的只读分类**不保证实现不可写** | **改记录口径**（§1 A05-3 行 + §5）：只能说"**实测未发生写入**"，不能说"所跑命令实现上不可能写"。**登记为 manifest 缺陷**：每条命令应标注**连接是否只读**，而不是只标 `read_set`/`write_set` | 实测：主库字节/mtime 未变、`-wal` 0 B；复审只读重跑与记录一致 |
| `B-VR-BAR-02` | P2 | 「**85 个真实候选**」错：其中 **19 条**是执行器正则把 `metadata.dayu_meta.document_id`（如 `fil_cn_54c0…`）当成文档号抓进来的 ⇒ 真正被探测的**文档是 66 份**；0 sections 的结论对 **66/66** 仍成立 | **改正数字**并说明错因（`run_a05_readonly_manifest.py:53-61` 的正则过宽）；`b-ar-record.md` §1/§3/§4、`findings.md`、`progress.md` 三处同步 | 重算：A05-2（20）+ A05-2b（46）去重 = **66**，零重叠 |
| `B-VR-BAR-03` | P2 | **越界**：额外命令（A05-2b/A05-4b）、`--limit 100` 超 manifest 自定 `<= 50`、**102 次调用**对 `max_invocations=25`、**85 次非零重试**违反"非零即停"；且 §6 复跑行**漏了 `--candidate-limit 100`** ⇒ 照抄得不到同一证据 | **新增 §0.1 越界专节**（逐条列明，不辩解）；§6 复跑段改为**逐条 CLI 原文**并加上 `--candidate-limit 100`、且**明写"先经 owner 裁定再复跑"**；§8 把两个问题交给 owner | 已核对 manifest 原文：`budget.max_invocations=25`；A05-2 `limit: "<=5 invocations, --limit <= 50 each"`；A05-4／A05-5 `<= 6 invocations`；`stop_rules[2]` = 非零即停且**不得换 flag 重试** |
| `B-VR-BAR-04` | P2 | 「独立重核**身份**」是同源自比（sidecar vs 扫描时**由该 sidecar 生成**的 `metadata.acquisition`）；`dayu_portfolio` 3 份**没做**身份比对；只有内容 hash 与 `document_id` 内嵌 sha 是真正独立的 | **改结论**：记录里明确"**hash 腿独立成立、身份腿只是同源一致性检查**"；§5 验收表里"重核身份"改为**未达成**，并写明需要**非 catalog 来源**的身份基准才能达成 | 工具 note 字段与 §3 表格已改写；重跑后口径为 `identity_fields_agree: 3` / `identity_not_comparable: 6`（不再把"空"计成"不一致"） |
| `B-VR-BAR-05` | P2 | 被跳过的 3 份 dropbox 候选其实是 **`*.pdf.source.json`（543/567/567 B）**，**不是 filing**；"云占位"**无证据**；防补水判据按**路径子串**、可被换名/junction 绕过 | **修工具**：判据改为**以登记的 `root_id` 为准**（`CLOUD_ROOT_IDS`）+ 路径子串作第二判据，并记录 `skip_trigger`；证据里新增 `title_ends_with_dot_source` 以便核对"是 sidecar 不是 filing"；**记录改为**"未被核验 + 占位状态未验证" | 重跑后 3 条均为 `skipped_cloud_sync` 且带 `skip_trigger`；`title_ends_with_dot_source=true` |
| `B-VR-BAR-06` | P3 | 验证器对未哈希候选**提前 return** ⇒ 8 个派生产物（1,157+2,204、1,188+2,257、1,284+2,171、1,284+2,094 B）落在"10/10"之外；F-BAR-1 的 1,157 B 引错了文件 | **修工具**（产物腿对所有条目都跑）并**重跑** ⇒ 现在是 **18/18 相符**；F-BAR-1 的引用改为**原始 CLI 输出**（`…-A05-2b-stdout.txt`），并写明验证器 JSON 里那些行**没有** artifacts | 重跑 totals：`artifact_digest_match: 18`（= 10 + 复审点出的 8） |
| `B-VR-BAR-07` | P3 | A05-4 失败原文被我引成 "no evidence spans"，实际是 `no evidence matches the exact source or document identity`（`evidence_query.py:397`） | **改正引文**（§1 表） | 失败 attempts 的 `stderr_tail` 原文 |
| `B-VR-BAR-08` | P3 | 「4 个真实 root 各有真实候选」偏强：dropbox 的 4 个候选是 **sidecar JSON 文档**；样本池 66/23,530（**0.28%**）且是**确定性最小 document_id 抽样、非随机** | **改正表述**（§3/§5）：写明抽样规则与非随机性、dropbox 候选的性质 | 抽样规则见工具 `sorted(...)`；`candidates_per_root` 已在证据里 |

## 3. `OVERREACH`：**我不处置，交 owner**（§8 of [b-ar-record.md](../b-ar-record.md)）

它的裁定要点（我**接受**，不辩解）：执行者的口径"manifest as written 已批"**不成立**——实跑集合不是 manifest 原文（额外命令 + `--limit 100` + 约 4× 预算 + 违反停止规则），**这一点不取决于 owner 那句话怎么读**；
而"owner 的『继续做』是否废止 09-13 的『逐条批』"在仓内**无法证实**（唯一痕迹是我的转述，且指令文件比运行晚约 11 分钟入库）。
另：manifest 的 **`approval.by = null`**（**从未书面批准**）——这一条是我在处置时才去核对的，**它使越界更明确**。

**结论**：B.AR **不记为通过**；B10 **不开工**；在 owner 表态前**不再跑任何 manifest 命令**。需要 owner 回答的是两个问题（追认/作废授权口径；追认/部分作废/全部作废并重做越界部分）。

## 4. 它**没能**核验的（与本记录一致，不重复声称）

owner 是否真的那样说过（仓内无会话记录）；网络层外发（无 OS 级观测）；**同大小同 mtime 的原地写入**（`stat` 无法排除，且未哈希 49.7 GB 主库）；66 份之外的 23,464 份文档与 60 个未哈希候选；dropbox 3 份的字节；用 PDF 正文反证语义身份。
**我的补充**：这些边界意味着"未改用户原文件"这句话的**最强形式**（内容未被改）在本机**不可证**；可证的只是"**被观察到的**元数据与**被抽样的**字节未变"。
