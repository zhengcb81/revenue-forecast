"""Replace the F-L8d / F-L9c gating with a participant-side signal-file wait.

The two cases need the ledger edited AFTER the participant's enter phase and BEFORE
its release phase.  They previously used an inner enter-path gate; that path proved
unreliable (the participant process left no report when a single enter-path gate was
armed), so the wait now happens in the PARTICIPANT, outside the code under test:
``--wait-for <file>`` parks the participant inside the scope body until the file
appears.  Nothing in the protocol is involved, so the case cannot depend on the hook
mechanism at all.
"""

from __future__ import annotations

import pathlib
import re
import sys

PART = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_participant.py"
)
SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

# --- participant: add --wait-for -------------------------------------------
part = PART.read_text(encoding="utf-8")
OLD_ARG = '''    parser.add_argument("--sleep-seconds", type=float, default=0.0)
'''
NEW_ARG = '''    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--wait-for", default="")
    parser.add_argument("--wait-timeout", type=float, default=60.0)
'''
if OLD_ARG not in part:
    print("ARG PATTERN NOT FOUND")
    sys.exit(1)
part = part.replace(OLD_ARG, NEW_ARG, 1)

OLD_WAIT = '''            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)
'''
NEW_WAIT = '''            if args.wait_for:
                # Park inside the scope body.  This is the HARNESS, not the code
                # under test: it exists so a schedule can edit the ledger after our
                # enter and before our release without instrumenting either.
                signal = Path(args.wait_for)
                report["waiting_for"] = str(signal)
                limit = time.monotonic() + args.wait_timeout
                while not signal.exists():
                    if time.monotonic() > limit:
                        report["wait_timed_out"] = True
                        break
                    time.sleep(0.005)
                report["wait_satisfied"] = signal.exists()
                report["in_scope_snapshot"] = _snapshot(root)
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)
'''
if OLD_WAIT not in part:
    print("WAIT PATTERN NOT FOUND")
    sys.exit(1)
part = part.replace(OLD_WAIT, NEW_WAIT, 1)
PART.write_text(part, encoding="utf-8")
print("participant: --wait-for installed")

# --- scheduler: pass it through --------------------------------------------
sched = SCHED.read_text(encoding="utf-8")
OLD_SPAWN = '''        sleep_seconds: float = 0.0,
        extra_env: dict | None = None,
'''
NEW_SPAWN = '''        sleep_seconds: float = 0.0,
        wait_for: str = "",
        wait_timeout: float = 60.0,
        extra_env: dict | None = None,
'''
if OLD_SPAWN not in sched:
    print("SPAWN PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_SPAWN, NEW_SPAWN, 1)

OLD_ARGV = '''        if sleep_seconds:
            argv.extend(["--sleep-seconds", str(sleep_seconds)])
'''
NEW_ARGV = '''        if sleep_seconds:
            argv.extend(["--sleep-seconds", str(sleep_seconds)])
        if wait_for:
            argv.extend(["--wait-for", str(wait_for), "--wait-timeout", str(wait_timeout)])
'''
if OLD_ARGV not in sched:
    print("ARGV PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_ARGV, NEW_ARGV, 1)

NEW_L9C = '''def case_f_l9c(run: CaseRun) -> None:
    """A user pause DURING our scope, in its DISTINGUISHABLE form (F-L9c).

    A human running ``worker-pause`` only flips ``desired_state`` on the wiki side,
    which our ledger cannot see - that is the I-04-C section 8 O-2 limitation, and it
    is registered as a cross-repo dependency rather than papered over here.  The
    DISTINGUISHABLE form is the one where the user's action also invalidates our
    ownership evidence: the operator pauses the worker and removes the ownership
    record our marker backed (W7/T10).  The tool must then NOT resume the user's
    pause, must not fabricate new ownership evidence, and must say so.

    A parks in the SCOPE BODY until the signal file appears, so the ledger is edited
    between A's enter and A's release without instrumenting either.
    """
    signal = run.dir / "signal.edit"
    run.spawn(
        "A",
        resume_wait=0.2,
        graceful=0.2,
        wait_for=str(signal),
    )
    assert run.wait_snapshot("A"), "A never reached the scope body"
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
        "owner_record": payload.get("owner"),
        "worker_state": _read_json(run.state),
    }
    run.state.write_text(
        json.dumps({"desired_state": "paused", "runtime_state": "stopped"}), encoding="utf-8"
    )
    if run.owner.exists():
        run.owner.unlink()
    # Rewrite ONLY the owner field: schema, generation, entries and the resume
    # obligation stay exactly as the code under test wrote them, so this case tests an
    # ownership-evidence change rather than a hand-made ledger.
    payload["owner"] = None
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["user_action"] = {
        "owner_marker_removed": not run.owner.exists(),
        "owner_record": payload.get("owner"),
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
    }
    signal.write_text("edit", encoding="utf-8")
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

    A third party replaces the ownership record while A is parked in the scope body,
    i.e. after A's lease is durable and before A releases.  The third party is a pid
    that does NOT exist, so its record is neither attributable nor resumable: the
    release must keep it byte-for-byte instead of taking the cycle over - taking it
    over would resume a pause this tool never created (a user's, in the worst case).
    """
    signal = run.dir / "signal.edit"
    run.spawn(
        "A",
        resume_wait=0.2,
        graceful=0.2,
        wait_for=str(signal),
    )
    assert run.wait_snapshot("A"), "A never reached the scope body"
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
        "worker_state": _read_json(run.state),
    }
    signal.write_text("edit", encoding="utf-8")
    run.reap("A")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount) if run.refcount.is_file() else "<absent>",
        "payload": _read_json(run.refcount),
        "worker_state": _read_json(run.state),
    }
'''

for name, new in (("case_f_l9c", NEW_L9C), ("case_f_l8d", NEW_L8D)):
    pattern = re.compile(rf"^def {name}\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
    match = pattern.search(sched)
    if not match:
        print(f"PATTERN NOT FOUND: {name}")
        sys.exit(1)
    sched = sched[: match.start()] + new + "\n\n" + sched[match.end() :]
    print(f"replaced {name}")

# --- scheduler: a helper that waits for the participant's scope-body snapshot ---
OLD_HELPER = '''    def report(self, tag: str) -> dict:
        return _read_json(self.dir / f"report.{tag}.json") or {}
'''
NEW_HELPER = '''    def report(self, tag: str) -> dict:
        return _read_json(self.dir / f"report.{tag}.json") or {}

    def wait_snapshot(self, tag: str, timeout: float = 30.0) -> bool:
        """Wait until the participant is parked in its scope body.

        The participant writes ``signal.<tag>.ready`` just before it starts waiting,
        so this observes a real state instead of guessing a sleep.
        """
        path = self.dir / f"signal.{tag}.ready"
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            if path.exists():
                return True
            time.sleep(0.005)
        return False
'''
if OLD_HELPER not in sched:
    print("HELPER PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_HELPER, NEW_HELPER, 1)
SCHED.write_text(sched, encoding="utf-8")
print("scheduler: wait_snapshot installed")

# --- participant: publish the ready marker just before waiting ---
part = PART.read_text(encoding="utf-8")
OLD_MARK = '''                signal = Path(args.wait_for)
                report["waiting_for"] = str(signal)
'''
NEW_MARK = '''                signal = Path(args.wait_for)
                report["waiting_for"] = str(signal)
                (signal.parent / f"signal.{args.tag}.ready").write_text("ready", encoding="utf-8")
'''
if OLD_MARK not in part:
    print("MARK PATTERN NOT FOUND")
    sys.exit(1)
part = part.replace(OLD_MARK, NEW_MARK, 1)
PART.write_text(part, encoding="utf-8")
print("participant: ready marker installed")
