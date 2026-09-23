# decision.md — FIX-W06-GAPS/a20260922-01 (per-fix red/green + minimality)

card FIX-W06-GAPS · owner ruling verbatim 「fail 的全部要修复」(+increments 「发现的缺陷都要全部修复」/「所有存疑都要确认」)
frozen oracle: `oracle.md` (+ dated APPEND A/B/C/D — frozen body untouched)
discipline: fix in COPIES (`iso/`), `before/` byte-identical originals, RED→GREEN→mutation, no historical
rewrites, no self-signing (`handoff.json: implementer_signed=false`), production source READ-ONLY.

## 0. Verdict summary

14 fix families, every one: RED reproduced on the BEFORE copy (matching the OPEN5-DOUBT-PROBE failure
faces) → GREEN on the iso copy → one mutation per family flips it RED (12/12 recorded mutations RED).
No-regression red lines kept green in every run (01's P1-a/P1-b PASS kept; P6's 8-writes/zero-lock/
658-reads-green shapes preserved under default timeout; positive controls in P5).
Product writes: exactly TWO files, both in revenue-forecast `tests/` (parent-authorized test-only
surface).  revenue-forecast `scripts/` and company-wiki `src/` byte-identical (binding.json
`product_source_integrity` all unchanged:true).

## 1. Per-fix red/green table

| # | fix group | probe face (RED on before/) | GREEN on iso/ | mutation (expect RED) | minimal repair rationale |
|---|---|---|---|---|---|
| 1 | P1-a fresh migrate | 01 P1-a was PASS — kept PASS | S1 PASS | — (control) | unchanged code path |
| 2 | P1-b idempotent re-migrate | 01 P1-b PASS — kept PASS | S2 PASS | — (control) | unchanged code path |
| 3 | P1-c N-1 additive migrate | 01 P1-b2 `new_columns_added=[] ok:false` → S3 FAIL | S3 PASS (7 cols added incl. key_version per APPEND A/D; 2nd run idempotent; 2 old rows + defaults intact) | drop one ADD COLUMN spec ⇒ S3..S6 RED | introspect `PRAGMA table_info` + one `ALTER TABLE ADD COLUMN` per missing column (nullable/defaulted per DEMAND_SCHEMA) — replaces the CREATE-IF-NOT-EXISTS silent no-op; no table rebuild, no row rewrite |
| 4 | P1-d register/claim on upgraded DB | 01 P1-c rc=1 `no column named request_sha256` / `no such column: lease_until` → S4/S5 FAIL | S4/S5 PASS | (covered by #3 mutation) | falls out of #3 (schema complete before use) |
| 5 | P1-e error contract | claim() bare `OperationalError` (01 P1-c) + list_active row-access IndexError class → S6 FAIL | S6 PASS (all failures = DemandStoreUnavailable w/ store's own message contract) | (covered) | wrap `(sqlite3.Error, KeyError, IndexError)` with the candidate's EXISTING message contracts ("demand store write/read failed: …"); no new message invented |
| 6 | P1-f fresh-DB path | S7 PASS | S7 PASS | — (control) | no change to fresh path |
| 7 | P2-B claim defined refusals | 02 assert B FAIL (loser got bare `None`, refusal shape {None,None,None}) + empty-pool silent None → P2B FAIL | P2B PASS (race: 1 winner + losers get `DemandStateError` w/ verbatim text; empty/unknown/live-lease refusals = M-D1 items 1-4) | claim empty-pool returns None again ⇒ RED | smallest contract change that removes the silent-loss face: `DemandStateError(DemandStoreError)` + the memory-queue's own texts (`no ready demand to claim` etc.), `claim()` never returns None; `demand_id`/`now` parameters additive (memory-queue shape) |
| 8 | P3-A explicit expire/reclaim | 03 `stranded_running_expired_lease=true`, no reclaim entry (AttributeError) → P3A FAIL | P3A PASS (expire() returns count; row → pending, lease cleared; explicit re-claim works) | expire neutered ⇒ RED | mirror the memory queue's `expire()` shape (the reference contract) — 1 UPDATE, explicit-only, never a silent steal |
| 9 | P3-B post-expiry refusals | 03 re-claim after expiry rc=0 -> None (both owners) → P3B FAIL | P3B PASS (`lease expired` for pool + demand_id shapes; live lease ⇒ `is not claimable`) | pool-branch text changed ⇒ RED | one precedence rule (expired-running ⇒ `lease expired`, else `no ready demand to claim`), texts frozen in oracle M-D1 |
| 10 | P4 pins (2 faces) | 04: 5/9 UNPINNED incl. C8-named #2/#4 | face1 4/4 + face2 8/8 green on current texts; product run 14/14 | 1 byte of pinned text (candidate copy / product source copy) ⇒ RED both faces | pins only — no product behavior change; single-source convergence: the block sentence is defined ONCE (w06a_candidate_patch.block_message_base), w06a_apply_candidate builds its anchor FROM it, and the product literal is pinned equal by assertion (cross-repo import impossible — the ruling's stated fallback) |
| 11 | P5-c dual binding mandatory | 05 P5-c `ACCEPTED` (WRITE-SIDE-GAP) → P5C FAIL | P5C PASS (missing binding ⇒ `source_sha256 must be a lowercase SHA-256` for ALL statuses; positive control accepts) | binding optional again ⇒ RED | validation flip only (`optional=True` → required), REUSES the pinned `must be a lowercase SHA-256` contract; call sites inventoried (17; 5 dual-bound; 17 flagged need-params — evidence/call_site_census.txt) |
| 12 | P5-a payload binding + rescan | 05 P5-a fabricated-hash `ACCEPTED` (FORGERY-FACE) + injection-payload-as-clean accepted → P5A FAIL | P5A PASS (payload required; sha256(payload)==evidence_sha256; internal scan_text re-run, declared status must equal scan verdict; true-clean positive accepts) | payload binding removed ⇒ RED | adds exactly the frozen checks ①②; RESIDUAL forgery face honestly recorded (any hash recomputable from any payload ⇒ full closure = OPEN-6 C1/C2 authorized tuple + signature, letter B) |
| 13 | P5-b disposal gate | 05 P5-b spoofed reviewer `ACCEPTED` (SPOOFABLE) → P5B FAIL | P5B PASS (tuple completeness → trust root → signature, each gap ⇒ `disposal authorization unavailable: <item>`; trust root absent ⇒ status always refused; valid Ed25519 signature positive accepts) | gate removed ⇒ RED | fail-closed gate with mechanical "no trust root ⇒ zero rows" form (OPEN-6 C3 shape, zero fake fixes); `not_detected` reviewer free string RETAINED + writer-audit metadata stamped, explicitly NOT identity (full identity chain = PARTIAL-fix-pending-external, letter B) |
| 14 | P6-A CAS + audit | 06 `lost_write_count=7` silent displacement → P6A FAIL | P6A PASS (8 concurrent writes: acks+defined rejections == attempts; read-back audit proves every ack;8/8 succeed under default timeout = red line kept) | CAS predicate removed ⇒ RED | read-modify-write becomes compare-and-swap (`WHERE metadata_json=<value read>`) with bounded retry then defined `concurrent write conflict`; append-only `prompt_injection_review_audit` makes every write read-back-provable ("无静默消失"); queue/merge slot semantics left to ratification |
| 15 | P6-B lock wrap | 06 P6-A2 7/8 bare `OperationalError: database is locked` → P6B FAIL | P6B PASS (all contention errors ⇒ `PromptInjectionReviewError: store busy/lock timeout: …`) | wrap removed ⇒ RED | wrap ALL writer/reader sqlite failures with the frozen text; APPEND B: the writer owns the transaction end of ITS write (commit/rollback) — GREEN-phase measurement showed the bare error escaping at the caller-side `c.commit()`; timeout rule kept (caller parameters may only be tightened — no added waits) |
| 16 | C7 state_domain fail-closed | C7 N1-N4 FAIL (no domain tags, legacy receipt accepted, ReviewEvaluation accepts any tag, `_SAFETY_MAP[unknown]` KeyError) | N1-N4 PASS (dual negatives + missing/illegal negatives + readiness strictest fallback) | state_domain check removed ⇒ RED | frozen-vocabulary CONFLICT (grep-verified, table below) blocks the rename route ⇒ ruling item 6 fallback: explicit `state_domain: cache\|review`, missing/illegal ⇒ refuse/strictest, ambiguity never defaulted |
| 17 | P7 idempotency key | c8/c9/c10: differing requests silently merged into one key/row (row `request_sha256` stale) + legacy surface unreadable → P7 FAIL | P7 PASS (each pair ⇒ 2 keys + 2 rows, per-row own request_sha256; legacy rows `key_version='triple-v1'`, no cross-version silent merge) | drop `as_of_date` identity field ⇒ c8 collapses ⇒ RED (after APPEND D decomposition) | key = sha256(canonical {source_sha256, review_policy, role_set, request_identity}) per OPEN-2 option A + OPEN-5 §4.5 条1; `key_version` column rides the P1 additive migrator (no silent semantic change: legacy keys stay historical, dedupe judges within version, read side exposes key_version = OPEN-4-style read-time judgment) |

## 2. Evidence map — 01_additive_migration.txt → this attempt (report requirement)

| 01_additive_migration.txt scenario | verdict there | this attempt evidence | verdict here |
|---|---|---|---|
| [P1-a first _initialize on fresh DB] rc=0 | PASS | evidence/RED_P1_migration.txt + GREEN_P1_migration.txt `S1_fresh_migrate` | PASS (kept) |
| [P1-b seed one row via register()] + re-run _initialize (2nd/3rd) | PASS | `S2_idempotent_re_migrate` | PASS (kept) |
| [P1-b2 build N-1 DB with 2 existing rows] / migrate 1st/2nd / `new_columns_added: []`, `ok: false` | FAIL | `S3_n1_additive_migrate` | PASS (RED run reproduces `ok:false` exactly; GREEN adds exactly the missing columns) |
| 01 rows after migrate (2) preserved + `old_rows_preserved/defaults_ok: true` | PASS | `S3` rows/defaults sub-checks | PASS (kept) |
| [P1-c register() against migrated N-1 DB] rc=1 `DemandStoreUnavailable: … no column named request_sha256` | FAIL | `S4_register_on_upgraded` | PASS (rc=0) |
| [P1-c claim() …] rc=1 bare `OperationalError: no such column: lease_until` | FAIL | `S5_claim_on_upgraded` + `S6_error_contract_wrap` | PASS (rc=0 / store-owned types only) |
| P1 OVERALL (fresh/idempotent/N-1-additive/preserve): FAIL | FAIL | S1-S7 aggregate + P2/P3/P5/P6/C7/P7 suites | PASS |

Related probe files map the same way: 02 assert B → P2B scenarios; 03 [P3-a candidate-store] stranded row +
resume/complete ABSENT → P3A/P3B/P3D scenarios; 04 pin table → P4 faces; 05 P5-a/b/c/d → P5A/P5B/P5C/P5D;
06 Phase A/A2/B → P6A/P6B/P6-redline.

## 3. C7 frozen-vocabulary conflict list (item 6 attribution grep-corrected per parent instruction)

Rename route (`cache_state="ignored"` → `policy_changed`) is BLOCKED; fallback = `state_domain` (ruling
item 6).  Grep-verified carriers of the literal `cache_state="ignored"` / `== "ignored"`:

| # | carrier (full path role + line) | citation nature |
|---|---|---|
| 1 | `execution_runs/I-06-B/a20260919-01/oracle.md:87` | **逐字钉点**（frozen acceptance expectation:「返回 `cache_state="ignored"`」） |
| 2 | `execution_runs/I-06-B/a20260919-01/handoff.json:50-51` | **逐字钉点**（N2b expected=measured=`cache_state=ignored`） |
| 3 | `execution_runs/I-06-B/a20260919-01/commands.json:17` | **用例名钉点**（`N2b(ignored)`，冻结执行契约） |
| 4 | `execution_runs/I-06-B/a20260919-01/scripts/w06b_review_harness.py:382` | **逐字断言钉点**（`eval_ignored.cache_state == "ignored"`） |
| 5 | `execution_runs/I-06-B/a20260919-01/after/review-invalidation-matrix.json:19` + `after/review-logs/run1_results.json:68` | **实测记录载体**（measured evidence rows, immutable history） |
| 6 | `execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md:233-234`（OPEN-5 RF 消费 owner 裁定，§6.4 消费侧底线条款） | **规范性契约引用**（逐字四态令牌 `tampered/ignored/expired/absent` 作「一律不可消费」契约词汇，自注「词汇取自 I-06-B 实测 cache_state：handoff.json:44-57」）；同文件 :376-377 = 分析性复述（对撞复核引同四态）；:439-441 = 其 C7 消歧定夺（描述性 + 指令：优先改名、冲突退断言字段） |

**归属更正（parent 指令第 3 条，已按「先 grep 后落记」执行）**：初报把第 6 项简写为「ruling.md:233-234」
未标全名。现证：该载体 = **T2-SIM-OPEN5-RF**（OPEN-5 RF 消费 owner 裁定）`ruling.md:233-234`，
**非** OPEN-6 文件。OPEN-6 文件（`execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md`）经 grep 核实
对该词**仅描述性引用**（:173 C7 条目、:201 留置、:218 消费面复核、:249 记6、:262-263 归属注记）——
全部在要求消歧、**无逐字钉点**，故 OPEN-6 文件不是钉点载体（与 OPEN-6 官核对一致）。未发现其他载体。

## 4. Scope boundary notes (honest, non-invented)

- **P3 resume/complete = 未建接口（非发现缺陷）**: parent ruling — handoff L240「不得假装存在」的正确缺席;
  their construction = I-06-B nine-step card.  Built here: P3-A expire + P3-B refusals (orphan-row defect,
  interface-independent).  Structural-absence pinned (P3D + face-2 `test_resume_refusal_surface_structurally_absent`,
  OPEN-5 C4 pending instantiation).
- **P4 item 3 `cases_json_declared_expectation_missing`** = RUNNER vocabulary (M01-M04 runner side), zero hits in
  both product repos is the CORRECT state (per parent clarification); pinned as a structural zero-hit assertion +
  this note — no product message to pin.
- **P5-a residual forgery face**: payload binding proves payload↔hash consistency, not truth — an arbitrary hash
  remains computable from an arbitrary payload; complete closure = OPEN-6 C1/C2 authorized tuple + signature
  (identity chain = letter B, external).  Recorded, not papered over.
- **P5-b identity**: reviewer free string retained for `not_detected` with `writer_pid/writer_write_at/
  writer_identity_note` audit stamp (explicitly NOT identity).  Full identity chain = PARTIAL-fix-pending-external.
  While the trust root is unestablished, `detected_and_ignored` is ALWAYS refused (OPEN-6 C3「身份落地前产品语义
  行数=0」mechanical form).
- **P6-A slot semantics**: the single-key primary receipt slot keeps its storage shape (last acknowledged CAS
  wins); queue/merge semantics left to ratification per parent instruction — but NO write is silent anymore
  (audit trail + ack-or-defined-reject, count conservation).
- **P6-B contract amendment (oracle APPEND B)**: writer owns the transaction end of its own write (the
  caller-side commit was where the bare lock error escaped — measured in GREEN phase).  Callers may still
  commit/rollback their own pending work.  Timeout semantics: caller parameters may only be tightened.
- **P7 authorities (three citations required by parent)**: OPEN-2 option A (key must include request identity —
  the reason the triple key was known-insufficient), OPEN-5 ruling §4.5 条1 (「request_identity 覆盖
  as_of_date/target/payload digest」verbatim contract), and that ruling's C1 condition (key includes request
  identity + probe re-run — the c8/c9/c10 re-run in evidence/p7_key_c8c9c10_*.txt).  APPEND D records the
  disjoint-decomposition resolution (single-field-drop mutation observable).
- **Idempotency key candidate status**: the KEY FORM is now the ruled OPEN-2 option A form, but the store itself
  remains UNRATIFIED (D-W06 frozen owner/schema/API signature still absent; candidate marker unchanged).
- **Product surface**: revenue-forecast `tests/` written (2 files, parent-authorized); all other product trees
  byte-identical; company-wiki hunks in changes.diff are PROPOSED ONLY.

## 5. Files written (hashes in binding.json)

- `before/` (10 byte-identical originals + MANIFEST.json), `iso/` (11 fixed/derived copies + 2 pin tests),
  `scripts/` (11 harness/generator scripts), `evidence/` (31 raw outputs), `oracle.md` (+4 APPENDs),
  `changes.diff`, `binding.json`, `commands.json`, `handoff.json`, `recovery/README.md`, this file.
- Product writes: `revenue-forecast/tests/test_message_contract_pins.py` (NEW), `revenue-forecast/tests/
  test_fc905b_trusted_receipt.py` (loose regex → verbatim pin; before sha256
  e5c965e5bfea67593772555d12ef68a325206e2559018b3333dbe715478b9684).

implementer_signed = false · accuracy = unproven · disclosure_adaptation = unmapped · status = review_pending
