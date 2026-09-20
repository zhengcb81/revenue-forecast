import json, sys
from pathlib import Path
A = Path(sys.argv[1])
h = json.loads((A/"handoff.json").read_text("utf-8"))
q = json.loads((A/"evidence"/"I-08-B"/"qualification.json").read_text("utf-8"))
print("carrier line_range   :", q["carrier"]["line_range"])
print("review_verdict range :", h["review_verdict"]["carrier_line_range"])
print("status               :", h["status"])
