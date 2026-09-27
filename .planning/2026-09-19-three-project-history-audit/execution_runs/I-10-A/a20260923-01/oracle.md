# I-10-A oracle.md — FROZEN EXPECTATIONS (written before the first judged run)

Attempt `a20260923-01`. This file is the frozen expectation face of the card.
Creation-time evidence: `evidence/I-10-A/run_log.jsonl` + this file's mtime/sha in
`handoff.json`; the judged commands (CMD-I10A-PROBE-*, CMD-I10A-VALIDATE-*) all log
`started_at` AFTER this file's freeze record. **Not edited after the first judged run**
(binding.forbidden). Residuals are NOT yet computed here: this file freezes the tolerance
and the expected values first (卡文 action 3: 先冻结容差，再解释残差).

## 0. Scope of expectations

Judged cases = 6 adopted (company, segment, model) packages (see
`evidence/I-10-A/selected_model_manifest.json`, which this oracle cites as frozen input):

| case_id | company | segment | model | M card |
|---|---|---|---|---|
| ZJ-MIN-M09 | 紫金矿业 (CN-ZIJIN-2025) | 矿产品分部 | resource | M09 |
| ZJ-SMT-M09 | 紫金矿业 (CN-ZIJIN-2025) | 冶炼产品分部 | resource | M09 |
| XM-PHONE-M03 | 小米集團－Ｗ (HK-XIAOMI-2025) | 智能手機（手機×AIoT 分部產品線） | unit_sales | M03 |
| XM-EV-M03 | 小米集團－Ｗ (HK-XIAOMI-2025) | 智能電動汽車及AI等創新業務分部 | unit_sales | M03 |
| MS-PBP-M05 | MICROSOFT CORP (US-MSFT-2026) | Productivity and Business Processes | subscription | M05 |
| MS-IC-M06 | MICROSOFT CORP (US-MSFT-2026) | Intelligent Cloud | usage_platform | M06 |

All other model_ids (26 of 31; M03/M05/M06/M09 are the only adopted models) are
`not_selected` with reasons — expectations for them are label-only (rule R1/R10).

Historical period under adaptation: **FY2025** (CN/HK, calendar-year 2025, closed) and
**FY2026** (US, FY ended 2026-06-30, closed). Information date `as_of = 2026-09-18`
(sample_manifest). Monetary unit conventions: CN = CNY 元 (MD&A 万元 tables converted
×10^4); HK = CNY 千元 (note 5) with MD&A 億元 narrative (=10^8 元); US = USD millions.

## 1. Frozen E-reconciliation expectations (hand-computed; independent of the run)

Rebuild formula per M-card E + I-10-A action 3: rebuilt_revenue from INDEPENDENTLY
DISCLOSED closed-period operating data (quantities × realized prices from the
sales/operating statistics), compared with same-scope disclosed revenue. NO parameter is
back-solved from revenue (rule R4b). Residual = disclosed − rebuilt; decomposition
categories fixed as 量 / 价 / 汇率 / 范围 / 确认时间.

### ZJ-MIN-M09 (8 product-line instances; CNY 元)

Inputs (source: Zijin AR2025 PDF p.44 按产品划分的销售详情 (单价（不含税）/销售数量/金额),
p.45 主营业务分产品, p.325-326 分部报告):

| # | 产品 | 销售数量(raw) | 换算 | 单价(元/单位) | rebuilt=qty×price (元) | disclosed 金额(元) |
|---|---|---|---|---|---|---|
| 1 | 矿山产金-金锭 | 49,074 千克 | ×1,000 → 49,074,000 克 | 810.17 元/克 | 39,758,282,580 | 39,757,980,000 |
| 2 | 矿山产金-金精矿 | 34,087 千克 | ×1,000 → 34,087,000 克 | 730.98 元/克 | 24,916,915,260 | 24,917,160,000 |
| 3 | 矿山产铜-铜精矿 | 666,158 吨 | ×1 | 63,613 元/吨 | 42,376,308,854 | 42,376,570,000 |
| 4 | 矿山产铜-电积铜 | 95,499 吨 | ×1 | 69,665 元/吨 | 6,652,937,835 | 6,652,940,000 |
| 5 | 矿山产铜-电解铜 | 123,286 吨 | ×1 | 71,422 元/吨 | 8,805,332,692 | 8,805,370,000 |
| 6 | 矿山产锌 | 352,470 吨 | ×1 | 14,999 元/吨 | 5,286,697,530 | 5,286,650,000 |
| 7 | 矿山产银 | 430,254 千克 | ×1,000 → 430,254,000 克 | 6.88 元/克 | 2,960,147,520 | 2,958,010,000 |
| 8 | 铁精矿 | 111.35 万吨 | ×10,000 → 1,113,500 吨 | 660 元/吨 | 734,910,000 | 734,820,000 |
| | Σ | | | | **131,491,532,271** | **131,489,500,000** |

Frozen expected: Σ rebuilt = 131,491,532,271 元 (±1e-9 relative per instance);
Σ disclosed = 131,489,500,000 元; aggregate residual (disclosed−rebuilt) = **−2,032,271 元**.
Per-instance rebuilt values as in the table (these are the probe expected outputs).

Level-2 bridge (范围, informational — NOT part of the tolerance gate):
8-主要产品口径 131,489,500,000 元 → 矿产品分部 (segment note p.326: 对外 109,977,556,345 +
内部 28,294,116,611 = 总计 138,271,672,956 元). Gap = +6,782,172,956 元, expected to decompose
into (a) 主要产品表外矿产品（锂/钼/铅精矿/钴等）, (b) 表注“不含非控股企业相关数据”口径,
(c) 内部销售/抵销口径。The disclosure does NOT itemize this gap ⇒ frozen expectation:
the gap amount MUST be reported quantified with categories named and marked
`partially_explained`（不得静默吸收进容差）。

### ZJ-SMT-M09 (3 product-line instances; CNY 元)

| # | 产品 | 销售数量(raw) | 换算 | 单价 | rebuilt (元) | disclosed (元) |
|---|---|---|---|---|---|---|
| 1 | 冶炼加工金 | 162,950 千克 | ×1,000 → 162,950,000 克 | 772.15 元/克 | 125,821,842,500 | 125,822,210,000 |
| 2 | 冶炼产铜 | 697,678 吨 | ×1 | 71,621 元/吨 | 49,968,396,038 | 49,968,070,000 |
| 3 | 冶炼产锌 | 403,324 吨 | ×1 | 20,327 元/吨 | 8,198,366,948 | 8,198,230,000 |
| | Σ | | | | **183,988,605,486** | **183,988,510,000** |

Frozen expected: Σ residual (disclosed−rebuilt) = **−95,486 元**.
Level-2: 3-产品口径 183,988,510,000 → 冶炼产品分部 总计 189,683,879,295 元 (p.326) —
gap +5,695,369,295 元 (硫酸/电池级碳酸锂/其他冶炼产品 + 口径差), same `partially_explained` rule.

### XM-PHONE-M03 (CNY 元)

Inputs (Xiaomi AR2025 PDF p.21 管理層討論與分析 (i) 智能手機; p.337 附註5):
units = 165.2 百萬部 = 165,200,000 部; unit_revenue = ASP 每部人民幣 1,128.7 元;
timing_factor = 1.0; other_revenue = 0 元 (scope = 智能手機銷售).

Frozen expected rebuilt = 165,200,000 × 1,128.7 = **186,461,240,000 元** (=186,461,240 千元).
Disclosed (note 5, p.337, 人民幣千元) = 186,439,777 千元 = 186,439,777,000 元.
Residual (disclosed−rebuilt) = **−21,463,000 元**.

### XM-EV-M03 (CNY 元)

Inputs (Xiaomi AR2025 PDF p.22 智能電動汽車及AI等創新業務; p.337 附註5):
units = 411,082 輛; unit_revenue = ASP 每輛人民幣 251,171 元; timing_factor = 1.0;
other_revenue = 其他相關業務收入 28 億元 = 2,800,000,000 元 (MD&A 億元-rounded).

Frozen expected rebuilt = 411,082 × 251,171 + 2,800,000,000 = 103,251,877,022 + 2,800,000,000
= **106,051,877,022 元**. Disclosed segment revenue (note 5) = 106,069,513 千元 =
106,069,513,000 元. Residual (disclosed−rebuilt) = **+17,635,978 元**.

### MS-PBP-M05 / MS-IC-M06 (USD)

Frozen expectation: **E is NOT executable** — the FY2026 10-K discloses **no operating
quantities** (seats/users/consumption/units) at required granularity: metrics section
(printed p.35-36) discloses only growth-rate metrics and records that “Microsoft 365
Consumer subscribers was removed as a metric”; revenue tables are dollar-only. Required
M05/M06 quantities/prices therefore stay `missing`. Frozen expectation: both cases
proceed to **STOP_DISCLOSURE_ADAPTATION**（收入历史桥未解决）with D completed
missing-marked, NO probe run, NO residual invented. Any artifact claiming an E rebuild or
probe for these cases violates R4/R6.

## 2. Frozen tolerance (E段容差) — set BEFORE residuals are computed

Basis = quantified DISCLOSURE-ROUNDING granularities (from the published precision, NOT
from the observed residual):

| case | per-instance tol | aggregate tol | economic basis (rounding bound) |
|---|---|---|---|
| ZJ-MIN-M09 | ±0.10% of disclosed | ±0.05% of Σ disclosed | price half-ulp: max = 银 6.88 元/克 ⇒ 0.5/6.88 = 0.0727%; 金额落万元 ⇒ ±5,000 元/线 (≤0.0007%) |
| ZJ-SMT-M09 | ±0.10% of disclosed | ±0.05% of Σ disclosed | price half-ulp: max = 772.15 ⇒ 0.00065%; 冶炼产锌 20,327 ⇒ 0.0025%; 万元 rounding |
| XM-PHONE-M03 | — | ±0.05% of disclosed (= ±93,219,888 元) | units granularity 0.1 百萬部 ⇒ ±50,000 部 ⇒ ±56,435,000 元; ASP granularity 0.1 元 ⇒ ±0.05×165.2M = ±8,260,000 元; bound total ±64,695,000 元 = 0.0347% ⇒ tol 0.05% |
| XM-EV-M03 | — | ±0.10% of disclosed (= ±106,069,513 元) | other_revenue rounded to 億元 ⇒ ±50,000,000 元 (0.0473%); ASP granularity 1 元 ⇒ ±0.5×411,082 = ±205,541 元; bound total 0.0475% ⇒ tol 0.10% |

Level-2 bridges are NOT gated by tolerance (they are scope bridges); they must be
reported quantified and marked `partially_explained` with the unexplained remainder named.

## 3. Frozen probe expectations (historical_mapping_probe)

For each of ZJ-MIN-M09 (8 instances), ZJ-SMT-M09 (3), XM-PHONE-M03 (1), XM-EV-M03 (1):

1. Inputs use FY2025 disclosed historical parameters with **identical values on
   low/base/high** (`scenario: "all"` parameters; one `calculate_model_path` call per
   scenario key). Expected: the three outputs are IDENTICAL to each other and equal the
   frozen rebuilt value in §1 within 1e-9×max(1,|e|).
2. Wiring counts (call-spy on `model_registry.calculate_registered_model`, count-on-entry):
   ZJ-MIN-M09 = 24 calls (8 instances × 3 scenarios); ZJ-SMT-M09 = 9; XM-PHONE-M03 = 3;
   XM-EV-M03 = 3. All other product functions uninstrumented; no count derives from
   artifact files.
3. Label: every probe artifact MUST carry `historical_mapping_probe: true` and the string
   `historical_mapping_probe`; it MUST NOT assert 三情景预测 / 真实情景 / 准确性 /
   accuracy (R5). low/base/high identical-value runs are 映射验证 only.
4. MS-PBP-M05 / MS-IC-M06: probe NOT run (parameters missing) — expectation is absence
   plus a `not_run_reason`.

Negative/mutation expectations per probe case (红→绿→变异 chain, all non-vacuous):
- RED arm (mis-wired variant must NOT validate): 千克→克 conversion factor mutated ×100
  (ZJ cases) / units ×10 (XM cases) ⇒ runner MUST reject (output ≠ frozen expected).
- MUT arm (corruption must be caught): (a) swap two parameter_ids across drivers
  (dimension mismatch ⇒ product raises ⇒ runner records refusal); (b) drop the explicit
  `other_revenue` ⇒ post-I-10-B registry raises ModelRegistryError (省缺即抛) ⇒ runner
  records refusal. Each runner refusal = correctly-rejected negative (rc 2); an unrefused
  mutant = rc 3 (应红未红).

## 4. Frozen validator rules (R1-R12) for CMD-I10A-VALIDATE-*

R1 manifest completeness/labels · R2 per-driver mapping completeness (required+optional,
missing marked, never 0-filled) · R3 quote verifiability (every non-missing quote appears
verbatim in the cited extract text) · R4 reconciliation integrity (4a tolerance frozen in
this oracle and referenced by sha; 4b no back-solving pattern — a parameter's
conversion/source must not derive from disclosed revenue; 4c all five residual categories
present with value or explicit n/a reason) · R5 probe labelling + no over-claim ·
R6 probe wiring evidence (identical low/base/high; equal frozen expected; spy counts equal
frozen counts) · R7 qualification bookkeeping (disclosure_adaptation unsigned/unmapped,
accuracy unproven; implementer never signs) · R8 carry integrity (three declarations
verbatim + overall_three_market_pass=false + zero-RevenueSourceRecord fact) · R9
model_DE_evidence_manifest completeness (4 M-card products per adopted case + hashes) ·
R10 not_selected honesty (no adaptation claimed) · R11 accounting_decision structure
(选择/理由/反例/兼容影响/恢复规则/拒绝的替代 + special_review routing + 精算 N/A reason) ·
R12 unit-conversion integrity (conversion_formula recompute: raw×factor == used).

RED fixtures (one per family F-A=R1/R7/R8/R10, F-B=R2/R3/R12, F-C=R4, F-D=R5/R6,
F-E=R9/R11): pre-adaptation skeleton artifacts must FAIL their family (rc 2, correctly
rejected). MUT fixtures: the real artifacts with exactly one injected defect per family
must FAIL (killed). A surviving mutant is recorded as a gap (never silently dropped).

## 5. Reviewer attack list (oracle attack surface)

1. Re-hash any source/quote: quotes must match `source_extracts/*` verbatim; CN/US quotes
   match the pdftotext/HTM extracts; HK quotes match `HK-XIAOMI-2025_decoded.txt` whose
   method (inverse of the embedded HYQiHei-FES `cmap`, 28,873 glyphs) is re-derivable
   from the untouched PDF (0 unmapped glyphs; cover-page pairs 股=20579/份=7871/幣=11813
   verified).
2. Recompute any 量×价 line and the four residuals in §1 by hand.
3. Check the probe runner really calls the product entry (`iso/rf/scripts/forecast/segments.py
   calculate_model_path`) and not a re-implementation: spy counts + argv + iso hash proof.
4. Try to find a back-solved parameter (R4b): every parameter traces to operating data or
   an explicit economic-basis default, never to revenue.
5. Grep decision/handoff for forbidden claims (三情景预测/准确性通过/企业适配通过 where
   unsigned).
6. Confirm MSFT cases did NOT invent quantities (missing stays missing) and did NOT run
   probes.
7. Verify the three carried declarations appear verbatim and `overall_three_market_pass`
   is false everywhere it appears.
