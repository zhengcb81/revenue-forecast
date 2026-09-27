#!/usr/bin/env python3
"""Generate the canonical_writer.py variants used by the red/green/mutation rig.

Inputs (in the card output directory, one level up from this file):
  canonical_writer.fixed.py            (post-fix image, sha 2788409F...)
  canonical_writer.preimage_asfound.py (as-found pre-fix image, sha 835DAB7F.. LF / 4BC65372.. CRLF)

Outputs (this directory):
  variants/asfound/canonical_writer.py
  variants/fixed/canonical_writer.py
  variants/m1..m5/canonical_writer.py
  variants/manifest.json   (name -> sha256 + one-line description)

Every mutation is a single surgical edit of the FIXED image; each one fails
loudly if its anchor text is missing or not unique, so a silently broken
mutation cannot be mistaken for a caught one.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent  # card output dir
VARIANTS = HERE / "variants"

FIXED = (OUT / "canonical_writer.fixed.py").read_text(encoding="utf-8").replace("\r\n", "\n")
ASFOUND = (OUT / "canonical_writer.preimage_asfound.py").read_text(
    encoding="utf-8"
).replace("\r\n", "\n")


def one_replace(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor for {label} appears {count} times (expected 1): {old[:80]!r}")
    return text.replace(old, new)


def one_slice(text: str, start: str, end: str, new: str, label: str) -> str:
    if text.count(start) != 1:
        raise SystemExit(f"start anchor for {label} not unique")
    if text.count(end) != 1:
        raise SystemExit(f"end anchor for {label} not unique")
    i = text.index(start)
    j = text.index(end, i)
    return text[:i] + new + text[j:]


# --- M1: drop fix element 1 — restore the GP-002 snapshot scan mode -------
def m1(text: str) -> str:
    text = one_replace(
        text,
        "from .scanner import scan_catalog\n",
        "from .scanner import scan_catalog, v2_scan_shadow_from_snapshot\n",
        "m1-import",
    )
    return one_replace(
        text,
        "                v2_scan_shadow=bool(self.company_root.adapter_id),\n",
        "                v2_scan_shadow=v2_scan_shadow_from_snapshot(\n"
        "                    self.catalog.config.catalog_dir\n"
        "                ),\n",
        "m1-scan-mode",
    )


# --- M2: drop fix element 2 — always rewrite the immutable sidecar --------
def m2(text: str) -> str:
    return one_replace(
        text,
        "            if destination_preexisting and provenance.exists():\n"
        "                self._verify_committed_provenance(provenance, candidate, receipt)\n"
        "            else:\n"
        "                self._write_provenance(provenance, request, candidate, receipt)\n",
        "            self._write_provenance(provenance, request, candidate, receipt)\n",
        "m2-sidecar",
    )


# --- M3: drop fix element 3 — demand a strictly single REUSED_EXACT match --
def m3(text: str) -> str:
    strict = (
        "            if exact_resolution.status is not ResolutionStatus.REUSED_EXACT:\n"
        "                raise CanonicalImportError(\n"
        '                    "canonical file was written but exact provider identity did not resolve"\n'
        "                )\n"
    )
    return one_slice(
        text,
        "            if exact_resolution.status is not ResolutionStatus.REUSED_EXACT:\n",
        "            # F-EE1:",
        strict,
        "m3-verification",
    )


# --- M4: break the __<sha12> hash-suffix fallback (same-name conflict) -----
def m4(text: str) -> str:
    return one_replace(
        text,
        "            if destination.exists():\n"
        "                if _hash_file(destination) != receipt.content_sha256:\n"
        "                    destination = destination.with_name(\n"
        "                        destination.stem\n"
        '                        + "__"\n'
        "                        + receipt.content_sha256[:12]\n"
        "                        + destination.suffix\n"
        "                    )\n",
        "            if destination.exists():\n",
        "m4-hash-suffix",
    )


# --- M5: break the identity back-fill (F-EE1 request_id adoption) ---------
def m5(text: str) -> str:
    return one_replace(
        text,
        "            resolution = replace(\n"
        "                exact_resolution, request_id=request.request_id)\n",
        "            resolution = exact_resolution\n",
        "m5-request-id-backfill",
    )


# --- M6: break the duplicate (already-indexed bytes) branch ---------------
def m6(text: str) -> str:
    return one_replace(
        text,
        "    def _existing_original(self, content_sha256: str) -> Path | None:\n",
        "    def _existing_original(self, content_sha256: str) -> Path | None:\n"
        "        if True:  # MUTATION M6: duplicate branch disabled\n"
        "            return None\n",
        "m6-duplicate-branch",
    )


MUTATIONS = {
    "m1": (m1, "revert fix element 1: import-time scan uses the v2 snapshot flag again"),
    "m2": (m2, "revert fix element 2: always rewrite the immutable provenance sidecar"),
    "m3": (m3, "revert fix element 3: post-write verification demands strict REUSED_EXACT"),
    "m4": (m4, "break the __<sha12> hash-suffix fallback for same-name conflicts"),
    "m5": (m5, "break the F-EE1 request_id identity back-fill on the returned resolution"),
    "m6": (m6, "break the duplicate branch (_existing_original always returns None)"),
}


def write_variant(name: str, text: str, description: str, manifest: dict) -> None:
    target = VARIANTS / name / "canonical_writer.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    compile(text, f"<variant {name}>", "exec")
    manifest[name] = {
        "sha256_lf": hashlib.sha256(text.encode("utf-8")).hexdigest().upper(),
        "bytes_lf": len(text.encode("utf-8")),
        "description": description,
    }


def main() -> int:
    VARIANTS.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    write_variant("asfound", ASFOUND, "as-found pre-fix image (defect present)", manifest)
    write_variant("fixed", FIXED, "fix image under review (3 elements, DEF-MSFT-CANONICAL-DUP)", manifest)
    for name, (fn, description) in MUTATIONS.items():
        write_variant(name, fn(FIXED), description, manifest)
    (VARIANTS / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
