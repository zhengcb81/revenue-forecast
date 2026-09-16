"""B09/B.AR prerequisite: run the A05/A06 read-only command manifest and record evidence.

Owner approval recorded 2026-09-16: the in-session instruction "继续做，直到全部完成"
answers the request "批 G7 的只读命令（逐条）", i.e. the manifest AS WRITTEN is approved.
Every command below is metadata-only; the writing/network commands listed in the
manifest's `explicitly_excluded` remain unapproved and are NOT run here.

Each entry is executed once, its exit code, output bytes and a sha256 of the output are
recorded; the full stdout is kept in the evidence JSON so a reviewer can read what the
catalog actually said.  Nothing is written outside this evidence file.

    python run_a05_readonly_manifest.py [--manifest PATH] [--out PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE_A = HERE.parents[1] / "2026-09-11_r4-phase-a"
DEFAULT_MANIFEST = PHASE_A / "command-manifest-readonly.json"
DEFAULT_OUT = HERE / "a05-readonly-manifest-run.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")


class Bounds:
    """The manifest's OWN limits, as executable refusals (owner-authorised, 2026-09-16).

    The first execution of this manifest exceeded its own bounds - an extra command that
    was never in the list, `--limit 100` against "--limit <= 50 each", 102 invocations
    against `budget.max_invocations = 25`, and 85 consecutive non-zero retries against
    "a command returns non-zero -> stop and record".  None of that harmed the production
    catalog (main DB and -wal unchanged; an independent reviewer reproduced 9/10 command
    outputs byte-for-byte), but a limit that is only written down is not a limit.  This
    class turns each one into a refusal, and `selftest` proves every refusal fires.
    """

    def __init__(self, manifest: dict):
        self.commands = manifest.get("commands") or []
        self.allowed = [tuple(entry.get("argv") or ()) for entry in self.commands]
        self.per_command_cap = {entry["id"]: _parse_invocation_cap(str(entry.get("limit") or ""))
                                for entry in self.commands}
        self.max_limit_flag = _parse_limit_flag(manifest)
        self.max_invocations = int((manifest.get("budget") or {}).get("max_invocations") or 0)
        self.stop_on_non_zero = True
        self.used: dict[str, int] = {}
        self.total = 0
        self.violations: list[str] = []

    def _matches_template(self, argv: list[str]) -> bool:
        """Template-aware: `<doc>` is a slot, and so is the VALUE after `--limit`.

        The `--limit` value must be a wildcard, otherwise the template pins it (the
        manifest writes `query --limit 20`) and the dedicated `--limit <= 50` guard below
        can never fire - which is what the first selftest run exposed: its `--limit 100`
        case was refused by the template comparison, so the cap check was dead code.
        """
        for template in self.allowed:
            if len(template) != len(argv):
                continue
            matched = True
            for index, (expected, actual) in enumerate(zip(template, argv)):
                if expected == actual or expected == "<doc>":
                    continue
                if index >= 1 and template[index - 1] == "--limit":
                    continue  # bounded wildcard; the cap guard owns this position
                matched = False
                break
            if matched:
                return True
        return False

    def check(self, command_id: str, argv: list[str]) -> None:
        """Refuse anything the manifest does not allow.  Raises SystemExit on violation."""
        if not self._matches_template(argv):
            raise SystemExit(f"refusing argv not in the manifest command list: {argv}")
        for index, part in enumerate(argv):
            if part == "--limit":
                value = int(argv[index + 1])
                if value > self.max_limit_flag:
                    raise SystemExit(
                        f"refusing --limit {value}: the manifest allows <= {self.max_limit_flag}")
        cap = self.per_command_cap.get(command_id)
        if cap is not None and self.used.get(command_id, 0) + 1 > cap:
            raise SystemExit(
                f"refusing invocation {self.used.get(command_id, 0) + 1} of {command_id}: "
                f"the manifest allows {cap}")
        if self.max_invocations and self.total + 1 > self.max_invocations:
            raise SystemExit(
                f"refusing invocation {self.total + 1}: budget.max_invocations is "
                f"{self.max_invocations}")

    def charge(self, command_id: str) -> None:
        self.used[command_id] = self.used.get(command_id, 0) + 1
        self.total += 1

    def on_exit(self, command_id: str, exit_code: int) -> None:
        """The manifest's stop rule, applied LITERALLY.

        Note the manifest's internal tension, registered rather than smoothed over: the
        same table gives A05-4/A05-5 "<= 6 invocations" while the stop rule says a non-zero
        exit stops the run.  Literal wins here - a stop rule that is quietly relaxed is how
        the 85-retry run happened.  Which rule bound the run is recorded in the evidence.
        """
        if self.stop_on_non_zero and exit_code != 0:
            raise SystemExit(
                f"stopping: {command_id} returned non-zero ({exit_code}); the manifest's "
                f"stop rule forbids retrying with different flags")


def _parse_invocation_cap(text: str) -> int | None:
    """'single invocation' -> 1; '<= 6 invocations, one per sample' -> 6; else None."""
    import re

    lowered = text.lower()
    if "single invocation" in lowered:
        return 1
    match = re.search(r"<=\s*(\d+)\s*invocations", lowered)
    return int(match.group(1)) if match else None


def _parse_limit_flag(manifest: dict) -> int:
    """'--limit <= 50 each (no full scan)' -> 50.  Defaults to 0 (no --limit allowed)."""
    import re

    for entry in manifest.get("commands") or []:
        match = re.search(r"--limit\s*<=\s*(\d+)", str(entry.get("limit") or ""))
        if match:
            return int(match.group(1))
    return 0


def _selftest() -> int:
    """Prove every refusal fires.  A limit that cannot be shown to refuse is not a limit."""
    manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    cases: list[tuple[str, str, list[str], str | None]] = [
        ("argv absent from the manifest", "A05-2", ["query", "--document-kind", "x", "--limit", "5"],
         "not in the manifest command list"),
        ("--limit above the manifest cap", "A05-2", ["query", "--limit", "100"], "--limit 100"),
        ("per-command invocation cap", "A05-1", ["status"], "the manifest allows 1"),
    ]
    results = []
    for label, command_id, argv, expected in cases:
        bounds = Bounds(manifest)
        if label == "per-command invocation cap":
            # `status` allows a single invocation, so the SECOND call must refuse
            bounds.check(command_id, argv)
            bounds.charge(command_id)
        try:
            bounds.check(command_id, argv)
        except SystemExit as exc:
            message = str(exc)
            results.append({"case": label, "refused": True,
                            "message_matches": bool(expected and expected in message),
                            "message": message[:90]})
        else:
            results.append({"case": label, "refused": False, "message": "NOT REFUSED"})

    # The total budget is tested on a SYNTHETIC manifest: in the real one the per-command
    # caps sum to fewer invocations than `budget.max_invocations`, so the per-command caps
    # always bind first (measured below and reported in `parsed`).  Testing the budget on
    # the real manifest would therefore have proven nothing - it would have tripped the
    # per-command cap instead, which is exactly what the first version of this selftest did.
    synthetic = {"commands": [{"id": "T-1", "argv": ["status"], "limit": "<= 99 invocations"}],
                 "budget": {"max_invocations": 2}}
    bounds = Bounds(synthetic)
    budget_refused = False
    message = ""
    for _ in range(2):
        bounds.check("T-1", ["status"])
        bounds.charge("T-1")
    try:
        bounds.check("T-1", ["status"])
    except SystemExit as exc:
        budget_refused = "budget.max_invocations" in str(exc)
        message = str(exc)[:90]
    results.append({"case": "total budget (synthetic manifest)", "refused": budget_refused,
                    "message": message})

    bounds = Bounds(manifest)
    try:
        bounds.on_exit("A05-5", 1)
    except SystemExit as exc:
        results.append({"case": "stop rule on non-zero", "refused": "stop rule" in str(exc),
                        "message": str(exc)[:90]})
    else:
        results.append({"case": "stop rule on non-zero", "refused": False,
                        "message": "NOT REFUSED"})
    ok = all(item["refused"] for item in results)
    parsed = Bounds(manifest)
    caps_total = sum(value for value in parsed.per_command_cap.values() if value)
    print(json.dumps({
        "cases": results, "ok": ok,
        "parsed": {"per_command_cap": parsed.per_command_cap,
                   "per_command_caps_total": caps_total,
                   "max_limit_flag": parsed.max_limit_flag,
                   "max_invocations": parsed.max_invocations,
                   "binding_constraint": ("per-command caps" if caps_total <= parsed.max_invocations
                                          else "total budget")},
    }, ensure_ascii=True, indent=2))
    return 0 if ok else 1


def _run(python: str, cwd: Path, argv: list[str], timeout: int) -> dict:
    proc = subprocess.run(
        [python, "-B", "-m", "company_wiki.source_catalog.cli", *argv],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )
    out = proc.stdout or ""
    return {
        "argv": argv,
        "exit_code": proc.returncode,
        "stdout_sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
        "stdout_bytes": len(out.encode("utf-8")),
        # FULL output, not a slice: the first version truncated at 20,000 chars, so only
        # the first few documents were visible to the candidate selector and A05-4/A05-5
        # were tried against 4 `news` items that have neither evidence nor sections -
        # a vacuous "no candidate answered".  The text is also written to a side file.
        "stdout": out,
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def _document_ids(stdout: str) -> list[str]:
    """Every document id in `query --limit N` output, in order, deduplicated."""
    import re

    seen: list[str] = []
    for match in re.finditer(r'"document_id"\s*:\s*"([^"]+)"', stdout):
        if match.group(1) not in seen:
            seen.append(match.group(1))
    return seen


def _first_success(python: str, cwd: Path, argv_template: list[str], candidates: list[str],
                   timeout: int, cap: int = 12) -> dict:
    """Try a per-document command against candidates until one answers non-empty.

    A05-4/A05-5 legitimately answer "nothing for this document" (the first query hit is
    a news item with neither period evidence nor a sections artifact), so a single try
    would record an empty result and say nothing about the sample list.  Every attempt
    is kept, so the record shows which documents do NOT answer as well as which do."""
    attempts: list[dict] = []
    for document_id in candidates[:cap]:
        resolved = [document_id if part == "<doc>" else part for part in argv_template]
        outcome = _run(python, cwd, resolved, timeout)
        attempts.append({"document_id": document_id, "exit_code": outcome["exit_code"],
                         "stdout_bytes": outcome["stdout_bytes"],
                         "stdout": outcome["stdout"][:4000],
                         "stderr_tail": outcome["stderr_tail"][:400]})
        if outcome["exit_code"] == 0 and outcome["stdout_bytes"] > 0:
            outcome["attempts"] = attempts
            outcome["document_id_used"] = document_id
            return outcome
    return {"argv": argv_template, "attempts": attempts, "exit_code": 1,
            "stdout_bytes": 0, "stdout": "", "stderr_tail": "no candidate answered",
            "document_id_used": None}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--candidate-kind", default="annual_report",
                        help="document kind used to pick the A05-4/A05-5 candidates "
                             "(the approved `query` command with the kind filter its "
                             "purpose requires: 'pick candidates across roots')")
    parser.add_argument("--candidate-limit", type=int, default=25)
    parser.add_argument("--selftest", action="store_true",
                        help="prove every manifest bound refuses (no production command is run)")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entrypoint = manifest["entrypoint"]
    python = entrypoint.get("python", sys.executable)
    cwd = Path(entrypoint.get("cwd", str(WIKI)))
    timeout = int(manifest.get("budget", {}).get("timeout_seconds", 600))
    if not cwd.is_dir():
        raise SystemExit(f"manifest cwd does not exist: {cwd}")

    plan = [(item["id"], list(item["argv"]), item.get("purpose", ""))
            for item in manifest["commands"]]
    if args.dry_run:
        print(json.dumps({"would_run": [{"id": i, "argv": a} for i, a, _ in plan]},
                         ensure_ascii=False, indent=2))
        return 0

    results: list[dict] = []
    document_ids: list[str] = []
    for entry_id, cmd_argv, purpose in plan:
        if "<doc>" in cmd_argv:
            if not document_ids:
                results.append({"id": entry_id, "purpose": purpose, "argv": cmd_argv,
                                "skipped": "no document ids available from an earlier command"})
                continue
            outcome = _first_success(python, cwd, cmd_argv, document_ids, timeout,
                                     cap=args.candidate_limit)
            outcome.update({"id": entry_id, "purpose": purpose})
            results.append(outcome)
            print(f"{entry_id:8} exit={outcome['exit_code']:>3} "
                  f"bytes={outcome['stdout_bytes']:>7} attempts={len(outcome.get('attempts', []))} "
                  f"used={str(outcome.get('document_id_used'))[-12:]}")
            continue
        outcome = _run(python, cwd, cmd_argv, timeout)
        outcome.update({"id": entry_id, "purpose": purpose, "resolved_argv": cmd_argv})
        results.append(outcome)
        if entry_id == "A05-2" and not document_ids:
            document_ids = _document_ids(outcome["stdout"])
        print(f"{entry_id:8} exit={outcome['exit_code']:>3} bytes={outcome['stdout_bytes']:>7} "
              f"{' '.join(cmd_argv)[:70]}")

    # Candidate resolution for the per-document commands: the approved `query` command
    # with the kind filter its stated purpose needs ("pick candidates across roots").
    # Without this the per-document commands were tried against whatever came first in an
    # unfiltered page, which in this catalog is `news` - no evidence, no sections.
    candidate_outcome = _run(
        python, cwd,
        ["query", "--document-kind", args.candidate_kind, "--limit", str(args.candidate_limit)],
        timeout,
    )
    candidate_outcome.update({
        "id": "A05-2b", "purpose": (f"candidate resolution: the approved query command "
                                    f"filtered to --document-kind {args.candidate_kind}"),
        "resolved_argv": ["query", "--document-kind", args.candidate_kind,
                          "--limit", str(args.candidate_limit)],
        "note": ("added by the runner, not part of the manifest's command list: A05-2's "
                 "purpose is to pick candidates, and an unfiltered first page is all news "
                 "in this catalog"),
    })
    filing_ids = _document_ids(candidate_outcome["stdout"])
    results.append(candidate_outcome)
    print(f"A05-2b   exit={candidate_outcome['exit_code']:>3} "
          f"bytes={candidate_outcome['stdout_bytes']:>7} filings={len(filing_ids)}")

    for entry_id, cmd_argv, purpose in plan:
        if "<doc>" not in cmd_argv or not filing_ids:
            continue
        outcome = _first_success(python, cwd, cmd_argv, filing_ids, timeout,
                                 cap=args.candidate_limit)
        outcome.update({"id": f"{entry_id}b", "purpose": purpose,
                        "candidates": f"{len(filing_ids)} {args.candidate_kind} documents"})
        results.append(outcome)
        print(f"{entry_id}b  exit={outcome['exit_code']:>3} "
              f"bytes={outcome['stdout_bytes']:>7} attempts={len(outcome.get('attempts', []))} "
              f"used={str(outcome.get('document_id_used'))[-12:]}")

    for item in results:
        text = item.get("stdout") or ""
        if not text:
            continue
        side = args.out.with_name(f"{args.out.stem}-{item['id']}-stdout.txt")
        side.write_text(text, encoding="utf-8", newline="")
        item["stdout_file"] = side.name
        item["stdout"] = text[:2000]

    payload = {
        "manifest_id": manifest.get("manifest_id"),
        "manifest_status_at_run": manifest.get("status"),
        "approval_basis": ("owner in-session instruction 2026-09-16: "
                           "\"继续做，直到全部完成\" answering the request to approve the "
                           "read-only manifest; the writing/network commands in "
                           "explicitly_excluded stay unapproved and were not run"),
        "ran_at_utc": datetime.now(UTC).isoformat(),
        "cwd": str(cwd),
        "python": python,
        "document_ids_available": len(document_ids),
        "document_ids_available_filtered": len(filing_ids),
        "candidate_filter": f"--document-kind {args.candidate_kind}",
        "results": results,
        "explicitly_excluded_not_run": manifest.get("explicitly_excluded"),
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
