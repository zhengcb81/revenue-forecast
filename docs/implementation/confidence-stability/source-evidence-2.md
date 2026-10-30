# Confidence source-evidence/2

This finite confidence calculation revision removes quote-multiplicity weights.
For each revenue-used parameter, freshness averages distinct original captures;
quality averages distinct (original capture, support_type) pairs. The existing
validated capture.snapshot_sha256 identifies an origin; legacy records without
a capture fall back to their source_id. This changes only scoring votes, never
the evidence claims, independent measurements, roles, numeric drivers or paths.

Same-SHA aliases count once. Conflicting known publication dates use the oldest
known date and disclose a limitation. Entirely unknown publication dates earn
zero freshness credit. Availability/read/verification dates cannot substitute
for publication dates.

New runs emit source-evidence/2. Strong replay dispatches by the recorded finite
calculation_version: stable-fsum/1 retains the original per-claim arithmetic;
an absent marker means that legacy revision with the preexisting 64-ULP bound.
Both marked revisions remain exact. Explicit null, malformed or unknown markers
are rejected. Engine 4.3.0, schema, historical output bytes and receipt hashes
are unchanged. Never relabel or refresh old outputs to the new algorithm.

Regression tests: tests/test_confidence_source_freshness.py and
tests/test_confidence_determinism.py. Author evidence and zero-model native
saved-input replay are in .planning/source-quote-adoption-20261030/m6/.
