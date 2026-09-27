import sys, json
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root/"scripts")); sys.path.insert(0, str(root/"tests"))
import test_golden_behavior_lock as g
res = g.run_family("volume")
print("TOPKEYS", sorted(res.keys()))
seg = res.get("segments")
print("SEGTYPE", type(seg).__name__)
if isinstance(seg, list) and seg:
    print("SEG0KEYS", sorted(seg[0].keys()))
    print(json.dumps(seg[0], ensure_ascii=False)[:1500])
