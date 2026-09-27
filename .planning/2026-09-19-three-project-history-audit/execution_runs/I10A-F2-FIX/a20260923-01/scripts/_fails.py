import json, sys, xml.etree.ElementTree as ET
from pathlib import Path
att = Path(sys.argv[1])
ids = [r["id"] for r in json.loads((att/"evidence"/"family_diff.json").read_text(encoding="utf-8"))["regressed"]]
want = {}
for cid in ids:
    cls, name = cid.split("::", 1)
    want[(cls, name)] = cid
root = ET.parse(att/"evidence"/"family_after_junit.xml").getroot()
out = {}
for case in root.iter("testcase"):
    key = (case.get("classname", ""), case.get("name", ""))
    if key not in want:
        continue
    node = case.find("failure")
    if node is None:
        node = case.find("error")
    if node is None:
        continue
    msg = (node.get("message") or "").replace("\n", " | ")
    out[want[key]] = msg[:300]
for cid in ids:
    print(f"{cid}\n    {out.get(cid, '<no failure element>')}\n")
