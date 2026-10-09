# W08 findings

- RF already preserves six-field causes across actual client/preparation subprocesses; protect this GREEN.
- _ClientError/_emit_error/_run_filing_fetch omit FF existing counts/stage and CWP numeric usage. Selected-source reader failures erase earlier FF observations.
- Raw top-level FF error, non-JSON stderr and exit0 failure reason leak synthetic credential/URL in actual RF final error. Closed cause validator alone cannot protect human text.
- Prior test explicitly demands raw fallback stderr in exception text. It conflicts with frozen no-leak requirement and must become a safe-diagnostic/no-echo contract, retaining failure status and no fabricated cause. An independent major reviewer must assess this change; don't merely update a literal.

## Responsibility and test semantics

Two consumer boundaries omitted a valid receipt while copying arbitrary error bodies. A shared pure decoder copies finite observed fields; malformed usage does not erase an independently valid cause. Exact schema/key/type/code/decimal checks reject malformed receipts rather than converting unknown to zero. No accounting or retry policy is moved into RF.

Two legacy tests demanded raw fallback stderr. Their unsafe diagnostic-echo expectations were replaced with fixed diagnostic/no raw echo, preserving failure and absence of fabricated cause. The third first-pass failure was an implementation regression in local named deadlines and was fixed without changing its old assertion.

## Independent-review finding W08-R1

_ClientError.candidates and _emit_error were a second arbitrary-body channel. The final preparation CLI filtering did not excuse the intermediate public CLI leak. Root independent_review_receipt.json recorded the actual v2 ambiguous child with nested error sentinel and exit2 leak. New actual v1/v2 exit2/0 tests demand valid four-field legacy identity and exact logical SourceRef output while rejecting unknown nested bodies, error-only records, URL/name injection and malformed types. The common projection is deliberately a disambiguation DTO, not another identity resolver: it does not contact providers, verify source bytes or grant permission.

## Limits

Historical failed US usage remains unknown; new tests and ceilings cannot recover it. MAIN W11 owns outer capture. source_reader labels the existing combined reader/record helper; narrative_reader is separately observed. Unrelated config/legacy free-text channels are not comprehensively migrated. New W08 controls all execute; the existing POSIX-only skip is recorded separately.
