# I-12-A-STAT-SIGN · 统计面阈值签署 —— oracle（**先冻结**）

> 任务：`I-12-A` 卡文 `Owner：统计reviewer和行业reviewer共同签字` 的**统计半边**签署裁定
> role：`statistics_reviewer_i12a`（**统计 reviewer，非实现者、非行业面**）· attempt：`execution_runs/I-12-A-STAT-SIGN/a20260926-01`（新建）
> 被审载体：`execution_runs/I-12-A/a20260926-01`（三件证据**只读**，收尾复哈希）
> Parent：`session-19074bf0-0205-4315-af73-9db57597275a`（编排层指派本统计面裁定）
> 冻结时间：2026-09-26 20:4x（UTC+01；门 0 探针 `2026-09-26T20:42:33.2172152+01:00` 之后、**任何签署产物之前**）
> 写入面（唯一）：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-12-A-STAT-SIGN/a20260926-01/`

---

## §0 冻结声明（本文件先于一切签署产物；时序可证）

1. **oracle 先冻结**：本文件写入 → 回读 → 计 sha → 才开始算 `decision_sha256`、写 `stat_signatures.json`；本文件 sha 记入 `handoff.json`。
2. **测试集结果保持封存**：本工位**未读**任何测试集/回测/准确性结果（含 `I-10-B`、`I-13` 及任何 accuracy 数值面）；`test_results_sealed=true`、`accuracy_results_read=false`。回源面严格限定于 §1 只读清单。
3. **不放行参数** · 不产生 `ACCEPT` · 不改任何卡 `status`/`decision`/`decision_sha256` · **不代签行业面**（本签名只是统计面半边）· 不派 `I-12-B`。
4. 封盘 `I-11-A/hypotheses.json` `sha=f2178768…` **零字节**；store `hypotheses_v3.json` `sha=b2063ac8…` 零改动（门 0 与收尾各只读复哈希一次）。
5. **fail-closed**：任一阈值不满足 §3 判据 ⇒ `NOT_SIGNED (insufficient_evidence)`，**不为解锁而签**；`I-12-B` 被堵不构成放宽任何判据的理由。
6. **禁 git（含 `git status`）· 禁联网 · 禁写五份计划文件 · 禁写 `.planning` 之外**。

### 门 0 自探原始输出（逐字）

```
=== GATE0 BEGIN (I-12-A-STAT-SIGN/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-A-STAT-SIGN\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-A-STAT-SIGN a20260926-01 write-readback-delete 2026-09-26T20:42:33.2172152+01:00
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
sealed_bytes=51697
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
store_matches_b2063ac8=True
=== GATE0 END ===
```

---

## §1 回源面（只读清单；sha256 实测于 2026-09-26 20:4x）

| # | 路径（相对 plan root） | bytes | sha256 | 用途 |
|---|---|---|---|---|
| 1 | `execution_v2/card_I-12-A.md` | 1,467 | `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` | Owner 行 / 停止①② / 验收 / 动作 1-4 |
| 2 | `execution_runs/I-12-A/a20260926-01/oracle.md` | 16,649 | `08723ab0f62c07cbf0f9a7563b8fc6382bff41da8a3f7c72ab14b81cfc7e76ee` | 6 项清单 + 签署形态 + STOP 规则 |
| 3 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json` | 22,317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` | 13 字段（9 filled + 1 filled_threshold_unsigned + 3 PENDING） |
| 4 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json` | 5,334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` | 6 项 `unsigned` 清单（L57-L64）+ 双 reviewer scope |
| 5 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json` | 5,618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` | SHA256 冻结 / unseal 门 |
| 6 | `execution_runs/I-12-A/a20260926-01/handoff.json` | 15,267 | （只读） | `STOP① BLOCKED_PROFESSIONAL_DECISION` 登记 |
| 7 | `execution_v2/research_cards.json` L115-L191 | 40,058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` | 13 字段原文 + 指标公式/边界（**仅定义，无结果值**） |
| 8 | `OWNER_DECISIONS.md` §三十七（L852-L871） | 109,029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` | 全沙箱常设授权（**授权 ≠ 专业签署**） |
| 9 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26,132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | 上游数据可得性（18 槽位 / 13 mapped + 5 declined） |
| 10 | `execution_runs/I-11-C/a20260926-01/parameter_mapping.json` | 54,875 | `d542b34d3429f2409417c2d72cb4335ad2fdde5bf1875103b79a0a2abce7192c` | 18 映射行（period 字段，无截点字段） |
| 11 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 零字节 |
| 12 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61,231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 零改动 |

**数据可得性实测（factual，逐条可复算）**：

- `D1` 可评 entity = **2**（紫金、微软）——`evaluation_design.json` **L111** `pool_size_current`；小米 gap-U1/U2 排除（**L100**、**L102-L107**）。
- `D2` cluster 单位 = **entity**（**L79**）；block 单位 = **origin**（**L243**）；成对同样本规则（**L242**）。
- `D3` 回源面内已登记 origin 截点 = **3 行、每公司 1 个**（紫金 `2026-03-20`、微软 `2026-07-29`、小米 `null`；`as_of=2026-09-18`）——`evaluation_design.json` **L124-L127**；上游同源 `I-07-E/calibration_validation_summary.md` **L15/L16/L17**。
- `D4` `execution_runs/I-11-C/**` 内 `available_at|vintage_class|published_at` 命中 = **0**（实测 grep 计数 0）⇒ **无历史 vintage 清单**。
- `D5` 18 槽位 = **13 mapped + 5 declined**（紫金 13 行 `L32-L48`、微软 5 行 `L50-L58`；小计 `L60`；小米 = 0 槽位）。
- `D6` 反向检索：`execution_v2/**` + `OWNER_DECISIONS.md` 内 `经济显著|可接受偏差|统计功效|可接受CI` 命中 = **6 处，全部为字段定义原文**（`common_research_cards.md` L144/L146、`research_cards.json` L125/L127、`research_cards.md` L144/L146），**0 处数值定标**。
- `D7` `I-12-A` 三件证据状态：`test_results_sealed=true`、`accuracy_results_read=false`（`evaluation_design.json` L8-L9）⇒ 本裁定不依赖任何未封存结果。

---

## §2 卡文判据（逐字；动作 / 停止 / 验收以卡文为准）

**卡头（Owner 行，逐字）**：`Parent：I-12；状态：planned；Owner：统计reviewer和行业reviewer共同签字；依赖：I-07-E。`

**停止（逐字，L20-L21）**：
- 「任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。」
- 「已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。」

**验收（逐字，L23）**：「evaluation_design_fields全部完成或有获批not_applicable；SHA256冻结在结果解封前。」

**动作 1（逐字，L13）**：「逐项填写evaluation_design_fields，未定项标PENDING，不由弱模型选择方便通过的阈值。」
**动作 2（逐字，L14）**：「选择primary endpoint、baseline、权重、样本最小数量/功效、成对比较、cluster/block方法、CI和多重比较校正。」

**6 项待签阈值（`professional_approval.json` L57-L64 逐条）**：
`① 字段5 时间划分折数/切点/窗口长度` · `② 字段10 最小公司数/每层样本数/统计功效/可接受CI宽度` · `③ 字段11 置信水平(CI level/α)` · `④ 字段11 重复抽样次数与随机种子` · `⑤ 字段11 多重比较校正方法` · `⑥ 字段12 成功/失败阈值：经济显著改善幅度、可接受偏差、情景包含率、区间宽度`

**统计 reviewer 签署范围（`professional_approval.json` L21-L26 逐字）**：字段 5 时间切分与折数 · 字段 10 最小样本量/功效/可接受 CI 宽度 · 字段 11 置信水平、重复抽样次数与随机种子、多重比较校正方法 · 字段 12 成功/失败阈值（**与行业 reviewer 共同**）。
**行业 reviewer 签署范围（L38-L43 逐字）**：字段 3 公司池 · 字段 8 baseline · 字段 11 行业相关 cluster/block 单位 · 字段 12 成功/失败阈值（**与统计 reviewer 共同**）。

---

## §3 签署判据（C1-C7；逐项**全部满足**才可签，缺一即 `NOT_SIGNED`）

| id | 判据 | 可证伪点（不满足 ⇒ 拒签） |
|---|---|---|
| `C1_traceable` | 依据与数据可得性事实**可回源**：每个依据给出 `path:Lx-Ly`，且该文件在 §1 只读面内、sha 已冻结 | 依据只能靠"常识/惯例"且无任何面内锚点 ⇒ 拒签 |
| `C2_result_independent` | 选择**不依赖任何测试/准确性结果**；`test_results_sealed=true`、`accuracy_results_read=false` 全程成立 | 需要方差/效应量/历史误差分布等**封存面**才能定值 ⇒ 拒签 |
| `C3_counterexample_tested` | 至少 1 个反例（错值 / 错向 / 越权 / 事后改）在 `_verify_signatures.ps1` 下被**具名判据击杀（rc=3）** | 反例跑不出红 ⇒ 该签署形态不成立 |
| `C4_role_scope` | 属**统计面**签署范围（`professional_approval` 统计 reviewer scope）；须**行业共同签署**者不得单签 | 越权到行业面 / 代实现者自签 ⇒ 拒签 |
| `C5_fail_closed_direction` | 阈值方向**不得比「只描述、不宣称准确性优势」更松**；不得以"当前只有 2 家"反推一个宽松阈值 | 阈值放宽以解锁任何下游 ⇒ 拒签 |
| `C6_value_plus_guard` | 给出**具体数值 + 适用性守卫**（cluster/block 不足 ⇒ 降级描述，守卫不因签署而放宽） | 只给"标准做法"而无守卫，或守卫被签署解除 ⇒ 拒签 |
| `C7_carrier_form` | 落盘形态符合 §4：`decision_payload_canonical`（ASCII）+ `decision_sha256` **写入前/后各复算一次且相等**；`NOT_SIGNED` 则 `decision_sha256=null` + `refusal_sha256` | hash 不匹配 / `NOT_SIGNED` 却带 `decision_sha256` ⇒ 违例 |

---

## §4 签署形态（冻结 schema）

`stat_signatures.json` 每项（6 项，顺序固定 S1..S6）：

```json
{
  "item_id": "S1|S2|S3|S4|S5|S6",
  "field_index": 5|10|11|12,
  "item_label": "<professional_approval L57-L64 逐字>",
  "selection": "SIGNED" | "NOT_SIGNED",
  "value": { "<具体数值，SIGNED 必填>" },
  "rationale": "<为什么按判据该签/该拒>",
  "counterexample": {"mutation": "...", "expected": "...", "observed": "..."},
  "compatibility_impact": "<对 I-12-A 兼容性/解封门的影响>",
  "recovery_rule": "<如何恢复/重签>",
  "rejected_alternatives": [{"option": "...", "why_rejected": "..."}],
  "evidence": [{"path": "...", "lines": "Lx-Ly", "what": "..."}],
  "missing_evidence_measured": [{"fact": "...", "measured_at": "...", "source": "path:Lx"}],
  "decision_payload_canonical": "<ASCII 规范串，hash 的原文>",
  "decision_sha256": "<SIGNED 才有；NOT_SIGNED = null>",
  "refusal_sha256": "<NOT_SIGNED 才有>",
  "signature": {"role": "statistics_reviewer_i12a", "signed": true|false,
                "signed_at": "...", "scope": "统计面半边", "industry_countersign": "required_separately",
                "does_not_imply": ["不放行参数", "不代签行业面", "不解除 STOP①", "不产生 ACCEPT"]}
}
```

**hash 规则（C7）**：`decision_sha256 = SHA256(UTF-8(decision_payload_canonical))`，**先算后写**；文件落盘后**从文件回读 canonical 串复算**第二次，两者必须逐位相等（结果登记进 `ruling_stat_sign.md` 与 `handoff.json`）。

---

## §5 逐项可签性判定（**冻结**；由 §1 数据可得性事实推出，签署时不得偏离）

| item | 字段 | 待签项 | 判定 | 数值 / 缺什么（冻结要点） | 关键依据（file:line） |
|---|---|---|---|---|---|
| `S1` | 5 | 时间划分折数/切点/窗口长度 | **NOT_SIGNED** | 缺：可得 vintage 清单（每 origin `available_at`+`vintage_class`）。实测已登记 origin = 每公司 1 个 ⇒ 滚动 origin **0 折可算** | `evaluation_design.json` L141/L152/L124-L127；`I-07-E` L15-L17；`I-11-C/**` `available_at` 命中 0 |
| `S2` | 10 | 最小公司数/每层样本数/功效/可接受 CI 宽度 | **NOT_SIGNED** | 缺 3 件：① 每层可接受 CI 半宽的定标来源（`D6` 实测 0 处数值定标，EA-1 明文禁挪用）② 效应量/方差基础（属封存面，`C2`）③ 每层 origin 数（同 `S1` 缺口） | `evaluation_design.json` L224/L229-L231；`I-07-E` L66；`research_cards.json` L125 |
| `S3` | 11 | 置信水平(CI level/α) | **SIGNED** | **双侧 95%（α=0.05）** + 守卫 `cluster≥3 且 block≥2`，否则该层 `insufficient_for_ci` 只描述 | `evaluation_design.json` L241-L245/L79/L243；`research_cards.json` L159；D1/D2/D3 |
| `S4` | 11 | 重复抽样次数与随机种子 | **SIGNED** | **B = 10,000**；**seed = 2,765,402,844**（= `hex(card sha256[0:8])` = `a4d4b2dc`，事前派生、与结果无关）+ 同一守卫 | `evaluation_design.json` L248/L249/L286（同种子复算逐位一致）；§1#1 card sha |
| `S5` | 11 | 多重比较校正方法 | **SIGNED** | **Holm（FWER）双侧 α=0.05**；family = 解封前 manifest 登记的全部确认性成对检验；BH-FDR 仅限显式 exploratory 附录 | `evaluation_design.json` L250（**「二选一由统计 reviewer 定」逐字**）/L252 |
| `S6` | 12 | 成功/失败阈值（经济显著幅度/偏差/包含率/区间宽度） | **NOT_SIGNED** | 缺 3 件：① 经济显著改善幅度无面内定标（`D6` = 0 处）② 可接受偏差/包含率/区间宽度无容差来源，EA-1「带形状=敏感性设计非精度主张」禁挪用 ③ 行业 reviewer 共同签署缺位（`C4`） | `evaluation_design.json` L259/L269-L270；`research_cards.json` L127/L164；`I-07-E` L66；`professional_approval.json` L38-L43 |

> 判定方向自检：`SIGNED` 3 项全部是**面内显式委托给统计 reviewer 的选择**（C4 成立）且**数值不依赖任何未封存结果**（C2 成立）；`NOT_SIGNED` 3 项全部卡在**面内实测无依据**或**须行业共签**，不是"难签"而是"无据可签"。

---

## §6 blocked 触发规则（fail-closed；本工位只登记、不自裁他卡）

- **停止① `BLOCKED_PROFESSIONAL_DECISION`（卡文逐字）**：`§2 6 项` 中**任一项**未获「统计 + 行业」双签即成立。本签署后：`S1/S2/S6 = NOT_SIGNED`（统计面亦未签）+ `S3/S4/S5` 仅统计面已签、**行业面未签** ⇒ **停止① 仍成立（TRIGGERED，未解除）**。
- **停止②**：「已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。」本工位 `test_results_sealed=true`、未读结果 ⇒ 未触发；本签署**先于**解封，若此后任何一项数值被改 ⇒ 新开探索版本，旧结果不得追认。
- **解除路径（只登记，不由本工位执行）**：① 行业 reviewer 对其 scope（字段 3/8/11 cluster-block/12）签署；② `S1/S2/S6` 补足面内依据或取得 `not_applicable` 批准后重签；③ 签署齐备后**新开 design 版本重冻 `design_manifest` SHA256**；④ 编排层明文解封。**四条齐备前不解封任何测试实际值、不派 `I-12-B`。**
- **裁定权边界**：卡文停止条件的最终裁定 = 独立复审/编排层；本站只登记事实，不改任何卡 `status`/`decision`/`decision_sha256`，不产生 `ACCEPT`。

---

## §7 变异清单（红绿双向，≥3；本卡 **3 红 + 1 绿**，在 `_mut/Mx/` 副本执行，原件字节不动）

| id | 变异（仅 `_mut/Mx/stat_signatures.json`） | 期望 rc | 击杀判据 |
|---|---|---|---|
| `GREEN` | 原件 `stat_signatures.json` | **0** | K1-K8 全 OK |
| `M1` 红·**签了不该签** | `S1` `selection` `NOT_SIGNED`→`SIGNED` 并附伪造 `value`（编造折数/切点） | 3 | `K2_verdict_lock`（`S1` 冻结判定 = NOT_SIGNED） |
| `M2` 红·**拒签了本可签** | `S3` `selection` `SIGNED`→`NOT_SIGNED`（把本可签的 CI 水平退回未签） | 3 | `K2_verdict_lock`（`S3` 冻结判定 = SIGNED） |
| `M3` 红·**阈值被篡改** | `S3.value.alpha` `0.05`→`0.50` 并同步重算 hash（模拟"结果后改阈值"） | 3 | `K3_value_lock`（§5 冻结数值表） |
| `M4` 红·**越权/放行** | `industry_countersign_still_needed` `true`→`false`（模拟代行业签、解除 STOP①） | 3 | `K6_boundary_lock` |

> `M1`/`M2` 覆盖派单要求的两个红向（签了不该签 / 拒签了本可签）；`M3` 覆盖停止②物种；`GREEN` 为正例（按判据该签的真签 = S3/S4/S5，该拒的真拒 = S1/S2/S6）。

**exit_code_legend（冻结）**：`0`=ALL_CRITERIA_OK · `1`=harness 失败 · `2`=无裁决 · `3`=判据违例（具名 `K1..K8`）。

---

## §8 边界自宣（本工位不做什么）

不读测试/回测/准确性结果（封存令）· 不放行任何参数（`params_released` 不适用且不产生）· **不代签行业面**（`industry_countersign_still_needed=true`）· 不代实现者自签 · 不产生 `ACCEPT` · 不改任何卡 `status`/`decision`/`decision_sha256` · `I-12-A` 三件证据只读（收尾复哈希）· 封盘 `f2178768…` 零字节、store `b2063ac8…` 零改动 · 不写五份计划文件 · 不写 `.planning` 之外（`git_diff_non_planning=0`）· 禁 git（含 `git status`，零 git 调用）· 禁联网（零外部检索）· **OPEN-2 红线**：`124,248.63` / `38,175.95` 只登记不消费，禁入任何阈值 · 缺依据 ⇒ `NOT_SIGNED`，残余不隐藏（fail-closed）。
