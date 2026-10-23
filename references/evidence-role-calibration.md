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

### Where the page slice comes from, and why a page prefix is not own-scope support

A page-prefix slice is a *retrieval* artefact, not an excerpt. When an authoring step cuts a fixed number of characters from the top of a PDF page, the resulting text often belongs to the previous business section, the previous table, or a footnote — while the claim's target parameter belongs to a section further down the same page. Byte/hash validity then proves only that the slice really exists, never that it describes the claimed business.

The repair is structural, not cosmetic: locate the section that *names* the target business, then take a contiguous range inside that section that contains the subject, the period, the mechanism and the nearest qualifying clause. Record the physical page, the character offsets and the page-text hash so the range can be reproduced. If the contiguous range exceeds the claim-excerpt limit, split it at a paragraph boundary into two source-owned ranges — do not truncate mid-sentence and do not fall back to "the whole page".

A second, cheaper mistake rides on the same artefact: because the slice is *about* something, it reads like a mechanism. Two distinct segments can share a page, and the same sentence can sit above or below the boundary of the business it describes. Check the owning section, not the page.

## Expected future recognition is not an actual, and an actual is not a floor

One paragraph frequently carries three different things at once:

- a **stock** at a stated date (for example a remaining-performance-obligation balance) — a reported point-in-time fact;
- an **issuer expectation** that part of that stock will be recognised in a future period — `management_guidance`, with an exact value if the issuer gave one point;
- **no actual realisation at all** for the future period.

An issuer's expected recognition amount is a single stated point for a named cohort. It is not an empirical range, not a probability, not a full-year floor and not an actual. It must not be added to the year's reported first-half revenue, and it must not be split across sub-businesses that were never disclosed. Conversely, a real future-dated contract stock, or a genuinely completed window, is not disqualified merely because its date is in the future: reject a claim for its *semantics*, never for a "future year" keyword.

When such a parameter has no revenue-DAG consumer, correcting its kind is still required — the role is wrong even when the arithmetic effect is zero — and the correction must be disclosed as a zero-arithmetic-impact repair rather than sold as a forecast improvement.

## Role changes must survive a negative control

Not every implicated claim is mis-roled. When a review set is built from three collections, some of its members are already correct, and a repair pass that "fixes" them introduces the defect it was meant to remove. Keep an explicit negative control: list the claims whose role must **not** change, state why the existing role is right, and assert the count before and after.

The common case is a cross-scope price observation. Disclosed margin price pressure for segment A is genuine evidence that price pressure exists in the market, and it is legitimately usable as a `conversion_assumption` for segment B — but only if the cross-scope transfer is written down as an analyst choice with its own rationale. Promoting it to `mechanism_direction` for segment B would claim segment B disclosed something it did not. Keeping it as `conversion_assumption` and *documenting the transfer* is the correct repair.

## Honest weakening beats a fabricated mechanism

Some claims cannot be repaired by re-binding: the source genuinely contains no forward operating mechanism. A historical decline row, a termination/classification footnote, or a zero-revenue perimeter statement is context, not a growth mechanism.

The honest dispositions are:

- re-role the claim to `history_base` (or `counterevidence` for a genuinely adverse fact) and re-bind it to the row that actually exists;
- keep the modelled contribution — including a zero or negative one — in the revenue sum, so the perimeter still reconciles;
- let the native driver report say that this driver has no future-mechanism evidence, and disclose that limitation;
- never invent a mechanism to hit a coverage quota, and never write a diagnostic string into a native enum field.

A driver with no mechanism evidence is a finding about the company, not a hole in the input.


Positive mechanism observations follow the existing claim target and its native dependency edges. A parameter claim must be in that target parameter's claim_ids; its observation may name the same parameter or an actual downstream derived parameter, including another year with an explicit formula. Growth-driver claims bind through the exact evidence_id and claim_ids of the existing driver evidence node, then that driver's actual parameter ancestry. Merely existing IDs cannot transfer support to an unrelated business or scenario. The observation period must match the named parameter measurement period (or annual period), and its scope must be the company or a segment that actually consumes it. Explicit contradictory relationships are rejected; an unknown product scope or unresolved claim relationship stays unverified and is excluded from supported_parameter_ids. Counterevidence/peer relations and historical context remain related observations without becoming positive support. The projection exposes binding_status; this checks declared structure, not economic truth.

The input generator marks future parameter claims `research_role_status="unclassified"` and assigns no positive mechanism role. Its hashes, excerpts and verification fields remain FIXME placeholders. The generator performs no real read, certifies no fidelity and generates no confidence score.

## Optional executable contract

Native input may include `operating_research` with exact keys:

- `schema_version="operating-research/1"`.
- `inventory`: rows with `item_id`, `topic`, `disposition`, `rationale`, `claim_ids`, `parameter_ids`, `driver_ids`, `recognition_note`, `included_in` (null unless included/subscope).
- `observations`: rows with `claim_id`, `observation_kind`, `scope`, `period`, `parameter_ids`, `driver_ids`, `rationale`. The role comes from the existing claim's `evidence_role`.
- `calibrations`: rows with `calibration_id`, `status` (`calibrated`, `unverified`, `stress`), `scope`, `observed_period`, `source_claim_ids`, `counterevidence_claim_ids`, `observed_range`, `conversion_formula`, `output_unit`, `scenario_input_parameter_ids`, `scenario_output_parameter_ids`, `rationale`, `limitations`.

`observed_range` is null or `{lower, upper, unit}`. A referenced range needs checked `value_range` claims for both endpoints, the same observed period/unit and declared business scope. Claims retain original dates and locators. Independent range endpoints prove their real parameter, unit, observed period and declared reference scope; an endpoint that never enters the revenue DAG (for example an unused upper bound) stays a legal independent reference. Each scenario's input list uses `x0` for the comparable observed reference and subsequent inputs for explicit conversion assumptions; its output ID is an actually used native `derived_fact` with the same formula and ordered input IDs. Units and observed measurement period are checked separately. A TTM input does not become FY by naming the calibration FY. Record outside evidence that contradicts the range and how it changes the assumptions.

The actual conversions and forecast outputs carry the stricter binding. Every scenario conversion input must be covered by a conversion observation whose `binding_status` is `bound`; an unbound observation yields `conversion_observation_unverified_scope:<parameter>:<claim>` or `conversion_observation_unverified_period:<parameter>:<claim>` and blocks `referenced_range`. The declared calibration scope must name the company or one of its real segments (`calibration_scope_not_native_business:<scope>` otherwise), and every scenario output must actually be consumed by that scope inside the native DAG (`calibration_output_scope_mismatch:<output>:<scope>-><actual>`); a different company, product line or total market is not automatically the same perimeter, and a legal cross-scope benchmark needs its explicit reviewable conversion relation. Support never propagates from one driver to other segments, scenarios or forecast years.

Example engineering bridge: an observed comparable range `[100,120] USD million` for `FY2025`, then `x0*x1` with reference 100 and separately disclosed Low/Base/High conversion factors 1.0/1.1/1.2, yields 100/110/120 USD million. These are arithmetic fixtures, not business estimates. Each formula is the native DAG, not a parallel calculator. Real inputs should use independently justified quantities, prices, cohorts, deliveries or transparent aggregate fallback as available; there is no mandatory units×ASP model or fixed percentage scaling.

Direct conversion inputs also retain their native applicability period (`parameter.period`): it must describe the calibration output's period, and a directly consumed output must describe its actual revenue/recognition cell year. A self-consistent conversion parameter/claim/observation for FY2031 does not calibrate an FY2026 output. These mismatches add `conversion_output_period_mismatch:<parameter>:<applicability period>:<output>:<output period>:<claim IDs>` or `calibration_output_consumption_period_mismatch:<output>:<output period>:<segment>:<scenario>:<cell period>` diagnostics and demote optional support to `unverified`; they do not block the document or change revenue arithmetic. Source disclosure dates, claim periods and `measurement_period` are not forced to equal a forecast year: existing observation-to-parameter binding remains separate. A historical reference stays historical, an unused upper endpoint stays legal, and a reviewable cross-period native bridge may carry an old factor into a derived conversion whose period is the actual target. Formula linkage checks structure, not economic truth or accuracy.

The diagnostic says `referenced_range` only when the source-range links, the bound conversion observations and the native output scope bindings all agree. Missing ranges, period mismatch, unbound conversions, non-native scope, missing conversion disclosure or different formula links yield `unverified`; null is never filled with zero. `stress` remains an illustration. A documented range is not empirical forecast accuracy or calibrated probability coverage. Do not declare the whole company calibrated when only one driver has a supported range. Engine 4.2.1 re-emits these calibration diagnostics (inputs that previously reached `referenced_range` through unbound conversions or a non-native scope re-emit as `unverified`); revenue arithmetic and the input contract are unchanged, and old 4.2.0 outputs keep their original bytes against the pinned 4.2.0 emitter.

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
