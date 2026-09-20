"""Audit every ``X.py:NNN`` document pointer inside one attempt (standard library only).

The independent review of 2026-09-20 raised the possibility of stale in-file line-number residue
in the hand-off documents. This script turns that concern into an executable check:

  * it extracts every ``<file>.py:<line>`` (or ``:start-end``) pointer from the attempt's
    documents and resolves it against, in order, the production tree, the attempt itself, the
    production ``scripts`` subtree, and - for references to sibling attempts' r3 tooling - the
    plan's ``execution_runs`` tree; a pointer counts as resolved only if the target really has at
    least that many lines;
  * it records the outcome of an explicit search for the five residue tokens the reviewer listed,
    excluding this audit script itself (which necessarily contains them as data);
  * it independently re-verifies the cross-batch M05-M08 r3 claims the F-02 correction relies on
    (``f07_enumerate.py:60`` really is ``spec.dimensions[driver]``; ``docfix_r3.json`` really
    records ``ratio_drivers_total_was 40`` -> ``now 41`` with
    ``missing_driver_added = direct_growth.growth_rate, domain (-1, inf)``), recording file hashes.

Writes ``evidence/<CARD>/doc_pointer_audit.json``. Prints ASCII only.
Exit codes: 0 all pointers resolve, 7 at least one pointer is dangling, 1 harness error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

POINTER = re.compile(r"([A-Za-z0-9_./\\-]+\.py):(\d+)(?:-(\d+))?")
RESIDUE_TOKENS = (":346", ":319", ":265", ":313", ":290")
SCAN_SUFFIXES = (".md", ".json", ".py", ".ps1", ".txt", ".diff")
SKIP_DIRS = ("iso/venv", "iso\\venv", "recovery/selfcheck", "recovery\\selfcheck", "__pycache__")
SELF_NAME = "audit_doc_pointers.py"
SELF_OUTPUT_NAME = "doc_pointer_audit.json"
CROSS_BATCH = (
    ("M05", "execution_runs/M05/a20260919-01/recovery/docfix-r3/f07_enumerate.py", 60,
     "dim = spec.dimensions[driver]"),
    ("M05", "execution_runs/M05/a20260919-01/evidence/M05/docfix_r3.json", None,
     "ratio_drivers_total_was 40 -> ratio_drivers_total_now 41, missing_driver_added "
     "direct_growth.growth_rate, domain (-1, inf)"),
)


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def line_count(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def find_bounded(root, basename, max_depth):
    """Bounded breadth-first search for a file with this basename."""
    frontier = [(root, 0)]
    hits = []
    while frontier:
        current, depth = frontier.pop(0)
        if depth > max_depth or not os.path.isdir(current):
            continue
        try:
            entries = sorted(os.listdir(current))
        except OSError:
            continue
        for name in entries:
            path = os.path.join(current, name)
            if name == basename and os.path.isfile(path):
                hits.append(path)
            elif os.path.isdir(path) and name not in ("venv", "__pycache__", ".git"):
                frontier.append((path, depth + 1))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--production-root",
                        default=os.path.join(os.environ["USERPROFILE"], "Projects",
                                             "revenue-forecast"))
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    plan = os.path.dirname(os.path.dirname(os.path.dirname(attempt)))
    evidence = os.path.join(attempt, "evidence", card)
    try:
        pointers = []
        residue_hits = []
        for root, dirs, files in os.walk(attempt):
            rel_root = os.path.relpath(root, attempt).replace("\\", "/")
            if any(rel_root.startswith(skip.replace("\\", "/")) for skip in SKIP_DIRS):
                dirs[:] = []
                continue
            for name in sorted(files):
                if not name.endswith(SCAN_SUFFIXES) or name.endswith(".pyc"):
                    continue
                path = os.path.join(root, name)
                if os.path.getsize(path) > 2_000_000:
                    continue
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
                rel = os.path.relpath(path, attempt).replace("\\", "/")
                if name not in (SELF_NAME, SELF_OUTPUT_NAME):
                    for token in RESIDUE_TOKENS:
                        if token in text:
                            residue_hits.append({"file": rel, "token": token})
                if name == SELF_NAME:
                    continue
                for match in POINTER.finditer(text):
                    target, first, last = match.group(1), int(match.group(2)), match.group(3)
                    pointers.append({"document": rel, "pointer": match.group(0),
                                     "target": target, "first_line": first,
                                     "last_line": int(last) if last else first})

        resolved, dangling = [], []
        for item in pointers:
            target = item["target"].replace("\\", "/")
            basename = os.path.basename(target)
            candidates = [
                ("production_root_direct", os.path.join(args.production_root, target)),
                ("attempt_direct", os.path.join(attempt, target)),
                ("production_scripts", os.path.join(args.production_root, "scripts", basename)),
                ("production_scripts_forecast",
                 os.path.join(args.production_root, "scripts", "forecast", basename)),
            ]
            hit = None
            how = None
            for label, candidate in candidates:
                if os.path.isfile(candidate):
                    hit, how = candidate, label
                    break
            if hit is None:
                found = find_bounded(os.path.join(args.production_root, "scripts"), basename, 3)
                if len(found) == 1:
                    hit, how = found[0], "production_scripts_search"
                elif len(found) > 1:
                    dangling.append(dict(item, reason="ambiguous basename under scripts/: %s"
                                                        % found))
                    continue
            if hit is None:
                found = find_bounded(os.path.join(plan, "execution_runs"), basename, 6)
                if len(found) >= 1:
                    hit, how = found[0], "plan_execution_runs_search"
                    if len(found) > 1:
                        how += " (first of %d matches)" % len(found)
            if hit is None:
                dangling.append(dict(item, reason="target file not found under the production "
                                                  "root, the attempt or the plan"))
                continue
            count = line_count(hit)
            entry = dict(item, resolved_path=hit, resolved_via=how, target_line_count=count,
                         ok=count >= item["last_line"])
            if entry["ok"]:
                resolved.append(entry)
            else:
                dangling.append(dict(entry, reason="target has fewer lines than the pointer"))

        unique = {}
        for item in resolved:
            unique[(item["document"], item["pointer"])] = item
        resolved_unique = [unique[key] for key in sorted(unique)]

        cross_batch = []
        for batch, rel, line_no, claim in CROSS_BATCH:
            path = os.path.join(plan, rel.replace("/", os.sep))
            entry = {"batch": batch, "path": rel, "claim": claim, "exists": os.path.isfile(path)}
            if entry["exists"]:
                entry["sha256"] = sha256_file(path)
                entry["line_count"] = line_count(path)
                if line_no is not None:
                    with open(path, "r", encoding="utf-8", errors="replace") as handle:
                        lines = handle.read().splitlines()
                    entry["line_checked"] = line_no
                    entry["line_text"] = lines[line_no - 1].strip() if line_no <= len(lines) else None
                    entry["line_matches_claim"] = entry["line_text"] == claim
                else:
                    with open(path, "r", encoding="utf-8", errors="replace") as handle:
                        text = handle.read()
                    entry["claims_found"] = {
                        "ratio_drivers_total_was_40": "\"ratio_drivers_total_was\": 40" in text,
                        "ratio_drivers_total_now_41": "\"ratio_drivers_total_now\": 41" in text,
                        "missing_driver_added": "direct_growth.growth_rate, domain (-1, inf)" in text,
                    }
                    entry["claims_all_present"] = all(entry["claims_found"].values())
            cross_batch.append(entry)

        report = {
            "card_id": card,
            "attempt": attempt,
            "rule": "every <file>.py:<line> pointer in this attempt's documents must resolve to an "
                    "existing file with at least that many lines; production and sibling-attempt "
                    "lookups are read-only",
            "pointer_count": len(pointers),
            "distinct_pointer_count": len(resolved_unique) + len(dangling),
            "distinct_pointers": resolved_unique,
            "dangling_pointers": dangling,
            "reviewer_residue_tokens_searched": list(RESIDUE_TOKENS),
            "reviewer_residue_tokens_found": residue_hits,
            "reviewer_residue_note": "the five tokens the reviewer listed as possible M13 residue "
                                     "were searched for across every document of this attempt "
                                     "(excluding iso/venv, the self-check scratch tree and this "
                                     "audit script, which contains them as data); whatever is "
                                     "listed in reviewer_residue_tokens_found is what exists",
            "cross_batch_references_verified": cross_batch,
            "cross_batch_note": "the F-02 correction leans on the M05-M08 r3 artifacts; this "
                                "attempt opened them read-only and re-checked the two specific "
                                "claims rather than quoting them on trust",
            "all_pointers_resolve": not dangling,
            "production_root": args.production_root,
            "checked_at_unix": time.time(),
            "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(os.path.join(evidence, "doc_pointer_audit.json"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, ensure_ascii=True, indent=1)
            handle.write("\n")
        print("pointers found: %d (distinct %d), dangling %d"
              % (report["pointer_count"], report["distinct_pointer_count"], len(dangling)))
        for item in dangling:
            print("dangling: %s in %s (%s)" % (item["pointer"], item["document"],
                                               item.get("reason", "")))
        print("reviewer residue tokens found: %s" % residue_hits)
        for entry in cross_batch:
            print("cross-batch %s %s exists=%s %s" % (
                entry["batch"], entry["path"], entry["exists"],
                entry.get("line_matches_claim", entry.get("claims_all_present"))))
        print("all_pointers_resolve: %s" % report["all_pointers_resolve"])
        return 0 if report["all_pointers_resolve"] else 7
    except Exception as exc:  # noqa: BLE001
        print("pointer audit harness error: %s: %s" % (
            type(exc).__name__, str(exc).encode("ascii", "backslashreplace").decode("ascii")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
