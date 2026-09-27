# I-10-A · a20260923-01 — 独立复核报告（reviewer_report.md）

**Reviewer**：独立行业/会计 reviewer（N=1，未参与本卡实现；受父代理 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单）
**Card**：`execution_v2/card_I-10-A.md`（sha `fe169c83…3b947`，31 行）— 独立 spec 来源
**复核依据**：卡文 Owner 行（行业/会计 reviewer 主责）+ `handoff.next_action` + `evidence/I-10-A/independent_adaptation_review.md §3`（9 步清单）+ oracle §5 攻击面
**日期**：2026-09-24（本地）
**实现者状态核对**：`handoff.status=review_pending`、`implementer_signed=false`、`implementer_never_signs_acceptance=true` ✅（本报告是实现者之后的第一步）

**复核方法边界（自我声明）**：read / grep / pwsh only；判据重跑全部落在 `%TEMP%\i10a_review_rerun\`；**对 attempt 树与产品树零写入**（实测：attempt 内最近 3 小时无修改文件，探针产物 mtime 仍停在 2026-09-24 00:01:52）；git 仅只读（`status` / `log` / `diff`）；**network=0**（本报告未发起任何 web 调用）；实现者证据文件**一字未改**，本报告与 `.sha256` 是我本轮仅有的两个交付文件。

---

## 0. 结论（Verdict）

**`accepted_scoped`**

| 维度 | 结论 |
|---|---|
| 4 个 GREEN case（ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03） | **disclosure_adaptation 授予并签署**（限各该公司/分部/该口径/FY2025，见 §8 签署表） |
| 2 个 STOP case（MS-PBP-M05 / MS-IC-M06，US-MSFT-2026） | **诚实出口确认**：D 完成（missing 标记、不补零、不倒推）、E/probe 未执行、**disclosure_adaptation 不授予**、公司正式预测**不放行** |
| accuracy | **unproven（本卡不授予）** |
| formula | 维持 M01–M31 `accepted_scoped`（31/31，实测 sweep + 4 张抽验 pin 全中），**不外推** |
| 公司放行 | **0 家放行**（三家公司 `formal_company_forecast_cleared=false` 实测在案） |
| 产品面 | **零变更**（anchors 5/5、iso 8/8、sources 6/6、plan inputs 12/12 复算全等） |
| 发现 | 卡面 4 条（F-I10A-1..4）全部独立核实/裁定 + 本轮新增 **F-REV-I10A-1..5**（簿记/文档类，全部 non-blocking） |
| 处置 | 6 case 已 disposition（4 授予 / 2 诚实 STOP）；`disclosure_adaptation` 机读状态**仍为 unmapped/unsigned**（我无权改实现者证据文件——签署落在本报告，落账动作由父代理/实现者转记）；F-I10A-2 → 已立修卡 **`I10A-F2-FIX`（ref `e1c31937`，REMEDIATION_REGISTER §一〇四）** |

**判据链全部复现（我在 %TEMP% 的独立重跑）**：probe normal 4/4 rc0（计数 24/9/3/3、输出=冻结手算值、low/base/high 同值）· mut_omit_optional XM-PHONE rc3 存活 / XM-EV rc2 击杀 · validator GREEN rc0 · RED 5/5 rc2 · MUT 5/5 rc2 · 解码重跑 sha 与留档**逐字节相同**（mapped 272,511 / unmapped 0）。

---

## 1. 交付物与完整性（清单 §3 步骤1）

### 1.1 8 件卡文证据 + protocol 交付物：全部在场、JSON 全部可解析

| 交付物 | 在场 | JSON 解析 | sha256（我实测） vs handoff pin |
|---|---|---|---|
| `oracle.md`（冻结件） | ✅ | n/a | `5cdd7331…9de6dd` = pin ✅ |
| `evidence/I-10-A/oracle_expected.json` | ✅ | ✅ | `bf212696…f9d01` = pin ✅ |
| `binding.json` / `commands.json` | ✅ | ✅ | `aea79243…` / `ed7a8f40…` = pins ✅ |
| `decision.md` | ✅ | n/a | `c84493fc…` = pin ✅ |
| `changes.diff` | ✅ | n/a | `681bdd8f…` = pin ✅ |
| `handoff.json` | ✅ | ✅ | self（excluded） |
| `recovery/README.md` | ✅ | n/a | `ec2e4d69…` = pin ✅ |
| `before/snapshot_before.json` / `after/snapshot_after.json` / `after/hash_table_before_after.json` | ✅ | ✅ | 见 §7 |
| **① selected_model_manifest.json** | ✅ | ✅ | `96b0f56e…` = pin ✅ |
| **② disclosure_mapping.json** | ✅ | ✅ | 实测 `7e03ea748cb99d74038daeef3b529b…`（64）；handoff/changes.diff pin 为 **63 位**（见 **F-REV-I10A-1**）；model_DE manifest 内的 64 位 pin 与实测一致 ✅ |
| **③ accounting_decision.md** | ✅ | n/a | `6f8cfea1…` = pin ✅；AD-1..AD-12（≥8 段）实测在场 |
| **④ historical_reconciliation.json** | ✅ | ✅ | `ce222355…` = pin ✅ |
| **⑤ historical_mapping_probe.json** | ✅ | ✅ | `b4ef9b96…` = pin ✅ |
| **⑥ model_DE_evidence_manifest.json** | ✅ | ✅ | 实测 `c3e489c580cc7e9eae18efa…`（64）；pin 为 **63 位**（F-REV-I10A-1） |
| **⑦ disclosure_qualification.json** | ✅ | ✅ | `6c42e9a8…` = pin ✅ |
| **⑧ independent_adaptation_review.md** | ✅ | n/a | `5c0bb928…` = pin ✅ |
| `forecast_integration.json` | ✅ | ✅ | `d9370847…` = pin ✅ |
| `run_log.jsonl` | ✅ | 73 行 0 解析错 | `16e466c4…` = handoff pin ✅（changes.diff 内为旧值，见 F-REV-I10A-5） |
| `deps/{input_hashes, m31_qualification_sweep, iso_hash_proof}.json` | ✅ | ✅ | 见 §7 / §1.3 |

`model_DE_evidence_manifest.per_model_case_products`：6 个 case × 4 件 M 卡产物引用（disclosure_mapping / accounting_decision / historical_reconciliation / forecast_integration）+ `independent_review (PENDING — unsigned)` 全在场；`aggregate_files` 内 4 个 64 位 sha 与我实测全部一致（R9 等价复算 ✅）。

### 1.2 冻结时序（creation-time）

| 文件 | mtime | 关系 |
|---|---|---|
| `binding.json` | 2026-09-23 22:17:43 | 早于一切判据运行 ✅ |
| `oracle.md` | 2026-09-23 23:50:46（run_log ORACLE-FREEZE 23:51:00，sha `5CDD7331…`） | 早于首判据运行 ✅ |
| `oracle_expected.json` | 2026-09-23 23:54:45 | 晚于冻结记录 3 分钟、仍**早于**首判据运行 23:58:37 ✅（机器可读期望在首跑前定稿） |
| `commands.json` | 2026-09-23 23:58:03 | 首判据运行前 34 秒（两段绑定的第二段；见 §1.4 备注） |
| 首判据运行（red_conv×4） | 2026-09-23 23:58:37 | — |

**冻结结论**：容差与期望先于 E/探针判据运行冻结（卡文 action 3「先冻结容差，再解释残差」成立）；`oracle.md` 在首判据运行后无修改（pin 全程一致）。

### 1.3 公式资格前置（STOP_FORMULA_DEPENDENCY 面）

`deps/m31_qualification_sweep.json`：`card_count=31`、`formula_accepted_scoped_count=31`、`formula_other={}`。抽验 4 张（M03/M05/M09/M31）`qualification.json` 实测 sha 与 sweep pin **逐个相等**，且三态一致（`formula=accepted_scoped` / `disclosure_adaptation=unmapped` / `accuracy=unproven`）。→ 停止条款 2 不触发，结论**独立复算成立**。

### 1.4 备注（不阻断）

- `commands.json` mtime 距首判据运行 34 秒——形式上满足「先绑定后运行」，但绑定与首跑几乎同时；其 argv 与 `command_runs/**/argv.json` 逐条一致（我抽验 20 个探针目录 + 11 个验证目录 argv 结构一致）。
- `binding.forbidden` 明列「git 命令一律禁止」「%TEMP% 使用须先记录」，`recovery/README.md` 记「无 %TEMP% 使用」——与我实测的 attempt 树 mtime 面一致。

---

## 2. 逐 case 抽查复算（我的行业/会计签署面）

冻结容差（oracle §2 / oracle_expected，先于残差冻结）：**ZJ-MIN ±0.10% 线级 / ±0.05% 合计；ZJ-SMT ±0.10% / ±0.05%；XM-PHONE ±0.05%；XM-EV ±0.10%**（合计）。

### 2.1 D 段原文/页/字段核对（≥5 条引文义务 → 实测 12 条）

| # | 引文/字段 | 留档位置 | 我的核对 |
|---|---|---|---|
| 1 | 金锭 810.17 元/克 · 49,074 千克 · 3,975,798 万元 | `CN-ZIJIN-2025.txt` L3958-3964（p.44 销售详情） | ✅ 逐字段相等 |
| 2 | 金精矿 730.98 / 34,087 / 2,491,716 | L3971-3976 | ✅ |
| 3 | 铜精矿 63,613 / 666,158 / 4,237,657；电积铜 69,665 / 95,499 / 665,294；电解铜 71,422 / 123,286 / 880,537；矿山产锌 14,999 / 352,470 / 528,665；矿山产银 6.88 / 430,254 / 295,801；铁精矿 660 / 111.35 万吨 / 73,482 | L3983-4049 | ✅ 6 行全等 |
| 4 | 冶炼加工金 772.15 / 162,950 / 12,582,221；冶炼产铜 71,621 / 697,678 / 4,996,807；冶炼产锌 20,327 / 403,324 / 819,823 | L4056-4085 | ✅ |
| 5 | p.45 分产品收入（金锭 3,975,798 … 铁精矿 73,482；冶炼 12,582,221 / 4,996,807 / 819,823） | L4137-4213 | ✅ 与 p.44 金额列互洽 |
| 6 | 分部注 p.326：矿产品对外 109,977,556,345 + 内部 28,294,116,611 = 138,271,672,956；冶炼合计 189,683,879,295 | L34991/34998/35012/35013 | ✅ L2 桥数字原文在案 |
| 7 | 小米 p.21：出货量 165.2 百萬部 | `HK-…_decoded.txt` L1404 | ✅ |
| 8 | 小米 p.21：ASP 每部人民幣 1,128.7 元 | L1436 | ✅ |
| 9 | 小米 p.22：交付量 411,082 輛 | L1582 | ✅ |
| 10 | 小米 p.22：ASP 每輛 251,171 元；其他相關業務收入 28 億元 | L1610 / L1635-1636 | ✅ |
| 11 | 小米附註5 p.337 分部收入行：`186,439,777 123,200,191 37,440,346 4,136,860 351,217,174 106,069,513 457,286,687`（千元） | L17789-17790 | ✅ 并做构成验算：4 项和=351,217,174；+106,069,513=457,286,687 → **解码列序自洽** |
| 12 | MSFT p.35「Microsoft 365 Consumer subscribers was removed as a metric」；p.36 仅增长率指标（seat/revenue growth/Azure growth）；p.84 收入表（In millions，仅美元额）；p.83 RPO $684B 存量 | `US-MSFT-2026.txt` L734 / L745-756 / L4790-4796 / L4057 | ✅ 支撑「量价不按所需粒度披露」 |

R3（引文逐字可核）等价复算：validator GREEN rc0 = 全部 quote 落在引用行域内。

### 2.2 E 段残差独立重算（我手算，非引用产物）

```
ZJ-MIN-M09   Σqty×price = 131,491,532,271 元   Σdisclosed = 131,489,500,000 元
             残差 = −2,032,271 元 = −0.001546%   冻结合计容差 ±0.05%（±65,744,750 元）→ 内 ✅
             8 线逐条在 ±0.10% 内；银线 −0.0723%（价格半 ulp 界 0.0727%）为最大者 ✅
             逐线残差：金锭 −302,580 / 金精矿 +244,740 / 铜精矿 +261,146 / 电积铜 +2,165
                      / 电解铜 +37,308 / 矿山产锌 −47,530 / 银 −2,137,520 / 铁精矿 −90,000
ZJ-SMT-M09   Σ = 183,988,605,486 vs 183,988,510,000 → −95,486 元 = −0.000052%（±91,994,255）✅
             冶炼金 +367,500 / 冶炼铜 −326,038 / 冶炼锌 −136,948，逐线 ±0.10% 内 ✅
XM-PHONE-M03 165,200,000 × 1,128.7 = 186,461,240,000 vs 186,439,777,000（附註5）
             → −21,463,000 元 = −0.011512%（冻结 ±0.05% = ±93,219,889）✅
XM-EV-M03    411,082 × 251,171 = 103,251,877,022 + 2,800,000,000（28 億元）= 106,051,877,022
             vs 106,069,513,000 → +17,635,978 元 = +0.016627%（冻结 ±0.10% = ±106,069,513）✅
```

- 四个残差与 oracle 冻结值、`historical_reconciliation` 三处**逐位一致**（我独立重算，不引用其产物）。
- `residual_decomposition` 五类（量/价/汇率/范围/确认时间）齐备且各有 value 或 basis（R4c ✅）；`no_parameter_backsolved_from_revenue=true` —— 复核 D 段每个量/价字段均有独立 `source`（我抽读全部量价字段），**未发现任何由收入倒推的参数（R4b ✅）**。
- L2 范围桥按冻结规则**不入容差门**，只须量化 + `partially_explained`：紫金 −产品口径→分部 gap +6,782,172,956 / +5,695,369,295 ✅ 已量化标记；小米两桥为构成项（trivial_composition，我已用附註5构成验算确认）✅。

### 2.3 探针（同值 low/base/high 手算核 + spy 计数）

| case | 我重算的期望值 | 留档 normal 臂输出（3 情景同值） | spy 计数（冻结期望 / 留档 / **我重跑**） |
|---|---|---|---|
| ZJ-MIN-M09 | 8 条 量×价（§2.2） | 8/8 相等、`matches_frozen_expected=true` | 24 / 24 / **24** ✅ |
| ZJ-SMT-M09 | 3 条 | 3/3 相等 | 9 / 9 / **9** ✅ |
| XM-PHONE-M03 | 186,461,240,000 | 相等 | 3 / 3 / **3** ✅ |
| XM-EV-M03 | 106,051,877,022 | 相等 | 3 / 3 / **3** ✅ |

标签面：20 个 `probe_result.json` 全带 `historical_mapping_probe=true`、`NOT_a_three_scenario_forecast=true`、`accuracy_evidence=false` ✅；MSFT 两 case 在 `historical_mapping_probe.not_run` 有 `probe_status=not_run` + `not_run_reason` ✅（`probe_runs/` 下确无 MSFT 目录 ✅，与 oracle §3「probe NOT run」冻结期望相符）。

---

## 3. STOP 条款（四条逐字评估 + 独立复核）

**§0 退出诚实块**逐字引用卡文四条停止条款 ✅（`decision.md` L12-15 与卡文 L24-27 逐字一致），且逐条给出实测评估：

1. **STOP_SELECTION_OR_EVIDENCE — 不触发** ✅：采用清单冻结（6 case / 26 未采用 model_id 登记理由 / 31 个 model_id 全覆盖——我实测 `total_models=31`、coverage 并集=31、not_selected 无理由=0；其中 resource/subscription/usage_platform 的双列表条目均带 `companies_not_selected_for` 作用域说明，非矛盾）；三份来源可读——我重哈希 3 raw + 3 sidecar **全部等于冻结值**，且小米解码**重跑逐字节相同**（§6 F-I10A-1）。
2. **STOP_FORMULA_DEPENDENCY — 不触发** ✅（§1.3 实测 31/31）。
3. **STOP_DISCLOSURE_ADAPTATION — 部分触发（US-MSFT-2026）** ✅ 证据充分：
   - `MS-PBP-M05` 4 字段（average_customers / revenue_per_customer / timing_factor / usage_revenue）、`MS-IC-M06` 3 字段（eligible_activity / monetization_rate / fixed_revenue）**全部 `zero_filled=false` + reason**（我数：`zero_filled=false` 7 处、`zero_filled=true` **0 处**）；
   - 不倒推断言在案（reason 文本 + AD-11 明示「不补 0、不以收入倒推、不以增长率反推绝对量」，反例=RPO 摊回 ARPU 被拒）✅；
   - `historical_reconciliation` 两 case：`E_status=STOP_DISCLOSURE_ADAPTATION`、`level1=null`、`residual=null`（**无捏造残差**）✅；
   - **卡文原句逐字在案**：`decision.md` §0「**允许其他已合格分部保留局部结果（ZJ-MIN/ZJ-SMT/XM-PHONE/XM-EV 的 D/E/probe 成果保留），但不放行整个公司正式预测**」+ `disclosure_qualification.company_level["US-MSFT-2026"].note` 同句 ✅；`formal_company_forecast_cleared=false` ×3 ✅。
4. **STOP_QUALIFICATION_SCOPE — 不触发** ✅：R5 禁语扫描（`FORBIDDEN_CLAIMS` = 授予准确性资格/通过三情景/企业适配已通过/适配资格已签署/accuracy granted）在我的独立重跑中 **evidence 面 0 命中**；我又对整个 attempt 的 .md/.json（排除 iso/vendor/_scratch/command_runs/source_extracts）做了更宽扫描：16 处命中**全部**是（a）卡文停止条款逐字引用、（b）扫描词表自身的登记（oracle/decision/harness 代码）、（c）否定句（「本卡不授予准确性」「NOT granted」）、（d）RED 负例夹具构造串——**无一处构成主张** ✅。
   `disclosure_qualification.json` 内**无**「三情景/准确性通过/proven」表述；`accuracy.status=unproven` ×6、`granted` 仅出现在 `card_grants.accuracy = "NOT granted by this card"` ✅。

---

## 4. 携带（carries）核对

| 项 | handoff.json | disclosure_qualification.json | 源（I-07-B reviewer_report，我抽验） |
|---|---|---|---|
| 声明1「三公司仅来源准备通过，仍未授予正式预测资格。」 | ✅ 逐字 | ✅ 逐字 | ✅ 在场 |
| 声明2「缺一市场/真实路径不得总体写三市场通过。」 | ✅ 逐字 | ✅ 逐字 | ✅ 在场 |
| 声明3「恢复：保留已取得raw，只回退当前隔离变更。」 | ✅ 逐字（亦见 `recovery/README.md` 引用） | ✅ 逐字 | ✅ 在场 |
| `overall_three_market_pass=false` | ✅（+ NEGATIVE 说明） | ✅ | ✅（I-07-B 字面 false） |
| `zero_RevenueSourceRecord_measured_fact=true` | ✅ | ✅ | ✅（I-07-B §4 F3 实测） |
| F1 / F2 / F3 路由 | ✅ 各带路由（owner / I-06-A OPEN-5 / D-W06 OPEN-4） | ✅ 三条 ID 在 `carried_findings` | ✅ I-07-B §F1/F2/F3 章节在场（L142/L158/L175、路由 L335-336） |

validator R8 等价复算：我重跑 GREEN 无 R8 违例 ✅。`carries_rule`（下游引用须带三句+false+实测事实）写入 handoff ✅。

---

## 5. 判据链（rgm：红→绿→变异）独立重跑

我的重跑全部在 `%TEMP%\i10a_review_rerun\`（产物不落 attempt），解释器=`<attempt>/iso/venv/Scripts/python.exe`（实现者同款，`-X utf8 -B`，`PYTHONIOENCODING=utf-8`）：

| 面 | 实现者留档 | **我的独立重跑** | 判定 |
|---|---|---|---|
| probe normal ×4 | rc 0/0/0/0，计数 24/9/3/3，输出=冻结值 | **rc 0/0/0/0，计数 24/9/3/3，8+3+1+1 实例 `matches_frozen_expected=true`、`low_base_high_identical=true`** | ✅ 复现 |
| probe red_conv ×4 | rc2 ×4 | （同族由下述 validator/probe 结构等价覆盖；留档臂我逐个读过 `business_verdict=correctly_rejected`） | ✅ |
| probe mut_swap_ids ×4 | rc2 ×4（产品维度检查先拒，注册调用 0） | 留档读取确认 `counts=0` + `refusals` 非空 | ✅ |
| probe mut_swap ×4 | rc3 ×4（等价变异体，F-I10A-3） | 留档读取确认输出与冻结值相等故无 mismatch | ✅ |
| probe mut_omit_optional | 3×rc3 存活 / XM-EV rc2 | **XM-PHONE rc3（存活）、XM-EV rc2（击杀）** | ✅ 复现（F-I10A-2 现场实证） |
| validator GREEN（真实产物） | 首跑 rc3=14 项 → GREEN-2 rc0 → GREEN-3 rc3(1×R12) → GREEN-4 rc0 | **rc0（n_all=0）** | ✅ 复现 |
| validator RED F-A..F-E | rc2 ×5（族非空转） | **rc2 ×5**（relevant 30/5/6/4/9） | ✅ 复现 |
| validator MUT F-A..F-E | 首遍 2/3/2/2/2 → MUT-F-B-2 rc2 → MUT3 2/2/2/2/2 | **rc2 ×5**（relevant 1/1/2/2/1） | ✅ 复现 |
| 解码（F-I10A-1 面） | mapped 272,511 / unmapped 0，out sha `91ad3f32…` | **rc0、mapped 272,511 / unmapped 0、`pdf_unchanged=true`、out sha 与留档逐字节相同** | ✅ 可复现 |

GREEN 首跑 14 项我逐条读过原始 `validate_result.json`：R2×2 + R3×6 + R9×6 = 14（**与 decision §2.2 的分类记述有 1 项出入 → F-REV-I10A-2**，总数与红→绿轨迹不受影响）。RED/MUT 夹具在我重跑中的违例族与留档一致（同夹具、同代码 → 确定性复现）。

---

## 6. Findings 裁定

### 卡面 4 条（我独立核实）

- **F-I10A-2（产品缺陷，HIGH）— 核实成立，已立修卡**。
  我在**生产文件本体**上确认：`scripts/forecast/calc.py:126-136` `_optional_series(..., default: float = 0.0)` 在 `driver not in driver_ids` 时返回 `[default]*len(years)`（**静默补 0**）；`scripts/forecast/segments.py:101-110` 对 `spec["optional"]` 逐个以 `float(spec.get("defaults", {}).get(driver, 0.0))` 调用它 —— **forecast 入口层**对无显式省缺仍静默补 0；iso 副本与生产两文件**逐字节相同**（我用 Compare-Object 验证，且 sha 等于冻结锚）。
  行为实证：`mut_omit_optional` 3/4 存活（ZJ-MIN/ZJ-SMT/XM-PHONE 的 other_revenue=0 被静默填而无错），XM-EV 因 0≠2.8e9 的输出差被检出（rc2）—— **我重跑复现（XM-PHONE rc3 / XM-EV rc2）**。
  → 路由：**修卡 `I10A-F2-FIX`（ref `e1c31937`）已由父代理立卡**（REMEDIATION_REGISTER §一〇四）；本卡不修产品（产品零变更 ✅）。
- **F-I10A-1（工具缺陷，MEDIUM）— 核实成立**。`superseded_pdftotext/` 两份 0-CJK 抽取留档；解码法=原件自带 HYQiHei-FES `cmap`（28,873 字形）反查。**我独立重跑解码：逐字节相同、unmapped=0**，构成方法可复现性硬证据。叙述/算术交叉验证（手机 1,864 億 ↔ 附註5 186,439,777 千元；EV 1,061 億 ↔ 106,069,513 千元；附註5 七列构成和自洽）也一致。
  「封面对照 8 组字形」→ 见 **F-REV-I10A-4**（只有 4 组可枚举）。
- **F-I10A-4（口径发现，INFO）— 我的裁定：属「舍入」而非「基准差」（rounding-vs-basis 规则）**。
  实算：39,757,980,000 ÷ 49,074,000 克 = **810.163834** ≠ round(810.163834)=810.16 vs 披露 810.17；残差 −302,580 元。
  半 ulp 检验（我的行业判据）：−302,580 ÷ 810.17 = **373.5 克 = 0.3735 千克 ≤ 0.5 千克**（披露销量以整数千克计量的半 ulp）→ **披露销量的呈现舍入即可完全解释该残差**；等价地 `金额/单价 = 49,073,626.5 克 → 四舍五入到 49,074 千克` 自洽。
  **结论**：不是口径/基准差异，不涉及收入金额（p.44 金额列 = p.45 分产品收入列，逐字段相等）；AD-8 presentation flag 保留作披露精度提示，**不需要重述、不影响本案签署**；若后续披露给出更细销量/单价基准，按卡文 6 记 delta。
- **F-I10A-3（等价变异体，INFO）— 披露接受**。`mut_swap`（量价**值**互换）因乘法交换律输出恒等 → rc3 属**预期等价性**；oracle §3 的维度错配预期由 `mut_swap_ids` 臂满足（4/4 击杀，产品维度检查先拒、注册调用 0）。**残余风险备忘（交 owner 面）**：同维值互换在产品层不可检（bounds 未拦截），其收入结果无害（a×b=b×a），但会使诊断性隐含单价失真；是否要求注册层禁止同 dimension 双驱动歧义，留 owner 裁定（handoff open_questions 已载）。

### 本轮新增（均为簿记/文档类，不阻断）

- **F-REV-I10A-1（LOW·簿记）**：`handoff.current_source_hashes` 与 `changes.diff` 中 **两枚 63 位 sha pin**（`disclosure_mapping.json`、`model_DE_evidence_manifest.json`）——各缺 1 个十六进制字符（我用删除位置比对确认：disclosure 缺 index23 的 `f`、model_DE 缺 index15 的 `e`），因此**按字面不可验证**。真实文件完好：`model_DE_evidence_manifest.aggregate_files` 内的 64 位 pin 与我实测相等。→ 建议以勘误方式补正 pin（不改证据文件内容）。
- **F-REV-I10A-2（LOW·文档）**：`decision.md §2.2 注1` 把 GREEN 首跑 14 项记作「R2×2 + R3×5 + R9×6 + R12×1」；原始 `CMD-I10A-VALIDATE-GREEN/validate_result.json` 实为 **R2×2 + R3×6 + R9×6（无 R12）**，R12 首次命中发生在 GREEN-3（1 项，XM-EV raw 形态）。总数 14 正确、红→绿轨迹成立，**分类记述有 1 项出入**。
- **F-REV-I10A-3（LOW·冻结件转写）**：`oracle_expected.json` 中 ZJ-MIN `aggregate_tolerance_abs=65,724,750`，而同文件 `0.0005 × 131,489,500,000 = 65,744,750`（差 −20,000 / −0.03%）；其余 3 case 该字段自洽。我 grep 确认该字段**在 harness 中只定义、不被任何门使用**（门全部用 `aggregate_tolerance_rel`），残差 −2,032,271 距任一值均有 30 余倍余量 → **不影响任何判定**；按冻结纪律**不回改**，登记为披露性转写差错。
- **F-REV-I10A-4（INFO·证据可枚举性）**：`decision.md:97/:130` 称「封面对照 8 组字形」，但证据面只枚举到 **4 组**（`decode_hk_text.py:159` 股=20579/份=7871/幣=11813/港=15857；`commands.json` 另记 年=11830）。其余 4 组未在案 → 8 组之说**部分可核**；0-unmapped 与方法可复现性我已硬证（§5），全表字形共享假设仍为开放项（实现者 §6.1 自述一致）。
- **F-REV-I10A-5（LOW·自指簿记）**：`changes.diff` 内 70 枚 pin 我全量复算：**68 中 2 不中**——`run_log.jsonl`（`96657544…` vs 实际/终态 `16e466c4…`）与 `README.md`（`f3551454…` vs 实际 `c1c71491…`）。两者均为 changes.diff 生成**之后**又追加/更新的活文件（run_log 由命令自身追加；README 是 live working document），属**自指性时序**，非篡改；handoff 的 run_log pin 是正确终态。建议后续批次把这两项标为 `excluded (live file)`。

---

## 7. 边界（Boundary）核对

| 组 | 冻结表 | **我实测重哈希** | 结论 |
|---|---|---|---|
| 产品锚 5 件（calc.py / segments.py / model_extensions.py / model_registry.py / revenue_constraints.py） | before==after | **5/5 相等**（并抽验 iso 副本与生产逐字节相同） | `anchors_identical=true` ✅ 产品零变更 |
| 来源 raw+sidecar 6 件 | before==after | **6/6 相等**（紫金 PDF/`.source.json`、小米 PDF/`.source.json`、MSFT HTM/`.source.json` 全部匹配冻结 sha） | `sources_identical=true` ✅ 未覆写原件 |
| 冻结计划/依赖输入 12 件 | before==after | **12/12 相等**（card/research_cards/common_research_cards/common_root_cards/model_cards/review_and_handoff/START_HERE/sample_manifest + I-00-B×2 + I-07-B×2） | `plan_inputs_identical=true` ✅ 未覆写旧审计 |
| iso 产品副本 8 件 | before==after | **8/8 相等** | `iso_copies_identical=true` ✅ |
| `changes.diff` 隔离面 pin | 70 枚 | 68 中、2 自指性不中（F-REV-I10A-5） | 隔离面清单完整 ✅ |
| git | `git_writes=0`（binding 禁 git） | 只读实测：`scripts/**` 对 index 与 HEAD **0 差异**；**尝试期间 0 新提交**（HEAD 仍为 2026-09-23 19:51 的 batch-9）；index 无 staged 变更。porcelain 中非 `.planning` 项仅 2 个 untracked（`.tmp-r41-mutation/`、`assurance/…/plan_inputs.json.bak`），均**非本卡 allowlist 面且非本 attempt 产物** | ✅ 无产品/索引写入 |
| network | `network_command_calls=0`（命令面） | 我本轮 0 网络调用；实现者 J-3 **主动披露** 诊断期 2 次 `web_fetch`（Adobe cmap-resources 参考表，存 `source_extracts/ref/` 并哈希，且作**否定检验**用、最终解码不依赖） | 命令面 0 成立 ✅；诊断面按披露接受（我无法独立审计历史网络面 → §9） |
| 旧审计覆写 | — | 12 件 plan inputs 全等 + attempt 目录为新建面 | ✅ |
| 写入面 | — | 我重跑只写 `%TEMP%`；attempt 树 3 小时内 0 修改 | ✅ |

---

## 8. 逐 case 签署表（行业/会计 reviewer）

签署效力：**仅 disclosure_adaptation、仅本案口径/期间（紫金/小米 FY2025；MSFT FY2026 D 段）**；不授予 accuracy、不授予任何公司正式预测放行、不外推 formula。

| case | 公司/分部/模型 | D | E | probe | 我的独立核算 | **结论（签署）** |
|---|---|---|---|---|---|---|
| **ZJ-MIN-M09** | 紫金 矿产品分部 / resource(M09) | 8 实例×3 字段，原文页/行全中 | Σ残差 −2,032,271（−0.001546%，冻结 ±0.05% 内）；L2 桥 +6,782,172,956 `partially_explained` | 24 调用，三情景同值=手算（我重跑复现） | 8 条 量×价 + 合计逐位重算 ✅；F-I10A-4 裁定=**舍入（销量粒度半 ulp 内）**，presentation flag 保留 | **accepted_scoped — 签署**（口径：主要产品 8 线同口径 E；L2 桥为已量化未分解开放项） |
| **ZJ-SMT-M09** | 紫金 冶炼产品分部 / resource(M09) | 3 实例×3 字段，原文页/行全中 | −95,486（−0.000052%）；L2 桥 +5,695,369,295 `partially_explained` | 9 调用，同值=手算（复现） | **保留案例 ①（冶炼产锌）逐手核算**：403,324 吨 × 20,327 元/吨 = **8,198,366,948** vs 披露 8,198,230,000 → −136,948（−0.0017%，线级 ±0.10%/合计 ±0.05% 内）✅；另 2 线同验 | **accepted_scoped — 签署**（保留案例通过） |
| **XM-PHONE-M03** | 小米 智能手機 / unit_sales(M03) | 1 实例×4 字段（p.21/p.337） | −21,463,000（−0.011512%，冻结 ±0.05% 内）；量/价舍入界已量化 | 3 调用，同值=手算（复现） | 165,200,000 × 1,128.7 = 186,461,240,000 与附註5 186,439,777 千元之差独立重算 ✅；解码我重跑逐字节复现 | **accepted_scoped — 签署**（口径：智能手機產品線量×价；構成桥 trivial 已验） |
| **XM-EV-M03** | 小米 智能電動汽車及AI等創新業務 / unit_sales(M03) | 1 实例×4 字段（含 other=28 億元→2.8e9） | **+17,635,978（+0.016627%，冻结 ±0.10% 内）** | 3 调用，同值=手算（复现）；mut_omit **rc2 击杀**（唯一 other≠0 case） | **保留案例 ②（预记预期后复验）**：oracle §1 冻结值 +17,635,978 → 我独立重算同值 ✅；411,082×251,171=103,251,877,022 + 2.8e9 复算 ✅ | **accepted_scoped — 签署**（保留案例通过；other_revenue 億元粒度 ±5e7 界已在容差依据内） |
| **MS-PBP-M05** | MSFT PBP / subscription(M05) | 4 字段全 missing（zero_filled=false，p.35/36/84 原文在案） | **STOP_DISCLOSURE_ADAPTATION**（E 未执行、无残差捏造） | 未运行（冻结期望=not_run ✅） | 量价披露粒度缺失我按原文复核成立（L734 指标删除、L745-756 仅增长率、L4790 仅美元额） | **不授予 disclosure_adaptation** —— 诚实出口确认：D 完成并保留，**公司正式预测不放行** |
| **MS-IC-M06** | MSFT IC / usage_platform(M06) | 3 字段全 missing（p.36/L232/p.83 RPO 存量） | **STOP_DISCLOSURE_ADAPTATION** | 未运行 ✅ | Azure 仅增长率（L755-756）、RPO 无 rollforward（L4057）复核成立 | **不授予 disclosure_adaptation** —— 同上 |

**保留案例结论**：① ZJ-SMT 冶炼产锌、② XM-EV（other≠0）**两案均在我手独立复算通过**，且两案都未参与实现者的修复迭代（实现者 §3.7 声明属实：GREEN 修复涉及行域/missing 清单/清单路径/XM-EV raw 形态——raw 形态更正只改 `raw_value` 呈现不改数值，我已用重算确认数值结论未变）。

**公司层**：CN-ZIJIN（2 分部适配）/ HK-XIAOMI（2 适配）/ US-MSFT（0 适配、2 STOP）→ **三家公司均未放行正式预测**（`formal_company_forecast_cleared=false` ×3 实测）。

---

## 9. 未验证 / 开放项（诚实清单，含继承项）

1. **渲染 PNG 的目视比对未由我完成**：我的模型无图像输入能力，`page_renders/*.png` 6 页仅做了哈希核对（7/7 与 changes.diff 相等）+ render manifest 一致性；原文核对改由解码文本 + 我的解码重跑 + 叙述/算术交叉验证承担。
2. **小米解码全表字形共享假设**：方法可复现性与 0-unmapped 已硬证，但全表逐字形独立验证未做（实现者 §6.1 自述一致）；「8 组对照」仅 4 组可枚举（F-REV-I10A-4）。
3. **AD-7 special_review**（机制混合分部：ZJ-其他 / 小米互聯網服務 / MSFT-MPC 拆分适配）— **留待独立裁定，本轮不宣称适配通过**（保持开放）。
4. **L2 范围桥 gap 逐项分解**（紫金两分部 +6,782,172,956 / +5,695,369,295）：披露无表外产品明细 → `partially_explained` 为上限结论（保持开放）。
5. **MSFT E 缺口能否由外部独立披露补足**（季度补充/指引）：超出本卡信息面（三份原件），未查证（保持开放）。
6. **紫金 2024 对照列未纳入复建**（E 面=单个已结束期间 FY2025；双期复建留 I-12 口径）（保持开放）。
7. **mut_swap 等价性在 `timing_factor≠1` 时的边界**（实现者 §6.6 自述；本轮 timing=1）。
8. **网络面历史审计**：我只能核对 binding/handoff 的命令面 0 与 J-3 的主动披露，无法独立证明诊断期之外无任何网络访问（无网络审计日志可查）。
9. **model_registry 晋级（I-10-B 修复后 62f864b9…）的授权**：属 owner 决策，本卡按当前字节适配并锚定（实现者 §6.7 自述一致）；我不对该晋级背书。
10. **机读资格状态尚未落账**：`disclosure_qualification.json` 仍为 `unmapped/signed=false`、`independent_adaptation_review.md §5` 签署区仍留白（我无权改实现者文件）——**我的签署只存在于本报告**；下游须以本报告为签署面，或由父代理按流程把签署转记入卡内产物（转记是簿记，不是实现者自签）。
11. **M01–M31 逐卡资格正文**：我核了 sweep 汇总（31/31）+ 4 张卡的 qualification.json 哈希与三态抽验，未逐卡通读 31 份正文。

---

## 10. 接受范围（Scope-if-accepting）与下游指令

1. **6 case 已 disposition**：4 case `disclosure_adaptation = accepted_scoped`（本报告签署）/ 2 case STOP_DISCLOSURE_ADAPTATION 诚实出口（不授予）。
2. **`disclosure_adaptation` 机读状态在卡内仍为 `unmapped`**，直到签署按流程落账；**不得**由实现者自签。
3. **F-I10A-2 → 修卡 `I10A-F2-FIX`（ref `e1c31937`）已立**（父代理派单，REMEDIATION_REGISTER §一〇四）；本卡不改产品。
4. **承继开放项**：AD-7 special_review + L2 桥 gap + 字形共享假设 + MSFT E 外部证据 + 紫金 2024 双期复建 —— 全部**保持开放**并随 handoff 下行。
5. **`formula = accepted_scoped`（M01–31 面）** 不因本卡提升或外推；**`accuracy = unproven`**；**无任何公司获正式预测放行**。
6. 三句声明 + `overall_three_market_pass=false` + `zero_RevenueSourceRecord` 实测事实 → **任何下游引用必须逐字携带**。
7. F-REV-I10A-1..5 建议以勘误/登记方式处理（不改冻结件、不改证据文件内容）。

---

## 11. REM-79 自查 + 方法学声明

- **REM-79（双向差集）自查**：我给出的每个扫描型结论都按**两个方向**核过并在句中带域——
  (a) 禁语面：`FORBIDDEN_CLAIMS ∖ evidence/I-10-A(.json/.md)` = **0 命中**（域=evidence 面 .json/.md）；宽域（attempt 全 .md/.json，排除 iso/vendor/_scratch/command_runs/source_extracts）16 处命中逐条给上下文=全为引用/词表/否定句/负例构造串（域=宽域）；
  (b) 必需面：三句声明 ∖ {handoff, disclosure_qualification, I-07-B 源} = **0 缺失**；`overall_three_market_pass` 与 `zero_RevenueSourceRecord_measured_fact` 在两处皆字面 `false`/`true`。
  即：不只报「没发现坏的」，也报「该在的都在」，两个差集都写明域。
- **工具面**：所有 Python 判据重跑以 `PYTHONIOENCODING=utf-8` + `-X utf8 -B` 执行（无 `.pyc` 落盘）；解释器=attempt 内 iso venv（未用全局 Miniconda）；`%TEMP%` 仅作复核暂存（`%TEMP%\i10a_review_rerun\`），实现者卡内 %TEMP% 面保持「未使用」不变。
- **独立性**：本报告全部结论基于我自己读取/重算/重跑的证据；对实现者产物**零写入、零修改、零自签**。

---

## 12. 签署区

- **Reviewer 身份**：独立行业/会计 reviewer（N=1，未参与 I-10-A 实现；独立验证者义务：原文核对 ≥5 条引文 ✅（实做 12 条）、手算 oracle 复算 ≥1 条 ✅（实做 4 案 + 13 线）、保留案例复验 ✅（两案））
- **结论**：**`accepted_scoped`**
- **授予范围**：ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03 的 **disclosure_adaptation**（各限该公司/分部/口径/FY2025）
- **不授予清单**：accuracy（unproven）· MSFT 两 case 的 disclosure_adaptation（STOP）· 任何公司正式预测放行 · 来源链资格（I-07-B 实测 zero RevenueSourceRecord）· 三情景预测（探针仅 historical_mapping_probe）· formula 外推
- **保留复验案例与预期**：① ZJ-SMT 冶炼产锌（403,324×20,327 = 8,198,366,948，残差 −136,948，容差内）✅ 通过；② XM-EV other≠0（残差 +17,635,978，±0.10% 内）✅ 通过
- **签署**：`accepted_scoped — signed by the independent INDUSTRY/ACCOUNTING reviewer in this reviewer_report.md`（实现者未签、本报告非实现者产物）
- **日期**：2026-09-24（本地）

（报告完；配套哈希见 `reviewer_report.md.sha256`）
