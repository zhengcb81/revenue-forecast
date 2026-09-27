# recovery/README.md — I-08-C-RESIDUAL / a20260923-01

**Recovery = NOT APPLICABLE for product state; documentation-only card.**

- This card performs no stateful product operation: no transaction, lock, migration,
  registry write, download or worker start. The publication registry was redirected into
  `%TEMP%\I08C-RESIDUAL-a20260923-01\run\runner\registry*` for every pytest invocation,
  so no formal `run_forecast` could append to any repository registry.
- If interrupted at any point: the attempt directory is self-describing (`oracle.md` is
  frozen-first; `commands.json` holds the frozen expectations; `evidence/` holds raw runs
  under distinct labels; `handoff.json`'s `next_step_number`/`next_action` name the first
  unfinished action). Nothing outside `<ATTEMPT>/` and `%TEMP%\I08C-RESIDUAL-a20260923-01\`
  was written, so there is nothing to roll back in any repo or historical attempt.
- `%TEMP%` scratch (`fixed/`, `m6/`, `run/`, `basetemp_*`) is disposable and NOT evidence;
  the judged-run raw that matters is preserved under `evidence/` (register §72 rule).
- Historical artifacts (referenced attempts) were verified untouched at completion
  (`evidence/manifests_comparison.json`); if a future reader finds them changed, that is
  a post-hoc external change to be ledgered — never repaired in place (same discipline as
  the B5 binding-mismatch precedent).
