# Nine-dimension revenue research coverage

Use this layer before numerical forecasting. Its purpose is to prevent omitted research, not to add points to CAGR or confidence.

The nine dimensions test coverage, not research depth or economic validity. Read [buy-side-methodology.md](buy-side-methodology.md) for independent benchmarks, falsifiable hypotheses, model-risk review and forecast evaluation, and [industry-lifecycle-routing.md](industry-lifecycle-routing.md) for segment-level industry and lifecycle routing. Those research standards are not additional runtime gates unless explicitly implemented.

This layer is necessary but not sufficient for forward statements. Complete the separate management-communication and target ledger in `management-targets.md`; do not hide a dated management target inside the generic `growth_curve` narrative.

It is also not the growth-driver explanation. The nine dimensions are a flat omission gate; the separate `growth_driver_tree` selects the material causal mechanisms, links them to Base parameters, branches into checked evidence and counterevidence, and ranks them by modeled revenue increment.

## Required dimensions

| Dimension | Question | Typical revenue mapping |
|---|---|---|
| `company_foundation` | What is the reported revenue perimeter and segment base? | reported total, segment base, signed base adjustments |
| `growth_curve` | Which operating variables create the forecast path? | volume, price, customers, activity, utilization, backlog conversion |
| `industry_market` | Does the addressable market constrain or support modeled demand? | eligible demand or market-share driver, never TAM alone |
| `competition` | How does competition change share, price, win rate, or retention? | units, price, bookings, churn, conversion |
| `capacity` | What can actually be delivered and recognized? | commissioned capacity, utilization, billable hours, stores |
| `technology` | Does technology change yield, acceptance, price, or adoption timing? | yield, unit revenue, launch timing, customer qualification |
| `policy` | Does policy create a traceable order, tariff, approval, or restriction? | bookings, approved volume, tariff, recognition timing |
| `customers` | Which customer behaviors drive revenue? | customers, ARPU, retention, concentration-adjusted orders |
| `demand` | What end demand converts into recognized revenue? | units, usage, activity, bookings followed by conversion |

## Allowed statuses

- `modeled_driver`: the conclusion maps to one or more parameters actually used by the revenue graph.
- `data_gap`: the dimension is material but evidence is insufficient. It may list partially modeled parameters, but must state the remaining gap.
- `immaterial`: the dimension is not material to the stated forecast horizon and must explain why. It cannot map parameters.

## Record schema

```json
{
  "dimension": "capacity",
  "status": "modeled_driver",
  "conclusion": "Commissioned lines cap 2027 shipments",
  "revenue_mechanism": "commissioned capacity × utilization × yield × unit revenue",
  "parameter_ids": ["capacity_2027_base", "utilization_2027_base"],
  "source_ids": ["fy2025_filing", "capacity_release"],
  "rationale": "Optional for modeled_driver; required for data_gap or immaterial"
}
```

Provide exactly one record for each required dimension.

## Hard gates

- A `modeled_driver` parameter must exist and be used by the reported/base bridge, a segment scenario, recognition carry-in, or a company forecast adjustment.
- `company_foundation` must map to at least one reported or base parameter.
- `growth_curve` must map to at least one forecast driver, recognition carry-in, or forecast adjustment.
- A `modeled_driver` record requires source IDs. Parameter-level facts and assumptions retain their own evidence identities.
- A `data_gap` or `immaterial` record requires a rationale.
- An `immaterial` record cannot hide a parameter used by the model.
- Every `data_gap` conclusion is copied into the standard forecast `data_gaps` output.

## Causal discipline

Do not convert a research narrative directly into CAGR. Translate it through an operating identity:

```text
policy or market change
→ customer budget or demand
→ orders / users / activity
→ deliverable capacity and timing
→ accounting recognition
→ revenue
```

Do not force all nine dimensions into the formula. A well-supported `immaterial` conclusion is preferable to an invented driver.

## Depth review: connect evidence to a falsifiable forecast

For each material dimension, review the following before assigning its status. This checklist is an analyst responsibility; the runtime does not understand the underlying economics merely because the record is complete.

| Dimension | Quantitative cross-check | Qualitative challenge |
|---|---|---|
| `company_foundation` | Reported versus comparable history, organic/FX/M&A bridge, gross/net and recognition basis | Is reported growth caused by perimeter or accounting changes? |
| `growth_curve` | Segment stage, observed unit economics, saturation/replacement/decline limits | What ends the current mechanism, and when would the model need changing? |
| `industry_market` | Served demand, eligible customers, comparable penetration and cycle history | Does the reference class include failed entrants and delayed adoption? |
| `competition` | Same-customer retention, net price, win/loss, substitute price/performance | Could share gains be temporary subsidies or channel loading? |
| `capacity` | Commissioned capacity, time in service, bottlenecks, available inventory | Is supply actually qualified, staffed, financed and deliverable? |
| `technology` | Qualification time, yield, performance at commercial scale, obsolescence | Does a lab/demo advantage survive customers' total-cost and reliability tests? |
| `policy` | Eligible budget, legal implementation, tariff/approval and fulfillment dates | Is the policy enacted and executable, or only an announcement? |
| `customers` | Concentration, contract duration, additions, churn, usage and purchasing cadence | Who decides and pays; can customers postpone, cancel or substitute? |
| `demand` | Sell-through, repeat purchase, inventory, bookings quality and cancellations | Is apparent demand pull-forward, restocking or recurring consumption? |

For material claims record an alternative explanation, the affected parameter and period, a leading indicator, and a falsifier with an observable trigger. Map these into the existing growth-driver tree and parameter evidence rather than creating a parallel source ledger. Distinguish independent evidence from repeated versions of one original announcement.

Prioritize gaps by potential revenue impact and decision sensitivity, not by the number of missing fields. Use the existing `rationale` to explain why a gap could alter volume, price, timing or model choice and what evidence would resolve it. Unknown does not mean zero impact; it also does not justify inserting an arbitrary downside number.

## Lifecycle and changing-business review

Assign lifecycle at product/segment level in the research rationale: pre-revenue, commercialization, expansion, maturity, cyclical recovery/contraction, decline, or transformation. These are research labels, not new enum values. Preserve the original schema statuses.

- For pre-revenue streams, investigate launch prerequisites and explicit zero-revenue years; never infer a CAGR from zero.
- For mature streams, explain replacement, retention, net pricing and market limits instead of assuming persistent new-customer growth.
- For cyclical streams, compare quantities, price, inventory and utilization over a relevant cycle; a rebound from a depressed base is not automatically structural growth.
- For declining streams, include customer loss, patent expiry, closures and residual service demand. Negative revenue growth is a valid forecast result.
- For transformation, separate old/new streams and account for customer migration and cannibalization exactly once.

## Custom dimensions

The nine core dimensions are required. For resource-business forecasts (mineral reserves, drug pipeline, land bank, capacity plan), additional custom dimensions may be added to capture domain-specific research:

| Custom dimension | Use when |
|---|---|
| `reserves` | 地质储量、资源分级、储量寿命 |
| `processing` | 回收率、选冶能力、冶金复杂度 |
| `regulatory_permits` | 采矿权、环保审批、土地使用权 |
| `pipeline` | 药物管线阶段、临床试验进展 |
| `land_bank` | 土地储备构成、开发权、规划条件 |
| `installed_base` | 设备、客户或门店存量及更新/服务机会 |
| `channel_inventory` | 生产、进货、动销与渠道库存变化 |
| `lifecycle_transition` | 商业化、成熟、衰退或新旧业务迁移 |
| `reference_class` | 同类成功/失败样本与外部基准的可比性 |

Custom dimensions follow the same schema as core dimensions (status, conclusion, revenue_mechanism, parameter_ids, source_ids, rationale). They do not replace core dimensions. The engine outputs custom dimensions after the nine core ones.

## Research authoring procedure

This procedure connects research to the existing engine. It uses the native input objects already described in [input-schema.md](input-schema.md), [m3-period-evidence.md](m3-period-evidence.md), [evidence-role-calibration.md](evidence-role-calibration.md), and [target-measurement-comparison.md](target-measurement-comparison.md). The current engine is 4.2.1, canonical schema 3.7 with opt-in 3.8/3.9. It does not add a gate or require a new signed receipt. Use the task's actual installed runtime, configured source/LLM providers and existing cumulative resource limits; preserve historical inputs, failures and emitting versions.

### A. Set the information window and material document needs

Freeze company, fiscal calendar, reporting currency/scale, base year and the requested consecutive forecast years. `as_of_date` is the information cutoff; actual research/capture/check dates are UTC operation dates and are not backdated. First identify the latest eligible financial filing, then search the period from its **actual publication date through as-of**. An earlier acquisition announcement may support control facts, but cannot cover later announcements. If the latest relevant filing or publication date is unresolved, retain that specific window gap.

Make one compact working matrix of document type, period/window, business question, materiality decision, actual query/tool/command event, returned original/reference and locator, and outcome. This is a research work record, not a new native schema or permission registry. Use it to fill existing communication coverage, targets, inventory and `data_gap` rationales. Do not repeat the same matrix into several artifacts; reference its retained bytes in the audit record.

| Material document family | Read when it could change the model | Honest outcome if unavailable/unneeded |
|---|---|---|
| Annual, half-year, quarterly filing and results release | Base/reconciliation, policies, current operations, reported segment KPIs | Exact missing period/source clock or current provider failure |
| Earnings call and original Q&A TXT/HTML/JSON | Near-term guidance, constraints, customer/price/mix changes, contrary answers | Actual market/capability/entitlement outcome; release/deck do not replace Q&A |
| Investor presentation, strategy communication and **IR activity record** | Business detail, new products, overseas operations, dated plans | IR activity is a separate need even when it is DOCX; SSE questions are not answers |
| IPO, equity/new-share/placement and convertible-bond prospectus; use-of-proceeds update | Business description, capacity build, funding prerequisites, customer concentration, new business | A separate materiality decision for each family; old IPO does not cover a current offering |
| Acquisition/disposal agreement, target historical audit and transaction pro-forma | Control date, prior/after-control operating base, external revenue and eliminations | Title does not prove administrative content; name the missing original/bridge |
| Post-filing material announcement, primary industry/customer/peer operating document | Updated drivers, prices, demand, constraints, counterevidence and independent range | Exact date/query/window and bounded failure or impact-specific skip reason |

Reuse verified local originals through the public preparation/read interface before requesting a missing original. Financial documents use `scripts/source_preparation.py` → filing-fetch → CWP verified SourceRef read; registered non-period originals use the existing registered-source adapter. Provider routing and canonical writing belong to CWP/filing-fetch. Original transcript language is retained; do not translate or force TXT through PDF conversion. Raw file paths are storage-layer details and do not become consumer identities. Use configured acquisition intent and caps, not a new human permission.

Every outcome must distinguish: discovered/indexed, original prepared/opened, selected/summary available, summary read, **used in a native parameter dependency**, or a concrete named gap. A fresh provider result replaces only that attempted case's current observation; never claim an old 403, missing credential or limit has been retested without a new call. A search lead/tool ID without retained original content cannot support a fact. An unsupported HK transcript provider is a capability gap, not proof that no call occurred publicly.

### B. Preserve actual checked scope

Use existing `management_communication_coverage` records for the six categories. `checked`, `incomplete`, `not_checked`, `not_available`, and `not_applicable` are distinct native statuses. For a current audit execution include the existing optional `checked_scope` (`management-communication-scope/1`): `category`, `start_date`, `end_date`, `coverage_complete`, `items` plus `schema_version`.

An item carries `item_ref`, `source_id` when available, `content_role`, explicit `selected`/`read`, `skip_reason` for an unselected item, and an optional real `published_date`. Roles are `business_original`, `discovery_index`, or `index_notice`. Only an actually read registered business original enters `source_ids`. Do not paste loading notices or an index into original coverage. An unread selected item or incomplete discovery means `coverage_complete=false`; use `incomplete` and a concrete conclusion. If nothing was acquired, do not copy “Read original / no target found” from a checked row. `not_available` records the actual `search_description` and native `search_event`; `not_applicable` uses a reason grounded in the company and window. Do not fabricate receipt events for a search that never ran.

For `material_announcements_since_last_filing`, the existing scope validator uses the latest registered regulatory/exchange filing publication date and requires the interval to end at as-of. Review the actual set of registered sources so a prospectus classification does not accidentally redefine the latest financial filing in research. If the runtime's category calculation and the desired financial-filing window differ, report the seam to the owner; do not silently relabel source types or pretend an incorrect interval is complete. `audit_communication_coverage=true` requests the existing read-only scope diagnostic; it does not create a new access restriction. Older no-scope rows remain legacy/semantically unverified and are not silently upgraded.

### C. Inventory content before selecting a model

Read original operating passages, accounting notes, target definitions and contrary context around each material item. Preserve negation, timing, qualification stage, speaker/company and product scope. A selection or parser score does not prove coverage. If a summary omits a material constraint but the original exists, read the original and classify the summary omission; do not declare the original absent or require a successful model summary before using a verified original.

Register actual items in `operating_research.inventory` with its existing fields and dispositions. `included`/`subscope` point to an existing parent `item_id` and stay within its used parameter set. New product metrics do not automatically create an additional revenue line: identify whether they replace, bundle with or already belong to the parent. `unmodeled`/`unknown` retains the actual revenue mechanism and gap; `materiality_skip` explains the likely effect on this horizon. A general “needed_for revenue” phrase is not a materiality decision.

Classify claims after reading: `history_base` establishes history; `mechanism_direction` establishes direction; `value_range` establishes observed magnitude; `conversion_assumption` is an analyst bridge; `recognition_policy` establishes accounting; `peer_analogy` needs comparability; `counterevidence`/`counter_comparison` challenges the thesis. A historical header or recognition policy cannot become a future growth mechanism, and one mixed node cannot borrow another source's independence. Register contrary evidence on its own role, not as positive parameter support.

### D. Calibrate the smallest sufficient bridge

Start from observations before picking Low/Base/High percentages. For each material revenue curve choose a bridge supported by actual disclosures: quantity × realized price × acceptance, average paying cohort × net revenue per cohort, bookings/backlog recognition, demand × qualified deliverable capacity, or a transparent aggregate fallback. Avoid multiplying several unknown drivers when only aggregate revenue is observed.

1. Cross-check the latest reported amount against independent disclosed operations or comparable history. Explain the perimeter and timing. For example, equipment sales quantity and reported product revenue can give an **implied historical blended revenue per unit**, not a verified current selling price or future product mix. A point-in-time paid seat or registered user count is not average billable exposure.
2. Identify reference scope, observed period, currency/scale, both real range endpoints and contrary evidence. Use several comparable measured periods when available. A single observation is a level, not an empirical range. No arbitrary ±10%, copied H1 YoY, or guessed peer interval becomes observed evidence.
3. Explain each conversion from the reference to the target company's scenario/year, including mix, delivery/acceptance, net pricing and currency. Fill the actual native `derived_fact` formula and ordered `input_parameter_ids`; values and units must recompute and reach the intended segment/year/scenario.
4. If declaring optional calibration, use the existing `calibrations` fields, `observed_range={lower,upper,unit}` or null, real `observed_period`, `source_claim_ids`, contrary claims, scenario input/output maps, rationale and limitations. Conversion claims/observations must bind to the actual company or segment and applicability period. An outside reference endpoint may stay outside the revenue DAG; converted outputs must be used in that DAG.
5. Re-check all requested years. Evidence for 2026 H2 does not automatically calibrate 2027–28; later-year retention, saturation, replacements, qualification or demand conditions need an explicit bridge. Full-company support cannot be inferred from one calibrated driver.

The P7 4.2.1 diagnostics distinguish structural support from economic truth. `referenced_range` means the endpoint/conversion/scope/period/native-use links agree; it is not accuracy or a probability interval. Diagnostic statuses/reasons stay visible even when arithmetic validates.

### E. Complete a conditional forecast when facts are sparse

Future actuals are not required. A future `analyst_assumption` or `scenario_stress` may be non-null with its real rationale and source-linked reasoning; a source is not claimed to have reported that analyst number. First seek any material existing facts missing from the model. Then reduce degrees of freedom: collapse an unsupported split into a recognized-revenue aggregate; use one explicitly conditional driver instead of guessed quantity, price, mix and recognition factors; or keep an identifiable launch line separate while avoiding double counting in its parent.

Use the strongest observed anchor and a small set of disclosed conditions to derive Low/Base/High. Conditions may include verified capacity/acceptance thresholds, a company guideline with a supported conversion, or explicit analyst persistence/competition conditions. When numerical endpoints are not observed, `observed_range` stays null and `status="unverified"`; chosen conditional values explain the decision and why the range could be exceeded. A flat/reference extension can be shown as a named conditional benchmark, not a claimed expected path. Repeating historic growth unchanged requires an explicit persistence assumption and contrary check. Do not turn absent data into zero, declare an unsupported Low to be an empirical lower bound, or invent calibrated probabilities.

Preserve the requested three-year horizon: every segment × three scenarios × three years must have valid numeric driver and recognized/effective revenue paths when a forecast can be constructed. Use existing `direct_growth`/`direct_revenue` fallbacks if granularity is unsupported; retain recognition policies and all reconciliation/target rules. If verified base/identity/units or required source contracts are genuinely unavailable, deliver the bounded failure and missing dependency, not fabricated numeric output. Incompleteness is not cured by all-null future slots or prose called a forecast.

Do not add a “must be calibrated” gate. A structurally valid conditional forecast may remain low confidence and not yet meet the independent analyst review standard. Improve the research where a material uncertainty is actionable; where it is irreducible, state the conditional decision and its potential impact rather than endlessly retrying sources or guessing precision.

### F. Resolve windows, perimeter and revenue recognition

- Fiscal-year amounts and reporting-quarter/half windows are distinct. On 3.9 use `period_flow` with exact evidenced dates for the currently supported **3/6/12 whole calendar-month** windows; compose H1 + H2 via a native formula. Non-calendar fiscal years use the actual `fiscal_year_end`. Never infer an H1 date from the source publication date.
- A group H1 reported flow can coexist with a newly controlled subsidiary's shorter contribution window. Keep the control date and exact contribution in the original source EvidenceSpan/checked excerpt and the working content inventory. Native inventory claim IDs must still bind to a legal target; do not leave a dangling parameter claim when the flow cannot be represented. The current `validate_period_flow_fields` cannot encode an arbitrary partial-control window: do not move its start to January 1 or change it into `point_in_time`/`annual` merely to pass. Keep the usable group H1 anchor and an explicit post-H1 conditional bridge; report only the missing typed partial-window representation to the runtime owner. Other amounts remain usable under their true definitions. Zero pre-control **group contribution** is not zero pre-control subsidiary sales.
- Full-year subsidiary targets need a year-specific control/perimeter bridge. Compare target external/gross revenue to recognized **group external** revenue only after the control period and internal eliminations are known. Do not multiply consolidated revenue by ownership percentage or mechanically prorate 7/12. Acquisition adjustments and segment eliminations must each appear once.
- Keep reported, constant-currency and adjusted growth separate. An FX percentage-point effect is not a multiplicative growth percentage. Normalized/ex-transaction variants remain distinct targets; an unsupported split remains an explicit gap. A search ex-TAC KPI is not the gross search/advertising plus another business's revenue perimeter.
- RPO/backlog is a stock. Total and commercial RPO may overlap; average duration is not a straight-line recognition rule. An expected next-12-month conversion belongs to that interval, then new bookings/renewals/remaining recognition reconcile without a second recognition multiplier. New user/seat metrics require average paying exposure, net pricing, commercial availability and parent overlap before a revenue increment is added.
- Recognition policy must describe the target business's actual performance trigger, gross/net and delivery/service period. Consulting services provided, ad displayed/action, license control, subscription service and hardware delivery are different policies. A KPI definition or another business's policy cannot fill the field. Already recognized aggregates use `modeled_as_recognized`; do not apply another recognition multiplier.

### G. Keep management targets comparable and complete

Record each material target found, including qualitative annual direction, capacity plans and adjusted/FX qualifiers, before choosing a target treatment. Retain exact wording, actor, target period, strength, raw currency/unit/scale, annual/quarter/run-rate/cumulative definition and scope. “Return to growth” and “roughly double capacity” are not automatically precise revenue amounts. “Billion”, “million”, 万元 and 亿元 require an explicit conversion; preserve the raw value and do not confuse a multiple with a growth percentage.

Use `management-target-comparison/1` only for supported annual amount, quarterly/H amount or annual YoY comparison with the actual native parameter ancestry. A Q1 forecast is not FY revenue × 1/4, and a target's base year uses that scenario's true matched denominator. Match each annual target independently; a current acquisition-year mismatch must not be reused for a later full-control year. For an in-horizon comparable target, use valid scenario treatment or an evidenced `independent_benchmark` with all three scenarios; this allows an independently forecast miss without forcing attainment. Unknown conversions retain `unmodeled_data_gap`; they do not justify dropping the target or silently claiming mismatch for a comparable business.

### H. Model a shared shock once and execute sensitivity

Choose a named economic event and actual exposure: customer financing/demand, common equipment/compute bottleneck, acceptance delay, pricing or cancelation. Trace the event into affected volumes/cohorts/prices and recognized revenue **inside the same native DAG**. Explain who bears the shock and what is unaffected; do not apply an identical company-wide discount to heterogeneous businesses without a real shared mechanism.

Use existing `sum_cap`, `linked_ratio`, elimination or signed adjustment only when their evidence/perimeter fits. Missing capacity data is not a zero cap and does not permit a guessed dollar ceiling. A financing receivable delay is not automatically a revenue cancellation. For a Q4→next-Q1 delay, specify the actual affected Q4 amount, catch-up fraction and cancellation; `build_quarter_delay_bridge` supports the transparent direct-revenue case and must not infer annual revenue/4. Explain if a general conditional stress has no measured exposure or calibrated probability.

Construct a separate new stress input with all consistent affected parameters, then rerun the native engine. Report original and stressed annual revenue, net differences, current-year deferral, next-year catch-up/cancellation and constraint audits. Single sensitivities use native `sensitivity_tests`; `percent=0.05` is ±5% of a value, `percentage_point=0.05` is ±5pp of a fraction, and `basis_point=50` is ±0.005. Review requested/effective values and clamping. Test a base parameter once; effects from separate tests must not be added to estimate the joint result. Preserve native path-order rejection; do not sort genuine crossing paths into a false low/base/high ordering.

### I. Preserve quote fidelity and attribution

An excerpt marked opened-and-checked must be locatable in the **same** opened original/version. Capture enough continuous context to preserve subject, time, units, “Total” headers, negation and constraints. Do not silently join a main-text amount to a distant footnote or stitch recognition policies from different sections into one quotation. A valid excerpt SHA proves the saved excerpt, not its truth or continuity.

For non-contiguous evidence, create separate native claims with their individual locators and short excerpts, then make the relationship explicit in the research rationale. If a manual OCR/table-row transcription is needed, label that transformation in the working authoring record, retain row/header/cell locators and original content, and check values/units independently. This label does not create a new native claim field or turn a reconstruction into a verbatim quote. A composite analyst summary is not quoted as one original span. Keep continuous quotation, reconstruction and inference visibly different.

For Q&A keep question versus answer, speaker/issuer and publication qualification. An unanswered investor question is not company guidance; a closing speech is not an operating answer. A multi-issuer official JSON projection does not give every sibling the selected company's identity or publication clock. Keep unknown first-publication status; update/retrieval times alone cannot establish prior as-of availability. Do not append another consumer identity registry to repair missing source facts.

### J. Execute once at the major research node and hand off

Fill the native source/claim/parameter objects and all three scenario/year paths; identify recognition, bridge, targets, calibration and shared-shock dependencies before validation. Use `generate_input_template` only as a skeleton: replace FIXME values and never count its generated claims as actual reads. One static lint/hash check, one collected native validation, and compute/render/snapshot over the final new input are sufficient at this major node; repeat only for a concrete failure or changed model. Do not add tests at every research sentence or expand normal CI into unrelated manual contract suites.

Use the actual runtime CLIs in this order:

```text
python -X utf8 -B scripts/lint_input.py <new-input.json>
python -X utf8 -B scripts/fix_hashes.py <new-input.json> --check
python -X utf8 -B scripts/revenue_forecast.py <new-input.json> --validate-only --verbose
python -X utf8 -B scripts/revenue_forecast.py <new-input.json> --output <new-forecast.json> --markdown <new-forecast.md>
python -X utf8 -B scripts/research_support_diagnostics.py --input <new-input.json> --output <new-economic-support.json>
python -X utf8 -B scripts/revenue_backtest.py create <new-input.json> --version <same-new-version> --output <new-snapshot.json>
```

Hash repair, if actually needed, applies only to a new authored input; it cannot repair a false quote, wrong source snapshot or fake invocation. Before compute/snapshot set `REVENUE_PUBLICATION_REGISTRY` to the owned attempt's registry path and restore the previous environment afterward. Set `forecast_version` to the same new version in the input before both calls: snapshot creation sets it internally, so inconsistent versions would produce different input anchors. Native snapshot/forecast may use different JSON serialization; compare semantic/canonical anchors, not arbitrary file-byte equality. Do not overwrite an old input, result, snapshot or sealed run. `--validate-only` is zero registry write; formal compute/snapshot writes the current attempt's registry.

Keep `input.json`, engine JSON/Markdown, snapshot, support diagnostics, actual command/exit records, source-to-used-parameter links, and an adjacent `TRUST_BOUNDARY.md` explaining structural versus actual-research guarantees. These are evidence artifacts, not sign-off files. Source bytes may remain referenced in CWP/audit CAS; do not duplicate the whole lake or every revision into the result. Report actual retained/peak sizes and prior unknown cost holds under the existing task budget.

At the existing four-independent-reviewer node separate source handling, acquisition reuse/routing, process/data and economic model quality. Supply exact original locators, target/perimeter bridges, assumption/calibration gaps and actual sensitivity results. Report engineering status and research acceptance independently; a green engine or all cells structurally supported cannot close an economic issue. Each actionable common-root issue becomes owner-scoped repair and a new attempt; no case-specific percentage patch, historical rewrite or new manual permission. The repository execution checklist is `docs/w04_research_authoring_card.md`; this reference contains the full installable procedure.
