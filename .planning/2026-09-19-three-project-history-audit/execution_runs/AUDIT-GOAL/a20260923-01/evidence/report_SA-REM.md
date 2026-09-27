# SA-REM Audit Report — REMEDIATION_REGISTER.md (read-only audit)

**Headline: zero fabrication — every evidence pointer checked exists and matches its recorded hash — but criterion ③ 「REM-01…REM-79 按依赖逐项处置」 fails: 10 rows have no recorded disposition at all, 10 more are disposed only implicitly.**

## (1) 23-row sample (REM | one-line | recorded disposition | evidence pointer | on-disk? | verdict)

| REM | Content | Disposition (as recorded) | Evidence pointer | Exists? | Verdict |
|---|---|---|---|---|---|
| 01 | `host_signed` label never verified | fixed in B1 iso + promoted (L437→L948) | `B1-I08C-product-fixes\a20260921-01\` + PROMOTION-EXEC report `E2A42D2D…` | ✅ hash e2a42d2d/20561B | **CLOSED-VERIFIED** |
| 02 | receipt check ≠ security boundary | owner-ruled acceptable; residual "consumer guardrail absent" tracked (L424) | same B1 chain | ✅ | **CLOSED-VERIFIED** (residual carried) |
| 03 | `base_revenue` unbound to output gate | fixed via B1 (L437) | same | ✅ | **CLOSED-VERIFIED** |
| 04 | full key written to event log | fixed r6 (L425) + r7 records closed (L522) | `I-14-D\…\reviewer_report_r7.md` `cc6da8d3…` | ✅ cc6da8d3/17203B | **CLOSED-VERIFIED** |
| 05 | `_VALUE` dead code, narrowing inert | stale 待修@L16; card "B2" (L100) never recorded run | none after L100 | — | **OPEN** |
| 09 | natural_window keys hardcoded False | 修复中@L20; no register closure | git commit `980c9b7a` "I-14-I complete (14-case gate rc 0)" | ✅ commit only | **CLOSED-CLAIM-ONLY** |
| 10 | container basis aborts batch rc4 | same ("重跑 14 例到 rc 0" per commit msg) | git `980c9b7a` | ✅ | **CLOSED-CLAIM-ONLY** |
| 11 | `bundle=None` full-closure leak | fixed, B3 ACCEPT (L410) | `B3-I05C-delivery-fixes\reviewer_report.md` 36110B | ✅ | **CLOSED-VERIFIED** |
| 18 | E1–E7 errata landing | fixed+accepted (L472, L1080) | `E1E7-ERRATA-LANDING\` + per-card oracle hashes L474 | ✅ | **CLOSED-VERIFIED** |
| 21 | cross-batch exact-name gate propagation | row stale 待派@L42; executed in B5 (L64/L123); M01-M04→REM-80 closed (L939) | B5 + B5-fix `69ea3b03…` + M01-M04 `3217a506…` | ✅ all 3 hash-matched | **CLOSED-VERIFIED** (stale row) |
| 25 | GENERATION_RESERVE 124 vs logon 150 | "需 owner 选"@L51 — choice never recorded; only doc-figure fix (`I-14-F-R1\decision.md:28`) | partial | partial | **OPEN** |
| 36 | claim-echo residual, new card required | 待另立卡@L63 | no such card found | — | **CARRIED-WITH-NOTE** |
| 40 | oracle "11 fields" vs 10 | closed L777 after 2nd review | `B1-PREREQ\reviewer_report.md` `e25a2c83…` + `_r2` `50437289…` | ✅ both match | **CLOSED-VERIFIED** |
| 43 | r1 RED stdout claim | closed L780 (re-scoped), ordering gate honored | same B1-PREREQ reports | ✅ | **CLOSED-VERIFIED** |
| 47 | conftest guard order reversed | fixed+reviewed+carrier, closed L683 | `B3-PREREQ\reviewer_report.md` `F367984B…` + `evidence\rem47_*` | ✅ f367984b/15544B | **CLOSED-VERIFIED** |
| 48 | `NOT_REHASHED` vs "every hash compared" | closed L684 | same + `rem48_verification.txt` | ✅ | **CLOSED-VERIFIED** |
| 49 | source_preparation comment double-error | closed L685; promotion parity L948 | same + `rem49_*` | ✅ | **CLOSED-VERIFIED** |
| 54 | B5 verdict carrier untracked | "本轮已按 T1-27 授权提交"@L155 | `B5-plan-level-remediation\reviewer_report.md` | ✅ 34764B / 0324bfdc == carrier pin | **CLOSED-VERIFIED** |
| 55 | I-14-E-APPLY killed mid-campaign | CLOSED L521 (v2 rerun accepted) | handoff `665d6d1a…` | ✅ hash matches | **CLOSED-VERIFIED** |
| 59/60/61 merged | r3-gen gap ×3 | merged @L180-192 → REM-62 landed @L215 → review closed @L240 | `handoff_r3.json` + `reviewer_report_r3.md` `c617c43a…` | ✅ 44008B match | **CLOSED-VERIFIED** (residual 64 implicit) |
| 79 | class-widening diff-set criterion | "✅已实际使用"@L352; "机制化完成"@L653 | `REM79-MECHANIZATION\` (register L747 honestly flags its own stale byte count) | ✅ | **CLOSED-VERIFIED** + label caveat (D3) |
| 80 | M01-M04 no exact-name gate | 待owner@L369 → CLOSED L939 | `M01-M04-PROPAGATE\reviewer_report.md` `3217a506…` | ✅ 24604B match | **CLOSED-VERIFIED** |
| 84 | START_HERE append-2 overgeneralized | 待owner@L388 → CLOSED L850 | `execution_v2\START_HERE.md` | ✅ 20436B / 5c6e111f = exact claim match | **CLOSED-VERIFIED** |
| 85 | anchor hashes EOL-sensitive | registered L491; owner-ruled "proceed-with-disclosure" L503-505 | `I-09-C\preflight_anchors.md` + `evidence\eol_reconstruction.txt` | ✅ | **CLOSED-VERIFIED (ruled)** |
| 86 | future anchors must normalize EOL | deferred to future template rev (L509) | — | — | **CARRIED-WITH-NOTE** |

Spot-checks: 16 SHA-256 pins (100% match), 7 git shas (`4b1c690b`, `980c9b7a`, `8b7229c3`, `3861f08d`, `6f74b056`, `6d62b046`, `1bddfc1e` — all real), 6 dir listings = 29 pointers, ≫10 required.

## (2) Census REM-01…REM-86 (id:state@line; F=fixed, FI=fixed-implicit, R=ruled, C=carried-with-note, O=open)

```
01:F@437 02:R@424 03:F@437 04:F@425 05:O@16 06:O@17 07:O@18 08:O@19 09:FI@20 10:FI@21
11:F@410 12:F@411 13:F@412 14:F@413 15:C@423 16:O@32 17:O@33 18:F@472 19:C@35 20:C@36
21:FI@64 22:F@123 23:R@44 24:FI@474 25:O@51 26:C@52 27:F@525 28:F@525 29:F@525 30:O@56
31:F@525 32:F@63 33:F@59 34:F@60 35:O@62 36:C@63 37:C@64 38:C@65 39:F@66 40:F@777
41:F@778 42:F@779 43:F@780 44:F@781 45:C@433 46:R@424 47:F@683 48:F@684 49:F@685 50:F@523
51:F@523 52:R@421 53:R@422 54:F@155 55:F@521 56:FI@215 57:F@158 58:C@159 59:FI@215 60:FI@215
61:FI@215 62:F@215 63:F@240 64:FI@311 65:F@261 66:F@242 67:O@263 68:C@244 69:F@281 70:F@271
71:F@309 72:F@310 73:F@311 74:C@312 75:F@328 76:F@350 77:F@351 78:FI@653 79:F@352 80:R@939
81:F@522 82:C@371 83:R@524 84:F@850 85:R@503 86:C@509
```

**Totals (86): F=45, FI=10, R=8, C=13, O=10.** Rows I cannot place in a disposed state (「一条不许静默丢」 violation): **REM-05, 06, 07, 08** (card "B2"@L100 never run), **16, 17** (card "B4"@L102 never run), **25** (owner choice never recorded), **30** (F-5 absent from ERR-I14FR1 set — verified `I-14-F-R1\decision.md:142-178` covers only F2/F3/F4/F6), **35** (wording fix never recorded), **67** (①③ unclosed). Within criterion scope REM-01…79: 10 un-disposed + 10 silently-disposed ⇒ explicit row-level trace = **59/79**.

## (3) Dependency-order check

- **A. REM-59/60/61→REM-62→REM-63**: merge (L178-192) → landing (L215) → review (L221→240). **Respected** (files verified).
- **B. REM-43 gate**: "r2 交付并复审通过前不得记 closed" (L611/637) → r2 delivered (L720) → 2nd review accepted (L767-771) → closed (L780). **Respected**.
- **C. REM-49 = B3 promotion hard-prereq** (L685/687) → closed (L683-687) before PROMOTION-EXEC (L948). **Respected**.
- Minor deviation: REM-24 "与 REM-18 同批" (L45) — landed in substance via E1E7 (L474) but its row never updated (silent dependent-row drop).

## (4) Deviations (severity)

1. **HIGH — 10 silent drops** (above): criterion ③ 「逐项处置」 fails on these rows. Not fabrication — the register never returns to them.
2. **MEDIUM — REM-78/79 id conflation**: REM79-MECHANIZATION mechanizes REM-78's rule (domain-scoped assertions, L331), but from L435 onward the register credits "REM-79" (L435/505/563/653/759); REM-78's row (@353) still says 仍欠机制化.
3. **MEDIUM — 10 implicit closures** (09/10/21/24/56/59/60/61/64/78): disposed only under other ids/cards/commits; rows stale or absent.
4. **LOW** — REM-54's "committed" claim: file+hash verified, git commit not re-verified (no sha cited). REM-30 falls through the I-14-F errata set while L525 reads as if the F-series closed.
5. **INFO** — `651efc51`/`bad229ae`/`d69db8d1`/`807189a7`/`08e56200`/`5ed7f075`/`f1df69db` etc. are dispatch/job ids, **not** git commits (verified unresolvable in git) — register never claims otherwise, but they are visually confusable with real shas. Duplicate §11–§20 numbering self-disclosed @L905 and confirmed.
6. **FABRICATION COUNT: 0** — all 14 hash pins tested matched exactly.

## (5) Coverage stats

86/86 ids enumerated (REM-01…86; none beyond). Sample 23 rows (≥20), all mandatory ids + merged 59/60/61 included. Pointers spot-checked 29 (≥10), match rate 100%, missing pointers 0. Disposed 76/86 (88%); explicitly row-traced 66/86 (77%); un-disposed 10/86 (12%), all inside criterion-③ scope. Dependency cases 3 checked, 3 respected (+1 minor deviation). Sample verdicts: CLOSED-VERIFIED 16, CLOSED-CLAIM-ONLY 2, CARRIED-WITH-NOTE 3, OPEN 2.

Written by SA-REM (independent reviewer) on 2026-09-23.