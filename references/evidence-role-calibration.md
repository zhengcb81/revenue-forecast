# Operating inventory, evidence roles and economic calibration

Use the smallest operating bridge sufficient for the material revenue question. Company name, business stage, source count and verified arithmetic do not determine an economic growth rate. This optional typed projection registers research declarations and checks their links; it never infers economic truth from English words, parser quality, hashes or human signatures.

## Content inventory before selecting parameters

Read the selected original documents and record each material item under a stable item ID. Topics include dated management targets, new products and ramps, recognition terms, shared bottlenecks, customer financing, competitive constraints and other operating content. There is no universal requirement that every company have each topic. Each actual item has one `disposition`: `modeled`, `included`, `subscope`, `unmodeled`, `materiality_skip` or `unknown`, plus a reason and recognition note. CPU/product/platform detail may be included in an existing parent segment rather than added as another sales line. `included`/`subscope` names its parent and remains within the parent's parameter set; circular inclusion is invalid.

Do not turn TTM into a fiscal-year denominator, contract minimum guarantees into current sales, rental sharing into hardware shipments, customer capex into one vendor's revenue, purchase commitments into realized sales, GW opportunity estimates into verified ASP/capacity, or an MOU into closed funding. Where conversion inputs are unavailable, retain the original item and the reason for `unknown`/`unmodeled`. State the recognition trigger and which period the uncertainty affects.

## Role counterexamples

| Declared observation | Permitted evidence role | What it does not establish |
|---|---|---|
| Historical revenue table/header | `history_base` | Future growth mechanism or future numerical range |
| Historical measured level | `history_base` / `value_range` | A future rate without a separate conversion |
| Weak PC demand | `counterevidence` / `counter_comparison` | A positive growth mechanism |
| Operating causal mechanism | `mechanism_direction` | Numerical effect size |
| Quantitative reference | `value_range` / `peer_analogy` | Automatic company-specific transfer |
| Analyst conversion | `conversion_assumption` | Reported business fact |
| Recognition policy | `recognition_policy` | Demand or sales magnitude |

These are explicit researcher classifications after reading the excerpt. Chinese and English fixtures test role propagation without a keyword plausibility classifier. The existing claim contract still validates source/locator/bytes once. Exact numeric historical-revenue or reported-baseline facts may retain `history_base`; this does not permit a future mechanism/value-range claim. Counterevidence remains a related research observation; it is not placed in a parameter's positive `claim_ids`. A source-linked future assumption supported only by historical-base claims is already rejected by the existing contract.

Positive mechanism observations follow the existing claim target and its native dependency edges. A parameter claim must be in that target parameter's claim_ids; its observation may name the same parameter or an actual downstream derived parameter, including another year with an explicit formula. Growth-driver claims bind through the exact evidence_id and claim_ids of the existing driver evidence node, then that driver's actual parameter ancestry. Merely existing IDs cannot transfer support to an unrelated business or scenario. The observation period must match the named parameter measurement period (or annual period), and its scope must be the company or a segment that actually consumes it. Explicit contradictory relationships are rejected; an unknown product scope or unresolved claim relationship stays unverified and is excluded from supported_parameter_ids. Counterevidence/peer relations and historical context remain related observations without becoming positive support. The projection exposes binding_status; this checks declared structure, not economic truth.

The input generator marks future parameter claims `research_role_status="unclassified"` and assigns no positive mechanism role. Its hashes, excerpts and verification fields remain FIXME placeholders. The generator performs no real read, certifies no fidelity and generates no confidence score.

## Optional executable contract

Native input may include `operating_research` with exact keys:

- `schema_version="operating-research/1"`.
- `inventory`: rows with `item_id`, `topic`, `disposition`, `rationale`, `claim_ids`, `parameter_ids`, `driver_ids`, `recognition_note`, `included_in` (null unless included/subscope).
- `observations`: rows with `claim_id`, `observation_kind`, `scope`, `period`, `parameter_ids`, `driver_ids`, `rationale`. The role comes from the existing claim's `evidence_role`.
- `calibrations`: rows with `calibration_id`, `status` (`calibrated`, `unverified`, `stress`), `scope`, `observed_period`, `source_claim_ids`, `counterevidence_claim_ids`, `observed_range`, `conversion_formula`, `output_unit`, `scenario_input_parameter_ids`, `scenario_output_parameter_ids`, `rationale`, `limitations`.

`observed_range` is null or `{lower, upper, unit}`. A referenced range needs checked `value_range` claims for both endpoints, the same observed period/unit and declared business scope. Claims retain original dates and locators. Each scenario's input list uses `x0` for the comparable observed reference and subsequent inputs for explicit conversion assumptions; its output ID is an actually used native `derived_fact` with the same formula and ordered input IDs. Units and observed measurement period are checked separately. A TTM input does not become FY by naming the calibration FY. Record outside evidence that contradicts the range and how it changes the assumptions.

Example engineering bridge: an observed comparable range `[100,120] USD million` for `FY2025`, then `x0*x1` with reference 100 and separately disclosed Low/Base/High conversion factors 1.0/1.1/1.2, yields 100/110/120 USD million. These are arithmetic fixtures, not business estimates. Each formula is the native DAG, not a parallel calculator. Real inputs should use independently justified quantities, prices, cohorts, deliveries or transparent aggregate fallback as available; there is no mandatory units×ASP model or fixed percentage scaling.

The diagnostic says `referenced_range` only when the source-range and native conversion links agree. Missing ranges, period mismatch, missing conversion disclosure or different formula links yield `unverified`; null is never filled with zero. `stress` remains an illustration. A documented range is not empirical forecast accuracy or calibrated probability coverage. Do not declare the whole company calibrated when only one driver has a supported range.

## Joint financing, delivery and shared-capacity pressure

Reuse existing `sum_cap`, `linked_ratio` and signed adjustment contracts. Count a CPU/GPU shared resource once. `research.timing_bridge.build_quarter_delay_bridge` constructs native formulas for the supported transparent direct recognized-revenue case across a Q4→next-Q1 boundary:

- Current-year revenue = original current-year revenue − explicit affected Q4 revenue.
- Next-year revenue = original next-year revenue + affected Q4 revenue × explicit catch-up fraction.
- Cancellation = affected Q4 revenue × (1 − catch-up fraction).

The helper requires explicit quarter amount, matched currency/scale, both years and a fraction in `[0,1]`. It does not infer quarter amount as annual revenue/4. The existing native shared cap then recomputes effective segment revenue and reports constraint audit changes. Equal caps can change segment shares enough to cross Low/Base/High; retain the native rejection and publish a separate conditional stress result rather than silently sorting annual values. In-year quarter delays, detailed cohorts and other recognition models need their own explicit operating bridge; this limited helper cannot settle them.

## Confidence and delivery

Old `stable-fsum/1` total, weights, components and snapshots are unchanged. When typed research is present, `confidence.research_adequacy` separately displays documentary presence, declared mechanism support, referenced magnitude range and unresolved inventory. It is recomputed from the original input during output validation and rendered in Markdown. It adds no access permission, human review gate or new source identity registry.

Run the actual generic assembly recipe:

`python -X utf8 -B tools/build_auditable_case.py --company <label> --input <authored-native-input> --research <operating-research.json> --preparation <W04-result.json> --discovery <W03-bounded-receipt.json> --as-of <same-information-date> --output-root <absent-owned-dir>`

The authored input and typed research are required; the recipe cannot create business facts from a company label. It preserves actual W04 source captures only when authored claims match the same bytes. Optional `--narrative-request --bindings --source-id --catalog-config` uses the real W04 reader and marks consumption only after a used parameter dependency exists. A summary that was merely read stays `not_consumed`. A discovery receipt is saved by hash and cannot establish original-content completeness. No provider/model/download runs are started. Optional `--delay-request` creates a separately labeled illustrative stress input and receipt.

Then use `tools/run_target_measurement_e2e.py --input <assembled>/linked-input.json --output-root <new-native-output>` for actual native validate, compute/render and immutable snapshot. Current company economic review, real official reads and four independent reviewers belong to the main M2 node. Do not call synthetic fixture success a current forecast, consensus beat, forecast accuracy or a historical backtest. Without a frozen past forecast, record the gap.
