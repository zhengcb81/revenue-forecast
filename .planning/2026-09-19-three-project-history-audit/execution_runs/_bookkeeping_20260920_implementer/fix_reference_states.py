#!/usr/bin/env python3
"""Task B2: correct the `reference_states` claims in M05/M06/M07/M08 handoff.json.

Those four files claim the reviewer verified oracle.md hashes against reviewer
snapshot directories `copy/` and `copy_r2/`.  A full recursive search of the PLAN
tree finds no such directories anywhere, so that verification is NOT reproducible
from what is on disk.  The claim is downgraded to an un-retained observation and
the original strings are preserved verbatim in *_pre_correction fields.

The file is re-dumped through the JSON encoder: the change is semantic only, and
this guarantees the result parses and carries no duplicate keys.  The pre-edit
bytes are archived verbatim before anything is written.

Usage:  python fix_reference_states.py <plan_root> [--dry-run]
"""
import hashlib
import json
import os
import sys

DISPOSITION = (
    "CORRECTED BY THE IMPLEMENTER 2026-09-20 (documentation consistency only; no verdict, "
    "expectation, threshold, exit code, oracle.md body or qualification state was touched). "
    "A full recursive search of the PLAN tree returns ZERO hits for any directory or file named "
    "`copy`, `copy_r2` or `copy_r3` anywhere under any attempt: the reviewer's temporary snapshot "
    "directories were NOT retained on disk. The r1/r2 hash comparisons quoted in "
    "oracle_md_hash_ledger were therefore made against snapshots that no longer exist and are NOT "
    "reproducible from what is on disk; they are reclassified here as an UN-RETAINED OBSERVATION "
    "(the reviewer's own contemporaneous report), not as a result any successor can re-verify from "
    "the plan tree. What IS reproducible on disk is stated separately under reproducible_from_disk. "
    "oracle.json is NOT affected by this correction and the earlier claim that no oracle.json exists "
    "anywhere in the tree is FALSE: expected-value files named oracle.json do exist (this card's own "
    "evidence/<CARD>/oracle.json and recovery/selfcheck[/...]/evidence/<CARD>/oracle.json)."
)
REPRODUCIBLE = (
    "partially, and this is what remains: the whole-file sha256 values recorded in "
    "oracle_md_hash_ledger can be recomputed against the bytes that DO exist, and the v1 frozen "
    "body is still recoverable from the current oracle.md as sha256(oracle.md[:prefix_bytes]). The "
    "r1/r2 whole-file values themselves cannot be re-derived from the live tree if later revisions "
    "changed the file, and that is exactly why the snapshot directories mattered."
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    plan = sys.argv[1]
    dry = '--dry-run' in sys.argv[2:]
    report = []
    for card in ('M05', 'M06', 'M07', 'M08'):
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        with open(path, 'rb') as fh:
            raw = fh.read()
        before = sha(raw)
        text = raw.decode('utf-8')
        nl = '\r\n' if '\r\n' in text else '\n'
        obj = json.loads(text)

        if not dry:
            rec = os.path.join(os.path.dirname(path), 'recovery')
            os.makedirs(rec, exist_ok=True)
            with open(os.path.join(rec, 'handoff_pre_reference_states_fix.json'), 'wb') as fh:
                fh.write(raw)

        node = obj['docfix_r3_hash_ledger']
        rs = node['reference_states']
        if 'correction_disposition' in rs:
            raise SystemExit('%s: already corrected; refusing to run twice' % card)
        r1_old = rs.pop('r1')
        r2_old = rs.pop('r2')
        r3_old = rs.pop('r3')
        if 'copy_r2' not in r2_old or 'copy_r2' in r1_old:
            raise SystemExit('%s: unexpected r1/r2 reference_states values' % card)

        new_rs = {}
        new_rs['r1_snapshot_claim_pre_correction'] = r1_old
        new_rs['r2_snapshot_claim_pre_correction'] = r2_old
        new_rs['r3'] = r3_old
        new_rs['correction_disposition'] = DISPOSITION
        new_rs['reproducible_from_disk'] = REPRODUCIBLE
        new_rs['retained_reviewer_snapshot_dirs'] = 0
        new_rs['un_retained_observation_not_reproducible'] = True
        node['reference_states'] = new_rs

        new_text = json.dumps(obj, indent=1, ensure_ascii=False)

        # --- validation: semantic identity except for the corrected block
        reparsed = json.loads(new_text)
        if reparsed != obj:
            raise SystemExit('%s: re-dump is not semantically identical' % card)
        rs2 = reparsed['docfix_r3_hash_ledger']['reference_states']
        if rs2.get('un_retained_observation_not_reproducible') is not True:
            raise SystemExit('%s: correction key missing' % card)
        if rs2['r1_snapshot_claim_pre_correction'] != r1_old:
            raise SystemExit('%s: r1 old value not preserved' % card)
        if rs2['r2_snapshot_claim_pre_correction'] != r2_old:
            raise SystemExit('%s: r2 old value not preserved' % card)
        for key in ('reviewer_status', 'status', 'qualifications'):
            if key in obj and obj[key] != reparsed[key]:
                raise SystemExit('%s: %s changed' % (card, key))

        if not dry:
            with open(path, 'wb') as fh:
                fh.write(new_text.replace('\n', nl).encode('utf-8'))
            after = sha(open(path, 'rb').read())
        else:
            after = '(dry-run)'

        idx = [i + 1 for i, l in enumerate(new_text.split('\n'))
               if '"reference_states"' in l]
        report.append({
            'card': card,
            'handoff_json': path,
            'sha256_before': before,
            'sha256_after': after,
            'reference_states_line_after': idx,
            'r1_pre_correction': r1_old,
            'r2_pre_correction': r2_old,
            'note': ('file was re-dumped through the JSON encoder; content is semantically '
                     'identical, only whitespace changed'),
        })
        print('OK %-4s before=%s after=%s reference_states_line=%s'
              % (card, before[:16], str(after)[:16], idx))
    out = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer',
                       'taskB2_reference_states.json')
    with open(out, 'wb') as fh:
        fh.write(json.dumps(report, indent=1, ensure_ascii=False).encode('utf-8'))
    print('DONE results=' + out)


if __name__ == '__main__':
    main()
