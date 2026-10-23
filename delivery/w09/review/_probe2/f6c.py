import json, hashlib, os
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
D = W / "delivery" / "w09"
OUTDIR = D / "review" / "_probe2"
lines = []

# graded checkpoints: all PASS?
g = json.loads((D / "research/acceptance-checkpoints-graded.json").read_text(encoding="utf-8"))
grades = {k: v["grade"] for k, v in g["grades"].items()}
lines.append("graded checkpoints: %s" % json.dumps(grades, ensure_ascii=False))
lines.append("all PASS: %s" % all(v == "PASS" for v in grades.values()))

# artifact SHAs recorded in graded file vs on-disk
for p_str, sha in g["artifacts"].items():
    p = Path(p_str)
    if p.exists():
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append("graded artifact %s match=%s" % (p.name, got == sha))
    else:
        lines.append("graded artifact MISSING: %s" % p_str)

# delivery size
total = 0
for p in D.rglob("*"):
    if p.is_file():
        total += p.stat().st_size
lines.append("delivery/w09 total bytes: %d = %.2f MiB (limit 32 MiB = %d bytes): under=%s" % (
    total, total / 1048576, 32 * 1048576, total < 32 * 1048576))

# cleanup receipt protected artifact SHAs vs on-disk
cr = json.loads((D / "cleanup/receipt.json").read_text(encoding="utf-8"))
lines.append("cleanup restored: %s" % cr["restored"])
for rel, meta in cr["protected_artifacts_after_cleanup"].items():
    p = W / rel
    if p.exists():
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append("receipt artifact %s match=%s (size %s vs %s)" % (rel, got == meta["sha256"], p.stat().st_size, meta["byte_size"]))
    else:
        lines.append("receipt artifact MISSING: %s" % rel)

# native-chain.json sha as recorded in graded file already checked; check main-forecast sha
mf = hashlib.sha256((D / "forecast/main-forecast.json").read_bytes()).hexdigest()
lines.append("main-forecast.json on-disk sha=%s" % mf[:16])

# recorder: verify 6 capture dirs frozen input == request.json bytes
nc = json.loads((D / "research/native-chain.json").read_text(encoding="utf-8"))
for c in nc["calls"]:
    req = Path(c["request_file"]).read_bytes()
    req_sha = hashlib.sha256(req).hexdigest()
    frozen = Path(c["frozen_input_path"]).read_bytes()
    consumed = Path(c["consumed_path"]).read_bytes()
    lines.append("call %s: request_sha=%s matches_native-chain=%s frozen==request_bytes=%s frozen==consumed=%s" % (
        c["request_id"], req_sha[:12], req_sha == c["request_sha256"], frozen == req, frozen == consumed))

# registry chain
reg = (D / "registry/publications.jsonl").read_text(encoding="utf-8").strip().splitlines()
lines.append("registry lines: %d" % len(reg))
prev = None
chain_ok = True
for i, ln in enumerate(reg):
    obj = json.loads(ln)
    if prev is not None and obj.get("prev_line_sha256") != prev:
        chain_ok = False
        lines.append("registry chain break at line %d" % i)
    prev = hashlib.sha256(ln.encode("utf-8")).hexdigest()
lines.append("registry prev_line chain ok: %s" % chain_ok)
lines.append("first line prev_line_sha256: %s" % json.loads(reg[0]).get("prev_line_sha256"))

(OUTDIR / "f6c_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
