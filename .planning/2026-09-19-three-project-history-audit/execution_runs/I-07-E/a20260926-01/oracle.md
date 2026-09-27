# oracle.md — I-07-E / a20260926-01（开工前冻结的独立预期 + 门 0 原始输出）

> **本文件在任何实质动作（汇总/验证/变异）之前冻结**。写入面 = 仅 `execution_runs/I-07-E/a20260926-01/`。
> 本工位 = 实现者（`implementer_i07e`）：做卡文 `card_I-07-E.md` 五动作的**校准/验证汇总**形态，
> **不自签、不放行参数、不触发任何 falsifier/自动动作、不派 I-12/I-13/I-16/I-17、不改任何封盘字节、不写五份计划文件、不写 `.planning` 之外、禁 git（含 `git status`）、禁联网**。
> status 交付形态 = `review_pending`（验收留给独立复审 + 落定父直写）。
> **正式发布格 = blocked**（卡文 L10：没有正式签名能力时可有研究草稿，但正式发布格 blocked）——本交付整体是**研究草稿**。

---

## 0. 门 0 自探（写+回读+删除三步留档 + 封盘/store 只读复哈希，不采信父探针）

- 探针（2026-09-26，本会话自探）：`Set-Content` 写 `_gate0_probe.txt` → 回读内容行 → `Remove-Item` 后确认消失；随后只读复哈希封盘 `I-11-A/hypotheses.json` 与 store `hypotheses_v3.json`。
- 原始输出（逐字转录，落档用）：

```
=== GATE0 BEGIN (I-07-E/a20260926-01) ===
cwd=.planning\2026-09-19-three-project-history-audit\execution_runs\I-07-E\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-07-E a20260926-01 write-readback-delete
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
=== GATE0 END ===
```

**结论：`gate0_passed=true`（写 ✅ / 回读 ✅ / 删 ✅ / 封盘 sha=f2178768… 与派单一致 ✅ / store sha=b2063ac8… 与 I-11-B C2 登记一致 ✅，均本会话自探，零提权、零破坏性替代）。**
三步写面动作均在本工位写入面内完成；探针文件已删除，未留残件。

---

## 1. 开工授权（逐字回源）

### 1.1 `OWNER_DECISIONS.md §三十四`（L745-L780）——链开工授权

- 节标题：`## 三十四、【已裁定·第十八批】**I-11-B 开工门槛改判：「A」**（2026-09-26 15:4x，选项式问答原话）`
- **owner 选择（L754）：「A」**（A = owner 明文改判开工门槛，以 `5✅+2❌` 现状开工，C3/C5 残余列开工后并行欠账）
- L757：**「改判 I-11-B 的开工门槛 —— 以 MERGE 七条当前 5✅ + 2❌ 现状开工；i11b_unblocked 的语义从『7/7 才开』改为『owner 明文许可开工』。」**
- L758：**「C3/C5 的残余不丢、不隐藏 —— 列为 I-11-B 开工后的并行欠账，每项在卡内载体以 expert_assumption 或 unverified 形式登记」**
- L761-L766 开工卡硬约束（本卡逐条继承）：**「oracle 先冻结」**（含改判逐字依据 + C3/C5 残余清单 + `expert_assumption` 标注要求）／**「不放行任何参数」**（`low/base/high` 仍 null、`_PLACEHOLDER` 维持）／**「不触发任何 falsifier/自动动作」**／**「实现者不自签 · 独立复审 · 落定走三件套」**／**「每一条以 expert_assumption 承接的判断，必须给敏感性区间 + equivalent_to_disclosure_basis=false（同 H4 的 (iv) 形态）」**
- L769-L775 边界：**不解除** `OPEN-2/3/5/6`、**不解除** `BLOCKED-6a/6b/6c`、`BLOCKED-NEEDS-ORIGIN-BYTES`；**不放行参数**（两个 `_PLACEHOLDER` + MSFT 四参数 + 新两分部参数）；**不产生 ACCEPT**、**不改任何 status/decision/decision_sha256**（除非是新卡自己的写入面）；**不代签**
- L779：**「I-11-B 的 I-11-C 后继卡按卡文依赖顺序（I-11-C ← I-11-B）另派，不在本节一并授权」** ⇒ 本卡（I-07-E）同理由编排层按依赖顺序派单（派单原文：`I-07-E`（19 卡链第 3 卡）…依赖 `I-07-B/C/D` + `I-08` + `I-09` + `I-10` + `I-11` 家族全部已满足）

### 1.2 `OWNER_DECISIONS.md §三十七`（L852-L871）——全沙箱常设授权

- 原话：**「给你授权所有的沙箱操作，不要再问我了」**（2026-09-26 17:5x）
- L855-L856：**「本会话内编排层（父）的一切沙箱提权操作，owner 一次性常设授权，无需逐次审批」**；覆盖三仓全部读写、系统调用、任意目录文件创建/修改、网络取证
- L859-L862 边界（**授权 ≠ 免除纪律**）：**「纪律 16/17/18/19/20 全部继续有效」**；**「生产零未授权改动的纪律不变」**；**「产品仓提交（git add/commit/push）不在本授权内」**
- **本卡对 §三十七 的使用面 = 零提权操作**：全部动作发生在 `.planning/.../execution_runs/I-07-E/a20260926-01/` 普通文件写入；无网络（禁联网纪律独立于本授权成立）；无 git。

### 1.3 `execution_v2/card_I-07-E.md` 卡文（逐字要点，sha `9552ac98…`/1,773 B）

- L4：`Parent：I-07。依赖：I-07-B、I-08、I-09、I-10、I-11。Owner：研究执行者；独立买方验收。`
- L6 入口：`入口：RF/scripts/revenue_forecast.py及受支持验证/发布入口…输入是前序真实source-preparation产物，禁止拿旧NOT_FORMAL草稿换名。…准确性F归后继I-12，不能形成I-10→I-12→I-07-E→I-10的循环。`
- L8-L12 五动作：①`为三公司各冻结基期、分部口径、币种单位、信息日、年度路径与来源claim；缺信息显式保留，不伪造capture。`②`将管理目标和主要增长驱动按I-11映射，按适用模型卡处理合并/内部抵销、H1锁定、微软重述等已审关键口径。`③`经真实计算→验证→发布到隔离正式格式registry，记录完整输入/输出与签名资格；没有正式签名能力时可有研究草稿，但正式发布格blocked。`④`独立复算分部加总、年度增量、敏感性和场景约束；跨根来源失效能追溯到相关输入/产物。`⑤`输出三公司独立结果，不因其中一家成功写3/3。交I-13买方验收；本卡仍不授予样本外准确性。`
- L14 退出：`每家公司有完整可审查来源链和产物，或明确blocked；无全文研究包不能通过。`

### 1.4 依赖面（派单断言 + 本工位磁盘实测双记）

派单断言：`I-07-B/C/D`（各 accepted）+ `I-08-A`/`I-09`/`I-10-A` + `I-11-B`/`I-11-C`（2026-09-26 落定 `accepted_scoped`）全部已满足。磁盘实测见 §2 sha 清单与汇总件 §E1；差异如实登记（如 `I-08-A` handoff `status` 字段按其复审裁定 not-granted 项 3 维持 `review_pending`，而 `reviewer_status` 记 `accepted_scoped（design/contract scope）`）。

---

## 2. 上游 sha 清单（冻结；验证阶段全量复算比对）

| # | 文件（相对计划根） | 字节 | sha256（实测，冻结于 oracle 写入时刻） |
|---|---|---|---|
| 1 | execution_v2/card_I-07-E.md | 1,773 | 9552ac980756d59daf9c3cb48455c404ef2ffada6213ec3f0338b13c0a2e861d |
| 2 | execution_v2/card_I-11-B.md | 1,672 | 38ff2907acb627f3d5f6a97ca386a17551329ad3909720e84463a185154ae87c |
| 3 | execution_v2/card_I-11-C.md | 1,433 | b7812e38e425dd00d93b41fe994ab7ab84723081b093e191946a80222f351a7a |
| 4 | OWNER_DECISIONS.md | 109,029 | 17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d |
| 5 | REMEDIATION_REGISTER.md | 486,951 | 867dc5f17f12199fb885336abf8da4a5dba8f6435e54636f8f77d1271652ca9a |
| 6 | execution_runs/I-07-B/a20260923-01/handoff.json | 31,448 | e43cf258e78f1ddc2085ef5e8c5d6cb3e2a730179cb18f566c6da4e15acb9e99 |
| 7 | execution_runs/I-07-C/a20260923-01/handoff.json | 46,545 | 550b489da48c5366069cef5248735d4804837469c67ae467348185c7388491f7 |
| 8 | execution_runs/I-07-D/a20260923-01/handoff.json | 45,995 | 82bb03aca1756d0cec155d039150e930d7b2a885659ad73d5a94e1c032d09e13 |
| 9 | execution_runs/I-08-A/a20260919-01/handoff.json | 24,147 | a728d8f690d6cdda27b23edf61e134cf4b0a9a80904811f00adf19b9616bd3e7 |
| 10 | execution_runs/I-09-A/a20260919-01/handoff.json | 43,143 | 816a44599270fae32492534d6928463f77d377c54efe87f3d07071803c19580d |
| 11 | execution_runs/I-09-B/a20260919-01/handoff.json | 10,793 | 00dd5018ff825ebadafe5fca62f6b908319721fe2316b21325afcdd34977c0b6 |
| 12 | execution_runs/I-09-C/a20260922-01/handoff.json | 34,036 | fa5c456b6a817ef7ba6a520bdc2e500d48488efc5214fb9e3d64591e80d17d83 |
| 13 | execution_runs/I-10-A/a20260923-01/handoff.json | 40,574 | a3f2208ac8601e1a1711d3f6aa30b3e935148bb93017c8a21d350c10dbea3c58 |
| 14 | execution_runs/I-11-A/a20260919-01/handoff.json | 27,788 | e4dafd16952b31317aa47f43e14fd73b078497d488be06a594a9de6b73c903c4 |
| 15 | execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json（**封盘**） | 51,697 | f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28 |
| 16 | execution_runs/I-11-B/a20260926-01/calibration_plan.json | 32,665 | e86b41355c1ba7c5e90fe11c763c1966939621d38f0597dc4a4bfa0d73090e1c |
| 17 | execution_runs/I-11-B/a20260926-01/expert_assumptions.json | 8,580 | 9f8b844e342ec17e731cbe4554388005f5070e0c586de329782df86ee3abd79f |
| 18 | execution_runs/I-11-B/a20260926-01/handoff.json | 37,319 | 4c3c5c908f7c69b23f3ecec52fc81fcbd766e1bfa1174422f8abafbbd7caed31 |
| 19 | execution_runs/I-11-B/a20260926-01/oracle.md | 17,723 | 80a2cda0601fcec5f9495e60ebc9f221c161188e9b585036bdd8d6648eeabba6 |
| 20 | execution_runs/I-11-C/a20260926-01/parameter_mapping.json | 54,875 | d542b34d3429f2409417c2d72cb4335ad2fdde5bf1875103b79a0a2abce7192c |
| 21 | execution_runs/I-11-C/a20260926-01/mapping_verification.json | 9,193 | cecdcb33281727f7c450d7c121d420dd743edbe53c88dbff25491cf8e4cb633f |
| 22 | execution_runs/I-11-C/a20260926-01/handoff.json | 20,258 | da25f736cfde6f97047a691ddff28f1b079c6c29d1cfeac03729ce4c32b9c453 |
| 23 | execution_runs/I-11-C/a20260926-01/oracle.md | 16,336 | 437a7758da4c038762ff72ca95b9cca7492e41fd87b8cd6eca70b397680a01ec |
| 24 | execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json（**store，只读**） | 61,231 | b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff |

**封盘纪律**：`I-11-A/hypotheses.json`（#15）**零字节**（sha=f2178768… 与派单一致）；本卡**不需要**新 hypotheses 版本；若未来需要 ⇒ 走 `supersedes` 形态**落本目录**，封盘原件不动。store（#24）只读，`low/base/high` 全 null、两个 `_PLACEHOLDER` 在位（I-11-C J3 绿证）。

---

## 3. ⭐ OPEN-2 禁消费红线（冻结；本卡只登记、不消费）

**红线原文**（`REMEDIATION_REGISTER.md` L3951 逐字）：

> **P2-1 真发现**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base 124,248.63` 与 store 自写除式真值 `38,175.95` **差 3.25×（store 先天缺陷）** ⇒ **落定 `not_granted` 首条 = `OPEN-2` 前禁消费**。

**执行读法（冻结）**：
1. 本卡汇总件中该参数（`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`）**只能登记**：可写 `124,248.63`（登记除法成立值）与 `38,175.95`（store 自写除式合成值）及 3.25×/3.26× 差异事实；
2. **不得消费**：不得进入任何收入路径/年度路径/分部加总/敏感性产出/情景产出/下游映射；`i11b_proposed_values`（118036.2/124248.63/130461.06）在 I-11-C 已判 `not_executable_no_propagation`、传播值置 null —— 本卡沿用，**传播值一律 null**；
3. 登记形态 = `registered_not_consumed`（`open2_ban_observed=true`）；OPEN-2 解锁（系数来源裁定 + 分母算术更正）前，任何消费动作均违规；
4. 同源红线一并冻结：`unverified-N2`（公式分母不自洽：`884,943+83,161×24=2,880,807 ≠ 885,141`；按合成分母商≈38,175.95）只登记不更正（store 不动）。

---

## 4. EA 模板（冻结；§三十四 L766「同 H4 的 (iv) 形态」，逐字继承 I-11-B oracle §5）

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
- 管理层目标**不得**用作独立准确性证据。
- 本卡消费 I-11-B `expert_assumptions.json` 的 **EA-1…EA-7**（7 条，实测 `all_have_sensitivity_interval=true`、`all_equivalent_to_disclosure_basis_false=true`）；本卡不新增 EA（如确需 ⇒ 按本模板落本目录，缺字段即不成立）。

---

## 5. 冻结预期（本卡 oracle：汇总件逐项应当呈现什么）

### 5.1 正例（应当成立）

| # | 预期 | 判据来源 |
|---|---|---|
| P1 | 三公司冻结表：每家有 基期/分部口径/币种单位/信息日/年度路径/来源claim 六字段；**缺信息显式保留**（不伪造 capture） | 卡文 L8 |
| P2 | 校准汇总表 18 槽位与 I-11-B `calibration_plan.json`（18 `parameters`）、I-11-C `parameter_mapping.json`（18 `mapping_rows`）**逐位一致**：13 `mapped/not released` + 5 `not executable/declined` | CP/PM 原文 |
| P3 | 全部数值状态 ∈ {`proposed_not_released`, `mapped_not_released`, `not_executable_no_propagation`, `unmapped_declined_no_number`, `declined_to_calibrate`}；**无任何 released** | §三十四 L763 |
| P4 | 红线行：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` = `registered_not_consumed`，传播值 null；`124,248.63`/`38,175.95` 仅出现于登记区 | §3 红线 |
| P5 | 关键口径（卡文 L11）：合并/内部抵销 = H-05/E5 已审形态（抵销 234,970,146,412 元仅在恒等式桥）；**H1锁定 / 微软雅黑述在回源面内未检出已审载体 ⇒ 显式保留为 gap，不伪造处理记录** | 卡文 L11 + fail-closed |
| P6 | 验证汇总：上游 24 件 sha 全量复算一致；分部加总（584,049,229,264−234,970,146,412=349,079,082,852，差=0）/ 带换算（±5%/±10%/g 换算）/ 场景约束（E1-E7 + EA-6 联动）逐项有来源 | I-11-C action1 P1-P8 + RECOMP |
| P7 | STOP：槽位级 5 行（REALIZED_UNIT + 两分金属实现价 + MSFT_CLOUD + MSFT_LICENSING）；卡级 `STOP_CALIBRATION` 未触发（从严触发式）但**严格读法登记在案**；`STOP_SCENARIO` 未触发 | I-11-C stop_verification |
| P8 | 三公司独立结果：不写 3/3 —— ZIJIN=有（13 槽位登记未放行）/ MSFT=有（5 槽位，3 登记未放行 + 2 显式拒绝）/ **XIAOMI=明确 blocked-缺位**（I-11-A `STOP_EVIDENCE`：`HK-XIAOMI-AR2025 not_readable_in_this_attempt`、0 hypotheses；FY2027 槽位=0） | 卡文 L12 |
| P9 | 发布格：研究草稿 = 在；**正式发布格 = blocked**（无正式签名能力）；`implementer_signed=false`、`releases_nothing=true`、`status=review_pending` | 卡文 L10 + 九步法 |
| P10 | 封盘零字节（sha=f2178768…）、store 零改动（sha=b2063ac8…）；新版本需求 = 无（`supersedes` 形态未启用） | 派单硬约束 |

### 5.2 负例 / 变异清单（冻结；红绿双向，≥3，实做 5）

| 编号 | 变异（副本 `_mut/` 上做，原件字节不动） | 期望（红） | 期望（绿） |
|---|---|---|---|
| M1 | `handoff.json` 的 `params_released` false→true（模拟放行参数） | 校验器 rc=3（J1 放行锁被破） | 原件 rc=0 |
| M2 | 汇总件红线行 `registered_not_consumed`→`consumed_for_forecast`（模拟消费被禁值） | 校验器 rc=3（J2 OPEN-2 红线被破） | 原件 rc=0 |
| M3 | `verification.json` 上游清单某 sha256 改 1 个 hex 位（模拟上游指纹不符） | 校验器 rc=3（J3 上游一致性被破） | 原件 rc=0 |
| M4 | 汇总件 EA 模板镜像某条 `equivalent_to_disclosure_basis` false→true（模拟破坏 H4 (iv) 常量） | 校验器 rc=3（J4 EA 模板被破） | 原件 rc=0 |
| M5 | 汇总件某真实数值格注入隔离合成数（`281520`；对 ZINC 行 base） | 校验器 rc=3（J5 合成数隔离被破） | 原件 rc=0 |

（绿臂 = 未变异原件一次通过；红臂 = 5 变异逐一被具名击杀。`exit_code_legend`：`0`=ALL_INVARIANTS_OK；`1`=harness 失败；`2`=无裁决；`3`=不变量违例（具名）——按 START_HERE 冻结码表；红臂 rc=3 属「声明期望不符」。）

### 5.3 上游一致性核（验证阶段必查，含已登记的层内差异）

- 24 件文件 sha 全量复算 == §2 冻结值（预期全绿）。
- **登记差异 u-N4（只登记不更正）**：store `hypotheses_v3.json` 内 `US-MSFT-10K-FY2026.doc_sha256` 为 **63 位**（`e3de0053…40ecff`，缺末位 `f`），与 I-07-B 实测 64 位 `e3de0053…40ecfff`（`US-MSFT-2026`，re-verified before AND after）**不一致** —— 转录层缺陷（同 F-REV-I10A-1 物种），store 只读不回改。
- **登记差异 u-N5（只登记不更正）**：`H-CN-ZIJIN-SEG-01.parameter_mapping.original_value='349,079,082,852'`（=四分部合计/合并营业收入）与 `parameter_id=ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027` 的分部语义张力（unverified-N1 继承）。
- **登记差异 u-N6（只登记不更正）**：EA-4 `band_rationale` 注记区间 [320,763, 348,432] 与其自身带换算（I-11-C 复算 ≈[375,283.38, 414,786.90]；基期合计±5% ≈[315,247.05, 348,430.95]）不符（unverified-N3 继承）。

---

## 6. 本 oracle 不做什么（边界自宣）

- 不产生 `ACCEPT`、不写 `decision`/`decision_sha256`、不代签任何面；独立复审另派；落定走父直写（V3 轻格式）。
- **不放行任何参数**：`hypotheses*.json`、`model_cards*`、store 全部**只读**；不新建 hypotheses 版本（不需要；若需要 ⇒ `supersedes` + `modified_indices` 落本目录，封盘原件零字节）。
- 不触发任何 falsifier/自动动作；不解 `OPEN-2/3/5/6`、不解任何 `BLOCKED-*`。
- **不派 I-12/I-13/I-16/I-17**（依赖顺序另派）；不写五份计划文件（task_plan/findings/progress/implementation_plan/PLANNING_STATUS 一律不动）；不写 `.planning` 之外；**禁 git（含 `git status`）**；**禁联网**（本卡零外部检索；如需外部数据 ⇒ provenance 四件 + `external_retrieval_not_local`，本卡未触发）。
- 示例数字（隔离清单 2/8760/0.5/0.6/0.7/40/20/30/32/34/1200/264000/281520/299040/17520）**禁止进入任何真实字段**；`1,200,000`（铜计划吨数，AR2025:p56）与示例 1200 非复制（collision 先例）。
- **fail-closed**：数据不足 ⇒ `STOP` 判 `blocked`（合格）；缺信息显式保留，不伪造 capture；残余不隐藏。
