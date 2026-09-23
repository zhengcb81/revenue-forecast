"""I-09-C FRESH READER process (card 按序动作 3).

A brand-new process that observes ONLY what a consumer can see:
  * registry chain recomputed independently (raw file parse + canonical
    line hashes + prev-chain), never trusting the writer's return value
  * visible package members and their on-disk hashes vs the committed row
  * commit-qualification via BOTH the product authority (commit_status) and
    an independent decision (committed row + every declared member present
    with matching hash + roles non-empty)
  * tmp leftovers, audit problems, PID/barrier/exit markers
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KILL_EXIT_CODE, setup_paths, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    setup_paths()
    from contracts.evidence import canonical_sha256  # noqa: E402
    import publication_registry as PR  # noqa: E402

    run_dir = Path(args.run_dir)
    registry = Path(args.registry)
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(registry)

    obs: dict = {
        "label": args.label,
        "reader_pid": os.getpid(),
        "t": time.time(),
        "registry_path": str(registry),
        "run_dir": str(run_dir),
    }

    # --- independent raw chain recomputation ------------------------------
    rows, raw = [], []
    chain = {"ok": True, "problems": []}
    if not registry.exists():
        chain.update(exists=False, rows=0, ok=True, note="registry file absent = zero rows")
    else:
        obs["registry_bytes"] = registry.stat().st_size
        obs["registry_readonly"] = not os.access(registry, os.W_OK)
        text = registry.read_text(encoding="utf-8", errors="replace")
        prev = None
        seen_prevs = {}
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                chain["ok"] = False
                chain["problems"].append(f"line {lineno}: invalid JSON (torn/corrupt): {exc}")
                raw.append({"lineno": lineno, "unparseable": True})
                continue
            payload = {k: v for k, v in entry.items() if k != "line_sha256"}
            claimed = entry.get("line_sha256")
            recomputed = canonical_sha256(payload)
            if recomputed != claimed:
                chain["ok"] = False
                chain["problems"].append(f"line {lineno}: line hash mismatch")
            if entry.get("prev_line_sha256") != prev:
                chain["ok"] = False
                chain["problems"].append(
                    f"line {lineno}: chain break (prev mismatch: {entry.get('prev_line_sha256')!r} != {prev!r})"
                )
            pv = entry.get("prev_line_sha256")
            seen_prevs.setdefault(pv, []).append(lineno)
            prev = claimed
            rows.append(entry)
            raw.append(
                {
                    "lineno": lineno,
                    "publication_id": entry.get("publication_id"),
                    "state": entry.get("state"),
                    "input_sha256": entry.get("input_sha256"),
                    "result_sha256": entry.get("result_sha256"),
                    "attempt_seq": entry.get("attempt_seq"),
                    "artifact_type": entry.get("artifact_type"),
                    "members": entry.get("members"),
                    "member_sha256": entry.get("member_sha256"),
                    "line_sha256": claimed,
                    "prev_line_sha256": pv,
                }
            )
        forks = {str(k): v for k, v in seen_prevs.items() if k is not None and len(v) > 1}
        if forks:
            chain["ok"] = False
            chain["problems"].append(f"fork: same prev_line_sha256 used by multiple lines: {forks}")
        chain.update(exists=True, rows=len(rows), forks=forks)
    obs["chain"] = chain
    obs["rows"] = raw

    # --- product reader cross-check ---------------------------------------
    try:
        product_rows = PR._read_entries()
        obs["product_read"] = {"ok": True, "rows": len(product_rows)}
    except Exception as exc:  # RegistryError and friends — fail closed
        obs["product_read"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    # --- per-package observation ------------------------------------------
    packages = {}
    for key in ("p0", "p1"):
        input_path = run_dir / f"input_{key}.json"
        if not input_path.exists():
            continue
        doc = json.loads(input_path.read_text(encoding="utf-8"))
        input_sha = canonical_sha256(doc)
        pkg = {"input_file": str(input_path), "input_sha256_computed": input_sha}
        matching = [r for r in rows if r.get("input_sha256") == input_sha]
        pkg["rows_for_input"] = len(matching)
        pkg["input_sha_matches_a_row"] = len(matching) > 0
        committed = [r for r in matching if r.get("state") == "committed"]
        pkg["committed_rows"] = len(committed)
        pkg["distinct_publication_ids_committed"] = sorted(
            {r["publication_id"] for r in committed if r.get("publication_id")}
        )
        pkg["logical_commits"] = len(pkg["distinct_publication_ids_committed"])
        pkg["attempt_seqs"] = sorted(r.get("attempt_seq") for r in committed if r.get("attempt_seq"))

        member_table = []
        consumable = False
        for row in committed:
            members = row.get("members") or {}
            hashes = row.get("member_sha256") or {}
            per_member = {}
            all_ok = bool(members)
            for role, fname in members.items():
                fpath = run_dir / fname
                exists = fpath.is_file()
                actual = None
                match = False
                if exists:
                    import hashlib

                    actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
                    match = actual == hashes.get(role)
                per_member[role] = {
                    "file": str(fpath),
                    "exists": exists,
                    "expected_sha256": hashes.get(role),
                    "actual_sha256": actual,
                    "hash_match": match,
                }
                all_ok = all_ok and exists and match
            declared = set(members)
            expected_roles = {"output_json", "output_markdown"}
            roles_complete = declared >= expected_roles if (run_dir / "input_p1.json").exists() else bool(declared)
            # independent product-authority cross-check
            product_status = None
            try:
                product_status = PR.commit_status(
                    publication_id=row.get("publication_id"),
                    member_paths={role: run_dir / fname for role, fname in members.items()},
                )
            except Exception as exc:
                product_status = {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
            entry = {
                "publication_id": row.get("publication_id"),
                "attempt_seq": row.get("attempt_seq"),
                "members": per_member,
                "roles_declared": sorted(declared),
                "all_members_verified": all_ok,
                "roles_complete_for_formal_pair": roles_complete,
                "independent_consumable": bool(all_ok and roles_complete),
                "product_commit_status": {
                    "status": (product_status or {}).get("status"),
                    "problems": (product_status or {}).get("problems"),
                    "member_verification": (product_status or {}).get("member_verification"),
                },
                "product_agrees_with_independent": (
                    (product_status or {}).get("status") == "committed"
                )
                == bool(all_ok and roles_complete),
            }
            member_table.append(entry)
            consumable = consumable or entry["independent_consumable"]
        pkg["package_versions"] = member_table
        pkg["consumable"] = consumable
        try:
            pkg["is_registered_history_query"] = PR.is_registered(input_sha)
        except Exception as exc:
            pkg["is_registered_history_query"] = f"error: {type(exc).__name__}: {exc}"
        packages[key] = pkg
    obs["packages"] = packages
    obs["no_mixed_package"] = all(
        (not p["consumable"]) or all(v["independent_consumable"] for v in p["package_versions"])
        for p in packages.values()
    )

    # --- tmp leftovers, writer markers, audit ------------------------------
    obs["tmp_files"] = [str(p) for p in run_dir.rglob("*.tmp")]
    obs["pid_manifests"] = sorted(p.name for p in run_dir.glob("pid_*.json"))
    obs["barriers"] = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(run_dir.glob("barrier_*.json"))]
    exited = []
    for p in sorted(run_dir.glob("writer_exited_*.json")):
        exited.append(json.loads(p.read_text(encoding="utf-8")))
    obs["writer_exits"] = exited
    hard_killed_pids = [
        e["pid"] for e in exited if e.get("rc") == KILL_EXIT_CODE
    ]
    obs["kill_exit_code_marker_seen"] = hard_killed_pids
    traces = {}
    for p in sorted(run_dir.glob("hook_trace_*.jsonl")):
        traces[p.name] = [
            json.loads(line)
            for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    obs["hook_traces"] = {k: [r["point"] for r in v] for k, v in traces.items()}
    try:
        obs["audit_problems"] = PR.audit()
    except Exception as exc:
        obs["audit_problems"] = [f"{type(exc).__name__}: {exc}"]
    try:
        obs["registry_file_readonly"] = not os.access(registry, os.W_OK) if registry.exists() else None
    except OSError:
        obs["registry_file_readonly"] = None

    write_json(args.out, obs)
    summary = (
        f"reader[{args.label}] rows={obs.get('chain', {}).get('rows')} "
        f"chain_ok={obs.get('chain', {}).get('ok')} "
        + " ".join(
            f"{k}:consumable={v['consumable']},committed_rows={v['committed_rows']},"
            f"logical={v['logical_commits']}"
            for k, v in packages.items()
        )
        + f" tmp={len(obs['tmp_files'])} audit={len(obs.get('audit_problems') or [])}"
    )
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
