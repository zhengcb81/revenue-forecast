# I-10-A / a20260923-01 — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = **`accepted_scoped`** — **transcribed verbatim** from the carrier (L15 = ``**`accepted_scoped`**``), granted scope and non-grants per §0 verdict table (L17–L26) and the §12 signature block (L292–L298): 4 GREEN case 的 **disclosure_adaptation 授予并签署**（限各该公司/分部/该口径/FY2025）· 2 STOP case **诚实出口、不授予** · `accuracy = unproven` · formula 维持 M01–M31 `accepted_scoped` 不外推 · **0 家公司放行正式预测** · 产品面零变更 · 发现 = 卡面 F-I10A-1..4 全部核实/裁定 + 新增 F-REV-I10A-1..5（全 non-blocking）。
- **carrier** = `reviewer_report.md`（attempt 内相对路径 `execution_runs/I-10-A/a20260923-01/reviewer_report.md`）
- **carrier sha256** = `6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb` — **35164 B / 300 行**，落定时刻只读独立复算 == 派单 pin == 侧车读回（三方相等）；编码 UTF-8 无 BOM（首 3 字节 `23 20 49` = `# I`）、**LF-only（CR=0）**、单尾 LF（尾字节 `… 0a`）。
- **pin** = `reviewer_report.md.sha256`（**85 B**，侧车自身 sha256 `6f37ee2941c260cd27aa83c0a823bac81143ed25bbd7900445e9c53bbd5f46c1`）内容 = `6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb  reviewer_report.md` —— **读回相等**（逐字节 == live 复算）。本 pass 对 carrier 与侧车写入 **0 字节**。
- **reviewer / N=1** = 独立行业/会计 reviewer（N=1，未参与本卡实现；父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单），复核日期 2026-09-24（本地）；方法边界 = read/grep/pwsh only、判据重跑全落 `%TEMP%\i10a_review_rerun\`、attempt 树与产品树零写入、git 仅只读、network=0（carrier L3/L9）。
- **nature of this file** = bookkeeping transcription（簿记转录）：本文件转录独立复核的裁决词、签署表与限定，**自身不授予任何东西、不添加任何验收**。签署面 = `reviewer_report.md`；**落账是簿记转录，不是实现者自签**（`verdict_is_transcribed_not_authored = true`；`implementer_signed = false`；`implementer_never_signs_acceptance = true`；独立复核 **N=1**）。
- `review.md` 此前不存在于本 attempt（无实现方 stub）；由 carrier-landing 簿记 pass 创建 —— 既非实现方所写、也非复核员所写（复核员的原词在 `reviewer_report.md`，本 pass 0 字节触碰）。

**ruling location**（1-based 行、包含端；byte proof = 对 carrier_sha256 态文件的 0-based 字节偏移，多行区域含内部 LF、不含该区末行的行尾 LF）：

| 区域 | 行 | bytes | len | sha256 |
|---|---|---|---|---|
| 标题/meta/方法边界 | L1–L9 | 0..1210 | 1211 | `5e7aab2b0776ce88bad695ac8190d061dad362ecc38109354698e3f26bb5f0fa` |
| `## 0. 结论（Verdict）` 标题 | L13–L13 | 1218..1242 | 25 | `940283e51dc8be78d7636a7d6a26e2d705ed0c7a9c5d112135c52d9f52e05cfd` |
| **verdict 行** = ``**`accepted_scoped`**`` | L15–L15 | 1245..1265 | 21 | `d5d57bf2b14aa9bace032212a8e5de338b7290f04fabb2529b15bc9ce39ebc32` |
| **verdict 块**（标题+verdict 行+八行结论表+判据链复现句） | L13–L28 | 1218..2933 | 1716 | `ffdf6160f16c485e7814805b477a9bbe3dd25e70f83d0df19a0f9354ffb61cc5` |
| §1 交付物与完整性 | L32–L81 | 2941..7067 | 4127 | `d44c1e1f89aef036a8d4eeec6607e688c588445b71f67ed0be834d62846d43f1` |
| §2 逐 case 抽查复算 | L83–L137 | 7070..12258 | 5189 | `643c5c1e2fac97e6248f568490630dfeba1e9d84f0411b035f5b8396dfa59a63` |
| §3 STOP 条款 | L139–L153 | 12261..14949 | 2689 | `008ff3cc71dc886c368150b22e5df200858966bc2ffae69d07afc18e4129b331` |
| §4 携带（carries）核对 | L155–L168 | 14952..16049 | 1098 | `a3d7512e81683cbeffd4c7139c8cb71c68b1e0aa9e1f73a0df88e9749236cb16` |
| §5 判据链独立重跑 | L170–L187 | 16052..18076 | 2025 | `168cf7b93ee37aac328a9bf937b753d28b8bc3e300329a48c263922020d50e5d` |
| §6 Findings 裁定（卡面 4 条 + F-REV 5 条） | L189–L214 | 18082..23568 | 5487 | `1614901e774eb0fa23989245f2a7d9b696b4ed5877cdfdd8a24d4a7c5ae6e6ba` |
| └ 其中 **F-REV-I10A-1..5** | L206–L212 | 21119..23563 | 2445 | `9122ea773a050ef3999ddcbca393d53929581870b875573270d8fa4b073da09c` |
| §7 边界（Boundary）核对 | L216–L229 | 23571..25586 | 2016 | `531edc4235209484f5f11ba4db4ef4e09f18a44f67cacf99b180840a304d6ad0` |
| §8 签署区（整节） | L231–L248 | 25592..29337 | 3746 | `6057fa94316b076b7e6fd0020fd0565488bdceb06f4e4e02dfcdd2d586ad079f` |
| └ **逐 case 签署表（verbatim 转录源）** | L236–L243 | 25850..28755 | 2906 | `8b95463f94eb75d715c95aa39a3d04c09d1d39e61a8b601f9682681b2b4da9f9` |
| §9 未验证/开放项（11 条） | L251–L264 | 29344..31614 | 2271 | `490b20ca5221d54c6525e4b128ee344a8b07944443bb5a633c22ab0436f93e82` |
| §10 接受范围（Scope-if-accepting）与下游指令 | L267–L276 | 31621..32713 | 1093 | `7011705ac85224ead49a577fd650d2ae4952f95ea992dad8196d13ea366a61f9` |
| §11 REM-79 自查 + 方法学声明 | L279–L287 | 32720..33943 | 1224 | `b307a6b741800e26d0d9dbedd1f3b52d42712ca5bf2cf13e8e774e09ffccb034` |
| §12 签署区（结论/授予/不授予/两保留案/签署行/日期） | L290–L300 | 33950..35162 | 1213 | `a6f8a9899e7adca346231dfabab1b166e04ba23f3246171fbfb48a72d21a5792` |

实现方状态核对（carrier L7）：落账前 `handoff.status=review_pending`、`implementer_signed=false`、`implementer_never_signs_acceptance=true` ✅ —— 本报告是实现者之后的第一步。

---

## Corrections applied FIRST（append-only erratum，先于三件落定写入）

`decision.md` 追加 **`## F-REV-I10A erratum (landing)`** 一节（唯一更正载体；上文原文一字未改）：

- sha256 before → after = `c84493fcba377aca40276f4f37ebc0e1812a15705ed8760a23af2210a05b2b6c`（13542 B / 138 行）→ **`63afc8dd8707b3353ca205fe8b711ea3149a767d3ed5ae62753ff0c6660a815d`（18035 B / 181 行）**
- 内容 = F-REV-I10A-1..5 逐条落定（详下 Findings 表）；-1 的两枚 corrected 64 位 pin 在该节登记、原件不回写；-2 的权威分类 R2×2+R3×6+R9×6 与原分类文字并存留痕。

---

## Per-case sign-off table（verbatim 转录自 carrier §8 L236–L243，byte 区 25850..28755）

签署效力（L234，逐字）：**仅 disclosure_adaptation、仅本案口径/期间（紫金/小米 FY2025；MSFT FY2026 D 段）**；不授予 accuracy、不授予任何公司正式预测放行、不外推 formula。

| case | 公司/分部/模型 | D | E | probe | 我的独立核算 | **结论（签署）** |
|---|---|---|---|---|---|---|
| **ZJ-MIN-M09** | 紫金 矿产品分部 / resource(M09) | 8 实例×3 字段，原文页/行全中 | Σ残差 −2,032,271（−0.001546%，冻结 ±0.05% 内）；L2 桥 +6,782,172,956 `partially_explained` | 24 调用，三情景同值=手算（我重跑复现） | 8 条 量×价 + 合计逐位重算 ✅；F-I10A-4 裁定=**舍入（销量粒度半 ulp 内）**，presentation flag 保留 | **accepted_scoped — 签署**（口径：主要产品 8 线同口径 E；L2 桥为已量化未分解开放项） |
| **ZJ-SMT-M09** | 紫金 冶炼产品分部 / resource(M09) | 3 实例×3 字段，原文页/行全中 | −95,486（−0.000052%）；L2 桥 +5,695,369,295 `partially_explained` | 9 调用，同值=手算（复现） | **保留案例 ①（冶炼产锌）逐手核算**：403,324 吨 × 20,327 元/吨 = **8,198,366,948** vs 披露 8,198,230,000 → −136,948（−0.0017%，线级 ±0.10%/合计 ±0.05% 内）✅；另 2 线同验 | **accepted_scoped — 签署**（保留案例通过） |
| **XM-PHONE-M03** | 小米 智能手機 / unit_sales(M03) | 1 实例×4 字段（p.21/p.337） | −21,463,000（−0.011512%，冻结 ±0.05% 内）；量/价舍入界已量化 | 3 调用，同值=手算（复现） | 165,200,000 × 1,128.7 = 186,461,240,000 与附註5 186,439,777 千元之差独立重算 ✅；解码我重跑逐字节复现 | **accepted_scoped — 签署**（口径：智能手機產品線量×价；構成桥 trivial 已验） |
| **XM-EV-M03** | 小米 智能電動汽車及AI等創新業務 / unit_sales(M03) | 1 实例×4 字段（含 other=28 億元→2.8e9） | **+17,635,978（+0.016627%，冻结 ±0.10% 内）** | 3 调用，同值=手算（复现）；mut_omit **rc2 击杀**（唯一 other≠0 case） | **保留案例 ②（预记预期后复验）**：oracle §1 冻结值 +17,635,978 → 我独立重算同值 ✅；411,082×251,171=103,251,877,022 + 2.8e9 复算 ✅ | **accepted_scoped — 签署**（保留案例通过；other_revenue 億元粒度 ±5e7 界已在容差依据内） |
| **MS-PBP-M05** | MSFT PBP / subscription(M05) | 4 字段全 missing（zero_filled=false，p.35/36/84 原文在案） | **STOP_DISCLOSURE_ADAPTATION**（E 未执行、无残差捏造） | 未运行（冻结期望=not_run ✅） | 量价披露粒度缺失我按原文复核成立（L734 指标删除、L745-756 仅增长率、L4790 仅美元额） | **不授予 disclosure_adaptation** —— 诚实出口确认：D 完成并保留，**公司正式预测不放行** |
| **MS-IC-M06** | MSFT IC / usage_platform(M06) | 3 字段全 missing（p.36/L232/p.83 RPO 存量） | **STOP_DISCLOSURE_ADAPTATION** | 未运行 ✅ | Azure 仅增长率（L755-756）、RPO 无 rollforward（L4057）复核成立 | **不授予 disclosure_adaptation** —— 同上 |

- **签署合计 = 4 签 + 2 STOP**：ZJ-MIN（−0.001546%）/ ZJ-SMT（−0.000052% + 保留案例①冶炼产锌通过）/ XM-PHONE（−0.011512% + §2.1 全表 **12 条引文行核** ≥5 义务达成）/ XM-EV（+0.016627% + 保留案例②预记预期后复验同值）四案 **accepted_scoped — 签署**；MS-PBP + MS-IC **STOP 不授予**。
- **STOP 机读面**（carrier §3，独立复核实测）：missing 字段合计 **7 处**（MS-PBP 4 + MS-IC 3）**全部 `zero_filled=false` + reason**，`zero_filled=true` **0 处、0 补零**；`historical_reconciliation` 两 case `E_status=STOP_DISCLOSURE_ADAPTATION`、`level1=null`、`residual=null`（无捏造残差）；不倒推断言在案（AD-11）。→ `cleared = false`：三家公司 `formal_company_forecast_cleared=false` ×3。
- **保留案例结论（L245，逐字要点）**：① ZJ-SMT 冶炼产锌、② XM-EV（other≠0）**两案均在复核手独立复算通过**，且两案都未参与实现者的修复迭代；**公司层（L247）** CN-ZIJIN 2 适配 / HK-XIAOMI 2 适配 / US-MSFT 0 适配 2 STOP → **三家公司均未放行正式预测**。

---

## What the review established (transcribed from `reviewer_report.md`)

### 独立重跑（carrier §0 L28 + §5 L170–L187）

| 面 | 实现者留档 | **复核独立重跑** |
|---|---|---|
| probe normal ×4 | rc 0/0/0/0，计数 **24/9/3/3**，输出=冻结手算值 | **rc 0/0/0/0，计数 24/9/3/3**，8+3+1+1 实例 `matches_frozen_expected=true`、`low_base_high_identical=true` ✅ |
| probe red_conv ×4 | rc2 ×4 | 留档臂逐个读过 `business_verdict=correctly_rejected` ✅ |
| probe mut_swap_ids ×4 | rc2 ×4 | 留档读取 `counts=0` + `refusals` 非空 ✅ |
| probe mut_swap ×4 | **rc3 ×4**（等价变异体，F-I10A-3） | 留档读取：输出与冻结值相等故无 mismatch ✅ |
| probe mut_omit_optional | 3×**rc3** 存活 / XM-EV **rc2** 击杀 | **XM-PHONE rc3（存活）、XM-EV rc2（击杀）** ✅（F-I10A-2 现场实证） |
| validator GREEN（真实产物） | rc3(14) → GREEN-2 rc0 → GREEN-3 rc3(1×R12) → GREEN-4 rc0 | **rc0（n_all=0）** ✅ |
| validator RED F-A..F-E | rc2 ×5 | **rc2 ×5**（relevant 30/5/6/4/9）= **5/5 击杀** ✅ |
| validator MUT F-A..F-E | 首遍 2/3/2/2/2 → MUT-F-B-2 rc2 → MUT3 2/2/2/2/2 | **rc2 ×5**（relevant 1/1/2/2/1）✅ |
| 小米解码（F-I10A-1 面） | mapped **272,511** / unmapped **0**，out sha `91ad3f32…` | **rc0、272,511 / 0、`pdf_unchanged=true`、out sha 与留档逐字节相同** ✅ |

- 判据链全部复现于 `%TEMP%\i10a_review_rerun\`（解释器 = attempt 内 iso venv，`-X utf8 -B`、`PYTHONIOENCODING=utf-8`）。
- 逐 case 残差独立手算（§2.2 L108–L120）：ZJ-MIN −2,032,271（−0.001546%）· ZJ-SMT −95,486（−0.000052%）· XM-PHONE −21,463,000（−0.011512%）· XM-EV +17,635,978（+0.016627%）——与 oracle 冻结值、`historical_reconciliation` 三处逐位一致；`no_parameter_backsolved_from_revenue=true`（R4b ✅）、五类残差分解齐备（R4c ✅）。
- D 段引文义务 ≥5 条 → **实测 12 条**（§2.1 L89–L102，含小米附註5 七列构成验算 4 项和=351,217,174 → +106,069,513=457,286,687 解码列序自洽）；R3 等价复算 = GREEN rc0。

### Findings 裁定与处置

#### 卡面 4 条（carrier §6 L192–L204）

| ID | 裁定 | 本 landing 处置 |
|---|---|---|
| **F-I10A-2**（产品缺陷，HIGH） | **核实成立**：产品本体证明 —— `scripts/forecast/calc.py:126-136` `_optional_series(..., default: float = 0.0)` 在 `driver not in driver_ids` 时返回 `[default]*len(years)`（静默补 0）；`scripts/forecast/segments.py:101-110` 对 `spec["optional"]` 逐个以 `float(spec.get("defaults", {}).get(driver, 0.0))` 调用它 —— **forecast 入口层**对无显式省缺仍静默补 0；iso 副本与生产两文件逐字节相同（Compare-Object 验证 + sha 等于冻结锚）。行为实证 = mut_omit_optional **3/4 存活**（ZJ-MIN/ZJ-SMT/XM-PHONE 的 other_revenue=0 被静默填而无错），XM-EV 因 0≠2.8e9 输出差被检出（rc2）——复核重跑复现（XM-PHONE rc3 / XM-EV rc2） | **修卡已立**：`I10A-F2-FIX`，**ref `e1c31937`**，`REMEDIATION_REGISTER.md` **§一〇四**（L1981 节题；L2090 记 F-I10A-2 产品本体实证 `calc.py:126-136`+`segments.py:101-110` iso==生产 → 修卡 `e1c31937` 引证 ✓）。**本卡不修产品、产品零变更** |
| **F-I10A-1**（工具缺陷，MEDIUM） | **核实成立**：pdftotext 0-CJK；解码法 = 原件自带 HYQiHei-FES cmap（28,873 字形）反查；复核独立重跑**逐字节相同、unmapped=0** = 方法可复现性硬证据；叙述/算术交叉验证一致。「封面对照 8 组字形」→ **F-REV-I10A-4**（只 4 组可枚举） | 证据留存 `superseded_pdftotext/` + 解码 manifest；后续卡建议沿用 `decode_hk_text.py` 路径（open_questions 在册） |
| **F-I10A-4**（口径发现，INFO） | **裁定 = 「舍入」而非「基准差」**（rounding-vs-basis 规则）：实算 39,757,980,000 ÷ 49,074,000 克 = 810.163834 ≠ 810.17；半 ulp 检验 **−302,580 ÷ 810.17 = 373.5 克 = 0.3735 千克 ≤ 0.5 千克**（披露销量以整数千克计量的半 ulp）⇒ **披露销量的呈现舍入即可完全解释该残差**；等价地 金额/单价 = 49,073,626.5 克 → 四舍五入到 49,074 千克自洽 | **不涉及收入金额**（p.44 金额列 = p.45 分产品收入列逐字段相等）；**presentation flag 保留、AD-8 保留**（作披露精度提示）；**不需重述、不影响本案签署**；若后续披露给出更细销量/单价基准，按卡文 6 记 delta |
| **F-I10A-3**（等价变异体，INFO） | **披露接受**：`mut_swap`（量价**值**互换）因乘法交换律输出恒等 → rc3 属**预期等价性**；维度错配预期由 `mut_swap_ids` 臂满足（4/4 击杀，产品维度检查先拒、注册调用 0） | **残余风险备忘（交 owner 面）**：同维值互换在产品层不可检（bounds 未拦截），其收入结果无害（a×b=b×a），但会使诊断性隐含单价失真；**是否要求注册层禁止同 dimension 双驱动歧义，留 owner 裁定**（handoff `open_questions` 已载） |

#### 本轮新增 F-REV-I10A-1..5（carrier §6 L206–L212，全为簿记/文档类、non-blocking）

| ID | Finding（转录） | 落定处置（本 landing） |
|---|---|---|
| **F-REV-I10A-1**（LOW·簿记） | `handoff.current_source_hashes` 与 `changes.diff` 中**两枚 63 位 sha pin**（`disclosure_mapping.json`、`model_DE_evidence_manifest.json`）各缺 1 个十六进制字符（删除位比对：disclosure 缺 index23 的 `f`、model_DE 缺 index15 的 `e`）⇒ 按字面不可验证；真实文件完好，`model_DE_evidence_manifest.aggregate_files` 内 64 位 pin 与实测相等 | **已更正登记（append-only）**：decision `## F-REV-I10A erratum (landing)` 记 corrected 64 位 pin —— `disclosure_mapping.json` = `7e03ea748cb99d74038daeef3b529b824f1300c17ee841aaf8fc19b9f1501e0b`；`model_DE_evidence_manifest.json` = `c3e489c580cc7e9eae18efa5199456a013a04099ed07d3d03bbb4ceb5726ac95`（本 pass 落定时只读重哈希 == 复核实测）。**原件、63 位原 pin、changes.diff 一律不回写**（原值留痕）；镜像入 handoff `bookkeeping.findings_disposition` 与 qualification `f_rev_mirrors` |
| **F-REV-I10A-2**（LOW·文档） | `decision.md §2.2 注1` 把 GREEN 首跑 14 项记作「R2×2 + R3×**5** + R9×6 + **R12×1**」；原始 `CMD-I10A-VALIDATE-GREEN/validate_result.json` 实为 **R2×2 + R3×6 + R9×6（无 R12）**，R12 首次命中在 **GREEN-3**（1 项，XM-EV raw 形态）；总数 14 正确、红→绿轨迹成立 | **已更正登记**：erratum 记权威分类 = **R2×2 + R3×6 + R9×6**，R12 首见 GREEN-3；**总数/轨迹/rc 序列不受影响**；§2.2 原分类文字留痕，由本 erratum 统辖 |
| **F-REV-I10A-3**（LOW·冻结件转写） | `oracle_expected.json` ZJ-MIN `aggregate_tolerance_abs=65,724,750` vs `0.0005 × 131,489,500,000 = 65,744,750`（**−20,000** / −0.03%）；其余 3 case 自洽；该字段只定义、**不被任何门使用**（门全用 `aggregate_tolerance_rel`），残差距任一值 30 余倍余量 ⇒ 不影响任何判定 | **照录不回改（冻结纪律）**：erratum 登记为披露性转写差错；`oracle.md` / `oracle_expected.json` **0 字节**（sha 仍 `5cdd7331…` / `bf212696…`） |
| **F-REV-I10A-4**（INFO·可枚举性） | `decision.md:97/:130` 称「封面对照 **8 组字形**」，证据面只枚举 **4 组**（`decode_hk_text.py:159` 股=20579/份=7871/幣=11813/港=15857；`commands.json` 另记 年=11830）；其余 4 组未在案 ⇒ 8 组之说部分可核 | **已更正登记**：erratum 记可枚举 = 4 组（+`年` 记录面），「8 组」降为部分可核；**0-unmapped 与方法可复现性已硬证**（272,511/0 + 逐字节重跑）；全表字形共享假设仍开放（unverified #2） |
| **F-REV-I10A-5**（LOW·自指簿记） | `changes.diff` 70 枚 pin 全量复算 = **68 中、2 不中** —— `run_log.jsonl`（`96657544…` vs 实际/终态 `16e466c4…`）与 `README.md`（`f3551454…` vs 实际 `c1c71491…`）；两者为 changes.diff 生成后又追加/更新的**活文件**，属自指性时序、非篡改；**handoff 的 run_log pin 是正确终态** | **照录 + 登记**：erratum 记 68/2 全量复算与两枚活文件归因；`changes.diff` 原值留痕（0 字节）；建议后续批次标 `excluded (live file)`；隔离面清单完整性结论维持 |

### Unverified / 开放项 — **9 项 declared**（carrier §9；本 landing 逐条承继）

1. **渲染 PNG 目视比对未做** —— 复核模型无图像输入能力，`page_renders/*.png` 6 页仅做**哈希核对（7/7 与 changes.diff 相等）**+ render manifest 一致性；原文核对改由解码文本 + 解码重跑 + 叙述/算术交叉验证承担。
2. **小米解码全表字形共享假设** —— 方法可复现性与 0-unmapped 已硬证，但全表逐字形独立验证未做（实现者 §6.1 自述一致）；「8 组对照」仅 4 组可枚举（F-REV-I10A-4）。
3. **AD-7 special_review**（机制混合分部：ZJ-其他 / 小米互聯網服務 / MSFT-MPC 拆分适配）—— 留待独立裁定，本轮不宣称适配通过（保持开放）。
4. **L2 范围桥 gap 逐项分解**（紫金两分部 +6,782,172,956 / +5,695,369,295）—— 披露无表外产品明细 → `partially_explained` 为上限结论（保持开放）。
5. **MSFT E 缺口能否由外部独立披露补足**（季度补充/指引）—— 超出本卡信息面（三份原件），未查证（保持开放）。
6. **紫金 2024 对照列未纳入复建**（E 面 = 单个已结束期间 FY2025；双期复建留 I-12 口径）（保持开放）。
7. **mut_swap 等价性在 `timing_factor≠1` 时的边界**（实现者 §6.6 自述；本轮 timing=1）。
8. **网络面历史审计** —— 只能核对 binding/handoff 的命令面 0 与 **J-3 主动披露**（诊断期 2 次 `web_fetch` 取 Adobe cmap-resources 参考表，存 `source_extracts/ref/` 并哈希、作否定检验用、最终解码不依赖），无法独立证明诊断期之外无任何网络访问（无网络审计日志可查）。
9. **M01–M31 逐卡资格正文** —— 复核只核了 sweep 汇总（31/31）+ 4 张卡的 `qualification.json` 哈希与三态抽验，**未逐卡通读 31 份正文**。

> 记账注记：carrier §9-10「机读资格状态尚未落账」由**本次落账的簿记动作**处置（`evidence/I-10-A/disclosure_qualification.json` 仍 `unmapped/signed=false`、0 字节不变，签署面 = reviewer_report + 本落账三件镜像）；carrier §9-9（model_registry 晋级授权）属 **owner 决策**，非可验证性命题，在 `open_questions` 承继 —— 二者不计入上述 9 项 declared。

### Boundary（carrier §7 L216–L229 — 复核实测）

- **产品锚 5 件**（calc.py / segments.py / model_extensions.py / model_registry.py / revenue_constraints.py）：before == after，**5/5 相等**（并抽验 iso 副本与生产逐字节相同）⇒ `anchors_identical=true`，**产品零变更**。
- **来源 raw+sidecar 6 件**（紫金 PDF/`.source.json`、小米 PDF/`.source.json`、MSFT HTM/`.source.json`）：**6/6 相等** ⇒ `sources_identical=true`，未覆写原件。
- **冻结计划/依赖输入 12 件**（card / research_cards / common_research_cards / common_root_cards / model_cards / review_and_handoff / START_HERE / sample_manifest + I-00-B×2 + I-07-B×2）：**12/12 相等** ⇒ `plan_inputs_identical=true`，未覆写旧审计。
- **iso 产品副本 8 件**：**8/8 相等** ⇒ `iso_copies_identical=true`。
- **`changes.diff` 隔离面 pin**：70 枚 → 68 中、2 自指性不中（F-REV-I10A-5）⇒ 隔离面清单完整。
- **git**：`git_writes=0`（binding 禁 git）；只读实测 **`scripts/**` 对 index 与 HEAD 0 差异**、**尝试期间 0 新提交**（HEAD 仍为 2026-09-23 19:51 batch-9）、index 无 staged 变更；porcelain 非 `.planning` 项仅 2 个 untracked（`.tmp-r41-mutation/`、`assurance/…/plan_inputs.json.bak`）= 非本卡 allowlist 面且非本 attempt 产物。
- **network**：`network_command_calls=0`（命令面）；复核本轮 0 网络调用；J-3 主动披露按披露接受（历史面不可独立审计 → unverified #8）。
- **禁语扫描（R5 / STOP_QUALIFICATION_SCOPE）**：`FORBIDDEN_CLAIMS` 对 evidence 面 **0 命中**；宽域扫描（attempt 全 .md/.json，排除 iso/vendor/_scratch/command_runs/source_extracts）16 处命中**全部**为 (a) 卡文停止条款逐字引用、(b) 扫描词表自身登记、(c) 否定句、(d) RED 负例夹具构造串 —— **无一处构成主张（all-cited）**；`disclosure_qualification.json` 内无「三情景/准确性通过/proven」表述，`accuracy.status=unproven` ×6。
- **M 资格面**：`deps/m31_qualification_sweep.json` `card_count=31`、`formula_accepted_scoped_count=31`、`formula_other={}` → **M-sweep 31/31**，抽验 4 张（M03/M05/M09/M31）sha 逐个相等且三态一致 ⇒ 停止条款 2 不触发。
- **冻结时序**：binding（22:17:43）→ oracle.md（23:50:46，run_log ORACLE-FREEZE 23:51:00）→ oracle_expected（23:54:45）→ commands（23:58:03）→ 首判据运行（23:58:37）—— 容差与期望先于判据冻结 ✅。

### Scope-if-accepting（carrier §10 L267–L276）

- **6 case 已 disposition**：4 case `disclosure_adaptation = accepted_scoped`（本报告签署）/ 2 case STOP_DISCLOSURE_ADAPTATION 诚实出口（不授予）。
- **`disclosure_adaptation` 机读状态在卡内仍为 `unmapped`、`signed=false`**，直到签署按流程落账；**不得由实现者自签**。**签署面 = `reviewer_report.md`**；本次落账 = **簿记转录（bookkeeping），不是实现者自签**。
- **F-I10A-2 → 修卡 `I10A-F2-FIX`（ref `e1c31937`，REMEDIATION_REGISTER §一〇四）已立**（父代理派单）；本卡不改产品。
- **承继开放项**：AD-7 special_review + L2 桥 gap + 字形共享假设 + MSFT E 外部证据 + 紫金 2024 双期复建 —— 全部**保持开放**并随 handoff 下行。
- **`formula = accepted_scoped`（M01–31 面）不因本卡提升或外推**；**`accuracy = unproven`**；**无任何公司获正式预测放行**。
- **carries（任何下游引用必须逐字携带）**：
  1. 「三公司仅来源准备通过，仍未授予正式预测资格。」
  2. 「缺一市场/真实路径不得总体写三市场通过。」
  3. 「恢复：保留已取得raw，只回退当前隔离变更。」
  + `overall_three_market_pass = false`（NEGATIVE）+ `zero_RevenueSourceRecord_measured_fact = true`（实测事实）
  + **F1/F2/F3 三处路由**（`handoff.carried_findings_and_carries.carried_findings_from_I_07_B` / `disclosure_qualification.json carried_findings` / I-07-B reviewer_report §F1/F2/F3 章节）：F1 owner 路由 · F2 → I-06-A unsigned **OPEN-5** · F3 → **D-W06 OPEN-4**（zero RevenueSourceRecord ⇒ 来源链资格未获得）。
  （carrier §4 REM-79 双向复算：三句 ∖ {handoff, disclosure_qualification, I-07-B 源} = **0 缺失**；R8 等价复算 GREEN 无违例 ✅）
- **F-REV-I10A-1..5** 建议以勘误/登记方式处理（不改冻结件、不改证据文件内容）——**已按此执行**（唯一更正载体 = decision erratum）。

---

## Not granted / boundaries of THIS file

`disclosure_adaptation` 机读面保持 **unmapped / signed=false**；`accuracy` 保持 **unproven**；`formula` 保持 M01–M31 **accepted_scoped（scoped, 不外推）**；**0 家公司**获正式预测放行（`formal_company_forecast_cleared=false` ×3）；MSFT 两 case **不授予** disclosure_adaptation。unverified 1–9 全部维持未证；AD-7 / L2 桥 / 字形共享 / MSFT E 外部证据 / 紫金 2024 全部保持开放。本落定不授予超出 carrier §10 的任何范围：不修产品、不晋升 model_registry（owner 决策）、不执行任何 git 命令（父之保留动作）、不回改 reviewer_report / 侧车 / oracle / oracle_expected / binding / commands / changes.diff / recovery / README / evidence 8 件卡文原件 / 快照三件。**0 产品写**；本 pass 无签名产生（`signatures_produced = 0`）。

---

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor（父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单之 delegated subagent），2026-09-24（本地）。
- Corrections FIRST：`decision.md` 先追加 `## F-REV-I10A erratum (landing)`（F-REV-I10A-1..5），再写本三件 —— 严格 append-only，上文原文一字未改。
- Status transition：`review_pending` → `accepted_scoped`，在 `handoff.json` 内执行（pre-image：**14861 B、sha256 `4ba63bcb722c597c1bf71950994cf02efb601e2b248f486b336bd081173c7f95`、`status=review_pending`、`implementer_signed=false`、`implementer_never_signs_acceptance=true`、`reviewer_status=PENDING`**）；裁决词本身仅由独立复核写于 `reviewer_report.md` L15（+ L292–L298 签署区）—— 非实现方所写、非本文件作者所写。
- **Exactly three files written + one decision append**：`decision.md`（仅追加 F-REV-I10A erratum 一节）+ `review.md`（创建）+ `handoff.json`（status/status_authority/bookkeeping/carries/supersession 增补，原键原值保留）+ `evidence/I-10-A/qualification.json`（创建）。**除此之外零写入。**
- sha256 before → after：
  - `decision.md` `c84493fcba377aca40276f4f37ebc0e1812a15705ed8760a23af2210a05b2b6c`（13542 B）→ **`63afc8dd8707b3353ca205fe8b711ea3149a767d3ed5ae62753ff0c6660a815d`（18035 B）**
  - `review.md` **（不存在）→ 本文件创建，hash 报父**
  - `handoff.json` `4ba63bcb722c597c1bf71950994cf02efb601e2b248f486b336bd081173c7f95`（14861 B）→ **post-edit hash 报父**
  - `evidence/I-10-A/qualification.json` **（不存在）→ 创建，hash 报父**
  - 落定后复核：`reviewer_report.md` 仍 `6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb`/35164 B；侧车 `6f37ee29…`/85 B；oracle.md `5cdd7331…`、oracle_expected `bf212696…`、binding `aea79243…`、commands `ed7a8f40…`、changes.diff `681bdd8f…`、recovery/README `ec2e4d69…`、README `c1c71491…`、evidence 8 件卡文原件 + forecast_integration + run_log + 快照三件逐一 sha 不变。
- `implementer_signed: false`；`implementer_never_signs_acceptance: true`；`verdict_is_transcribed_not_authored: true`；独立复核 **N=1**；本 pass `git_writes = 0`。

---
carrier-landing 转录 · 父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` · verdict = `accepted_scoped`（4 签 + 2 STOP；F-REV-I10A-1..5 carried，全簿记级非阻断；accuracy=unproven、disclosure_adaptation 机读面 unmapped、0 家放行）· 本文件无自己的裁决词
