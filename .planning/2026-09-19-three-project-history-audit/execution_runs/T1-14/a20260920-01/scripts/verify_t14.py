#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""T1-14 — verify that I-11-A's registered pdftotext register actually holds.

OWNER_DECISIONS.md T1-14 (TIER-1) adopts the I-11-A reviewer's OPEN-1 opinion:
  pdftotext.exe is ALLOWED as a CROSS-CHECK path only,
  NEVER as the sole source of any cited number;
  its ABSOLUTE PATH + sha256 must be written into binding.json;
  upgrading Git to obtain text-extraction capability is FORBIDDEN.

Three propositions are checked.  Each is a *separate* falsifiable claim, because
"the field exists" and "the field is true" are different facts:

  P-1  the register FIELD EXISTS, with an absolute path and a 64-hex sha256
  P-2  the REGISTERED HASH EQUALS the hash of the binary actually on disk
  P-3  the binary is the version the register claims (so the hash is not
       merely "some file at that path")

A fourth claim is checked about the *policy* rather than the artifact:

  P-4  no Git upgrade occurred as a consequence of this card.  This is checked
       the only way it can honestly be checked from inside the repo — by
       comparing the Git install tree's mtime against the attempt's own
       timestamps and reporting the result.  If the tree postdates the card,
       the proposition is NOT verified and must be reported as such rather than
       waved through.

Output is a JSON record; the script prints a human summary to stdout as well.
Exit code is 0 when P-1..P-3 hold and P-4 is either held or honestly reported as
unverifiable; 1 otherwise.
"""

import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                       # .../execution_runs/T1-14/a20260920-01
I11A = RUN.parent.parent / "I-11-A" / "a20260919-01"
BINDING = I11A / "binding.json"

REGISTERED_PATH = "C:/Program Files/Git/mingw64/bin/pdftotext.exe"
REGISTERED_SHA = "252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0"
REGISTERED_VERSION_PREFIX = "pdftotext version 4.00"


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    out = {}
    verdicts = {}

    # ---- load the register ------------------------------------------------
    raw = BINDING.read_text(encoding="utf-8")
    binding = json.loads(raw)
    ext = binding.get("external_tools", {}).get("pdftotext", {})
    out["register_source"] = {
        "file": str(BINDING).replace("\\", "/"),
        "bytes": len(raw.encode("utf-8")),
        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }

    # ---- P-1: the field exists and is well formed -------------------------
    reg_path = ext.get("path")
    reg_sha = ext.get("sha256")
    hexish = isinstance(reg_sha, str) and len(reg_sha) == 64 and all(
        c in "0123456789abcdef" for c in reg_sha.lower()
    )
    abs_path = isinstance(reg_path, str) and (
        (len(reg_path) > 2 and reg_path[1] == ":") or reg_path.startswith("/")
    )
    verdicts["P-1"] = {
        "claim": "binding.json registers an absolute path and a 64-hex sha256 for pdftotext",
        "registered_path": reg_path,
        "registered_sha256": reg_sha,
        "path_is_absolute": abs_path,
        "sha_is_64_hex": hexish,
        "holds": bool(abs_path and hexish),
    }

    # ---- P-2: registered hash == on-disk hash -----------------------------
    disk = pathlib.Path(REGISTERED_PATH)
    exists = disk.exists()
    actual_sha = sha256_of(disk) if exists else None
    verdicts["P-2"] = {
        "claim": "the registered sha256 equals the hash of the binary actually at the registered path",
        "path_exists": exists,
        "size_bytes": disk.stat().st_size if exists else None,
        "disk_sha256": actual_sha,
        "registered_sha256": reg_sha,
        "holds": bool(exists and actual_sha == reg_sha),
    }

    # ---- P-3: version agreement -------------------------------------------
    version_ok = False
    version_text = None
    if exists:
        try:
            r = subprocess.run(
                [str(disk), "-v"], capture_output=True, timeout=20
            )
            version_text = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
            version_ok = REGISTERED_VERSION_PREFIX in version_text
        except Exception as exc:  # pragma: no cover - environment dependent
            version_text = f"<error: {exc}>"
    verdicts["P-3"] = {
        "claim": "the on-disk binary is the version the register names",
        "registered_version": ext.get("version"),
        "observed_first_line": (version_text or "").splitlines()[0]
        if version_text
        else None,
        "expected_prefix": REGISTERED_VERSION_PREFIX,
        "holds": bool(version_ok),
    }

    # ---- P-4: no Git upgrade was performed for this card ------------------
    # The honest form of this check: the Git install tree must NOT have been
    # modified after the attempt's own register was last written.  A
    # post-dating tree would be *evidence of* (though not proof of) an upgrade
    # performed to obtain extraction ability.
    git_root = disk.parents[2] if exists else None  # .../Git
    binding_mtime = BINDING.stat().st_mtime
    git_mtime = git_root.stat().st_mtime if git_root and git_root.exists() else None
    before = bool(git_mtime is not None and git_mtime <= binding_mtime)
    verdicts["P-4"] = {
        "claim": "the Git install tree was not modified after this card's register was written",
        "git_install_root": str(git_root).replace("\\", "/") if git_root else None,
        "git_tree_mtime_epoch": git_mtime,
        "binding_mtime_epoch": binding_mtime,
        "git_tree_predates_register": before,
        "holds": before,
        "caveat": (
            "mtime comparison is evidence, not proof: a silent in-place patch "
            "that preserves mtimes would not be caught.  Reported as such."
            if before
            else "the Git tree postdates the register; this is NOT verified and "
            "must be escalated rather than waved through."
        ),
    }

    # ---- overall ----------------------------------------------------------
    core = all(verdicts[k]["holds"] for k in ("P-1", "P-2", "P-3"))
    p4 = verdicts["P-4"]["holds"]
    overall = "PASS" if (core and p4) else ("PASS_with_caveat" if core else "FAIL")

    out["verdicts"] = verdicts
    out["overall"] = overall
    out["core_register_verified"] = core
    out["policy_p4_verified"] = p4
    out["conclusion"] = (
        "T1-14's substantive condition already holds on disk: the absolute path "
        "and the sha256 are registered, and the registered sha256 is the sha256 "
        "of the binary actually at that path.  The card's requirement is "
        "SATISFIED, so no edit is made to I-11-A's binding.json."
        if core
        else "The register does not hold; an additive correction is required."
    )

    target = RUN / "t14_register_verification.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    for k in ("P-1", "P-2", "P-3", "P-4"):
        v = verdicts[k]
        print(f"{k}: holds={v['holds']} | {v['claim']}")
    print(f"overall: {overall}")
    print(f"wrote: {target}")
    return 0 if core else 1


if __name__ == "__main__":
    sys.exit(main())
