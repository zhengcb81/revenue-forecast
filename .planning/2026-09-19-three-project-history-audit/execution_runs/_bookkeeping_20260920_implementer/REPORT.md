# Bookkeeping completion + documentation cleanup (implementer), 2026-09-20

Role: **implementer**. This pass only transcribed verdicts that the independent reviewer
had already written, and cleaned up documentation defects that were already registered.
It added no acceptance anywhere and signed nothing.

Scope discipline actually observed:

* Production repositories `company-wiki`, `revenue-forecast`, `filing-fetch`: **zero
  writes**. This pass never ran `git add/commit/restore/stash` and never ran a command
  with a production repo as its target.
* `<PLAN>\reviews`: **not written** (read-only).
* No network access.
* Files written: the 14 `handoff.json` under Task A, the 4 `review.md` + 4 `handoff.json`
  under Task B, the per-card `recovery/` archives, and this work directory.

Cards that were explicitly off-limits (M01-M07 except where Task B required it, I-00-A,
I-07-A, I-08-A, I-15-A, I-04-C, M08) were **not** touched by Task A. When Task B
required a `review.md` change for M05-M08, it removed only the duplicated r2 section:
one heading removed, zero words rewritten, zero verdicts touched.

Reproduce the self-check with:

```
python selfcheck.py <PLAN_ROOT>
```


## Task A - 14 cards, bookkeeping only

Every card below had a reviewer-authored `accepted_scoped` already written in its
own `review.md`. Only the two bookkeeping fields were brought into line.

| card | reviewer verdict located at | verbatim reviewer text | handoff.json `status` line | `reviewer_status` line | sha256 before | sha256 after |
|---|---|---|---|---|---|---|
| I-00-B | `review.md:3` | `## 结论：accepted_scoped` | L4 | L34 | `c9668074e1a88f18267e967c1cbfd0b43d685ed33dc238790696432f91707422` | `73ca3c169ba27a8401446f8e8dbe6d92ec281a19f3c762cf22c0053287a3e529` |
| I-00-C | `review.md:3` | `**结论：accepted_scoped**` | L4 | L48 | `7dc779847a6cff969bc8e0ad9372c61b4fdaa489d915148efab2ebab6dbce749` | `0f0375c54ed88a9c39502214c5803500816f811374185a84b14cf4e55169482f` |
| I-00-D | `review.md:3` | `## 结论：accepted_scoped` | L4 | L39 | `a061a1a0828401f5ead2e2840e862f9d0243902575d6b64072ca2ffcba6bf05a` | `e497008a0aeafcd75b58e9d59b749d6f1cc85546a1fc340a021e06a2b5966a77` |
| I-01-A | `review.md:3` | `结论：**accepted_scoped**（附 3 项记录性发现均非阻断）` | L4 | L52 | `b9bd82e7ff2e70bc23d208c4c2c5e429851f805e0fa25e6d80e470c0471fdd3b` | `cb043c33b2cfb6e9adf22ae8bda674794844a9e37dc97d2c934d4c59fda4e89a` |
| I-02-A | `review.md:3` | `结论：**accepted_scoped**` | L4 | L5 | `7a2b49006fa40144274174046496122552aab5d084583a6c9360f4aa95d0d4ba` | `b145360f646aa65671c2d097a50b8f31ba8a3acdb0c7274ab8933f676e5982c0` |
| I-02-B | `review.md:3` | `## 结论：**accepted_scoped**（限定范围内接受。见末尾限定申明）` | L4 | L5 | `8818038f97cd753e05d5e6fac5162022c346bab52d30bce76ad7d78efbe8f503` | `df54d76cc67226d432280effaa690dcd1e13e0d4b6f4201d2193fe4265fcc870` |
| I-02-C | `review.md:5` | `## 结论：accepted_scoped` | L4 | L5 | `251494d10cbd59e607f7ed3316a6b9e76e9c9463e0de34ad991bb7433a1c67a6` | `71f3f153511363f34081cdd6bd5fca67749315b081810ac5c406adc4c6ba472b` |
| I-02-D | `review.md:5` | `## 结论：**ACCEPT**` | L4 | L5 | `5e2d017cbf0559be8425bd3b6d0f04bfcdb4c33e9b6bff10b5744be5e43b6ff9` | `01a1c0060ae35a98be1ac843fb5ce2e65581de9d4daf553c1cc8d8d120389b35` |
| I-02-E | `review.md:5` | `## 结论：accepted_scoped` | L5 | L8 | `a73e8810311636486446904245594387d2fbd80c35666135d12300b3385cdabb` | `15b18198c4a3d28a97c19637c8d9dfd0534daf9634dba11240bafcad7990189f` |
| I-03-A | `review.md:5` | `- **结论：accepted_scoped**（复签、,无未定格需要否决、见 §8 保留意见与 §9 限定）。` | L5 | L51 | `4aac103bcdf9ef4d8178e0a16510af853b7e6057f70c098fbba44519cc5906f9` | `8c2572a8b02319e9c85914766da945d096dc74f3c1687e538c06e88f046d6be4` |
| I-03-B | `review.md:5` | `- **结论：accepted_scoped**。` | L5 | L85 | `6da0a23077ab2aeb99ade9e318e1f36aafb3882412d005f8fe54258755bad9a4` | `8f451a67d26562095b6f92674d05f8cdcfcab87574dc24b6e58b1ae7b9ae77a1` |
| I-03-C | `review.md:5` | `- **结论：accepted_scoped**。` | L5 | L89 | `2b933f32eba0ede28f8e4aa6855d6e9e7746764f82233ce4fe4dba7fa334d4c8` | `2e67e910b5a67bc07502316d818feb46129584ee6f3e26fb2a4a95cd2d44fe70` |
| I-03-D | `review.md:5` | `## 结论：accepted_scoped` | L5 | L95 | `551ec8da16497cceed1658de63a5daa887f25bf29752abb5809b6bb59b835999` | `e323da7dd77e4a64defcf7cf5c377aaaa507dc90edf85f9ebed708ea436e4176` |
| I-14-A | `review.md:233` | `## r3 re-read - P4/P5 closed, N2 fixed, and one reviewer error NOT carried forward (APPEND-ONLY)` | L4 | L30 | `c5ba34d716f3cd1cdb0722c8d736b86b302949d0e2c3d9db4e110d6cf012a0c3` | `ae0d2e137102fa8983d17798e9134f159b108834892395686247321356c39242` |

### Task A - what exactly changed in each file

**I-00-B** (`review.md:3` -> `handoff.json` L4 / L34)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "## 结论：accepted_scoped". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-00-C** (`review.md:3` -> `handoff.json` L4 / L48)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "**结论：accepted_scoped**". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-00-D** (`review.md:3` -> `handoff.json` L4 / L39)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "## 结论：accepted_scoped". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-01-A** (`review.md:3` -> `handoff.json` L4 / L52)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "结论：**accepted_scoped**（附 3 项记录性发现，均非阻断）". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-02-A** (`review.md:3` -> `handoff.json` L4 / L5)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending (independent reviewer must verify against review_and_handoff.md; implementer does not self-accept)`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "结论：**accepted_scoped**". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. JSON HYGIENE: this file carried TWO "reviewer_status" keys (handoff.json:5 and handoff.json:70, with different values) - a duplicate key, which makes the file ambiguous to ordinary JSON parsers. Both old values are preserved verbatim in reviewer_status_merged_history and the duplicate at line 70 was removed, leaving exactly one reviewer_status key. No other field changed. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-02-B** (`review.md:3` -> `handoff.json` L4 / L5)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending (independent reviewer must verify per review_and_handoff.md; implementer does not self-accept)`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:3: "## 结论：**accepted_scoped**（限定范围内接受；见末尾限定申明）". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-02-C** (`review.md:5` -> `handoff.json` L4 / L5)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `review_pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "## 结论：accepted_scoped". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-02-D** (`review.md:5` -> `handoff.json` L4 / L5)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `review_pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "## 结论：**ACCEPT**". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. VOCABULARY NOTE: the reviewer's own word at review.md:5 is `ACCEPT`, which is NOT one of the plan's four verdict words (accepted_scoped / changes_required / blocked / not_applicable_with_reason). This ledger field records `accepted_scoped`; normalizing the reviewer's word is pending the reviewer's own confirmation (vocabulary_normalization_pending_reviewer_confirmation: true). The implementer did not edit review.md and did not reword the reviewer; review.md:5 still reads ACCEPT. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-02-E** (`review.md:5` -> `handoff.json` L5 / L8)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending (independent reviewer must read evidence; implementer cannot self-accept)`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "## 结论：accepted_scoped". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-03-A** (`review.md:5` -> `handoff.json` L5 / L51)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `review_pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "- **结论：accepted_scoped**（复签，无未定格需要否决；见 §8 保留意见与 §9 限定）。". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-03-B** (`review.md:5` -> `handoff.json` L5 / L85)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `review_pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "- **结论：accepted_scoped**。". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-03-C** (`review.md:5` -> `handoff.json` L5 / L89)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `review_pending`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "- **结论：accepted_scoped**。". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-03-D** (`review.md:5` -> `handoff.json` L5 / L95)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `pending review by independent reviewer; do not inherit PASS beyond scope`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:5: "## 结论：accepted_scoped". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

**I-14-A** (`review.md:233` -> `handoff.json` L4 / L30)

* `status`: `review_pending` -> `accepted_scoped`
* old `reviewer_status` value preserved verbatim under `reviewer_status_before_bookkeeping_fix`:
  `r1 accepted_scoped for the isolated fix; the r2 correction pass itself (new E5b evidence, oracle section 9 and review.md r2 errata) is un-reviewed and needs a spot-check; D1/D2/D3 remain unsigned`
* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\uXXXX` escapes):
  `accepted_scoped - verdict written by the independent reviewer in review.md:233: "## r3 re-read — P4/P5 closed, N2 fixed, and one reviewer error NOT carried forward (APPEND-ONLY)". Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not sign acceptance. r3 RE-READ CONFIRMED: review.md:235 states that the r3 re-read "confirmed accepted_scoped" for this card, closed P4 and P5, and withdrew the reviewer's own mid-course P4 misjudgement. That r3 section (review.md:233-263) was written by the reviewer as APPEND-ONLY. Promotion remains blocked - see promotion_blocked in this file: D1/D2/D3 are unsigned, so accepted_scoped is the reviewer's qualification of the ISOLATED measurement fix only, not a promotion. NEXT REVIEWER ACTION REGISTERED, NOT WRITTEN BY THE IMPLEMENTER: if a reviewer-authored r3 re-read block is wanted inside review.md, the reviewer must add it; the implementer did not author one and did not sign anything. The reviewer reviewed the scope stated in that section; the implementer changed no verdict word and no scope, and this transcription transfers no qualification beyond what the reviewer wrote.`

### Task A - pre-edit copies

Each card keeps a byte-identical pre-edit copy of its `handoff.json` at
`<PLAN>\execution_runs\<CARD>\a20260919-01\recovery\handoff_pre_bookkeeping.json`.

* `I-00-B` was changed by ANOTHER session between the audit snapshot (03:50:39) and this
  pass: its `status` had already been set to `accepted_scoped` at 03:57:36. The
  audit-snapshot bytes are preserved at
  `recovery\handoff_pre_bookkeeping_audit_snapshot.json` (sha256
  `2f444453d32c436095dc6a24063974033384f164cdd6df0258794f4912c686ba`) and
  `recovery\handoff_pre_bookkeeping.json` was re-anchored to the live bytes
  `c9668074e1a88f18267e967c1cbfd0b43d685ed33dc238790696432f91707422` before editing.
  This pass therefore only had to fix the `reviewer_status` field on that card.
* `I-02-A`: the duplicate `reviewer_status` key at `handoff.json:70` was removed after
  BOTH old values were preserved verbatim in `reviewer_status_merged_history`; the file now
  has exactly one `reviewer_status` key.
* `I-02-D`: `review.md:5` reads `ACCEPT`, which is not one of the plan four verdict words.
  The ledger records `accepted_scoped` and carries
  `vocabulary_normalization_pending_reviewer_confirmation: true`. `review.md` was NOT edited.
* `I-00-D`: the stale `next_action` ("reviewer reads diff and signs review.md") was
  corrected, with the original kept verbatim in `next_action_note`.
* `I-03-D`: `blocked_by` was not touched (out of scope).
* `I-14-A`: handled in ledger form. `status` -> `accepted_scoped`;
  the old `reviewer_status` is kept under `reviewer_status_at_r2_20260920T0350`; a
  `reviewer_status_ledger` records r1 / r2 / r3; `review.md` was NOT edited, and
  "the reviewer should add its own r3 re-read block" is registered as a NEED, not written.

## Task B1 - duplicated r2 section merged in M05/M06/M07/M08 `review.md`

The section `## revision r2 - response to the independent review` appeared twice in each
file with identical wording. The FIRST copy was kept; the SECOND copy plus the `---`
separator that followed the first was removed. No word was rewritten.

| card | kept (1-based) | removed (1-based) | removed lines | sha256 before | sha256 after | verbatim archive |
|---|---|---|---|---|---|---|
| M05 | 122-140 | 140-157 | 18 | `d2d75766533fae4b62256ad101e54d8a817b6addbf1dbefcd317b0daa720d33d` | `f4b1bc9db534600d1b3053f9e229f30d68e812efe28d6a45c07d2f61b7dfb7de` | `recovery\review_md_r2_duplicate_removed.txt` |
| M06 | 118-137 | 137-155 | 19 | `832dd44673cb848a47139b125a465ac90f91486fd596ae4b45dba66ced72c6bb` | `5696c74cf2541ac5eb7947654aa7d26cf1940cd7fe52e46f5bc6d650afe3373c` | `recovery\review_md_r2_duplicate_removed.txt` |
| M07 | 117-136 | 136-154 | 19 | `ff9b5e8eabd1614d900540236dbf0b23795ca8dd42180c804e1c8d0b32899cbc` | `d8b9ec92c3d7f91c476c98785a4c34cd93a250bf343dee3c749060d502dd1130` | `recovery\review_md_r2_duplicate_removed.txt` |
| M08 | 121-144 | 144-166 | 23 | `ebd45b13fcfac510f65756ca62819cf202cecae07377d6e1768d2beac8115901` | `d00331cbe001caebb6ffbb6b485357a8d79b13c2371b555f6ae10d52d09b164c` | `recovery\review_md_r2_duplicate_removed.txt` |

The removed bytes are archived verbatim, each with a header line naming the source line
range, in the card `recovery/` directory listed above. `oracle.md` was NOT touched
(its own duplicate section was already folded by an earlier pass, F-M08-06).

## Task B2 - the un-reproducible reviewer snapshot claim in M05-M08 `handoff.json`

The four files claimed the reviewer verified `oracle.md` hashes against snapshot
directories `copy/` and `copy_r2/`. A full recursive search of the PLAN tree returns
**zero** hits for any `copy`, `copy_r2` or `copy_r3` directory anywhere: the reviewer
snapshots were never retained on disk, so that verification is not reproducible.

| card | `reference_states` now at | sha256 before | sha256 after | pre-edit archive |
|---|---|---|---|---|
| M05 | L177 | `34c4a3f0bd6a01b4ac86e7d2bef7354053bb1b6441c656ca3c726c895b75b46b` | `46cb0a0592fe016966f5deac23f4065f9551634f992cece9e126aaa4cda94c15` | `recovery\handoff_pre_reference_states_fix.json` |
| M06 | L177 | `9bfb05ef5891dccb266847ceddc46c0a464ca84b785e1dbd3633e7b6fdbc6aeb` | `ba62d26611fb981eeffe57bcf43ca4701f8405da2ad575317fc6f390c4e1eb97` | `recovery\handoff_pre_reference_states_fix.json` |
| M07 | L177 | `4cba1d4c45389e8ef735c401ab0e68715f1efb992116c5ff5c7ddd104aeabbbd` | `2f473ab2c3c79183a8feaaf54d29b5e1a5cdb7cb314e8920e51393fed7b26f69` | `recovery\handoff_pre_reference_states_fix.json` |
| M08 | L226 | `838eefac9304fbdfe785fd66a9844d45db6e6889a6dc184b26cc440c08b46a2b` | `2ea09d4f6d0b4fa616576a3d9806f9f83afa76877e73e4ba1d2d9e51f19de397` | `recovery\handoff_pre_reference_states_fix.json` |

Each block now carries `correction_disposition`, `reproducible_from_disk`,
`retained_reviewer_snapshot_dirs: 0`,
`un_retained_observation_not_reproducible: true`, and both original strings under
`r1_snapshot_claim_pre_correction` / `r2_snapshot_claim_pre_correction`. The claim is
downgraded to an un-retained observation, so nothing in those files can still be read
as reproducible on disk. The files were re-dumped through the JSON encoder: the change
is semantic only and the result is guaranteed to parse with no duplicate keys.

**Correction to the audit report itself.** The audit report also stated that no
`oracle.json` exists anywhere in the PLAN tree. **That is false.** Expected-value files
named `oracle.json` DO exist, for example
`execution_runs\M05\a20260919-01\evidence\M05\oracle.json` and
`execution_runs\M05\a20260919-01\recovery\selfcheck\evidence\M05\oracle.json`.
The `reference_states` correction therefore asserts only the true part: the `copy/` and
`copy_r2/` snapshot directories are absent.

## Task B3 - M01 `revision_history` duplicate entries

**Not done, and nothing was removed, because there was nothing left to remove.** When
this pass read `M01\a20260919-01\handoff.json` (another session had just rewritten it,
mtime 2026-09-20T04:07:38), `revision_history` already held 5 entries and the
byte-identical pairs the audit reported at `:175-178` / `:183-186` and `:179-182` /
`:187-190` were **no longer present**; the file now carries an `r4` entry too.
A programmatic duplicate scan reports 0 byte-identical duplicates.

No archive of removed entries exists for M01, because this pass removed none and will
not fabricate a "removed copy". If the parent needs the audit-time text, it must come
from the audit snapshot or the session record of whichever session performed that edit.

## Self-check

`selfcheck.py` re-parses all 18 touched `handoff.json` files with
`object_pairs_hook` duplicate-key detection, verifies every Task A card ends at
`status: accepted_scoped` with the no-self-signature note present and the old value
retained, verifies the Task B2 correction keys and archives, verifies each M05-M08
`review.md` now has exactly one r2 section while its archive holds exactly one copy,
and scans M01 for duplicates. Result: **ALL CHECKS PASSED**.

## Concurrent writers - what happened after this pass

This plan tree was being edited by several sessions at once. Ten of the fourteen Task A
files were written again by other sessions AFTER this pass finished, so the sha256 shown
in the Task A table above is this pass's post-edit value, not necessarily the current
one. `postcheck.py` re-reads the current bytes and confirms that in **all fourteen
cards** this pass's transcription is still present and exact: `status` is
`accepted_scoped`, `reviewer_status` still carries the transcription string byte for
byte, and the old value is still retained under its preserved key.

* Rewritten after this pass (transcription intact): I-00-B, I-00-C, I-00-D, I-01-A,
  I-02-B, I-02-C, I-02-D, I-02-E, I-03-B, I-03-D.
* Unchanged since this pass: I-02-A, I-03-A, I-03-C, I-14-A.
* `I-00-B` is worth flagging: it was changed by another session BEFORE this pass too
(its `status` was set to `accepted_scoped` at 03:57:36 while the audit snapshot was
taken at 03:50:39), which is why both a re-anchored pre-edit copy and the audit-time
copy are kept for that card.

## Not done / not verified

* No technical verification was redone: no oracle was recomputed, no product command was
re-run, no exit code was re-measured. This pass is bookkeeping and documentation only.
* No verdict was created, changed or withdrawn for any card. In particular, the cards the
audit judged `not_accepted` (I-00-A, I-08-A) and the conditional ones (I-04-C, M01-M07)
were NOT given `accepted_scoped` by this pass.
* `I-02-D` vocabulary normalization is recorded as pending the reviewer confirmation; it
was not decided here.
* `I-14-A` still wants a reviewer-authored r3 re-read block inside `review.md`; it was
registered as a need, not written.
* No `review.md` verdict text was edited anywhere. The only `review.md` edits were the
four duplicate-section removals in Task B1.
* `oracle.md`, `qualification.json` grant states, expectations, thresholds, negative
cases and exit codes were not modified.
* Concurrency: M01, M05, M06, M07, M08 and I-00-B were all being modified by other
sessions during this pass. The cases where that mattered are documented above.

