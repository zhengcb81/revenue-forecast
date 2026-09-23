import json
import sys

for p in sys.argv[1:]:
    s = open(p, encoding="utf-8").read()
    try:
        json.loads(s)
        print("JSON-OK", p)
    except Exception as e:
        print("JSON-FAIL", p, type(e).__name__, e)
        pos = getattr(e, "pos", None)
        if pos is not None:
            print("  pos", pos, "context:", repr(s[max(0, pos - 100):pos + 100]))
