# Causal revenue growth-driver tree

## Purpose

The forecast formulas answer **how much revenue** each segment produces. The growth-driver tree answers **why the Base path could happen, what evidence supports it, and what would disprove it**.

Keep the first view short: normally three to five positive drivers, ranked by terminal revenue increment. Keep the underlying tree complete and auditable. If only one or two material drivers are supportable, show one or two; never manufacture entries to reach a display count.

## Universal causal structure

Do not force companies into an industry taxonomy. Start with the company's economic identity and trace a material mechanism through whichever stages apply:

```text
external condition or company action
→ offer / capability / capacity / distribution change
→ customer eligibility, adoption, retention, usage, price, or mix
→ delivered activity under real constraints
→ accounting recognition
→ segment revenue
→ company revenue
```

Common candidate lenses include market expansion, share gain or substitution, product/category/geography/customer/channel expansion, price or mix, capacity and utilization, installed-base monetization, retention and usage, backlog conversion, regulation, acquisitions, and business-model transitions. These are prompts for discovery, not allowed-value enums and not automatic conclusions.

Build the chain from the model in both directions:

1. Starting from the segment formula, ask what real-world facts determine each Base parameter.
2. Starting from researched catalysts, ask which volume, price, mix, customer, activity, utilization, backlog, or recognition parameter would change.
3. Reject a story that cannot meet in the middle.

## Evidence branches and inference distance

Each root has one or more evidence nodes. `evidence_type` is an analyst-defined label so the framework remains industry-neutral. Useful labels may describe company execution, customer demand, product competitiveness, channel availability, capacity, market structure, regulation, or independent operating indicators.

Classify inference distance:

- `direct`: the checked evidence directly states or measures the company variable being modeled;
- `one_step`: one explicit causal bridge connects the evidence to the modeled variable;
- `analogical`: a peer, adjacent product, geography, or historical analogy supports direction but not company magnitude;
- `contrary`: checked evidence weakens or falsifies the driver.

A driver is `triangulated` only when non-contrary support contains at least two distinct evidence types and at least two distinct sources. A limited driver may remain in the model, but the report calls out the limitation. Source count alone is not triangulation when several articles repeat the same underlying fact.

Examples of disciplined inference:

- Extreme weather plus peer sell-through supports category demand. It does not prove the subject company's sales without company availability, channel, shipment, or market-share evidence.
- Product reviews support relative competitiveness. They do not prove overseas volume without launch scope, homologation, distribution, orders, deliveries, or capacity.
- A domestic capacity expansion supports possible supply. It becomes revenue only after demand, delivery, constraints, and recognition are modeled.

## Search workflow

For every candidate root:

1. Write the exact causal claim and the parameter it would affect.
2. Search official filings, releases, transcripts, presentations, operating disclosures, customer/regulatory records, and other primary evidence first.
3. Search independent demand, channel, product, capacity, or industry evidence to test the bridge rather than merely repeat the company statement.
4. Search explicitly for delays, weak demand, price pressure, failed launches, customer loss, capacity constraints, regulation, substitution, and accounting timing that could break the chain.
5. Open each cited source, register a checked `growth_driver` claim, and mark inference distance.
6. Record `found`, `searched_none_found`, or `data_gap` for counterevidence; silence without a documented search is not confirmation.

## Structural versus temporary growth

Classify persistence as `multi_year_structural`, `cyclical`, `temporary`, or `uncertain`, with a rationale. A short weather event, stock-out, subsidy, launch spike, or comparison-base effect may reveal demand but should not be extrapolated across years without evidence for capacity, repeated exposure, distribution, installed base, or durable share.

Separate the observation from the durable mechanism. For example, a stock-out is an observation; repeated category demand plus expanding distribution and supply can be a multi-year mechanism.

## Quantitative attribution and ranking

Every root maps to parameter IDs that actually enter the Base path. It does not write a second revenue forecast or add an arbitrary CAGR premium.

For driver `d` and segment `s`:

```text
driver terminal increment(d)
= Σ [Base terminal segment increment(s) × attribution weight(d,s)]
```

Across all roots, weights for each segment sum to one. This permits several causal mechanisms to share one segment without double counting. Positive roots are ranked by computed increment; negative roots are reported as headwinds. Company-level forecast adjustments remain separately visible because the existing company bridge may not assign a base adjustment to an individual operating root.

## Output shape

The concise section includes rank, title, one-sentence thesis, Base terminal increment, share of positive driver increment, and evidence status.

The detailed tree expands each root into:

- causal chain;
- segment attribution and quantified impact;
- actual Base parameter IDs;
- horizon and persistence;
- evidence nodes, claims, sources, types, and inference distance;
- leading indicators;
- falsifiers;
- counterevidence search result;
- reconciliation to the segment and company increment bridge.
