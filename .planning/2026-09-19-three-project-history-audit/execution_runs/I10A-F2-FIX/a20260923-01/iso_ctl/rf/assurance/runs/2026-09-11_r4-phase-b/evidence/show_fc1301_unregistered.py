"""Print the actionable part of the FC-1301 inventory (read-only)."""

from __future__ import annotations

import json
import pathlib

path = pathlib.Path(__file__).with_name("fc1301-reason-inventory.json")
data = json.loads(path.read_text(encoding="utf-8"))
summary = data["summary"]["resolved_positional"]
lines = [
    f"scanned_files={data['scanned_files']} registry={data['registry_module']}",
    f"registered_codes={data['registered_codes']}",
    f"positional sites={summary['sites']} code_like={summary['code_like_sites']} "
    f"unregistered_code_like={summary['unregistered_code_like_sites']}",
    "",
    "distinct unregistered code-like values:",
]
lines += [f"  {value}" for value in summary["unregistered_code_like_values"]]
lines += ["", "unregistered sites:"]
for item in data["resolved_positional"]:
    if not item["registered"]:
        lines.append(f"  {item['file']}:{item['line']}  callee={item['callee']} "
                     f"param={item['param']} value={item['value']} kind={item['kind']}")
out = path.with_name("fc1301-unregistered.txt")
out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
print(f"wrote {out} ({len(lines)} lines)")
