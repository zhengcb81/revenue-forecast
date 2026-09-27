# I-12-A-STAT-SIGN · 统计面 6 项阈值裁定书（ruling）

> role：`statistics_reviewer_i12a`（统计 reviewer · **非实现者** · **非行业面**）· attempt：`execution_runs/I-12-A-STAT-SIGN/a20260926-01`
> 被审载体：`execution_runs/I-12-A/a20260926-01`（三件证据只读）· 卡：`execution_v2/card_I-12-A.md`（sha `a4d4b2dc…`）
> 判据来源：本目录 `oracle.md`（**先冻结**，17,839 B，sha256 `1c3ebb51f062dee1af30e2ec33f30b0fee38ed315404d9fe0b265b55f6303f2c`）§3 判据 C1-C7 · §5 逐项判定表 · §6 STOP 规则 · §7 变异清单
> 结论：**6 项 = 3 签署（S3/S4/S5）+ 3 拒签（S1/S2/S6）** ⇒ `signed_count=3`、`not_signed_count=3`；**STOP① `BLOCKED_PROFESSIONAL_DECISION` 仍未解除**（行业面未签 + 3 项无据）

---

## §1 逐项裁定（选择 · 数值 · 证据基础 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案）

### S1 — 字段 5 时间划分折数/切点/窗口长度 ⇒ **`NOT_SIGNED (insufficient_evidence)`**

- **实测缺什么**：① 回源面内已登记 origin 截点 = **每公司 1 个**（紫金 `2026-03-20`、微软 `2026-07-29`、小米 `null`，`as_of=2026-09-18`）—— `evaluation_design.json` **L124-L127**、上游 `I-07-E/calibration_validation_summary.md` **L15-L17**；② `I-11-C/**` 内 `available_at|vintage_class|published_at` 命中 = **0**（grep 计数实测）⇒ 无历史 vintage 清单；③ 单 origin ⇒ 滚动 origin **可算折数 = 0**（需 ≥2 origin/公司才成 1 折）。
- **理由**：面内无据 ⇒ 违 `C1_traceable` 与 `C2_result_independent`（任何折数都得靠猜），按 `C5` fail-closed 拒签；卡文动作 1 明禁"挑方便值"。
- **反例（已测）**：`M1` 把本项改成 `SIGNED` 并附伪造折数 ⇒ **rc=3，`K2_verdict_lock`**。
- **兼容影响**：字段 5 维持 `PENDING` ⇒ 验收不达成；与字段 4 `vintage_class` 硬分（L130-L134）一致（缺清单 ⇒ `unavailable` 不入池）；不影响已签 S3/S4（其守卫已按 cluster/block 不足降级）。
- **恢复规则**：面内登记每公司 ≥3 个历史 origin（`published_at`/`available_at` + 原文 sha256 + `vintage_class=true_vintage`）⇒ 重算折数/切点/滚动窗口 ⇒ 新开 design 版本、重冻 SHA256 后重签；解封后才补的切点一律作废为探索性（停止②）。
- **被拒绝的替代方案**：`按单 origin 定 1 折（全量作测试）`（无训练段，方便通过型）· `凭惯例填 5 折 / 70-30 切分`（面内零锚点，且切点与真实 `available_at` 不符即泄漏）· `解封后按结果回调切点`（停止②）。

### S2 — 字段 10 最小公司数/每层样本数/统计功效/可接受 CI 宽度 ⇒ **`NOT_SIGNED (insufficient_evidence)`**

- **实测缺什么（三件）**：① **可接受 CI 半宽的定标来源**：`execution_v2/**` + `OWNER_DECISIONS.md` 内 `经济显著|可接受偏差|统计功效|可接受CI` 共 **6 命中、全为字段定义原文、0 处数值定标**（`common_research_cards.md` L144/L146、`research_cards.json` L125/L127、`research_cards.md` L144/L146）；② **效应量/方差基础** = 封存结果面（`evaluation_design.json` **L8-L9** `test_results_sealed=true`、`accuracy_results_read=false`），本工位禁读；③ **每层 origin 数** 随 S1 同缺；上游事实：可评 entity = **2**（L111）、18 槽位 = 13 mapped + 5 declined（`I-07-E` L60）。
- **理由**：精度型缺定标、功效型缺方差 ⇒ 违 `C1`/`C2`；且明确**不得**以"当前只有 2 家"反推宽松阈值（`C5`）。
- **反例（已测）**：`M5` 改成 `SIGNED` 并编造宽松阈值（最小公司数=2）⇒ **rc=3，`K2_verdict_lock`**。
- **兼容影响**：字段 10 维持 `PENDING`；其不变量"样本不足 ⇒ 只描述、不宣称准确性优势"（L230）**已冻结、与本拒签无关地继续成立**；与 S3/S4 守卫同向 ⇒ 零放宽。
- **恢复规则**：三件齐备后一次性定数并新版本重签 —— ① 统计+行业共同给定每层可接受 CI 半宽 `w` 与置信水平（须先解 S6）；② 效应量/方差基础只能来自解封后由编排层明文授权的**训练段/历史面**（非测试集），或改走纯精度型回避方差；③ 每层 origin 数随 S1 到位。定数公式事前登记（比例精度型 `n >= z^2·p(1-p)/w^2`，`p=0.5` 最保守），解封后不得改。
- **被拒绝的替代方案**：`以 entity=2 定最小公司数=2`（反向适配数据）· `沿用 EA-1 行业带（量±10%/价±5%）当容差`（EA-1 明文"带形状=敏感性设计非精度主张"，`I-07-E` L66）· `给宽松半宽让样本量够用`（违 `C5`）· `从封存结果估方差`（违 `C2` + 停止②）。

### S3 — 字段 11 置信水平（CI level/α）⇒ **`SIGNED`**

- **数值**：`confidence_level = 0.95`、`alpha = 0.05`、`ci_form = two_sided`；**适用性守卫** `cluster_count >= 3 AND block_count >= 2`，否则该层记 `insufficient_for_ci` **只描述**；判定规则 = model vs baseline 成对差异的双侧 95% CI 不含 0（方向事前登记）且通过 S5 的 Holm 校正。**当前池 cluster=2、block=1 ⇒ 守卫必然触发 ⇒ 只描述。**
- **证据基础（回源）**：`evaluation_design.json` **L241-L245**（structure_frozen：成对同样本 / cluster=entity L79 / block=origin L243）、**L247**（`confidence_level = PENDING` 待签位置，统计面 scope `professional_approval` L24 覆盖）、**L111 + L124-L127**（守卫输入：entity=2、每公司 origin=1）；`research_cards.json` **L159**「CI 或显著性方法按冻结设计」、**L126**（字段 11 原文）。
- **理由**：该值是面内**显式委托**给统计面的选择（`C4`），数值与数据/结果无关（`C2`），并把"当前算不出"写成守卫而非放宽（`C5/C6`）。
- **`decision_sha256` = `12e0ea07cca59111e5a61c4f4403ecf3efa84f7874adc2b35f3c636ec45fac51`**（写入前算 = 写入后回读复算，逐位相等）
- **反例（已测）**：`M2` 退回 `NOT_SIGNED`（拒签本可签）⇒ **rc=3，`K2_verdict_lock`**；`M3` 把 `alpha` 改 0.50 **并同步重算 hash** ⇒ **rc=3，`K3_value_lock`（唯一失败项，K7 hash 通过 ⇒ 证明值锁独立生效）**。
- **兼容影响**：不改字段状态、不解封、不放行、不产生 `ACCEPT`；守卫与 field 7 `thin_stratum_rule`（L184）、field 10 不变量（L230）同向；STOP① 因行业面与 S1/S2/S6 未签仍成立。
- **恢复规则**：解封前改 α/CI 形式 ⇒ 新版本 + 重冻 SHA256 后重签；解封后改 ⇒ 停止②，该次评估作废为探索性。守卫解除仅当面内登记 `cluster>=3 且 block>=2` 的 vintage 清单（依赖 S1 恢复）。
- **被拒绝的替代方案**：`90% CI`（确认性过宽，违 `C5`）· `99% CI`（无面内依据，且与 S5 FWER α 需另配，引入不一致）· `单侧不登记方向`（结果后挑方向，停止②物种）· `只报点估计不给 CI`（违卡文动作 2 与 `research_cards` L159）· `n=2 也给区间`（伪造精度）。

### S4 — 字段 11 重复抽样次数与随机种子 ⇒ **`SIGNED`**

- **数值**：`repetitions = 10000`；`seed = 2765402844`（派生式 `hex(SHA256(card_I-12-A.md)[0:8]) = a4d4b2dc → 2765402844`，**事前由卡文指纹派生、与结果无关、不可事后择优**）；方案 = 按 `cluster=entity`、`block=origin` 的成对重抽样；**守卫同 S3**（不足 ⇒ 不执行重抽样、记 `insufficient_for_resampling`、只描述）；复现性 = 同 design + 同参数 + 同 seed ⇒ 逐位一致（`evaluation_design` **L286**），PRNG 实现随 manifest 登记。
- **证据基础（回源）**：`evaluation_design.json` **L248-L249**（两项 `PENDING`；L249 逐字「实现者不擅自固定一个『刚好好看』的种子」= 事后择优种子被明文禁止，故须事前由本面固定）、**L243-L244**（block=origin、按 origin 分块重抽样）、**L286**（rerun_rules）；`card_I-12-A.md` **L14** + sha `a4d4b2dc…`（seed 派生指纹，§1#1）；`research_cards.json` **L126**。
- **理由**：`C4` 面内显式留给统计面；`C2` 数值不依赖结果（B 与 seed 均事前可定）；B=10,000 使 95% 双侧分位的 Monte-Carlo 索引标准差 ≈ `sqrt(10000×0.025×0.975) ≈ 15.6`（相对 ≈0.16%），相对确认性下限 `B>=2,000` 留 5 倍余量。
- **`decision_sha256` = `2367b078911467bd75650c152a9caefcab22e22d9980c7c2626aa95f0730b12d`**（写前 = 写后复算相等）
- **反例（已测）**：`M7` 改 `repetitions=100` 并同步重算 hash ⇒ **rc=3，`K3_value_lock`（唯一失败项）**。
- **兼容影响**：只增可复现性与守卫；当前 cluster/block 不足 ⇒ 重抽样根本不执行，与"只描述"同向；不解封、不放行、不解除 STOP①。
- **恢复规则**：解封前改 B/seed ⇒ 新版本 + 重冻后重签；解封后改 seed ⇒ 停止②（择优种子即证据污染），作废为探索性；PRNG 未登记或复算不逐位一致 ⇒ 该次运行判不可复现、结果作废为探索性。
- **被拒绝的替代方案**：`B=1,000`（分位 MC 索引标准差 ≈0.5%，端点抖动可见）· `B=100`（≈1.6%，不可信）· `用当前时间/系统随机源当 seed`（不可复现，违 L286）· `解封后择好看 seed`（面内明禁 L249 + 停止②）· `n=2 仍强行重抽样`（退化取值，伪造精度）。

### S5 — 字段 11 多重比较校正方法 ⇒ **`SIGNED`**

- **数值**：`method = holm`、`error_control = FWER`、`alpha = 0.05`（与 S3 同源）；**family** = 解封前在 `design_manifest` 登记的全部确认性成对检验（model vs baseline × entity 层 × 指标 × horizon 层），`m` 事前固定；**BH-FDR 仅限显式标注 exploratory 的附录**，不得用于任何确认性成功主张；family 增删/事后换方法 ⇒ 新版本 + 重冻，解封后变更 ⇒ 停止②。
- **证据基础（回源）**：`evaluation_design.json` **L250** 逐字「候选：Holm FWER / BH FDR，**二选一由统计 reviewer 定**」（= 面内逐字委托）、**L246 + L252**（待签位置 + 结果后补阈值 = 停止②）；`professional_approval.json` **L24**（统计面 scope 含多重比较校正）；`card_I-12-A.md` **L14**；`research_cards.json` **L126**。
- **理由**：`C4` 完全成立（逐字委托）；本评估要出的是"确认性成功"判定 ⇒ 必须控 FWER；Holm 在任意依赖结构下有效且严格优于 Bonferroni；α 与 S3 一致避免两套 α；family 事前登记防事后挑族（`C3` 反例已测）。
- **`decision_sha256` = `7ab9bfa5f765dae29d54ae503c07fe22fc270231657cf809df0b0b6bac8ede4c`**（写前 = 写后复算相等）
- **反例（已测）**：`M8` 改 `method=bh_fdr`（用于确认性主张）并同步重算 hash ⇒ **rc=3，`K3_value_lock`（唯一失败项）**。
- **兼容影响**：与 S3 互洽（同一 α）；不解封、不放行；family 事前登记与 I-12-A `design_manifest` 冻结流程兼容（签署齐备后须新版本重冻）；不解除 STOP①。
- **恢复规则**：解封前换方法/改 α/改 family ⇒ 新版本 + 重冻后重签；解封后变更 ⇒ 停止②，作废为探索性；family 内缺登记的检验不得作确认性宣称（fail-closed）。
- **被拒绝的替代方案**：`BH-FDR q=0.05`（控 FDR，确认性语境允许错误发现逃逸）· `Bonferroni`（被 Holm 严格支配）· `不校正`（多模型/多指标下第一类错误膨胀）· `解封后定 family/换方法`（L252 明禁）· `secondary 指标一律做确认性检验`（以指标数量刷显著；未登记即只描述）。

### S6 — 字段 12 成功/失败阈值（经济显著改善幅度 / 可接受偏差 / 情景包含率 / 区间宽度）⇒ **`NOT_SIGNED (insufficient_evidence)`**

- **实测缺什么（三件）**：① **经济显著改善幅度**面内 **0 处数值定标**（同 D6 反向检索：6 命中全为字段定义原文）；② **可接受偏差/包含率/区间宽度**唯一可用行业带 EA-1 明文「**带形状=敏感性设计非精度主张**」（`I-07-E` **L66**）不得挪用；情景带无名义概率（`evaluation_design` **L215-L216**、`research_cards` **L164**）⇒ 只能谈情景包含率、但仍无"可接受包含率"来源；③ **行业 reviewer 共同签署缺位**（`professional_approval.json` **L33-L43** `signed=false`）⇒ 单签违 `C4`。
- **理由**：`C1`（无据）+ `C4`（须共签）双重不成立，且这是卡文明文"由统计与行业reviewer签字"的唯一一项 ⇒ **fail-closed 拒签，不为解锁而签**。
- **反例（已测）**：`M6` 改成 `SIGNED` 并编造阈值（Skill>+5% / bias<=10% / containment>=0.8）⇒ **rc=3，`K2_verdict_lock`**；`M4` 把 `industry_countersign_still_needed` 改 false（模拟代行业签、解除 STOP①）⇒ **rc=3，`K6_boundary_lock`**。
- **兼容影响**：字段 12 维持 `PENDING` ⇒ 验收不达成、停止① 成立；与 field 9「无名义概率只评情景包含率」不冲突（本拒签不写任何覆盖率阈值）；S3/S4/S5 已签项不失效，但整体不解封。
- **恢复规则**：① 行业 reviewer 先在面内给定经济显著改善幅度与可接受偏差/包含率/区间宽度的容差定标（若拟升格 EA-1 带为容差，须由 owner/行业面明文废止"非精度主张"限定，**本面不得代为升格**）；② 统计面复核其统计形态（事前可定性、与 S3/S5 α 族相容）后**共签**；③ 双签齐后新开版本重冻 SHA256；解封后补签一律作废为探索性（面内 L270 `anti_cherry_pick`）。
- **被拒绝的替代方案**：`用 EA-1 ±5%/±10% 当可接受偏差/区间宽度`（误用敏感性设计）· `统计面先签占位阈值（Skill>0 即成功）以解锁`（方向≠经济显著幅度，且缺共签）· `把情景包含率写成 80%/90% 覆盖率阈值`（面内明禁）· `等看到结果再定阈值`（停止②）· `由统计面代行业 reviewer 签`（Owner 行共同签字要求 + 派单禁代签）。

---

## §2 汇总

| item | 字段 | 裁定 | 数值 / 缺什么 | `decision_sha256`（写前=写后） |
|---|---|---|---|---|
| S1 | 5 | `NOT_SIGNED` | 缺 vintage 清单（实测 origin=1/公司、`available_at` 命中 0） | `null`（`refusal_sha256 a138debb…`） |
| S2 | 10 | `NOT_SIGNED` | 缺 容差定标（0 处）/ 效应量方差（封存）/ 每层 origin 数 | `null`（`refusal_sha256 ea0e6ac0…`） |
| S3 | 11 | **`SIGNED`** | 95% 双侧、α=0.05、守卫 cluster≥3∧block≥2 否则只描述 | `12e0ea07cca59111e5a61c4f4403ecf3efa84f7874adc2b35f3c636ec45fac51` |
| S4 | 11 | **`SIGNED`** | B=10,000、seed=2765402844（= `a4d4b2dc` 派生）、同守卫 | `2367b078911467bd75650c152a9caefcab22e22d9980c7c2626aa95f0730b12d` |
| S5 | 11 | **`SIGNED`** | Holm、FWER、α=0.05、family 事前登记、BH 仅 exploratory | `7ab9bfa5f765dae29d54ae503c07fe22fc270231657cf809df0b0b6bac8ede4c` |
| S6 | 12 | `NOT_SIGNED` | 缺 经济显著定标（0 处）/ 容差来源（EA-1 禁挪用）/ 行业共签 | `null`（`refusal_sha256 8b99a715…`） |

`signed_count = 3` · `not_signed_count = 3` · **`industry_countersign_still_needed = true`** · **`releases_nothing = true`** · STOP① `BLOCKED_PROFESSIONAL_DECISION` **仍成立**（卡文停止①：任一关键统计选项/阈值未签署）。

**hash 复算登记（C7）**：6 项 `decision_payload_canonical` 的 sha256 **写入 `stat_signatures.json` 之前**算一次、**写入后从文件回读再算一次**，两次与文件内登记值三方逐位相等（`ALL_HASH_MATCH=True`，见 `handoff.json.decision_sha256_recheck`）。

---

## §3 红绿变异（oracle §7 冻结 + 追加臂；原件字节不动）

**exit legend（冻结）**：`0=ALL_CRITERIA_OK` · `1=harness 失败` · `2=无裁决` · `3=判据违例（具名 K1..K8）`

| 臂 | 变异（仅 `_mut/Mx/stat_signatures.json` 副本） | 期望 rc | 实测 rc | 首个具名违例 |
|---|---|---|---|---|
| `GREEN` | 原件副本 | **0** | **0** | — （K1-K8 全 OK） |
| `M1` 红·**签了不该签** | `S1` `NOT_SIGNED`→`SIGNED` + 伪造折数 | 3 | **3** | `K2_verdict_lock`（5 项违例） |
| `M2` 红·**拒签了本可签** | `S3` `SIGNED`→`NOT_SIGNED` | 3 | **3** | `K2_verdict_lock`（7 项违例） |
| `M3` 红·阈值事后篡改 | `S3.alpha` 0.05→0.50 **并同步重算 hash** | 3 | **3** | `K3_value_lock`（**唯一**违例；K7 hash 通过） |
| `M4` 红·越权代签/放行 | `industry_countersign_still_needed` true→false（2 处） | 3 | **3** | `K6_boundary_lock`（2 项违例） |
| `M5` 红·追加（签了不该签） | `S2` → `SIGNED` + 编造最小样本数 | 3 | **3** | `K2_verdict_lock` |
| `M6` 红·追加（签了不该签） | `S6` → `SIGNED` + 编造成功/失败阈值 | 3 | **3** | `K2_verdict_lock` |
| `M7` 红·追加（值篡改） | `S4.repetitions` 10000→100（hash 同步重算） | 3 | **3** | `K3_value_lock`（唯一违例） |
| `M8` 红·追加（方法篡改） | `S5.method` holm→bh_fdr（hash 同步重算） | 3 | **3** | `K3_value_lock`（唯一违例） |

- 追加臂 `M5-M8` 与 oracle §7 冻结方向**一致且更严**（只增不减，不放宽任何判据）；`M1/M2/M4` 与 `M3` 分别覆盖派单要求的"签了不该签 / 拒签了本可签 / 正例"三个必需方向。
- **原件完整性**：全部臂跑完后 `stat_signatures.json` sha256 仍 = `d4263357db5997353b22297d14b82f535f13c501452cf6281d45903a2a921c38`（`original_stat_signatures_unchanged=True`）。

**GREEN 臂原始输出（逐字）**：

```
=== GREEN (original bytes copy) ===
rc=0
CHECK K1_items_set OK
CHECK K2_verdict_lock OK
CHECK K3_value_lock OK
CHECK K4_signature_form OK
CHECK K5_result_seal OK
CHECK K6_boundary_lock OK
CHECK K7_hash_integrity OK
CHECK K8_open2_redline OK
RESULT ALL_CRITERIA_OK
```

**红臂原始输出（逐字首行）**：

```
M1 rc=3 first_fail=FAIL K2_verdict_lock : S1.selection=SIGNED != frozen NOT_SIGNED
M2 rc=3 first_fail=FAIL K2_verdict_lock : S3.selection=NOT_SIGNED != frozen SIGNED
M3 rc=3 first_fail=FAIL K3_value_lock : S3.alpha=0.5 != 0.05
M4 rc=3 first_fail=FAIL K6_boundary_lock : summary.industry_countersign_still_needed != true
M5 rc=3 first_fail=FAIL K2_verdict_lock : S2.selection=SIGNED != frozen NOT_SIGNED
M6 rc=3 first_fail=FAIL K2_verdict_lock : S6.selection=SIGNED != frozen NOT_SIGNED
M7 rc=3 first_fail=FAIL K3_value_lock : S4.repetitions=100 != 10000
M8 rc=3 first_fail=FAIL K3_value_lock : S5.method=bh_fdr != holm
original_stat_signatures_unchanged=True
```

> 完整逐字输出存 `_mut/GREEN|M1..M8/verifier_output.txt`（原件零改动；`_verify_signatures.ps1` 只读）。

---

## §4 边界与未做的事

**做了**：只读回源（§1 全部 file:line 可复算）· 6 项逐条裁定 · 3 项数值签署（写前/写后双复算 hash）· 3 项 fail-closed 拒签（附实测缺口）· 9 臂红绿变异（1 绿 + 8 红，rc 与期望全一致）· 封盘 `f2178768…` 零字节、store `b2063ac8…` 零改动（门 0 与收尾复哈希）。

**没做（明确声明）**：
- **没读任何测试集/回测/准确性结果**（封存令：`test_results_sealed=true`、`accuracy_results_read=false`；证据路径不含 `I-10-B`/`I-13`/accuracy 面，`K5_result_seal` 机器核验）。
- **没代行业 reviewer 签字**（`industry_countersign_still_needed=true`；字段 3/8/11 cluster-block/12 行业面仍 unsigned）。
- **没代实现者自签**、**没放行任何参数**（`params_released=false`、`releases_nothing=true`）、**没产生 `ACCEPT`**、**没改任何卡 `status`/`decision`/`decision_sha256`**。
- **没改 I-12-A 三件证据**（只读，收尾复哈希）、**没动封盘与 store**、**没写五份计划文件**、**没写 `.planning` 之外**（`git_diff_non_planning=0`）、**没调用 git（含 `git status`）**、**没联网**。
- **没解除 STOP①**：本签署不构成解封依据；解封仍需 行业面签署 + S1/S2/S6 补据或获批 `not_applicable` + 新版本重冻 SHA256 + 编排层明文解封。
- **没派 `I-12-B`**、**没消费 OPEN-2 禁消费值**（`K8_open2_redline` 机器核验：`stat_signatures.json` 内无 `124248`/`38175`/`consumed_for_forecast`）。
