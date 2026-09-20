"""Rewrite the F-L9c / F-L8d cases so the ledger they edit is the LIVE one.

Both cases must hold the participant inside its release critical section, otherwise
the participant completes its release (and unlinks the ledger) before the scheduler
reads it.
"""

from __future__ import annotations

import pathlib
import re
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

NEW_L9C = '''def case_f_l9c(run: CaseRun) -> None:
    """A user pause DURING our scope, in its DISTINGUISHABLE form (F-L9c).

    A human running ``worker-pause`` only flips ``desired_state`` on the wiki side,
    which our ledger cannot see - that is the I-04-C section 8 O-2 limitation, and it
    is registered as a cross-repo dependency rather than papered over here.  The
    DISTINGUISHABLE form is the one where the user's action also invalidates our
    ownership evidence: the operator pauses the worker and removes the owner evidence
    our marker backed (W7/T10).  The tool must then NOT resume the user's pause, must
    not fabricate new ownership evidence, and must say so.

    A is held INSIDE its release critical section, so the ledger the scheduler edits
    is the LIVE one rather than an already-collected one.
    """
    run.spawn(
        "A",
        hooks="arrive:release-read@A,gate:release-read-fence@A",
        resume_wait=0.2,
        graceful=0.2,
    )
    assert run.wait_arrival("release-read", "A"), "A never entered its release critical section"
    time.sleep(0.15)
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    run.meta["live_ledger"] = {
        "sha256": _sha256(run.refcount),
        "lease_set": sorted(
            str(e.get("lease_id")) for e in payload.get("entries") or [] if isinstance(e, dict)
        ),
    }
    run.state.write_text(
        json.dumps({"desired_state": "paused", "runtime_state": "stopped"}), encoding="utf-8"
    )
    if run.owner.exists():
        run.owner.unlink()
    # Rewrite ONLY the owner field: schema, generation, entries and the resume
    # obligation stay exactly as the code under test wrote them, so this case tests
    # an ownership-evidence change rather than a hand-made ledger.
    payload["owner"] = None
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["user_action"] = {
        "owner_marker_removed": not run.owner.exists(),
        "owner_record": payload.get("owner"),
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
    }
    run.release("release-read-fence", "A")
    run.reap("A")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount) if run.refcount.is_file() else "<absent>",
        "payload": _read_json(run.refcount),
        "worker_state": _read_json(run.state),
        "owner_marker_exists": run.owner.exists(),
    }
'''

NEW_L8D = '''def case_f_l8d(run: CaseRun) -> None:
    """The owner evidence is rewritten under us: R5 fails closed (F-L8d).

    A is held inside its release critical section while the ownership record is
    replaced by a third party that cannot be attributed and cannot be proven dead.
    """
    run.spawn(
        "A",
        hooks="arrive:release-read@A,gate:release-read-fence@A",
        resume_wait=0.2,
        graceful=0.2,
    )
    assert run.wait_arrival("release-read", "A"), "A never entered its release critical section"
    time.sleep(0.15)
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    payload["owner"] = THIRD_PARTY_OWNER
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["owner_rewrite"] = {
        "sha256": _sha256(run.refcount),
        "owner": payload["owner"],
        "lease_set": sorted(
            str(e.get("lease_id")) for e in payload.get("entries") or [] if isinstance(e, dict)
        ),
    }
    run.release("release-read-fence", "A")
    run.reap("A")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount) if run.refcount.is_file() else "<absent>",
        "payload": _read_json(run.refcount),
        "worker_state": _read_json(run.state),
    }
'''

text = PATH.read_text(encoding="utf-8")
for name, new in (("case_f_l9c", NEW_L9C), ("case_f_l8d", NEW_L8D)):
    pattern = re.compile(rf"^def {name}\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        print(f"PATTERN NOT FOUND: {name}")
        sys.exit(1)
    text = text[: match.start()] + new + "\n\n" + text[match.end() :]
    print(f"replaced {name}")
PATH.write_text(text, encoding="utf-8")
