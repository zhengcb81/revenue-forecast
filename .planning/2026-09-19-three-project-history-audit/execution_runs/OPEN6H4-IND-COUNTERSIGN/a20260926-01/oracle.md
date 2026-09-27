# OPEN6H4-IND-COUNTERSIGN · `H4` 四要件补齐结果 —— 矿业行业面**会签 oracle（先冻结，后裁定）**

- 工位：`mining_industry_reviewer_h4`（矿业行业 reviewer，**非实现者、非代签会计面**）
- 卡：`I-11-A` · 会签对象（**全程只读**）：`execution_runs/OPEN6-H4-FOUR-REQ/a20260926-01/`
- 本载体（**新建**）：`.planning/2026-09-19-three-project-history-audit/execution_runs/OPEN6H4-IND-COUNTERSIGN/a20260926-01/`
- 写入面：`oracle.md`（本件，先冻结）· `ind_countersign.json` · `ruling_h4_ind.md` · `handoff.json`；**若四问判需补 `revert_rule` 豁免分支或锁口径** ⇒ 追加第五件 `hypotheses_h4_ind_v2.json`（`provenance.supersedes` 指向 v1），**不回改** `OPEN6-H4-FOUR-REQ` 任何字节
- 本文件是**判据冻结件**：先写本件 → 才允许判四问、才允许生成其余交付物。**冻结后不回改**（若必须改 ⇒ 整轮作废重跑）
- 纪律：**禁网** · **禁 git 写** · **禁用 `git status`** · `.planning` 之外**零写入**（`company-wiki` 的两份 PDF 仅**只读取文与哈希**，输出到管道/内存，不落盘）· 五份计划文件**不写** · 封盘 `I-11-A` 与 `OPEN6-H4-FOUR-REQ` **零字节改动**

---

## 0. 授权与定义（回源逐字；sha256 为本工位现算，不采信他人登记）

| # | 授权点 | 逐字原文 | 出处（本工位实测 sha） |
|---|---|---|---|
| A1 | **四要件定义** | 「审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`」 | `I11A-OPEN-ACCT/a20260924-01/ruling.md` **L226**，`f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2`（37,355 B） |
| A2 | **A-6.3 前置五条** | L248 观测量可复算；L249–L253 数值属 (i)–(iv) 之一；**L253 (iv)「专家假设：允许，但必须标 `expert_assumption` 并给出敏感性区间，永远不得被记为『等同披露依据』」**；L254 签署=非实现者；L255 追加式版本化 | 同上 **L248–L256** |
| A3 | **A-6.1 fail-closed** | 「二者缺一或状态为 `not_reviewed` ⇒ **fail-closed**：阈值不参与判定」／「`threshold_basis=professional_judgement_required` 且 `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**」 | 同上 **L230** |
| A4 | **BLOCKED-6a 分派** | 「BLOCKED-6a：3 条 `professional_judgement_required` 阈值的**数值**是否恰当……需行业/专业 reviewer 按 A-6.3 给出证据与签署」 | 同上 **L296** |
| A5 | **BLOCKED-6c 归属** | 「BLOCKED-6c：`threshold_review_status` 字段的**落地实现与校验器改动** —— 属 I-11-A 实现者/编排层与 schema 侧，我只给要求」 | 同上 **L298** |
| I1 | **H4 行业面给数** | 「**H4** ｜ 计划达成率 `[0.9, 1.1]` ｜ ✅ **采用**（矿业面给数）｜ **0.90 – 1.10**（±10%）｜ `professional_judgement`（本 reviewer，矿业面）」 | `I11A-OPEN-IND/a20260924-01/ruling.md` **L288**，`8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b`（39,207 B） |
| I2 | **放行条件（会签权来源）** | 「**放行条件**：本条仅为**行业面审定**；是否可标 `threshold_basis` 升级、以什么基础允许给数，**由 `I11A-OPEN-ACCT` 依其基础规则确认**，在此之前 I-11-B/I-11-C 不得据此触发。」 | 同文件 **L299** |
| I3 | **豁免分支要求（Q4 的直接来源）** | 「**反例**：新项目**爬坡年**、重大**并购并表年**、**不可抗力/长周期检修年**——这些结构性年份即使偏离 >10% 也不应判定『计划失真』。⇒ `revert_rule` 必须补一条**『爬坡/并表/不可抗力年豁免分支』**，否则阈值会在结构性年份误触发。」 | 同文件 **L298** |
| I4 | **阈值 ≠ 参数放行** | 「**注意这两个参数仍是 `_PLACEHOLDER`，阈值审定不等于参数放行**」 | 同文件 **L330** |
| I5 | **给数反例（不得为凑数）** | 「为『凑齐三条 pjr』而强行给 H2 一个数字（无口径、无基准 ⇒ 违反 fail-closed）」 | 同文件 **L345** |
| I6 | **BLOCKED-6 行** | 「**BLOCKED-6** ｜ OPEN-6：H2 单位收入阈值的**替代数值**（±5% 不采用）……**保持 `professional_judgement_required` 未审定**」 | 同文件 **L373** |
| M1 | **判例文本** | 「### 3.2 易误读点 (a)：行业面给了 **H4 = [0.90, 1.10]** —— 这等于该命题 `approved_frozen` 吗？」／「**结论：四要件 1/4 满足 ⇒ 不齐 ⇒ 按 ACCT L226 一律维持 `not_reviewed`**」 | `I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` **L275/L288**，`2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1`（49,062 B） |
| M2 | **合并工位对 H4 的开放清单** | 「OPEN-6：`threshold_review_status` 字段与校验器落地（BLOCKED-6c）；**H4 补齐四要件后由会计面确认**；H2 补 OPEN-2 口径 + 价格归一化基准；4 条恒等式容差对照表（BLOCKED-6b）」 | 同文件 **L330** |
| M3 | **C5 派单原文** | 「OPEN-6：threshold_review_status 落地 + **H4 四要件补齐** + H2 基准 + 恒等式容差对照表」 | `I11A-OPEN-MERGE/a20260924-01/handoff.json` **L122**，`b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878`（21,808 B） |
| H1 | **会签对象（会计面四要件结论）** | 「四要件 **4/4**」· `decision_sha256 = 9d2d38450d8fa8f1423a695628b6fbacf91eecc5b4796d3fa7fb621fd147e1c9`· 「**`threshold_review_status` 仍 `not_reviewed`**」 | `OPEN6-H4-FOUR-REQ/a20260926-01/h4_four_req.json`（`b11b905d28c389996d15903ee7f7ec1d8654a8c5b82bd19d37d34d4abd64a1ca`，13,722 B）L241/L242/L250 |
| H2 | **会计面给行业面的五项会签提请** | 「1. **口径必须先统一（最高优先）**……请明确 H4 用哪一张表、并在 `source_route` 中锁定；差异成因（口径桥）本工位未取证。2. 敏感性档位确认 3. `revert_rule` 的豁免分支……请在**新版本**中补 4. 计划值本身的口径 5. 会签落点」 | `OPEN6-H4-FOUR-REQ/a20260926-01/ruling_h4.md` **§⑧ L226–L230**，`acce9a38be1a98a2b394e44eb14770348bce03fb654476b676245ca1b78cbaef`（23,957 B） |
| H3 | **会计面自述的口径冲突（被裁对象）** | 「同一期、同一指标、两个披露口径给出相反结论（0.763635 在 `[0.9,1.1]` 之外、0.943588 在之内）；**差异成因我未取证**（未做口径桥），据实登记为**会签提请事项 #1**」 | 同文件 **L104** |

> **我 = 矿业行业面 reviewer（非实现者）**：不代签会计面、不代签任何实现者动作；`handoff.implementer_signed = false`。
> **本工位只做一件事**：对会计面 `H4` 四要件补齐结果做**行业面会签**，并裁**口径桥冲突**与**豁免分支**两件提请。**不放行任何参数、不解任何 `BLOCKED`、不触发任何动作。**

---

## 1. 冻结判据：四问 Q1–Q4（逐条可机检）

对「`H4` 行业面是否可会签」判定：**Q1–Q4 全部 `pass` ⇒ `countersigned = true`；任一 `blocked` ⇒ `countersigned = false` 并输出该问实测（此为合格交付）**。

### Q1 口径锚定 —— H4 应锚哪个披露口径（或两者都不可锚 ⇒ 换 observable）

**同时成立 ⇒ `pass`：**

1. **分母口径可由披露原件直接锁定**：存在披露原件把「计划值」与「同口径实际产量」**并列于同一张表**（或两年年报同表序列可交叉验证），且该表数值口径 = MD&A「矿山产铜 / 矿山产金」口径（**口径 B**）；
2. **分子两个候选口径各有原文逐字口径注文**（文件 + 行号 + 引文），不得靠推测；
3. **锁定后分子分母同口径**：比值可直接相除，**不需要任何未经披露的换算系数**；
4. **被拒口径的不可锚理由可量化复算**（该口径与公司自报的产量序列/计划序列**不衔接**，或在全部敏感性档下必然带外 ⇒ 对该阈值无判别力）；
5. **落为可执行 `caliber_lock`**：`source_route` 精确到表/行（主源 + 交叉校验源 + 舍入粒度），**写入本工位新版本**（追加式，`supersedes` 链；不回改封盘与 v1）。

**`blocked` 触发**：分母口径在原文无处可锁 / 锁定后仍需未披露换算 / 任一侧口径注文缺失 / 无法给出可执行 `caliber_lock`（⇒ 即「两者都不可锚、H4 须换 observable 但换不了」）。

### Q2 口径桥取证 —— 两口径差异能否取证

**同时成立 ⇒ `evidenced`：**

1. **规则层**：两表各自的口径说明均有原文逐字注文（A 侧表注、B 侧分矿山表「持有权益」列与「总计」行）；
2. **同基对照**：至少一条与「非控股剔除」**无关**的对照行在两表**数值完全相等** ⇒ 证明两表除该注文外同基；
3. **定量复算**：`差额 = 可识别（<50% 持股、权益法/参股）项合计 + 残差`；残差符号与规则一致，且 **残差 ≤ 原文未明细合计行（「其他矿山合计」）的大小**；
4. **覆盖率 ≥ 90%**（理由先冻结：披露只列「主要」矿山，明细桶不可拆 ⇒ 至多 10% 的差额允许归入未明细桶；超出即不可解释）；
5. **结论稳健**：以识别项调整后与锚口径原值，在**三档敏感性**下带内/带外判定**不翻转**。

**`blocked` 触发**：规则层无原文注文 / 无同基对照行 / 残差 > 未明细桶 / 覆盖率 < 90% / 残差导致带内带外翻转 ⇒ 该结论按 fail-closed 处理，`countersigned = false` 并给实测。

### Q3 会计面选择（`(iv) expert_assumption` + 敏感性 3 档）可否会签

**同时成立 ⇒ `pass`：**

1. **四类判定树本工位独立复跑**：`(i)/(iii)` 关键词检索在一手语料上**0 命中**（自测，不引用会计面结论作为证据）；`(ii)` 可配对期数 **< 2**（自测）⇒ 只剩 `(iv)`；
2. 记录含 `expert_assumption = true`、**三档敏感性**（主 `[0.9,1.1]` / 外 `[0.85,1.15]` / 内 `[0.95,1.05]`）、**各档后果**、`equivalent_to_disclosure_basis = false`；
3. **三档后果由本工位在锚口径基准样本上自测并登记**（哪一档在哪一金属上带内/带外），且**没有任何一档被设为默认可触发档**（`threshold_review_status` 仍 `not_reviewed` ⇒ A-6.1 门关闭）；
4. 该选择**不改** `threshold_basis`、**不放行**参数、**不升** status、**不构成**命题批准或 `I-11-B` ACCEPT；
5. 数值来源 = `IND L288/L296`（本方给数），**不存在** `IND L345`「为凑三条 pjr 强行给数」情形（H2 仍 `BLOCKED`，见 `IND L373`）。

**`blocked` 触发**：(iv) 被记为等同披露依据 / 缺任一敏感性档或缺后果 / 任一档被设为默认触发档 / 该选择被用于放行参数或升级 status / (i)(ii)(iii) 实为可取证却谎报不可用。

### Q4 `revert_rule` 豁免分支 —— 补不补、怎么补

**同时成立 ⇒ `pass`（结论应为「补，且按下述方式补」）：**

1. `IND L298` 逐字**确有**该要求；封盘与 `hypotheses_h4_v1.json` 的 `falsifier.revert_rule` 逐字**确无**该分支（两条回源）；
2. 原文中存在**真实**结构性年份实例（可引用交割日/并购/检修披露）⇒ 分支非纯假设；
3. 补法 = **追加式**：写入本工位新版本 `hypotheses_h4_ind_v2.json`（`provenance.supersedes_sha256` → v1），**不回改**封盘与 `OPEN6-H4-FOUR-REQ`；
4. 豁免**必须可核且有界**：①逐次引用原文交割/爬坡/检修披露作为触发证据；②由**披露原文**触发，**不得由 reviewer 自行主张**；③豁免年**不计入**「第二个可观测年度」的积累；④同一计划年度内**最多连续豁免 1 年**，其后年度一律按阈值判定；⑤每次豁免须登记 `exemption_log`，否则判 `blocked`。

**`blocked` 触发**：给出的豁免是**无条件/自证**的（⇒ 阈值永久失效，比不补更坏）/ 豁免写回封盘或 v1 / 触发证据不可核 / 无年度上限。

### 统一：`blocked` 触发条件（fail-closed，先冻结）

出现下列任一 ⇒ 判 **`blocked`**，输出 `countersigned = false` + 缺哪一问 + 实测证据（**该结果即为合格交付**），**不得放宽判据凑会签**：

- Q1–Q4 任一判据不满足；
- §2 的 preimage 两次复算不一致；
- 任一受审文件收尾 sha ≠ 开工 sha（只读纪律被破坏）；
- 写入面越界（`.planning` 之外出现新字节、五份计划文件被改、`OPEN6-H4-FOUR-REQ` 被改）；
- 本工位在判据冻结后放宽任一判据（一经发现整轮作废）。

---

## 2. 冻结：`decision_sha256` 求值方式（`decision-sha256/v1`，与两半区同形态）

```
preimage = utf8( json.dumps(pre, sort_keys=True, ensure_ascii=False, separators=(',',':')) )
decision_sha256 = sha256(preimage) 的小写十六进制
```

`pre` 的键集合（**先冻结；写入前不得增删改键名**）：

| 键 | 内容 |
|---|---|
| `schema` | `"decision-sha256/v1"` |
| `role` | `"mining_industry_reviewer_h4"` |
| `carrier` | `"execution_runs/OPEN6H4-IND-COUNTERSIGN/a20260926-01"` |
| `action` | `"h4_industry_countersign"` |
| `authorized_by` | `{ind_l299: <IND L299 逐字>, ruling_h4_section_8: <会计面 §⑧ 逐字>, acct_l226: <ACCT L226 逐字>, c5: <merge handoff L122 逐字>}` |
| `scope` | `{hypothesis_id: "H-CN-ZIJIN-PLAN-04", threshold: "实际产量 ÷ 计划产量 ∈ [0.9, 1.1]", parameter_ids: [两个 `_PLACEHOLDER`]}` |
| `four_questions` | `{q1..q4: "pass"/"blocked"}`（按实测；任一 `blocked` ⇒ 该 sha **不写入**） |
| `caliber_anchor` | `"B"`（或实测 `"none"`） |
| `caliber_bridge_status` | `"evidenced"` / `"not_evidenced"` |
| `basis_class` | `"expert_assumption"` |
| `expert_assumption_marked` | `true` |
| `sensitivity_interval` | `{main:[0.9,1.1], outer:[0.85,1.15], inner:[0.95,1.05]}` |
| `equivalent_to_disclosure_basis` | `false` |
| `revert_exemption_added` | `true` / `false` |
| `supersedes_version_sha256` | `hypotheses_h4_v1.json` 的 sha（实测 `329a719b…`） |
| `new_version_file` | `"hypotheses_h4_ind_v2.json"`（若判不需新版本则 `null`） |
| `threshold_review_status_effective` | `"not_reviewed"` |
| `releases_nothing` | `true` |
| `signed_by` / `signed_at_utc` | `"mining_industry_reviewer_h4（矿业行业 reviewer，非实现者）"` / ISO-8601 Z |

- preimage 全文（canonical 字符串）逐字存入 `ind_countersign.json → decision_preimage_canonical`，任何人可重算。
- **复算两次**：写入新版本**前**一次、写入**后**重新提取 preimage 再算一次，两次与写入 JSON 的值必须逐字符相同。

---

## 3. 冻结：`threshold_review_status` 与各 `BLOCKED` 的处置（先裁定，后执行）

| # | 判据（先冻结） | 结论 |
|---|---|---|
| 3.1 | 本工位能否把 `threshold_review_status` 升为 `reviewed` | **不能**。派单明令「不升 `reviewed`」（升 reviewed 需 schema 落地 + 编排层，`ACCT L298` 归属 BLOCKED-6c，不归本工位） |
| 3.2 | 会签通过是否 = 状态升级 | **不等同**。A-6.3（L246）是必要条件句式；会签只解除「被强制维持」的一部分，状态升级是 schema 落地后的**独立动作** |
| 3.3 | 本工位新版本写什么 | **显式写 `threshold_review_status = "not_reviewed"`**（追加字段、fail-closed） |
| 3.4 | 机器后果 | A-6.1 触发门**两侧保持关闭**；`releases_nothing = true`；无 falsifier 触发、无情景切换、无校准边界、无 I-11-C 反方检验 |
| 3.5 | `BLOCKED-6a` | **不解除**（H4 一份额之外仍有 H2/H8，见 `IND L373` / `ACCT L296`） |
| 3.6 | `BLOCKED-6b` / `6c` / `OPEN-6` | **一律 untouched**（不改校验器、不落地 schema、不改容差表、不产生 `I-11-B` ACCEPT） |

---

## 4. 冻结：取证与复算方法

1. **一手语料**（sha 由本工位现算）：`CN-ZIJIN-2025.txt` 抽取件（`196f2c54…`，763,644 B）；FY2025 年报 PDF（`01819e1c…`，79,925,886 B）；FY2024 年报 PDF（`004f733e…`，32,100,114 B，`company-wiki/…/annual/`，**只读**）；封盘 `hypotheses.json`（`f2178768…`）；会计面五件；两半区三份 ruling。
2. **不采信转述**：涉及「计划值 / 实际值 / 口径注文 / 差额」的数字，一律由本工位从原文**自己重算**并登记行号与命令结果；会计面 `single_period_probe` 是**被复核对象**，不是依据。
3. **口径桥复算**：逐行解析两表 → 自行加总校验「总计」行 → 按持股比例筛出 <50% 项 → 算差额、识别项、残差、覆盖率 → 三档带内/带外复算。
4. **PDF 取证**：`pdftotext -f N -l N -enc UTF-8 [-layout] <pdf> -` **输出到管道**（不落盘、不改字节）；`Get-FileHash -Algorithm SHA256`。
5. **变异测试脚本**以 stdin 内联执行（`python -X utf8 -B -`，**不落盘**）。
6. **JSON 写后 `json.load` 重解析**；UTF-8 **无 BOM**；**LF**（CR 计数 = 0）。
7. 收尾只跑 `git -c core.quotepath=false diff HEAD --name-only`（**禁用 `git status`**），非 `.planning` 条目须为 0。

---

## 5. 冻结：红 / 绿 / 变异清单

**绿（`rc = 0`）：**

| id | 案卷 | 期望 |
|---|---|---|
| **G1** | 本工位真实案卷（`ind_countersign.json` + `hypotheses_h4_ind_v2.json`）判四问 | `countersigned = true`，四问全 `pass`，`rc = 0` |

**红（`rc ≠ 0` = 被检出 = 判别力成立）：**

| id | 变异 / 分支 | 期望 |
|---|---|---|
| **B0** | **基线红分支**：对会计面 `hypotheses_h4_v1.json` **直接会签、不裁口径**（会签提请 #1 未处理，`caliber_lock` 缺失） | Q1 `blocked` ⇒ `countersigned = false`，`rc ≠ 0` |
| **B1** | **口径桥无证据**：去掉识别项，残差 > 原文未明细桶（模拟「差异成因未取证」） | Q2 `blocked`，`rc ≠ 0` |
| **B2** | **(iv) 选择越界**：`equivalent_to_disclosure_basis = true` 或敏感性三档缺内档 | Q3 `blocked`，`rc ≠ 0` |
| **B3** | **豁免无条件**：`revert_rule` 豁免分支写成「由 reviewer 酌情豁免」且无年度上限 | Q4 `blocked`，`rc ≠ 0` |
| **M1** | **判据改弱（方向性红）**：Q1 改成「任一口径可锚，无需与计划同口径」⇒ 喂入「锚口径 A、不锁 `source_route`」的记录 | 弱判据 `pass` ∧ 强判据 `blocked` ⇒ **检出**，`rc = 0` |
| **M2** | **判据改弱（方向性红）**：Q2 改成「两表注文不同即算已取证」（不复算差额）⇒ 喂入无差额复算的记录 | 弱判据 `pass` ∧ 强判据 `blocked` ⇒ **检出**，`rc = 0` |

- **红绿双向**：M1/M2 证明「判据被改弱后，一个不该通过的会签**必须能通过**」；B0–B3 证明「**判 `blocked` 的分支也要红**」。
- **`rc ≠ 0` 的含义**：该变异未被检出 = 判别力不足 = 不合格；总 `OVERALL rc = 0` 才是合格交付。

---

## 6. 范围边界（交付时逐条核对：不授予什么）

1. **不放行任何参数**：`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 维持 `_PLACEHOLDER`，`low/base/high` 维持 `null`（`IND L330`）。
2. **不升 `threshold_review_status`**（仍 `not_reviewed`）；**不解** `OPEN-6`；**不解除** `BLOCKED-6a/6b/6c` 任何一条。
3. **不触发任何 falsifier / 情景切换 / 校准边界 / I-11-C 反方检验**（`ACCT L230` + `IND L299`）。
4. **不改** `threshold_basis`（仍 `professional_judgement_required`）；**不产生 `I-11-B` 的 ACCEPT**；**不构成命题 `approved_frozen`**。
5. **不代签会计面**；**不声称 I-11-A 验收**；不写五份计划文件；不改 `OPEN6-TOLERANCE-*`、`I11A-OPEN-ACCT/IND/MERGE`、`OPEN6-H4-FOUR-REQ` 任一字节。
6. **零 git 写 · 零 `git status` · 零联网 · `.planning` 之外零写入**（`company-wiki` 两份 PDF 只读）。

---

## 7. 交付物之间的关系

```
oracle.md（本件：冻结 Q1–Q4 判据 + blocked 条件 + decision-sha256/v1 + status 处置 + 变异清单 + 边界）
   └── ind_countersign.json（四问逐条结论 + 证据 + 口径桥实测 + countersigned bool + preimage 两次求值）
         ├── hypotheses_h4_ind_v2.json（若判需补：caliber_lock + revert_rule 豁免分支，supersedes → v1）
         └── ruling_h4_ind.md（四问正文 + 与会计面 §⑧ 五项的衔接 + 红绿变异 rc + 不授予）
               └── handoff.json（role / authorized_by / countersigned / caliber_bridge_ruling / status 仍 not_reviewed / releases_nothing / written_files / git_diff_non_planning）
```
