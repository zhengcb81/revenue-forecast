# Money Unit Conversion (`rf-input-quantity/1`)

The single money-unit description for research input quantities: one finite
Currency x Scale vocabulary derived in `scripts/research/input_quantities.py`,
shared by the conversion entry, the record validator, the sensitivity builder
and the sensitivity consumer. There is no second hand-written currency list.

## Unit table

Money units are named `{currency}_{scale}` and only same-currency scale
conversion exists. Cross-currency conversion is always refused — this layer
never queries, guesses or stores an FX rate.

| Currency (aliases) | Canonical | Scales (factor in base currency) |
|---|---|---|
| `usd` | `usd` | `usd_unit` (1, 元), `usd_thousand` (1e3, 千), `usd_10k` (1e4, 万/wan), `usd_million` (1e6, 百万), `usd_100m` (1e8, 亿/yi), `usd_billion` (1e9, 十亿) |
| `rmb` (`cny` is the same currency; both normalize to the existing `rmb_*` names) | `rmb` | `rmb_unit`, `rmb_thousand`, `rmb_10k`, `rmb_million`, `rmb_100m`, `rmb_billion` (same scale ladder) |
| `hkd` | `hkd` | `hkd_unit`, `hkd_thousand`, `hkd_10k`, `hkd_million`, `hkd_100m`, `hkd_billion` (same scale ladder) |

Scale spellings: `unit`/`元`, `thousand`/`千`, `10k`/`wan`/`万`,
`million`/`百万`, `100m`/`yi`/`亿`, `billion`/`十亿`. Pre-DU5 canonical names
(`usd_million`, `usd_thousand`, `usd_billion`, `rmb_million`, `rmb_billion`,
`rmb_100m`) are unchanged and re-derive stored records byte-identically.

Share-of-total units (unchanged): `pp` (`percentage_point`), `percent` (`pct`,
`%`), `ratio` (`fraction`), `basis_point` (`bp`, `basis_points`). Count units
(unchanged): `units`, `thousand_units`, `million_units`.

Unknown spellings are rejected, never guessed:

- a currency-less `万元` / `wan_yuan` / `wan` / `亿` / `百万` is **unknown**
  (error), never defaulted to RMB; a context-free spelling has no calling
  context to resolve against;
- multi-currency expressions (`usd_hkd_million`, `usd hkd million`) never
  resolve;
- the only "context" that resolves a currency-less scale is the parameter's
  own declared `currency`/`scale` (see below), e.g. a HKD document with
  `unit: 万` pairs with `hkd_10k` records.

## Public usage

```python
from research.input_quantities import (
    convert_input_quantity,        # human unit -> engine contract unit
    validate_input_quantity_record,   # re-derive a stored record (fail closed)
    build_sensitivity_test,        # auditable sensitivity shock construction
    validate_input_quantity_for_parameter,  # consumer-side parameter check
)

# Same-currency scale conversion only. 7.25 yi HKD = 725 million HKD.
record = convert_input_quantity(7.25, input_unit="hkd_100m", engine_unit="hkd_million")

# Sensitivity construction: optional engine_unit converts for real (the
# converted number is what the engine applies); omitted keeps legacy behavior.
test = build_sensitivity_test(
    parameter_id="revenue_2027", value=7.25, input_unit="hkd_100m",
    shock_semantics="absolute", engine_unit="hkd_million",
)
# test["shock_value"] == 725.0 and test["input_quantity"] is the audit record.
```

`shock_semantics` keeps relative and absolute shocks apart: `additive`
(pp/bp on a ratio), `multiplicative` (percent factor), `absolute` (money or
count amount in the parameter's own unit). An explicit `engine_unit` must be
the engine's contract unit for share shocks (`ratio` or `basis_point`) — a
human spelling like `pp` is never accepted as an engine target, because
relabeling 5 pp as `shock_value=5` would read as 500 pp.

## Consumer check (real parameter unit)

The sensitivity consumer (`scripts/analysis/sensitivity.py`) calls one helper,
`validate_input_quantity_for_parameter`, for every stored `input_quantity`
record. It re-derives the conversion (including the factor line in
`conversion`), then checks the record against the parameter's real unit as
bound by the document contracts (`currency == data["currency"]`,
`scale == data["unit"]` on monetary dimensions):

- shock semantics: `percent`/`percentage_point`/`basis_point` need a
  share-of-total unit; `absolute` needs a money or count unit — the two never
  mix;
- dimension: money units only shock pure monetary dimensions (`revenue`,
  `monetary_balance`, `backlog`); a monetary-per-unit dimension
  (`revenue_per_unit`, `revenue_per_activity`, `revenue_per_area`) gets a
  clear diagnostic — the per-unit denominator is never dropped; count units
  only shock `quantity`/`activity`/`coverage_units`;
- currency family: the record's currency must match the parameter's currency
  (CNY and RMB are one family; USD/HKD/RMB never mix without an FX basis);
- scale: the record's scale must equal the parameter's scale; convert to the
  parameter scale at construction time;
- an uninterpretable parameter `currency`/`scale` spelling yields a clear
  diagnostic ("cannot be safely interpreted"), never a guess.

## Evidence

- Hand oracles and the public-entry E2E (synthetic HKD document, 0 API/0
  model): `docs/plans/du5-units-2026-10-15/receipts/e2e-run.json` — 7.25 亿
  = 725 百万, 5 十亿 = 5000 百万 and both reverses checked against hardcoded
  constants; the converted shock moves terminal revenue by exactly +725 on
  `scripts/revenue_forecast.py`'s formal path; same-numbers-different-currency
  and tampered-record inputs are refused by the public CLI.
- Behavior freeze (old USD/RMB/share/count records and builder outputs,
  byte-identical conversion lines): `tests/test_du5_money_unit_registry.py`
  (`LegacyFreezeTests`).
- W08 combination matrix: `C01-USD-L`, `C01-CNY-L`, `C01-HKD-L`,
  `C01-HKD-C` (cross-currency refused), `C01-UNK-C` (unknown spelling
  refused) in `tools/model_generalization_matrix/combinations.py`.
