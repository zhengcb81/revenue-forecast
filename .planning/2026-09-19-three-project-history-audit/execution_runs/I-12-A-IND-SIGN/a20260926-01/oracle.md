# I-12-A-IND-SIGN · 行业面会签 —— oracle（**先冻结**）

> 卡：`execution_v2/card_I-12-A.md`（sha `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` / 1,467 B）· attempt：`execution_runs/I-12-A-IND-SIGN/a20260926-01`（**新建**）· role：`industry_reviewer_i12a`
> 任务：`I-12-A` 行业面会签（卡文 Owner 条款的**行业半边**；统计面由 `98869ea8` **并行在飞**）
> 被审对象：`execution_runs/I-12-A/a20260926-01/`（`accepted_scoped`，STOP① `BLOCKED_PROFESSIONAL_DECISION` 仍在）—— **三件 + 全目录只读**
> 冻结时间：**2026-09-26 20:5x（本地戳 `2026-09-26T20:51:04+01:00` 门 0 之后、任何签署产物之前）**
> 写入面（唯一）：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-12-A-IND-SIGN/a20260926-01/`

---

## §0 冻结声明（本文件先于一切签署产物；时序可证）

1. **oracle 先冻结**：本文件写入 → 回读 → 计 sha → 才开始写 `ind_signatures.json` / `ruling_ind_sign.md` / `handoff.json`；本文件 sha 记入 `handoff.json.written_files`。
2. **门 0 先于本文件**：写+回读+删除自探 + 封盘/store 只读复哈希 + 7 件回源 sha 实测，原始输出逐字在 §7（本文件冻结前完成）。
3. **测试集结果保持封存**：本工位**未读**任何测试集/回测/准确性结果（含 `I-10-B`、`I-13`、`I-12` 任何 accuracy 面、`verification.json` 结果面）；回源面**严格限定**于派单清单：`I-12-A/a20260926-01` 五件（`oracle.md`/`evaluation_design.json`/`professional_approval.json`/`design_manifest.json`/`handoff.json`）+ 卡文 + `OWNER_DECISIONS §三十七`。**未**回读上游 `I-07-E/calibration_validation_summary.md`（可能含验证数值面 ⇒ 本面一律转引、不独立复核，见 §4 残余）。
4. **不代统计面签**：本工位只裁**行业面**（口径 / 分部 / 业务定义 / 公司池 / baseline / cluster-block 单位）；统计面 6 项阈值（时间切分、样本量/功效/CI 宽度、置信水平、重抽样次数与种子、多重比较校正、成功失败阈值）**逐项 `deferred_to_statistics`**，本面**不签、不改、不填值**。
5. **fail-closed**：证据不足 ⇒ `NOT_SIGNED`；不因 `I-12-B` 被堵、不因并行统计面在飞、不因「看起来合理」而放宽。
6. **零放行 / 零状态变更 / 零 ACCEPT**：不放行任何参数、不触发任何自动动作、不改 `I-12-A` 任何字节、不改任何卡 `status`/`decision`/`decision_sha256`、不产生 `ACCEPT`、**不派 `I-12-B`**。
7. 封盘 `I-11-A/hypotheses.json` `sha=f2178768…` **零字节**（51,697 B 实测一致）；store `hypotheses_v3.json` `sha=b2063ac8…` 零改动（门 0 + 收尾各复哈希一次，§7/§8）。
8. 禁五份计划文件 · 禁 `.planning` 外写 · 禁 git（含 `git status`）· 禁联网。

---

## §1 卡文判据（逐字；Owner 行 + STOP 路径）

**卡头（`execution_v2/card_I-12-A.md` L3/L5，逐字）**：`I-12-A · 专业冻结评估设计`；「Parent：I-12；状态：planned；**Owner：统计reviewer和行业reviewer共同签字**；依赖：I-07-E。」

**前提（L9 逐字）**：「上游证据资格/版本边界可用；无需等待完整I-07或I-10准确性结果。」

**动作（L13-L16 逐字）**：
1. 「逐项填写evaluation_design_fields，未定项标PENDING，不由弱模型选择方便通过的阈值。」
2. 「选择primary endpoint、baseline、权重、样本最小数量/功效、成对比较、cluster/block方法、CI和多重比较校正。」
3. 「严格区分真实历史vintage与重建实验；低/高情景没有概率标签就只评情景包含率。」
4. 「将设计、reviewer身份、签署、版本和SHA256冻结；测试集结果在此之前保持封存。」

**停止（L20-L21 逐字）**：
- 「任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。」
- 「已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。」

**验收（L23 逐字）**：「evaluation_design_fields全部完成或有获批not_applicable；SHA256冻结在结果解封前。」

**授权（`OWNER_DECISIONS.md §三十七` L852-L871）**：「给你授权所有的沙箱操作，不要再问我了」（L855「一切沙箱提权操作，owner 一次性常设授权，无需逐次审批」）；边界（L860-L862）「授权 ≠ 免除纪律」「纪律 16/17/18/19/20 全部继续有效」「产品仓提交（`git add/commit/push`）不在本授权内」。
> **本工位使用面 = 零提权**（全部动作 = 本 attempt 目录普通文件写入）；**该授权是沙箱操作授权，不是专业签署本身**；签署资格来自卡文 Owner 行的「行业reviewer」半边 + 编排层派单指派（本工位）。

---

## §2 回源 sha 清单（门 0 只读实测，2026-09-26 20:51 UTC+01）

| # | 路径（相对 plan root） | bytes | sha256 | 状态 |
|---|---|---|---|---|
| 1 | `execution_v2/card_I-12-A.md` | 1,467 | `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` | ✅ 与 I-12-A 冻结值一致 |
| 2 | `execution_runs/I-12-A/a20260926-01/oracle.md` | 16,649 | `08723ab0f62c07cbf0f9a7563b8fc6382bff41da8a3f7c72ab14b81cfc7e76ee` | ✅ 与 design_manifest 一致 |
| 3 | `…/evidence/I-12-A/evaluation_design.json` | 22,317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` | ✅ 与 design_manifest 一致 |
| 4 | `…/evidence/I-12-A/professional_approval.json` | 5,334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` | ✅ 全 `unsigned`（签署状态面） |
| 5 | `…/evidence/I-12-A/design_manifest.json` | 5,618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` | ✅ 与 handoff 一致 |
| 6 | `execution_runs/I-12-A/a20260926-01/handoff.json` | 16,285 | `7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714` | ✅ 落定 `accepted_scoped`（STOP① 仍在） |
| 7 | `OWNER_DECISIONS.md` | 109,029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` | ✅ 与 I-12-A 冻结值一致 |
| 8 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | ✅ 零字节 |
| 9 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61,231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | ✅ 零改动 |

**STOP 现状（冻结事实）**：`professional_approval.json` 两 reviewer 全 `signed=false`、`signature_status=unsigned`、6 项关键统计选项/阈值全 `PENDING`（L57-L64）、`status=BLOCKED_PROFESSIONAL_DECISION`（L96）；`design_manifest.unseal_gate.currently_satisfied=false`（L22）。本面**登记不解除**。

---

## §3 行业面签署项清单（本 oracle 冻结的裁定对象，17 项）

**归属规则（互补不重叠）**：
- **行业面（本工位裁）** = 口径 / 分部 / 业务定义边界 / 公司池 / baseline / cluster-block 单位 —— 对齐 `professional_approval.json` `industry_reviewer.scope_of_signature`（L38-L43：字段 3、字段 8+not_applicable、字段 11 cluster/block、字段 12 共同）+ 派单点名的 `vintage_class` 硬分（字段 4）、分部口径（字段 2/6）、业务定义边界（字段 4/6/9）。
- **统计面（`98869ea8` 并行裁，本面 6 项逐项 `deferred_to_statistics`，不得代签）** = 字段 5 时间切分 · 字段 10 样本量/功效/CI 宽度 · 字段 11 置信水平 · 字段 11 重抽样次数与种子 · 字段 11 多重比较校正 · 字段 12 成功/失败阈值（**重叠项**：行业半签须待统计面出值后回签，早于解封）。
- **不属签署对象**（`requires_professional_signature=false` 的结构字段 1/2/4/7/9/13 中，除派单点名者外）：只登记不签，不虚增 `signed_count`。

| id | field | 行业面裁定对象 | 预期形态 |
|---|---|---|---|
| `IND-01` | 4 | `vintage_class` 硬分：primary 只准 `true_vintage`；重建只进 sensitivity；primary 出现重建观测 ⇒ 判失败 | SIGNED |
| `IND-02` | 4 | 信息截点：`available_at<=origin` 硬约束；披露日缺失 ⇒ 不入池（fail-closed） | SIGNED |
| `IND-03` | 2 | 分部口径与重复权重：合并=Σ四分部对外销售；合并/分部不同时入误差池；entity 内 segment 等权 | SIGNED |
| `IND-04` | 6 | gross/net：统一对外销售收入（net of internal，E5 抵销）；含内部交易不作收入基期 | SIGNED |
| `IND-05` | 6 | 实际值 = 首次披露（as-originally-reported）；重述仅 secondary 且须 origin 时点可得 | SIGNED |
| `IND-06` | 6 | 财年对齐 / 分部重组不回溯 / 并购断点后新 series（业务定义边界） | SIGNED |
| `IND-07` | 6 | 跨币种绝对误差展示（origin 前可得汇率来源） | **NOT_SIGNED**（证据不足，fail-closed） |
| `IND-08` | 3 | 公司池纳入/排除理由与分层结构（A/H/US、行业、生命周期、可得披露条件） | SIGNED（层内 n 充分性归字段 10） |
| `IND-09` | 8 | 朴素 baseline 主/次选择 +「季节性同季」`not_applicable` 行业面获批 | SIGNED |
| `IND-10` | 9 | `low/high` = 情景非统计区间 ⇒ 只评情景包含率 + 区间宽度；禁置信覆盖措辞 | SIGNED |
| `IND-11` | 11 | 行业相关 cluster/block 单位：cluster=entity、block=origin（阈值项除外） | SIGNED |
| `DEF-01` | 5 | 时间划分折数/切点/窗口长度 | `deferred_to_statistics` |
| `DEF-02` | 10 | 最小公司数/每层样本数/功效/可接受 CI 宽度 | `deferred_to_statistics` |
| `DEF-03` | 11 | 置信水平（CI level/α） | `deferred_to_statistics` |
| `DEF-04` | 11 | 重复抽样次数与随机种子 | `deferred_to_statistics` |
| `DEF-05` | 11 | 多重比较校正方法 | `deferred_to_statistics` |
| `DEF-06` | 12 | 成功/失败阈值（经济显著改善幅度、可接受偏差、情景包含率、区间宽度）——**与统计面重叠** | `deferred_to_statistics`（**行业半签未完成**） |

> 预期 `signed_count = 10`、`NOT_SIGNED = 1`、`deferred_to_statistics = 6`；`industry_countersign_complete` 见 §5 判定式（存在未签行业项 ⇒ 必须 `false`，fail-closed）。

---

## §4 判据（校验器 `_verify_ind_sign.ps1` 冻结为 K1-K5）+ 残余

| id | 不变量 |
|---|---|
| `K1_release_lock` | `handoff`：`role=industry_reviewer_i12a`、`releases_nothing=true`、`statistics_sign_still_needed=true`、`git_diff_non_planning=0`、`params_released=false`/`params_released_count=0`、`produces_accept!=true`、`writes_outside_planning=0` |
| `K2_seal_discipline` | `handoff`+`ind_signatures`：`test_results_unsealed=false`、`test_results_sealed=true`、`accuracy_results_read=false`；`reads_forbidden_and_not_performed` 非空 |
| `K3_source_integrity` | `ind_signatures.source_hashes` 9 件逐件 sha256 复算比对（含封盘 `f2178768…`、store `b2063ac8…`、`I-12-A handoff 7bf747b1…`）；任一不符 ⇒ rc=3 |
| `K4_signature_discipline` | 每项 `ruling ∈ {SIGNED, NOT_SIGNED, deferred_to_statistics}`；SIGNED ⇒ 六要素齐全（选择/依据(file+line)/反例/兼容影响/恢复规则/被拒方案）+ `decision_sha256 == sha256(decision_payload)`；非 SIGNED ⇒ `decision_sha256 == "NOT_SIGNED"`；`belongs_to_statistical_six=true` 的项**禁** `SIGNED`（行业不代签统计面）；`signed_count == count(SIGNED)`；`signed_by` 恒为 `industry_reviewer_i12a`；`industry_countersign_complete == (全部 industry_face 项均 SIGNED)` 的计算值 |
| `K5_write_boundary` | `handoff.written_files`/`changed_paths` 全部位于 `execution_runs/I-12-A-IND-SIGN/a20260926-01/` 之内（对 `I-12-A` 只读：其 5 件 sha 由 K3 复算锁定）；无 `ACCEPT` |

**exit_code_legend（冻结）**：`0`=ALL_INVARIANTS_OK · `1`=harness 失败 · `2`=无裁决 · `3`=不变量违例（具名 K1..K5）。

**残余（不隐藏，随件移交）**：
1. 上游 `I-07-E/calibration_validation_summary.md` 的 §C4/E5 恒等式与「约 67%」为**转引**（`evaluation_design.json:L77/L169`），本面未独立复核（封存纪律 + 派单回源面未含该件）。
2. `IND-07`（跨币种绝对误差展示）无 origin 前可得可核汇率来源且禁网 ⇒ `NOT_SIGNED`；primary/secondary 路径只用无量纲指标，不因此阻断字段 6 其余裁定。
3. `DEF-06` 行业半签须统计面出值后**回签**（早于解封）；`design_manifest.unseal_gate` 需双签 + 新版本重冻 —— 本面不解除、不代签。
4. `OPEN-2` 红线：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 本面**只登记不消费**（登记值见 `evaluation_design.json:L307-L314`），不入任何裁定输入、阈值或分层。

---

## §5 签署形态（冻结）

- **`SIGNED`**：`choice`（具体口径选择）+ `rationale_refs`（`文件:行号` 至少 1 条卡文/被审件）+ `counterexample`（反例：不这样签会怎样坏）+ `compatibility_impact`（兼容影响，含与统计面 6 项的关系）+ `recovery_rule`（恢复/再签规则）+ `rejected_alternatives`（被拒方案 ≥1）+ `decision_payload`（单行、` || ` 分隔的上述浓缩串）+ `decision_sha256 = SHA256(UTF-8(decision_payload))`。
- **`NOT_SIGNED`**：证据不足 ⇒ 必须给 `not_signed_reason` + `recovery_rule`（补什么证据可再签）；`decision_sha256` 字面 `"NOT_SIGNED"`（**不许**给签署哈希冒充已签）。
- **`deferred_to_statistics`**：非本面管辖（统计面 6 项）；`decision_sha256` 字面 `"NOT_SIGNED"`；`overlap_with_industry_face` 标注（`DEF-06=true`，其余 `false`）。
- **`industry_countersign_complete` 判定式（fail-closed）**：`true` ⇔ 存在任一 `industry_face=true` 且 `ruling != SIGNED` 的项时必须为 `false`；本轮 `IND-07`（NOT_SIGNED）与 `DEF-06`（行业半签未完成）均未签 ⇒ **`false`**。
- **签署人**：每项 `signed_by = industry_reviewer_i12a`；**任何项不得 `signed_by = statistical_*`**（不代统计面签）。

---

## §6 变异清单（红绿双向 ≥3；本 oracle 冻结 5 红 + 1 绿，在 `_mut/Rx/` 副本执行，原件字节不动）

| id | 变异（仅 `_mut/Rx/` 副本） | 期望 rc | 击杀判据 |
|---|---|---|---|
| `GREEN` | 原件（`oracle.md`+`ind_signatures.json`+`handoff.json`） | **0** | K1-K5 全 OK |
| `R1` | `handoff.json` `statistics_sign_still_needed` true→false（模拟谎称统计面已签/停止①已清） | 3 | K1 |
| `R2` | `ind_signatures.json` `IND-01.decision_payload` 改 1 个字符（sha 不改，模拟签署载荷被篡改） | 3 | K4 |
| `R3` | `ind_signatures.json` `DEF-06.ruling` `deferred_to_statistics`→`SIGNED` 且 `decision_sha256` 伪造（模拟行业面代签统计阈值） | 3 | K4 |
| `R4` | `ind_signatures.json` `source_hashes` 中 `professional_approval.json` sha 改 1 个 hex 位（模拟回源指纹不符/被审件被改） | 3 | K3 |
| `R5` | `handoff.json` `industry_countersign_complete` false→true（模拟掩盖未签项、谎报会签完成） | 3 | K4 |

红臂原始输出逐字存 `_mut/Rx/verifier_output.txt`；`I-12-A` 三件与原件字节在变异前后复哈希不变。

---

## §7 门 0 自探原始输出（逐字，2026-09-26T20:51:04+01:00）

```
=== GATE0 BEGIN (I-12-A-IND-SIGN/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-A-IND-SIGN\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-A-IND-SIGN a20260926-01 write-readback-delete 2026-09-26T20:51:04.8607142+01:00
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
sealed_bytes=51697
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
store_matches_b2063ac8=True
store_bytes=61231
--- step6 source sha (read-only) ---
execution_v2\card_I-12-A.md	1467	a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f
execution_runs\I-12-A\a20260926-01\oracle.md	16649	08723ab0f62c07cbf0f9a7563b8fc6382bff41da8a3f7c72ab14b81cfc7e76ee
execution_runs\I-12-A\a20260926-01\evidence\I-12-A\evaluation_design.json	22317	203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0
execution_runs\I-12-A\a20260926-01\evidence\I-12-A\professional_approval.json	5334	0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1
execution_runs\I-12-A\a20260926-01\evidence\I-12-A\design_manifest.json	5618	ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178
execution_runs\I-12-A\a20260926-01\handoff.json	16285	7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714
OWNER_DECISIONS.md	109029	17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d
=== GATE0 END ===
```

---

## §8 边界自宣（本面不做什么）

不代统计面签（6 项逐项 `deferred_to_statistics`）· 不读任何测试集/准确性结果（封存）· 不改 `I-12-A` 目录任一字节（收尾复哈希 §2 表 8 件）· 不放行参数（`params_released=false`、计数 0）· 不产生 `ACCEPT`、不改任何卡 `status`/`decision`/`decision_sha256` · 不解除 STOP①（只登记行业半边签署事实与未签残余）· 不派 `I-12-B` · 封盘 `f2178768…` 零字节 · store `b2063ac8…` 零改动 · 不写五份计划文件 · 不写 `.planning` 之外（`git_diff_non_planning=0` 由写入面枚举推导）· 禁 git（含 `git status`，本面零 git 调用）· 禁联网 · fail-closed（证据不足 ⇒ `NOT_SIGNED`）。
