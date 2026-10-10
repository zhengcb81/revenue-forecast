# W07 RF period flow and mechanism role contract

Owner: m3_rf_flow_role_implementation. Base/remote main 0c248d9a07a2dd7a2c756946d88507479d5e9d15. Branch codex/m3-period-evidence-20261010. Independent worktree rf-period-evidence-20261010.

## Scope
Explicit new schema and engine capability for dated period flows and same-proposition scoped mechanism triangulation. Existing schema 3.7/3.8 artifacts keep byte identity and declared old semantics. No source/network/model calls, raw changes, production config changes, assurance/output edits, whole skill install or full raw lake copy.

## Phases
1. Current consumer/compatibility inventory and DTO: complete (contract_consumer_map.json).
2. RED contract tests for periods/roles/old versions: in_progress.
3. Implement pure contracts, role filtering, compatibility and authoring: pending.
4. Focused GREEN, real half-year read-only conversion evidence, old byte controls: pending.
5. Normal commit/push, exact CI and MAIN output/install handoff: pending.

## Next Step
Write tests/test_m3_period_flow_contract.py, test_m3_evidence_roles.py, test_m3_schema_compatibility.py (RED) against the decided matrix: schema 3.9 opt-in + engine 4.2.0, 3.7/3.8 emit sets frozen to {4.1.0,4.1.1,ENGINE_VERSION}; role-aware triangulation gated on 3.9.

## Decisions
- Version matrix per existing registry pattern: new schema 3.9 requires a new engine row; SKILL_VERSION 4.1.1->4.2.0 in constants.py (write-set). 3.7/3.8 rows become {"4.1.0","4.1.1",ENGINE_VERSION} to preserve 4.1.1 history after the bump. CHANGELOG/SKILL.md/old version-pin tests (test_schema_compatibility.py, test_data_contract.py:463) are MAIN-owned -> MAIN_INTEGRATION_PATCH.patch; exact CI on this branch stays red on those pins until MAIN merges (card-sanctioned: version release wiring via patch, MAIN serial merge).
- period_flow contract: time_basis=period_flow + period_start/period_end only in 3.9; ISO dates, start<end, within FY window derived from fiscal_year_end (handles cross-calendar-year and non-12M fiscal years via exact fiscal span), month length in {3,6,12} or exact fiscal-year span; period fields on any non-period_flow parameter rejected in every schema; no fabricated start dates (unknown stays out of the typed contract).
- Role-aware triangulation gated on schema 3.9 only: triangulated requires >=2 evidence types and >=2 sources among nodes with >=1 mechanism_direction claim; history_base/value_range/conversion_assumption/recognition_policy/counter_comparison/peer/counterevidence nodes disclosed, not counted; mixed nodes keep valid supports and all counterevidence; confidence score unchanged by role category. 3.7/3.8 keep legacy peer-only exclusion (old triangulated results byte-preserved).
- Real 18 half-year flows located read-only: HK 10 H1 + 5 H2 in m3-20261009T184946-hk-00700/execution/native-reviewable-input-v2.json (sha 2c0f9d27...), CN 3 H1 (h124/h125/h126) in m3-20261009T184946-cn-688012/execution/forecast/native-input-v6.json (sha 01c5e19b...).

## Protected write boundary
Allowed: scripts/research/drivers.py, scripts/contracts/constants.py/document.py, new period flow pure contract, scripts/schema_compatibility.py, dedicated tests and references/CHANGELOG documenting versions. MAIN handles revenue_report.py and public output consumers; W06 handles filing_fetch_client/source_preparation. Other owners' assurance and output stay unchanged.

## Errors
No RF AGENTS.md exists. Guessed schema-engine-matrix.json and authoring.py absent; actual registry is scripts/schema_compatibility.py and authoring currently references/input-construction.md. These are inventory corrections, not product failures.
