# RF local preparation observation — ready for ROOT review

## Frozen delivery

- Worktree: C:/Users/郑曾波/Projects/revenue-forecast-r1-local-observation
- Branch: codex/r1-local-budget-observation; base674d08d92fe2ec64e1d42a3ebab0b364e0ac4354.
- Product commit: dedebe0be27bad0723e6a642be5083bf53b357fc.
- Runtime is exactly one changed file: scripts/filing_upstream_cause.py. Physical SHA256:1cefb1e79ffc4b024619ca957013aeca4c117060630ae015a1ee6679654f5c08. All bindings are in evidence/source-bindings.json.
- No merge/push/install/main mutation; ROOT owns nonauthor review and consumer-first publication. This report is an author delivery, not independent acceptance.

## What changed

Both root causes are fixed together: the complete FF failure accepts the optional local_preparation_observation, and the RF stderr decoder can carry a large complete versioned observation without losing the reason. The nine-key outer DTO is checked for version/types; operations/diagnostics are copied as bounded machine JSON. Existing RF strict JSON/pathless decoding and canonical serialization are reused. No FF import, second identity check, fiscal validation, owner budget recomputation, provider usage inference or business enum was added.

Limits: legacy complete base remains16KiB; optional compact UTF8<=128KiB; full compact<=144KiB. Existing legacy len(text)<=65536 behavior is retained. Only a complete validated extended object/RF error wrapper can use the hard1MiB UTF8 raw parse window; wrapper residual<=16KiB. Wrong schema/type/extra key, physical/body/credential fields, invalid nonfinite/depth/count/size, truncation and duplicate keys in the extended path refuse completeness. No truncation is presented as complete. The actual FF client safely strips an invalid optional object before emitting its small safe cause, so the actual preparation chain retains cause/owner exit/calls/downloads even for oversize optional data.

FF final public hygiene136ab5a: original machine schema grammar with explicit drive:/, scheme:// and absolute file:/ rejection; opaque URN namespace and file:missing remain legal. RF does not duplicate FF status enums or numeric quota ranges. local_io_usage remains null. provider_started=false/usage_complete=true concern provider work, not local reading0; owner observed_charge_bytes>charged_read_bytes is unchanged. Owner-trigger/counter facts are not interpreted.

## Evidence and boundaries

- RED base code:8F/36P/3.29s, including both actual RF CLI stages small/large; logs/XML retained.
- Final same-class suite and affected suites:201P/1 pre-existing opt-in skip/0F/14.52s (56 new cases, none skipped).
- Existing full ruff scope PASS; existing12 public mypy+focused helper=13 files PASS; normal existing precommit ruff/mypy/host guard all PASS.
- Host guard kept direct malicious input literals. Exactly two full rule/file/value negative cases have per-case rationale in the existing baseline registry, following ROOT instruction and FF practice; no guard code, blanket exemption or skip changed.
- Large fixture optional108288B; full compact108902B; native Windows pretty replay file138928B; client stderr113111B; preparation stderr113093B. Measured stderr lengths are UTF8 of captured normalized text; see wire-sizes.json. Small and large logical payloads compare exactly at each RF boundary.
- Frozen fixture comes from actual FF serializer at6dbb9e84; new tests replay it into real RF client/preparation subprocesses. This lane does not claim a fresh full CWP->FF->RF run; ROOT owns real combined producer integration. No network, API, key read, source rescan, originals, paid summary or business-quality acceptance occurs here.
- The known failing H1 budget condition remains a genuine failure with preserved diagnosis. This compatibility change does not complete that company forecast or invent missing metrics.

## Cleanup and next action

Mother RF three tracked assurance WIPs retain their exact original SHA256; output was never read/copied/changed. Only owned test scratch .planning/r1rfobs was removed after compact evidence was copied; cleanup.json proves restored absence. Existing other-worker/old W04 directories/config/originals were untouched.

ROOT: independently inspect the one runtime source and finite counterexamples, run the real combined producer chain against finalFF, then publish/install RF consumer before FF/CWP producers. Revert product commit to roll back code only; no original or ledger migration is required. The current branch must not be called merged or installed before ROOT does so.
