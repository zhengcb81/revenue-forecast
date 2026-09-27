# oracle.md — I-11-B / a20260926-01（开工前冻结的独立预期 + 门 0 原始输出）

> **本文件在任何实质动作之前冻结**。写入面 = 仅 `execution_runs/I-11-B/a20260926-01/`。
> 本工位 = 实现者（`implementer_i11b`）：做卡文 `L11-L16` 四动作，**不自签、不放行参数、不触发任何 falsifier/自动动作、不派 I-11-C、不改任何封盘字节**。
> status 交付形态 = `review_pending`（验收留给独立复审 + 落定三件套）。

---

## 0. 门 0 自探（写+回读+删除三步留档，不采信父探针）

- 探针 #1（2026-09-26T17:14:22+01:00）：`Set-Content` 写 `_gate0_probe.txt` → `write ok=True` → `Get-Content` 回读到内容行 `gate0 probe I-11-B a20260926-01 2026-09-26T17:14:22.6845194+01:00` → `Remove-Item` 后 `gone=True`。
- 探针 #2（原始输出逐字转录，落档用）：

```
=== GATE0 BEGIN (I-11-B/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-11-B a20260926-01 write-readback-delete
--- step3 delete ---
deleted_gone=True
=== GATE0 END ===
```

**结论：`gate0_passed=true`（写 ✅ / 回读 ✅ / 删 ✅，均本会话自探，零提权、零破坏性替代）。**
三步均在本工位写入面内完成；探针文件已删除，未留残件。

---

## 1. 开工授权（逐字回源）

### 1.1 `OWNER_DECISIONS.md §三十四`（当轮新立，L745-L780）逐字依据

- 节标题：`## 三十四、【已裁定·第十八批】**I-11-B 开工门槛改判：「A」**（2026-09-26 15:4x，选项式问答原话）`
- 提问三选一（L750-L753）：**A** owner 明文改判开工门槛（以 `5✅+2❌` 现状开 `I-11-B`，C3/C5 残余列开工后并行欠账）／**B** 维持 7 条合取，磨到 7✅／**C** 折中：`6✅ + C5 待` 开工，C5 的 H4/6b 留作卡内 `expert_assumption` 标注
- **owner 选择（L754）：「A」**
- 执行映射（L757）：**「改判 I-11-B 的开工门槛 —— 以 MERGE 七条当前 5✅ + 2❌ 现状开工；i11b_unblocked 的语义从『7/7 才开』改为『owner 明文许可开工』。」**
- L758：**「C3/C5 的残余不丢、不隐藏 —— 列为 I-11-B 开工后的并行欠账，每项在卡内载体以 expert_assumption 或 unverified 形式登记」**；L759 `C3` 四项（① origin 字节 ✅ ② B2 晋升 ✅ ③ ACCT-R2 ✅（E1=BLOCKED-PARTIAL、S=S1、4 份语料降 E3）④ IND-r2 在跑）；L760 `C5`（`6c` ✅ · `H4` ⚠️ 口径桥残差 269t/534kg 闭合不了 · `6b` 路径 (c) 已执行（unquantified），整条 6b 是否转 accepted 按 `ruling_6b L110` 另判 · `H2` ✅ 交付但 still_blocked）
- L761-L766 开工卡硬约束：**oracle 先冻结**（含本条改判逐字依据 + `C3/C5` 残余清单 + `expert_assumption` 标注要求）／**不放行任何参数**（`low/base/high` 仍 null、`_PLACEHOLDER` 维持）／**不触发任何 falsifier/自动动作**（`ACCT L230` + `IND L299`）／**实现者不自签 · 独立复审 · 落定走三件套**／**每一条以 `expert_assumption` 承接的判断，必须给敏感性区间 + `equivalent_to_disclosure_basis=false`**（同 `H4` 的 `(iv)` 形态）
- L769-L775 边界：**不解除** `OPEN-2/3/5/6` 任何一条；**不解除** `BLOCKED-6a/6b/6c`、`BLOCKED-NEEDS-ORIGIN-BYTES`；**不放行参数**（两个 `_PLACEHOLDER` + MSFT 四参数 + 新两分部参数）；**不产生 ACCEPT**、**不改任何 status/decision/decision_sha256**（除非是新卡自己的写入面）；**不代签**；`i11b_reason` 里「两半 handoff 自述不解锁」仍有效，**本节是 owner 明文改判，优先级高于该自述**
- L777-L779 执行纪律：派工给足（七条现状含 sha · C3/C5 残余清单 · expert_assumption 模板 · 红绿双向变异 · fail-closed 残余不隐藏即红线）；**I-11-C 按依赖顺序另派，不在本节授权**

### 1.2 `i11b_unlock_conditions` 第 1 条原文（`execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` L117-L123）

> 「≥1 条命题在新版本上由非实现者 reviewer 写入 `decision.decision_sha256` 并达 `approved_frozen`（**或 owner 明文改判开工门槛**）」

⇒ **`§三十四` 即该逃生口的行使**（第 1 条的后半句）。该 handoff 自述 `i11b_unblocked=false`、`i11b_verdict=BLOCKED`（`i11b_reason`：两半自述不解锁）——按 §三十四 L775，**owner 明文改判优先于该自述**。
同一第 1 条的前半句路径（≥1 条 approved_frozen）事实上也已由 `I11A-HYP-APPROVE/a20260925-01` 满足（见 §2 C1），**双路径同时成立**。

### 1.3 `execution_v2/card_I-11-B.md` 卡文（逐字要点）

- L5：`Parent：I-11；状态：planned；Owner：行业/会计reviewer决策，弱模型执行已签规则；依赖：I-11-A、I-10-A。`
- L7-L9 前提：`I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。`
- L11-L16 动作：①按 contract arithmetic、历史经验或外部可比选择校准方法，保存选择依据与样本；缺数据就标 expert_assumption ②明确 low/base/high 值、单位、起止年份、原值→新值、转换公式；管理层目标不得用作独立准确性证据 ③用 dependency_control 列共享驱动及约束，检查同一事件是否同时在销量、价格、额外收入重复出现 ④按 qualitative_synthetic_example 手算复核实施机制，再执行真实已审定映射；不复制示例数字到真实公司
- L18-L20 停止：**幅度无来源又未明确分析师假设→STOP_CALIBRATION**；独立调高多个有关联 driver 导致不可能的联合情景→STOP_SCENARIO
- L23 验收：参数幅度、相关性及收入增量能够复核；**专业 reviewer 签署后方可进入 forecast，不等同准确性通过**

### 1.4 依赖两项（卡文 L5/L7-L9）回源复核

- **I-11-A accepted**：`execution_runs/I-11-A/a20260919-01/handoff.json` L317 `"status": "accepted_scoped"`（`e4dafd16…`/27,788 B；`qualification.json` `"state": "accepted_scoped"`）。**该 run 目录下仅此一个 attempt（已自探目录列表）**，即卡级最新 attempt。
  - ✅ **父勘误（2026-09-26，编排层对账后入册）**：派单原文称卡级最新为 `execution_runs/I-11-A/a20260922-02/handoff.json` 系**父侧误记**（把 `I-06-A` 的卡级最新误记到 `I-11-A`）。**勘误结论：I-11-A 唯一 attempt = `a20260919-01` / `accepted_scoped`**，即卡级最新；纪律 20 的意图（取卡级最新）由该 attempt 满足。本工位曾以 `unverified-D1` 登记该差异（未隐藏），父对账后按本勘误改记；判据本身不变。
- **I-10-A 披露适配已签**：`execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/handoff.json`：`c7_status=met`、`disclosure_adaptation_signed_count=4`、`decision_sha256=86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`、`status=signed_scoped`（该 handoff `188f49e9…`/21,107 B）。

---

## 2. MERGE 七条逐条现状（开工门槛实测依据；每条回源 + sha）

| 条 | 现状 | 回源（run/attempt + sha256 前 16 位 / 字节） | 关键字段实测 |
|---|---|---|---|
| **C1** | ✅ | `I11A-HYP-APPROVE/a20260925-01/handoff.json` `af4130bb6c67a8e6`/19,481；`hypotheses_v2.json` `32c22208573a71d5`/55,213 | `approved_frozen_count=1`（`H-CN-ZIJIN-SEG-01`，hypotheses_v2[0]）；`decision.decision_sha256=4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f`（写前/写后两次复算相同）；`c1_status` 自述第 1 条路径已满足 |
| **C2** | ✅ | `OPEN2-C2-REGISTRATION/a20260926-01/handoff.json` `ae67e2b9fda61942`/21,226；`hypotheses_v3.json` `b2063ac8533a96ba`/61,231 | `c2_branch2_discharged=true`（仅注册语义）；4 个新 `parameter_id`（`ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027`、`ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027`）已注册 model_cards + hypotheses_v3（`parameter_id_count=18`，零重复）；4 个新 id `low/base/high=null`、`released=false` |
| **C3** | ❌ | 见 §3 C3 残余清单 | origin 字节 ✅（62,953 B）；B2 晋升 ⚠️（派单 ✅ vs 磁盘 blocked，见 unverified-C3b）；ACCT-R2 ✅（`E1=BLOCKED-PARTIAL`/`S1`/4 语料降 E3）；IND-r2 在跑（目录空） |
| **C4** | ✅ | `OPEN5-S3-REACQUISITION/a20260925-01/handoff.json` `df5b368c26192499`/24,338；`OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/handoff.json` `88e12c72621da52d`/65,590；`OPEN5-S5-ACCT-GRADING/a20260926-01/handoff.json` `5609ac467c82de0b`/11,326；`OPEN5-S5-IND-RULING/a20260926-01/handoff.json` `b7fc61c5a2668f17`/17,248 | S3 `readability_result=readable`（5/5 锚词命中）；S4 `status=accepted_scoped`；S5 会计 `levels_graded`（GRADED）；S5 行业 `industry_face_status=PASS（四点全部裁定成立）`。**注意**：S4/S5 自述「参数放行、OPEN-5 解除、I-11-B ACCEPT 一概归有权方」——本卡不据此解除任何东西 |
| **C5** | ❌ | 见 §3 C5 残余清单 | 6c ✅（accepted_scoped）；H4 ⚠️（口径桥残差 269 吨/534 千克，countersigned=false）；6b 路径(c) 已执行退 `unquantified`；H2 交付但 `still_blocked` |
| **C6** | ✅ | `I11A-OPEN11-IND/a20260924-01/handoff.json` `69fcc785e45abd37`/8,703 | `cross_period_availability=available_verified_locally_two_consecutive_periods` |
| **C7** | ✅ | `I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/handoff.json` `188f49e98018b423`/21,107 | `c7_status=met`；`disclosure_adaptation_signed_count=4`；`decision_sha256=86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`；2 个 case（`MS-PBP-M05`/`MS-IC-M06`）为已签**不授予**判定（`STOP_DISCLOSURE_ADAPTATION`），不计入 4 |

**实测合计 = 5✅ + 2❌（C3/C5）——与 §三十四 现状一致。** 开工门槛按 §三十四 改判为「owner 明文许可开工」，**不等于 7/7**；`C3/C5` 未解、`OPEN-2/3/5/6` 未解、`BLOCKED-*` 一个未解。

---

## 3. C3 / C5 残余清单（红线：逐条登记，不隐藏、不当作已解）

### 3.1 C3 残余（OPEN-3 / BLOCKED-NEEDS-ORIGIN-BYTES 面）

| # | 项 | 派单口径 | 本卡登记形态 | 回源实测 |
|---|---|---|---|---|
| C3-① | origin 字节 | ✅ 62,953 B | `unverified→已核到字节层`（字节层 ✅；E1 等级仍 BLOCKED-PARTIAL） | `OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/handoff.json`：`origin_bytes_retrieved=62953`、`origin_bytes.bin` sha `cf84c29048ab314e…`、`status=BLOCKED-PARTIAL` |
| C3-② | B2 晋升 | ✅（本轮完成） | **父对账（2026-09-26）：晋升已完成**（本工位曾记 unverified-C3b，父对账后改记） | 父对账原文：本工位所读 `B2-PROMOTION/a20260926-01/handoff.json`（`status=blocked`、`promoted=false`、`MISSING`、`git_apply_rc=128`）写于**事故时刻**，属实；其后**父用提权按 §三十二 完成晋升**（`Copy-Item` 单步覆盖，非 `git apply`）：`dayu …/sec_downloader.py` = 74,543 B / `4684933e…`（== changes.diff 后像）、`cw …/dayu_cli_adapter.py` = 25,328 B / `32ef1165…`（== 后像）、`committed=false`、回滚源 `preimage/` 在位。产品仓不在本工位读面 ⇒ 该状态为**父证**（`verified_by_parent`），非本工位自证；handoff 的 MISSING 为事故时点旧值 |
| C3-③ | ACCT-R2 | ✅（已裁） | `unverified`（等级为 fail-closed 结果，非通过） | `OPEN-3-ACCT-R2/a20260926-01/handoff.json` `status=RULED`、`e1_level=BLOCKED-PARTIAL`、`s_level=S1`、`corpus_files_level=E3`（4 件降级、8 条引文作废）、`s_is_not_release: 参数一律不放行` |
| C3-④ | IND-r2 | 在跑 | `unverified`（在跑未归） | `execution_runs/OPEN-3-IND-R2/a20260926-01/` 目录存在但**空**（本会话实测零文件） |
| C3-⑤ | MSFT 六参数 / 新两分部参数 | —— | `unverified`（维持不放行） | `I11A-OPEN-MERGE` 两半裁定：`MSFT_PBP/IC/MPC_REVENUE_FY2027`、`MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027`、I-07-E 微软分部口径全部维持不放行；新两分部参数「取数目前只存在于外部来源，两条路都不得在当前状态放行」 |

### 3.2 C5 残余（OPEN-6 面）

| # | 项 | 派单口径 | 本卡登记形态 | 回源实测 |
|---|---|---|---|---|
| C5-① | 6c | ✅ accepted | `unverified`（accepted_scoped 带 2×P2 + 3×P3） | `BLOCKED6C-THRESHOLD-REVIEW-STATUS/a20260926-01/handoff.json` `status=accepted_scoped`、`status_scope` 严格限 iso+changes.diff 的证据与判据 |
| C5-② | H4 口径桥 | ⚠️ 残差闭合不了 | **`expert_assumption` 不适用 → 登记 `unverified`（fail-closed 保留）** | `OPEN6H4-IND-COUNTERSIGN/a20260926-01/handoff.json`：残差 269 吨（铜）/534 千克（金）未逐行闭合，金在内/外档翻转 ⇒ 冻结判据 Q2 fail-closed；`countersigned=false`；`blocked_summary` 明载；会签成立前不得升 `threshold_review_status`、不得触发任何动作 |
| C5-③ | 6b 路径(c) | 已执行（unquantified）；整条 6b 归 `ruling_6b L110` 另判 | `unverified`（整条 BLOCKED-6b 未解） | `OPEN6B-R2-REVERT-UNQUANTIFIED/a20260926-01/handoff.json`（`758aa03fdcbf94c2`/14,120）已按 revert_rule 退 `unquantified`；`OPEN6B-TOLERANCE-RULING/a20260926-01/ruling_6b.md` **L110 恢复规则**：「新建 `OPEN6B-TOLERANCE-RULING-R2`（附本裁 decision_sha256、证据链、作用域）追加裁定；R1/R3/R4 的签署值不受 R2 影响，但**整条 BLOCKED 的状态**由 owner/编排层在 R2 解决后重判；本文件与被审 attempt 一律不回改。」（L108：`signed_count=3`、`blocked_6b_status=still_blocked`，R2 `NOT_SIGNED`，实测 max\|Δ\|=154 千克） |
| C5-④ | H2 | 交付但 still_blocked | `unverified` | `OPEN6H2-ACCT-SIGNOFF/a20260926-01/handoff.json`（`7be2122a75de16c6`/15,919）：`conclusion=维持 still_blocked（不推进）；3 条 pjr 完成 A-6.3 全套 = 0/3`、`blocked_6a_status=still_blocked` |

**fail-closed 宣言**：以上每一项在本卡任何载体中**均不写成「已解」**；`expert_assumption` 只用于校准幅度的分析师判断（§5 模板），**不用于冲销任何 BLOCKED**。

---

## 4. `STOP_CALIBRATION` / `STOP_SCENARIO` 判据（冻结）

- **STOP_CALIBRATION**（卡文 L20）：任一参数的**幅度**既无可核来源（contract arithmetic / 历史经验 / 外部可比）**又**未被明确标注为分析师假设（`expert_assumption` + 敏感性区间 + `equivalent_to_disclosure_basis=false`）⇒ 该参数**不得出数**，卡判 `blocked`，**不为推进链放宽**。
- **STOP_SCENARIO**（卡文 L21）：独立调高多个有关联 driver ⇒ 产生不可能的联合情景（例如同一事件在销量、价格、额外收入三处重复计增量）⇒ 停止并判 `blocked`。
- 判定位置：`calibration_plan.json`（逐参数 `stop_evaluation`）+ `revert_or_stop.json`（总判定与回滚规则）。

## 5. `expert_assumption` 标注模板（冻结；§三十四 L766「同 H4 的 (iv) 形态」）

每一条以 `expert_assumption` 承接的判断，**必须**同时具备：

```json
{
  "id": "EA-x",
  "assumption": "……（明确写出假设内容）",
  "basis": "……（为何只能靠分析师判断；缺口是什么）",
  "sensitivity_interval": {"low": "…", "base": "…", "high": "…", "unit": "…", "band_rationale": "…"},
  "equivalent_to_disclosure_basis": false,
  "carrier_form": "A-6.3 (iv) expert_assumption + 敏感性区间",
  "release_state": "not_released",
  "blocked_by_residuals": ["…"]
}
```

- 缺任一字段 ⇒ 该条不成立 ⇒ 对应参数触发 `STOP_CALIBRATION`。
- `equivalent_to_disclosure_basis=false` 为**常量**，禁止改写。
- 管理层目标**不得**用作独立准确性证据（卡文 L14；`calibration.management_target_is_not_independent=true` 恒成立）。

## 6. 红绿双向变异清单（冻结）

| 编号 | 变异 | 期望（红） | 期望（绿） |
|---|---|---|---|
| M1 | 删除某 `expert_assumption` 的 `sensitivity_interval` | 校验器 rc≠0（EA 模板缺件） | 原件 rc=0 |
| M2 | 把任一 `equivalent_to_disclosure_basis` 翻成 `true` | 校验器 rc≠0（常量被破坏） | 原件 rc=0 |
| M3 | 把任一 `released`/`params_released` 翻成 `true` | 校验器 rc≠0（违反「不放行参数」） | 原件 rc=0 |
| M4 | 把某参数 `low/base/high` 从 null 填成数值（模拟放行） | 校验器 rc≠0（store 侧 low/base/high 必须为 null） | 原件 rc=0 |
| M5 | 把 C3/C5 残余清单某项改成 `"resolved"` | 校验器 rc≠0（残余隐藏红线） | 原件 rc=0 |

（变异在**副本**上进行，原件字节不动；红绿 rc 记录进 `synthetic_mechanism_check.json` / `handoff.json`。）

## 7. 本 oracle 不做什么（边界自宣）

- 不产生 `ACCEPT`、不写 `decision`/`decision_sha256`、不代签任何面（行业/会计/外部方）。
- 不放行任何参数：`hypotheses*.json`、`model_cards*` 全部**只读**；不新建 hypotheses 版本（若确需 ⇒ `hypotheses_h4_v1.json` 形态 + `supersedes` + `modified_indices`，封盘原件零字节——本卡**不需要**）。
- 不触发任何 falsifier/自动动作（`ACCT ruling L230` + `IND ruling L299`）；不解 `OPEN-2/3/5/6`、不解任何 `BLOCKED-*`。
- 不派 `I-11-C`（依赖顺序另派）；不写五份计划文件；不写 `.planning` 之外；禁 git 写、禁 `git status`；不联网。
- 示例数字（`qualitative_synthetic_example` 的 2/8760/0.5/40/20/1200/264000/281520/299040 等）**只用于机制手算复核**，禁止进入真实公司任何字段。
