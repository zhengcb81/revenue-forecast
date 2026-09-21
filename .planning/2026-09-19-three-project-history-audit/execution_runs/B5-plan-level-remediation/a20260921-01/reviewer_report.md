# Independent reviewer report — card **B5+B6** (REM-21 cross-batch runner propagation + REM-22 rc code table freeze)

* Reviewer role: **independent reviewer** (not the implementer, not the orchestrator)
* Plan: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
* Attempt under review: `<PLAN>\execution_runs\B5-plan-level-remediation\a20260921-01`
* Reviewer scratch (new files only): `<ATTEMPT>\_reviewer_verify\`
* Mode: read-only on all historical artifacts; **no production writes**; **no historical file modified**

---

## 0. VERDICT

**NOT ACCEPTED AS-IS — "measured core verified / 3 blocking findings".**

Returned to the implementer (not self-signed; this card stays `review_pending`).

| Area | Ruling |
|---|---|
| **REM-22 rc-table freeze** | **PASS.** Pure append proven independently: current file is byte-prefix-identical to the recorded PRE image (`1bdfbd91…`, 9895 B — which is exactly the `post_sha256` of the owner-authorized T1-19 rc-table freeze, `T1-19\a20260920-01\handoff.json:18`) with 0 deleted lines and all 10 frozen anchor lines intact. |
| **REM-21 four-arm propagation** | **PASS (measured).** E=0 / F=3 / G=2 **uniform on all six batches and all 31 cards**. Arm B is a genuine measurement and is *not* uniformly 0 (0 / 2 / 3 across batches). I independently reproduced all four arms of one full batch. |
| **"missing `expected` ⇒ rc=3" falsification** | **PASS.** Reproduced on the unpatched runners: raw **rc=1**, uncaught `KeyError: 'expected'`, **zero files written**. The registered rc=3 claim is indeed false. (One caveat, F-4: on M25-M28 the same experiment yields rc=1 by the set-level gate, not by `KeyError`.) |
| **ValueError decoy** | **PASS.** Real code; measured `is_target_type=true` **and** `declared_expectation_ok=false` in the same record. No `isinstance()` on the raised-vs-declared path; no rc constant renumbered in any of the six copies. |
| **Boundaries** | **PASS.** 68/68 historical runner copies byte-unchanged (67 under `M01..M31` + the `iso\` baseline; all 8 batches internally byte-consistent), 31/31 frozen `cases.json` byte-unchanged, 37323/37323 files under `execution_runs\M01..M31` untouched (`git status --porcelain` empty), production `scripts\` untouched. |
| **Premise corrections** | **BOTH CONFIRMED.** `5307d2cc…` is on no file on disk; M09-M12 and M21-M24 already gate on exact type-name. |
| **G1 / G2 (M25-M28)** | **FORCED — but not resolvable by the implementer.** The deviation is *necessary*, the chosen resolution is *not the only* one, and it silently re-semanticises a frozen rule text. **Owner sign-off required.** |
| **G3 (key rename)** | **CONFIRMED — hard breakage proven.** `M14\...\recovery\consolidated_report.py:75` reads the old key path and will `KeyError`. **Blocking.** |
| **G4 (rc=2 wording)** | **ADJUDICATED.** "a negative case correctly rejected" is a **per-case** statement; a run that correctly rejects all negatives is **rc=0** (measured on 31/31 frozen runs). The per-run rc=2 clause is the "no verdict is produced at all" clause. |

**Blocking findings: F-1 (G3 key rename), F-2 (G1/G2 frozen-rule override without owner sign-off), F-3 (`evidence.json` schema divergence on M13-M16).**

---

## 1. Claims verified independently

### 1.1 REM-22 — the rc table appends are pure

Measured directly against the bytes on disk (my own code, not the implementer's script):

```
current  execution_v2/START_HERE.md   sha256 a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf   18 452 B
prefix   bytes [0, 9895)              sha256 1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835   ( == recorded PRE )
         prefix ends at a line boundary: true
suffix   bytes [9895, 18452)          8 557 B, 108 newlines
```

* Prefix hash reproduces the value the attempt records as PRE. **Provenance independently located:** `1bdfbd91…` is exactly the **`post_sha256`** recorded at `execution_runs\T1-19\a20260920-01\handoff.json:18` (and re-asserted in that card's `t19_rc_table_verification.json`) — i.e. the state of `START_HERE.md` *after the owner-authorized T1-19 rc-table freeze*. This is the decisive check: it proves the current file is **the frozen rc table's own post-image plus a suffix**, with not one byte of the frozen region altered. This is a stronger result than the attempt claimed for itself, and it is the strongest form of the append-only property available: the baseline is not merely "some earlier version", it is the frozen artifact itself.
* `108 = 74 + 34` and `8 557 = (16 314 − 9 895) + (18 452 − 16 314)`: the "+74/−0 then +34/−0" decomposition is arithmetically exact.
* **All 10 frozen anchor lines intact** — I verified each verbatim string against both the current file and the 9 895-byte prefix: the section heading, `**冻结码表（本包唯一规范值）**`, the `| rc | 含义 | 判据 |` header, the separator, all four rc rows, `**已知的历史偏差（只登记、不回改）**`, both legacy-bias bullets, the `expected`-classification paragraph and the "历史 rc 与其证据**一律不动**" sentence.
* The appended region repeats two table-header lines (`| rc | 含义 | 判据 |`, `|---|---|---|`) inside the new **re-assertion** section (lines 156-161). That is a *new* table, not a modification of the old one — the old rows are byte-identical in the prefix. Registered as an observation, **not** a defect.
* *Minor:* the implementer's own `scripts/verify_append.py` `orig_table` list has **9** entries, two of which are the same string (line 115 is tested twice), so its `frozen_original_lines_all_intact` is a weaker check than the "10 frozen anchor lines" phrasing suggests. The real coverage is fine — I verified 10 distinct lines independently — but the script's list should be corrected.

Append 2's headline correction is itself correct (see §1.4), so the erratum is a truthful addition.

### 1.2 Measured rc reality — citations confirmed

Every `file:line` citation in the appended registry was read back from the historical bytes:

| batch | registry claim | verified |
|---|---|---|
| M01-M04 | 0 / 2 / 3, **rc=1 missing** | `M01/.../run_card.py:251-255` — `if harness_incomplete: exit_code = 2 elif verdict=="pass": 0 else: 3`. **No `return 1`, no `EXIT_HARNESS`.** Confirmed. |
| M05-M08 | 0 / 2 / 3, **rc=1 missing** | `M05/.../run_card.py:299-304` — same shape. Confirmed. |
| M09-M12 | `EXIT_PASS=0/EXIT_HARNESS=1/EXIT_NO_VERDICT=2/EXIT_NEGATIVE=3` | `:48-51` verbatim. Confirmed. |
| M13-M16 | `RC_PASS=0/RC_HARNESS=1/RC_NO_VERDICT=2/RC_NEGATIVES=3` | `:62-65` verbatim. Confirmed. |
| M17-M20 | `EXIT_*` 0/1/2/3 | `:69-72` verbatim. Confirmed. |
| M21-M24 | 0 / 2 / 3, **rc=1 missing** | `:384-389` — same shape. Confirmed. |
| M25-M28 | 0 / **1** / 2 / 3, rc=1 real | `:418-423` (0/2/3 table) **plus** `:168 return 1` (whole-set `case_contract` gate) **plus** `:466 return 1` (unguarded-harness `except`). Confirmed — this batch really is the odd one out. |
| M29-M31 | `EXIT_*` 0/1/2/3 | `:59-62` verbatim. Confirmed. |

The "M01-M04 / M05-M08 / M21-M24 have `rc=1` unreachable in this family; M25-M28 has a real rc=1" distinction is **correct** and is the registry's most useful single output.

### 1.3 Per-batch propagation — one batch re-run from scratch by me

I wrote my own arm harness (`_reviewer_verify\run_arms_m0508.py`), built my own scratch roots, copied the historical `input.json`/`oracle.json`, applied the contract's mutation rule myself (`first negative case whose frozen expected is "ModelRegistryError"` → **NEG-CARD**), and read the raw process exit codes:

| arm | runner | cases.json | M05 | M06 | M07 | M08 | verdict |
|---|---|---|---|---|---|---|---|
| **E** | new | frozen | **0** | **0** | **0** | **0** | `pass` |
| **F** | new | `expected` → `"ValueError"` | **3** | **3** | **3** | **3** | `fail`, `declared_expectation_mismatch=1` |
| **B** | byte-copy historical | same as F | **0** | **0** | **0** | **0** | `pass` — the fabricated green |
| **G** | new | `expected` key deleted | **2** | **2** | **2** | **2** | `no_verdict`, `cases_json_declared_expectation_missing:NEG-CARD` |

**E=0, F=3, B=0, G=2 confirmed on all four cards.** The implementer's recorded values for M05-M08 are exactly right, and my F-arm record shows the decoy predicate in the raw output:

```
"id": "NEG-CARD", "expected": "ValueError", "declared": "ValueError", "raised": "ModelRegistryError",
"is_target_type": true, "declared_expectation_ok": false, "declared_expectation_mismatch": true,
"verdict": "FAIL_declared_expectation_mismatch"
```

For the other five batches I verified the recorded rc values against the **raw artifacts in the implementer's own scratch** (the `exit_code` embedded in every `out_*.json` / `run_result.json`), per card:

```
M09-M12   E=0/0/0/0   F=3/3/3/3   B=3/3/3/3   G=2/2/2/2
M13-M16   E=0/0/0/0   F=3/3/3/3   B=2/2/2/2   G=2/2/2/2
M21-M24   E=0/0/0/0   F=3/3/3/3   B=3/3/3/3   G=2/2/2/2
M25-M28   E=0/0/0/0   F=3/3/3/3   B=<no output JSON, by construction>   G=2/2/2/2
M29-M31   E=0/0/0/0   F=3/3/3/3   B=0/0/0/0   G=2/2/2/2   (+ raw process rc in arm_results.json)
```

All six batches: **E=0, F=3, G=2 uniformly on every card.** Arm B is genuinely non-uniform (0 / 2 / 3), which is the honest outcome the erratum demanded.

### 1.4 "Missing `expected` ⇒ rc=3" is FALSE — reproduced on the unpatched bytes

I ran the **byte-copy historical runner** (`run_card_before.py`, sha256 equal to the historical file) on a `cases.json` with NEG-CARD's `expected` key deleted — real child processes, raw rc:

| batch | runner | deleted key | raw rc | files written | stderr |
|---|---|---|---|---|---|
| M05-M08 (M05) | historical copy | `NEG-CARD` | **1** | **0** | `KeyError: 'expected'` |
| M09-M12 (M09) | historical copy | `NEG-CARD` | **1** | **0** | `KeyError: 'expected'` |
| M25-M28 (M25) | historical copy | `NEG-CARD` | **1** | **0** | `cases whose \`expected\` is not 'ModelRegistryError': ['NEG-CARD']` |

The registered rc=3 claim is **falsified**. Two distinct mechanisms produce rc=1, and the implementation's append 2 registers only the first:

* **M05-M08 / M09-M12** (and, by the same hard-subscript pattern, the other no-`case_contract` batches that index `case["expected"]` directly) → uncaught **`KeyError`**, **no evidence files at all**. Exactly as claimed.
* **M25-M28** → a third mechanism: its **whole-set `case_contract` gate** compares with `case.get("expected")`, so a *deleted* key becomes `None ≠ "ModelRegistryError"` and trips the **rc=1 abort** (no `KeyError`, no output JSON). Also rc=1 and also no verdict, but by a different mechanism and with a different reason string.

**Finding F-4 (minor):** append 2 says "在**尚未打补丁**的历史 runner 上删除某例的 `expected` 键，得到的**既不是 rc=2 也不是 rc=3**" and then explains it solely as a hard-subscript `KeyError`. That is true for the two batches it tabulates, but **not** the mechanism on M25-M28 — where the same experiment yields rc=1 via the set-level gate. The registry's conclusion (rc=1, not rc=3) survives; the *explanation* is over-general. A one-line addition naming the M25-M28 mechanism closes it.

### 1.5 The ValueError decoy is real code, and no rc constant was renumbered

* In all six patched copies the **only** `isinstance()` calls on the `expected`/`declared` path test whether the declaration *is a non-empty string* (`isinstance(declared, str) and declared.strip()`); the comparison itself is exact type-name equality in every copy:
  * M05-M08 `:299` `declared_ok = (entry["raised"] == declared)  # exact type-name equality`
  * M09-M12 `:499` via the pre-existing `raised_matches_expected_name`
  * M13-M16 `:530` `declared_ok = (raised_name == declared)`
  * M21-M24 `:377/:381` `expected_type_matches_raised` then `declared_ok`
  * M25-M28 `:420` `raised_name = type(exc).__name__`
  * M29-M31 likewise
* **No rc constant was renumbered.** Diffing every `EXIT_*`/`RC_*` assignment and every `return <int>` literal between each `run_card.py` and its `run_card_before.py`: **zero differences in all six batches.** The `"exit_code": N` literals inside the result dicts are also identical sets before/after.
* The F-arm measurement shows `is_target_type=true` **and** `declared_expectation_ok=false` in the same case record, so an `isinstance`-based comparison would demonstrably have passed it. **The decoy discriminates.** Confirmed.

### 1.6 Boundaries

| claim | measurement | ruling |
|---|---|---|
| 68/68 historical runner copies unchanged | Exact census: **67** `run_card.py` under `execution_runs\M01..M31` (31 `a20260919-01\scripts\` + 12 `recovery\selfcheck\scripts\` + duplicates: M09-M12 carry 6 each) **plus** the 68th, the frozen-baseline copy at `execution_runs\M05-M08\a20260919-01\iso\run_card.py`. **All 8 batches internally byte-consistent, every card equal to the sha256 bound for its batch** (`b5fcc685…` / `fd3a11c9…` / `997c553b…` / `9e4a6450…` / `94619a98…` / `a5ee7599…` / `eab01162…` / `9ea69c72…`), and all six attempt-dir `run_card_before.py` copies byte-equal to their historical file. | **PASS — the "68/68" figure is accurate** (it silently assumes the `iso\` baseline; worth stating explicitly) |
| 31/31 frozen `cases.json` unchanged | 31 files found; all 347 cases declare exactly `ModelRegistryError`; 0 compound, 0 missing, 0 non-string. Per-card counts (11/11/13/15 for M01-M04, 11 elsewhere) match the frozen files. | **PASS** (also independently re-derives the book's 347-case figure) |
| 0 of 37 323 historical files touched | `Get-ChildItem -Recurse` under `execution_runs\M01..M31` = **37 323**. `git status --porcelain` over those 27 card directories = **0 lines** (clean). | **PASS** |
| production anchors intact | `scripts\` has no `git status --porcelain` output; the isolation code root still hashes `model_registry.py 9ec65295…` / `model_extensions.py 9939480b…` = identical to the production files; `scripts\` mtimes all ≤ 2026-09-20 16:34, before this card. | **PASS** |

### 1.7 Premise corrections

* **`5307d2cc…` matches no file on disk — CONFIRMED.** Hashing **all 74** `run_card.py` files under `execution_runs` (14 distinct hashes): **zero** start with `5307d2cc`. `94619a98f5761752…` matches exactly 8 paths — `M17..M20\scripts\run_card.py` and `M17..M20\recovery\selfcheck\scripts\run_card.py`. The only two occurrences of the literal `5307d2cc` in the whole plan tree are **inside the append this card wrote** (`START_HERE.md:182,189`) plus the four `M17 review.md` lines (`:162/:232/:261/:339/:348`) where it is recorded as a superseded r2-generation value. **`94619a98…` is the correct authority.**
* **"M17-M20 is the only batch comparing `expected`" is OVERSTATED — CONFIRMED.** `M21/.../run_card.py:304` computes `expected_type_matches_raised` and **`:312-313` gates the verdict** (`elif not entry["expected_type_matches_raised"]: verdict = "FAIL_expected_type_mismatch"`). `M09/.../run_card.py:427` computes `raised_matches_expected_name` and **`:430-431` gates** (`elif is_target and entry["raised_matches_expected_name"]: PASS_rejected`, with `:432-433` the failing branch). Both gate by exact string equality, not `isinstance`. The owner's "four batches" **count** happens to match, but the **labels** do not: of the six authorized batches, only **four genuinely lacked a per-case gate** (M05-M08, M13-M16, M25-M28, M29-M31) and **two already had one** (M09-M12, M21-M24). The attempt's `evidence/ast_gate_analysis.json` correction is right, and the retraction of the unreliable `compares_raised_to_expected` flag (false for all 8 batches, including the reference) is a correct call.

---

## 2. Adjudications

### G1 — M25-M28 whole-set `case_contract` gate split

**Question put to me:** is the split FORCED by the owner's own criterion ("every batch gains a 改 `expected` ⇒ rc=3 arm")? Accept, or require a different resolution?

**Ruling: the *deviation* is FORCED; the implementer's particular resolution is NOT the only compliant one, and it must not be accepted without owner sign-off.**

The conflict is real and I verified every leg of it:

1. `execution_runs\M25..M28\...\cases.json` `case_contract.rule` (frozen, byte-unchanged, all four cards) says verbatim: *"every case's `expected` must equal declared_expected_exception and the id list must equal expected_ids, otherwise the harness refuses to issue a verdict (rc=1)"*.
2. The historical runner implements exactly that (`run_card_before.py:140-168`, `if contract_problems: ... return 1`), **and I measured it**: arm B = **rc=1**, stderr `cases whose 'expected' is not 'ModelRegistryError': ['NEG-CARD']`, **no output JSON at all**.
3. Therefore, on M25-M28 the owner-mandated arm F ("改 `expected` ⇒ rc=3", `OWNER_DECISIONS.md:214` T1-8) is **impossible** while that rule binds. The implementer's `open_issues` entry is correct: the mutation trips a pre-judgement gate, so a per-case rc=3 can never be reached.
4. T1-11 (`OWNER_DECISIONS.md:217`) says `case_contract` and `scripts/run_card.py` are an **interlocked pair** and changing either requires a full re-run and re-freeze as a new rN — and it says **不授权** (no re-freeze). So the frozen `rule` text cannot be edited.

So a deviation is the only way through. **But** the implementer chose to demote the set-level violation to **fully non-gating** (`set_level_declaration_violations` is recorded but drives nothing), while keeping the *frozen artifact* declaring rc=1. The net effect is a frozen file that now lies about its own runner — the implementer names this honestly ("that sentence is now saturated by this patch's behaviour"), and I give credit for disclosing it, but disclosure does not resolve it.

**There is a strictly better resolution that is also compliant and that I verified is reachable:** classify the set-level declaration violation as **rc=2 (no verdict)** rather than silently dropping it. The frozen table — the artefact the owner *did* freeze, T1-19 — makes this the *correct* mapping, and it shows the frozen `rule` text's "rc=1" is the outlier:

* rc=1's judgement text is *"测试/运行器自身出错：导入失败、夹具错误、期望文件缺失、路径未绑定"* — runner/infrastructure faults. A per-case declaration that disagrees with the set-level declaration is **none of those four**.
* rc=2's judgement text is *"或该命令不产生裁决"* — precisely what the historical gate does: it refuses to issue a verdict.
* The reference implementation agrees: `M17/.../run_card.py:540-544` maps *declaration* problems to `EXIT_NO_VERDICT` (2), not 1.

The implementer already uses exactly this reason namespace (`cases_json_declared_expectation_missing:<ids>` → rc=2). Routing the set-level disagreement to the same rc=2 class costs nothing, keeps a *reported* gate instead of a *dead* one, and satisfies every frozen artefact except the literal "rc=1" string — which is unsatisfiable anyway.

**Required action (choose one):**
* **(G1-a, preferred)** Keep the structural rc=1 abort; map the whole-set declaration violation to **rc=2 + `no_verdict`** (reason namespace extended to cover disagreement as well as absence), and record the frozen rule's "rc=1" as superseded-by-the-frozen-rc-table at the layered-priority level. Then arm F (per-case mutation ⇒ rc=3) and arm G (deleted key ⇒ rc=2) both exist and both are honest. **No frozen file is edited.**
* **(G1-b)** Keep the patch exactly as it is and obtain an explicit **owner sign-off** on the record that a frozen per-batch rule text is overridden by the frozen rc table, i.e. an owner-level ruling that the rc table outranks `case_contract.rule`. Without that sign-off the package cannot be accepted: the divergence is invisible to anyone who reads the frozen `cases.json` and trusts it.

Either way, the deviation must be surfaced to the owner as a **TIER-1 decision**, not absorbed at card level.

### G2 — anchor conflict inside a frozen artifact

**Ruling: there is NO fully compliant resolution that satisfies all three constraints; register the conflict as an owner item, and do NOT edit the frozen file.**

The three constraints and their measured states:

| constraint | source | state |
|---|---|---|
| differing `expected` ⇒ harness refuses a verdict, **rc=1** | frozen `M25..M28\...\cases.json` `case_contract.rule` | unchanged on disk (all 4 cards verified) |
| mismatch ⇒ **rc=3** | frozen rc table, `START_HERE.md:102` | unchanged |
| the rc=3 mutation arm is mandatory | T1-8, `OWNER_DECISIONS.md:214` | unfilled for M25-M28 without the split |

Two of the three can be satisfied at once, never all three. Editing `cases.json` is forbidden (T1-11), so the conflict is **structurally unresolvable inside this card**. The implementer's "leave it registered" is therefore the right *shape* of answer.

*Additional observation the implementer did not record:* `case_contract` exists **only in M25-M28** (verified: absent in M05/M09/M13/M17/M21/M29) and on M25-M28 the check uses `case.get("expected")`, so a **deleted** key trips the whole-set gate (rc=1) rather than a `KeyError`. M25-M28 is thus *already* the batch whose "missing `expected`" behaviour conforms to the frozen table's rc=1 (harness failure: "期望文件缺失") — and the implementer's arm G changes it to rc=2. That is required for cross-batch uniformity (T1-19's stated purpose), but it is a second, unregistered semantic change on M25-M28. It should be registered alongside G1.

### G3 — M13-M16 key rename

**Ruling: CONFIRMED, and it is BLOCKING. Emit both keys.**

The contract is explicit: *"Do **not** remove or rename existing fields — downstream evidence files were generated from them."* The rename `expectation_consistency.facts.declared_expectations` → `declared_expectations_in_cases_json` removes the old key, and I proved a **real downstream reader**:

```
execution_runs\M14\a20260919-01\recovery\consolidated_report.py:75
    run["expectation_consistency"]["facts"]["declared_expectations"]
```

A scan of 107 occurrences of `declared_expectations` across the M13-M16 trees found **exactly one** consumer that indexes the old key path — that one. It will raise `KeyError` against the patched output.

Scope, measured precisely (credit to the implementer for the honest disclosure, and M05-M08 did **not** do the same thing — M05-M08's runner has **no** `expectation_consistency.facts` block at all, so there was no key to rename):

* The frozen historical `run_result.json` / `formula_result.json` for M13-M16 **contain** the old key, so any consumer written against frozen output (as `consolidated_report.py` is) breaks.
* Only **one** batch is affected: M13-M16 (the frozen M13..M16 runners all carry the old name at `:206`).

**Required action:** keep `declared_expectations` under its original name and meaning **and** add `declared_expectations_in_cases_json` as the contract-required name (the contract's §2 list is *additive*; it does not ask for a replacement). The implementer's "one key, one meaning, no stale duplicate" reasoning is aesthetically defensible but contractually backwards — the contract anticipated exactly this and forbade it.

### G4 — frozen rc=2 wording ambiguity

**Ruling: it is a per-case statement inside a per-run table. Read rc=2's "预期拒绝" as "no verdict was produced at all"; read "a negative correctly rejected" as contributing to rc=0.**

Measured on the frozen corpus: of all 31 cards' frozen `run_result.json`/`formula_result.json`, the **only** rc value observed is **0**, and in **31/31** of those runs **every negative passed** (`neg_passed == neg_total`). There are **zero** instances of rc=2 with all negatives correctly rejected.

The reading is also forced by the table's internal logic:

* rc=0 = *"命令正常结束，且**业务判定为通过**"*. If a run's whole business judgement is "were the negatives rejected?", then correctly rejecting them **is** the pass ⇒ rc=0.
* rc=3 = *"负例**未被拒绝**"* — the negative outcome.
* If rc=2 also meant "negative correctly rejected", it would collide with both rc=0 and rc=3 for the same observation. A code table cannot have an observation that is simultaneously pass, no-verdict and fail.
* So rc=2's first gloss must describe a **different** kind of command — one whose *purpose* is to check that a rejection happens, but which **issues no verdict** (the table's own alternative: *"或该命令不产生裁决（如只读查询）"*), or the declaration-unusable case the reference implementation actually implements (`M17 :540-544`).

**The attempt's registered reading is CORRECT and I adopt it**: aggregators must not read "negative correctly rejected" as rc=2; the reference implementation emits rc=0 when all negatives are correctly rejected and rc=2 only when the frozen expectation itself is missing/unusable. The appended §4 registration is accurate; per T1-12 the frozen body is correctly left untouched.

---

## 3. Findings

| id | severity | finding | evidence |
|---|---|---|---|
| **F-1** | **BLOCKING** | **G3 rename breaks a real consumer.** `M14\...\recovery\consolidated_report.py:75` indexes `expectation_consistency.facts.declared_expectations`, which the M13-M16 patch removes. Contract §2 forbids renaming. | my scan: 1 reader, `KeyError` on patched output |
| **F-2** | **BLOCKING (owner sign-off)** | **G1/G2: a frozen rule text is silently re-semanticised.** `M25..M28\cases.json` `case_contract.rule` still says a differing `expected` ⇒ rc=1, while the patched runner now emits rc=3 and reports that condition as non-gating. Deviation is forced; the chosen resolution overrides a frozen artefact without owner authority. | frozen `rule` text on all 4 cards; patched `run_card.py:185-212`; measured arm B rc=1 |
| **F-3** | minor | **`evidence.json` schema diverges across batches.** M13-M16's `arms.{E,F,B,G}` block exists but every field is `null`; the real per-arm data lives in `arm_summary_rows` / `arm_rollup`. A machine consumer reading `evidence["arms"][arm]["rc"]` — the shape the contract's own §6 template prescribes — reads `null` for M13-M16 only. | measured: `arms.E.rc is None` for M13-M16, populated for the other five |
| **F-4** | minor | **Append 2's explanation of "missing `expected`" is over-general.** It attributes the rc=1 to a hard-subscript `KeyError`. That holds for M05-M08/M09-M12 but **not** M25-M28, where the same experiment yields rc=1 from the whole-set `case_contract` gate (no `KeyError`, no output JSON). The conclusion (rc=1, not rc=3) is unaffected. | my run: M25 raw rc=1, stderr = the set-level gate message |
| **F-5** | minor | **M25-M28 arm G is a second, unregistered semantic change.** On M25-M28 a deleted `expected` historically produced rc=1 *conforming to the frozen table's* "期望文件缺失"; the patch changes it to rc=2. Required for T1-19 uniformity, but it should be registered with G1 rather than only under the rc-3/rc-1 discussion. | my run vs patched G arm |
| **F-6** | informational | **M05-M08 violated the contract's arm-selection rule.** §5 says "Pick the mutated case as the **first** negative case (lowest `id`)" — that is **NEG-CARD** (first in file order, and lowest ordinal id). M05-M08 mutated **CONT-BREAK**, the *last* case in the file, with no selection-rule justification in its `open_issues` (it registered only that §6's `"N01"` example didn't apply). The finding is robust either way — I re-ran the batch with **NEG-CARD** and got identical E=0/F=3/B=0/G=2 — but the deviation should be declared. Note M21-M24 handled the same ambiguity correctly, testing both readings (arms F2/B2) and proving equivalence. | my run (`target=NEG-CARD`) vs the implementer's scratch (`CONT-BREAK`) |
| **F-7** | informational | `scripts/verify_append.py`'s `orig_table` has 9 entries, one of them duplicated, so its "frozen lines intact" check is weaker than described. Real coverage is fine (I verified 10 distinct lines). | source read |
| **F-8** | informational | The appended §1 table repeats the frozen table's header rows inside a new section. Byte-wise this is a pure append (verified), so it is not a modification — but a reader skimming may mistake the re-assertion for the normative table. | byte check: old rows intact inside the 9 895-byte prefix |

### What the package gets right (recorded deliberately)

* The **erratum culture is working.** §8 of `PROPAGATION_CONTRACT.md` retracts its own §3/§5 predictions after a worker measured arm B = rc=3, and every one of the six batches then reported arm B as a **measurement** rather than fitting it to the prediction. Arm B's non-uniformity (0/2/3) is the direct proof that no value was fudged.
* The attempt correctly **retracted its own unreliable scan flag** (`compares_raised_to_expected` was `false` for all 8 batches including the known-positive reference) and replaced it with an AST analysis carrying a positive and a negative control. That is the right response to the project's recurring "guard that returns false everywhere" family.
* The attempt refused to "fix" the superseded `5307d2cc…` hash and registered it instead.
* The arm-B rc=1 discovery on M25-M28 was escalated rather than hidden, and arm B0/B1 isolation controls were built to separate the three gate families.

---

## 4. Unverified / cannot-vouch list

1. **The POST1 intermediate image does not exist on disk.** `e7cb90fc…` (16 314 B) is a recorded value, not a file I can hash. I proved the *current* file is a pure suffix extension of **PRE**; the "+74 then +34" split rests on the implementer's own `verify_append.py` and is corroborated only by exact arithmetic (108 = 74+34; 8 557 = 6 419+2 138) and by append 2's own distinct heading. **Verdict: verified to the limit of what is on disk, not independently witnessed step-by-step.**
2. **POST1 prefix `[0, 16314)` is trivially true** (current file = POST1 + append 2). The implementer's `append_1_check_vs_PRE` reports 108 inserted lines, which conflates both appends; its own `read_this_correctly` note says so. No defect, but the JSON key naming invites misreading.
3. **Arm runs for M09-M12, M13-M16, M21-M24, M25-M28 were not re-executed by me.** I verified them by (a) reading the rc embedded in each arm's raw `out_*.json` / `run_result.json` per card, and (b) resolving each batch's gate structure from source. Only M05-M08 was reproduced end-to-end with raw process exit codes. Residual risk that a stale artifact was copied into the wrong arm directory is **low but non-zero**.
4. **`negative_results.json` reproduction** — no arm reproduced the `--negative-out` artifact for M09/M13/M29 against the frozen baseline; those flags were passed but the frozen comparison was not redone.
5. **The 4-batch vs 6-batch scope question** — whether M09-M12 and M21-M24 should have been touched at all, given they already gated correctly, is **not mine to rule on**. Their arms show F=3 with a pre-existing gate (and arm B = 3), so the change is a genuine refinement, but the owner's authorization language covers "each batch's own copy" and the scope is an owner call.
6. **`b5_scan.json`'s 347-case and per-batch byte figures** were re-derived by me only for the cases.json side (347 total, all `ModelRegistryError`) — matching. The runner byte counts in the registry table match the files I hashed.

### Boundary disclosure (my own footprint)

My verification wrote **new files only**, into `<ATTEMPT>\_reviewer_verify\` (7 scripts + 5 result JSONs). That directory is inside the attempt directory but under `execution_runs\`. It creates **no** file under any historical card directory, modifies **no** historical artifact (all historical reads were read-only; every child process ran with `-B` and a redirected scratch root), and touches no production path. `_reviewer_verify\` is safe to delete; nothing in it is referenced by any historical artifact. I flag it explicitly so the owner can remove it rather than discover it.

---

## 5. Required before acceptance

1. **F-1 (G3):** restore `expectation_consistency.facts.declared_expectations` in the M13-M16 copy, keeping the new name as an **additional** key; re-run arms E/F/B/G and show the old key present in all four outputs.
2. **F-2 (G1/G2):** either (G1-a) route the whole-set declaration violation to **rc=2 + `no_verdict`** instead of leaving it non-gating, or (G1-b) obtain explicit **owner sign-off** that the frozen rc table outranks the frozen `case_contract.rule`. Register F-5 alongside it.
3. **F-3:** populate M13-M16's `arms.{E,F,B,G}` block to the contract §6 shape (the data already exists in `arm_summary_rows`).
4. **F-4 / F-6:** append the corrected mechanism for M25-M28's missing-`expected` behaviour, and declare M05-M08's arm-selection deviation (or re-run with NEG-CARD, which I have already shown yields identical results).
5. **F-7:** correct `verify_append.py`'s anchor list, and add the 10 verified frozen lines as the check's operand so the "pure append" claim is reproducible from the script alone.

---

## 6. Reviewer independence statement

I am not the implementer and did not author any artifact under review. Every load-bearing number in this report was measured by reviewer-written code executed in this session, against the bytes on disk and against real child processes; no implementer-computed value was accepted without a source-level or byte-level cross-check. I did not self-sign: this card remains `review_pending`.

*Reviewer scratch:* `<ATTEMPT>\_reviewer_verify\` — `run_arms_m0508.py`, `structural_checks.py`, `isinstance_check.py`, `verify_rem22.py`, `test_missing_expected.py`, `g3_readers.py`, `g4_rc2_semantics.py`, `case_declaration_scan.py`, `triangulate.py`, `crosscheck_exitcodes.py`, `aggregate_table.py`, `runner_copy_census.py` (+ `reviewer_arm_results.json`, `structural_checks.json`, `rem22_boundaries.json`, `missing_expected_results.json`).

---

## 7. Report pin (self-excluding)

The pin covers every byte of this file **before** this section. Verify by hashing
`reviewer_report.md[0 : 34071]` -- **not** the whole file: a whole-file hash of a
document that contains its own hash cannot close.

```
payload_bytes  34071
payload_sha256 600c9e7b71ee201b6c10aab2a2ce79705f9449b96ac4535a02d3310a5c49f27d
```

Verification:

```python
import hashlib
raw = open('reviewer_report.md','rb').read()
i = raw.index(b'## 7. Report pin')
print(len(raw[:i]), hashlib.sha256(raw[:i]).hexdigest())
```

*(The implementer should re-verify on receipt; if the two values do not reproduce, the
report has been altered after review and the verdict is void.)*
