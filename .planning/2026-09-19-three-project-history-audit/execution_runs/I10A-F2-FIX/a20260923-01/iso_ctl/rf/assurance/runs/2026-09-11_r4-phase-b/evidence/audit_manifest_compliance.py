"""Retrospective compliance audit: the manifest's bounds vs what was actually executed.

Written after `B.VR-bar` adjudicated the A05 execution as OVERREACH.  The run is NOT
rewritten here - `a05-readonly-manifest-run.json` stays exactly as produced - this tool
re-computes the declared-vs-actual comparison from that evidence and from the manifest, so
the violation is a NUMBER anyone can check instead of a paragraph anyone must trust.

Read-only: it opens two JSON files and writes only `--out`.

    python audit_manifest_compliance.py [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "a05-readonly-manifest-run.json"
MANIFEST = HERE.parents[1] / "2026-09-11_r4-phase-a" / "command-manifest-readonly.json"


def _result_invocations(item: dict) -> int:
    """One result is one execution, plus one per recorded attempt."""
    attempts = item.get("attempts")
    if attempts is None:
        return 1
    return len(attempts) or 1


def _matches_template(argv: list[str], template: tuple) -> bool:
    """Same wildcard rule the enforced runner uses: `<doc>`, and the value after --limit."""
    if len(argv) != len(template):
        return False
    for index, (expected, actual) in enumerate(zip(template, argv)):
        if expected == actual or expected == "<doc>":
            continue
        if index >= 1 and template[index - 1] == "--limit":
            continue
        return False
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=HERE / "b-ar-manifest-compliance.json")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    run = json.loads(args.run.read_text(encoding="utf-8"))

    declared = {entry["id"]: entry for entry in manifest.get("commands") or []}
    budget = int((manifest.get("budget") or {}).get("max_invocations") or 0)
    limit_cap = 0
    for entry in manifest.get("commands") or []:
        import re

        match = re.search(r"--limit\s*<=\s*(\d+)", str(entry.get("limit") or ""))
        if match:
            limit_cap = int(match.group(1))
            break

    # Group executions by the MANIFEST command they belong to: the runner labels a second
    # batch `A05-5b`, which is the same command run again, not a new command.
    per_command: dict[str, list[dict]] = {}
    extra_commands: list[dict] = []
    for item in run.get("results") or []:
        command_id = str(item.get("id") or "")
        base = command_id.rstrip("b") if command_id.endswith("b") else command_id
        item_argv = [str(part) for part in (item.get("argv") or item.get("resolved_argv") or [])]
        # "Extra" is decided by ARGV, not by the id label: the runner called a second batch
        # `A05-5b`, which is the same command run again.  `A05-2b` looks similar but its argv
        # (`query --document-kind annual_report --limit 100`) matches NO declared template.
        # An extra is counted ONCE, here: classifying it in a second pass as well made the
        # first version of this audit report 103 invocations where the reviewer measured 102.
        if item_argv and not any(_matches_template(item_argv, tuple(entry.get("argv") or ()))
                                 for entry in manifest.get("commands") or []):
            extra_commands.append({"id": command_id, "argv": item_argv,
                                   "invocations": _result_invocations(item)})
            continue
        if base not in declared:
            extra_commands.append({"id": command_id, "argv": item_argv,
                                   "invocations": _result_invocations(item)})
            continue
        per_command.setdefault(base, []).append(item)

    violations: list[dict] = []
    rows: list[dict] = []
    total_invocations = 0
    for command_id, entry in declared.items():
        items = per_command.get(command_id, [])
        invocations = sum(_result_invocations(item) for item in items)
        total_invocations += invocations
        exits = [item.get("exit_code") for item in items]
        nonzero = sum(1 for item in items for _ in range(_result_invocations(item))
                      if item.get("exit_code") != 0)
        cap = None
        import re

        limit_text = str(entry.get("limit") or "").lower()
        if "single invocation" in limit_text:
            cap = 1
        else:
            match = re.search(r"<=\s*(\d+)\s*invocations", limit_text)
            cap = int(match.group(1)) if match else None
        row = {"id": command_id, "declared_limit": entry.get("limit"),
               "declared_cap": cap, "invocations": invocations, "exit_codes": exits,
               "nonzero_invocations": nonzero}
        rows.append(row)
        if cap is not None and invocations > cap:
            violations.append({"kind": "per_command_invocations", "id": command_id,
                               "declared": cap, "actual": invocations})
        if nonzero > 1:
            # Every non-zero AFTER the first one is a retry the stop rule forbids.
            violations.append({"kind": "stop_rule_retries_after_nonzero", "id": command_id,
                               "extra_nonzero_invocations": nonzero - 1})

    for item in run.get("results") or []:
        item_argv = [str(part) for part in (item.get("argv") or item.get("resolved_argv") or [])]
        for index, part in enumerate(item_argv):
            if part == "--limit" and index + 1 < len(item_argv):
                value = int(item_argv[index + 1])
                if limit_cap and value > limit_cap:
                    violations.append({"kind": "limit_flag_above_cap", "id": item.get("id"),
                                       "declared": limit_cap, "actual": value})
    for extra in extra_commands:
        violations.append({"kind": "command_not_in_manifest", "id": extra["id"],
                           "argv": extra["argv"], "invocations": extra["invocations"]})
    for extra in extra_commands:
        total_invocations += extra["invocations"]
    if budget and total_invocations > budget:
        violations.append({"kind": "total_budget", "declared": budget,
                           "actual": total_invocations})

    payload = {
        "tool": "audit_manifest_compliance.py",
        "note": ("Retrospective read of the SAME evidence file (nothing is rewritten): the "
                 "manifest's declared bounds vs what was executed."),
        "manifest": {"id": manifest.get("manifest_id"), "status": manifest.get("status"),
                     "approval": manifest.get("approval"),
                     "declared_commands": sorted(declared),
                     "budget_max_invocations": budget, "limit_flag_cap": limit_cap,
                     "stop_rule": (manifest.get("stop_rules") or [None])[2]},
        "run": {"ran_at_utc": run.get("ran_at_utc"), "approval_basis": run.get("approval_basis"),
                "executed_results": len(run.get("results") or [])},
        "per_command": rows,
        "extra_commands_not_in_manifest": extra_commands,
        "total_invocations": total_invocations,
        "violations": violations,
        "compliant": not violations,
        "counts": dict(sorted(Counter(item["kind"] for item in violations).items())),
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({"compliant": payload["compliant"],
                      "total_invocations": total_invocations,
                      "budget": budget, "counts": payload["counts"],
                      "violations": violations}, ensure_ascii=True, indent=2))
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
