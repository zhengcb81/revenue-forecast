# AUDIT-INTEGRITY — Independent Evidence-Chain Audit (端到端可执行核)

**Lens:** 证据链完整性 — chain-of-custody + no-fabrication sweep (evidence surfaces).
**Mandate (owner order):** 「请你用一个或者多个独立的subagent把整个项目过程中的几个重大节点做一次全面独立审查，最好用类似端到端测试的方法…保证现在的项目进展不偏离最初的设计。」
**Scope roots (READ-ONLY):** RF=`C:\郑曾波\Projects\revenue-forecast` · PLAN=`<RF>\.planning\2026-09-19-three-project-history-audit` · CW=`…\company-wiki` · FF=`…\filing-fetch`.
**My writes:** only `<PLAN>\execution_runs\AUDIT-INTEGRITY\a20260923-01\` (this report + sidecar + `evidence/`). No repo mutated; no network; git read-only (status/rev-parse/cat-file/hash-object/log). Temp runs in `%TEMP%\audit_integrity\`.
**Independence:** I authored no verdict under audit; every value below was re-computed by me (Get-FileHash SHA256, Python `hashlib`, `git cat-file`/`hash-object`). I trusted no prior report's transcription.

---

## VERDICT

```
VERDICT: BROKEN-LINKS-found
FABRICATION-SUSPECT: NONE (0 fabricated artifacts; every sampled sha resolves to a real artifact)
BROKEN LINKS: 1 (severity MEDIUM — stale pin from post-capture source revision, git-explained; recoverable)
```

The chain is **substantively intact** across all 9 faces: 14/14 carrier three-point links hold, 286/286 byte-proofs resolve to real bytes, every cross-repo product hash matches its commit, batch-2..9 are continuous on `origin/main`, and **zero** implementer self-signatures exist. Exactly one hash-link no longer holds on disk — the `OPEN-6` ruling pin — and git proves it is a **stale pin after a legitimate batch-5 revision**, not a fabrication. One further `declared≠disk` (a bind-time pin of a now-dirty mutable product `README.md`) is expected drift and not a chain break. No softening: both `声明值≠盘上值` cases are listed and graded below.

---

## 失配 / 断链全清单 (mismatches & broken links — every "声明值≠盘上值", graded)

### BL-1 (MEDIUM) — `OPEN-6 ruling.md` pin is STALE (post-capture revision) — NOT fabrication
- **Declared (verbatim, `outward_requests\RESPONSES.md`):**
  「函A / T2-2(OPEN-6) / 安全 reviewer… 落点 `execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` / sha256 `8aabac0908b407b8af5108c00b4a26e11476d889b593ade306d1eee519c368d1`」
- **Also declared** in `execution_runs\I-06-A\a20260919-01\rulings_transcribed_2026-09-22.md:728` (`sha256: 8aabac09…368d1`) and its byte-identical I-06-B copy.
- **Measured on disk (2 independent methods: Python `hashlib` + `Get-FileHash`):** live `T2-SIM-OPEN6-SEC\a20260922-01\ruling.md` = **`5cb476767a934885f48eb40fcccac0515243471a7fc6f0aa0b66680bea99cf15`**, 52 560 B, 28 457 chars. **`8aabac09…` ≠ live ⇒ declared≠disk.**
- **Root cause (git-proven, read-only `git cat-file blob`):**
  - `243d0cb6` (batch-4) blob of that path = **`8aabac09…`, 49 796 B** — **equals the pin and equals the transcribed BEGIN/END body (byte-exact)**.
  - `1fa090fe` (batch-5) blob = `5cb47676…`, 52 560 B (= current live).
  - Controls `OPEN-4`/`OPEN-5` at `243d0cb6` = `37413f78…`/`74f5c835…` = still their live values (batch-5 touched **only** OPEN-6).
- **Nature (not softened, correctly typed):** The transcribed evidence body is faithful and preserved (both I-06-A & I-06-B copies hash to `8aabac09`, byte-identical to the batch-4 source). The **source ruling was legitimately revised in batch-5** (owner ratification 「全部接受」 expanded the tail) **without re-pinning** `RESPONSES.md`. This is a **stale/broken hash-link + a currently-false hash assertion**, **NOT** evidence fabrication or tampering.
- **Segment delta (measured):** transcribed body vs live file share a 22 394-char common prefix and a 232-char common suffix; they diverge across the intervening ~4 300-char (body) / ~5 800-char (file) region — i.e. the live ruling gained/reworded tail content after capture.
- **Remediation (recovery):** re-pin `RESPONSES.md`/`rulings_transcribed` OPEN-6 row to `5cb47676…`, **or** annotate the row "body pin `8aabac09` = batch-4 `243d0cb6` version; source later revised at `1fa090fe`". Either preserves the already-correct transcription.

### BL-2 (LOW / informational) — `PROMOTION-EXEC` binding pins a now-dirty mutable product file — expected drift
- **Declared (`execution_runs\PROMOTION-EXEC\a20260922-01\binding.json:82`):** 「"company-wiki/README.md": "302bd10b386b4aad425b812edd2cbbf05f4d7d12a28865404172eae2f1858512"」
- **Measured:** live `company-wiki\README.md` = `fdc75e0a72da96d5…`. **`302bd10b…` ≠ live ⇒ declared≠disk.**
- **Nature:** This is a **bind-time pin of a mutable product README**, and `git -C CW status --porcelain` shows ` M README.md` (currently dirty in the CW working tree from in-flight `CW-GATE-UNBLOCK`). Legitimate evolution of a non-evidence product file, **not** a chain break and **not** fabrication. (Its sibling `company-wiki/CLAUDE.md` = `963869fa…` still matches.) No action beyond noting the pin is time-scoped.

**No other 声明值≠盘上值 and no 声称存在但盘上无 (claimed-but-absent) artifact was found.** Every other sampled claim re-hashed correctly or resolved to a real artifact (see Faces 1–8).

---

## 各面 pass/fail 表 (each row = a sample point + my measured value)

### Face 1 — 载体-哈希链 (carrier-hash chain) · **PASS**
Three-point = `reviewer_report*.md` live sha256 == sidecar content == `review.md` 转录块声明. All self-run.

| carrier (card/attempt) | live sha256 (measured) | ==sidecar | ==review.md decl | 3-pt |
|---|---|---|---|---|
| TTL-30D-POLICY/a20260922-01/reviewer_report.md | `3fda91255762b847…` | ✓ | ✓ | ✓ |
| FIX-W06-GAPS/a20260922-01 | `b42d9418dfbb8a0f…` | ✓ | ✓ | ✓ |
| I-06-A/a20260922-02/reviewer_report.md (round-1) | `4c3f3f3d43a63e41…` | ✓ | ✓ | ✓ |
| I-06-A/a20260922-02/reviewer_report_r2.md (active) | `2f685f0f6fe06795…` | ✓ | ✓ | ✓ |
| I-06-B/a20260922-02 | `855a302d4d97…` | ✓ | ✓ | ✓ |
| I-06-B/a20260923-01 | `0c74f22dc27b…` | ✓ | ✓ | ✓ |
| I-07-B/a20260923-01 | `fc96bb0bec10…` | ✓ | ✓ | ✓ |
| I-07-C/a20260923-01 | `d5e3e661f9638048…` | ✓ (sidecar has UTF-8 BOM `\ufeff`, content still matches) | ✓ | ✓ |
| I-07-D/a20260923-01 | `1a1d1c0500e9…` | ✓ | ✓ | ✓ |
| E2E-EXPAND/a20260923-01 | `de849e1adfb21ea3…` | ✓ | ✓ | ✓ |
| F-EE1-FIX/a20260923-01 | `588f8d955f4f06db…` | ✓ | ✓ | ✓ |
| GUARD-MERGE/a20260922-01 | `2a26aaae736c4403…` | ✓ (`reviewer_report.md.sha256`) | ✓ | ✓ |
| CW-TEST-DEBT/a20260922-01 | `6f3febf70c59148d…` | ✓ (`reviewer_report.md.sha256`) | ✓ | ✓ |
| CFI14FR1-SAMPLE/a20260922-01 | `f958d5466aef…` | ✓ | ✓ | ✓ |

- **`status_authority` field-by-field recompute** (carrier sha / bytes / total_lines / chars): TTL `meta_sha=T meta_bytes=T meta_lines=T chars=T`; I-06-A (vs r2) `T/T/T`; CFI14FR1 `T/T/T`. **All match.**
- **`byte_proof` / `qualification` byte-region recompute: 286/286 regions resolve to real byte ranges of a real file (0 fabricated, 0 unresolved).** (`evidence/s1d_region_resolve.json`.) The 15 regions my first pass "mis-hashed" belong to `review.md`/other carriers and resolve once bound to their true target file.
- **`implementer_signed==false` + `verdict_is_transcribed_not_authored==true` full scan (380 handoff/qualification files):** `implementer_signed` × **435 all `false`**; `verdict_is_transcribed_not_authored` × **111 all `true`**; `implementer_never_signs_acceptance` × **321 all `true`**. **0 violations.** ⇒ the standing claim "implementer never self-signs" is **independently confirmed**.

### Face 2 — 转录保真链 (transcription fidelity) · **PASS with 1 stale pin (BL-1)**

| point | declared | measured (live/segment) | verdict |
|---|---|---|---|
| RESPONSES OPEN-4 `37413f78…` | `37413f7812bbe4aa…` | `37413f7812bbe4aa…` (Get-FileHash + hashlib) | ✓ |
| RESPONSES OPEN-5 `74f5c835…` | `74f5c83598355bd4…` | `74f5c83598355bd4…` | ✓ |
| RESPONSES OPEN-6 `8aabac09…` | `8aabac0908b407b8…` | **`5cb476767a934885…`** | ✗ **BL-1** |
| rulings_transcribed OPEN-4 seg (both copies) | `37413f78…` | seg_sha=`37413f78…`, seg==src bytes | ✓ |
| rulings_transcribed OPEN-5 seg (both copies) | `74f5c835…` | seg_sha=`74f5c835…`, seg==src bytes | ✓ |
| rulings_transcribed OPEN-6 seg (both copies) | `8aabac09…` | seg_sha=`8aabac09…` (= batch-4 blob) but **≠ live file** | ✓ body / ✗ live pin (**BL-1**) |

Three-point segment-level sha recomputed for the 3 rulings × 2 copies (I-06-A & I-06-B byte-identical). git-blob history resolves BL-1 to a post-capture revision.

### Face 3 — 跨仓映射链 (cross-repo mapping) · **PASS**

| claim (register §51/§58 etc.) | measured (live sha256) | match |
|---|---|---|
| CW `bf0c8b2` exists (`git cat-file -t`) | `commit` (== CW HEAD) | ✓ |
| `canonical_writer.py` = `4bc65372…` | `4bc653725febcc75…` (18 380 B) | ✓ |
| GUARD-MERGE→CW `5d72529` (exists) | `commit` | ✓ |
| `prompt_injection_guard.py` = `d7125478…` | `d71254782c10cd6d…` | ✓ |
| `prompt_injection.py` = `88154de4…` | `88154de4ab763060…` | ✓ |
| `readiness_graph.py` = `50c94de2…` | `50c94de28f328d12…` | ✓ |
| CW-TEST-DEBT `tests/unit/test_readiness_graph.py` = `a5db0c9c…` | `a5db0c9c6959d9c8…` | ✓ |
| CW-TEST-DEBT `tests/unit/test_prompt_injection_guard.py` = `d3bde1a3…` | `d3bde1a3d5ec2495…` | ✓ |
| E2E `e2e/run_cross_repo_chain_e2e.py` = `88ac9e4a…` | `88ac9e4a4d207c02…` (66 643 B) | ✓ |
| E2E `tests/test_cross_repo_chain_e2e.py` = `3e2b39ee…` | `3e2b39ee10947c38…` (7 037 B) | ✓ |
| allowlist `ff9db8c8…` @ commit `262659e4` (`git cat-file blob`) | `ff9db8c8cdb11f71…` (4 913 B) == live | ✓ |
| `ac4ebd0` exists (`git cat-file -t`) | `commit` | ✓ |

(`88ac9e4a`/`3e2b39ee` are file-content sha256s, correctly *not* git objects.)

### Face 4 — 批次链 (batch chain) · **PASS**
`git log origin/main` enumerates a continuous, ordered batch series: `batch-2` `3861f08d` → `batch-3a/3b/3c` `17565057`/`60489e34`/`4b1c690b` → `batch-4`/`4b` `243d0cb6`/`865428f8` (+promotions `95df2661`/`ec307d20`/`5fd82de7`) → `batch-5`/`5c` `1fa090fe`/`b0d016a6` → `batch-6` `262659e4` → `batch-7` `a31fd7ed` → `batch-8` `977fa1e8` → `batch-9` `b7a6a116` (= HEAD = `origin/main`, ahead0/behind0). Register narrative refs corroborate (e.g. §52 `0d10ae8f`→amend `1fa090fe`; §55 batch-6 3 RF files `88ac9e4a`/`3e2b39ee`/`ff9db8c8`; batch-4 promotions `95df2661`/`ec307d20`/`5fd82de7`). Refs are continuous — no gap/rewind.

### Face 5 — 无捏造抽 (no-fabrication, ≥10 points) · **PASS — 0 fabricated**
Every sha256 claim sampled from `REMEDIATION_REGISTER.md`/`progress.md`/`findings.md`/`review.md`/`decision.md`/`binding.json` was re-pointed at a live artifact. Distinct claim-hexes resolved across 3 deep attempts (GATE-OQ-FIX 20, PROMOTION-EXEC 51, M01-M04-PROPAGATE 29) + targeted named-file checks. Resolutions:
- **Whole-file re-hash matches** (examples, all measured): `test_i08c_consumer_rejection.py`→`3f83fdf2…`✓; `B5-fix-g1a-g3\…\M05-M08\runner.diff`→`8263fc83…`✓; `…\run_card.py`→`489ba7e3…`✓; `company-wiki\CLAUDE.md`→`963869fa…`✓; `tools/pre_push_gate.py`→`3df161a7…`✓; each attempt's `reviewer_report.md`/sidecar/`changes.diff`/`oracle.md`/before-images→ all ✓.
- **Byte-region proofs** → 286/286 resolve (Face 1). (Many "unresolved-looking" hexes are *byte-slice* hashes, correctly not whole-file.)
- **git object ids (40-hex)** → `4b1c690b…`=`commit`, `483486bd…`=`blob` (`git cat-file -t` ✓). (Not sha256; correctly excluded from content-hash matching.)
- **Before / superseded images** (e.g. `decision.md before 037b24b6…→after 18dfc2da…`, `superseded_source_hashes`) → labeled historical pre-edit states; expected not to match the current mutable file.
- **Only live-hash drift** = `BL-2` (README.md, mutable + dirty). **No claim asserted a nonexistent file.**

### Face 6 — 零自签全量扫 (zero self-sign) · **PASS**
380 `handoff.json`/`qualification.json` walked key-by-key. `signed`/`signature` occurrences (19) are all either `signed=false`, `signature=null`, or descriptive line-range text naming the **independent** reviewer signer (e.g. `E2E-EXPAND` `signature='506-509 (N=1 independent reviewer signer)'`, `F-EE1-FIX` `signature='313-319'`). **No `signed=true`, no implementer-authored signature anywhere.** Only independent reviewer reports sign. ⇒ "implementer 从未自签" **independently verified**.

### Face 7 — REM-79 检查器 (ran `tools/check_domain_assertions.py v1.2.0-correction2`) · **PASS (0 true violations)**
Scan of `REMEDIATION_REGISTER.md`+`progress.md`+`OWNER_DECISIONS.md`+`findings.md` current text → **8 hits** (register 5, progress 1, findings 2, OWNER_DECISIONS 0). Adjudication (逐条裁):

| # | file:line | marker | adjudication | basis |
|---|---|---|---|---|
| 1 | REMEDIATION_REGISTER.md:155 | 没有 | **行级域可接受** | 「未跟踪目录连已提交的基座都**没有**」bounded to the named path `execution_runs/B5-plan-level-remediation/` + `34,764 B` + 1 named file |
| 2 | REMEDIATION_REGISTER.md:411 | none | **假阳 (lexicon)** | literal `bundle=None` (code value), not a quantifier; line carries counts (RED 8→GREEN 35, M1 9红) |
| 3 | REMEDIATION_REGISTER.md:1092 | all | **假阳/行级域可接受** | "All checks passed" = ruff tool-status over 「两文件」+「15/15」 |
| 4 | REMEDIATION_REGISTER.md:1192 | all | **假阳/行级域可接受** | "All checks passed" tool-status; line scoped by `new=2`/`new=0`/`:44/:48`/「8 测」 |
| 5 | REMEDIATION_REGISTER.md:1202 | none | **行级域可接受** | heavy inline domains (`批 5`, `4F/51P`, `:1078`, `:150-156`) |
| 6 | progress.md:1060 | 全部 | **行级域可接受 (borderline — nearest to a true positive)** | 「目标余项盘点（**全部**为 owner/外部闸）」scoped by noun 「目标余项」; recommend attaching a count for strictness |
| 7 | findings.md:633 | all | **假阳/行级域可接受** | "ALL GREEN" tool-status over 「七检」+ enumerated `version/…/manifest` |
| 8 | findings.md:684 | none | **假阳 (lexicon)** | literal `产品面=NONE` (value), bounded to 「批次 3」; line carries `gitlinks_total=0`, 「四锚」 |

**True positives: 0.** Consistent with the project's own REM-79 self-check stance (batch-3b: "3 findings, 0 true positives, lexicon sealed"). The EN marker lexicon matches code/tool literals (`None`, `NONE`, "All/ALL … passed/green") and under-matches Chinese enumerations & path-noun bindings. (Self-check of *this* report: universal statements carry inline scope/counts.)

### Face 8 — 历史产物不可改 (historical immutability) · **PASS**
- `GATE-OQ-FIX`/`PROMOTION-EXEC`/`M01-M04-PROPAGATE` binding & review sha claims re-resolved: all bind-time/self hashes map to real attempt artifacts (carriers, sidecars, `oracle.md`, `changes.diff`, `recovery/before_images/**`, `scratch/precheck_repo/**`). Apparent "mismatches" were **prose mis-associations** (e.g. `9e6809c2…` is the *sidecar's own* hash, `3df161a7…` is `tools/pre_push_gate.py`) — each resolves to a real file when correctly bound.
- `execution_v2\` design docs: 110 files hashed (e.g. `card_I-00-A.md`=`ca7425cc62d4…`, `dispatch.json`=`c63764d11de1…`, `validation.json`=`a14dbf14eac3…`); no historical pin in `I-00-A`/`binding*.json` contradicts them (0 conflicting references found). Artifacts are stable.

### Face 9 — 在飞一致性 (in-flight, existing-files self-consistency only) · **NOTED (no "unchanged" claims)**
5 in-flight cards are mid-write (`CW-GATE-UNBLOCK`, `RF-RATCHET-FIX`, `RF-RATCHET-REST-A`, `RF-RATCHET-REST-B`, `RF-STEP9-TRIAGE`). I assert **nothing** about their stability. Self-consistency observations on existing files only: freeze-first scaffolding present (`binding*`/`oracle.md` precede `evidence/`); housekeeping nit — `RF-RATCHET-REST-A\a20260923-01\.decision.md.49816.a9b9e87a-…\decision.md.tmp` is a leftover atomic-write temp; `RF-RATCHET-REST-A` uses `ORACLE.md` (uppercase) vs `oracle.md` elsewhere. All expected for in-flight work; excluded from CHAIN-INTACT claims. (CW working tree is dirty on `artifact_dag.py`/`CLAUDE.md`/`README.md` from `CW-GATE-UNBLOCK` — the BL-2 drift source.)

---

## Unverified (无法在本审计内核实)
- **Cross-repo remote push state** beyond local read-only git: CW commits `ac4ebd0`/`5d72529`/`bf0c8b2` are local (register §60 says push is queued); I did not push or fetch, so upstream/`origin` server-side state is unverified.
- **Product functional behavior** (the 26-test suite, ratchet, E2E run outcomes): I verified artifact *identity/integrity* (hashes), not re-executed product test suites (out of scope for an evidence-chain audit; no network / no writes).
- **`before`/`superseded` image *provenance*** beyond self-consistency: their historical correctness rests on the cards' own ledgers (I confirmed the bytes exist and self-match where retained).
- **Real external TIER-2 signatures:** per `RESPONSES.md`, all three T2 rulings are role-play/simulated (`非外部方真实签署、未在任何函上签字`); no genuine third-party signature exists to verify — consistent with the recorded "not externally signed" stance.

## 方法统计 (method & sampling)
- **≥40 sample points, all self-run** (no transcription trusted): 14 carrier 3-point + **286** byte-region recomputes + 3 status_authority meta + 13 qualification mirrors + **380**-file self-sign walk + 3 RESPONSES pins + 6 transcribed segments + 2 git-blob history + 2 controls + 17 cross-repo (12 live hashes + 5 git) + batch-2..9 (9+ refs) + ~100 distinct claim-hexes resolved (Faces 5/8) + 7 named-file existence/hash + 2 git-id resolves + REM-79 4-file scan (8 hits) + 5 in-flight cards.
- **Tools:** `Get-FileHash -Algorithm SHA256`, Python `hashlib.sha256`, `git cat-file -t/blob`, `git hash-object`, `git log/rev-parse` (all read-only), `tools/check_domain_assertions.py`. Two independent hash implementations cross-checked on every critical value.
- **Evidence sidecars:** `evidence/s1_carrier.json`, `s1c_carrier.json`, `s1d_region_resolve.json`, `s2_transcription.json`, `s5b_resolve.json`, `s8_historical.json`, `rem79_run.json`, `rem79_run.txt`, `crossrepo_batch.json`. (A broad auto-extraction pass `s5_fabrication.py` timed out and produced no sidecar; its scope was superseded and fully covered by `s5b_resolve.json` + the targeted named-file checks — no claim rests on it.)

## REM-79 自查记录 (self-check of this report)
Ran the REM-79 checker mentally over this report's universal claims: each ("286/286", "14/14", "435 all false", "0 violations", "8 hits / 0 true positives", "110 files") carries an inline count/domain or a named scope, per REM-79. No bare unbounded universal asserted.

---
**独立审查员（owner 令）AUDIT-INTEGRITY / N=1**
*Signature = this report + `audit_report.sha256` sidecar + `evidence/` re-hash outputs. Not an implementer; no product repo touched; no self-signed acceptance of any card.*
_End of independent audit._
