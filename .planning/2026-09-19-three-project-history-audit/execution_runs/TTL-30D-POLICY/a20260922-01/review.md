# TTL-30D-POLICY review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **ACCEPT — scope-limited (`accepted_scoped`)**. The independent reviewer wrote the
verdict in `reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is
the carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict
and findings so the attempt's `review.md` slot exists. **It is a pure bookkeeping
transcription: it is not a signature, and it adds no acceptance of its own.** Read
`reviewer_report.md` itself for the reviewer's own words (Verdict, Findings F1–F14, Unverified,
REM-79 自检, 复跑与足迹). No verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this
file was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **TTL-30D-POLICY** / attempt `a20260922-01`
  (`<PLAN>\execution_runs\TTL-30D-POLICY\a20260922-01`) — land the owner-ratified 30-day
  receipt TTL policy cap in company-wiki's `prompt_injection_guard`.
- Verdict: **ACCEPT — 证据链齐备、原始件自洽、披露诚实；接受范围严格限定为父派发所列五项** —
  i.e. **ACCEPT, scope-limited**, transcribed from `reviewer_report.md` **line 7** (the verdict
  line under the `## Verdict` heading on line 5), scope items on **lines 9–13**.
- Verdict author: **独立复核** — an independent reviewer session dispatched by the parent;
  the report's signing-nature line (line 3) records the implementer did not sign
  (`handoff.unsigned.implementer_signed=false` 已核) and that the report claims no external
  signature. The landing executor did not author any part of this verdict.
- Round: round 1 of this card (single independent review round); verdict is **scoped**, not
  clean — five binding scope conditions travel with it.

### Carrier (byte-pinned, verified read-only at landing)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` (inside the attempt) |
| sha256 | `3fda91255762b847b24a5655a7d2099496d2481d98b626e67fdc798615502ff0` (independently re-hashed at landing; equals the dispatch's expected pin) |
| bytes | 14458 (matches the dispatch's 14458 B) |
| lines | 101, single trailing LF; 9461 characters |
| encoding | UTF-8 without BOM; LF line endings only (0 CRLF) |
| verdict heading line | 5 (`## Verdict`), bytes 418..427 (10 B), sha256 `297877e6ba7dd30cc1903ba18db2eba9d95a78231314d74e79e12e0c0619dd13` |
| verdict line | **7** (bytes 430..546, 117 B, sha256 `0ac6cb85fc5cc1f38d959177610c54bb3d09c5598eea3171b220916c116a6e45`) |
| verdict block lines | 5–13 (heading 5, verdict text 7, five scope items 9–13) |
| scope items byte regions | L9 549..695 (147 B) `6e0c163e…edc`; L10 697..782 (86 B) `33fcc18d…088`; L11 784..891 (108 B) `dece85ed…ca1`; L12 893..1050 (158 B) `f3a831d1…bd2`; L13 1052..1105 (54 B) `cf51f42b…cbd` |
| signing-nature (disclaimer) line | 3 (bytes 93..415, 323 B, sha256 `cd6deec024fce0b606fd645c310d9a9fc8eeb539930ac63506653fa550dc231e`) — 独立复审签署; implementer unsigned; reviewer actions read/grep/pwsh only |
| findings section lines | 15–82 (heading 15, `### F1` 17 … `### F14` 78, F14 nits 79–82) |
| unverified section lines | 84–92 (7 items; heading sha256 `5827c555…91c`, last item L92 13707..13804) |
| REM-79 self-check lines | 94–96 — `0 violation(s) across 1 file(s)`, exit 0 (L96 sha256 `d1c509f3…6de`) |
| reviewer boundaries lines | 98–101 — footprint: reviewer wrote **only** `reviewer_report.md` + `reviewer_report.sha256` (L101 14311..14456, 146 B, sha256 `cf7dc00562f2e31548c517ef0f47af94c88c38e604b28ef89d0fb1ded309b4c6`) |
| whole file minus trailing LF | 14457 B, sha256 `26489ad7f879a8c8eeb5acbf04d9e642a1b7d08bc120d4bd406236bbbf534c20` |
| pin sidecar | `reviewer_report.sha256` — **pre-existing** (reviewer-declared as one of its two written files); 86 B; sha256 `c5bda673f70d9cb52b7eef0d134d1a465f6ea8cd4e969a01724ed38cea9b09fd`; content `3fda91255762b847b24a5655a7d2099496d2481d98b626e67fdc798615502ff0  reviewer_report.md` — **content-matches** this pass's independent re-hash ⇒ not overwritten; **0 bytes written** to it |
| producer | independent reviewer (独立复核), not the implementer |

No byte of the carrier was changed by this landing pass: `reviewer_report.md` and its
`reviewer_report.sha256` sidecar were read-only here (this pass wrote only `review.md`,
`handoff.json`, and `evidence/TTL-30D-POLICY/qualification.json`).

## (a) Scope conditions — the five verdict items, VERBATIM from the carrier (lines 9–13)

Acceptance is **scope-limited, not clean**. Reproduced word-for-word from the reviewer's
verdict block:

1. 生产提交权归父：CW guard 单文件，after = `142AE84838960D500528F2BD3BEE1742758152E0518E061A67ED3997CA6DD7DD`（勿 `git add -A`）。
2. U-1（N7 窗口内 past-now 类）维持 **unproven**，本卡未宣称已堵死。
3. U-2（cap 不在 RULESET_HASH 载荷）= **声明式契约 + 运维纪律**的如实披露，非缺陷。
4. U-3（CLIP vs REJECT 先例冲突）= 父欠一次归一裁决，须与 I-06-A/a20260922-02 复审协调；本报告只记录分歧、不裁全局选择。
5. 零产品测试编辑（复算成立，见 F9）。

## (b) Findings F1–F14 — transcribed in substance (full records: `reviewer_report.md` lines 15–82; mirrored in `handoff.json.carried_findings`)

- **F1 — 交付件重哈希（逐项相符, L17）**: live re-hash matches
  `evidence/final_deliverable_hashes.json` / handoff / decision §6 item-by-item —
  `oracle.md`=30c4b637dd174f2bcfd3c0a6778519f543c94b70c9a4e93f94eec8551ca704c2 (13447 B),
  `oracle_freeze.json` 50c94d63…, `binding.json` d3ed1e35…, `commands.json` 566c0893…,
  `decision.md` acd9bff8…, `recovery.md` 79eeca05…, `handoff.json` e4e6fbd9…,
  `changes.diff` 8271158b…, `iso/` 142ae848…, mutants m1 61cdab69… / m2 f75eed61…,
  `caller_audit.txt` b42b2153…, product_tests before/after/mutant_m1 58b4ba08…/39fe2be5…/56cd47b8…,
  `hashes.json` b0a8615b…; full-attempt byte scan: **0** files carry a UTF-8 BOM (==
  `bom_remaining: []`). Non-blocking.
- **F2 — 冻结先行（CreationTime 实证, L21)**: ascending CreationTime — `oracle.md`
  **22:53:00** (earliest in the attempt) → `iso/` 22:55:47 → `scripts/ttl30d_probe.py` 22:57:01 →
  `evidence/red_before.json` **22:57:22** (first run). oracle.md's last write 22:55:45 precedes
  the first run ⇒ §5 errata (incl. §5-3 N7 pre-registration non-gating) fall inside the pre-run
  window, matching `oracle_freeze.json.errata_note`; oracle closing hash == freeze hash (F1);
  `red_before.json` embeds `guard_sha256=f900a13d…` == pre-freeze state ⇒ fixed before the
  target was touched. **frozen-first holds.**
- **F3 — before/after 锚 == live 生产 (L24)**: before=`F900A13D…9C08` (case-normalized) ==
  reviewer's live re-hash of the CW production guard `f900a13d…9c08`; after=`142AE848…7dd` ==
  live iso re-hash ✓.
- **F4 — changes.diff 可复现且无 git (L27)**: independently regenerated to %TEMP% with the
  card's own `scripts/make_diff.py` (difflib, reads live production + iso): **112 lines /
  6 hunks / sha256 8271158bf034e6fec60b65d48bec173f5ee1a98ad1538d29a8daebcbd29fdbd3 ==
  card pin, byte-identical**; hunk headers `@@ -20,12 / -58,6 / -157,13 / -187,6 / -194,6 / -211,6`.
- **F5 — 计数从原始件复算 (L30)**: RED `red_before.json` = **7/16 gating passed, 9 gating RED**
  = exactly the frozen set `{C0,G1,N1,N2,N3,N5,N6,N8,N9}` (N7 observed hit, gating=false);
  GREEN `green_after.json` = **16/16**, failed=[], embedded `guard_sha256=142ae848…` ✓, plus
  `green_confirm.json` (post-restore re-test) = **16/16** ✓; MUT-1 `mutation_m1_cap_removed.json`
  gating_failed=`{G1,N1,N2,N3,N8,N9}` == frozen set (10/16), embedded sha=61cdab69… == m1 file ✓;
  MUT-2 `mutation_m2_pastnow_removed.json` gating_failed=`{N5,N6}` == frozen set (14/16),
  embedded sha=f75eed61… ✓; **mutant purity by the reviewer's own difflib line-diffs**:
  **m1 = iso minus exactly the 5-line cap+isfinite block (one hunk); m2 = iso minus exactly the
  past-now branch block (one hunk)** ⇒ one guard flipped at a time.
- **F6 — 复审者自有 %TEMP% 复跑 (L36)**: fresh mirror `%TEMP%\rev-ttl30d-rev1` (new image + iso
  guard): probe full table **16/16, failed=[]**, guard 142ae848…; **N1** (365d over-cap) raises
  `PromptInjectionGuardError` with message **逐字** `ttl_seconds exceeds policy cap of 2592000s`;
  **N5** (past-now on FIXED iso): raised=null, `status=not_reviewed`, `cache_state=tampered`,
  reason=`receipt reviewed_at is after now (clock anomaly; now may only tighten freshness)`
  (contains `reviewed_at`) ✓; **G1 raises the same literal string as N1**; N7 observed hit
  (pre-registered non-gating); N8 `ttl_seconds must be a finite number`; N9 takes the cap message.
- **F7 — 实现轨迹（iso after 逐行读过, L43)**: constant
  `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400 * 30` (L85) with comment block L77-84
  (§十九 / C6 / 4c / policy_hash coverage) and module docstring L24-36 declaring the cap a
  policy-hash-covered policy surface (change = policy change; old receipts invalidated at read
  per OPEN-4 4c); `__all__` L267 exports the constant ⇒ C0's three conditions met. Validation
  order L239-250 **all before** L250 receipt lookup: source_sha256 format → policy_hash format →
  `ttl<0` → **`>cap` literal raise** → `math.isfinite` (NaN rejected) → only then the receipt ⇒
  over-cap rejected even with a missing receipt (invalid input before store access). `_freshness`
  L201-210: `now < reviewed_at` ⇒ `not_reviewed/tampered` (clock-anomaly text), placed **before**
  the age>ttl comparison; `now == reviewed_at` still fresh (strict `<` edge, P3 green). Boundary
  semantics confirmed: `-inf` → `>=0` text, `+inf` → cap text, `NaN` → finite text (N8/N9 re-runs).
- **F8 — 透传继承 (G1 代码路径, L49) [record-note]**: `readiness_graph.py` L82 parameter →
  L102 `ttl_seconds=ttl_seconds` into `evaluate_review` → L115/L132 public entries pass through;
  readiness side builds **no** cap of its own ⇒ automatic inheritance (reviewer's probe G1 raises
  the same text as the raw call); the readiness file itself is unchanged (not in the diff).
  Recorded as a note: no action, nothing to fix.
- **F9 — 零测试编辑：独立复算成立 (L52)**: repo-wide grep of `ttl_seconds` in CW: product-test
  call sites = `test_prompt_injection_guard.py` **10** (L187/201/214/228/241/253/268/286/298/302)
  + `test_readiness_graph.py` **2** (L223, L181 with `TTL=86400*30` from L34) ⇒ **12 sites**,
  matching decision §7's 10+2; **max value == 2592000 == cap; count of values `>cap` = 0**;
  decoy excluded (`tests/contract/test_source_catalog_control.py` L700/707's
  `now + 86400 * 365` is the `llm_summary_failures` expiry column, not `ttl_seconds`); other CW
  hits are docs/plans JSON-schema foreign domains (`authorization_ttl_seconds` max 2592000,
  journal `ttl_seconds` max 300). Edit surface: newest CW `tests/` mtime = **22:22:42 <
  attempt window start 22:53** ⇒ **0** CW test files written during this card. Conclusion:
  `caller_audit.txt`'s "max==cap, >cap=0 ⇒ zero test edits" recomputes as true.
- **F10 — 诚实缺口 U-1 / U-2 / U-3（含引文核对, L59)**:
  **U-1**: oracle §5-3 makes N7 a pre-registered **non-gating** structural limitation — proven
  by F2's timestamp evidence to precede the first run; N7 observed hit in both rounds with
  gating=false, disclosed in decision §5-1 and handoff.unproven, never claimed as a pass ⇒
  stays **unproven** ✓. **U-2**: in iso, `RULESET_HASH = sha256(json(_RULESET_PATTERNS))` (L69-73)
  — the cap constant is **not** in the payload ⇒ changing the cap does not roll policy_hash,
  true as stated. Citation check: OWNER_DECISIONS.md:439 verbatim ✓; OPEN-6 ruling.md:172 C6
  verbatim ✓ (negative case 「被拒或被策略上限截断」 present); :215 「L168 纯调用方比较、无策略侧上限」
  present; OPEN-4 ruling.md:63 (4c APPROVE: invalidate at read, policy-content change ⇒ full
  re-review) and :116-127 (policy_hash mismatch ⇒ ignored→not_reviewed, invalidation at next
  read, full re-review refusing incremental patch) present; **「TTL 的数值不由本裁定规范」 is
  verbatim at :137**; **:194 is same-meaning but NOT verbatim**（「本裁定全文未写规范数值…TTL 归数值裁定
  轨道」）— decision §1 calling both 「:137,:194」 明文 is a **minor citation nit** (F14-3), conclusion
  unchanged. U-2 characterization = declarative contract + ops discipline; automatic rollover
  would void every existing receipt and is beyond this card's authorization ⇒ honest disclosure
  holds. **U-3 — clip-vs-REJECT divergence**: both precedent implementations are proven on disk —
  **I-06-A/a20260922-02** iso guard live re-hash = `cf9174b538288f71349f3d33b46f96eacb6a16f5df4906764b08439230119c03`; its **L78-82 `effective_receipt_ttl` = CLIP**
  (`min(float(ttl), RECEIPT_TTL_POLICY_CAP_SECONDS)`, L71 constant 86400*30) applied at
  **L296** (L297 also clamps `now`); **production contains NEITHER** — live CW guard grep of
  `effective_receipt_ttl|RECEIPT_TTL_POLICY_CAP|effective_review_instant|policy cap` = 0 hits ⇒
  divergence recorded, normalization belongs to the parent (coordinate with the I-06-A review);
  this report does not rule CLIP vs REJECT globally ✓.
- **F11 — 产品基线 26 (L64)**: raw three files: before "26 passed in 9.46s", after
  "26 passed in 13.68s", mutant m1 "26 passed in 16.66s", all under the same
  CW-BASETEMP-DECISION header; reviewer's **own** independent %TEMP% re-run (iso guard, zero
  test edits): **26 passed in 4.52s** ⇒ the honest statement "product tests still 26 under m1
  (they cannot detect it; the oracle probe is the only detector)" holds.
- **F12 — commands 账本诚实（GBK + BOM, L67)**: C11a rc=1 (GBK stdout pipe failure on U+21D2,
  19-line fragment) **disclosed**; C11b direct UTF-8 overwrite — reviewer's reproduction (F4)
  yields the same hash ⇒ final artifact clean, fragment never used as evidence. BOM:
  `scripts/_final_hashes.py` checks **4 candidates** (`evidence/hashes.json` + 3 product_tests
  txt); `final_deliverable_hashes.json` records `bom_normalized` = **3** (the 3 product_tests;
  hashes.json had no BOM) and `bom_remaining` = []; the 3 files' mtimes (23:17:00.21x) match
  that normalization; reviewer's whole-tree byte scan = 0 BOM, raw 26-passed structure intact.
  **Minor ledger gap: `commands.json` does not list the BOM-normalization step** (the fact lives
  only in `evidence/final_deliverable_hashes.json` + the script) — a disclosure-channel nit, not
  concealment (F14-2). The brief's "4 BOM-normalized" = 4 candidates examined; actual writes
  normalized = 3, `bom_normalized` is authoritative.
- **F13 — 边界：生产零写 / 零 git / recovery 单文件 (L72)**: production zero-write — CW guard
  live re-hash == f900a13d (F3); CW tree mtime scan over the card window (22:50–23:20): source
  and tests **zero** writes, sole hit `.source_catalog/catalog.sqlite3-shm` (SQLite transient
  sidecar; `catalog.sqlite3`/`-wal` still dated 09-19) — unattributable to a process inside a
  window with sibling attempts running ⇒ recorded as Unverified. Zero git: reviewer's boundary
  forbids git ⇒ **porcelain spot not executed**; substitute evidence = `commands.json` contains
  no git verb end-to-end and `changes.diff` is difflib-generated and byte-reproducible without
  git (F4). `recovery.md` = **exactly 1 file** rollback: forward anchor 142AE848 → landing,
  rollback anchor F900A13D (= production's current bytes), after→before pair aligned, commit
  scope "exactly 1 file, 勿 git add -A", post-rollback behavior returns to the before baseline
  with product tests still 26 (the probe's reason for existing) — consistent with F1/F3.
  Incidental observation (RF repo, outside this card): `tests/test_fc905b_trusted_receipt.py`
  (23:15:07.9839532) and `tests/test_message_contract_pins.py` (23:12:33.4872869) written in
  window, byte-identical to sibling `FIX-W06-GAPS/a20260922-01/iso/rf/*` (db8bbb48… /
  41da045c…); RF root `.pytest_cache\v\cache\nodeids` 22:55:37 also in window; no intersection
  with this card's ledger/iso/scripts ⇒ attributed to the sibling card and **adjudicated at
  landing — see (d)**.
- **F14 — 瑕疵清单（不阻断接受, L78) [record-notes]**:
  1. (信息) oracle.md's "frozen-first" currently rests on filesystem timestamps + closing hash;
     a future card could add an external time anchor at freeze time if the plan layer wants
     stronger evidence.
  2. (轻微) the BOM-normalization step is absent from `commands.json`'s step table (see F12).
  3. (轻微) decision §1 cites OPEN-4 ":137,:194" as both verbatim; **:194 is same-meaning,
     not verbatim** (:137 is verbatim).
  4. (提示) decision/handoff say "prod and iso are both LF-only (0 CRLF)" — consistent with the
     hash-chain diff reproduction; the reviewer did not do a per-line EOL count (non-gating).
  None of the four blocks acceptance; all are recorded as notes only.

## (c) Unverified / open — carried forward verbatim-in-substance (carrier lines 84–92)

1. **git state / porcelain spot**: review boundary forbids git; no `git status`/`diff` ran —
   RF/CW git hygiene rests on mtime scan + hashes + the card ledger (F13).
2. **In-window write attribution** (at landing: see (d)) — `catalog.sqlite3-shm` (CW) remains
   unattributed; the two RF test files + RF `.pytest_cache` were judged sibling activity by
   content/time correlation and are now **adjudicated as authorized** (parent's FIX-W06-GAPS
   product-test face).
3. **U-1** (now ∈ [reviewed_at, legal now) in-window past-now): structurally undecidable,
   stays **unproven**; proof needs a trusted clock/monotonic anchor contract change.
4. **U-2** (cap into the RULESET_HASH payload): not implemented, not authorized here;
   = declarative contract + ops discipline disclosure.
5. **U-3** (CLIP vs REJECT normalization): only both implementations' existence and production
   having neither is proven; global ruling reserved for the parent + the I-06-A review.
6. **U-4** (production wiring behavior): shadow-only module has no production entrypoint calling
   `evaluate_review`; unverified **by design**.
7. No external signature exists in the carrier; the implementer never signed
   (`handoff.unsigned` checked item-by-item).

## (d) Parent adjudication added at landing (bookkeeping record, not a new verdict)

- **RF test writes are the sibling card's authorized face, not a boundary violation:**
  `revenue-forecast/tests/test_fc905b_trusted_receipt.py` + `tests/test_message_contract_pins.py`
  = **FIX-W06-GAPS's authorized product-test face**. Basis: the parent's P4-SCOPE dispatch (as
  quoted in this landing dispatch) explicitly scoped 「产物 tests/test_message_contract_pins.py
  （或等价）、只加测试不动产品源」, and FIX-W06-GAPS's own report states 「产品写入仅 2 文件」 —
  corroborated on disk by `FIX-W06-GAPS/…/decision.md:105` ("revenue-forecast `tests/` written
  (2 files, parent-authorized)") and `commands.json` ("Copy-Item iso/rf/test_message_contract_pins.py
  -> revenue-forecast/tests/… (NEW, parent-authorized test-only)"). ⇒ **NOT a boundary
  violation**; the reviewer's factual observation stands and is here adjudicated as authorized.
  This adjudication is recorded by the landing pass on the parent's dispatch and adds no
  acceptance beyond transcription of that dispatch.
- **RF `.pytest_cache`** = a product-tree test-run side effect of that authorized face; recorded
  honestly, no action.
- **U-3 parent action owed**: standardization between CLIP (I-06-A iso) and REJECT (this card's
  iso) must be coordinated with the **I-06-A/a20260922-02** review; production currently has
  neither implementation.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this
  pass on the parent's dispatch; the verdict itself is the reviewer's (carrier line 7).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; the verdict is
  **transcribed, not authored**, by this pass — this file adds **no acceptance of its own**.
- Authority: acceptance was written by an independent reviewer (独立复核) in
  `reviewer_report.md` (sha256 `3fda9125…02ff0`, 14458 B, 101 lines, pinned by the **pre-existing**
  `reviewer_report.sha256` whose content matches this pass's independent re-hash).
- Files written by this pass (exactly three): `review.md` (created, this file — sha256 reported
  to the parent), `handoff.json` (status + status_authority + bookkeeping + carried_findings
  F1–F14 + carried_unverified U-1..U-4 + cross-card adjudication + `*_historical_pre_verdict`
  retention of stale pre-verdict prose; pre-existing content otherwise untouched), and
  `evidence/TTL-30D-POLICY/qualification.json` (created). **0 bytes** written to
  `reviewer_report.md`, its sidecar, any evidence raw file, any plan file, any git state, or
  production. Zero git commands executed.
