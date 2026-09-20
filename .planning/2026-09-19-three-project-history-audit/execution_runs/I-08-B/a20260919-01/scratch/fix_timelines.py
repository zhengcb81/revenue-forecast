"""Apply the final timeline corrections to the I-08-B protocol tests."""

from __future__ import annotations

import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

pairs = [
    # T-O3: keep the default issued+1 stamp so the window really has closed
    (
        'record = self.signed_record(request, signed_at_offset=-7199)\n'
        '        self.assertEqual(verify_publication_attestation(_artifact(record)), [])',
        'record = self.signed_record(request)\n'
        '        self.assertEqual(verify_publication_attestation(_artifact(record)), [])',
    ),
    # T-R7: same
    (
        'record = self.signed_record(request, signed_at_offset=-7199)\n'
        '        for _ in range(5):',
        'record = self.signed_record(request)\n'
        '        for _ in range(5):',
    ),
    # T-N28: a window wide enough that issued+601 is strictly inside it
    (
        'issued_at=self.at(600), expires_at=self.at(1200), signed_at_offset=601',
        'issued_at=self.at(600), expires_at=self.at(1800), signed_at_offset=601',
    ),
    # production funnel: the trust domain is deliberately as wide as the format
    # allows, so no absolute stamp can fall outside it
    (
        'entry={"not_before": "1970-01-01T00:00:00Z", "not_after": "2100-01-01T00:00:00Z"}',
        'entry={"not_before": "1971-01-01T00:00:00Z", "not_after": "2099-01-01T00:00:00Z"}',
    ),
]
for old, new in pairs:
    count = text.count(old)
    print(f"x{count}: {old.splitlines()[0][:70]}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8", newline="")
print("written")
