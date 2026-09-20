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
