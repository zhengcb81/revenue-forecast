# Existing local originals as RF source provenance

## Completed engineering milestone

Previously a verified local original with unknown source URL could be rejected by both RF preparation and persisted forecast input. Both boundaries now share the pure `contracts.company_wiki_original` DTO rules and `contracts.source_provenance` provenance rule. An explicit null URL requires exact CWP manifest/reference/read-receipt/capture binding regardless of `require_capture`; actual bytes remain verified by the public owner read. HTTP URL validation is unchanged. No URL, fiscal year or publication date is invented, no provider resolution is added, and optional signatures remain optional.

Malformed capture shapes now stop dependent accesses after collecting an error, using existing shape rules. The permanent regression package covers IR/prospectus/convertible offering, 2.1/2.2 receipts, unknown dates, tampering, collector behavior and immutable inputs.

Validation: 181 passed / 1 existing skip in 2.68s across eight affected modules; mypy 14 source files; scoped ruff; independent frozen 25 tests passed / 0 OPEN, six source/test paths sealed. A real CN IR original was registered in an owned isolated catalog and opened by the actual RF→CWP binary reader, then validated as RF source input: zero network/download/model/raw copies, original/config unchanged and temporary lake removed. First experiment supplied an incomplete candidate DTO; corrected by translating the real owner manifest to the existing candidate DTO, without changing production validation. Initial test harness import failures were fixed in the test entry, not production.

## Remaining mainline work

This proves source preparation/input acceptance, not narrative adoption or an actual forecast parameter. Summary omissions, attribution/degree/modality fidelity, real summary/cache recovery and RF parameter/formula adoption remain OPEN under company-wiki `docs/plans/du11-source-closure-2026-10-18/review/source-information-20261030/description-final/SUMMARY_QUALITY_IMPLEMENTATION.md`. No FF request capability is invented by this change. RF pre-existing assurance WIP is excluded.
