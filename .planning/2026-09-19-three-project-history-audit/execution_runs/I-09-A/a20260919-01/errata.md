# errata.md — I-09-A / a20260919-01（回应独立对抗式复核 changes_required）

**性质**：**追加式勘误**。本文件**不改写** `oracle.md` 的冻结正文（只在 `oracle.md` 末尾**追加**一节"勘误指针"，不移动/删除/改写任何冻结行），并更正 `oracle_addendum.md` / `decision.md` / `review.md` / `open_items.md` / `handoff.json`。

- 复核结论：`changes_required`（窄幅，仅文档/勘误层；**证据层不需要重跑**）
- 复核人**背书**：`C-01…C-12` 提案本体、`I09-E01…E10` 命名空间、`F-IDEM` 必答反例（独立重写算法、6 个值全部复现、`publication_id` 第三次独立重算）、`E31` 判定点、c02/c03/c05/c06/c07/c08/c11/c12 的全部实测结论；并用**真实长路径（不经 `C:\i09a`）**复跑 12/12 case，`ALL_CASE_INVARIANTS_IDENTICAL=True`。
- **本次勘误不构成重新验收**；`handoff.json.status` 保持 `review_pending`，reviewer 段落留空待填。
- **未改动任何 C-条目与 `I09-E` 码**（复核明令）。

---

## E-1 生产 registry 非空 `artifact_id` 行数：**实测 3 行，我写的"1 行"是错的**（P1-1）

**我错在哪（自我归因）**：我把**去重计数** `distinct_artifact_id=1` 当成**行数**写进了 4 处，并因此产生 `1+57=58≠60` 的自相矛盾。

**本次复核时用独立通道重数（PowerShell + ConvertFrom-Json）**，结果与复核人两条通道一致：

| 观测 | 值 |
|---|---|
| 总行数 | 60 |
| 非空 `artifact_id` **行数** | **3** |
| `null` `artifact_id` 行数 | **57** |
| 非空值的**去重**个数 | 1 |
| 该唯一值 | `47a46003e300d4972db50d36f65f94525ee470fcd4742b1c61921b42b8626788` |
| 3 行的 `artifact_type` / `note` | 全部 `snapshot` / 全部 `revenue_backtest create` |
| forecast 行中有 `artifact_id` 的 | **0 / 57** |

**结论方向反而加强**：3 行 snapshot 携带**同一个** `artifact_id`（一个 snapshot 被注册 3 次），而 **57 行 forecast 一个身份都没有** —— 「已提交的行无法自证是哪一次发布」的判据不变且更硬。

**处置（4 处 + 1 处撤回）**：

| 位置 | 原文 | 更正 |
|---|---|---|
| `oracle.md:62`（冻结期望） | `artifact_id` 非空行数 **1**（唯一一个 snapshot）；其余 **57** 行 `null` | 非空行数 **3**（全是 snapshot，且**同值**）；`null` **57**；注：`1+57=58≠60` 说明原值是去重计数误用。**按"只追加"原则，此更正以 `oracle.md` 末尾 §10 勘误指针落地，不改写第 62 行** |
| `oracle_addendum.md:19` | 判为 **✅ 成立** | **撤回该 ✅**：冻结期望 1 行为错，实测 3 行；该格改判 **❌ 期望错误（已勘误）**。这是本次唯一的 **false pass** |
| `decision.md:28`（N-1） | 非空 `artifact_id` 只有 1 行 | 非空 **3** 行（同值，全 snapshot）；**57 行 forecast 全为 null** |
| `review.md:72` | 非空 artifact_id / null = **1 / 57** | **3 / 57**（并注明去重值数为 1） |

---

## E-2 c02 的冻结原文是否真的写错：**我的"自曝"方向错了，撤回**（P1-2）

**我错在哪**：`oracle_addendum.md §2/§3` 与 `review.md §5` 声称冻结期望是「registry 行数 = 0；`is_registered=false`」，并据此宣布"期望写反"。**核对 `oracle.md:76` 冻结原文，记的是**：

> producer rc=**2**；`out.json` **不存在**；`report.md` 不存在；registry 行数=**1**；reader 仍报 `is_registered=true` 且 `commit_qualified`=**1**

即**行数与 is_registered/commit_qualified 三项与实测完全一致**；真正写错的**只有**「`out.json` 不存在」（实测：该路径上存在的是我注入的**目录**）。c03 同理：错的只有「`report.md` 不存在」，其余（rc=2、`out.json` 存在、行数=1）与实测一致。

**因此**：

1. **撤回**「冻结期望写反」这一自曝项 —— 它把 oracle 说得比实际更差，属**反向不实陈述**；
2. c02/c03 的实际偏差缩小为**一处措辞**：「注入物所在路径上不存在文件」被写成「路径上什么都没有」；
3. **判据方向从未改变**：rc=2（失败）却留下 `is_registered=true` / `commit_qualified=1` 的已提交行且磁盘零真实成员 —— 这是**冻结原文就写对**的结论。

**我无法出示 03:36 之前的 `oracle.md` 副本**（本 attempt 未保留实现前副本，`before/baseline_hashes.txt` 也未对 `oracle.md` 取 hash）。因此按复核要求：**撤回该自曝项**，并在下方 §U 如实登记「冻结文件的只追加无法逐行核验」。

---

## E-3 「I-08-A §7 次序修正」缺独立问题陈述（P2-1）

`oracle.md:143`（A6）与 `decision.md:403`（A6）把次序修正分别指向 `OPEN-I09A-2` / `OPEN-I09A-1`，而这两项的**问题陈述都不覆盖次序**（-2 是"两目标算一个还是两个发布"；-1 是 `package_target` 语义 + D4 耦合）→ 派单会漏项。

**处置**：新增 **`OPEN-I09A-6`**（问题陈述、裁定人、是否阻塞两列齐全，见 `open_items.md`），并在 `oracle.md` 末尾 §10 与 `decision.md` 的 A6 行加**勘误指针**纠正交叉引用。

---

## E-4 `decision.md` 的阻塞计数错误（P2-2）

`decision.md:16` 原文「其中 **2 项**阻塞 I-09-B 的绑定」→ 更正为 **4 项**（`-1`/`-2`/`-3`/`-5`），与 `open_items.md`、`handoff.json.blocked_by` 对齐。

---

## E-5 陈旧哈希（P2-4）

| 位置 | 我声明的 | 实测（本次） | 原因 |
|---|---|---|---|
| `handoff.json.product_hashes["after/git_status_after.txt"]` | `7afc49a8…`（9159 B） | `c6faa500…`（9942 B，132 行） | 该文件在 03:46 被**重抓**（并发卡继续改动该树）后我未刷新声明 |
| `handoff.json.product_hashes["changes.diff"]` | `ce43c6a6…` | 以本次重新生成后的值为准 | 打包顺序更新 |

**处置**：`handoff.json.product_hashes` 全部改为**本次重新生成后的实测值**，并对 `handoff.json` 自身、`changes.diff`、`after/product_hashes.txt` 三者显式标注 **`self-reference：不可声明`**（自己不能包含自己的 hash），指向"以后打包生成的 `after/product_hashes.txt` 为准"。

---

## E-6 git 行数三处口径不一（P2-5）

| 位置 | 原文 | 问题 |
|---|---|---|
| 快照文件（实测） | before = 148 行 / 142 条真实条目；after = **132 行 / 126 条** | 基准 |
| `review.md:79` | `148 / 124 / 132` | 中间的 124 来自**未保留的**中间快照 |
| `binding.json:27` | `142 / 118 / 132` | 同理 |

**处置**：统一为**只引可复核的快照文件**：before `148` 行（142 真实条目）、after `132` 行（126 真实条目）；并明确注明「**首次 after 快照（124 行）未保留，故不作为证据引用**」。`binding.json` 的 `concurrent_activity_caveat` 同步改写为同口径。

---

## E-7 `proposed_identity()` 的字面量载荷（P3-1）

`iso/probe_commit.py::proposed_identity()` 里 `package_target="out.json"`、`members=["out.json"]` 是**硬编码字面量**，且 `members` 用的是**文件名**而非 C-04 要求的**相对角色名**。

**处置**：在"身份契约 5/5 一致"处（`review.md §4`、`decision.md §3.4`、`oracle_addendum.md`）加限定：

> 该 5/5 是对 **harness 字面量载荷**的自洽性检验（同一算法两次实现一致、`as_of`/company/engine/artifact_type 四个维度都改变身份）；`package_target` 与 `members` **尚未与生产事实绑定**（分别属 `OPEN-I09A-1` 与 `OPEN-I09A-3`）。**不得**据此宣称身份契约已可用于生产落地。

---

## E-8 两处措辞收窄（P3-3）

1. `decision.md:254`「唯一 commit 点」段：把「单次**原子**追加」限定为「**单次追加；不承诺抗撕裂**；撕裂由链校验 fail-closed 检出（见故障点 F7）」。
2. `oracle_addendum.md §5`（c04b）：注明 `producer_rc` 是**包装进程**的退出码，CLI 自身的 rc 在 `producer_stdout` 里（`rc=2` 出现在 stdout 行，包装进程仍为 0）。

---

## E-9 `changes.diff` 的规模口径（P3-2）

`changes.diff` 标题写「87 files」，而 attempt 内（排除 `iso/venv/` 与 `__pycache__`）实有 **173** 个文件；86 个未声明几乎全在 `iso/scratch/**`（含 `cases/*/input.json`、`*/out.json`、`*/report.md` 等**原始用例字节**）。

**处置**：改为**显式两类声明**（并新增一个机械核验脚本，使"没有未声明文件"可被复算）：

- `iso/gen_changes_diff.py` 现在输出三行头部：`DELIVERABLES = 91`、`WORK PRODUCTS (iso/scratch/**) = 86`、`TOTAL DECLARED = 177`；每个条目带 `# class=deliverable` 或 `# class=workspace-output` 标记 + sha256 + size；
- **只排除** `iso/venv/**`（一次性解释器）与 `__pycache__/**`（字节码缓存），并在头部**写明它们不是证据**；
- 机械核验：`TOTAL DECLARED` 与实际文件数**逐一致**（不含 venv/pycache 的实际文件数 = 声明数）；
- **不删除** `iso/scratch` 的原始用例字节（`cases/*/input.json`、`*/out.json`、`*/report.md`、各 case 私有 registry）—— 它们是证据。

---

## 需要补的规格（复核 P2-3 已给实测反证）

**反证事实**（复核人自造边界输入，源码依据 `revenue_publication.py:222-226` 只校验 `attestation_status` 的**取值合法性**；全产品 grep `publication_attestation|attestation_record` **0 命中**）：**一个 receipt 声称 `host_signed` 却没有任何 attestation 记录，验证器照样接受**（`validator_accepts_host_signed_without_record=true`、`register_rc=0`、`rows=2`、`validation_status=["validated","validated"]`）。

**因此 I-08-A 的 G3b/G4 分支在生产里没有实现落点**，我在 `decision.md §5.5` 写的「`| G4 无效 | 不可能 |`」是一条**未兑现的断言**。

**处置（采纳复核给的选项 (a) + (b) 并行）**：

- **新增 `C-13`**（只新增，不改 -01…-12）：
  > **C-13**：「receipt 声称 `host_signed` 但**无任何 attestation 记录**」的形状，在该门落地后**必须于提交前拒绝**，且**不得**被算作 committed；错误码**归属 I-08-B 的 attestation 门**定义（本卡不占用、不新造 I-08-A 的错误码号）。在 I-08-B 落地前，该形状**必须**被显式标为「**兼容缺口未闭**」，并在交付说明中保留复核人的实测反证。
- `decision.md §5.5` 的 G4 格降级为：「**由 I-08-B 的 attestation 门实现；落地前不得声称已闭**」，并附该反证。
- 该反证写入 `oracle.md` 末尾 §10 勘误指针（不新增冻结期望，只登记为**上游缺口**）。

---

## 其它要求的处置

| 复核要求 | 处置位置 |
|---|---|
| `open_items.md` 注明 **OPEN-I09A-2 由 OPEN-I09A-1 导出**，并修正两项"倾向"的互相矛盾（-1 倾向"逻辑名" ⇒ 同逻辑目标两个目录=同一发布；-2 倾向"按 `package_target` 区分" ⇒ 两个发布） | `open_items.md`：-2 改为「**由 -1 导出**；若采纳 -1 的"逻辑名"倾向，则**同一逻辑目标的两个目录 = 同一发布**（两处目录只是同一 `package_target` 的副本，`member_paths` 不参与身份）」——与 -1 一致 |
| 把 **OPEN-I09A-4** 写进 **I-09-B 的 allowlist**：必须 fail-closed（`RegistryError`）+ 负例测试 | `handoff.json.implementation_targets["I-09-B"]` 与 `open_items.md` 的 -4 行 |
| 把 **c02/c03/c05 与 V2（单成员包：只给 `--output`，从不请求 `--markdown`）** 写成 I-09-B 的验收用例；"半包可见"保持**证据**而非"已修好" | `handoff.json.implementation_targets["I-09-B"]` 新增 `acceptance_cases_from_i09a` |
| **裁定意见①**：批准 I-08-A §7 改序，但须同时定**孤儿成员规则**（P5 成功/C3 失败会留下已落盘、无 committed 行的成员）、重述 **E31** 触发语义，且由 **I-08-A 的 owner** 写进上游文本 | `open_items.md` 的 OPEN-I09A-6 附条件；`decision.md` §5.6 增补孤儿成员规则与 E31 重述（**归属 I-08-A owner**） |
| **裁定意见②**：同意 attestation 锚与本卡字段集**一次升版**，但**锚不得进入 `identity_payload`**（否则重签会改变发布身份、破坏 C-08 幂等）；须给出"新增哪些键/哪些参与身份"；并与 **I-08-A OPEN-D4 同批裁决**；D4 升版时"**历史行身份不重算**"从倾向**提升为 C-01 强制条款** | `open_items.md` 的 -3 与 -1；`decision.md` 的 C-01 增补强制条款（见下） |
| **不得**改动任何 C-条目与 `I09-E` 码；勘误不得读作"重新验收"；`handoff.json.status` 保持 `review_pending` | 本文件与所有更正均遵守 |

**C-01 的强制条款增补（不改 -01 正文，作为附注）**：
> **C-01-附注（强制）**：`identity_payload` 的字段集**封闭**；I-08-B 的 attestation 锚（以及任何未来行内键）**不得**进入 `identity_payload`。当 `receipt_schema_version`（I-08-A OPEN-D4）或行 schema 升版时，**历史行的身份一律不重算**——旧行保留其原 `publication_id`，新行使用新版本；「不重算」是**强制条款**，不再是倾向。

**机械核验（新增脚本，供第二轮复核定点复跑）**：`iso/check_errata_integrity.py` → `after/errata_integrity_check.stdout.txt`。它证明三件事：

1. `oracle.md` 仍含 **C-01…C-12 十二行**（表行数=12）与 **I09-E01…E10 十个码**；
2. 勘误所声明"错"的两行**仍逐字存在**（`artifact_id` 非空行数=1 那行、c02 冻结行含 `registry 行数=1` 与 `` `out.json` **不存在** `` 两个标记）→ 证明修正确实是**追加**而非改写；
3. `oracle.md` 中**没有** `C-13` 字样（`C-13` 是 `decision.md` 的**新增**条目），且 `oracle.md` 末尾存在勘误指针节。

脚本首次运行曾报 `C-13_in_oracle=True`，原因是 `oracle.md §10` 的勘误指针行当时**内嵌了 `C-13` 字样**；已把该行改为「追加提案（编号落在 §5 的 C-12 之后）」的中性表述，使机械检查恢复为 `False`。这是**指针文字**的改动，**未触碰任何冻结契约行**（第 1/2 项检查在两次运行中均为真）。

---

## §U 未验证项（原样承接复核清单）

以下各项**本 attempt 未能验证**，一字不改地承接：

1. `oracle.md` 的"只追加"无法逐行核验（PLAN 内无实现前副本；本 attempt 的 `before/baseline_hashes.txt` 也未对 `oracle.md` 取 hash）。
2. `C:\i09a` 是否曾被用于写入（本次复核经 `fsutil` 确认它是 Junction 且只指向本 attempt；最终探针不依赖它）。
3. 跨卷 `I09-E09` **未实测**（本机仅 `C:/Recovery`）。
4. I-08-A 的 `classify()` 语义**只引用未复核**（生产 grep 无 `classify`/`G3a`/`R-LEGACY` 落点）。
5. attempt1 的 argv 缺陷**未重放**。
6. `OPEN-I09A-5` 中「计划 owner 是否知悉」未验证。
7. 14 条脏路径的完整历史：能证 **I-09-A 未改**，**不能**证是谁改的。
8. **G2 × committed 组合未测**。
9. **3.8 消费者侧未测**。
10. **`E31` 补偿行机制未测**。

## §C 勘误后的状态

- `handoff.json.status` = **`review_pending`**；reviewer 段留空。
- 生产三仓零写入；`<PLAN>\reviews` 零写入；未执行 `git add/commit/restore/stash`。
- 三资格陈述不变：①设计/契约=提案已冻结待裁；②实现=未获得（`changed_paths=[]`）；③事务/故障=未获得。
- **本勘误不构成重新验收，也不改变任何 C-条目与 `I09-E` 码。**

### 勘误后 hash（勘误前后对照）

| 文件 | 勘误前 sha256 | 勘误后 sha256 |
|---|---|---|
| `errata.md` | （不存在） | `cbe48638764cabc4029aa800a1e87564fca1693223b65458ad20117cff9f25b1`（**自引用**：本表写入后本文件又变化一次，权威值见 `after/product_hashes.txt`） |
| `oracle.md` | `237eab025a3a6d99b3f844467a76338e9116a28f77aa73419518d3080b36efbc` | `d7f6b102ecc99a564ff6977b69a7b5e8fe6af9edcc4ae356c041426891e6dc8d` |
| `oracle_addendum.md` | `1d411dcd9930f00bcaedd03cea8d84f858a9a43c829cada901419898916d0422` | `ac960483d18a20b2e2dc16112429030dbd072cc1baa7029ddd8fa88aee28dea5` |
| `decision.md` | `8af31d2af48e0412989bc7dc75d6f0d5a0c7e8a2b176231b1a313d22ff11d4a7` | `d12f8a53baf9fbe0be4c4e6dad6229d41b31ce3d0a0c3104d27678afa168a68c` |
| `open_items.md` | `4982b9134dec93071df3a06c6efd3b2003675006500b95b1ac1c4f57863bb8ef` | `adfd00a64d5ec3ef061c5f601e6692ca6f690ff59ee6eb015fb08f1174f3c629` |
| `review.md` | `7190c3fe45a39af7a5c6ec6bbcd7a6d1d9c7c255bd3d040ff4cae02ced96064f` | `d6b067f2a6667b70bfd58eb82e4943961173e18cf5d2fa449d23b02d82b1ed97` |
| `binding.json` | `9213948accdaf15cc91701a2fc70a2f70c888c9dc827161a09e79a56e8c3dd61` | `71995ed3e3771f95dabbf99d8b1ebe7faeb13e84a7443a6b46f0580956d5b5b9` |
| `handoff.json` | `1b17edb6bb80e40f508900817ad62198d05998939e3b1f8802718983ede753a3` | `c442539bbc2acb495db4c821d7e42d0d15ed82bf581e0f58ca78eef3667b8a99` |
| `commands.json` | `60aa3a99a5db0392e2b6c4164dbd5e284da6baf07a2c951d842d3ddbdc8b5644` | **未变**（勘误未改命令集） |
| `changes.diff` | `a809fbf943a1ff0a2fbfb17b7eb6eb9783dcec790ec8811c8627f770420041db` | **自引用**：它声明其它文件的 hash，自身值只在最后打包的 `after/product_hashes.txt` 里 |
| `iso/gen_changes_diff.py` | （不存在） | `b0f16a07e3dde9fd716cc649ea704228cdc190e9f03b178e94043077ab87481a` |
| `iso/check_errata_integrity.py` | （不存在） | `4271cd88e38b5d423ab6a0a16a1e3a4d701b7a74c901b7f886dbe3844a7ab272` |
| `after/errata_integrity_check.stdout.txt` | （不存在） | `334dc0a381c88bb83b271ba7ef67c310bbdf65274f52750feeb37102dea239f4` |
| `after/product_hashes.txt` | `b8523dce86762a09c4bdb4ca271b592bb26dcc5b7bc0c54bfe7fa28cae43d2a2` | **自引用**（最后打包生成，权威清单；它不能包含自身 hash） |
| 全部探针脚本与原始证据（`iso/probe_*.py`、`after/probe_*.stdout.txt`、`after/probe_*_report*.json`、`before/baseline_hashes.txt`、`before/git_status_before.txt`） | — | **全部未变**（勘误层未重跑任何探针、未改写任何原始证据） |
