# SA-CHAIN Independent Audit Report — D1–D7 Goal-vs-Reality Traceability

Scope: 2026-09-19-three-project-history-audit PLAN. Baseline B = owner directive chain D1–D7. All paths relative to PLAN = `.planning/2026-09-19-three-project-history-audit`. Hashes independently re-computed read-only (Get-FileHash SHA-256). Method: grep/read only; no tests run; no network.

## 1. Directive Table (D1–D7)

| # | Verbatim quote + recorded at | Execution landing points | Verdict |
|---|---|---|---|
| D1 | 「A-1: 1, A-2: 授权, B: 全批， C:更新函件」 `OWNER_DECISIONS.md:420` (§18, execution map :422-428) | A-1=①扩权 → `execution_runs/M01-M04-PROPAGATE/a20260922-01/` (handoff.json:4 status=accepted_scoped; arms E=0/F=3/G=2/S=1/B=0 ×4, 20 fresh runs, 7722-file historical manifest zero drift — handoff.json:30-31,72). A-2=授权 → `execution_v2/START_HERE.md:228-241` ("rc 码表·勘误 append-3 (REM-84; owner 授权 2026-09-22「A-2: 授权」)"; prefix 18452 B / `a9cb5a4a…` claimed re-verified at :231). B=全批 → `PROMOTION-EXEC/a20260922-01` (accepted_scoped; 10/11 promoted files landed byte-exact; **B-6c STOPPED+REVERTED** after proven 59-pass→31-fail regression, handoff.json:100,109 — disclosed deviation, re-landed later via `MODEL-ORACLE-ALIGN` (dir present) per REMEDIATION_REGISTER.md §44:1073) + `PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md` (exists) + `GATE-OQ-FIX/a20260922-01` (accepted_scoped; OQ-01 real-data 1200→1800 that step only, OQ-02 f2 120→300; load-side GREEN explicitly owed to batch-4 push — U-1/U-2 honest non-claims, handoff.json:143-156). B-6a maintained non-promotion and B-5 prune-EXECUTION unsigned per E-4 — both disclosed. C=更新函件 → all three letters carry appended 「更新（2026-09-22，追加式更新段）」 (`outward_requests/A_DW06_OPEN-4-5-6.md:169`, `B_signature_trust_domain.md:224`, `C_I-05-C_gap2_gap3.md:164`) + `outward_requests/_provenance.json` `updates_2026_09_22` (prefix proofs) + `README.md:47`. **BUT the named card dir `execution_runs/OUTWARD-LETTERS-UPDATE/` (「已派 ea7ecf69」, OWNER_DECISIONS.md:427) does NOT exist on disk** — see Finding F2. | EXECUTED-WITH-DISCLOSURE |
| D2 | 「fail 的全部要修复」 `REMEDIATION_REGISTER.md:981` (§39) verbatim; also `FIX-W06-GAPS/a20260922-01/binding.json:4`, `decision.md:3`, `oracle.md:4` | `OPEN5-DOUBT-PROBE/a20260922-01` probes P1–P6 (evidence 01–06 on disk, hashes at REMEDIATION_REGISTER.md:1032) → `FIX-W06-GAPS/a20260922-01` repair surface (12 组修面终表 :1032; handoff.json:4 accepted_scoped, verdict "ACCEPT (scoped), F1–F7"; mutations 12/12 RED retained). P1 migration FAIL → 真 additive migrator etc. | FULLY-EXECUTED (disclosed supersession: P5-b first registered BLOCKED-on-external at §40:1015, upgraded to fail-closed real fix by D4 at §41:1027 — additive register trail) |
| D3 | 「全部接受」 `OWNER_DECISIONS.md:435` (§19 终确) + TTL=A 30天 `:439` (「TTL 定值 = 选项 A：30 天（86400×30）为 policy 上限…调用方 now/ttl 只可收紧」) | (i) three T2 rulings activated — `outward_requests/RESPONSES.md:3-7` (3 rows, explicitly labelled owner-ratified role-played, 非外部方真实签署 — correct disclosure), I-06-A first blocker released → 19-card chain (REMEDIATION §43:1062-1067; progress.md:1107); (ii) TTL → `execution_runs/TTL-30D-POLICY/a20260922-01/` (POLICY_RECEIPT_TTL_CAP_SECONDS=86400×30=2592000; RED 9-gating→GREEN 16/16; 2 one-hunk mutants redden exactly frozen sets; reviewer independently re-ran; accepted_scoped) | EXECUTED-WITH-DISCLOSURE (TTL fix landed in **iso only, zero production writes** — live CW guard has NEITHER TTL implementation (TTL handoff U-3/U-4) ⇒ 「落产品策略」= reviewed changes.diff awaiting promotion; cap not in RULESET_HASH payload (U-2, declarative contract + ops discipline) — F3) |
| D4 | 「发现的缺陷都要全部修复」 `REMEDIATION_REGISTER.md:1025` (§41) verbatim + `FIX-W06-GAPS binding.json:4` | Registration + routing verified (full defect ledger covered by the other reviewer per brief): 修面终表 12 组 routed to FIX-W06-GAPS (:1032); P5-b upgraded 暂缓→真修 fail-closed 处置闸 (:1027); P5-a record-side re-scan (:1028); P4-SCOPE single-source convergence (:1029); honest boundary (P3 resume/complete = 接口未建, 非缺陷, :1030). FIX-W06-GAPS accepted_scoped. Residuals openly carried (handoff RF-B/RF-6 external ride letter-B trust root; RF-P6A ruling-track) | EXECUTED-WITH-DISCLOSURE (registered + routed + landed; ledger completeness = other reviewer's scope) |
| D5 | 「所有存疑都要确认」 verbatim in `FIX-W06-GAPS/a20260922-01/binding.json:4` + `decision.md:3` + `oracle.md:4` (NOT as a register 「原话」 line — F5). Closure account: `REMEDIATION_REGISTER.md:1036-1058` (§42; §42.4: 已确认关闭 17 + 随修复自动关 3 + 待你 2, 「OPEN-4#7 与 TTL 同票」, 零无主) → sealed §43:1064 (「22 条存疑终态表封存（19 关闭确认+3 随修复关）」) + `progress.md:1108` (19+3+0) | Enumeration basis = the three T2-SIM rulings' numbered doubt lists: OPEN-4#1–#8 (`T2-SIM-OPEN4-WIKI/ruling.md:169-178`「8 条逐字保留」), OPEN-5存疑1–#6 (`T2-SIM-OPEN5-RF/ruling.md:272-273,285-309`), OPEN-6#1–#8 (`T2-SIM-OPEN6-SEC/ruling.md:212-223`) = 22. Doubt machinery = `OPEN5-DOUBT-PROBE` (probes answered 存疑 1/2 + 5/6) + `T2-SIM-OPEN*` 追加解析态 sections. ARITHMETIC CHECKS: 17+3+2=22 ✓ and, the 2 owner-pending items (#1 终确 and TTL/#7) closed by 「全部接受」, 19+3+0=22 ✓ | FULLY-EXECUTED (with the classification nuance of F7) |
| D6 | E2E 四约束 verbatim 「各种可能情形都尽量覆盖，主要步骤都尽量加上，要用真实数据，测试要自建独立环境和数据，测试完数据要恢复…用小规模数据测试，不要大张旗鼓」 registered at `execution_runs/E2E-EXPAND/a20260923-01/oracle.md:5` ("Owner constraints (verbatim, card line 1)") | (a) scenario coverage + (b) main steps → cross-repo full-chain suite E2E-EXPAND (scenarios S1 download / S4 cleanup etc.; `RF-E2E-ADAPT/a20260923-01` root-cause fix accepted, gate selection 55 GREEN per REMEDIATION §53/§57:1271; §57 records 复审自跑 pytest rc0, runner exit0). (c) real data → `reviewer_report.md:110` "REAL data — VERIFIED" (CW real bytes/live hash match; `changes.diff:935` "owner: 要用真实数据") + live real-download retest (D7). (d) isolated env + post-test restore → `reviewer_report.md:137` VERIFIED (drift-exit2 实证, 14/14 pins, snapshot content keys 7/7, production DB stat-only; deletion proof inventory15/deleted2/post_absent×2). (e) small scale / not heavy → `reviewer_report.md:175,195` VERIFIED (时标重导 1×2 ≤50 MB; +11 allowlist literals verbatim in runner, 3-file diff, zero workflow refs, quality.yml untouched). Central reviewer ruling KEEP-THE-RED on frozen `downloads==1` oracle (假零=品缺) → F-EE1-FIX defect card → live retest pass (disclosed, correct per contract) | FULLY-EXECUTED |
| D7 | 「给你真实下载复测授权」 `REMEDIATION_REGISTER.md:1368` (§65) → 「同意」 `:1378-1380` (§66「我呈批清单第 1 项三动作，owner 一字『同意』」). The question clause「还需要什么要我批准的吗？」is NOT on disk (F5) | (i) real-download retest EXECUTED — §65:1369-1371: round 1 transient skip (honestly recorded), round 2 S1=pass (`s1.downloads=True`, `envelope_download_events=1`, deletion evidence `post_absent=True`, 134.87s); evidence `execution_runs/E2E-EXPAND/a20260923-01/evidence/live_retest_20260923/` + `live_retest2_pass_20260923/` — both exist on disk; the "18 件" claim counted 18 files ✓. F-EE1 真实下载面 = VERIFIED-PASS. (ii) Three outbound actions ①push CW (`git push origin fcap:master`) ②change `compatibility/current.json` wiki pin + FC-1101 local green ③push RF (:1381-1383) = PENDING-ROUTED: explicit execution sequence at :1384 with in-flight cards CW-GATE-UNBLOCK / RF-RATCHET-FIX / RF-STEP9-TRIAGE (§67–§69, still 在飞 as of :1422); `F-EE1-FIX/a20260923-01` and `CFI14FR1-SAMPLE/a20260922-01` attempt dirs exist. External/network steps explicitly routed ⇒ acceptable per brief | retest: EXECUTED-WITH-DISCLOSURE (round-1 transient disclosed) + three outbound actions: PENDING-ROUTED |

## 2. 22-Doubt Closure Table

22 = OPEN-4#1–#8 (`T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md:169-178`) + OPEN-5存疑1–#6 (`T2-SIM-OPEN5-RF/a20260922-01/ruling.md:272-273,285-309`) + OPEN-6#1–#8 (`T2-SIM-OPEN6-SEC/a20260922-01/ruling.md:212-223`).

| id | doubt | answer source | closure state |
|---|---|---|---|
| OPEN-4#1 | 模拟裁定待 owner 终确 (ruling.md:171) | OWNER_DECISIONS.md:435-438 | CLOSED (spot-check ①) |
| OPEN-4#2 | 函B 未逐字通读恐有相反裁定 | ruling.md:189 全扫无矛盾 | CLOSED |
| OPEN-4#3 | 并发写回执交错未验证 (I-06-A handoff:147) | OPEN5-DOUBT-PROBE report.md:49 (P6) + ruling.md:190 | CLOSED-w-followup (P6-A/B landed in FIX; RF-P6A ruling-track residual carried) |
| OPEN-4#4 | 阻断文案跨仓断言未排查 (handoff:146) | P4 9-row sweep `evidence/04_blocked_message_sweep.md` + ruling.md:191 | CLOSED-w-followup (P4-SCOPE pinning) |
| OPEN-4#5 | RF 侧源码未读 | ruling.md:192 blob 链实证 | CLOSED |
| OPEN-4#6 | harness 代码未逐行审 | ruling.md:193 (618 行逐行) | CLOSED |
| OPEN-4#7 | TTL 数值/过期策略未审 | OWNER_DECISIONS.md:439 TTL=A → TTL-30D-POLICY | CLOSED (spot-check ③) |
| OPEN-4#8 | detected_and_ignored 下游语义 | OPEN-6 ruling C-set + ruling.md:195 | CLOSED |
| OPEN-5#1 | 候选 additive migration / 并发 claim / lease 过期未验证 | OPEN5-DOUBT-PROBE report.md:57 RESOLVED-YES (P1→FAIL→FIX-W06-GAPS ①) | CLOSED-w-fix (spot-check ②) |
| OPEN-5#2 | 阻断文案跨仓文本断言未排查 / C8 钉住 | report.md:61 + 04_blocked_message_sweep.md | CLOSED-w-followup (C8 钉住 = P4-SCOPE 落定自动关, §42.2) (spot-check ④) |
| OPEN-5#3 | 父并行实证项 (title text not read verbatim) | REMEDIATION §39:1000 终格「已解除」 | CLOSED |
| OPEN-5#4 | 父并行实证项 (title text not read verbatim) | REMEDIATION §39:1000 终格「已解除」 | CLOSED |
| OPEN-5#5 | 父并行实证项 (title text not read verbatim) | REMEDIATION §39:1000 终格「已解除」 | CLOSED |
| OPEN-5#6 | 两方裁定反压耦合风险 | ruling.md:454 终格「已解除、零反压」 | CLOSED |
| OPEN-6#1 | 产品源字节未直读 | ruling.md:214 | CLOSED |
| OPEN-6#2 | now/ttl 调用方供给面 (C6) | ruling.md:215 → TTL-30D-POLICY | CLOSED |
| OPEN-6#3 | 假回执格式合法哈希面 | P5 CONFIRMED 3/3, ruling.md:216 → P5-a/b/c 修复 | CLOSED |
| OPEN-6#4 | 并发写回执原子性 | ruling.md:217 → P6-A/B | CLOSED-w-followup (§42.2 自动关) |
| OPEN-6#5 | 术语碰撞 ignored vs detected_and_ignored | ruling.md:218 | CLOSED |
| OPEN-6#6 | 阻断文案未排查（钉住留置） | ruling.md:219 → P4-SCOPE | CLOSED |
| OPEN-6#7 | I-05-B 消费面入口未读 | §42.1.2 确认缺席 by-design (handoff L240「不得假装存在」) | CLOSED (spot-check ⑤) |
| OPEN-6#8 | role_set 可篡改面 RF_W06_ROLE_SET | §42.1.3 确认前瞻 (grep 双证零引用) | CLOSED (spot-check ⑥) |

Totals per account: 19 CLOSED + 3 CLOSED-w-followup-fix (OPEN-6#4, OPEN-5#2 残余, C7 消歧) + 0 ownerless = 22 ✓; every item has an owner/answer party (T2-1/T2-2/T2-3 owners or owner vote) — "零无主" holds for all items checked.

### Spot-check chains (doubt text → answer → execution)

① OPEN-4#1: ruling.md:3,171 (性质声明「待 owner 终确；非外部方真实签署」) → OWNER_DECISIONS.md:435-438 (终确=关闭条件) → RESPONSES.md:3-7 登记 + REMEDIATION §43:1064. ✔
② OPEN-5#1: I-06-A handoff.json:147 (quoted OPEN5-DOUBT-PROBE oracle-lite.md:8) → report.md:57 RESOLVED-YES (three behaviors tested) → P1 FAIL upgraded at REMEDIATION §39:989-996 → FIX-W06-GAPS changes.diff ①真 additive migrator (accepted_scoped). ✔
③ OPEN-4#7: ruling.md:177,194 「数值不属本裁定」 → OWNER_DECISIONS.md:439 (TTL=A) → TTL-30D-POLICY binding.json:8-16 + decision.md RED/GREEN table (TTL-N1/N2/N3 exact message `ttl_seconds exceeds policy cap of 2592000s`; 2 one-hunk mutants). ✔
④ OPEN-5#2: handoff.json:146 → report.md:61 + evidence/04_blocked_message_sweep.md (9 rows, PINNED×2/UNPINNED×5/ABSENT×2) → FIX-W06-GAPS P4-SCOPE pinning (tests/test_fc905b + test_message_contract_pins; accepted F1–F7). ✔
⑤ OPEN-6#7: ruling.md:203,220 → §42.1.2 (probe+grep 双证 no consume/resume CLI) → closure = correct absence, C4 instantiated as future I-06-B work (no fabrication of an interface). ✔
⑥ OPEN-6#8: ruling.md:221 → §42.1.3 (RF+CW grep 双证零引用) → forward constraint C5 binding (I-06-B future). ✔

## 3. Findings (severity)

- **F1 HIGH — INTEGRATION/PIN MISMATCH, FABRICATION-SUSPECT CLASS (claim-vs-named-file)**: `outward_requests/RESPONSES.md:7` records sha256 `8aabac09…` for `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md`, but the file on disk re-hashes to `5CB476767A934885F48EB40FCCCAC0515243471A7FC6F0AA0B66680BEA99CF15`. The other two pins match (OPEN-4 `37413F78…` ✓, OPEN-5 `74F5C835…` ✓). Mitigation: ruling.md carries dated appended re-verification sections (§7-补 etc.) and FIX-W06-GAPS F7 records it as a modified plan-space file attributed to "T2-SIM ruling files by their owners" ⇒ most likely a stale pin after authorized appends, NOT invented evidence — but as written the register line is now false against disk and must be re-pinned or annotated append-style. This is the only claim-vs-file mismatch found.
- **F2 MEDIUM — NAMED EVIDENCE DIR ABSENT**: `execution_runs/OUTWARD-LETTERS-UPDATE/` claimed dispatched at OWNER_DECISIONS.md:427 (「更新卡 `OUTWARD-LETTERS-UPDATE` 已派（ea7ecf69）」) does not exist (whole execution_runs scan). The letter-update work itself is verified on disk (3 appended update sections + `_provenance.json` prefix proofs), so this is an evidence-pointer/bookkeeping defect for D1-C, not proof of non-execution.
- **F3 MEDIUM — D3 TTL scope over-reading risk**: TTL fix is iso-only (TTL handoff U-3: live CW guard has neither REJECT nor CLIP implementation; CLIP-vs-REJECT divergence with I-06-A iso `cf9174b5…` awaits parent normalization). 「落产品策略」 must not be read as in-production.
- **F4 LOW**: `DW15-REPAIR` named at OWNER_DECISIONS.md:357 absent; the existing dir is `DW15-prune-repair` (per §16:369). Apparent rename; recommend annotation.
- **F5 LOW — Verbatim-quote registration gaps**: D5 quote exists only in card carriers (`FIX-W06-GAPS binding.json:4`/`decision.md:3`/`oracle.md:4`), not as a register 「原话」 line (§39/§41/§42 titles paraphrase); D7's question clause「还需要什么要我批准的吗？」absent from disk (only the authorization clause at §65:1368 and「同意」at §66:1380).
- **F6 LOW — Cross-ref numbering ambiguity**: §42.3 calls the TTL-numbers doubt "OPEN-4#7/OPEN-6#6", but the OPEN-6 ruling's row #6 is the blocked-message sweep (ruling.md:219) and the now/ttl row is #2 (:215) — the same cross-carrier citation-slip family the register itself logged at §40:1008.
- **F7 LOW — 22-account partition nuance**: §42.2's third auto-close item (C7 同词异义消歧) is a 边界补充记 item, not verifiably one of the 22 numbered IDs; arithmetic 19+3+0=22 is preserved but one cell of the partition is loose.
- **F8 INFO**: M01-M04-PROPAGATE handoff.json:179 — REM-80 register-row closure + formal 31/31 追认 still owed to parent (work itself accepted_scoped).

No other fabrication suspects: every other named evidence pointer checked exists (`promotion_batch_manifest.md` ✓, TTL/OPEN5/T2-SIM/F-EE1-FIX/CFI14FR1-SAMPLE/RF-E2E-ADAPT/FIX-W06-GAPS/GATE-OQ-FIX/M01-M04-PROPAGATE attempt dirs ✓, `live_retest*` dirs ✓ 18 files).

## 4. Coverage Stats

- Directives traced 7/7; verbatim quotes located 7/7 (D5 only in card carriers; D7 half-quote missing — F5).
- Named attempt/evidence pointers checked 13: present 12, absent 1 (OUTWARD-LETTERS-UPDATE — F2; +DW15-REPAIR rename note F4).
- SHA-256 pins independently re-hashed 3: match 2, mismatch 1 (F1).
- Doubt items: 22/22 enumerated (OPEN-4#1-8, OPEN-5#1-6, OPEN-6#1-8), end-to-end spot-checked 6 (≥5 required); arithmetic 17+3+2 → 19+3+0 = 22 both check; ownerless 0.
- Completeness verdicts: D1 EXECUTED-WITH-DISCLOSURE; D2 FULLY-EXECUTED; D3 EXECUTED-WITH-DISCLOSURE; D4 EXECUTED-WITH-DISCLOSURE (registered+routed; ledger = other reviewer); D5 FULLY-EXECUTED; D6 FULLY-EXECUTED; D7 EXECUTED-WITH-DISCLOSURE (real-download retest) + PENDING-ROUTED (3 outbound actions ①CW push ②manifest pin ③RF push, explicitly sequenced at REMEDIATION §66:1384).
- Zero DEVIATED/UNVERIFIABLE verdicts; zero hard fabrication (work-claim without any evidence), 1 stale hash pin (F1), 1 missing named dir (F2).

Written by SA-CHAIN (independent reviewer) on 2026-09-23.
