# I-09-A review — 实现者自述 + 独立验收待办

> **本文件由实现者撰写，不构成验收结论。** 本卡是设计/契约卡：实现者只能声明「协议提案已冻结、现状基线已实测、正反例已逐条跑过」。是否接受由**独立 transaction reviewer** 判定。
>
> 实现者**未自签**任何 accepted / passed 标签。

- card: I-09-A（父项 I-09）
- attempt: `a20260919-01`
- 状态: `review_pending`
- 生产仓改动: **0**
- **独立对抗式复核已回**：verdict = `changes_required`（窄幅，仅文档/勘误层；**证据层不需重跑**），并**背书** `C-01…C-12`、`I09-E01…E10`、`F-IDEM`（独立重写算法复现 6 个值）、`E31` 判定点与 c02/c03/c05/c06/c07/c08/c11/c12 的实测结论。逐条处置见 **`errata.md`**。本文件已按勘误更正；**勘误不构成重新验收**，reviewer 段仍留空。

---

## 1. 我实际做了什么（可核对清单）

| 动作 | 产物 | 证据 |
|---|---|---|
| 读 START_HERE / dispatch / review_and_handoff / common_filing_cards / card_I-09-A / filing_cards 的 I-08-A/B/C 三段 | 本文件、`oracle.md` §1 | `before/baseline_hashes.txt` 前 11 行 |
| 读 I-08-A 全部交付物（含 §2.5 错误码表、§6 `classify()`、§7 顺序、§8 OPEN-D1..D7） | `decision.md` §8 | `before/baseline_hashes.txt`（I-08-A 6 个文件的 sha256） |
| 读 I-06-A 的 `decision.md`（OPEN-2 幂等键先例） | `decision.md` §1、§3.3 | `before/baseline_hashes.txt` |
| 重定位并重算 7 个卡锚点 hash（**不用卡的行号做门**） | 3/3 文件 hash 与卡正文**逐字一致** | `binding.json.card_anchor_verification` |
| 建隔离 venv（不装任何第三方包） | `iso/venv` | `commands.json` I09A-c1 |
| 复制产品 `scripts/` 到 `iso/rf/scripts` 并逐文件比对 | 43/43 .py SAME，0 DIFF | `before/baseline_hashes.txt` |
| **先**冻结 `oracle.md`（含 12 个 case 的期望、C-01…C-12、F-IDEM） | `oracle.md` | `binding.json.oracle_freeze_disclosure` |
| **后**写并跑 `iso/probe_commit.py`（12 case + 身份反例 + 并发） | `after/probe_commit.stdout.txt`、`after/probe_commit_report.json` | `commands.json` I09A-c4 |
| 用**另一条通道**（PowerShell + .NET SHA256）独立复算生产 registry 的 60 行 | 60/57/3/31/21/6、链问题 0 | `commands.json` I09A-c7 |
| 追加登记与冻结期望的偏差（**不修改冻结文本**） | `oracle_addendum.md` | 同上 |
| 真实 ACL 拒绝造 registry 故障并复原 | `after/probe_registry_fault.stdout.txt` | `commands.json` I09A-c5 |
| 稳定性复跑 + 不变量比对 | 12/12 case 不变量一致，身份契约 5/5 一致 | `after/probe_commit.run2.stdout.txt`、比对输出见本文件 §4 |
| 三仓 git 状态前后捕获 | `before/git_status_*.txt`、`after/git_status_*.txt` | `commands.json` I09A-c8 |
| 生产锚点前后重算 | 8/8 SAME，0 CHANGED | 本文件 §4 |

**没有做**（范围外或禁止）：没有改任何产品代码/配置/生产 registry；没有跑真实 provider；没有联网；没有 git add/commit/restore/stash；没有写 `PLAN/reviews`；没有执行任何产品命令（卡原文：本卡无产品执行命令）。

---

## 2. 三资格分别陈述（不互相继承）

| 资格 | 现状 | 依据 |
|---|---|---|
| **① 设计/契约资格**（本卡的唯一目标） | **提案已冻结，待独立裁定**。C-01…C-12 + `I09-E01…E10` 在 `oracle.md` §5（先于运行写入）；现状基线 N-1…N-14 已实测 | `oracle.md`、`decision.md` §1–§7 |
| **② 实现资格** | **未获得，也未尝试**。本卡不实施产品（执行门原文），`changed_paths = []` | `handoff.json.changed_paths` |
| **③ 事务/故障资格** | **未获得**。故障点表 F1–F12 是**冻结的预期**，其中 F3/F4/F9 只做到「现状行为已实测」，F6/F7/F8/F10/F11 **未实测**（I-09-C 范围） | `decision.md` §7 的 E 栏 |
| ★ 附带：**签名/信任** | **未获得，也不属本卡**（I-08-A/B/C）；本卡只消费其契约 | `decision.md` §8 |

**三者互不继承**：设计提案被接受**不**等于产品已实现；现状缺陷被实测**不**等于协议正确。

---

## 3. 我认为已被证据支持、且应被 reviewer 攻击的结论

1. **现状是「先提交、后产物」，与协议要求的「成员齐备才提交」相反。**
   - c02：输出写失败（真实 WinError 5）→ producer rc=2，而消费者仍看到 1 个 `validation_status=validated` 的 forecast 行、`is_registered=true`、磁盘上**零个真实成员文件**。
   - c03：JSON 已落盘 94614 B、Markdown 写失败 → 消费者仍看到完整提交资格 → **半包可见**。
   - 这与历史反例 `reviews/revenue/logs/publication_probe.stdout.txt`（`registry_entries_added: 1, output_exists: false`，CLI rc=2）**同形**，本卡在隔离环境**复现**了它。
2. **registry 行没有任何身份/提交状态字段**：60 行里 57 行 `artifact_id=null`，无 `publication_id`/`members`/`commit_state`。因此「已提交」只能由「行存在」近似表达 → 正是 P-D1 的失败形状。
3. **`is_registered(anchor)` 不是 commit 资格**：它只看 anchor 是否出现过；c11 证明库调用者可以落一行「anchor 属请求 A、载荷属请求 B」的记录且 rc=0。
4. **请求身份在当前**正式 CLI **路径上确实参与 anchor**（N-9/N-14：仅 `as_of_date` 不同 → `input_sha256` 不同；`verify_input_binding` 强制绑定），**但**该不变量没有任何持久化表达（结论 2/3），所以 I-06-A OPEN-2 类缺陷在本系统的形态是「已提交的行无法自证是哪次请求」。
5. **提案的身份函数满足必答反例**：`as_of_date` 仅差一天 → `request_sha256`、`publication_id`、`idempotency_key` **三者全不同**，且 `publication_id` 可被第二次独立重算复现。
6. **registry 不可达时是 fail-closed**（c04b：真实 ACL 拒绝 → rc=2、无输出、0 行）。
7. **`_append` 的读链尾与 append 之间没有锁**（源码事实 F-1）；两次并发 burst 都成功**不构成**安全性证据。

---

## 4. 数字与不变量（全部可复算）

| 项 | 值 | 来源 |
|---|---|---|
| 生产 registry sha256（前=后） | `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91` | `before/baseline_hashes.txt`、`after/probe_commit_report.json` |
| 生产 registry 行数 / 有 validation_status / 无 | 60 / 57 / 3 | PowerShell 独立通道 |
| forecast / snapshot | 57 / 3 | 同上 |
| 非空 artifact_id / null | **3 / 57**（3 行非空全为 `snapshot`、**同值** `47a46003…`；去重值数=1。原写 1/57 是把去重计数当行数 → 勘误 `errata.md` E-1） | 同上 |
| 链问题数 / 末行 line_sha256 | 0 / `61fbec623b2a641b9b69555c3eae4e5b64b63697a05877ed95510d73d87ce67f` | 同上 |
| `(input,result,engine,schema,type)` 组数 / >1 的组 / 最大重数 | 31 / 21 / 6 | 同上 |
| 稳定性复跑（run1 vs run2，12 case 不变量行） | **12/12 一致**；身份契约 5 项全一致 —— **限定**：该 5/5 是对 **harness 字面量载荷**（`package_target="out.json"`、`members=["out.json"]`，硬编码）的自洽性检验，`package_target`/`members` **尚未与生产事实绑定**（OPEN-I09A-1/-3）；**不得**据此宣称可用于生产落地（复核 E-7） | `after/probe_commit.run2.stdout.txt` |
| 生产锚点前后重算 | 8/8 SAME（含 registry） | `commands.json` 与本节 |
| 隔离副本 vs 生产 `.py` | 43/43 SAME | 同上 |
| 复跑后并发两 worker rc | run1 `[0,0]`、run2 `[0,0]`（**仍未构成锁的证明**） | 比对输出 |
| revenue-forecast `git status` 行数（**两个保留的快照文件**，勘误 E-6 统一口径） | before 快照 = **148 行 / 142 真实条目**；after 快照（重抓于本 attempt 期间）= **132 行 / 126 真实条目**；**首次 after 快照（124 行）未保留，明确排除、不作证据**。**注**：该树此后仍在被并发卡改动（本勘误阶段收尾时再测已到 **270 行**），故上述两值只是**快照时点**的读数，不是"最终状态" | `before/git_status_before.txt`、`after/git_status_after.txt` |
| company-wiki / filing-fetch 前后 | 0 差异 / 0 差异 | `before/`、`after/` |

---

## 5. 与冻结期望的偏差（诚实登记，不修冻结文本）

完整逐条见 `oracle_addendum.md`。摘要：

| case | 冻结原文（`oracle.md`） | 实测 | 判定 |
|---|---|---|---|
| c02 | 「`out.json` **不存在**；registry **1 行**；`is_registered=true`；`commit_qualified=1`」 | `out.json` **路径上是注入的目录**；registry **1 行**；`is_registered=true`；`commit_qualified=1` | ⚠️ **仅一处措辞错**（「路径上不存在文件」写成「路径不存在」）。**行数与资格判据冻结原文即写对**，与实测一致；原「期望写反」自曝**已撤回**（复核 E-2） |
| c03 | 「`out.json` 存在；`report.md` **不存在**；1 行」 | `out.json` 存在（94614 B）；`report.md` **路径上是目录**；1 行；`is_registered=true` | ⚠️ 同上，仅措辞 |
| c04 | 「rc=2、registry 非文件、无输出」 | **rc=0、append 成功** | ❌ **冻结期望不成立**：`registry_file()` 把目录 env 当**目录根**，真 registry 变成嵌套同名文件并写入成功 → 新发现的 **fail-open**（N-13） |
| c04b（新增） | 原 c04 的判据 | 真实 ACL 拒绝 → rc=2、无输出、0 行 | ✅ 判据成立，注入手段修正 |
| 其余 9 个 | — | — | ✅ 一致 |

**索引勘误（复核 E-1/E-2）**：本表原写「c02 = registry 0 行 / `is_registered=false`」，与 `oracle.md:76` **冻结原文不符**，属对冻结文本的**反向不实陈述**，已更正并撤回。唯一 false pass 出现在 `oracle_addendum.md` 的 registry 统计格（非空 `artifact_id`），已撤回（`errata.md` E-1）。

**harness 缺陷保留**：`after/probe_commit.attempt1_argv_bug.*`（第 1 次运行忘传位置参数，c01–c10 全无效）、`probe_registry_fault` 第 1 次运行的 `import json`/解码/ACL 复原缺陷（ACL 已手工复原并复核）。**没有**为了好看而重写这些证据。

---

## 6. 两处必须由 reviewer/owner 处理的冲突（我停下记录，不自行改索引文档）

### C-A（阻塞下游）：依赖卡的验收状态与派单陈述不一致

派单陈述「I-00-A、I-00-B、I-08-A 均已 accepted_scoped」。**实测其交付物并非如此**：

| 卡 | `handoff.json.status` | `handoff.json.reviewer_status` | 其他文件里的结论 |
|---|---|---|---|
| I-00-A | `review_pending` | `accepted_scoped_pending_errata_confirm` | `review.md` 的结论是 **changes_required**（1 个阻断项），`errata_fix_note.md` 记录了重拍修复；但**没有**修复后的独立复核记录 |
| I-00-B | `review_pending` | `pending` | **无**任何独立结论记录 |
| I-08-A | `review_pending` | `pending` | `decision.md` §11 自述「独立验证结论…尚未由独立 reviewer 出具」 |

**我没有改任何索引文档，也没有把这三张卡当作已 accepted。** 影响：I-09-A 的**设计**可以继续（它只是消费契约名），但 **I-09-B 不得在 I-08-A 未被独立接受前把本协议与签名载荷一起落地**。登记为 OPEN-I09A-5。

### C-B（不阻塞）：`PLAN/reviews` 的 mtime 与派单陈述不一致

派单要求「`reviews` 只读，mtime 必须保持 2026-09-19 10:05」。**实测目录 mtime = 2026-09-19 09:14:20**（子目录 `revenue` = 2026-09-19 09:25:25）。我**只读**了该目录，未写入。该陈述与事实不符，登记为观察项（不阻塞本卡，但说明派单里的环境事实不可当作已核验）。

### C-C（不阻塞，但影响证据解释）：同一棵树里有并发卡在运行

本 attempt 期间 `revenue-forecast` 的 `git status --porcelain` 行数从 148（before 快照）变为 124（**首次 after 快照，未保留 ⇒ 该数字不作证据**）、再到 132（当时保留的 after 快照；**该文件其后在勘误轮被就地重抓为 270 行、旧内容不可复验**，见 `errata.md` E-11），且差异集中在 **I-04-C** 与若干 **M09–M28 / I-11-A / _m2931_build** 的 attempt 目录 —— **本卡从未触碰这些路径**。同期 `company-wiki`、`filing-fetch` 前后零差异。

因此**「无改动」不能靠 git 状态快照证明**。本卡改用**更强的证据**：

- 生产锚点前后重算 **8/8 SAME**（含生产 registry 的 sha256）；
- 隔离副本与生产 `scripts/` 逐文件比对 **43/43 .py SAME**；
- 所有 case 的写入目标都在 `<attempt>\iso\scratch\` 之下。

`binding.json.three_repos.revenue-forecast.concurrent_activity_caveat` 已登记该事实。**建议 owner 对同一棵树的并发卡做互斥/约定**（这是跨卡的流程问题，不是本卡可修的）。

---

## 7. reviewer 必须自己做的事（第一轮已完成；下表保留复验路径）

> **状态更新**：下列 1–7 项已由独立对抗式复核完成（verdict `changes_required`，仅文档层），第 8 项为约束。本节保留原文以便**第二轮定点复核**复用；第二轮只需核 §`errata.md` 的逐条处置与新 hash，**不需重跑证据层**。

1. **先读原始输出**，再看本文件：`after/probe_commit_report.json`（原始）与 `after/probe_summary.stdout.txt`（渲染）。
2. **独立复算至少一个 oracle**：从 `after/probe_commit_report.json` 里取 `as_of_only_differs` 的两组输入（`as_of_date=2026-09-19` / `2027-03-31`，其余取 `RF/tests/test_recognition_bridge.py::forecast_document`），用**你自己的** canonical JSON 实现重算 `request_sha256` 与 `publication_id`。
3. **复跑**：`iso/probe_commit.py`（本文件 §4 已给出 run1/run2 不变量一致，但请你自己选第三次的 `--work` 新目录）。**复核已用真实长路径（不经 `C:\i09a`）复跑，`ALL_CASE_INVARIANTS_IDENTICAL=True`。**
4. **构造一个我未用于编写协议的变体**（建议，预先写下预期再跑）：
   - `forecast_version` 变化、`schema_version=3.8`（opt-in）、`artifact_type` 混用；或
   - 让 `members` 里出现第二个成员（同时请求 `--output` 与 `--markdown` 后再删掉 Markdown），检查读者的 `commit_status` 是否按 C-06 判为不可消费；或
   - 把 registry 指向**另一卷**（例如另一个盘符的临时目录）以验证 `I09-E09` 的必要性。
   - **复核实际采用的是**：`host_signed` 声称但无 attestation 记录的边界输入（得到 `validator_accepts_host_signed_without_record=true`）→ 由此新增 `C-13`。
5. **攻击 §3 的 7 条结论**，特别是第 4 条（「现状已有请求身份参与」）——它最容易被误读为「现状已经安全」。**复核已攻**：见 `errata.md` 规格补充（G4 分支无实现落点）。
6. **裁定 OPEN-I09A-1…6**（见 `open_items.md`），并明确哪些 C-条目被接受、哪些被否。**复核已给两项裁定意见**（§7 改序 + attestation 锚不入身份），见 `open_items.md` 与 `errata.md`。
7. **检查 allowlist**：`changed_paths` 必须为空（本卡不实施产品）；若发现任何产品文件被改，直接 `changes_required`。
8. **不得**把本卡的接受外推到 I-09-B/C 的实现资格或 I-08 的签名资格。

---

## 8. 未获得的资格（明确）

- 未获得：产品实现资格、事务/故障恢复资格、签名/信任资格、跨仓消费者资格、部署资格、预测准确性资格。
- 未裁决：I-08-A OPEN-D1..D7；本卡 OPEN-I09A-1..6。
- 未实测：提交锁、真实 kill/掉电、重复恢复、跨卷、跨仓消费者读取 `commit_status`、**`E31` 补偿行机制**、**G2 × committed 组合**、**3.8 消费者侧**、**attempt1 argv 缺陷重放**。
- **未验证（原样承接复核清单）**：`oracle.md` 的"只追加"无法逐行核验（无实现前副本）；`C:\i09a` 是否曾被用于写入；跨卷 `I09-E09`（本机仅 `C:/Recovery`）；I-08-A 的 `classify()` 语义只引用未复核（生产无 `classify`/`G3a`/`R-LEGACY` 落点）；`OPEN-I09A-5` 中"计划 owner 是否知悉"；14 条脏路径的完整历史（能证 I-09-A 未改，不能证谁改）。

---

## R. 独立 reviewer 最终裁决（round 3，2026-09-20）

> 本节由**独立 reviewer** 追加写入 `review.md`（该文件的 reviewer 段归属方）。追加为**纯字节级拼接**，未改动上文任何字节。追加前全文 sha256 = `9faa0990d7ffd4e2504af96c6eb4fa62d3f333e41dc58117fc8460fe063e541d`（16292 B）。**追加后文件 sha256 与本节字节 sha256 记录在 reviewer 报告 `REPORT3.md` 中（避免自引用）。**

### R.0 verdict（四值词表内）= **`changes_required`**

窄幅，**仅 2 处文本**（R-1、R-2，均为**追加勘误即可闭合**，不需重跑、不得就地回改冻结行）。除此之外：**证据层、契约本体（C-01…C-13）、`I09-E01…E10` 命名空间、OPEN 项登记、以及 E-10…E-13 的实质处置，我全部核验通过并背书**。

我在第二轮给出的预先承诺**未被违反**：那 4 条（E-10…E-13）**确以追加勘误落地**，证据层**零重跑**；R-1/R-2 是**本次闭合动作自身新引入的**文本缺陷（自我报告与实际落点不一致、以及一个重复标题），不是那 4 条的翻案。

### R.1 必须闭合的 2 项（最小修法：追加勘误）

- **R-1（P3，自我报告与文件不符）**：`errata.md` E-11 的处置表与 `handoff.json.review_round_2.findings.E-11` 均称 `review.md` 的 132/126 **出处**已改写为「本 attempt 期间的一次快照读数（该文件其后被重抓，现为 270 行）」。实测：该措辞落在 **`review.md:123`（§6-C）**，而 E-11 所指的 **`review.md:80`（§4 表行）仍是旧措辞**——仍标"**两个保留的快照文件**"，仍以 `after/git_status_after.txt` 作为 **132 行/126 真实条目**的出处，而该文件现已为 **270 行**，即 E-11 自称已修的那一处**未修**（该行末的"注"虽披露了 270 行的后续读数，但出处与数值依旧不可互证）。
  - **最小修法（追加勘误）**：在 `errata.md` 增一条 note，把 E-11 的落点**逐字更正为 `review.md:123`**，并声明 `review.md:80` §4 表行的"两个保留的快照文件"与出处引用**尚未修正、保持原样**（若 owner 允许改 `review.md`，则该行出处改为"本 attempt 期间一次快照读数（其后被重抓）"即可；**不改也接受**，只要勘误说清）。
- **R-2（P3，结构）**：`errata.md` 出现**重复的二级标题** `## §U 未验证项（原样承接复核清单）`（**L195** 与 **L236**），且 **L195 标题之下并不是未验证清单**，而是"P2-3 反证 + C-13 规格补充"的正文——该段原有的小标题在插入 E-10…E-13 时丢失，导致 C-13 的依据被挂在"未验证项"标题下。
  - **最小修法（追加勘误）**：追加一条 note 指明 L195 标题为**误置**，该段实为「规格补充：`C-13` 与 G4 降级（复核 P2-3 反证）」；L236 才是唯一的 `§U 未验证项`。若 owner 允许改 `errata.md`，把 L195 换成正确标题最干净。

**观察项（不阻塞、不要求本轮修）**：两处 `SELF-REFERENCE (not declarable here)` 行仍带**过期 size**（`after/product_hashes.txt` 记 `10843`，实测 `10940`；`changes.diff` 记 `32732`，实测 `33655`）。hex 已按要求撤除，完整性主张无损；建议下次重新生成时把 size 一并写成 `n/a`。

### R.2 我本轮**亲自复算**的读数值（逐条）

| 对象 | 实现者声明 | 我的实测 | 判定 |
|---|---|---|---|
| `oracle.md` | `d7f6b102…` | `d7f6b102ecc99a56…`，23302 B | **SAME**；且与 round 2 **逐字节相同 ⇒ 本轮未再就地改写** |
| `review.md` | `9faa0990…` | `9faa0990d7ffd4e2…`，16292 B | **SAME** |
| `decision.md` | `4a8cc048…` | `4a8cc048c797…`，43706 B | **SAME** |
| `handoff.json` | `f7eece90…` | `f7eece9086e1…`，32683 B | **SAME** |
| `binding.json` | 未变 `71995ed3…` | `71995ed3e377…`，20086 B | **UNCHANGED**（与 round 2 相同） |
| `commands.json` | 未变 `60aa3a99…` | `60aa3a99a5db…`，11687 B | **UNCHANGED** |
| `open_items.md` | 未变 `adfd00a6…` | `adfd00a64d5e…`，6874 B | **UNCHANGED** |
| `oracle_addendum.md` | `de7fa1f3…` | `de7fa1f335e4…`，11550 B | **SAME** |
| `errata.md` | `08b94980…` | `08b949803b3c…`，28630 B | **SAME** |
| `changes.diff` | 时点 `5a7ea074…`（自引用不给 hex） | `d0524711aa6e…`，33655 B | 自引用文件，**时点读数≠最终字节属预期**；我实测最终值如上 |
| `after/product_hashes.txt` | 时点 `17656c0f…`（自引用不给 hex） | `c2b86c1702e5…`，10940 B | 同上（亦为预期） |
| `decision.md:16` | 5 项（-1/-2/-3/-5/-6） | 原文核验：`其中 **5 项**（-1/-2/-3/-5/**-6**）阻塞 I-09-B 的绑定。本行是本文件**唯一**的阻塞项计数表述` | **成立**；我 round-2 的 grep 结论被正确引用 |
| `oracle.md` §9 末行 | 未回退 | L160 = `- 未裁决 OPEN-D1—D7（I-08-A）与 OPEN-I09A-1—6（本卡）。` | **未回退**，符合我的明示要求 |
| `oracle.md` 行数 | 178 | **178** | **成立**；§10 为末尾追加 |
| 「唯一一处就地改写」 | 成立 | **成立（以我 round-1 持有的 160 行副本为参照）**：round 2 比对显示 lines 1–159 与 §10 之外逐字相同、唯一差异为 L160；round 3 文件与 round 2 逐字节相同。**但这是复核侧副本证据，不构成独立第三方证明**（见 R.4 ①） |
| 证据层零重跑 | 声明 | **10/10** 探针脚本与原始证据哈希与第一轮完全相同；`commands.json` 未变 | **成立** |
| `handoff.json.unclosed_gaps` | 4 条 | `GAP-C13-attestation-record`（`status = OPEN - compatibility gap NOT closed`）+ `GAP-3.8-consumer-gate` + `GAP-e09-cross-volume` + `GAP-e31-compensation` | **成立**，满足我对 `C-13` 的第 3 条要求 |
| 自签/范围 | 未自签 | `status=review_pending`、`reviewer_status=pending`、`implementer_self_acceptance=false`、`changed_paths=[]` | **成立** |
| 生产不可变 / `reviews` | 零写入 | registry `bc3256bb…d1e91` 未变；`-- tools scripts config` 仍为**先于本卡**的 14 条既有脏路径；company-wiki 2 条、filing-fetch 0 条；`<PLAN>\reviews` 目录 mtime 仍 `2026-09-19 09:14:20` | **成立** |

### R.3 授予范围、标注与待 owner 项

- **授予范围（严格限定）＝仅"设计/契约层的记录完整性"**。**不授予**：①产品实现资格；②事务/故障恢复资格；③签名/信任资格；④跨仓消费者资格；⑤部署资格；⑥**预测 formula / 准确性相关资格——按原卡口径未授予**（本卡无产品执行命令、无 formula 交付物，该类资格不可由本裁决推导）。
- **`disclosure_adaptation` = `unmapped`（保持）**；**`accuracy` = `unproven`（保持）**。
- **待 owner 项：`OPEN-I09A-1…6` 全部仍未被裁决。** 我在 round 2 §5 给出的逐项意见（-1 逻辑名 + 身份封闭 + 历史身份不重算；-2 由 -1 导出；-3 一次升版且锚不入身份、与 D4 同批；-4 进 I-09-B allowlist + fail-closed + 负例；-5 维持阻塞直至 dispatch/索引更新；-6 由 I-08-A owner 落笔 + 会签）**只作建议**，不构成已生效决定。我复核确认：`errata.md:193`、`handoff.json.review_round_2.findings.owner_decision_suggestions` 与 PLAN 根 `OWNER_DECISIONS.md` 的框架一致（"待裁建议 / 未签之前保持 blocked 或 review_pending、实现者不得自决"），**未发现自裁**。
- `C-13`：**接受**其"规格 + 兼容缺口未闭 + 保留反证"的收口形式；三项要求（错误码保持**未分配**、绑定 I-09-B **可失败负例**、"兼容缺口未闭"进入 `unclosed_gaps`）**均已落实**。
- I-08-A §7 改序：**批准**，三条件（孤儿成员五条 / `E31` 仅在"已 append 的 committed 行成员缺失或 hash 不符"时触发 / 上游文本由 **I-08-A owner** 落笔）已按我的意见写入 `decision.md §5.6b` 与 `open_items.md`。

### R.4 我**未能验证**的项（不得当作已证）

1. `oracle.md` 的"只追加"**不可与实现前副本逐行核验**（PLAN 内无实现前副本；本 attempt 的 `before/baseline_hashes.txt` 未对 `oracle.md` 取 hash）。本轮"唯一一处就地改写"的结论**依赖我 round-1 持有的副本**，非独立第三方证明。
2. `after/git_status_after.txt` 的**旧内容（132 行 / 9942 B / `c6faa500…`）已不可获得**，该值永久不可复验。
3. `C:\i09a` **是否曾被用于写入**——未能验证（我只能证明它是只指向本 attempt 的 Junction，且我的复核全程不经它）。
4. **跨卷 `I09-E09`** 未实测（本机仅 `C:`/`Recovery`）。
5. I-08-A 的 **`classify()` 语义只引用未复核**（生产 grep 无 `classify`/`G3a`/`R-LEGACY` 落点）。
6. **attempt1 的 argv 缺陷未重放**（只核验其证据被保留且自洽）。
7. **`OPEN-I09A-5`/`-6` 的裁定人是否知悉**——无法验证。
8. **14 条脏路径的完整历史**——只能证明"I-09-A 未改"（43/43 `.py` 隔离副本一致），不能证明是谁、何时改的。
9. **`G2`（可复验签名）× `committed` 组合未测**（本环境无 attestation provider）。
10. **3.8 消费者侧未测**（属 I-08-A OPEN-D6，跨仓）。
11. **`E31` 补偿行机制未测**（本卡只冻结语义，不实现）。

### R.5 结论与后续

- 本裁决 = **`changes_required`（仅 R-1、R-2 两处文本，追加勘误即可）**。**R-1/R-2 落地后，我可仅凭文本核对直接改判 `accepted_scoped`，无需第四轮对抗式复核。**
- **禁止**：就地回改任何已冻结行（本轮 `oracle.md` 未再被改，E-10 登记的 §9 末行 `-5`→`-6` **保持未回退**，符合要求）；改动任何 `C-` 条目或 `I09-E` 码；把本裁决外推到 I-09-B/C、I-08 或部署。
- `handoff.json.status` 在 R-1/R-2 闭合前**保持 `review_pending`**；本节**不构成**对 `OPEN-I09A-1…6` 的裁决。
