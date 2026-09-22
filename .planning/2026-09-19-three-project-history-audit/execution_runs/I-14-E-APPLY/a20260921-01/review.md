# review.md — card `I-14-E-APPLY` (attempt `a20260921-01`) — carrier landing verdict block

> Nature of this block: **bookkeeping transcription, adds no acceptance of its own.** The implementer never signed and does not sign here; the verdict is transcribed verbatim from the independent reviewer's carrier. No production writes; no self-signing.

## Verdict block

- **verdict** = `accepted_scoped`
- **Q1** = `option (ii)`（§5 blocked 触发在实体上不成立，依据 = 冻结的 addendum-C C7.2 预注册了两形态区分；反自我豁免由范围语句保住）
- **carrier** = `reviewer_report.md` — sha256 `feaec562df3ff9a33516885c69c546a0b08d4660bcc877b349e76535c3a16ce7`, size 21411 B; pin file `reviewer_report.md.sha256` (`feaec562…  reviewer_report.md`) recomputed and verified equal at landing time.
- **carrier line ranges**: verdict declaration = line 4; Q1 ruling = §1.2 lines 16–24; **scope language = §1.3 lines 26–35 (quote block 28–35)**; verdict summary footer = line 76.
- **reviewer** = 独立复核 (independent sibling of the implementer; the implementer did not self-sign; the reviewer did not flip status — that move belongs to parent/owner).
- **authority**: `verdict_is_transcribed_not_authored: true`. `handoff.json.status` moves `review_pending → accepted_scoped` strictly as bookkeeping, per carrier §1.3 point 6 ("only by the parent/owner, never by the implementer").

## Scope language — copied VERBATIM from carrier §1.3, lines 28–35 (condition of acceptance)

> **ACCEPTED WITH SCOPE — I-14-E-APPLY a20260921-01 (reviewer ruling on Q1 = option (ii))**
> 1. **R1′/R2′ accepted at 6/6** (shrunk from 8/8 by owner §16 E-2 + addendum C1/C7.4, pre-declared). The frozen 8/8 is **UNTESTED** and must never be cited as met.
> 2. **R3 (non-vacuity) accepted on**: quiet pytest-level 2/2 PASS **plus** event-level checks (a)(b)(c) 4/4 — 2 `session_start_timeout` kills per run, uptimes within [3.9, 5.0], `child_started == 3` — independently re-derived by the reviewer from `campaign_v2.jsonl` and the retained capture event files. **R3 is NOT green at pytest level under cpu8**: those 2 runs are budget-REDs at the node's frozen outer `timeout=15` with assertions never executed; **pytest-level R3 under load remains UNVERIFIED**.
> 3. **§5/C1/C7.2's blocked-trigger is adjudicated NOT engaged on the merits** for this campaign, on the pre-registered C7.2 distinction (budget-RED vs vacuity-RED) and the 4/4 event proof. This ruling is **card-specific and does not amend oracle §5**: any future non-vacuity RED with the watchdog not firing (vacuity-RED) is **automatically blocked, no adjudication**; any future budget-RED likewise requires full events disclosure and reviewer adjudication; **implementer self-exemption remains forbidden in all cases**.
> 4. **No authorization is created** for raising the node's outer `timeout=15` or any other test-side timing change beyond the applied derivation fix. `timeout=15`, `child_poll_milliseconds=100`, `child_started == 2` stay frozen; such a change requires a separate owner decision and a new oracle addendum (§13 T1-7 / follow-up card).
> 5. **R4′ accepted as 0/6 passed** (5 pytest-RED + 1 guard-timeout; reported unrounded), mutation active in 6/6 runs.
> 6. **Production stays read-only; promotion remains a separate owner decision.** `handoff.json.status` may move `review_pending → accepted_scoped` only by the parent/owner, never by the implementer.
> 7. Qualification: this acceptance covers this attempt's evidence at the domains stated in the reviewer report; anything beyond them is unverified.

## Carried findings register (append-only; mirrored in `evidence/I-14-E-APPLY/qualification.json`)

1. **R3 load-level UNVERIFIED**: `accepted_scoped` covers quiet 2/2 + event-level (a)(b)(c) 4/4; R3 is **NOT green at pytest level under cpu8** — any future claim of that requires owner + a new addendum raising the §2.3-frozen outer `timeout=15` and a re-run (this acceptance creates NO such authorization).
2. **R1′/R2′ = 6/6 shrunk** (owner-authorized shrink, pre-declared); **8/8 untested** = open owner-callable gap (Q2, not blocking).
3. **R4′ = 0/6 unrounded** (5 failed + 1 guard-timeout; 4 of 5 REDs are TimeoutExpired@15, only run6 AssertionError — disclosed).
4. **Reviewer LOW finding**: `EXIT=3221225786` lives in `bench.log:31`, NOT in `arm-logs/B5-clockmut-cpu8.log` — addendum C0 + handoff `campaign_v1_history.evidence[2]` misattribute the file; substance intact (v1 died STATUS_CONTROL_C_EXIT mid-B5, B4 never ran).
5. **Convention deviation**: no commands.json/binding.json (argv preserved per-run in JSONL); addendum declared record-time 07:31:56Z vs mtime 07:49:16Z (both pre-run, disclosed).
6. **Source card I-14-E is NOT accepted on record** (its review.md conclusion unfilled, status `review_pending`) — authorization rests on §13 T1-7 + §16 E-2 verbatim; do not cite it as an "accepted carrier".
7. **Q3 accepted as disclosed-with-evidence**; foreign-burner origin unattributed (campaign-era orphans ruled out by 300s expiry).

---

*Transcription only: verdict, Q1 ruling, and scope language above are the carrier's, not this file's. Status transition recorded in `handoff.json` (`status_authority` + `bookkeeping`); formula state in `evidence/I-14-E-APPLY/qualification.json`.*
