import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"

sealed_main = json.loads((RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json").read_text(encoding="utf-8"))
sealed_stress = json.loads((RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-shared-stress.json").read_text(encoding="utf-8"))
new_main = json.loads((W / "delivery/w09/forecast/main-forecast.json").read_text(encoding="utf-8"))
new_stress = json.loads((W / "delivery/w09/forecast/stress-forecast.json").read_text(encoding="utf-8"))

lines = []


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# file-level SHA checks against card / review
for name, p, expected in [
    ("sealed final3-forecast.json", RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json", "41ea79efa319226ac93e65d5210bb304b4d458cfac95ef5998fdf06eaf12279d"),
    ("sealed final3-input.json", RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json", "e54ba7df7a5914772222e88e56661d0822e251e257814b9dc7c976c454660257"),
]:
    got = sha_file(p)
    lines.append("%s sha=%s expected_match=%s" % (name, got[:16], got == expected))

# locate segment_subtotal structures
def find_subtotals(obj, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "segment_subtotal":
                hits.append((path + "/" + k, v))
            else:
                hits.extend(find_subtotals(v, path + "/" + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(find_subtotals(v, path + "/%d" % i))
    return hits


for label, new, old in [("MAIN", new_main, sealed_main), ("STRESS", new_stress, sealed_stress)]:
    n_hits = find_subtotals(new)
    o_hits = find_subtotals(old)
    lines.append("%s: new segment_subtotal nodes=%d old=%d" % (label, len(n_hits), len(o_hits)))
    same_nodes = 0
    diffs = []
    for pth, val in n_hits:
        match = None
        for opth, oval in o_hits:
            if opth == pth:
                match = (opth, oval)
                break
        if match and match[1] == val:
            same_nodes += 1
        else:
            diffs.append((pth, val, match[1] if match else None))
    lines.append("%s: identical-at-same-path nodes=%d differing=%d" % (label, same_nodes, len(diffs)))
    for d in diffs[:10]:
        lines.append("  DIFF path=%s new=%r old=%r" % (d[0], json.dumps(d[1])[:200], json.dumps(d[2])[:200] if d[2] is not None else None))

# also compare full leaf diff counts (context for the memo claim)
def leaves(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, path + "/%d" % i)
    else:
        yield path, obj


for label, new, old in [("MAIN", new_main, sealed_main), ("STRESS", new_stress, sealed_stress)]:
    nl = dict(leaves(new))
    ol = dict(leaves(old))
    common = set(nl) & set(ol)
    changed = [p for p in common if nl[p] != ol[p]]
    added = set(nl) - set(ol)
    removed = set(ol) - set(nl)
    lines.append("%s leaf diff: changed=%d added=%d removed=%d total-diff=%d" % (
        label, len(changed), len(added), len(removed), len(changed) + len(added) + len(removed)))

# forecast input_sha256 vs snapshot input_sha256 (FIX-5)
for name, fp, sp in [
    ("main", W / "delivery/w09/forecast/main-forecast.json", W / "delivery/w09/snapshots/main-v1.json"),
    ("stress", W / "delivery/w09/forecast/stress-forecast.json", W / "delivery/w09/snapshots/stress-v1.json"),
]:
    f = json.loads(fp.read_text(encoding="utf-8"))
    s = json.loads(sp.read_text(encoding="utf-8"))
    fsha = f.get("input_sha256")
    ssha = s.get("input_sha256")
    lines.append("%s: forecast input_sha256=%s snapshot input_sha256=%s match=%s" % (
        name, str(fsha)[:16], str(ssha)[:16], fsha == ssha))
    lines.append("%s: snapshot keys sample: %s" % (name, ", ".join(list(s.keys())[:20])))

(OUTDIR / "f5c_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
