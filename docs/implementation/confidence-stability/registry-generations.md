# Confidence revisions in publication history

New publication registry rows derive confidence_calculation_version from the
actual forecast confidence through the scoring owner's finite revision parser.
Snapshot rows derive it from the nested forecast_result, never a caller's outer
label. Historical rows missing the field are read as stable-fsum/1 without any
row, line hash or chain rewrite. Unknown, null or malformed explicit revisions
are errors, not separate generations.

Audit generation is (input SHA, engine, schema, artifact type, confidence
revision). The same input can legitimately be rerun under source-evidence/2
without inventing a different forecast_version. Identical repeated results in
one generation are harmless; different result hashes within one generation
remain conflicts. Existing line-hash and chain checks continue unchanged.

Focused regression: tests/test_registry_confidence_generations.py, including
two native formal runs of exactly the same input under old/new confidence,
historical missing-field lines, same-generation conflicts, malformed versions,
snapshots, order/chain checks and preserved historical bytes.
