# M3-FLOW: Dated Period Flows and Mechanism Evidence Roles (schema 3.9)

Work package W07 remediation of frozen root causes R19/R20: at least 18 real
half-year revenue flows (HK 10 H1 + 5 H2, CN 3 H1) wore `time_basis=annual`
because the vocabulary only offered `annual`/`point_in_time`, and the
growth-driver triangulation counted any two sources/types — including
historical bases and financing background — as if they proved a future growth
mechanism. This note is the engineering contract for the fix; calibrating the
actual forecast magnitudes with these flows is follow-up research, not part of
this capability.

## Version matrix (decided from the existing registry, not assumed)

| schema | emitted by | notes |
|---|---|---|
| 3.7 | 4.1.0, 4.1.1, 4.2.0 | canonical; unchanged semantics |
| 3.8 | 4.1.0, 4.1.1, 4.2.0 | +`operating_units` opt-in |
| 3.9 | 4.2.0 | +`period_flow` dates and role-aware triangulation |

Engine 4.1.x never emitted schema 3.9 and fails closed on it in every read
mode. Old 3.7/3.8 artifacts keep validating against their declared emitting
engine (4.1.0/4.1.1 included); frozen bytes, hashes and published
`triangulated` results are not re-judged by the new rule.

## Period flow contract (`scripts/contracts/period_flow.py`)

Pure rules, no I/O, enforced by `contracts/document.py:validate_parameters`
only when `schema_version == "3.9"`:

1. `time_basis="period_flow"` requires `period_start` and `period_end`
   (strict ISO days, `period_start < period_end`).
2. The window must lie inside the fiscal year of the `FYyyyy` `period` label
   resolved from `fiscal_year_end` (Feb-29 FYE anchors to Feb-28 in non-leap
   years so windows stay contiguous). Cross-calendar-year flows and
   non-calendar fiscal years need no extra vocabulary.
3. The covered length must be 3, 6 or 12 whole months (inclusive-day count
   over the average calendar month, tolerance 0.2 months). Amounts belong to
   the covered window; nothing annualizes implicitly. `H1 + H2 = annual` holds
   only through an explicit derived formula with identical unit/currency.
4. `period_start`/`period_end` are rejected on every non-`period_flow`
   parameter in every schema; `period_flow` itself is rejected on 3.7/3.8.
5. `point_in_time` stocks are untouched: same basis, no period dates, never
   doubled.
6. Unprovable start dates stay unknown — the contract requires both endpoints,
   so an author must evidence them or keep the flow out of the typed basis.

## Mechanism role contract (`scripts/research/drivers.py`)

Gated on schema 3.9 (`role_aware`):

* A supporting evidence node counts toward `triangulated` only when at least
  one of its claims carries `evidence_role="mechanism_direction"`; two
  distinct evidence types and two distinct sources are still required.
* `history_base`, `value_range`, `conversion_assumption`,
  `recognition_policy`, `counter_comparison`, `peer_analogy`, `counterevidence`
  and unroled claims remain fully disclosed in `evidence_nodes` with all
  counter-evidence rows — mixed nodes keep their valid mechanism supports.
* Drivers that lose triangulation get an explicit limitation naming the
  missing future-mechanism evidence.
* Confidence scoring never reads the role category, so the change cannot
  inflate confidence.
* On 3.7/3.8 the legacy rule (peer analogies excluded only) is byte-preserved.

## Authoring

`generate_input_template.py --schema {3.7,3.8,3.9}` selects the version; the
skeleton stays annual-basis by default because period dates are facts to be
evidenced, never templated. `references/input-construction.md` carries the
author-facing rules (see "Dated period flows (schema 3.9 opt-in)" and
"Mechanism evidence roles (schema 3.9 opt-in)").

## Real 18-flow mapping (read-only control)

The two real artifacts below were read, never modified; their half-year flows
map 1:1 onto the new contract under a 12-31 fiscal year end.

| artifact | byte sha256 | flows |
|---|---|---|
| `revenue-forecast-audit/runs/m3-20261009T184946-hk-00700/execution/native-reviewable-input-v2.json` | `2c0f9d27301fc1f9455637f62d6b9f33e0d1b7f542a125a903ffca5b0548ee2d` | `{games,socialnetworks,marketingservices,fintechbusiness,others}_h1_{2025,2026}` (10 reported facts, Jan–Jun) + `{...}_h2_2025` (5 derived facts `x0-x1`, Jul–Dec) |
| `revenue-forecast-audit/runs/m3-20261009T184946-cn-688012/execution/forecast/native-input-v6.json` | `01c5e19b9eaadb4fbd1798f51bd1c364c557ce411bed3fffc3e4ca7220a947bc` | `h124`/`h125`/`h126` (3 reported facts, FY2024/25/26 Jan–Jun, CNY million) |

The mapping table with per-flow rows (original value, unit provenance,
resolved window, unknown policy) is
`.planning/m3-period-evidence-20261010/real_flow_mapping.json` in the lane
worktree; a converted 3.9 control document validates against this code. The
original runs are untouched — remediated research re-attempts belong to W08+.
