# I-12-B oracle（运行前冻结）· execution_runs/I-12-B/a20260926-01

> 卡：`execution_v2/card_I-12-B.md`（1,549 B / sha `f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b`）
> 冻结时间：2026-09-26T20:5x+01:00 · role：`implementer_i12b` · 本件先于任何证据写入冻结，冻结后不改。
> 性质：实现者工作记录；**不自签、不产生 ACCEPT、不改任何 status/decision/decision_sha256**。

---

## 1. 卡文逐字（唯一判据）

**卡头（L5）**：`Parent：I-12；状态：planned；Owner：数据整理执行者；独立证据reviewer验收；依赖：I-12-A。`

**前提（L9-L10）**：
- 冻结设计可读；仅按已批准数据来源获取方式执行。

**动作（L13-L16，逐字）**：
1. 按entity/segment/origin/horizon生成唯一sample_id，记录筛选与排除全量表。
2. 每个输入保留source版本/hash/available_at，逐条验证available_at<=origin；有疑义隔离，不能事后补当时不可得数据。
3. 真实vintage保留原预测；重建实验单独标reconstructed并记录全部假设，不可合并进真实vintage成绩。
4. 按冻结实际值政策处理重述、并购和分部重组；训练、调参、最终测试分组和时间切分必须可审计。

**停止（L19-L21，逐字）**：
- future leakage、重复sample或缺origin→STOP_DATASET。
- 分层样本不足→记录limited，不补选表现更好的公司。

**验收（L23）**：独立reviewer可从每个样本追到信息时点与实际值；缺失/排除计数守恒。

**证据（L25，逐字）**：`evidence/I-12-B/sample_manifest.jsonl`、`evidence/I-12-B/exclusions.jsonl`、`evidence/I-12-B/source_vintages.jsonl`、`evidence/I-12-B/actuals_policy_application.json`、`evidence/I-12-B/split_manifest.json`。

**共用规则逐字（common_research_cards.md L17-L23 / L289）**：
- 「所有evidence/<card_id>/路径相对于本轮新attempt_root；attempt_root由I-00-B绑定…每次尝试独立，禁止覆盖旧证据。」
- 「实际值封存规则：I-12-B的实际值由独立reviewer收集封存，预测执行者只见ID、hash与政策；I-12-C冻结预测manifest后才由该reviewer出具unblind_receipt解封。已见实际值或重建资料含无法排除的未来信息，一律标exploratory，不能伪装真实vintage或确认性盲测。」
- 研究卡原文动作 5/6（research_cards.json L550/L554）：「实际值内容由独立reviewer收集并封存；预测执行者此阶段只见sample_id、封存hash及政策，不见数值。若同人已见实际值，显式记录暴露并将实验降为exploratory，不能伪装盲测。」「重建资料若含未来信息且无法排除，保留exploratory标签、来源和局限，不进入真实vintage或确认性测试集。」

---

## 2. 上游冻结输入（本卡运行前实测 sha256；校验器逐件复算）

| # | 路径（相对计划根） | 字节 | sha256 |
|---|---|---|---|
| U1 | `execution_v2/card_I-12-B.md` | 1549 | `f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b` |
| U2 | `execution_v2/card_I-12-C.md` | 1604 | `49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91` |
| U3 | `execution_v2/research_cards.json` | 40058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` |
| U4 | `execution_v2/common_research_cards.md` | 14736 | `2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b` |
| U5 | `execution_v2/START_HERE.md` | 20436 | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` |
| U6 | `execution_v2/review_and_handoff.md` | 4005 | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| U7 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` |
| U8 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json` | 22317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` |
| U9 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json` | 5334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` |
| U10 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json` | 5618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` |
| U11 | `execution_runs/I-12-A/a20260926-01/handoff.json`（`accepted_scoped`，2026-09-26 20:4x） | 16285 | `7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714` |
| U12 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` |
| U13 | `execution_runs/I-07-E/a20260926-01/verification.json` | 10089 | `237bc2d394ec5726c05adc00f6b7de2b88e302aafe658300f64fbac5dd25671c` |
| U14 | `execution_runs/I-07-E/a20260926-01/handoff.json`（`accepted_scoped`） | 14267 | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` |
| U15 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json`（来源 sha/页码转录层） | 13863 | `3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf` |
| U16 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘，只读**） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| U17 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` |

**上游状态**：`I-12-A = accepted_scoped`（2026-09-26 20:4x，U11）；其 `professional_approval.json` 双签状态 = `statistical_reviewer/industry_reviewer 均 unsigned`，`design_manifest.unseal_gate.currently_satisfied=false`、`test_results_unsealed=false` ⇒ **本卡不解封任何测试实际值**（派单亦注明「统计/行业双签在飞」）。

---

## 3. 授权逐字

- **§三十四（OWNER_DECISIONS L745-L780）**：L762-L766 硬约束逐字「oracle 先冻结」「不放行任何参数」「不触发任何 falsifier/自动动作」「实现者不自签 · 独立复审 · 落定走三件套」「每一条以 expert_assumption 承接的判断，必须给敏感性区间 + equivalent_to_disclosure_basis=false」；L769-L775 边界逐字「不解除 OPEN-2/3/5/6 任何一条」「不放行参数（两个 _PLACEHOLDER + MSFT 四参数 + 新两分部参数）」「不产生 ACCEPT、不改任何 status/decision/decision_sha256（除非是新卡自己的写入面）」「不代签行业面 / 会计面 / 外部方」；L779「后继卡按卡文依赖顺序另派，不在本节一并授权」。
- **§三十七（L852-L871）**：授权原话「给你授权所有的沙箱操作，不要再问我了」；边界逐字「纪律 16/17/18/19/20 全部继续有效」「生产零未授权改动的纪律不变」「产品仓提交（git add/commit/push）不在本授权内」。本卡使用面 = 零提权（attempt 目录普通文件写入），**禁 git（含 `git status`）、禁联网**。
- **派单（编排层 2026-09-26）**：顺序 `I-12-B → I-12-C → I-12-D → I-12-E`；产出四件；每卡先冻结 oracle + 门 0 留档；红绿变异 ≥3；`handoff.json` 字段固定；不派 I-13/I-16/I-17。

---

## 4. 红线（只登记、不消费）

- `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE`：登记除法值 **124,248.63**（真值/公式商 **38,175.95**）；ban 原文「OPEN-2 前禁消费」（`REMEDIATION_REGISTER.md` L3951，转引上游 I-07-E §F）。
- 本卡处置：**registration_state = registered_not_consumed**；evidence 目录（`evidence/I-12-B/**`）**禁止出现这两个字面量**（校验器 J6 具名检查）；本 oracle 仅作登记。

---

## 5. 判据 J（校验器 `_verify.py` 逐条；全绿 rc=0，任一违例 rc=3，缺件/坏 JSON rc=1）

| id | 判据 |
|---|---|
| J1 | `sample_manifest.jsonl` 每行 `sample_id` = `SMP-<ENTITY>_<SEGCODE>_<ORIGINYYYYMMDD>_<HORIZON>` 且**全表唯一**；行数=7；`entity/segment/origin/horizon` 四键与 id 逐字一致。 |
| J2 | **计数守恒**：`entities_total(3)=included(2)+excluded(1)`；`candidate_rows(9)=included_rows(7)+excluded_rows(2)`；`included_rows = manifest 行数`；`excluded_rows = exclusions.jsonl 中 universe=row 的行数`。 |
| J3 | **available_at<=origin**：7 条 included 样本的 `available_at<=origin=true` 且样本级 `available_at_le_origin=true`；`available_at=null` 的来源（HK-XIAOMI-AR2025）必须 `state=quarantined_unavailable` 且不得被任何 included 样本引用；protocol 类输入必须带 `exemption_reason`。 |
| J4 | **vintage 分离**：included 样本 `vintage_class` 全为 `true_vintage`；`reconstructed` 计数=0；`reconstructed_mixed_into_true_vintage=false`。 |
| J5 | **封存/切分**：全部样本 `actual_value=null`、`scorable=false`；`target_period_actuals_seen=false`；`unseal_gate_currently_satisfied=false`；`split_manifest` 四集合计数全 0 且 `state=PENDING_unsigned`（设计字段 5 = PENDING）。 |
| J6 | **红线 + 放行 + 签署**：`evidence/I-12-B/**` 不含 `124248.63`/`124,248.63`/`38175.95`；`params_released=false`；`implementer_signed=false`；`open2_ban_observed=true`。 |
| J7 | **上游一致性**：§2 的 U1-U17 实测 sha 与 oracle 登记逐件一致（现场复算）。 |
| J8 | **封盘/store 零字节**：U16 sha=`f2178768…`（51,697 B）、U17 sha=`b2063ac8…`（61,231 B）。 |
| J9 | **handoff 形态**：`status=review_pending`、`gate0_passed=true`、`releases_nothing=true`、`git_diff_non_planning=0`、`written_files` 覆盖五件证据。 |

**rc 码表（本卡自描述 `exit_code_legend`）**：`0`=全部 J 通过；`1`=harness 失败（缺件/JSON 解析失败）；`2`=无裁决（本卡不使用）；`3`=具名 J 违例（负例被正确拒绝）。

---

## 6. 变异清单（红臂；在 `_mut/Mx` 副本上改，原件字节不动）

| id | 变异 | 期望 |
|---|---|---|
| M1 | 在 `sample_manifest.jsonl` 末尾追加一条重复 `sample_id` 行 | rc=3（J1） |
| M2 | 把某条 included 样本的 `available_at_le_origin` 改为 `false`（future leakage 形态） | rc=3（J3） |
| M3 | 从 `exclusions.jsonl` 删掉 `universe=row` 的一行（计数不守恒） | rc=3（J2） |
| M4 | 在 `actuals_policy_application.json` 写入红线字面量 `124248.63` | rc=3（J6） |
| M5 | 把 `handoff.json` 的 `params_released` 改为 `true` | rc=3（J6/J9） |
| 绿臂 | 原件 | rc=0 |

---

## 7. 门 0 原始输出（先于证据写入执行）

```text
=== GATE0 BEGIN (I-12-B/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-B\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-B a20260926-01 write-readback-delete 2026-09-26T20:54:24+01:00
readback_match=True
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
=== GATE0 END ===
```

---

## 8. fail-closed 预期（写证据前先声明，防事后挑口径）

1. **可评样本数 = 0**：预测目标期 FY2027（紫金截至 2027-12-31、微软截至 2027-06-30）在本卡执行日 2026-09-26 **尚未结束** ⇒ 目标期实际值**尚不存在**；叠加 `design_manifest.unseal_gate.currently_satisfied=false`（双签在飞）⇒ 本卡**不得**读取/生成任何目标期实际值。⇒ 样本登记面完成，`scorable=0`，按卡文停止②记 `limited`。
2. **不补选公司**：小米（HK）按设计字段 3 的 `excluded_with_reason` 维持排除（gap-U1 证据不可读 / gap-U2 披露日未登记），**不换入表现更好的公司**。
3. **切分不自选**：设计字段 5 = `PENDING`（未签署）⇒ `split_manifest` 只登记冻结规则骨架 + 四集合全 0，不挑切点/折数。
4. **分层键不臆造**：设计字段 3 未给出行业/生命周期取值 ⇒ 该两轴留 `null` 并在下游标 `unproven`。
5. **来源 sha 不自证**：本卡不重哈希 raw 文件（不在本工位可写/授权面）⇒ `hash_verified_this_station=false`，sha 一律转录自 U15/U12，并登记 U4 层已知 63/64 位差异。
