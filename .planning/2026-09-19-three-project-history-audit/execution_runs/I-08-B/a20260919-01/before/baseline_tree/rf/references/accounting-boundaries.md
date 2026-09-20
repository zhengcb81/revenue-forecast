# Revenue accounting boundaries

## Customer contracts

IFRS 15 requires identifying the contract and performance obligations, determining and allocating the transaction price, and recognizing revenue when control transfers as a performance obligation is satisfied. A performance obligation can be satisfied at a point in time or over time; over-time revenue needs an appropriate progress measure.

Official reference:

- https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/

Implementation rules:

- Record `timing`, `trigger`, `presentation`, matching modeled presentation, and accounting-policy claim IDs for every segment.
- Require `progress_measure` and scenario progress parameter IDs for over-time recognition. Recognized revenue is recomputed as modeled revenue times progress.
- Use `lagged_activity` when modeled activity precedes acceptance or another point-in-time trigger; supply carry-in revenue and retain the unrecognized tail.
- Split streams when a contract contains materially different recognition patterns.

## Principal versus agent

Gross merchandise value, payment volume, bookings, and customer billings are not automatically revenue. Determine whether the company controls the good or service before transfer. Use `presentation=net` for commission or take-rate revenue and `presentation=gross` only when the reporting policy supports gross recognition.

## Projects and backlog

Reconcile opening backlog, bookings, cancellations, contract changes, recognized revenue, and closing backlog. First-year opening backlog must match a source-claimed base backlog parameter; subsequent opening balances equal prior closing balances. Use project-level schedules when maturities differ materially.

## Banks

For a top-line operating-revenue bridge, calculate net interest income from average earning assets and average interest-bearing liabilities, then add fee and other reported revenue. FDIC defines NIM using average earning assets:

- https://www.fdic.gov/resources/supervision-and-examinations/examination-policies-manual/section5-1.pdf

## Insurers

IFRS 17 presents insurance revenue separately from insurance finance amounts and excludes investment components from insurance revenue. Do not substitute written or collected premiums for insurance revenue.

Official reference:

- https://www.ifrs.org/issued-standards/list-of-standards/ifrs-17-insurance-contracts/

Use a reported insurance-revenue path or a service-unit model only when it reconciles to the company’s IFRS 17 disclosures.
