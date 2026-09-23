"""I-07-D FRESH READER process for F06 (adapted from I-09-C harness/reader.py).

Run in a NEW interpreter after seed/fault/recovery1/recovery2; never trusts
the writer's return value.  Targets the CURRENT production registry schema
(append-only JSONL with chained prev_line_sha256/line_sha256, input_sha256,
result_sha256, ... — there is NO publication_id/commit-state field in current
production; membership + member completeness define consumability).

Independence: the chain is recomputed HERE with contracts.evidence.canonical_sha256,
input_sha256 is recomputed from the input bytes' parsed document, member files
are re-read from disk; the product's own authorities (is_registered / audit)
are additionally invoked in this same fresh process and cross-checked.

Output schema (one JSON file):
  {label, reader_pid, t, registry_path, run_dir,
   rows[{lineno, input_sha256, result_sha256, artifact_type,
         validation_status, registered_at, line_sha256, prev_line_sha256}],
   chain{ok, problems, rows, recomputed_line_hashes_ok},
   inputs{p0:{sha_computed}, p1:{...}},
   product_authority{is_registered_p0, is_registered_p1, audit_problems,
                     audit_result_files},
   packages{p0:{json_exists, md_exists, json_parse_ok, input_claim,
                input_match, result_sha256, registry_rows_for_input,
                result_matches_registry, consumable, ...}, p1:{...}},
   no_mixed_package, tmp_files, pid_manifests, barriers, writer_exits,
   hook_traces{file:[points]}, kill_evidence{...}}

Consumable (frozen oracle §2 F06): json exists ∧ markdown exists ∧ json parses
∧ recomputed input_sha256 == json claim ∧ ∃ registry row with same
input_sha256 AND same result_sha256 ∧ chain ok.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--input-p0", required=True)
    ap.add_argument("--input-p1", required=True)
    ap.add_argument("--json-p0", required=True)
    ap.add_argument("--json-p1", required=True)
    ap.add_argument("--md-p0", required=True)
    ap.add_argument("--md-p1", required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import setup_paths  # noqa: E402

    setup_paths()
    from contracts.evidence import canonical_sha256  # noqa: E402
    import publication_registry as PR  # noqa: E402

    run_dir = Path(args.run_dir)
    registry = Path(args.registry)
    out: dict = {
        "label": args.label,
        "reader_pid": __import__("os").getpid(),
        "t": time.time(),
        "registry_path": str(registry),
        "run_dir": str(run_dir),
        "note": "fresh reader process; writer return values are never trusted",
    }

    # ---- inputs: recompute input_sha256 the way production does (canonical over doc)
    inputs = {}
    input_shas = {}
    for name, p in (("p0", args.input_p0), ("p1", args.input_p1)):
        try:
            doc = json.loads(Path(p).read_text(encoding="utf-8"))
            sha = canonical_sha256(doc)
            inputs[name] = {"input_file": p, "sha_computed": sha, "parse_ok": True}
            input_shas[name] = sha
        except Exception as exc:  # noqa: BLE001
            inputs[name] = {"input_file": p, "parse_ok": False,
                            "error": f"{type(exc).__name__}: {exc}"}
            input_shas[name] = None
    out["inputs"] = inputs

    # ---- independent chain recompute
    rows = []
    problems = []
    previous = None
    if not registry.exists():
        problems.append("registry file missing")
    else:
        for lineno, raw in enumerate(
                registry.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError as exc:
                problems.append(f"line {lineno}: invalid JSON: {exc}")
                continue
            claimed = entry.get("line_sha256")
            payload = {k: v for k, v in entry.items() if k != "line_sha256"}
            recomputed = canonical_sha256(payload)
            if recomputed != claimed:
                problems.append(f"line {lineno}: line_sha256 mismatch")
            if entry.get("prev_line_sha256") != previous:
                problems.append(f"line {lineno}: chain break")
            previous = claimed
            rows.append({
                "lineno": lineno,
                "input_sha256": entry.get("input_sha256"),
                "result_sha256": entry.get("result_sha256"),
                "artifact_type": entry.get("artifact_type"),
                "validation_status": entry.get("validation_status"),
                "registered_at": entry.get("registered_at"),
                "line_sha256": claimed,
                "prev_line_sha256": entry.get("prev_line_sha256"),
            })
    out["chain"] = {"ok": not problems, "problems": problems, "rows": len(rows)}
    out["rows"] = rows

    # ---- product authorities (same fresh process, product's own functions)
    auth = {}
    try:
        auth["is_registered_p0"] = bool(
            input_shas["p0"] and PR.is_registered(input_shas["p0"]))
        auth["is_registered_p1"] = bool(
            input_shas["p1"] and PR.is_registered(input_shas["p1"]))
    except Exception as exc:  # noqa: BLE001
        auth["authority_error"] = f"{type(exc).__name__}: {exc}"
    result_files = [Path(p) for p in (args.json_p0, args.json_p1)
                    if Path(p).is_file()]
    auth["audit_result_files"] = [str(p) for p in result_files]
    try:
        auth["audit_problems"] = list(PR.audit(result_files))
    except Exception as exc:  # noqa: BLE001
        auth["audit_problems"] = [f"{type(exc).__name__}: {exc}"]
    # registry path actually used by the product (env must match)
    try:
        auth["product_registry_path"] = str(PR.registry_file())
        auth["registry_path_match"] = str(PR.registry_file()) == str(registry)
    except Exception as exc:  # noqa: BLE001
        auth["registry_path_error"] = f"{type(exc).__name__}: {exc}"
    out["product_authority"] = auth

    # ---- member/package checks
    packages = {}
    for name, jp, mp in (("p0", args.json_p0, args.md_p0),
                         ("p1", args.json_p1, args.md_p1)):
        jpath, mpath = Path(jp), Path(mp)
        rec = {
            "input_file": args.input_p0 if name == "p0" else args.input_p1,
            "json_file": jp, "md_file": mp,
            "json_exists": jpath.is_file(),
            "md_exists": mpath.is_file(),
            "json_sha256": None, "md_sha256": None,
            "json_parse_ok": False,
            "input_claim": None, "input_match": False,
            "result_sha256": None,
            "rows_for_input": 0,
            "result_matches_registry": False,
        }
        if jpath.is_file():
            rec["json_sha256"] = __import__("hashlib").sha256(
                jpath.read_bytes()).hexdigest()
            try:
                obj = json.loads(jpath.read_text(encoding="utf-8"))
                rec["json_parse_ok"] = isinstance(obj, dict)
                rec["input_claim"] = obj.get("input_sha256")
                rec["result_sha256"] = obj.get("result_sha256")
                rec["input_match"] = (input_shas[name] is not None
                                      and rec["input_claim"] == input_shas[name])
            except Exception as exc:  # noqa: BLE001
                rec["json_error"] = f"{type(exc).__name__}: {exc}"
        if mpath.is_file():
            rec["md_sha256"] = __import__("hashlib").sha256(
                mpath.read_bytes()).hexdigest()
        sha = input_shas[name]
        matching = [r for r in rows if sha and r["input_sha256"] == sha]
        rec["rows_for_input"] = len(matching)
        rec["result_matches_registry"] = bool(
            rec["result_sha256"] is not None
            and any(r["result_sha256"] == rec["result_sha256"] for r in matching))
        rec["consumable"] = bool(
            rec["json_exists"] and rec["md_exists"] and rec["json_parse_ok"]
            and rec["input_match"] and rec["result_matches_registry"]
            and out["chain"]["ok"])
        packages[name] = rec
    out["packages"] = packages
    out["no_mixed_package"] = bool(
        # a "mixed" package would be a json claiming p1's input while only the
        # p0 md exists, or any member/input mismatch; defined as: for each
        # package, if json exists then input_match must hold
        all((not p["json_exists"]) or p["input_match"]
            for p in packages.values()))

    # ---- filesystem + kill evidence
    out["tmp_files"] = [str(p) for p in run_dir.rglob("*.tmp")]
    out["pid_manifests"] = sorted(p.name for p in run_dir.glob("pid_*.json"))
    out["barriers"] = sorted(p.name for p in run_dir.glob("barrier_*.json"))
    out["writer_exits"] = sorted(p.name for p in run_dir.glob("writer_exited_*.json"))
    traces = {}
    for p in sorted(run_dir.glob("hook_trace_*.jsonl")):
        points = []
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                points.append(json.loads(line).get("point"))
            except json.JSONDecodeError:
                points.append("<unparseable>")
        traces[p.name] = points
    out["hook_traces"] = traces
    out["kill_evidence"] = {
        "pid_manifests": out["pid_manifests"],
        "barriers": out["barriers"],
        "writer_exit_records": out["writer_exits"],
        "killed_marker_proven": bool(out["barriers"])
                                and not any(w.startswith("writer_exited_")
                                            for w in out["writer_exits"])
                                if out["barriers"] else None,
    }

    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str),
                    encoding="utf-8")
    print(json.dumps({
        "label": args.label,
        "chain_ok": out["chain"]["ok"],
        "p0_consumable": packages["p0"]["consumable"],
        "p1_consumable": packages["p1"]["consumable"],
        "p1_rows": packages["p1"]["rows_for_input"],
        "is_registered_p1": auth.get("is_registered_p1"),
        "audit_problems": len(auth.get("audit_problems") or []),
        "tmp_files": len(out["tmp_files"]),
        "barriers": len(out["barriers"]),
        "writer_exits": len(out["writer_exits"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
