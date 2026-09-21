"""I-14-C harness: drive the REAL worker exception exit under a stub session.

Nothing here is imported by the product.  The stub session/control doubles are
imported from the product's own contract test module
(CW/tests/contract/test_source_catalog_worker_bootstrap.py) so that this harness
does not fork a second, divergent definition of "the real exit path".

Usage (argv is ASCII-only by contract):

    python drive_real_exit.py --scenario <name> --state-path <abs path> [--cli-exit]

--cli-exit additionally reproduces the CLI's generic handler
(cli.py:1551-1558) by printing error_taxonomy.structured_error(exc) to stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from run_guard import REFUSAL_EXIT, guard_run_dir

RE_RAISED_SENTINEL = 3
MISSING_CAUSE_SENTINEL = 4

# r2: the reviewer's synthetic credential (39 chars, no whitespace).  Kept in one
# place so the scenario, the oracle (N5c/N5d), the rule table and the probe agree.
_REVIEWER_SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"

SCENARIOS = {
    # name: (top message, optional cause message, optional middle cause message)
    "token-in-message": ("Authorization: Bearer SYNTHETIC_AUDIT_TOKEN rejected by provider", None, None),
    # r2 (review F-REV-D-01): the scheme word and the credential are on DIFFERENT
    # lines, which is what a wrapped Authorization header really looks like.  This is
    # the shape that persisted the credential in plaintext before the RULING-2 fix,
    # and the shape whose diagnostics the pre-fix base tree deleted.  The credential
    # is the reviewer's synthetic 39-char one (no whitespace); it is obviously fake by
    # construction, and run_exit_probe.py greps for its absence in every produced file.
    "bearer-newline": ("Authorization: Bearer\n" + _REVIEWER_SECRET + "\ndoc=17",
                       None, None),
    "nested-cause": (
        "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
        "Authorization: Bearer SYNTHETIC_AUDIT_TOKEN",
        None,
    ),
    "nested-cause-deep": (
        "stage=acquisition code=adapter_or_staging_failed request_id=req-SYNTH-0002",
        "adapter command failed: token=SYNTHETIC_AUDIT_TOKEN",
        "Authorization: Bearer SYNTHETIC_AUDIT_TOKEN",
    ),
    "unknown-key": ("upload failed for digest=SYNTHETIC_AUDIT_TOKEN", None, None),
    "unknown-key-with-token": ("upload failed for token=SYNTHETIC_AUDIT_TOKEN", None, None),
    "plain": ("document not in catalog: doc-1", None, None),
    "truncation-boundary": (
        "start-" + ("x" * 170) + " token=SYNTHETIC_AUDIT_TOKEN " + ("y" * 120),
        None,
        None,
    ),
    # r2/F-I14C-05: quoted value the 200-char cut leaves unterminated.  This is the
    # shape for which "redact before truncate" is load-bearing.
    "quoted-truncation-boundary": ('password: "' + ("Q" * 300) + '"', None, None),
}


def _build_exception(name: str) -> BaseException:
    """Build the chained exception object without materialising a traceback."""
    top, cause, middle = SCENARIOS[name]
    exc = RuntimeError(top)
    inner: BaseException | None = None
    if cause is not None:
        inner = ValueError(cause)
    if middle is not None:
        outer = KeyError(middle)
        outer.__cause__ = ValueError(cause) if cause else None
        outer.__suppress_context__ = True
        inner = outer
    if inner is not None:
        exc.__cause__ = inner
        exc.__suppress_context__ = True
    return exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--src", required=True)
    parser.add_argument("--tests-dir", required=True)
    parser.add_argument("--cli-exit", action="store_true")
    args = parser.parse_args(argv)

    # Binding guard (r5: shared with run_real_cli_exit.py, see run_guard.py).
    # Product paths are ALWAYS refused; a non-product scratch root may be declared through
    # I14C_RUN_ROOT so that an independent reviewer can run the subprocess-backed cases from
    # their own directory.  Refusal exit code stays 97.
    run_dir = guard_run_dir(args.run_dir)
    if run_dir is None:
        return REFUSAL_EXIT
    run_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, args.src)
    sys.path.insert(0, args.tests_dir)

    from company_wiki.source_catalog.worker import SourceCatalogWorker, WorkerConfig

    # Product-provided test doubles: _ControlStub, _StoppingSession, _make_worker.
    import test_source_catalog_worker_bootstrap as product_doubles

    state_path = run_dir / "worker_state.json"
    worker = product_doubles._make_worker(run_dir)
    worker.state_path = state_path

    raised = _build_exception(args.scenario)

    class _ExplodingSession(product_doubles._StoppingSession):
        """Same surface as the product doubles, but raises our synthetic exception."""

        def wait(self, _seconds):
            raise raised

    control = product_doubles._ControlStub(_ExplodingSession())

    try:
        worker.run_forever(control=control)
    except BaseException as exc:  # noqa: BLE001 - this IS the exit under test
        if args.cli_exit:
            # Version-agnostic reproduction of the CLI's generic handler.
            #
            # r1 review finding F-I14C-06: this branch used to import
            # ``redact_text`` unconditionally, so against the PRE-fix tree it
            # raised ImportError and the ImportError traceback - not the product -
            # produced the stderr marker hit.  The redactor is now imported
            # defensively: absent helper => leave the message as the product would,
            # which is exactly the state under test.
            from company_wiki.source_catalog.error_taxonomy import structured_error

            envelope = structured_error(exc)
            try:
                from company_wiki.source_catalog.observability import redact_text
            except ImportError:
                pass                      # pre-fix tree: no redactor exists yet
            else:
                envelope["error"] = redact_text(envelope["error"])
            print(
                json.dumps(envelope, ensure_ascii=False, sort_keys=True),
                file=sys.stderr,
            )
        else:
            print("RE-RAISED:" + type(exc).__name__, file=sys.stderr)
        return RE_RAISED_SENTINEL
    print("NO-EXCEPTION", file=sys.stderr)
    return MISSING_CAUSE_SENTINEL


if __name__ == "__main__":
    raise SystemExit(main())
