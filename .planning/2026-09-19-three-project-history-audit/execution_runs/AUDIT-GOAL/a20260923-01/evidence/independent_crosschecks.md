# Evidence: AUDIT-GOAL lead's own independent cross-checks (2026-09-23)

These are measurements the lead auditor re-ran personally (PowerShell `Get-FileHash`,
`git cat-file`, file reads) to cross-check the delegated reviewers' highest-severity
claims before accepting them. Read-only throughout.

## 1. Criterion ① pin sweep — all 8 in-flight cards (re-computed SHA-256 vs sidecar pins)

| card/attempt | reviewer report recomputed sha256 (head) | sidecar pin | match |
|---|---|---|---|
| GATE-TIMEOUT-1200\a20260922-01 | 2a66abae6f04… | same | True |
| DW15-prune-repair\a20260922-01 | a9b9076f731b… | same | True |
| B5-fix-g1a-g3\a20260922-01 | 69ea3b033d22… | same | True |
| I-08-C\a20260919-01 (report_r2) | ee5046a5bafb… | same | True |
| I-14-F-R1\a20260922-01 | 8ce87ef6d310… | rich sidecar `sha256: 8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c` | True |
| INVEST-CORE-ATTEST-GATE\a20260922-01 | 09b4e13ec1bd… | same | True |
| I-14-E-APPLY\a20260921-01 | feaec562df3f… | same | True |
| I-14-D\a20260919-01 (report_r7) | cc6da8d3878d… | same | True |

## 2. I-14-D append-only byte-prefix proofs (re-computed by the lead)

- `review.md` first 26172 B → `163cb939a11da0f245823ad24bb3ad1949890c02afced41ea53308343a58f373` = claimed post-r7 pin (MATCH)
- `review.md` first 22100 B → `8a2ff101b5501a9de93651ff1988fab339d76af779982cbe1c398b734fc28ae7` = claimed r6 pin (MATCH)
- `reviewer_report.md` (r1) recomputed `499d91acf06a…` = quoted in review.md L10 (MATCH)
- `handoff_r6.json` status_authority carrier = `reviewer_report_r7.md`, sha `cc6da8d3…` (MATCH), status=accepted_scoped (transcribed, verdict_is_transcribed_not_authored=true)

## 3. Batch-boundary commit existence (SA-PUSH claim cross-check)

`git cat-file -t` = commit for all 10 spot-checked boundary shas: ab20cebe, 6f74b056,
3861f08d, 4b1c690b, 865428f8, b0d016a6, 262659e4, a31fd7ed, 977fa1e8, b7a6a116.
`git rev-parse HEAD origin/main` at audit time = b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb (ahead=0).

## 4. FABRICATION-SUSPECT class — claim-vs-disk (highest severity per audit charter)

Independently re-hashed the three T2 ruling.md files vs the pins recorded at
`outward_requests\RESPONSES.md:5-7`:

| ruling file | RESPONSES.md claims | disk recomputed | match |
|---|---|---|---|
| T2-SIM-OPEN4-WIKI\a20260922-01\ruling.md | 37413f78… | 37413f7812bbe4aa… | True |
| T2-SIM-OPEN5-RF\a20260922-01\ruling.md | 74f5c835… | 74f5c83598355bd4… | True |
| T2-SIM-OPEN6-SEC\a20260922-01\ruling.md | 8aabac09… | **5cb476767a934885…** | **False — CONFIRMED stale/false pin** |

Also confirmed: `execution_runs\OUTWARD-LETTERS-UPDATE\` (named at OWNER_DECISIONS.md:427
as dispatched) **absent on disk** (exists=False); the letter-update work itself exists in
`outward_requests\` (3 appended update sections + `_provenance.json` prefix proofs —
verified present by SA-CHAIN). `execution_runs\DW15-REPAIR\` absent while
`DW15-prune-repair\` exists (rename, no substance loss).

## 5. SA-REM silent-drop rows confirmed at source

Register L100: `| **B2** | REM-05/06/07/08 | I-14-D 残项修复卡（…）|` — repair card "B2"
was registered as the routing target; no execution record for a "B2" card exists.
Register L263: `REM-67 之①/③ … **未处理**（不在 r4 范围…F-REV-R3-03 的正式更正未做）`.
REM-25 L51 = "待修（需 owner 选）" — owner choice never recorded. REM-30 L56 = "待修".

## 6. Inter-reviewer contradiction adjudicated (REM-62)

SA-DEFECT scored REM-62 as OPEN ("r3 carrier never written"); SA-REM scored it F@215.
Lead re-read the register: L198 registered the gap (待收口), L209/L215 record
「Round 70：REM-62 **已落地**」 with `handoff_r3.json` added and four carriers appended
(prefix-preserved). Independent file check: `I-14-D\a20260919-01\handoff_r3.json` EXISTS.
ADJUDICATION: REM-62 = CLOSED (landed 2026-09-22); SA-DEFECT's row reflects the L198
snapshot only.

## 7. I-06-B gate-break-suspect (SA-GATE-DEP D2) confirmed at source

`I-06-B\a20260919-01\handoff.json`: status=accepted_scoped while its own blocked_by[]
reads 「I-06-A blocked (D-W06 unsigned) — persistent demand store and original-request
resume CLI unavailable」「D-W06 OPEN-1..OPEN-6 unsigned …」. Confirmed verbatim.

## 8. 92-card census (lead's own script, per-card best status across attempts)

- accepted_scoped: 72 (73 if I-14-D's r7 acceptance carrier handoff_r6.json is counted;
  the top-level handoff.json stays historical review_pending by append-only design)
- review_pending: 4 (I-00-A, I-08-A, I-14-D, I-14-E)
- not started (no attempt dir at all): 16 (I-07-E, I-10-A, I-11-B/C, I-12-A..E,
  I-13-A..C, I-16-A/B, I-17-A/B)
- total dispatch cards: 92 (matches dispatch.md's own 「总计92张执行卡」)
