"""Convert the staged absolute stamps in the protocol tests to window offsets."""

from __future__ import annotations

import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
pairs = [
    ('signed_at=self.at(-599)', 'signed_at="-599"'),
    ('signed_at=self.at(-7199)', 'signed_at="-7199"'),
    ('signed_at=self.at(601)', 'signed_at="601"'),
    ('signed_at=self.at(600)', 'signed_at="600"'),
]
for old, new in pairs:
    count = text.count(old)
    print(f"{old} -> {new}  x{count}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8", newline="")
print("written")
