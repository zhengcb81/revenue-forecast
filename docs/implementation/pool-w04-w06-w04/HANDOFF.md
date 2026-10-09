# W04 RF complete source result and narrative input consume

Functional commit: `33404bd6daeba4be33a8ba407bb6362fa45b162e`; base `8b48a99f23a19b1fd71a7e051837a55e12bb7d30`.

`resolve_filing_result` preserves the validated full FF machine result. `resolve_filing` still selects only the filing. `prepare_source_result` emits source-preparation-result/1 with source, filing_fetch, and explicit narrative read receipt. `prepare_source` and default CLI remain source-only. Latest uses the producer-resolved candidate year and the same verified manifest; exact year remains strict. Counts stay producer-owned and unknown stays null.

`consume_narrative_input` reads one exact bundle once, creates claims only from caller-selected parsed spans, binds them to an existing source capture and used parameter, and records actual model/driver/output dependencies. An unreferenced summary is not_consumed. Invalid or unavailable references do not fall back to raw/audit paths or a model. The linked input is a new copy.

RED: 5 failed/3 passed, exit 1, 0.42 s. Final concentrated GREEN: 145 passed, exit 0, 7.23 s. Ruff --no-cache and public-contract mypy passed. Local raw-open proof is the exact producer fixture with same-call manifest, two synthetic fiscal calendars, and negative period/as-of cases. This is local engineering evidence, not a real paid-summary or economic M2 PASS.

Actual CLI:

```text
python -X utf8 -B scripts/source_preparation.py --request-file <request> --company-wiki-catalog-config <catalog> --company-wiki-config <ff_config> --filing-fetch-root <ff_root> --result-envelope
python -X utf8 -B tools/run_narrative_consumption_e2e.py --input <new_input> --narrative-request <exact_read_request> --bindings <span_claim_parameter_bindings> --source-id <input_source_id> --catalog-config <catalog> --output-root <absent_owned_root>
```

The recipe produces linked-input.json and consumption.json; MAIN next runs native validation, compute, report, and snapshot. It has no --case flag or company special branch. Prepare can optionally read an existing same-source narrative with --narrative-request-file, and that read alone stays not_consumed until input bindings exist.

No supplier/model/network call, installation, push, upstream/production write, or production original deletion occurred. Every rW04-* TEMP root was absent initially and restored in finally. Recorded FF calls=3/downloads=0 and independent transcript entitlement remain unchanged. Exact changed-file SHA and installation closure are in handoff.json.

Remaining: MAIN W03/M2 must provide a real canonical summary and run actual consume. Current producer golden covers TXT/PDF transport; HTML and unknown-language extensions require the real W03 exported contract, not consumer invention. W05/W06 proceed on this functional commit.

## HTML follow-up

Functional commit `a7c2c73758e7b7bbb6454c2955390f179f2d5f28` consumes the exact W03 exported HTML engineering golden through the existing route. RED: missing lineage 1 failed / 14 passed; GREEN: 146 passed, 5.56s, exit 0. Producer golden is synthetic loopback, not a paid/current company original read. Runtime closure also includes `scripts/company_wiki_narrative_contracts.py`. The earlier HTML-awaits-W03 limitation is resolved. Configured `.githooks` is absent; normal commits ran no hook; MAIN owns canonical gate.

## Nullable nonfinancial SourceRef follow-up

Functional commit `73a03b5751cd9e95d166104f31210cc642af0a6c`. RED 5 failed / 5 passed, 0.54s; GREEN 75 passed, 1.40s, exit 0. Shared period semantics keep only annual/semi-annual/quarterly financial reports strict; legitimate nonfinancial null stays null, positive exact-year requests still match. No false fiscal year is supplied. `prepare_registered_source_result` passes an already registered pathless candidate to the same binary reader and SourceCapture builder, without asking FF to resolve official IR/call content. IR maps to company_release, investor_call_transcript to earnings_transcript. This is verified engineering fixture replay; actual current-config original reads remain MAIN.

`handoff.json` now contains all three functional commits, exact current branch file hashes and read-only old/new SHA values for both installed skills. No installation took place. It supersedes earlier single-commit path hashes where later W04 fixes changed files.
