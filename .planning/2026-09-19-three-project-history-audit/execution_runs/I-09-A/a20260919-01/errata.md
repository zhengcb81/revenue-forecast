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

| 位置 | 我声明的 | 实测（第一轮勘误时） | 原因 |
|---|---|---|---|
| `handoff.json.product_hashes["after/git_status_after.txt"]` | `7afc49a8…`（9159 B） | `c6faa500…`（9942 B，132 行） | 该文件在 03:46 被**重抓**（并发卡继续改动该树）后我未刷新声明 |
| `handoff.json.product_hashes["changes.diff"]` | `ce43c6a6…` | 以重新生成后的值为准 | 打包顺序更新 |

**第二轮更正（E-11）**：上表"实测"栏的 `c6faa500…`（9942 B / 132 行）**已在本轮勘误中被就地重抓覆盖**（现为 25955 B / 270 行 / `f3ef8287…`），**该旧快照未保留、`c6faa500…` 永久不可复验**。因此本表该格应读作「**第一轮勘误时的实测值，现已不可复验**」，不得作为当前锚点。

**处置**：`handoff.json.product_hashes` 不再逐文件声明 hex（避免每轮再产生陈旧值），统一指向最后生成的 `after/product_hashes.txt`；并对 `handoff.json` 自身、`changes.diff`、`after/product_hashes.txt` 三者标 **`SELF-REFERENCE`**（第二轮进一步要求：**不输出具体 hex**，见 E-13-1）。

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

# 第二轮复评（verdict `changes_required`，仅勘误文本）—— E-10 与四项闭合

复评**背书**：E-1…E-9 全部真落地；独立重数 registry 与更正后声明一致；E-9 机械复现 `177 = 91 + 86`、未声明文件 0；**证据层零重跑**（11/11 探针脚本与原始证据哈希与第一轮完全相同、`commands.json` 未变）；规格补充写法正确（是**规格**而非"已修好"）。以下 4 条为必须闭合项。

## E-10 `oracle.md` §9 末行被**就地改写**（未事先声明）—— P1

**事实（复核实测，我复核确认）**：`oracle.md` §9 末行由
`- 未裁决 OPEN-D1—D7（I-08-A）与 OPEN-I09A-1—**5**（本卡）。`
改为
`- 未裁决 OPEN-D1—D7（I-08-A）与 OPEN-I09A-1—**6**（本卡）。`
（第一轮 160 行 → 本轮 178 行；§10 是追加，**这一行是唯一一处就地改写**。）

**为什么是错的**：它推翻了四处明文承诺——`errata.md:3`、`oracle.md:166`、`open_items.md:32`、以及派单陈述的「冻结正文一字未改」。成因是我把"新增 `OPEN-I09A-6`"顺手回填到了 §9 的冻结清单行，而没有意识到那属于**冻结正文**。

**加重情节（必须一并承认）**：`iso/check_errata_integrity.py` 的输出被我表述为"**证明修正确实是追加而非改写**"，**该推论不成立**——脚本只检查 *C-id 集合*、*I09-E id 集合*、*两行 marker 是否存在*、*`C-13` 是否不在 oracle*、*§10 指针是否存在*。**两行存在 ≠ 其余行未被改**；本轮实测恰好存在一处就地改写，而脚本仍全 True。该脚本已在文件头写入 **`capability_limit`**。

**处置（按复核要求，不回改那一行）**：

1. **不回退**该行（回退会造成第二次就地改写）；
2. **撤回**「`oracle.md` 冻结正文一字未改」这一措辞——正确表述是：**冻结正文有且仅有 1 处就地改写（§9 末行 `-5`→`-6`，因新增 -6），其余 177 行未动，§10 为追加**；
3. 该改写**未事先声明**，属本勘误轮的方法缺陷，登记为 **E-10**；
4. `iso/check_errata_integrity.py` 加 `capability_limit`（见下）；
5. 「冻结正文只追加」的可核验性**依赖复核侧的副本**，**不构成独立第三方证明**（承接未验证项①）。

**脚本能力边界（已写入脚本文件头与 `errata.md` 本行）**：

> `check_errata_integrity.py` 只证明：**被点名的** frozen 行仍在、C-id/`I09-E` id 集合未变、`C-13` 不在 `oracle.md`、§10 指针存在。它**不证明**其余冻结行未被就地改写，也**不构成**"只追加"的证明。

## E-11 `after/git_status_after.txt` 在勘误轮被**就地重抓**（已声明产物被覆盖）—— P2

**事实**：该文件第一轮 9942 B / 132 行 / `c6faa50068bb…` → 本轮 **25955 B / 270 行 / `f3ef8287ff07…`**，**旧快照未保留**。

**后果与处置**：

| 后果 | 处置 |
|---|---|
| `c6faa500…` **永久不可复验**（复核第一轮曾核它为真） | 登记为**未验证项⑨（新增）**：该文件的旧（132 行 / 9942 B）内容现已不可获得 |
| E-5 表仍把它列为"实测（本次）`c6faa500…`（9942 B，132 行）"，与脚注矛盾 | 已改写为：「第一轮实测值 `c6faa500…`（9942 B / 132 行），**该快照已在本轮被就地覆盖、不可复验**；现文件为 25955 B / 270 行」 |
| `review.md` 以该文件为出处声明"after 快照 = 132 行/126 真实条目"，出处与数值不再对应 | 出处改为「**本 attempt 期间的一次**快照读数（该文件其后被重抓，现为 270 行）；数值仅对该次读数成立」 |
| 今后纪律 | **快照一律另存新名**，不再覆盖任何已被声明过的产物 |

## E-12 阻塞项计数不一致（4 vs 5）—— P2

`decision.md:16` 写「其中 **4 项**（-1/-2/-3/-5）」，而 `open_items.md`（-1/-2/-3/-5/**-6** 全为"是"）与 `handoff.json`（"…-1, -2, -3, -5 **and -6** block…"）都是 **5 项**；同一行已写 `OPEN-I09A-1…6` 却只列 4 项。
**处置**：改为「其中 **5 项**（-1/-2/-3/-5/**-6**）阻塞 I-09-B 的绑定」。复核另指出派单所称"分别表述"并未发生（`grep 阻塞 I-09-B` 在 `decision.md` 只命中第 16 行）—— 本行即**唯一**表述处，已如实说明。

## E-13 三项 P3—— 处置

1. **自引用 hash 不再输出具体 hex**：`refresh_hashes.py` 与 `iso/gen_changes_diff.py` 已改，对 `after/product_hashes.txt` 与 `changes.diff` 一律输出 `SELF-REFERENCE (not declarable here)`，**不给 hex**；`product_hashes.txt` 文件内自身那一行同样标注（此前文件内 `grep SELF` = 0 命中）。
   **复核更正我派单中的错值**：`after/product_hashes.txt` 的**实际** sha256 是 `49df7f25e1269a39be9756c6be7cfa351c05f2618eb02ddcb10916656c79c1bb`（10729 B），**不是**它自声明的 `a126badf…`；**自声明值不得当下游锚点**。gen_changes_diff 的第一轮还曾为「自身」输出过一行 hex（`L128`/`L173`），本次已一并消除。
2. `decision.md` §8 A2 行（仍写 `G1/G4 **不可能是** committed`）→ 追加「（见 §5.5 降级说明）」；`review.md` §6-C 的 `148→**124**→132` 叙事补上「124 未保留、不作证据」限定（E-6 的统一此前只落到 §4 表格）。
3. `oracle_addendum.md` §7 末行写错 c04 的 reader 结果 → 按 **c04（嵌套路径**存在**且已写入 ⇒ reader `is_registered=true`）** 与 **c04b（ACL 拒绝 ⇒ 路径不存在、0 行）** 分列更正。

## 复核对 `C-13` 与 §7 改序的裁定意见（**接受**，三条要求已写入文档）

**`C-13`（接受，附三条）**：
1. 错误码在 I-08-B 定案前保持**未分配**——**不得**借用任何 `I09-E` 号（本卡不占用、不新造）；
2. `C-13` 必须绑定一条 I-09-B 的**可失败负例**（receipt 声称 `host_signed` 且无记录 ⇒ 提交前拒绝、不得落 committed 行）；
3. 「**兼容缺口未闭**」必须出现在 `handoff.json` 的**未关闭清单**里（而非仅正文），以免下游误读为已闭。

**§7 改序（批准，附三条条件）**：
1. 孤儿成员五条（一律不可消费、不得自动删除、重试必须复用同一 `package_target` 与角色名、判定可复算、**不写 prepare 行**）——已在 `decision.md §5.6b`；
2. `E31` 触发语义必须是「**已 append 的 committed 行**所声明的必需成员缺失或 hash 不符」——**孤儿、prepare 失败、成员写盘失败但 C3 未发生，都不得触发 `E31`**；
3. 该上游文本改动**必须由 I-08-A 的 owner 落笔**，本卡**不得**代改。

**`OPEN-I09A-1…6` 的逐项裁决建议**：已抄入计划层 `OWNER_DECISIONS.md`。本卡文档只登记它们是**待裁建议**（见 `open_items.md`），**不作为已生效决定**。

## §U 未验证项（原样承接复核清单）

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

**机械核验（新增脚本，供第二轮复核定点复跑）**：`iso/check_errata_integrity.py` → `after/errata_integrity_check.stdout.txt`。**能力边界（第二轮复核已纠正我的过度表述，见 E-10）**：它只证明

1. `oracle.md` 仍含 **C-01…C-12 十二行**（表行数=12）与 **I09-E01…E10 十个码**；
2. 勘误所声明"错"的**被点名两行**仍逐字存在（`artifact_id` 非空行数=1 那行、c02 冻结行含 `registry 行数=1` 与 `` `out.json` **不存在** `` 两个标记）；
3. `oracle.md` 中**没有** `C-13` 字样（`C-13` 是 `decision.md` 的**新增**条目），且 `oracle.md` 末尾存在勘误指针节。

**它不证明**「其余冻结行未被改写」，**也不构成"只追加"的证明**——本轮实测恰有一处就地改写（§9 末行，E-10）而脚本仍全 True。**原表述「证明修正确实是追加而非改写」已撤回。**

脚本首次运行曾报 `C-13_in_oracle=True`，原因是 `oracle.md §10` 的勘误指针行当时**内嵌了 `C-13` 字样**；已把该行改为「追加提案（编号落在 §5 的 C-12 之后）」的中性表述，使机械检查恢复为 `False`。这是**指针文字**的改动；**但注意**：同一轮里 §9 末行也被就地改写了（E-10），当时**未**被这一检查发现。

---

## §U 未验证项（原样承接复核清单）

以下各项**本 attempt 未能验证**，一字不改地承接：

1. `oracle.md` 的"只追加"无法逐行核验（PLAN 内无实现前副本；本 attempt 的 `before/baseline_hashes.txt` 也未对 `oracle.md` 取 hash）。**第二轮补充**：该核验依赖复核侧的副本，**不构成独立第三方证明**；且本卡已承认一处就地改写（E-10）。
2. `C:\i09a` 是否曾被用于写入（本次复核经 `fsutil` 确认它是 Junction 且只指向本 attempt；最终探针不依赖它）。
3. 跨卷 `I09-E09` **未实测**（本机仅 `C:/Recovery`）。
4. I-08-A 的 `classify()` 语义**只引用未复核**（生产 grep 无 `classify`/`G3a`/`R-LEGACY` 落点）。
5. attempt1 的 argv 缺陷**未重放**。
6. `OPEN-I09A-5` / **`-6`** 的「裁定人是否知悉」未验证。
7. 14 条脏路径的完整历史：能证 **I-09-A 未改**，**不能**证是谁改的。
8. **G2 × committed 组合未测**。
9. **3.8 消费者侧未测**。
10. **`E31` 补偿行机制未测**。
11. **（第二轮新增）** `after/git_status_after.txt` 的**旧内容（132 行 / 9942 B / `c6faa500…`）现已不可获得**（被本轮就地重抓覆盖，见 E-11）。

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
| 全部探针脚本与原始证据（`iso/probe_*.py`、`after/probe_*.stdout.txt`、`after/probe_*_report*.json`、`before/baseline_hashes.txt`、`before/git_status_before.txt`） | — | **全部未变**（两轮勘误均未重跑任何探针、未改写任何原始证据） |

### 第二轮闭合后的 hash（**最终值，取自文件系统；自引用文件不给 hex**）

| 文件 | 第二轮闭合后 sha256 |
|---|---|
| `errata.md`（含 E-10…E-13 与本节） | **自引用**：本表每写一次本文件就变一次 ⇒ **不给 hex**；第二轮闭合时点真实值 = `886619dd1403df4a0ec925f33507ef53b5ba6427ff06e3bc394623cd6aaee59f`（28471 B），审查者请自行 `Get-FileHash` |
| `oracle.md`（178 行；**唯一就地改写 = §9 末行**，见 E-10，**未回退**） | `d7f6b102ecc99a564ff6977b69a7b5e8fe6af9edcc4ae356c041426891e6dc8d` |
| `oracle_addendum.md`（§7 末行按 c04/c04b 分列更正） | `de7fa1f335e4c4054e6cccdb7d8c25160518bee0efc50bc1091de9392715bcb5` |
| `decision.md`（阻塞项 **5**；A2 加降级指引） | `4a8cc048c7977d914b378cfcee9b5974befb49e1f53e5cb1333e2184b75c8667` |
| `open_items.md`（未变） | `adfd00a64d5ec3ef061c5f601e6692ca6f690ff59ee6eb015fb08f1174f3c629` |
| `review.md`（124 限定 + provenance 更正） | `9faa0990d7ffd4e2504af96c6eb4fa62d3f333e41dc58117fc8460fe063e541d` |
| `binding.json`（未变） | `71995ed3e3771f95dabbf99d8b1ebe7faeb13e84a7443a6b46f0580956d5b5b9` |
| `commands.json`（**未变**） | `60aa3a99a5db0392e2b6c4164dbd5e284da6baf07a2c951d842d3ddbdc8b5644` |
| `handoff.json`（新增 `unclosed_gaps` + `review_round_2`） | `f7eece9086e16469d9a0e6f0f4398147d0412cb2b9d2fbe18a3088bbf7466c49` |
| `iso/check_errata_integrity.py`（加 `capability_limit`） | `a8aaef4d28a556d94b6d019d15d30146c4424932cfffd952ae49bd0bc3e7870a` |
| `iso/gen_changes_diff.py`（自引用不给 hex） | `a1841cabddfe3d0a121ed026c1e6655857c4f13b8f57ae1b39f60198c89a4b98` |
| `refresh_hashes.py`（自引用不给 hex，前缀无关） | `da0ead736229ab277516a80f2f5aab4274fe154d3772dce2ef7bd63eb89abe21` |
| `after/errata_integrity_check.stdout.txt`（含 CAPABILITY_LIMIT 行） | `2ab1f283a2360cd275a094ff8d0859aa39bef6be03b7b90b4c28c36fa5514c9f` |
| `recovery/README.md`（未变） | `f94f3b9a9922f954bee4ad03644704ba6271ea5d00708b1a2cd57e8eee618a87` |
| `changes.diff` | **SELF-REFERENCE（不给 hex）** |
| `after/product_hashes.txt` | **SELF-REFERENCE（不给 hex）**：真实值 = 文件系统读数 `569d76ffa2e00411bf4a3a6e6334ab0ec579e79387362e7727268f15bd6362c7`（**仅为第二轮闭合时点读数，写回本文件会再次失效**；审查者应自行 `Get-FileHash`） |

**纪律（E-11 之后）**：任何快照/清单**另存新名**，不再就地覆盖已声明产物；生成物（`changes.diff`、`after/product_hashes.txt`）在每次改动后按 `changes.diff → product_hashes.txt` 顺序**最后重生成**。

---

# 第三轮（reviewer 亲自追加裁决于 `review.md` §R）—— R-1 / R-2 闭合

reviewer 的 round-3 verdict = **`changes_required`**（窄幅，**仅 2 处文本**：R-1、R-2；追加勘误即可闭合，**不需重跑**、**不得就地回改冻结行**）。除 R-1/R-2 外，**E-10…E-13 的实质处置、证据层零重跑、契约本体（C-01…C-13）、`I09-E01…E10`、OPEN 项登记全部获其背书**；第二轮预先承诺**未被违反**，R-1/R-2 是闭合动作自身新引入的缺陷，不是翻案。
**本节为纯追加**：上文（含 E-11 原文）**一字未改**；R-1 的报告落点偏差按"追加 note 更正"处理，不回写 E-11 段落。

## R-1（P3，自我报告落点与文件不符）—— 追加 note 更正

**事实（我已复核）**：E-11 的处置表与 `handoff.json.review_round_2.findings.E-11` 声称"`review.md` 的 132/126 **出处**已改写"。实测：

| 行 | 现状 | 说明 |
|---|---|---|
| **`review.md:123`（§6-C）** | **已改写**为「148（before 快照）→ 124（**未保留 ⇒ 不作证据**）→ 132（当时保留的 after 快照；**该文件其后在勘误轮被就地重抓为 270 行、旧内容不可复验**）」 | **E-11 的真实落点在这里**，不是 `:80` |
| **`review.md:80`（§4 数据表行）** | **仍是旧措辞**：仍标「**两个保留的快照文件**，勘误 E-6 统一口径」，并以 `after/git_status_after.txt`（现 270 行）作为「**132 行 / 126 真实条目**」的出处 | **该行保持原样、未修**（其行末"注"已披露 270 行的后续读数，但**出处与数值仍不可互证**） |

**更正声明（逐字）**：E-11 所述"`review.md` 出处已改写"的落点是 **`review.md:123`（§6-C）**；**`review.md:80` 该行未修、保持原样**。本卡在此**明确声明该行仍存在"出处与数值不可互证"的缺陷**，并把它列为**已知缺口**（见 `handoff.json.review_round_3.known_gaps`）。
**未修理由**：本轮边界为"**只许追加**"，且 `review.md` 的既有字节（含 reviewer 自行追加的 §R）**不得改动**；若 owner 允许改 `review.md`，最小修法是仅改 `:80` 的**出处列**（改为"本 attempt 期间一次快照读数，该文件其后被重抓"）。

## R-2（P3，结构：重复二级标题）—— 追加 note 更正

**事实（我已复核）**：`errata.md` 存在**重复二级标题** `## §U 未验证项（原样承接复核清单）`：

| 行 | 实际内容 | 判定 |
|---|---|---|
| **L195** | 标题之下**不是**未验证清单，而是「**复核 P2-3 反证 + `C-13` 规格补充**」正文（原文的小标题在插入 E-10…E-13 时遗失，导致该段被误置于 `§U` 标题之下） | **标题误置** |
| **L236** | 真正的未验证清单（11 项） | **唯一有效的 `§U`** |

**更正声明（逐字）**：**L195 的 `## §U …` 标题属误置**，其下内容实为「**规格补充：`C-13` 与 G4 降级（复核 P2-3 反证）**」；**`§U` 只有 L236 一处有效**。
**未就地改标题的理由**：同上（只许追加、不就地回写）。本 note 即为该结构的权威更正，机器读法以本声明为准。

## 可选观察（不阻塞、本轮不要求修）

两处 `SELF-REFERENCE (not declarable here)` 行仍带**过期 size**（声明 10843 / 实测 10940；声明 32732 / 实测 33655）。**hex 已撤除 ⇒ 完整性主张无损**；这是"生成物在被声明后又被重新生成"的固有现象。**下次生成时把 size 写 `n/a`** 已被本卡接受为后续改进项（本轮不改，避免为了美观再制造一次生成物变动）。此项**不阻塞**。

## 边界遵守声明

- 本节**只追加**；未回改任何冻结行、未回改 `review.md` 既有字节（含 reviewer §R）、未改任何 `C-条目` 与 `I09-E` 码、未重跑探针、未动原始证据。
- 生产三仓零写入、`<PLAN>\reviews` 零写入、未 commit；`handoff.json.status` 保持 **`review_pending`**（在 reviewer 改判前）。
- reviewer 的 **11 项未验证**原样承接（见 L236 的 `§U` 与 `handoff.json.unclosed_gaps`），**含**：oracle 只追加不可逐行核验（依赖复核侧副本，非独立第三方证明）、`after/git_status_after.txt` 旧内容**永久不可复验**、`C:\i09a` 是否曾写入、跨卷 `I09-E09`、`classify()` 未复核、attempt1 argv 未重放、`G2 × committed`、3.8 消费者侧、`E31` 补偿机制等。