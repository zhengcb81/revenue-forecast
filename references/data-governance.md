# Revenue data governance

## Source hierarchy

The calculation engine accepts these source types and records their ranks as metadata:

| Rank | Accepted source types | Intended use |
|---:|---|---|
| 1 | `audited_filing`, `exchange_filing`, `regulatory_filing`, `official_statistics` | Reported revenue, segment notes, accounting policies, official industry data |
| 2 | `company_release`, `investor_presentation`, `earnings_transcript`, `official_operating_data` | Guidance and operating KPIs |
| 3 | `contract_award`, `customer_filing`, `tender_document`, `sector_regulator` | Orders, customer validation, regulated volumes or tariffs |
| 4 | `industry_association`, `primary_market_dataset` | Market size, shipments, capacity, utilization, adoption |
| 5 | `specialist_research`, `reputable_news` | Corroboration and leads |

Search snippets, aggregators, social posts, and model-generated summaries are leads only and cannot be registered as sources.

## Source contract

Every source requires:

- `source_id`;
- accepted `source_type`;
- title and publisher;
- HTTPS URL to the underlying page or filing;
- `published_date` and optional `accessed_date`;
- page, table, note, paragraph, or section locator.
- a schema-1.0 capture receipt binding the tool trace, capture date, whole-source snapshot hash, untrusted-data treatment, and prompt-injection disposition.

The script rejects placeholder domains, local addresses, common search-result hosts, unsupported source types, malformed dates, and sources published after the model `as_of_date`.

Important: syntax and receipt validation cannot prove that a URL is accessible, that a model truly used the named tool, or that the content supports a parameter. They prove internal linkage and tamper evidence. The research agent must open the underlying page and verify the cited passage before registering it; authenticated invocation proof belongs to the host harness.

Source rank does not directly raise forecast confidence. Confidence uses revenue-weighted verified claim coverage, claim support type, and freshness, preventing a user-declared high-rank source from mechanically increasing the score.

## Evidence claim contract

Growth-driver evidence uses the same checked claim registry as numerical parameters; do not create a parallel citation system. Search-result snippets, unsourced summaries, and model-generated text are discovery leads, not evidence claims. Product reviews, channel stock-outs, weather, peer performance, and similar observations may support an indirect node only when their inference distance is disclosed and the causal bridge to the company's modeled revenue driver is explicit.

Do not connect parameters directly to a URL and call that evidence. Register a claim with target identity, locator, short checked excerpt, excerpt hash, retrieved-content hash, verification status/person/date, and extracted value/unit/period where applicable. The claim source must also be registered on the target parameter.

## Parameter identities

Use one of five kinds:

| Kind | Required evidence |
|---|---|
| `reported_fact` | At least one source ID |
| `management_guidance` | At least one source ID |
| `derived_fact` | Formula and input parameter IDs |
| `analyst_assumption` | Explicit rationale; evidence sources when available |
| `scenario_stress` | Explicit rationale |

Every parameter also requires scalar value, strict fiscal period, definition, machine-readable dimension, time basis, and currency/scale for monetary values. Forecast parameters identify `low`, `base`, `high`, or `all` in the optional `scenario` field.

Derived facts use restricted arithmetic with `x0...xn`; the engine recomputes them. A formula string without a matching value is rejected.

Do not cite a source as if it published an analyst assumption. Cite the evidence supporting the rationale and retain the assumption label.

## Research coverage gate

Complete all nine records defined in [research-coverage.md](research-coverage.md) before numerical forecasting. The gate checks whether material research conclusions enter used revenue parameters, remain explicit data gaps, or are excluded with a horizon-specific rationale. Coverage status is not a confidence-score component.

Separately complete the official management-communication and target gate in [management-targets.md](management-targets.md). Nine-dimensional thematic coverage does not prove that the latest earnings call or strategy communication was reviewed.

## Conflict handling

Normalize period, unit, currency, gross/net presentation, restatements, and fiscal calendars before comparing values. Parameters with the same definition, period, unit, and scenario but different values fail as unresolved conflicts. Resolve them by documenting different definitions or selecting the authoritative source before calculation.

## Historical and base gates

Require at least two ordered, consecutive historical company-revenue observations unless `pre_revenue=true`. Historical years cannot exceed the base year. A company with no history may be pre-revenue only when the reported and segment base are zero. The base-year observation must equal reported total; segment bases plus signed adjustments must also reconcile.

## Structured data

Prefer official machine-readable data where available, but reconcile it to the filing. The SEC provides submissions and XBRL companyfacts APIs without authentication; fiscal dates, units, taxonomy tags, amendments, and custom extensions still require review:

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## Freshness

Use quarterly or faster evidence for users, bookings, shipments, capacity, utilization, prices, and market share; annual evidence for slow-moving installed bases; and event-driven updates for approvals, launches, contract awards, acquisitions, disposals, and policy changes.
