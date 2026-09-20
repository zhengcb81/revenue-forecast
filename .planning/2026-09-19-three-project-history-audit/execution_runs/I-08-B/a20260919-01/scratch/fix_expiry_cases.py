"""Point the expiry-replay cases at artifacts whose stamps really have expired."""

from __future__ import annotations

import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

old_o3 = (
    "        request = self.make_request(issued_at=self.at(-7200), expires_at=self.at(-7100))\n"
    "        record = self.signed_record(request)\n"
    "        self.assertEqual(verify_publication_attestation(_artifact(record)), [])"
)
new_o3 = (
    "        request = self.make_request(\n"
    "            issued_at=self.at(0), expires_at=self.at(100), signed_at_offset=-7200\n"
    "        )\n"
    "        record = self.signed_record(request)\n"
    "        self.assertLess(\n"
    "            ap.parse_utc(record[\"expires_at\"], \"expires_at\"), self.ANCHOR\n"
    "        )\n"
    "        self.assertEqual(verify_publication_attestation(_artifact(record)), [])"
)
print("O3:", text.count(old_o3))
text = text.replace(old_o3, new_o3)

old_r7 = (
    "        request = self.make_request(issued_at=self.at(-7200), expires_at=self.at(-7100))\n"
    "        record = self.signed_record(request)\n"
    "        for _ in range(5):"
)
new_r7 = (
    "        request = self.make_request(\n"
    "            issued_at=self.at(0), expires_at=self.at(100), signed_at_offset=-7200\n"
    "        )\n"
    "        record = self.signed_record(request)\n"
    "        for _ in range(5):"
)
print("R7:", text.count(old_r7))
text = text.replace(old_r7, new_r7)

path.write_text(text, encoding="utf-8", newline="")
print("written")
