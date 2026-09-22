# REM79-MECHANIZATION — recovery / re-run guide

Attempt: `.planning/2026-09-19-three-project-history-audit/execution_runs/REM79-MECHANIZATION/a20260922-01`
Interpreter: system `python` 3.13 (stdlib only, no network, no venv needed). Run every command
with cwd = this attempt directory. Use `-X utf8 -B` for deterministic UTF-8 output.

## What is frozen

- `oracle.md` — the frozen rule, lexicons (markers + domain patterns D1–D7), corpus hash
  table, expected detect/not-detect table per file+line, exit semantics, mutation red sets.
  Frozen sha256: `6faa0ae90a0693ffeb03f9b63a811d4832d12f0e598f1699dcaf29462bdc241f`
  (re-verify: `python -c "import hashlib;print(hashlib.sha256(open('oracle.md','rb').read()).hexdigest())"`).
- `oracle_table.json` — machine twin, sha256 `366b18253c973306fc1a8ea237c377551bc3be68243e6fc83cf5f247a87edae7`.
- `evidence/freeze_record.json` — freeze timestamp, order, and all corpus hashes.
- `corpus/*.md` — six frozen files; their hashes are re-checked by `harness/verify.py`
  (guard output: `evidence/corpus_hash_guard.json`) before any RED/GREEN run.

## Re-run the whole proof (safe, writes only inside this attempt)

```
python -X utf8 -B harness/build_corpus.py        # re-extract corpus (extraction only)
python -X utf8 -B harness/make_mutations.py      # rebuild the 3 mutation files
python -X utf8 -B harness/verify.py              # RED -> GREEN -> mutations vs frozen oracle
```

Expected: `RED_FAILS_ORACLE_AS_REQUIRED`, `GREEN_MATCHES_ORACLE_EXACTLY (violations=4)`,
`MUT_A/B/C_PASS`, `OVERALL: PROTOCOL_SATISFIED`, rc 0.
NOTE: `build_corpus.py` re-reads the live plan files; if those changed since extraction,
corpus hashes will drift and `verify.py` will abort with the hash-guard error. To re-run the
proof against the FROZEN corpus, skip `build_corpus.py` (the corpus files on disk are the
frozen ones) and go straight to `verify.py`.

## Re-run the live scan (read-only; owners decide findings)

```
python -X utf8 -B tools/check_domain_assertions.py ..\..\..\task_plan.md ..\..\..\findings.md ..\..\..\progress.md
```

Expect rc 1 and 214 violations at extraction time of this attempt
(`evidence/live/summary.json`); counts drift as the plan files are edited by their owners.

## Evidence map (all raw, never rewritten)

- `evidence/build_corpus.stdout.txt` — corpus build log.
- `evidence/freeze_record.json` — freeze declaration.
- `evidence/red/` — RED arm: raw text+JSON stdout of the naive checker, `red_verdict.json`.
- `evidence/green/` — GREEN arm: raw text+JSON stdout, per-file JSONs, `green_verdict.json`.
- `evidence/mutations/` — per-mutation raw JSON + `mutation_verdicts.json`.
- `evidence/verify_summary.json` — one-object roll-up; `evidence/commands_run.json` — every
  subprocess argv/rc the harness ran.
- `evidence/live/` — live scan raw outputs, `findings_file_line_list.txt` (214 file:line),
  `summary.json`, oracle self-scan (0 violations).
- `evidence/utf8_normalize_report.json` — bookkeeping: six shell-redirected evidence files
  were written UTF-16 by PowerShell `>` and re-encoded to UTF-8; content unchanged.
- `evidence/final_hashes.json` — sha256 of every deliverable.

## Round 2 — after oracle CORRECTION 1 (parent-ordered)

CORRECTION 1 (appended to `oracle.md`, prefix-proven via
`evidence/oracle_correction1_ledger.json`: sha256(bytes[:13029]) still equals the frozen
round-1 sha) added domain patterns D8 (same-line numeral+classifier count) and D9
(subject/enumeration qualifier), and narrowed the EN marker boundaries at
alphanumeric/underscore adjacency (D10a). `oracle_table.json` was NOT changed.

```
python -X utf8 -B harness/verify.py round2       # RED + GREEN + 3 mutations under the correction
python -X utf8 -B harness/live_round2.py         # round-2 live scan + old/new diff with causes
python -X utf8 -B tools/check_domain_assertions.py oracle.md   # self-scan (expect 0, rc 0)
```

Expected: `evidence/round2/verify_summary.json` = PROTOCOL_SATISFIED; live scan
214 → 48 (task_plan 28 / findings 10 / progress 10), disappeared-by-cause
D8=136 / D9=5 / D10a=26, remained 47, new 1 (attributed to owner drift of
progress.md — see `evidence/live/round2_new1_attribution.md`; task_plan/findings are
byte-stable with new=0). Round-1 raw evidence under `evidence/red|green|mutations|live`
is preserved untouched; round-2 writes only under `evidence/round2/` +
`evidence/live/round2_*`.

NOTE: `progress.md` is owned by the parent and drifts between scans; a re-run of
`live_round2.py` later will diff against the round-1 JSON (frozen at 214) and the
disappeared/cause labels for progress.md are only as good as line stability.

## Round 3 — after oracle CORRECTION 2 (FINAL lexicon iteration; lexicon v2 frozen)

CORRECTION 2 (appended, prefix-proven via `evidence/oracle_correction2_ledger.json`:
sha256(bytes[:19324]) still equals the CORRECTION-1 state c8a6f209…) added D8b
(count/noun pairing incl. Chinese numerals + universal-bounded-NP + conditional 只有…时),
D10b (hyphen-compound / CLI-flag / `all(`/`all[` code-call marker skips — superseding the
§3 `record-only`-matches note), and D11 (quoted-line skip). `oracle_table.json` still
UNCHANGED. **No CORRECTION 3 — lexicon v2 is final.**

```
python -X utf8 -B harness/verify.py round3           # RED + GREEN + 3 mutations under v2
python -X utf8 -B harness/verify_correction2.py      # C2.3-declared quote-sample mini-GREEN
python -X utf8 -B harness/live_round3.py             # round-3 scan + full diff
python -X utf8 -B tools/check_domain_assertions.py oracle.md  # self-scan (expect 0, rc 0)
```

Expected: `evidence/round3/verify_summary.json` = PROTOCOL_SATISFIED;
`evidence/correction2/quote_samples_verdict.json` = C2_MINI_GREEN_PASS (flags [12,14]);
live scan 214 → 48 → **2** (`task_plan.md:1630`, `findings.md:633` — the residual handed
to the parent for item-by-item ruling; `new_vs_r1` = 0). Round-1 and round-2 raw evidence
stays untouched; round-3 writes only under `evidence/round3/`, `evidence/correction2/`,
`evidence/live/round3_*`.

## State / authority

`handoff.json` is `status=review_pending`; this attempt never signs a verdict,
never edits plan files, product, or other attempts, and makes no git writes.
The frozen lexicon is the contract — widen/narrow only via an appended labelled
CORRECTION in `oracle.md` (§11), never a silent edit.
