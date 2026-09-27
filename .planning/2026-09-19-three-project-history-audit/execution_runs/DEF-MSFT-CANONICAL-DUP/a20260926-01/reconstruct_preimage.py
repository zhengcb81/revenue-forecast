# Reconstruct the as-found pre-image of canonical_writer.py by reversing the
# fix edits; verify sha256 == 4BC65372... (the state found on disk).
import hashlib

LIVE = r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\canonical_writer.py"
OUT = r"C:\Users\郑曾波\Projects\revenue-forecast\execution_runs\DEF-MSFT-CANONICAL-DUP\a20260926-01\canonical_writer.preimage_asfound.py"
EXPECTED = "4BC653725FEBCC755E3A01AC48227A6B0799C4C262968356B356F8CB42D3C6BC"

src = open(LIVE, encoding="utf-8", newline="").read()
CRLF = "\r\n" in src
if CRLF:
    src = src.replace("\r\n", "\n")  # normalize for editing; restore below
pairs = []

pairs.append((
    """from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
from typing import Any""",
    """from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import os
from pathlib import Path
import re
import shutil
import unicodedata
from typing import Any""",
))

pairs.append((
    "from .scanner import scan_catalog\n",
    "from .scanner import scan_catalog, v2_scan_shadow_from_snapshot\n",
))

i = src.index("            destination = self._destination(request, candidate, receipt)")
j = src.index("            exact_request = SourceRequest(")
old_block = src[i:j]
new_block = (
    "            destination = self._destination(request, candidate, receipt)\n"
    "            destination.parent.mkdir(parents=True, exist_ok=True)\n"
    "            if destination.exists():\n"
    "                if _hash_file(destination) != receipt.content_sha256:\n"
    "                    destination = destination.with_name(\n"
    "                        destination.stem\n"
    "                        + \"__\"\n"
    "                        + receipt.content_sha256[:12]\n"
    "                        + destination.suffix\n"
    "                    )\n"
    "                if destination.exists() and _hash_file(destination) != receipt.content_sha256:\n"
    "                    raise CanonicalImportError(\"canonical filename collision after hash suffix\")\n"
    "            if not destination.exists():\n"
    "                self._atomic_copy(staged, destination, receipt)\n"
    "            provenance = destination.with_name(destination.name + \".source.json\")\n"
    "            self._write_provenance(provenance, request, candidate, receipt)\n"
    "            scan_catalog(\n"
    "                self.catalog.config,\n"
    "                self.catalog.store,\n"
    "                dry_run=False,\n"
    "                root_ids={self.company_root.root_id},\n"
    "                v2_scan_shadow=v2_scan_shadow_from_snapshot(\n"
    "                    self.catalog.config.catalog_dir\n"
    "                ),\n"
    "            )\n"
)
pairs.append((old_block, new_block))

i = src.index("            exact_resolution = SourceResolver(self.catalog).resolve(exact_request)")
j = src.index("            # F-EE1:")
pairs.append((
    src[i:j],
    "            exact_resolution = SourceResolver(self.catalog).resolve(exact_request)\n"
    "            if exact_resolution.status is not ResolutionStatus.REUSED_EXACT:\n"
    "                raise CanonicalImportError(\n"
    "                    \"canonical file was written but exact provider identity did not resolve\"\n"
    "                )\n",
))

pairs.append((
    """                # DEF-MSFT-CANONICAL-DUP: when the committed bytes were
                # already on canonical disk this import is a re-acquisition
                # of existing content, not a new document — journal it as
                # the established deduplicated outcome.
                status=(
                    CanonicalImportStatus.DEDUPLICATED_AFTER_DOWNLOAD
                    if destination_preexisting
                    else CanonicalImportStatus.IMPORTED_NEW
                ),""",
    "                status=CanonicalImportStatus.IMPORTED_NEW,",
))

i = src.index("    @staticmethod\n    def _verify_committed_provenance(")
j = src.index("    def _remove_staged(self, staged: Path) -> None:")
pairs.append((src[i:j], ""))

out = src
for old, new in pairs:
    count = out.count(old)
    assert count == 1, "pattern not unique/found: %r count=%d" % (old[:60], count)
    out = out.replace(old, new)

if CRLF:
    out = out.replace("\n", "\r\n")
sha = hashlib.sha256(out.encode("utf-8")).hexdigest().upper()
print("reconstructed sha:", sha)
print("expected         :", EXPECTED)
print("MATCH" if sha == EXPECTED else "MISMATCH")
with open(OUT, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
live = open(LIVE, "rb").read()
print("live (fixed) sha :", hashlib.sha256(live).hexdigest().upper())
