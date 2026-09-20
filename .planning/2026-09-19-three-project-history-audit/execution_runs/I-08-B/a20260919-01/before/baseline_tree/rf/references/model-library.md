# Executable revenue model library

Assign models per segment. The exact model and driver names below match `scripts/revenue_core.py`.

The runtime source of truth is the immutable `MODEL_REGISTRY` in `scripts/model_registry.py`. `revenue_core.py` exports compatibility views but contains no formula-selection branch.

| Model | Required drivers | Optional drivers | Formula |
|---|---|---|---|
| `direct_growth` | `growth_rate` | — | prior revenue × (1 + growth rate) |
| `direct_revenue` | `revenue` | — | explicit recognized revenue |
| `unit_sales` | `units`, `unit_revenue` | `timing_factor`, `other_revenue` | units × unit revenue × timing + other |
| `capacity_utilization` | `capacity`, `utilization`, `yield`, `unit_revenue` | `timing_factor`, `other_revenue` | capacity × utilization × yield × unit revenue × timing + other |
| `subscription` | `average_customers`, `revenue_per_customer` | `timing_factor`, `usage_revenue` | average customers × revenue/customer × timing + usage |
| `usage_platform` | `eligible_activity`, `monetization_rate` | `fixed_revenue` | eligible activity × monetization rate + fixed |
| `services` | `billable_capacity`, `utilization`, `billing_rate` | `timing_factor`, `other_revenue` | billable capacity × utilization × billing rate × timing + other |
| `project_backlog` | `opening_backlog`, `bookings`, `cancellations`, `contract_changes`, `closing_backlog` | `backlog_remeasurements` | opening + bookings − cancellations + changes + non-performance remeasurements − closing |
| `resource` | `saleable_volume`, `realized_price` | `other_revenue` | saleable volume × realized price + other |
| `infrastructure` | `billable_volume`, `tariff` | `other_revenue` | billable volume × tariff + other |
| `bank_revenue` | `average_earning_assets`, `asset_yield`, `average_interest_bearing_liabilities`, `funding_cost`, `fee_revenue` | `other_revenue` | interest income − interest expense + fees + other |
| `asset_management` | `average_aum`, `management_fee_rate` | `performance_fee_revenue`, `other_revenue` | average AUM × fee rate + performance fees + other |
| `retail_franchise` | `average_owned_stores`, `revenue_per_owned_store` | `franchise_system_sales`, `recognized_fee_rate`, `supply_revenue` | owned-store revenue + recognized franchise fees + supply revenue |
| `transport` | `capacity`, `utilization`, `yield` | `ancillary_revenue` | capacity × utilization × yield + ancillary |
| `real_estate_rental` | `average_occupied_area`, `rent_per_area` | `other_revenue` | occupied area × rent/area + other |
| `licensing_commercial` | `treated_units`, `net_revenue_per_unit` | `milestone_revenue`, `royalty_revenue`, `service_revenue` | commercial + milestone + royalty + service revenue |
| `advertising` | `eligible_impressions`, `fill_rate`, `revenue_per_thousand_impressions` | `other_revenue` | impressions/1,000 × fill rate × revenue per thousand + other |
| `gaming` | `active_users`, `payer_conversion`, `revenue_per_payer` | `other_revenue` | active users × payer conversion × revenue/payer + other |
| `cohort_subscription` | `opening_customers`, `new_customers`, `churned_customers`, `ending_customers`, `revenue_per_customer` | `new_customer_revenue_fraction`, `churned_customer_lost_fraction`, `timing_factor`, `usage_revenue` | (opening + new × new-customer fraction − churn × lost fraction) × revenue/customer × timing + usage |
| `delivery_pipeline` | opening orders, new orders, cancellations, deliveries, ending orders, unit revenue | `timing_factor`, `other_revenue` | deliveries × unit revenue × timing + other |
| `milestone_royalty` | `eligible_sales`, `royalty_rate` | milestone and service revenue | eligible sales × royalty rate + milestone + service |
| `insurance_service` | `coverage_units`, `revenue_per_coverage_unit` | `timing_factor`, `other_revenue` | coverage units × revenue/coverage unit × timing + other |
| `reserve_depletion` | `opening_reserves`, `additions`, `depletion`, `closing_reserves`, `recovery_rate`, `realized_price` | `reserve_revisions`, `other_revenue` | depletion × recovery rate × realized price + other; reserve revisions affect the stock bridge only |

Lifecycle and operating extensions are documented with exact drivers, formulas and limitations in [extended-models.md](extended-models.md): `subscription_arr_bridge`, `installed_base_aftermarket`, `store_cohorts`, `renewable_generation`, `aum_fee_bridge`, `commercial_launch`, `finite_adoption`, and `inventory_sellthrough`. Use the registry as the source of truth; do not infer driver names from a model label.

## Selection notes

- Split product and after-sales service when their drivers differ.
- Split subscription and usage-based streams when ARPU does not already include usage.
- Use average customers, stores, AUM, occupied area, or earning assets where revenue accrues through the period.
- Use commissioned revenue-capable capacity, not announced capacity.
- Treat `yield` as manufacturing yield only in `capacity_utilization`; in `transport`, `yield` means revenue per utilized capacity unit.
- Use average earning assets and liabilities in the bank model. Do not substitute period-end total assets.
- Use `cohort_subscription` when opening/adds/churn/ending data are available; the engine enforces the stock-flow bridge and continuity. New-customer revenue and churned-customer lost fractions default to 0.5 (uniform intra-year timing); supply sourced fractions when onboarding or churn is seasonal/concentrated. Do not apply a second `timing_factor` for the same effect. This is an aggregate customer bridge, not a full vintage-by-vintage retention model.
- Use `delivery_pipeline` when order units convert to delivered units; the engine enforces order continuity and base opening orders.
- Use `insurance_service` only when coverage/service units reconcile to IFRS 17 disclosures; never substitute premiums collected.
- Use `timing_factor` for year-in-service, commissioning, or explicit seasonal availability. Do not use it as an unsupported growth plug.
- Use `reserve_depletion` only when a same-unit physical stock is depleted into saleable output. The stock bridge is opening + additions + reserve revisions − depletion = closing. Patent expiry and capacity retirements are not revenue-producing depletion; land development is not necessarily delivery. See [resource-business-guidance.md](resource-business-guidance.md). Use `resource` when saleable volume is pre-computed and no stock-flow bridge is needed.
- Use `backlog_remeasurements` only for signed non-performance changes such as FX/reclassification. They enter the backlog bridge so that those changes do not appear as contract fulfillment. `contract_changes` captures genuine changes to enforceable contract consideration. The analyst must classify these movements from evidence.

## Model-by-model review requirements

These are economic review requirements. Some are enforced numerically (ranges and registered stock-flow bridges); customer behavior, units inside generic dimensions and accounting meaning still require source review. See [buy-side-methodology.md](buy-side-methodology.md) for the distinction between a passed contract and a supported forecast.

| Model | Check before using | Extend or change route when |
|---|---|---|
| `direct_growth` | Comparable prior revenue, supported growth path, nonzero base when using CAGR | Launch from zero, step change, saturation, M&A or structural decline needs operating drivers |
| `direct_revenue` | Recognized amount and accounting bridge are externally supported | The amount is only a target, billings, GTV or unverified analyst plug |
| `unit_sales` | Sold units and net revenue/unit share one period/perimeter | Product mix, returns, shipments versus sell-through or inventory matter |
| `capacity_utilization` | Revenue-capable period capacity, utilization and manufacturing yield counted once | Commissioning, bottleneck, outages, demand limits or inventory require separate bridges |
| `subscription` | Average billable customers, service-period ARPU and usage separation | Material additions/churn/expansion/contraction require cohort or ARR bridge |
| `usage_platform` | Eligible monetized activity and recognized net take rate | Two-sided participation, fee tiers, principal/agent changes or subsidies matter |
| `services` | Billable hours/capacity, utilization and compatible billing-rate time basis | Fixed-fee projects, subcontractors, reimbursements or milestone acceptance differ |
| `project_backlog` | Backlog is unrecognized enforceable revenue; revisions/FX/cancellations are separate | Bookings have a different perimeter or progress was already recognized; avoid a second progress discount |
| `resource` | Saleable quantity, net payable price, byproduct treatment | Processing loss, grade, stock depletion or production/sales differences are material |
| `infrastructure` | Billable volume × allowed realized tariff, pass-through separately traced | Capacity payments, regulatory true-ups, availability or alternative tariffs matter |
| `bank_revenue` | Period-average interest-bearing balances and annualized effective yield/cost | Repricing buckets, non-accruals, hedges or net/gross presentation are material |
| `asset_management` | Time-weighted fee-earning AUM and fee schedule | Flows, market returns, fee tiers or crystallization require an AUM bridge/extra assumptions |
| `retail_franchise` | Comparable average stores and store productivity; franchise/supply revenue separated | Openings, closures, cohorts and cannibalization drive growth |
| `transport` | Capacity and yield denominator match; utilization has physical meaning | Passenger/cargo mix, load factor, seasonality or charter revenue diverge |
| `real_estate_rental` | Average occupied area × recognized rent; incentives/free-rent periods included | Lease cohorts, turnover rent, development sales or cash/straight-line rent differ |
| `licensing_commercial` | Treated units and net unit revenue, milestone/royalty recognition independent | Clinical stage, launch ramp, patent expiry and gross-to-net deductions are material |
| `advertising` | Valid eligible impressions, one fill factor, net recognized CPM | Format mix, auction pricing and traffic acquisition change independently |
| `gaming` | Users × payer conversion × payer revenue all share measurement period | Launch cohorts, payer churn, virtual-goods deferrals or franchise decay dominate |
| `cohort_subscription` | Customer bridge, weighted time contribution and unit revenue compatibility | Cohort age, expansion/contraction or multiple plan tiers differ materially |
| `delivery_pipeline` | Order/delivery/cancellation units match, opening and closing orders reconcile | Deliveries precede acceptance or advance payments are confused with revenue |
| `milestone_royalty` | Eligible third-party sales, enforceable royalty rate and earned milestones | Clinical probability, cap/floor, clawback or variable-consideration constraints are material |
| `insurance_service` | Service-unit revenue reconciles to insurance-revenue disclosures | Full IFRS 17 measurement is required; use a disclosed accounting bridge/direct_revenue |
| `reserve_depletion` | Same-unit economic reserves; depletion leads to saleable output; revisions do not | Patent expiry, retirement, land development or mismatched ore/metal units are being substituted |

The bank model is a revenue bridge, not a full balance-sheet/repricing simulation. The insurance model is a disclosed service-revenue approximation, not an actuarial IFRS 17 engine. Negative revenue line items and extreme stresses may fall outside generic nonnegative segment contracts; do not hide them with an unsupported positive plug. Preserve the gap and use an accounting-consistent alternative representation.

## Double-counting gates

- Do not add market growth, customer growth, capacity growth, and substitution growth when they describe the same units.
- Do not multiply ARPU by another monetization factor when ARPU already represents revenue per user.
- Do not add churn and expansion separately when NRR already contains them.
- Do not add mix premium outside unit revenue when realized unit revenue already embeds mix.
- Do not use reserves, TAM, pipeline value, total bookings, or announced capacity as revenue drivers without a conversion identity.

## Fallback policy

Use `direct_growth` only when an operating identity cannot be built from disclosed data. State the missing drivers in `data_gaps`. Use `direct_revenue` for accounting-defined streams whose internal mechanics cannot be represented safely, including many IFRS 17 insurance-revenue forecasts. Both fallbacks reduce the explicit-model component of confidence.

The scoring penalty is not evidence that a more complex model predicts better. Prefer an honest fallback to invented operating detail, and compare candidate models against frozen out-of-sample benchmarks before claiming improved accuracy. Industry and lifecycle breadth comes from economic routing and explicit assumptions, not from assigning every company a unique formula.

## Adding a model safely

1. Create one frozen `ModelSpec` with a unique `model_id`, complete required/optional drivers, defaults, dimensions, ratio-driver metadata, displayed formula, and a pure calculator.
2. The calculator receives only base revenue, resolved driver arrays, and forecast years. It must not read files, call an LLM, fetch data, mutate inputs, or introduce assumptions.
3. Register the spec once in `MODEL_REGISTRY`; duplicate IDs and incomplete dimension coverage must fail at import time.
4. Add the model to `tests/test_models.py` and `tests/test_industry_end_to_end.py`. Registry IDs, formula cases, and industry fixtures must remain exactly aligned.
5. Never add `if model == ...` or `elif model == ...` to `calculate_model_path`. Parameter resolution and common finite/non-negative checks remain in `revenue_core.py`; model-specific stock-flow continuity belongs in the registered calculator.
