#!/usr/bin/env python3
"""Task A bookkeeping fix (implementer, 2026-09-20).

Transcribes the independent reviewer's already-written `accepted_scoped` verdicts
into the two bookkeeping fields of each card's handoff.json.  It never invents a
verdict, never edits review.md, and never deletes an existing field value.

Usage:  python apply_bookkeeping.py <manifest.json> [--dry-run]
"""
import hashlib
import io
import json
import os
import re
import sys

IMP = ("Transcribed for bookkeeping by the implementer on 2026-09-20; "
       "the implementer did not and does not sign acceptance.")
TAIL = (" The reviewer reviewed the scope stated in that section; the implementer "
        "changed no verdict word and no scope, and this transcription transfers no "
        "qualification beyond what the reviewer wrote.")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def read_raw(path):
    """Return (text, newline) decoding UTF-8 without BOM."""
    with open(path, 'rb') as fh:
        data = fh.read()
    if data.startswith(b'\xef\xbb\xbf'):
        raise SystemExit('unexpected BOM in ' + path)
    text = data.decode('utf-8')
    nl = '\r\n' if '\r\n' in text else '\n'
    return text, nl


def write_raw(path, text, nl):
    with open(path, 'wb') as fh:
        fh.write(text.replace('\n', nl).encode('utf-8'))


def make_instructions(card, line, quote, extra):
    s = ('accepted_scoped - verdict written by the independent reviewer in '
         'review.md:%d: "%s". %s' % (line, quote, IMP))
    if extra:
        s += ' ' + extra
    return s + TAIL


def main():
    manifest_path = sys.argv[1]
    dry = '--dry-run' in sys.argv[2:]
    with open(manifest_path, 'rb') as fh:
        manifest = json.loads(fh.read().decode('utf-8'))

    results = []
    for card in sorted(manifest.keys()):
        spec = manifest[card]
        path = spec['path']
        before = sha256_file(path)
        text, nl = read_raw(path)
        lines = text.split('\n')

        # --- guard: file unchanged since the pre-edit snapshot was taken
        if spec.get('expect_sha256') and before != spec['expect_sha256']:
            raise SystemExit('DRIFT vs snapshot for %s: %s != %s'
                             % (card, before, spec['expect_sha256']))

        status_idx = spec['status_line'] - 1
        rs_idx = spec['rs_line'] - 1
        if not re.match(r'^\s*"status"\s*:', lines[status_idx]):
            raise SystemExit('status anchor mismatch for ' + card)
        if not re.match(r'^\s*"reviewer_status"\s*:', lines[rs_idx]):
            raise SystemExit('reviewer_status anchor mismatch for ' + card)
        # the value we are about to move must match the pre-edit snapshot's value
        # (leading indentation may legitimately differ: the snapshot preserves the
        #  original one-space indent while the live file was re-indented to two)
        if lines[rs_idx].strip() != spec['old_line'].strip():
            raise SystemExit('old reviewer_status line drifted for %s:\n live=[%s]\n snap=[%s]'
                             % (card, lines[rs_idx], spec['old_line']))

        ind = re.match(r'^(\s*)', lines[rs_idx]).group(1)
        new_key = spec.get('new_key', 'reviewer_status_before_bookkeeping_fix')
        old_key = spec['old_key']
        instructions = make_instructions(card, spec['review_line'],
                                         spec['quote'], spec.get('extra', ''))

        out = list(lines)
        out[status_idx] = re.sub(r'"status"\s*:\s*"[^"]*"',
                                 '"status": "accepted_scoped"', out[status_idx], count=1)

        if spec.get('mode') == 'ledger':
            # keep old value under a distinct key, and record the reviewer's verdict
            # under the existing reviewer_status key; the r1/r2/r3 trail goes into a
            # ledger so that no earlier reviewer statement is lost or overwritten.
            # every field here is followed by another field, so each keeps its comma.
            out[rs_idx] = '%s"%s": %s,' % (ind, old_key, json.dumps(spec['old_value']))
            inserted = ['%s"reviewer_status": %s,' % (ind, json.dumps(instructions))]
            inserted += ['%s"%s": %s,' % (ind, k, json.dumps(v))
                         for k, v in spec['ledger'].items()]
            out = out[:rs_idx + 1] + inserted + out[rs_idx + 1:]
        else:
            # 1. retain the old value verbatim under a new key
            out[rs_idx] = '%s"%s": %s,' % (ind, new_key, json.dumps(spec['old_value']))
            # 2. record the reviewer's transcribed verdict under reviewer_status
            rs_line = '%s"reviewer_status": %s' % (ind, json.dumps(instructions))
            if lines[rs_idx].rstrip().endswith(','):
                rs_line += ','
            out.insert(rs_idx + 1, rs_line)
            if spec.get('merged_history'):
                # 3. remove the duplicate reviewer_status key (JSON duplicate-key defect)
                dup_idx = spec['dup_rs_line']
                if not re.match(r'^\s*"reviewer_status"\s*:', out[dup_idx]):
                    raise SystemExit('duplicate-key anchor mismatch for ' + card)
                out[dup_idx] = '%s"reviewer_status_merged_history": %s' % (
                    ind, json.dumps(spec['merged_history'], ensure_ascii=False))

        if spec.get('next_action_line'):
            na_idx = spec['next_action_line'] - 1
            if not re.match(r'^\s*"next_action"\s*:', out[na_idx]):
                raise SystemExit('next_action anchor mismatch for ' + card)
            na_ind = re.match(r'^(\s*)', out[na_idx]).group(1)
            close_at = max(i for i, ln in enumerate(out) if ln.strip() == '}')
            if na_idx >= close_at:
                raise SystemExit('next_action is the last property, cannot append for ' + card)
            out[na_idx] = '%s"next_action_note": %s,' % (na_ind, json.dumps(spec['next_action_note']))
            out.insert(na_idx + 1, '%s"next_action": %s,' % (na_ind, json.dumps(spec['next_action'])))

        new_text = '\n'.join(out)

        # --- independent structural + duplicate-key validation
        try:
            parsed = json.loads(new_text)
        except Exception as exc:
            print('--- patched text around the failure for %s ---' % card)
            for n, ln in enumerate(new_text.split('\n'), 1):
                print('%3d| %s' % (n, ln))
            raise SystemExit('patched text is not valid JSON for %s: %s' % (card, exc))
        if parsed.get('status') != 'accepted_scoped':
            raise SystemExit('status not accepted_scoped for ' + card)
        check_status = parsed.get('reviewer_status')
        if not check_status:
            raise SystemExit('reviewer_status missing for ' + card)
        if check_status != spec['old_value']:
            if not check_status.startswith('accepted_scoped'):
                raise SystemExit('reviewer_status not accepted_scoped for ' + card)
            if ('review.md:%d' % spec['review_line']) not in check_status:
                raise SystemExit('reviewer_status lacks review.md line ref for ' + card)
            if spec['quote'] not in check_status:
                raise SystemExit('reviewer_status lacks the verbatim quote for ' + card)
            if 'did not and does not sign acceptance' not in check_status:
                raise SystemExit('reviewer_status lacks the no-self-signature note for ' + card)
        if parsed.get('reviewer_status_before_bookkeeping_fix') != spec['old_value'] \
                and parsed.get(spec['old_key']) != spec['old_value']:
            raise SystemExit('old reviewer_status value was not retained for ' + card)
        if card == 'I-02-A':
            if parsed.get('reviewer_status_merged_history') is None:
                raise SystemExit('I-02-A merged history missing')
            if new_text.count('"reviewer_status"') != 1:
                raise SystemExit('I-02-A still has a duplicate reviewer_status key')
        # duplicate TOP-LEVEL key scan on the raw text (top-level keys are the only
        # ones indented by exactly one space in these hand-formatted files; nested
        # keys such as a "status" inside case_results must not be counted here)
        for key in ('reviewer_status', 'status', 'reviewer_status_before_bookkeeping_fix'):
            hits = len(re.findall(r'^ "%s"\s*:' % re.escape(key), new_text, re.M))
            if hits > 1:
                raise SystemExit('duplicate key %s (%d) in %s' % (key, hits, card))

        if not dry:
            write_raw(path, new_text, nl)
        after = sha256_file(path) if not dry else '(dry-run)'
        results.append({
            'card': card,
            'review_line': spec['review_line'],
            'quote': spec['quote'],
            'status_line': spec['status_line'],
            'rs_line': spec['rs_line'],
            'old_reviewer_status': spec['old_value'],
            'new_reviewer_status_key': new_key,
            'instructions': instructions,
            'sha256_before': before,
            'sha256_after': after,
        })
        print('OK %-8s review.md:%-3d statusLine=%d rsLine=%d  %s -> %s'
              % (card, spec['review_line'], spec['status_line'], spec['rs_line'],
                 before[:16], str(after)[:16]))

    out_path = os.path.join(os.path.dirname(manifest_path), 'taskA_results.json')
    with open(out_path, 'wb') as fh:
        fh.write(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8'))
    print('DONE cards=%d results=%s' % (len(results), out_path))


if __name__ == '__main__':
    main()
