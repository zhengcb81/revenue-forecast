# 函 B —— 签字信任域（D1/D2/D3、D5、D6、D7、I09A-1…6、全文 W/T/L）请他方裁决

**收件方**（按项分属不同方，请各自作答）：

| 项 | 主题 | 待裁方 |
|---|---|---|
| **T2-9 / OPEN-D1** | 权威信任根位置（repo 配置文件 / 机器级只读路径 / OS keystore） | **跨仓双方**（安全/运维提选项，项目 owner 择定） |
| **T2-9 / OPEN-D2** | 谁可持 L3 私钥；一人可否多钥；是否强制双人控制 | **跨仓双方**（项目 owner 政策决定） |
| **T2-9 / OPEN-D3** | 撤销是否**追溯**使已发布工件失效（设计默认：否） | **跨仓双方** + **独立安全 reviewer 二次校验** |
| **T2-11 / OPEN-D5** | 消费者降级开关 `require_attestation=False` 是否保留、谁可授权、是否留痕 | **cross-repo（invest-core 消费 owner 与 revenue publication owner 联合）** |
| **T2-10 / OPEN-D6** | 谁落项目侧 3.8 消费门（`invest_contracts.py:1116`、`:1131-1132`） | **跨仓双方**（授权**开跨仓卡**落地 R-LEGACY-1 与 E29） |
| **T2-8 / T2-15 / OPEN-D7** | 三个数值 `W`（发布窗口）`T`（provider 超时上限）`L`（provider stdout 上限） | **跨仓双方 + 安全域** |
| **T2-13 / OPEN-I09A-1…6** | 见 §4 | **跨仓双方**（⑥须 **I-08-A owner 写入上游文本**） |

**授权依据**：`OWNER_DECISIONS.md` §13 **T2-8 / T2-9 / T2-10 / T2-11 / T2-13 / T2-15**。
**上游卡**：`execution_v2/card_I-08-A.md`、`card_I-08-B.md`、`card_I-08-C.md`、`card_I-09-A.md`、`card_I-09-B.md`。
**证据目录**：`execution_runs/I-08-A|I-08-B|I-09-A|I-09-B/a20260919-01/`。

---

## 0. 三条**已成立**的前提（请勿重复推翻，但可指出其不足）

这三条是**设计已冻结、且有实测证据**的，请在其之上裁决剩余项。

**(P1) 默认零可信签名者。**
`I-08-B` 实测：**未签状态 = 合法零可信签名者**（legal zero trusted signers）。
`I-08-A` 的 OPEN-D1 未定 ⇒ 该默认**至今未变**。请知悉：这意味着当前系统
**不存在可用于生产验证的信任根**。

**(P2) 已发布工件**不被撤销**追溯**失效——这是**设计默认**，**尚未裁定**（见 §2 D3）。
实测：`I-08-B` 只实现了该默认，并明确记录 "Only the design default … is implemented; NOT adjudicated"。

**(P3) 3.8 旁路缺口仍然 OPEN，且**不得**报为「已关」。**
`I-08-B` 原文：

> "`is_legacy_exempt()` is exported in-repo only; **the bypass gap remains OPEN and is NOT
> reported as closed**."
>
> "Until that card exists the 3.8 all-gates bypass stays open and **must NOT be reported as closed**."

⇒ 若贵方在裁决前看到任何「3.8 已关」的表述，那是**越权陈述**，请据 P3 驳回。

---

## 1. OPEN-D7 —— `W` / `T` / `L` 三数值（**最高优先，因为它把系统卡在拒服务状态**）

### 1.1 当前行为（实测，非设计意图）

`I-08-B` 原文记录：

> "OPEN-D7 W/T/L — parameterised only; **T or L unset means the provider call is REFUSED**,
> **W unset means no upper bound is enforced and `W_enforced=false`**. **No numeric value was invented.**"

⇒ 也就是说：**今天**在默认配置下，provider 调用被**拒绝**（T/L 未设），
而发布窗口**没有上界**（W 未设）。这是一个**双向不安全**的默认：
一边拒绝服务，一边无界。

### 1.2 卡的原始立场（请务必尊重）

`OWNER_DECISIONS.md` §13 **T2-8 / T2-15** 明文：

> 授权启动；**裁决前任何人不得把具体秒数/字节数写成规范值**。

且 `I-08-A` 记录：

> "the three numeric parameters have **no supporting evidence**" ——
> `W`（E18）/ `T`（E07）/ `L`（E06）；
> 其中 `L` 的早期硬编码 `65536` **已在 r3 撤回**（withdrawn）。

### 1.3 请贵方裁定（逐参数，须给证据基础）

对 `W`、`T`、`L` **各**回答：

1. **证据基础是什么**？绑在哪个 E 编号 / 哪次实测上？
   （`L` 尤其重要：`65536` 已被撤回，**不得复活**，除非给出新证据。）
2. **数值**是多少（秒 / 字节），以及**容差/边界语义**（闭区间？含等号？超限是拒绝还是截断？）。
3. **实现者需要补什么测量**才能支撑该数值？请给出测量方法（谁提供 evidence）。
4. **未设时的行为**应当是什么？当前「T/L 未设 ⇒ 拒绝调用」是**fail-closed**，
   请确认保留还是改为其他；「W 未设 ⇒ 无上界」是否可接受？

> **起草方不提供任何候选数值**。任何在此函内出现的具体数字都会违反 T2-8/T2-15 的
> 「裁决前不得写成规范值」，故本函**刻意留空**。

---

## 2. OPEN-D1 / D2 / D3 —— **必须一批裁**（reviewer 明确要求）

`I-08-A` 的 open question 原文（注意最后一条约束）：

> "**BATCHING CONSTRAINT (review recommendation)**: D1/D2/D3 should be adjudicated **in one batch**
> because together they fix **issuer naming, rotation and revocation semantics**; deciding them
> separately would make **I-08-B rework** the trust domain."

⇒ 请**同一批**给出 D1/D2/D3 三项的裁定，不要分批。

### 2.1 OPEN-D1 权威信任根

三个候选（原文）：
1. **repo 配置文件**
2. **机器级只读路径**
3. **OS keystore**

`I-08-A` 记录的分工：**"project owner decides, security/ops propose the options."**
⇒ 请**安全/运维**给出选项的**理由与反例**，请**项目 owner**（跨仓双方）**择定**。

请一并回答：
- 信任根的**权威副本**在哪，副本如何同步，**冲突时谁赢**？
- 信任根**缺失**时的行为（见 §3 的「法律零信任」未决项）。
- 与 **I-09-A 的 registry row** 的 attestation anchor 如何合并（见 §4 I09A-3）。

### 2.2 OPEN-D2 私钥持有与双人控制

- 谁可持 **L3 私钥**？
- **一人可否持多钥**？若可，多钥如何区分同一人的多次行为？
- **强制双人控制**（dual control）是**必须**还是**可选**？若必须，签名流程是两段式还是双子签？
- ⚠️ 实测边界：`I-08-B` 只用了 **ephemeral in-process test keys**（进程内临时测试钥），
  **从未**触及真实私钥托管。请贵方在裁定中明确：**测试钥的资格不得外推**到生产。

### 2.3 OPEN-D3 撤销的追溯性

- 设计默认：**撤销不追溯**（只阻止**未来**发布）。请确认、或替换。
- 若**改为追溯**：已发布工件的处理规则是什么（标记？删除？置为 `revoked`？），
  已下游消费的工件怎么办？
- **恢复规则**：撤销后能否**恢复**信任？谁能恢复？
- ⚠️ **本项须独立安全 reviewer 二次校验**（card 原文：`plus an independent security
  reviewer's second check`）。起草方**不**代替该二次校验。

---

## 3. OPEN-D5 / D6 —— 消费者侧的降级与旁路

### 3.1 OPEN-D5 降级开关（跨仓双方联合）

实测位置（**未修改**）：`invest_contracts.py:1070-1071` 的
`require_attestation=False` 消费者降级开关。

请裁定：
1. **保留还是删除**？
2. 若保留，**谁可授权**降级？是否需**双人**？
3. **是否必须留痕**（若留痕，落在哪、字段是什么）？
4. 降级期间产生的工件，**事后**如何被识别为「在降级下产生」？

> `I-08-A` 原文分工：**"invest-core consumer owner jointly with revenue publication owner."**
> ⇒ 本项**须两方联署**，单方裁定无效。

### 3.2 OPEN-D6 谁落 3.8 消费门（跨仓双方 + 授权开卡）

**规则已冻结**：`decision.md` §6.3 的 **R-LEGACY-1 + E29**。
**但实现它需要改跨仓消费者** `invest_contracts.py:1116-1127`，**本卡范围之外**。

`OWNER_DECISIONS.md` §13 **T2-10** 已授权：**「授权**开跨仓卡**落地 R-LEGACY-1 与 E29」**。
⇒ 请贵方裁定：
1. **谁**落这道门（哪一方作为实现者）？
2. **卡开在哪**（哪个仓的 planning 根）？
3. **门的确切位置**（`:1116` 与 `:1131-1132` 两处是否都要改，还是只改其一）？

**在开卡完成之前**，请全体**继续**按 P3 报告：**3.8 旁路缺口 OPEN，不得报「已关」**。
这是 `I-09-A` OPEN-I09A-5 已经指出的同类问题（见 §4）。

---

## 4. OPEN-I09A-1…6（跨仓双方；⑥须 I-08-A owner 写入上游文本）

| 项 | 内容（原文摘要） | 请回答 |
|---|---|---|
| **I09A-1** | `package_target` 语义（**逻辑名 vs 路径**）与其对 **OPEN-D4** 的耦合——决定收据 schema bump 是否**改变历史身份** | 语义选哪个？schema bump 是否改变历史身份？ |
| **I09A-2** | **由 -1 派生**：同一请求发布到**两个不同目录**算一次还是两次发布？ | 一次还是两次？判据是什么？ |
| **I09A-3** | 谁定 **member role-name 列表**；`I-08-B` 须加的 **attestation anchor** 如何合入**单次 registry-row schema bump** | 谁定列表？anchor 合入规则？（**约束**：anchor 须与 registry row 同一次 schema bump） |
| **I09A-4** | `REVENUE_PUBLICATION_REGISTRY` 指向**目录**时被**静默重解释**为目录根，append **成功写入嵌套同名文件**（本 attempt 实测） | 该静默行为**保留**（并文档化）还是**改为拒绝**？ |
| **I09A-5** | **依赖验收冲突**：调度声明 `I-00-A`/`I-00-B`/`I-08-A` 为 `accepted_scoped`，但其自身工件记录为 `review_pending` | 以哪个为权威？如何更正？ |
| **I09A-6** | （review 发现 **E-3** 新提）`I-08-A` §7 的 **ORDER 必须改**：冻结的上游顺序是 `validate -> sign -> registry append -> write output (+ roll back the r…` | **⑥ 须由 I-08-A owner 写入上游文本**：新顺序是什么？回滚范围是什么？ |

> **⑥ 的硬要求**：`OWNER_DECISIONS.md` §13 T2-13 明文——
> ⑥ 须附 **「孤儿成员五条规则 + E31 四段式重述」**。
> 请 I-08-A owner 在写入上游文本时**同时附上**这两件，不得省略。

---

## 5. 两份**设计上未决**的项（reviewer 请一并表态或明确记为长期未决）

`I-08-A` 记录了两条 "**UNRESOLVED-BY-DESIGN**"：

1. **attestation anchor 的确切字段名与兼容策略**（要追加到 registry 行上的那个锚）。
2. **当 `host_signed` 工件的 attestation 记录**因**信任域文件缺失**而**无法验证**时，
   消费者应当怎么做？（原文："legal zero-trust"）
   - 选项 α：**保留** `host_signed` 并附一条 `legacy_read_only` 式注记；
   - 选项 β：**拒绝**。
   （原文此处被截断："or reject; decide…"）

请**明确择定**，或明确写「维持未决，且其后遗症是 X」。

---

## 6. 回执要求

- **落点**：各卡自己的载体（`decision.md` / `review.md` / `handoff.json` / 新建 `rulings_*.md`），
  **不在本函上签字**。
- 每项须含：**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**。
- `W`/`T`/`L` 三数值：请**附证据出处**，且**不得**复活已撤回的 `65536`。
- D1/D2/D3：**必须同批**出。
- D5：**须 invest-core 消费 owner 与 revenue publication owner 联署**。
- D6：请明确**开卡方与卡位置**；开卡前继续报告「3.8 旁路 OPEN」。
- 完成后通知编排层，由其在本目录 `RESPONSES.md` 登记一行，**不改一字裁决内容**。

---

## 7. 本函的自证（起草动作）

| 项 | 值 |
|---|---|
| 起草人 | 编排层（owner 执行人，**非**收件方、**非**签署者） |
| 授权依据 | `OWNER_DECISIONS.md` §13 **T2-8 / T2-9 / T2-10 / T2-11 / T2-13 / T2-15** |
| 引用前像 | `I-08-A/a20260919-01/handoff.json`（`status = review_pending`，`reviewer_status` 记「已出 `accepted_scoped`，仅限设计/契约提议，**不**把 status 置为 accepted」）；`I-08-B/a20260919-01/handoff.json`（`status = accepted_scoped`） |
| 本函写入了什么 | 仅新增本 `outward_requests/` 目录下的文件；**未修改**任何载体、产品源码、门、数值 |
| 不产生 | 任何裁定、任何签名、任何 `status` 变化 |
| **刻意留空** | `W`/`T`/`L` 的具体数值（T2-8 / T2-15 禁止裁决前写成规范值） |

> **另请注意（与本函相关、但不属本函）**：`I-08-A` 的 reviewer **明文要求**
> 「I-08-A 已被接受」**不得**写入任何载体 ⇒ I-08-A 的收口方式须**单独商定**，
> 不可走常规 `handoff.status` 路径。这**不**影响本函各项的裁决。

---

## 更新（2026-09-22，追加式更新段）

> **性质**：本节系 2026-09-22 更新 pass（`OWNER_DECISIONS.md` §十八 C「更新函件」）在原函**之后追加**；原函正文逐字节未动（前缀证明见本目录 `_provenance.json` 的 `updates_2026_09_22`）。以下事实全部取自本计划记录并逐条注明出处；本节**不新增、不删改任何待裁项**。

### 一、与本函相关的新增佐证（截至 2026-09-22）

1. **I-08-C 安全三项（REM-01/02/03 = attestation 消费侧绑定 + receipt 弃用 + base_revenue 对账绑定）已在隔离树修复并获接受**：
- 修复卡 B1（`execution_runs/B1-I08C-product-fixes/a20260921-01/`）在隔离副本完成，复审 = `accepted_with_conditions`（登记册 §十四【状态刷新·Round 2】「已修复于隔离副本」表，行 REM-01/02/03）；
- 其条件项 REM-40…44 已全部关闭、二轮复审 = `accepted_scoped`（登记册 §二十八）；`OWNER_DECISIONS.md` §十七 B-1 前置状态记「REM-40…44 已关、二轮 accepted、落定齐」；
- 晋升已获 owner 批准（§十八「B: 全批」，含 §十七 B-1），按 `promotion_batch_manifest.md`（`6759d1eb…`）行 B-1 执行；执行卡 `PROMOTION-EXEC` 已派（登记册 §三十三）。
2. **B3 卡（I-05-C 交付面修复）已接受、其晋升亦已批准**——独立复审 = ACCEPT（全部 9 项声明经独立重跑证实，登记册 §十），卡状态 `accepted_scoped`（晋升清单 B-2 块）；晋升经 §十八「B: 全批」批准（清单行 B-2，REM-49 注释修复随批）。
3. **invest-core 消费者侧守卫补丁：已存在、已接受、未合入**：
- `OWNER_DECISIONS.md` §十六 E-3：已立卡（invest-core 消费者卡），**补丁+红绿在隔离副本，合入待该仓 owner**；
- INVEST-CORE 卡复审 = `accepted_scoped`（接受 = 补丁+冻结证明包），**合入明确不受理**（authority = invest-core owner）（卡复审记录，`findings.md` L630）；
- 登记册 §十八【状态刷新·Round 11】「待外部」：「INVEST-CORE 合入 = invest-core owner（+其测试设计卡欠账随行）」；
- 落地顺序按 `OWNER_DECISIONS.md` §十七 B-8 **原话照录**：「INVEST 补丁合入=invest-core owner；**落地序 锚+B1→补丁、永设绕过旗标**；合入前测试设计卡欠账已登记」——起草方不作解释性改写，其方向与语义请以贵方裁定为准。
4. **信任根文件仍实测缺席**——B1-F5 完整性复验对四生产锚的核验两处记「**trust 缺**」（登记册 §二十二·补1 的 F5 与边界行）；本计划记录中未见任何已建信任根的证据，与本函 P1「默认零可信签名者」的设计默认一致。至于因信任域文件缺失而无法验证时消费者应采 α（保留并附注记）还是 β（拒绝），仍是本函 §5 的待裁项，本节不预判。

### 二、对原函的影响

以上均为**佐证性状态更新**：第 1 条不改变 D1/D2/D3 必须同批与独立安全 reviewer 二次校验的要求；第 3 条**不改变** D5 须两方联署、D6 开卡前继续按 P3 报告「3.8 旁路 OPEN」的纪律；第 4 条不替代本函 §5 的两项择定。原函全部请求项（D7 三数值、D1/D2/D3、D5、D6、I09A-1…6、§5 两未决、§6 回执要求）**原样保留**。

**原函请求项不变，以上更新供贵方在裁定时一并知悉。**
