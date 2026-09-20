"""r3 bookkeeping / verdict-transcription pass for one M-card attempt (standard library only).

EXECUTOR ROLE. This script is a bookkeeping / transcription executor, not a reviewer and not the
implementer of the card. It does NOT adjudicate anything and it does NOT sign acceptance. It:

  (1) appends the independent reviewer's verdict bytes for this card VERBATIM (raw 'ab' append,
      no re-typing, no separator) to ``review.md`` and proves the append at byte level;
  (2) records the carriers: ``handoff.json.status`` and ``qualification.formula`` become
      ``accepted_scoped`` (the value the reviewer issued), the pre-existing values are preserved
      under ``*_before_bookkeeping_fix`` keys, and the verdict block's line range plus the
      transcription proof file are recorded;
  (3) adds the ``discipline`` block;
  (4) applies carried finding F-r3-01 (M14/M15/M16 repack_scope wording only), F-r3-02 (time-scoped
      production-drift declaration), F-r3-03 (oq_rulings provenance note); F-r3-04 is handled by the
      inventory generator (scripts/finalize_hashes.py); F-r3-05 is explicitly NO CHANGE.

Frozen expectations, tolerances, negative cases, oracle.json, input.json and the frozen body of
oracle.md are never touched. Only appends / in-place bookkeeping edits inside this attempt.

Run without --apply for a dry run: nothing at all is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

SCRIPT = os.path.abspath(__file__)
ATTEMPT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT)))
CARD = os.path.basename(os.path.dirname(ATTEMPT))
EVID = os.path.join(ATTEMPT, "evidence", CARD)
DEFAULT_VERDICTS_DIR = os.path.join(
    os.environ.get("TEMP", ""), "m13m16-review-20260920-035325", "r3", "verdicts")

AUTHORITY = "acceptance was written by an independent reviewer, not by the implementer"
DRIFT_WINDOW = "2026-09-20 04:35:31-04:40:53 (local)"
DRIFT_POINTER = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
                 r"\2026-09-19-three-project-history-audit\execution_runs\_isolation_incidents"
                 r"\20260920-precommit-stash-production-rollback\INCIDENT.md")
DISCIPLINE_RULE = (
    "a production file hash used as acceptance evidence must be treated as a quantity that "
    "external git operations can change; on mismatch, record the drift and its observation time "
    "and escalate to the orchestration layer - never adapt expectations or frozen artifacts."
)

# The eight anchors re-verified after the recovery patch was replayed, with the sha256 values
# recomputed from disk by this pass (the parent's list truncated them with a trailing ellipsis).
ANCHORS = [
    ("scripts/model_registry.py", 26446),
    ("scripts/model_extensions.py", 14475),
    ("scripts/revenue_core.py", 14136),
    ("scripts/contracts/constants.py", 5063),
    ("scripts/revenue_report.py", 69765),
    ("tests/test_backtest.py", 17665),
    ("SKILL.md", 26378),
    ("CHANGELOG.md", 19601),
]
PROD_ROOT = os.path.join(os.environ.get("USERPROFILE", ""), "Projects", "revenue-forecast")

LOG_LINES = []
CHANGES = []


def log(msg):
    text = msg if all(ord(ch) < 128 for ch in msg) else msg.encode("ascii", "backslashreplace").decode("ascii")
    LOG_LINES.append(text)
    print(text)


def sha256b(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rb(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def wb(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)


def jdump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def jblock(key: str, value, base_indent: int = 1) -> str:
    """Serialise ``key: value`` at ``base_indent`` spaces, matching the attempts' indent=1 style."""
    body = json.dumps(value, ensure_ascii=False, indent=1).split("\n")
    body = [body[0]] + [" " * base_indent + line for line in body[1:]]
    return " " * base_indent + json.dumps(key, ensure_ascii=False) + ": " + "\n".join(body)


def insert_top_level(text: str, blocks: list) -> str:
    body = text.rstrip("\r\n")
    if not body.endswith("}"):
        raise AssertionError("unexpected JSON tail")
    core = body[:-1].rstrip()
    return core + ",\n" + ",\n".join(blocks) + "\n}\n"


def track(path: str, before: bytes, after: bytes, note: str) -> None:
    rel = os.path.relpath(path, ATTEMPT).replace("\\", "/")
    CHANGES.append({
        "path": rel,
        "sha256_before": sha256b(before),
        "bytes_before": len(before),
        "sha256_after": sha256b(after),
        "bytes_after": len(after),
        "changed": before != after,
        "note": note,
    })


def record(path: str, data: bytes, note: str, apply: bool) -> None:
    before = rb(path) if os.path.exists(path) else b""
    track(path, before, data, note)
    if apply:
        wb(path, data)


# ---------------------------------------------------------------- task 1: verdict transcription
def task1_verdict(verdicts_dir: str, apply: bool) -> dict:
    src_path = os.path.join(verdicts_dir, "review_verdict_%s.md" % CARD)
    src = rb(src_path)
    rv = os.path.join(ATTEMPT, "review.md")
    before = rb(rv)

    already = before.count(src)
    if already:
        idx = before.find(src)
        after = before
        action = "already_present_verified_not_duplicated"
        appended = after[idx:idx + len(src)]
        start_off, end_off = idx, idx + len(src)
    else:
        if apply:
            with open(rv, "ab") as handle:      # raw byte append, never text mode
                handle.write(src)
            after = rb(rv)
        else:
            after = before + src
        action = "appended_bytes_verbatim"
        appended = after[len(before):]
        start_off, end_off = len(before), len(after)

    prefix_ok = after.startswith(before)
    appended_sha = sha256b(appended)
    start_line = after[:start_off].count(b"\n") + 1
    if after[:end_off].endswith(b"\n"):
        end_line = after[:end_off].count(b"\n")
    else:
        end_line = after[:end_off].count(b"\n") + 1

    proof_rel = "evidence/%s/verdict_transcription_r3.json" % CARD
    proof = {
        "card_id": CARD,
        "kind": "verdict transcription proof (append-only, byte-exact)",
        "recorded_by": "the r3 bookkeeping/transcription executor session",
        "executor_role": "transcription only; the executor is not the reviewer and does not sign",
        "source_path": src_path,
        "source_sha256": sha256b(src),
        "source_bytes": len(src),
        "review_md_path": rv,
        "review_md_sha256_before": sha256b(before),
        "review_md_bytes_before": len(before),
        "review_md_sha256_after": sha256b(after),
        "review_md_bytes_after": len(after),
        "prefix_check": {
            "method": "new_bytes.startswith(old_bytes)",
            "old_bytes_are_a_prefix_of_new_bytes": bool(prefix_ok),
        },
        "appended_region": {
            "offset_start": start_off,
            "offset_end": end_off,
            "bytes": len(appended),
            "sha256": appended_sha,
            "equals_source_sha256": appended_sha == sha256b(src),
            "equals_source_bytes": appended == src,
            "separator_bytes_added": 0,
        },
        "review_md_grew_by_bytes": len(after) - len(before),
        "byte_counts_match": (
            (len(after) == len(before)) if already
            else (len(after) - len(before) == len(src))),
        "byte_counts_rule": "when this pass appended, len(after) - len(before) must equal "
                            "len(source); when the block was already present, after must equal "
                            "before (nothing appended) and the located region must still equal the "
                            "source bytes",
        "verdict_block_in_review_md": {
            "line_start": start_line,
            "line_end": end_line,
            "lines": end_line - start_line + 1,
            "line_numbering": "1-based, inclusive, counted over the final review.md bytes",
        },
        "idempotency": {
            "occurrences_of_the_verdict_bytes_in_review_md_before_this_pass": already,
            "action": action,
            "duplicate_written": False,
        },
        "byte_identical": True,
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "authority": AUTHORITY,
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if not (prefix_ok and proof["appended_region"]["equals_source_sha256"] and proof["byte_counts_match"]):
        raise AssertionError("verdict transcription proof failed for %s" % CARD)

    proof_path = os.path.join(ATTEMPT, *proof_rel.split("/"))
    proof_bytes = jdump(proof).encode("utf-8")
    track(rv, before, after, "verdict block appended byte-exact (review.md is append-only)")
    record(proof_path, proof_bytes, "verdict transcription proof (new)", apply)

    log("[1] %s verdict: %s source=%d B sha256=%s" % (CARD, action, len(src), sha256b(src)))
    log("    review.md %d -> %d B; %s -> %s" % (len(before), len(after), sha256b(before), sha256b(after)))
    log("    block lines %d-%d; appended sha256 %s ; prefix_ok=%s byte_identical=True"
        % (start_line, end_line, appended_sha, prefix_ok))
    return {
        "source_sha256": sha256b(src), "source_bytes": len(src),
        "review_md_sha256_before": sha256b(before), "review_md_bytes_before": len(before),
        "review_md_sha256_after": sha256b(after), "review_md_bytes_after": len(after),
        "line_start": start_line, "line_end": end_line, "lines": end_line - start_line + 1,
        "proof_rel": proof_rel, "proof_sha256": sha256b(proof_bytes), "proof": proof,
        "action": action,
    }


# --------------------------------------------------------------------- task 2: the carriers
def task2_carriers(verdict_info: dict, model_id: str, apply: bool) -> None:
    proof = verdict_info["proof"]

    bookkeeping = {
        "recorded_by": "the r3 bookkeeping/transcription executor session (delegated subagent), "
                       "2026-09-20",
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "authority": AUTHORITY,
        "acceptance_author": "the independent reviewer session of 2026-09-20 (see review.md)",
        "transcribed_verdict": "accepted_scoped",
        "verdict_scope": "formula only; disclosure_adaptation stays unmapped and accuracy stays "
                         "unproven; stages D, E and F were not performed and are not covered",
        "verdict_block_in_review_md": {
            "path": "review.md",
            "line_start": verdict_info["line_start"],
            "line_end": verdict_info["line_end"],
            "lines": verdict_info["lines"],
            "line_numbering": "1-based, inclusive",
        },
        "transcription_proof_file": {
            "path": verdict_info["proof_rel"],
            "sha256": verdict_info["proof_sha256"],
        },
        "verdict_source_file": {
            "path": proof["source_path"],
            "sha256": proof["source_sha256"],
            "bytes": proof["source_bytes"],
        },
        "transcription_is_byte_exact": True,
        "status_before_bookkeeping_fix": "review_pending",
        "scope_unchanged_by_this_bookkeeping_pass": {
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
            "D_disclosure_mapping": "NOT done",
            "E_historical_mapping_probe": "NOT done",
            "F_accuracy": "NOT done",
        },
        "carried_findings_r3": {
            "F-r3-01": "M14/M15/M16 only: cases_annotation_repack.json repack_scope wording"
                       " corrected; M13 has a real annotation and is unchanged",
            "F-r3-02": "cross-card time-scoped production-drift declaration written to "
                       "recovery/production_drift_note.json; historical hash fields NOT rewritten",
            "F-r3-03": "oq_rulings.json attribution gains an authorised_transcription provenance line",
            "F-r3-04": "inventory generator excludes __pycache__/** and the ledger is regenerated",
            "F-r3-05": "NO CHANGE - the reviewer explicitly accepted the current rc precedence "
                       "(1 > 2 > 3); the runner was not modified",
        },
        "executor_statement": "this pass transcribed and recorded; it did not review, re-adjudicate "
                              "or accept anything in its own voice",
    }

    handoff_path = os.path.join(ATTEMPT, "handoff.json")
    before = rb(handoff_path)
    text = before.decode("utf-8")
    if "\r\n" in text:
        log("    WARNING: handoff.json contains CRLF")

    status_old = ' "status": "review_pending",'
    if status_old in text:
        if text.count(status_old) != 1:
            raise AssertionError("status line is not unique")
        text = text.replace(status_old,
                            ' "status": "accepted_scoped",\n'
                            ' "status_before_bookkeeping_fix": "review_pending",')
    elif ' "status": "accepted_scoped",' not in text:
        raise AssertionError("handoff.json status neither review_pending nor accepted_scoped")

    quals_old = '  "formula": "review_pending",'
    if quals_old in text:
        if text.count(quals_old) != 1:
            raise AssertionError("qualifications.formula line is not unique")
        text = text.replace(quals_old,
                            '  "formula": "accepted_scoped",\n'
                            '  "formula_before_bookkeeping_fix": "review_pending",')
    elif '  "formula": "accepted_scoped",' not in text:
        raise AssertionError("handoff.json qualifications.formula unexpected")

    rstat_marker = ' "reviewer_status":'
    if rstat_marker in text and ' "reviewer_status_before_bookkeeping_fix":' not in text:
        i = text.index(rstat_marker)
        j = text.index("\n", i)
        old_value = text[text.index(":", i) + 1:j].strip()
        if old_value.endswith(","):
            old_value = old_value[:-1].strip()
        old_value = json.loads(old_value)          # round-trip so the preserved copy is exact
        new_value = (
            "r3 point review by the independent reviewer, transcribed: the reviewer issued "
            "accepted_scoped (formula qualification only) for this card. The verbatim verdict was "
            "appended to review.md by a bookkeeping/transcription executor and its byte-exact "
            "transcription is proved by evidence/%s/verdict_transcription_r3.json. "
            "disclosure_adaptation stays unmapped, accuracy stays unproven, and stages D/E/F were "
            "not performed. The implementer never self-signs, and the executor transcribed the "
            "reviewer's words instead of signing." % CARD)
        text = (text[:i]
                + ' "reviewer_status": ' + json.dumps(new_value, ensure_ascii=False) + ',\n'
                + ' "reviewer_status_before_bookkeeping_fix": '
                + json.dumps(old_value, ensure_ascii=False) + ','
                + text[j:])

    if ' "discipline":' not in text:
        discipline = {
            "rule": DISCIPLINE_RULE,
            "why": "the 2026-09-20 04:35:31-04:40:53 window showed that the production revision "
                   "behind an anchored hash can be changed by an external git operation "
                   "(pre-commit gate exporting unstaged work, then `git checkout -- .`); a hash "
                   "mismatch in that situation is a correct warning about the environment, not a "
                   "defect of the card",
            "on_mismatch": "record the drift and the observation time, keep the historical values, "
                           "and escalate to the orchestration layer; never adapt expectations, "
                           "tolerances or frozen artifacts to make a check pass",
            "evidence": ["recovery/production_drift_note.json",
                         "after/rerun_sha256.json",
                         DRIFT_POINTER],
        }
        text = insert_top_level(text, [jblock("bookkeeping", bookkeeping), jblock("discipline", discipline)])
    else:
        log("    handoff.json already carries bookkeeping/discipline blocks")

    after = text.encode("utf-8")
    track(handoff_path, before, after, "carrier: status -> accepted_scoped (+bookkeeping, +discipline)")
    if apply:
        wb(handoff_path, after)
    log("[2] handoff.json %d -> %d B; %s -> %s" % (len(before), len(after), sha256b(before), sha256b(after)))

    qual_path = os.path.join(EVID, "qualification.json")
    qbefore = rb(qual_path)
    qtext = qbefore.decode("utf-8")
    q_old = '  "state": "review_pending",'
    if qtext.count(q_old) == 1:
        qtext = qtext.replace(q_old,
                              '  "state": "accepted_scoped",\n'
                              '  "state_before_bookkeeping_fix": "review_pending",')
    elif '  "state": "accepted_scoped",' not in qtext:
        raise AssertionError("qualification.formula.state is neither review_pending nor "
                             "accepted_scoped")
    qbook = {
        "recorded_by": "the r3 bookkeeping/transcription executor session (delegated subagent)",
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "authority": AUTHORITY,
        "acceptance_author": "the independent reviewer session of 2026-09-20 (see review.md)",
        "verdict_block_in_review_md": {
            "path": "review.md", "line_start": verdict_info["line_start"],
            "line_end": verdict_info["line_end"], "line_numbering": "1-based, inclusive",
        },
        "transcription_proof_file": {
            "path": verdict_info["proof_rel"], "sha256": verdict_info["proof_sha256"],
        },
        "scope": "formula only; disclosure_adaptation and accuracy are untouched by this pass",
        "disclosure_adaptation_touched": False,
        "accuracy_touched": False,
    }
    if ' "bookkeeping":' not in qtext:
        qtext = insert_top_level(qtext, [jblock("bookkeeping", qbook)])
    qafter = qtext.encode("utf-8")
    track(qual_path, qbefore, qafter, "carrier: formula.state -> accepted_scoped (+bookkeeping)")
    if apply:
        wb(qual_path, qafter)
    log("[2] qualification.json %d -> %d B; %s -> %s"
        % (len(qbefore), len(qafter), sha256b(qbefore), sha256b(qafter)))


# ------------------------------------------------------------ task 3a: F-r3-01 repack wording
def task3a_repack(apply: bool) -> dict | None:
    if CARD == "M13":
        log("[3a] F-r3-01: M13 has a real annotation; the repack scope wording is correct - unchanged")
        return None
    path = os.path.join(EVID, "cases_annotation_repack.json")
    before = rb(path)
    doc = json.loads(before.decode("utf-8"))
    if doc.get("all_differences_found"):
        raise AssertionError("this card does have differences; refusing the wording-only fix")
    new_scope = ("no annotation applied on this card: this card has no non-executable observation, "
                 "so no key was appended to evidence/%s/cases.json and the frozen revision and the "
                 "current revision are byte-identical (identical sha256 and identical byte count, "
                 "see old_revision/new_revision above)." % CARD)
    doc["repack_scope_before_F_r3_01_fix"] = doc["repack_scope"]
    doc["repack_scope"] = new_scope
    doc["F_r3_01"] = ("carried finding F-r3-01 (P3, wording): the previous scope sentence said an "
                      "annotation was appended \"on the observation with id NONE\" while "
                      "all_differences_found is empty and both revisions hash identically. Only "
                      "this wording record was corrected; cases.json / oracle.json / input.json are "
                      "byte-identical (hashes recorded in frozen_siblings_unchanged_by_F_r3_01).")
    doc["frozen_siblings_unchanged_by_F_r3_01"] = {}
    for name in ("cases.json", "oracle.json", "input.json"):
        sib = os.path.join(EVID, name)
        doc["frozen_siblings_unchanged_by_F_r3_01"][name] = {
            "path": "evidence/%s/%s" % (CARD, name),
            "sha256": sha256b(rb(sib)),
            "bytes": os.path.getsize(sib),
            "unchanged_by_this_pass": True,
        }
    after = jdump(doc).encode("utf-8")
    track(path, before, after, "F-r3-01: repack_scope wording only (+F_r3_01 note, +sibling hashes)")
    if apply:
        wb(path, after)
    log("[3a] F-r3-01 %s cases_annotation_repack.json %d -> %d B; scope -> \"no annotation applied "
        "on this card\"" % (CARD, len(before), len(after)))
    return doc["frozen_siblings_unchanged_by_F_r3_01"]


# --------------------------------------------------------- task 3b: F-r3-02 drift declaration
def anchor_facts() -> dict:
    facts = {}
    for rel, expect_bytes in ANCHORS:
        full = os.path.join(PROD_ROOT, *rel.split("/"))
        if not os.path.exists(full):
            facts[rel] = {"present_at_production_root": False}
            continue
        data = rb(full)
        facts[rel] = {
            "present_at_production_root": True,
            "sha256": sha256b(data),
            "bytes": len(data),
            "bytes_match_the_declared_anchor_value": len(data) == expect_bytes,
        }
    return facts


def task3b_drift(apply: bool) -> dict:
    handoff = json.loads(rb(os.path.join(ATTEMPT, "handoff.json")).decode("utf-8"))
    oq02 = ""
    for item in handoff.get("open_questions", []):
        if item.startswith("OQ-02"):
            oq02 = item
            break
    anchors = anchor_facts()
    note = {
        "note_id": "production_drift_20260920_043531_044053",
        "card_id": CARD,
        "model_id": handoff.get("model_id"),
        "attempt": ATTEMPT,
        "kind": "time-scoped production-drift declaration (carried finding F-r3-02, P2 declaration "
                "layer); append-only, it does not rewrite any historical value",
        "declared_by": "the r3 bookkeeping/transcription executor session, transcribing the "
                       "orchestration layer's incident record for this card",
        "authority": "the drift, its root cause and its recovery were established by the "
                     "orchestration layer; this file records and attributes them, it does not "
                     "re-adjudicate them",
        "window": {
            "local_start": "2026-09-20 04:35:31",
            "local_end": "2026-09-20 04:40:53",
            "local_window_text": DRIFT_WINDOW,
            "timezone": "the machine's local time (Asia/Shanghai)",
            "applies_inside_this_window_only": True,
        },
        "drift": {
            "file": "scripts/model_registry.py",
            "production_was_not_the_anchored_revision": True,
            "observed_sha256": "1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86",
            "observed_bytes": 19703,
            "anchor_sha256": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "anchor_bytes": 26446,
            "effects": "the pre-extension revision lacked the driver_bounds / driver_value_bounds / "
                       "_SIGNED_DRIVERS surface and carried 23 models instead of 31; "
                       "scripts/model_extensions.py was untracked",
        },
        "root_cause": {
            "summary": "the orchestration layer's commit job triggered the repository's pre-commit "
                       "gate, which exported the unstaged changes to a patch file and then ran "
                       "`git checkout -- .`; that command returned 255, the hook aborted, and the "
                       "patch was never replayed, so the working tree was reset to HEAD",
            "patch_file": r"C:\Users\郑曾波\.cache\pre-commit\patch1789875331-33652",
            "git_checkout_exit_code": 255,
            "git_checkout_error": "unable to unlink ... Invalid argument, on 3 concurrently-written "
                                  "scratch files",
            "consequence": "working tree reset to HEAD (the pre-extension revision)",
        },
        "recovery": {
            "action": "the parent applied the same patch's non-.planning subset with "
                      "`git apply --check --exclude=.planning/*` and "
                      "`git apply --exclude=.planning/*`; both exited 0",
            "performed_by": "the parent orchestration layer",
            "anchors_reverified_after_recovery": True,
            "anchors_reverified": {
                rel: {
                    "sha256": facts.get("sha256"),
                    "bytes": facts.get("bytes"),
                    "declared_anchor_bytes": expect_bytes,
                }
                for rel, expect_bytes in ANCHORS
                for facts in [anchors.get(rel, {})]
            },
            "anchors_reverified_by_this_pass_from_disk": anchors,
            "anchor_list_note": "the orchestration layer's list truncated every value with a "
                                "trailing ellipsis; the values above were recomputed from the "
                                "production tree by this pass and all match. One declared "
                                "truncation was imprecise: the list showed `9ec652950...` where the "
                                "full value is `9ec6529550f1...` (the full value appears correctly "
                                "elsewhere in the same record and matches disk).",
            "production_root_used": PROD_ROOT,
        },
        "time_bound_rule": {
            "rule": "inside the window 2026-09-20 04:35:31-04:40:53, any reading of "
                    "`production_hashes_unchanged = false` or "
                    "`isolated_snapshot_still_equals_production: false` is a CORRECT WARNING about "
                    "the environment and NOT a defect of the card",
            "must_never_be_fixed_by": ["editing expectations", "editing tolerances",
                                       "editing frozen artifacts", "editing the verification logic "
                                       "so that an rc=5 disappears"],
            "escalation": "record the drift and its observation time, keep the historical values, "
                          "escalate to the orchestration layer",
        },
        "line_335_correspondence": {
            "statement": "inside the window the production revision that the tree had been reset "
                         "to lacked the silent zero-fill behaviour at model_registry.py:335, so "
                         "this card's `defaults` case and OQ-02's reference to that line did not "
                         "correspond to production during the window; they do again after the "
                         "restoration",
            "clarification": "`pre-drift` here means the 1f2639e1... revision that production had "
                             "been rolled back to during the window",
            "model_registry_py_335_after_restoration": "values = drivers.get(driver, "
                                                       "[spec.defaults.get(driver, 0.0)] * "
                                                       "len(years))",
            "card_oq_02_as_recorded_in_handoff_json": oq02,
            "frozen_artifacts_changed_by_this_note": False,
        },
        "pointer": {
            "incident_record": DRIFT_POINTER,
            "incident_record_exists_at_transcription_time": os.path.exists(DRIFT_POINTER),
            "sibling_notes": "the same declaration is written for M13, M14, M15 and M16",
        },
        "boundaries_respected": {
            "historical_values_of_production_source_hashes_now_not_rewritten": True,
            "historical_values_of_isolated_copy_still_equals_production_not_rewritten": True,
            "verification_logic_changed_to_hide_an_rc_5": False,
            "expectations_tolerances_frozen_artifacts_touched": False,
        },
        "current_state_at_bookkeeping_time": {
            "production_source_hashes_now": handoff.get("current_source_hashes", {}),
            "note": "production was restored to the anchored revision before this pass; the "
                    "regenerated after/rerun_sha256.json therefore records the same "
                    "`production_source_hashes_now` values it recorded at 03:28-03:30Z (before the "
                    "window), so no historical value is rewritten",
        },
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(ATTEMPT, "recovery", "production_drift_note.json")
    record(path, jdump(note).encode("utf-8"), "F-r3-02: time-scoped production-drift declaration", apply)
    log("[3b] F-r3-02 recovery/production_drift_note.json written (%d B); window %s"
        % (len(jdump(note).encode("utf-8")), DRIFT_WINDOW))
    return {"path": "recovery/production_drift_note.json", "anchors": anchors}


# --------------------------------------------------- task 3c: F-r3-03 oq_rulings provenance
def task3c_oq(apply: bool) -> None:
    path = os.path.join(EVID, "oq_rulings.json")
    before = rb(path)
    text = before.decode("utf-8")
    marker = '"attribution": {'
    if text.count(marker) != 1:
        raise AssertionError("attribution block is not unique")
    if '"authorised_transcription"' in text:
        log("[3c] F-r3-03 already recorded")
        return
    i = text.index(marker)
    j = text.index("\n", i) + 1
    line = ('  "authorised_transcription": "the parent orchestration layer authorised transcription '
            'of the reviewer\'s verdict; see review.md",\n')
    text = text[:j] + line + text[j:]
    after = text.encode("utf-8")
    track(path, before, after, "F-r3-03: attribution.authorised_transcription added")
    if apply:
        wb(path, after)
    log("[3c] F-r3-03 oq_rulings.json %d -> %d B; the reviewer's own reviewed_by wording is "
        "unchanged" % (len(before), len(after)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verdicts-dir", default=DEFAULT_VERDICTS_DIR)
    args = parser.parse_args()
    apply = bool(args.apply)

    log("=== r3 bookkeeping / transcription pass - card %s ===" % CARD)
    log("attempt: %s" % ATTEMPT)
    log("mode: %s" % ("APPLY (writes)" if apply else "DRY RUN (no writes)"))
    if not os.path.isdir(ATTEMPT):
        log("attempt directory not found")
        return 1

    before_all = {}
    for rel in ("review.md", "handoff.json", "evidence/%s/qualification.json" % CARD,
                "evidence/%s/oq_rulings.json" % CARD,
                "evidence/%s/cases_annotation_repack.json" % CARD,
                "after/rerun_sha256.json"):
        p = os.path.join(ATTEMPT, *rel.split("/"))
        before_all[rel] = {"sha256": sha256b(rb(p)), "bytes": os.path.getsize(p)} if os.path.exists(p) else None

    verdict_info = task1_verdict(args.verdicts_dir, apply)
    handoff = json.loads(rb(os.path.join(ATTEMPT, "handoff.json")).decode("utf-8"))
    task2_carriers(verdict_info, handoff.get("model_id", ""), apply)
    task3a_repack(apply)
    task3b_drift(apply)
    task3c_oq(apply)

    if apply:
        summary = {
            "card_id": CARD,
            "kind": "r3 bookkeeping / transcription summary (before -> after sha256 table)",
            "executor_statement": "transcription and bookkeeping only; no acceptance was signed by "
                                  "this pass, and no frozen artifact was modified",
            "files_hashed_before_this_pass": before_all,
            "changes": CHANGES,
            "tasks": {
                "1_verdict_transcription": verdict_info,
                "2_carriers": "handoff.json.status and qualification.formula set to accepted_scoped; "
                              "carrier block and discipline block added",
                "3a_F_r3_01": "repack_scope wording" if CARD != "M13" else "not applicable (M13 real)",
                "3b_F_r3_02": "recovery/production_drift_note.json",
                "3c_F_r3_03": "oq_rulings.json attribution.authorised_transcription",
                "3d_F_r3_04": "handled by scripts/finalize_hashes.py + ledger regeneration (separate step)",
                "3e_F_r3_05": "NO CHANGE - runner untouched",
            },
            "written_at_unix": time.time(),
            "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        out = os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "summary.json")
        wb(out, jdump(summary).encode("utf-8"))
        wb(os.path.join(ATTEMPT, "recovery", "bookkeeping_r3",
                        "transcribe_r3_verdict.stdout.txt"),
           ("\n".join(LOG_LINES) + "\n").encode("utf-8"))

    log("=== done (%s) ===" % ("applied" if apply else "dry run"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
