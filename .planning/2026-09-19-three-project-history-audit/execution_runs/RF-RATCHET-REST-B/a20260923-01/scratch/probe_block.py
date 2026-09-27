import hashlib
from pathlib import Path

text = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tools\tests\test_complexity_ratchet.py").read_text(encoding="utf-8")
start = text.index("FROZEN_MAX = {")
end = text.index("NEW_FILE_MAX = 10") + len("NEW_FILE_MAX = 10")
block = text[start:end]
cands = {
    "raw": block,
    "plus_nl": block + "\n",
    "line16_45": "\n".join(text.splitlines()[15:45]),
    "line16_45_nl": "\n".join(text.splitlines()[15:45]) + "\n",
}
target = "1e9cce36115c381683f69e391c4e680336c61faff57e635a324d2b2ecd389074"
for name, b in cands.items():
    h = hashlib.sha256(b.encode("utf-8")).hexdigest()
    print(f"{name:15s} {h} {'<== MATCH' if h == target else ''}")
