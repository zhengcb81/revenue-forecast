import json, sys, pathlib
D = pathlib.Path(sys.argv[1])
def j(p): return json.loads((D/p).read_text(encoding="utf-8"))
out = {}
f1 = j("evidence/cases/F01/verdict.json")
out["F01"] = {"rcs": f1["raw_rcs"], "fetch_run1": f1["trigger"]["fetch_count_run1_window"],
  "fetch_total": f1["trigger"]["fetch_count_total"], "disc_run1": f1["trigger"]["discover_count_run1_window"],
  "spy_deltas": f1["trigger"]["spy_provider_delta"], "recovery_catalog_delta":
  j("evidence/cases/F01/run4_recovery_entry/evidence.json")["catalog_count_delta"],
  "recovery_provider": j("evidence/cases/F01/run4_recovery_entry/evidence.json")["counter_delta"]}
f2 = j("evidence/cases/F02/verdict.json")
out["F02"] = {"rcs": f2["raw_rcs"], "count": f2["trigger"]["count"], "statuses": f2["trigger"]["status"],
  "fault_catalog_delta": f2["fault_catalog_delta"], "hold": {k: f2["trigger"]["hold"].get(k) for k in ("opened_at","closed_at","held_seconds","released_by")},
  "divergences": f2["prediction_divergences"],
  "scan2_delta": j("evidence/cases/F02/scan2_recovery/evidence.json")["catalog_count_delta"]}
f3 = j("evidence/cases/F03/verdict.json")
out["F03"] = {"rcs": f3["raw_rcs"], "count": f3["trigger"]["count"], "elapsed": f3["trigger"]["scan_elapsed"],
  "overlap": f3["trigger"]["overlap_ok"], "lock": {k: f3["trigger"]["lock_hold"].get(k) for k in ("locked_at","released","ok","hold_s")},
  "err": f3["trigger"]["error_doc"],
  "scan2_delta": j("evidence/cases/F03/scan2_recovery/evidence.json")["catalog_count_delta"],
  "scan1_counter": j("evidence/cases/F03/scan1_fault/evidence.json")["counter_delta"]}
f4 = j("evidence/cases/F04/verdict.json")
kr = f4["trigger"]["kill_record"]["killed"]
pid = list(kr)[0] if kr else None
out["F04"] = {"rcs": f4["raw_rcs"], "count": f4["trigger"]["count"], "killed_pid": pid,
  "gate_checks": kr[pid]["checks"] if pid else None,
  "exit_code_set": kr[pid]["kill"].get("exit_code_set") if pid else None,
  "committed_raw": f4["trigger"]["committed_raw_path"],
  "fault_counter": j("evidence/cases/F04/run1_entry_fault/evidence.json")["counter_delta"],
  "scan2_delta": j("evidence/cases/F04/scan2_recovery/evidence.json")["catalog_count_delta"],
  "entry_after_provider": j("evidence/cases/F04/entry_after_recovery/evidence.json")["counter_delta"]}
f5 = j("evidence/cases/F05/verdict.json")
out["F05"] = {"rcs": f5["raw_rcs"], "count": f5["trigger"]["count"],
  "fault_report": f5["trigger"]["fault_report"], "recovery_report": f5["trigger"]["recovery_report"],
  "cause": f5["cause_survival"]["verdict"][:80],
  "hold": {k: f5["trigger"]["hold"].get(k) for k in ("opened_at","closed_at","held_seconds")}}
for c in ("F06A","F06B","F06C"):
    v = j(f"evidence/cases/{c}/verdict.json")
    out[c] = {"rcs": v["writer_rcs"], "trigger": {k: v["trigger"].get(k) for k in ("count","location","marker_in_stderr","killed","fault_writer_exit_records")},
      "rows": v["registry_rows"], "failed": [k for k,x in v["checks"].items() if not x],
      "findings": [x["id"] for x in v.get("product_findings", [])]}
print(json.dumps(out, ensure_ascii=False, indent=1))
