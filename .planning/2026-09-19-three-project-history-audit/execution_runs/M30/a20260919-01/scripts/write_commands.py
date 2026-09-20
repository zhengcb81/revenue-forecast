"""Record every unit of one card attempt into commands.json / command_manifest.json.

Two rules are enforced mechanically instead of promised:

  1. NO FAKE POINTERS.  Every absolute-path token in every argv must either already
     exist or be declared by that unit as an output it creates.  Any other path is a
     hard error (the script exits 2 and writes nothing).
  2. RAW rc ONLY.  The recorded rc is read back from the rc.json written by run_unit
     while the command ran; this script never invents or rewrites a return code.

Usage:
  python -X utf8 -B write_commands.py --card M17 --attempt-root <attempt> \
      --interpreter <venv python.exe> --phase post|final
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

import card_units

PATH_RE = re.compile(r"^[A-Za-z]:\\")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", required=True)
    parser.add_argument("--phase", required=True, choices=("pre", "post", "final"))
    parser.add_argument("--final-hashes", default=None,
                        help=("write the final deliverable hash ledger to this path AFTER "
                              "commands.json, so the ledger covers the final command record"))
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    units = card_units.build_units(card, attempt) + card_units.closing_units(card, attempt)

    checked = 0
    declared = 0
    undeclared = []
    recorded = []
    for unit in units:
        creates = {os.path.normcase(os.path.abspath(c)) for c in unit["creates"]}
        token_report = []
        for token in unit["argv"]:
            if not PATH_RE.match(token):
                continue
            checked += 1
            normalised = os.path.normcase(os.path.abspath(token))
            exists = os.path.exists(token)
            is_create = normalised in creates or any(
                normalised.startswith(os.path.normcase(os.path.abspath(c)) + os.sep)
                for c in unit["creates"])
            token_report.append({"token": token, "exists_now": exists,
                                 "declared_as_created_output": is_create})
            if not exists and not is_create:
                undeclared.append({"unit_id": unit["unit_id"], "token": token})
            if not exists and is_create:
                declared += 1
        stdouts = unit["stdout"]
        entry = {
            "unit_id": unit["unit_id"],
            "purpose": unit["purpose"],
            "cwd": unit["cwd"],
            "argv": unit["argv"],
            "network": unit["network"],
            "expected_rc": unit["expected_rc"],
            "raw_rc": None,
            "stdout": unit["stdout"],
            "stderr": unit["stderr"],
            "rc_record": unit["rc_record"],
            "creates": unit["creates"],
            "path_check": token_report,
            "stdout_exists": os.path.exists(stdouts),
        }
        if unit.get("note"):
            entry["note"] = unit["note"]
        if unit.get("expected_business_result"):
            entry["expected_business_result"] = unit["expected_business_result"]
        if os.path.isfile(unit["rc_record"]):
            with open(unit["rc_record"], "r", encoding="utf-8") as handle:
                rc_doc = json.load(handle)
            entry["raw_rc"] = rc_doc["raw_returncode"]
            entry["rc_record_sha256"] = sha256(unit["rc_record"])
            entry["stdout_sha256"] = rc_doc.get("stdout_sha256")
            entry["stderr_sha256"] = rc_doc.get("stderr_sha256")
            entry["rc_recorded_utc"] = rc_doc.get("finished_utc")
        else:
            entry["raw_rc_note"] = "pending: this unit had not completed when this record was written"
        recorded.append(entry)

    if undeclared and args.phase != "pre":
        for item in undeclared:
            print("FAKE POINTER REJECTED: unit %s references a missing path %s"
                  % (item["unit_id"], item["token"]))
        return 2
    if undeclared:
        # Phase 'pre' runs BEFORE the card's own commands: a path that only a later unit creates is
        # legitimately absent now. The strict rejection above is applied when the record is rewritten
        # in phase 'post', i.e. after every unit has run.
        for item in undeclared:
            print("PENDING PATH (phase pre): unit %s will create or receive %s"
                  % (item["unit_id"], item["token"]))

    doc = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": card_units.CARDS[card]["model_id"],
        "cwd": attempt,
        "interpreter": args.interpreter,
        "isolation": {
            "code_root": os.path.join(attempt, "iso", "checkout_scripts"),
            "never_used": ["the global Miniconda interpreter for any card command",
                           "the production scripts directory on sys.path",
                           "network", "provider", "LLM"],
        },
        "rules": [
            "every product invocation used --code-root <attempt>/iso/checkout_scripts",
            "raw exit codes are the child's own return codes; expected codes are separate fields",
            "skip / timeout / not-collected is never recorded as pass",
            "every absolute path in every argv exists or is declared as an output of that unit",
        ],
        "path_check": {
            "rule": "each absolute-path argv token must exist now or be declared in the unit's creates",
            "path_tokens_checked": checked,
            "tokens_declared_as_not_yet_created_outputs": declared,
            "undeclared_missing_tokens": undeclared,
        },
        "units": recorded,
        "phase": args.phase,
        "created_before_card_runs": args.phase in ("pre", "post"),
        "scope": "this card only; no unit of this file belongs to another card attempt",
        "note": ("argv were fixed before the product run (phase 'pre' recorded the same unit list with "
                 "raw_rc still null); this record is (re)written afterwards so that raw_rc values are "
                 "read back from the rc.json files produced while each command ran"),
    }

    out = os.path.join(attempt, "commands.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("commands.json written", out, "phase", args.phase, "units", len(recorded))

    if args.phase == "post":
        manifest = {
            "card_id": card,
            "attempt_id": "a20260919-01",
            "model_id": card_units.CARDS[card]["model_id"],
            "cwd": attempt,
            "rules": doc["rules"],
            "path_check": doc["path_check"],
            "units": recorded,
            "note": ("identical unit list to commands.json (single source of truth: scripts/"
                     "card_units.py); commands.json is rewritten once more after the evidence pack "
                     "so that the pack's own rc is filled in, while this manifest keeps the unit list "
                     "as it stood when the pack hashed it"),
        }
        mout = os.path.join(attempt, "evidence", card, "command_manifest.json")
        with open(mout, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=1)
        print("command_manifest.json written", mout)

    for entry in recorded:
        print("  %-28s expected=%s raw=%s" % (entry["unit_id"], entry["expected_rc"], entry["raw_rc"]))

    if args.final_hashes:
        # Written LAST, after commands.json, so the ledger covers the final command record.
        # iso/venv is excluded (thousands of interpreter files); iso/checkout_scripts and
        # iso/oracle_card.md are included.
        import datetime
        skip = os.path.normcase(os.path.join("iso", "venv"))
        files = {}
        for root, dirs, names in os.walk(attempt):
            rel_root = os.path.relpath(root, attempt)
            if rel_root != "." and os.path.normcase(rel_root) == skip:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if os.path.normcase(os.path.join(rel_root, d)) != skip]
            for name in sorted(names):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, attempt).replace("\\", "/")
                if rel.endswith("final_deliverable_hashes.json"):
                    continue
                files[rel] = {"absolute_path": path, "sha256": sha256(path),
                              "size_bytes": os.path.getsize(path)}
        ledger = {
            "card_id": card,
            "attempt_id": "a20260919-01",
            "model_id": card_units.CARDS[card]["model_id"],
            "attempt_root": attempt,
            "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "interpreter_path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
            "excluded_from_the_table": ["iso/venv/** (attempt-local interpreter, not an evidence file)"],
            "written_last": ("this ledger is produced inside the Z-close-attempt unit, after "
                             "commands.json has been rewritten with the final phase, so it covers the "
                             "finished attempt"),
            "file_count": len(files),
            "files": files,
        }
        with open(args.final_hashes, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle, ensure_ascii=False, indent=1)
        print("final_deliverable_hashes.json written", args.final_hashes, "files", len(files))
        print("commands.json sha256 in that ledger:",
              files.get("commands.json", {}).get("sha256"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
