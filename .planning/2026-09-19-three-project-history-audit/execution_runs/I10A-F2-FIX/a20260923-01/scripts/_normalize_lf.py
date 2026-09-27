import hashlib, sys, json
from pathlib import Path
targets = sys.argv[1:]
report = {}
for t in targets:
    p = Path(t)
    b = p.read_bytes()
    nb = b.replace(b"\r\n", b"\n")
    if nb != b:
        p.write_bytes(nb)
    report[str(p)] = {
        "bytes_before": len(b), "bytes_after": len(nb),
        "sha256": hashlib.sha256(nb).hexdigest(),
    }
print(json.dumps(report, indent=1))
