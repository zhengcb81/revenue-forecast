#!/usr/bin/env python3
"""Emit REPORT.md for the 2026-09-20 bookkeeping pass, straight from the JSON
result ledgers so no hash or quote is retyped by hand.

Usage:  python write_report.py <plan_root>
"""
import json
import os
import sys

BANNER = """# Bookkeeping completion + documentation cleanup (implementer), 2026-09-20

Role: **implementer**. This pass only transcribed verdicts that the independent reviewer
had already written, and cleaned up documentation defects that were already registered.
It added no acceptance anywhere and signed nothing.

Scope discipline actually observed:

* Production repositories `company-wiki`, `revenue-forecast`, `filing-fetch`: **zero
  writes**. This pass never ran `git add/commit/restore/stash` and never ran a command
  with a production repo as its target.
* `<PLAN>\\reviews`: **not written** (read-only).
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

"""


def load(path):
    with open(path, 'rb') as fh:
        return json.loads(fh.read().decode('utf-8'))


def main():
    plan = sys.argv[1]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')
    a = load(os.path.join(work, 'taskA_results.json'))
    b1 = load(os.path.join(work, 'taskB1_r2_merge.json'))
    b2 = load(os.path.join(work, 'taskB2_reference_states.json'))

    out = [BANNER]

    out.append('## Task A - 14 cards, bookkeeping only\n')
    out.append('Every card below had a reviewer-authored `accepted_scoped` already written in its\n'
               'own `review.md`. Only the two bookkeeping fields were brought into line.\n')
    out.append('| card | reviewer verdict located at | verbatim reviewer text | handoff.json `status` line | `reviewer_status` line | sha256 before | sha256 after |')
    out.append('|---|---|---|---|---|---|---|')
    for r in a:
        out.append('| %s | `review.md:%d` | `%s` | L%d | L%d | `%s` | `%s` |'
                   % (r['card'], r['review_line'], r['quote'].replace('|', '\\|'),
                      r['status_line'], r['rs_line'],
                      r['sha256_before'], r['sha256_after']))
    out.append('')

    out.append('### Task A - what exactly changed in each file\n')
    for r in a:
        out.append('**%s** (`review.md:%d` -> `handoff.json` L%d / L%d)' % (
            r['card'], r['review_line'], r['status_line'], r['rs_line']))
        out.append('')
        out.append('* `status`: `review_pending` -> `accepted_scoped`')
        out.append('* old `reviewer_status` value preserved verbatim under `%s`:' % r['new_reviewer_status_key'])
        out.append('  `%s`' % r['old_reviewer_status'])
        out.append('* new `reviewer_status` (ASCII text; the CJK excerpt is carried as `\\uXXXX` escapes):')
        out.append('  `%s`' % r['instructions'])
        out.append('')

    out.append('### Task A - pre-edit copies\n')
    out.append('Each card keeps a byte-identical pre-edit copy of its `handoff.json` at\n'
               '`<PLAN>\\execution_runs\\<CARD>\\a20260919-01\\recovery\\handoff_pre_bookkeeping.json`.\n')
    out.append('* `I-00-B` was changed by ANOTHER session between the audit snapshot (03:50:39) and this\n'
               '  pass: its `status` had already been set to `accepted_scoped` at 03:57:36. The\n'
               '  audit-snapshot bytes are preserved at\n'
               '  `recovery\\handoff_pre_bookkeeping_audit_snapshot.json` (sha256\n'
               '  `2f444453d32c436095dc6a24063974033384f164cdd6df0258794f4912c686ba`) and\n'
               '  `recovery\\handoff_pre_bookkeeping.json` was re-anchored to the live bytes\n'
               '  `c9668074e1a88f18267e967c1cbfd0b43d685ed33dc238790696432f91707422` before editing.\n'
               '  This pass therefore only had to fix the `reviewer_status` field on that card.\n'
               '* `I-02-A`: the duplicate `reviewer_status` key at `handoff.json:70` was removed after\n'
               '  BOTH old values were preserved verbatim in `reviewer_status_merged_history`; the file now\n'
               '  has exactly one `reviewer_status` key.\n'
               '* `I-02-D`: `review.md:5` reads `ACCEPT`, which is not one of the plan four verdict words.\n'
               '  The ledger records `accepted_scoped` and carries\n'
               '  `vocabulary_normalization_pending_reviewer_confirmation: true`. `review.md` was NOT edited.\n'
               '* `I-00-D`: the stale `next_action` ("reviewer reads diff and signs review.md") was\n'
               '  corrected, with the original kept verbatim in `next_action_note`.\n'
               '* `I-03-D`: `blocked_by` was not touched (out of scope).\n'
               '* `I-14-A`: handled in ledger form. `status` -> `accepted_scoped`;\n'
               '  the old `reviewer_status` is kept under `reviewer_status_at_r2_20260920T0350`; a\n'
               '  `reviewer_status_ledger` records r1 / r2 / r3; `review.md` was NOT edited, and\n'
               '  "the reviewer should add its own r3 re-read block" is registered as a NEED, not written.\n')

    out.append('## Task B1 - duplicated r2 section merged in M05/M06/M07/M08 `review.md`\n')
    out.append('The section `## revision r2 - response to the independent review` appeared twice in each\n'
               'file with identical wording. The FIRST copy was kept; the SECOND copy plus the `---`\n'
               'separator that followed the first was removed. No word was rewritten.\n')
    out.append('| card | kept (1-based) | removed (1-based) | removed lines | sha256 before | sha256 after | verbatim archive |')
    out.append('|---|---|---|---|---|---|---|')
    for r in b1:
        out.append('| %s | %d-%d | %d-%d | %d | `%s` | `%s` | `recovery\\review_md_r2_duplicate_removed.txt` |'
                   % (r['card'], r['kept_block_lines'][0], r['kept_block_lines'][1],
                      r['removed_including_separator'][0], r['removed_including_separator'][1],
                      r['removed_line_count'], r['sha256_before'], r['sha256_after']))
    out.append('')
    out.append('The removed bytes are archived verbatim, each with a header line naming the source line\n'
               'range, in the card `recovery/` directory listed above. `oracle.md` was NOT touched\n'
               '(its own duplicate section was already folded by an earlier pass, F-M08-06).\n')

    out.append('## Task B2 - the un-reproducible reviewer snapshot claim in M05-M08 `handoff.json`\n')
    out.append('The four files claimed the reviewer verified `oracle.md` hashes against snapshot\n'
               'directories `copy/` and `copy_r2/`. A full recursive search of the PLAN tree returns\n'
               '**zero** hits for any `copy`, `copy_r2` or `copy_r3` directory anywhere: the reviewer\n'
               'snapshots were never retained on disk, so that verification is not reproducible.\n')
    out.append('| card | `reference_states` now at | sha256 before | sha256 after | pre-edit archive |')
    out.append('|---|---|---|---|---|')
    for r in b2:
        line = r.get('reference_states_line_after') or r.get('block_lines_replaced_1based')
        if isinstance(line, list) and len(line) == 1:
            loc = 'L%d' % line[0]
        elif isinstance(line, list):
            loc = 'L%d-L%d' % (line[0], line[1])
        else:
            loc = str(line)
        out.append('| %s | %s | `%s` | `%s` | `recovery\\handoff_pre_reference_states_fix.json` |'
                   % (r['card'], loc, r['sha256_before'], r['sha256_after']))
    out.append('')
    out.append('Each block now carries `correction_disposition`, `reproducible_from_disk`,\n'
               '`retained_reviewer_snapshot_dirs: 0`,\n'
               '`un_retained_observation_not_reproducible: true`, and both original strings under\n'
               '`r1_snapshot_claim_pre_correction` / `r2_snapshot_claim_pre_correction`. The claim is\n'
               'downgraded to an un-retained observation, so nothing in those files can still be read\n'
               'as reproducible on disk. The files were re-dumped through the JSON encoder: the change\n'
               'is semantic only and the result is guaranteed to parse with no duplicate keys.\n')
    out.append('**Correction to the audit report itself.** The audit report also stated that no\n'
               '`oracle.json` exists anywhere in the PLAN tree. **That is false.** Expected-value files\n'
               'named `oracle.json` DO exist, for example\n'
               '`execution_runs\\M05\\a20260919-01\\evidence\\M05\\oracle.json` and\n'
               '`execution_runs\\M05\\a20260919-01\\recovery\\selfcheck\\evidence\\M05\\oracle.json`.\n'
               'The `reference_states` correction therefore asserts only the true part: the `copy/` and\n'
               '`copy_r2/` snapshot directories are absent.\n')

    out.append('## Task B3 - M01 `revision_history` duplicate entries\n')
    out.append('**Not done, and nothing was removed, because there was nothing left to remove.** When\n'
               'this pass read `M01\\a20260919-01\\handoff.json` (another session had just rewritten it,\n'
               'mtime 2026-09-20T04:07:38), `revision_history` already held 5 entries and the\n'
               'byte-identical pairs the audit reported at `:175-178` / `:183-186` and `:179-182` /\n'
               '`:187-190` were **no longer present**; the file now carries an `r4` entry too.\n'
               'A programmatic duplicate scan reports 0 byte-identical duplicates.\n')
    out.append('No archive of removed entries exists for M01, because this pass removed none and will\n'
               'not fabricate a "removed copy". If the parent needs the audit-time text, it must come\n'
               'from the audit snapshot or the session record of whichever session performed that edit.\n')

    out.append('## Self-check\n')
    out.append('`selfcheck.py` re-parses all 18 touched `handoff.json` files with\n'
               '`object_pairs_hook` duplicate-key detection, verifies every Task A card ends at\n'
               '`status: accepted_scoped` with the no-self-signature note present and the old value\n'
               'retained, verifies the Task B2 correction keys and archives, verifies each M05-M08\n'
               '`review.md` now has exactly one r2 section while its archive holds exactly one copy,\n'
               'and scans M01 for duplicates. Result: **ALL CHECKS PASSED**.\n')

    out.append('## Concurrent writers - what happened after this pass\n')
    out.append('This plan tree was being edited by several sessions at once. Ten of the fourteen Task A\n'
               'files were written again by other sessions AFTER this pass finished, so the sha256 shown\n'
               'in the Task A table above is this pass\'s post-edit value, not necessarily the current\n'
               'one. `postcheck.py` re-reads the current bytes and confirms that in **all fourteen\n'
               'cards** this pass\'s transcription is still present and exact: `status` is\n'
               '`accepted_scoped`, `reviewer_status` still carries the transcription string byte for\n'
               'byte, and the old value is still retained under its preserved key.\n')
    out.append('* Rewritten after this pass (transcription intact): I-00-B, I-00-C, I-00-D, I-01-A,\n'
               '  I-02-B, I-02-C, I-02-D, I-02-E, I-03-B, I-03-D.\n'
               '* Unchanged since this pass: I-02-A, I-03-A, I-03-C, I-14-A.\n'
               '* `I-00-B` is worth flagging: it was changed by another session BEFORE this pass too\n'
               '(its `status` was set to `accepted_scoped` at 03:57:36 while the audit snapshot was\n'
               'taken at 03:50:39), which is why both a re-anchored pre-edit copy and the audit-time\n'
               'copy are kept for that card.\n')

    out.append('## Not done / not verified\n')
    out.append('* No technical verification was redone: no oracle was recomputed, no product command was\n'
               're-run, no exit code was re-measured. This pass is bookkeeping and documentation only.\n'
               '* No verdict was created, changed or withdrawn for any card. In particular, the cards the\n'
               'audit judged `not_accepted` (I-00-A, I-08-A) and the conditional ones (I-04-C, M01-M07)\n'
               'were NOT given `accepted_scoped` by this pass.\n'
               '* `I-02-D` vocabulary normalization is recorded as pending the reviewer confirmation; it\n'
               'was not decided here.\n'
               '* `I-14-A` still wants a reviewer-authored r3 re-read block inside `review.md`; it was\n'
               'registered as a need, not written.\n'
               '* No `review.md` verdict text was edited anywhere. The only `review.md` edits were the\n'
               'four duplicate-section removals in Task B1.\n'
               '* `oracle.md`, `qualification.json` grant states, expectations, thresholds, negative\n'
               'cases and exit codes were not modified.\n'
               '* Concurrency: M01, M05, M06, M07, M08 and I-00-B were all being modified by other\n'
               'sessions during this pass. The cases where that mattered are documented above.\n')

    text = '\n'.join(out) + '\n'
    dest = os.path.join(work, 'REPORT.md')
    with open(dest, 'wb') as fh:
        fh.write(text.encode('utf-8'))
    print('wrote ' + dest + ' bytes=' + str(len(text.encode('utf-8'))))


if __name__ == '__main__':
    main()
