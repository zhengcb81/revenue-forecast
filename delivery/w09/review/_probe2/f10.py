import hashlib, json
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
lines = []
# after my reconcile rerun, confirm native-chain.json is unchanged (idempotent) and still matches the graded artifact sha
g = json.loads((W / "delivery/w09/research/acceptance-checkpoints-graded.json").read_text(encoding="utf-8"))
nc_path = W / "delivery/w09/research/native-chain.json"
got = hashlib.sha256(nc_path.read_bytes()).hexdigest()
expected = [v for k, v in g["artifacts"].items() if k.endswith("native-chain.json")][0]
lines.append("native-chain.json after my reconcile rerun: sha=%s matches graded artifact: %s" % (got[:16], got == expected))

# read-only inputs unchanged? card-expected sha of inputs/readonly-inputs.json recorded in receipt (checked earlier)
# confirm sealed run files untouched by checking mtimes are all older than today's session start? Just record SHAs.
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
for rel in ("execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json",
            "execution_replays/r1-remediation-01/phase_b/forecast/final3-shared-stress.json",
            "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json",
            "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json"):
    p = RUN / rel
    lines.append("sealed %s sha=%s mtime=%s" % (rel.split("/")[-1], hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.stat().st_mtime))

# delivery manifest size breakdown (top-level dirs)
D = W / "delivery" / "w09"
per = {}
for p in D.rglob("*"):
    if p.is_file():
        top = p.relative_to(D).parts[0]
        per[top] = per.get(top, 0) + p.stat().st_size
lines.append("size by top dir: " + json.dumps({k: v for k, v in sorted(per.items(), key=lambda kv: -kv[1])}))

# verify the 6 stdout files in captures
nc = json.loads((D / "research/native-chain.json").read_text(encoding="utf-8"))
for c in nc["calls"]:
    st = Path(c["capture_dir"]) / "stdout.txt"
    se = Path(c["capture_dir"]) / "stderr.txt"
    lines.append("capture %s: stdout_bytes=%s stderr_bytes=%s exit=%s" % (
        c["request_id"], st.stat().st_size, se.stat().st_size, c["exit_code"]))

(OUTDIR / "f10_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
