"""Switch signed_record call sites to integer stamp offsets."""

from __future__ import annotations

import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
pairs = [
    ('signed_at="-7199"', "signed_at_offset=-7199"),
    ('signed_at="-599"', "signed_at_offset=-599"),
    ('signed_at="601"', "signed_at_offset=601"),
    ('signed_at="600"', "signed_at_offset=600"),
]
for old, new in pairs:
    print(f"{old} -> {new}  x{text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8", newline="")
print("written")
