"""I-07-C attempt-support aggregator (NOT a product command): prints a compact
per-cell view of the isolated catalog dumps and the resolve envelopes so the
per-cell conclusions in decision.md quote measured rows, not recollection.

  python summarize_cells.py            -> evidence/cell_summary.json (+ stdout)
"""
from __future__ import annotations

import json
import sys

from i07c_common import CELLS, EVID, read_json, write_json


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    summary: dict = {}
    for cell in CELLS:
        entry: dict = {"cell": cell, "scans": []}
        for scan in sorted((EVID / cell).glob("scan[0-9]*")):
            if not (scan / "catalog_dump.json").is_file():
                continue
            dump = load(scan / "catalog_dump.json")
            srec = {
                "run": scan.name,
                "rc": load(scan / "product_rc.json")["product_returncode"],
                "stdout": (scan / "stdout.txt").read_text(encoding="utf-8").strip(),
                "counts": {k: v for k, v in dump["counts"].items() if v},
                "roles": [{"rel": l["relative_path"], "role": l["role"],
                           "error": l.get("error")}
                          for l in dump["locations"]],
                "roots": [{k: r[k] for k in ("root_id", "kind", "priority")}
                          for r in dump["roots"]],
            }
            if dump["scan_runs"]:
                report = json.loads(dump["scan_runs"][-1]["report_json"] or "{}")
                srec["scan_report"] = {k: report.get(k) for k in
                                       ("errors", "new_errors", "error_details",
                                        "strategy", "files_seen", "files_hashed",
                                        "locations_active")}
            entry["scans"].append(srec)
        if entry["scans"]:
            last = entry["scans"][-1]
            dump = load(EVID / cell / last["run"] / "catalog_dump.json")
            entry["scan_rc"] = last["rc"]
            entry["counts"] = last["counts"]
            entry["roots"] = last["roots"]
            entry["sources"] = dump["sources"]
            entry["documents"] = [{k: d.get(k) for k in
                                   ("document_id", "document_kind",
                                    "source_status", "title",
                                    "primary_source_id", "published_date")}
                                  for d in dump["documents"]]
            entry["locations"] = [{k: l.get(k) for k in
                                   ("root_id", "relative_path", "role",
                                    "location_status", "source_id",
                                    "document_id", "observed_size", "error")}
                                  for l in dump["locations"]]
            entry["document_entities"] = dump["document_entities"]
        resolves = sorted((EVID / cell).glob("resolve*/stdout.txt"))
        entry["resolves"] = []
        for out in resolves:
            rc_path = out.with_name("product_rc.json")
            text = out.read_text(encoding="utf-8").strip()
            rec: dict = {"run": out.parent.name,
                         "rc": load(rc_path)["product_returncode"] if rc_path.is_file() else None}
            if text:
                try:
                    payload = json.loads(text)
                    rec["reason"] = payload.get("reason")
                    rec["status"] = payload.get("status")
                    env = payload.get("resolution_envelope") or {}
                    rec["outcome"] = env.get("outcome")
                    rec["prompt_injection_status"] = env.get("prompt_injection_status")
                    rec["source_sha256"] = env.get("source_sha256")
                    rec["qualification"] = env.get("qualification")
                    rec["matches"] = len(payload.get("matches") or [])
                    rec["canonical_location_rationale"] = env.get(
                        "canonical_location_rationale")
                    # capture selected candidate/location details if present
                    matches = payload.get("matches") or []
                    if matches:
                        m0 = matches[0]
                        rec["match0"] = {k: m0.get(k) for k in
                                         ("document_id", "document_kind", "title",
                                         "selected_location", "locations")}
                except ValueError:
                    rec["stdout_head"] = text[:400]
            err = out.with_name("stderr.txt")
            if err.is_file() and err.read_text(encoding="utf-8").strip():
                tail = err.read_text(encoding="utf-8").strip().splitlines()[-1]
                rec["stderr_last_line"] = tail
            entry["resolves"].append(rec)
        # resolve side dumps (post-resolve catalog) for the located-claim check
        for rdir in sorted((EVID / cell).glob("resolve*")):
            cd = rdir / "catalog_dump.json"
            if cd.is_file():
                entry.setdefault("resolve_catalog_counts", {})[rdir.name] = {
                    k: v for k, v in load(cd)["counts"].items() if v}
        summary[cell] = entry
    write_json(EVID / "cell_summary.json", summary)
    print(json.dumps({c: {"scan_rc": e.get("scan_rc"),
                          "counts": e.get("counts"),
                          "resolves": [{"run": r["run"], "rc": r["rc"],
                                        "reason": r.get("reason"),
                                        "outcome": r.get("outcome")}
                                       for r in e.get("resolves", [])]}
                      for c, e in summary.items()},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
