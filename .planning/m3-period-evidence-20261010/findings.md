# Findings

- CodeGraph context/impact before literal scans: TIME_BASES in contracts/constants.py and validate_parameters in document.py. Exact literal time_basis consumers show current engine only checks annual/point_in_time; formula compute otherwise uses amount unchanged.
- Current registry binds schema3.7/3.8 to engine4.1.0/4.1.1. Current schema top-level is 3.7 or3.8 only. Roles optional; old growth driver excludes only peer_analogy, other history/financing sources incorrectly count.
- Existing source clock/1 and research diagnostics plus signed base DAG are already present and are not recreated.
- Proposed new schema3.9 opt-in carries both features. Default canonical3.7 kept to avoid silently reinterpreting old input; current engine version4.2.0 will be explicitly documented. New schema3.9 supports existing operating_units; old3.8 remains opt-in. Registry old emitting sets remain explicit, while newengine can emit legacy shape only with legacy semantics. MAIN will wire new output schema acceptance and strong check.
