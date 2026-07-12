# Executable revenue model library

Assign models per segment. The exact model and driver names below match `scripts/revenue_core.py`.

| Model | Required drivers | Optional additive drivers | Formula |
|---|---|---|---|
| `direct_growth` | `growth_rate` | — | prior revenue × (1 + growth rate) |
| `direct_revenue` | `revenue` | — | explicit recognized revenue |
| `unit_sales` | `units`, `unit_revenue` | `timing_factor`, `other_revenue` | units × unit revenue × timing + other |
| `capacity_utilization` | `capacity`, `utilization`, `yield`, `unit_revenue` | `timing_factor`, `other_revenue` | capacity × utilization × yield × unit revenue × timing + other |
| `subscription` | `average_customers`, `revenue_per_customer` | `timing_factor`, `usage_revenue` | average customers × revenue/customer × timing + usage |
| `usage_platform` | `eligible_activity`, `monetization_rate` | `fixed_revenue` | eligible activity × monetization rate + fixed |
| `services` | `billable_capacity`, `utilization`, `billing_rate` | `timing_factor`, `other_revenue` | billable capacity × utilization × billing rate × timing + other |
| `project_backlog` | `opening_backlog`, `bookings`, `cancellations`, `contract_changes`, `closing_backlog` | — | opening + bookings − cancellations + changes − closing |
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
| `cohort_subscription` | opening, new, churned, ending customers; revenue/customer | `timing_factor`, `usage_revenue` | average opening/ending customers × revenue/customer × timing + usage |
| `delivery_pipeline` | opening orders, new orders, cancellations, deliveries, ending orders, unit revenue | `timing_factor`, `other_revenue` | deliveries × unit revenue × timing + other |
| `milestone_royalty` | `eligible_sales`, `royalty_rate` | milestone and service revenue | eligible sales × royalty rate + milestone + service |
| `insurance_service` | `coverage_units`, `revenue_per_coverage_unit` | `timing_factor`, `other_revenue` | coverage units × revenue/coverage unit × timing + other |

## Selection notes

- Split product and after-sales service when their drivers differ.
- Split subscription and usage-based streams when ARPU does not already include usage.
- Use average customers, stores, AUM, occupied area, or earning assets where revenue accrues through the period.
- Use commissioned revenue-capable capacity, not announced capacity.
- Treat `yield` as manufacturing yield only in `capacity_utilization`; in `transport`, `yield` means revenue per utilized capacity unit.
- Use average earning assets and liabilities in the bank model. Do not substitute period-end total assets.
- Use `cohort_subscription` when opening/adds/churn/ending data are available; the engine enforces the stock-flow bridge and continuity.
- Use `delivery_pipeline` when order units convert to delivered units; the engine enforces order continuity and base opening orders.
- Use `insurance_service` only when coverage/service units reconcile to IFRS 17 disclosures; never substitute premiums collected.
- Use `timing_factor` for year-in-service, commissioning, or explicit seasonal availability. Do not use it as an unsupported growth plug.

## Double-counting gates

- Do not add market growth, customer growth, capacity growth, and substitution growth when they describe the same units.
- Do not multiply ARPU by another monetization factor when ARPU already represents revenue per user.
- Do not add churn and expansion separately when NRR already contains them.
- Do not add mix premium outside unit revenue when realized unit revenue already embeds mix.
- Do not use reserves, TAM, pipeline value, total bookings, or announced capacity as revenue drivers without a conversion identity.

## Fallback policy

Use `direct_growth` only when an operating identity cannot be built from disclosed data. State the missing drivers in `data_gaps`. Use `direct_revenue` for accounting-defined streams whose internal mechanics cannot be represented safely, including many IFRS 17 insurance-revenue forecasts. Both fallbacks reduce the explicit-model component of confidence.
