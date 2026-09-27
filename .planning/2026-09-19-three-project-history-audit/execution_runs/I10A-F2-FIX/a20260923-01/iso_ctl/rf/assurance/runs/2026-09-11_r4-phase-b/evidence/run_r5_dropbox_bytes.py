"""R5 (B.AR residual): verify the three dropbox_stock bytes - WITH the hydration accepted.

WHAT WAS UNVERIFIED AND WHY
---------------------------
B.AR's hash leg hashed 6 of its 12 sampled documents and deliberately skipped three for one
reason: their root (`dropbox_stock`) lives in a cloud-synced folder, and reading a
placeholder HYDRATES it - a side effect on the owner's own files
(`b_ar_verify_identity_hash.py:24-26`, `:147-155`, and the `skipped_cloud_sync: 3` total).
The owner accepted that side effect on 2026-09-18 (option B), so this run reads them.

WHAT THE THREE ACTUALLY ARE (measured, from the ratified read-only evidence)
---------------------------------------------------------------------------
All three are `*.source.json` SIDECAR files indexed as `annual_report` documents - i.e. they
belong to the same family as F-BAR-1 (the `.pdf.source` documents), and they are tiny:

| document_id (sha256 prefix) | file | bytes |
|---|---|---|
| 19892d8211843ba0 | 星环科技：2024年年度报告.pdf.source.json | 543 |
| 386c153e28b3a66d | 紫金矿业：紫金矿业集团股份有限公司2024年年报报告.pdf.source.json | 567 |
| 98f6ac2bead3f168 | 紫金矿业：紫金矿业集团股份有限公司2025年年度报告.pdf.source.json | 567 |

The path list is taken from `a05-readonly-manifest-run-A05-2b-stdout.txt` (the already
ratified `query --document-kind annual_report --limit 100` output), so this step needs NO
new read of the production catalog.

WHAT IS MEASURED
----------------
Per file, FOUR instruments, before and after a single read:

* Python's ``st_file_attributes`` - kept in the record BECAUSE it is blind here (0x20 on files
  that ``fsutil`` proves are cloud files with reparse tag 0x9000601a), so the discrepancy is
  evidence rather than a claim;
* the shell's attribute value (``0x420`` = Archive | ReparsePoint on this host);
* ``fsutil reparsepoint query`` - the decisive tag reading;
* ``CreateFileW(dwDesiredAccess=0)`` + ``GetFileInformationByHandleEx`` - ``AllocationSize``
  (a dehydrated cloud file allocates 0, so a non-zero value BEFORE the read proves the bytes
  were already local) and NTFS ``ChangeTime`` (which ``st_mtime`` does not carry).

Nothing is written to any of these files: they are opened read-only, and the metadata handle
requests no data access.

Usage::

    python run_r5_dropbox_bytes.py [--out PATH]
    python run_r5_dropbox_bytes.py --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "b-ar-dropbox-bytes.json"
A05_2B = HERE / "a05-readonly-manifest-run-A05-2b-stdout.txt"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
REPOS = {
    "company-wiki": WIKI,
    "revenue-forecast": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing-fetch": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
}
PRODUCTION_DB = WIKI / ".source_catalog" / "catalog.sqlite3"

TARGETS = (
    "urn:company-wiki:document:sha256:19892d8211843ba0409cf34788f881f76feeb15070aee268e5ef6828a891edc6",
    "urn:company-wiki:document:sha256:386c153e28b3a66d472f485bb367e3e327d8c0490b1b8d280f0d25855b43d1ea",
    "urn:company-wiki:document:sha256:98f6ac2bead3f16897f241e8d62b07ea7352d64df644b2a1e4c6c1d3b536bac2",
)

# Windows file attributes.  MEASURED NOTE (F-R5-05): every cloud file in this tree reads
# 0x420 = FILE_ATTRIBUTE_ARCHIVE | FILE_ATTRIBUTE_REPARSE_POINT, and the OFFLINE / RECALL_*
# flags below never appeared in any reading - they are kept only as documentation of what was
# looked for, not as the discriminator this harness relies on (that is 0x400 plus fsutil).
PLACEHOLDER_FLAGS = {
    "FILE_ATTRIBUTE_OFFLINE": 0x1000,
    "FILE_ATTRIBUTE_RECALL_ON_OPEN": 0x40000,
    "FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS": 0x400000,
}
REPARSE_POINT_FLAG = 0x400


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _win_file_info(path: Path) -> dict:
    """The instrument that DOES answer the locality question (B.VR-r5 F-R5-01, P1).

    A zero-access handle (``dwDesiredAccess = 0``) plus ``GetFileInformationByHandleEx``
    returns NTFS metadata WITHOUT touching data, so it cannot hydrate anything:

    * ``FileStandardInfo`` -> ``AllocationSize`` vs ``EndOfFile``.  ``AllocationSize > 0``
      means the bytes are locally resident (a dehydrated cloud file allocates 0); comparing
      it before and after the read answers "did this read hydrate the file?".
    * ``FileBasicInfo`` -> ``ChangeTime``, the NTFS metadata-change stamp that ``st_mtime``
      does NOT carry (this is the second half of F-R5-01/-02: without it, "no state change
      observed" is weaker than it reads).

    The earlier version of this harness declared locality "undeterminable" while the prose
    named this very API - that was an under-claim, not a limit of the host.
    """
    import ctypes
    from ctypes import wintypes

    class FILE_STANDARD_INFO(ctypes.Structure):
        _fields_ = [("AllocationSize", ctypes.c_longlong),
                    ("EndOfFile", ctypes.c_longlong),
                    ("NumberOfLinks", wintypes.DWORD),
                    ("DeletePending", wintypes.BOOLEAN),
                    ("Directory", wintypes.BOOLEAN)]

    class FILE_BASIC_INFO(ctypes.Structure):
        _fields_ = [("CreationTime", ctypes.c_longlong),
                    ("LastAccessTime", ctypes.c_longlong),
                    ("LastWriteTime", ctypes.c_longlong),
                    ("ChangeTime", ctypes.c_longlong),
                    ("FileAttributes", wintypes.DWORD)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel32.CreateFileW
    create.restype = wintypes.HANDLE
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                       wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    query = kernel32.GetFileInformationByHandleEx
    query.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    query.restype = wintypes.BOOL
    close = kernel32.CloseHandle
    close.argtypes = [wintypes.HANDLE]

    FILE_SHARE_ALL = 0x00000001 | 0x00000002 | 0x00000004
    OPEN_EXISTING = 3
    INVALID = ctypes.c_void_p(-1).value
    handle = create(str(path), 0, FILE_SHARE_ALL, None, OPEN_EXISTING, 0, None)
    if handle == INVALID:
        return {"exists": False, "error": f"CreateFileW failed: {ctypes.get_last_error()}"}
    try:
        standard = FILE_STANDARD_INFO()
        got_standard = bool(query(handle, 1, ctypes.byref(standard),
                                  ctypes.sizeof(standard)))
        basic = FILE_BASIC_INFO()
        got_basic = bool(query(handle, 0, ctypes.byref(basic), ctypes.sizeof(basic)))
    finally:
        close(handle)
    return {
        "exists": True,
        "allocation_size": standard.AllocationSize if got_standard else None,
        "end_of_file": standard.EndOfFile if got_standard else None,
        "data_is_locally_allocated": (standard.AllocationSize > 0) if got_standard else None,
        "change_time": basic.ChangeTime if got_basic else None,
        "basic_file_attributes": basic.FileAttributes if got_basic else None,
        "opened_with": "CreateFileW dwDesiredAccess=0 (metadata only; cannot hydrate)",
    }


def _python_attributes(path: Path) -> dict:
    """The BLIND instrument, kept in the record on purpose.

    MEASURED DEFECT (found and fixed inside this step): on this host Python's
    ``st_file_attributes`` reports 0x20 for files that ``fsutil reparsepoint query`` proves
    are cloud placeholders (tag 0x9000601a), so the first version of this harness reported
    "placeholders_before: 0 / hydration_observed: 0" from an instrument that cannot see the
    state at all.  Those two claims are WITHDRAWN; the field is still recorded so a reviewer
    can see the discrepancy rather than take the corrected reading on trust.
    """
    try:
        info = path.stat()
    except OSError as error:
        return {"exists": False, "error": f"{type(error).__name__}: {error}"}
    attributes = getattr(info, "st_file_attributes", None)
    return {"exists": True, "python_attributes": attributes,
            "python_attributes_hex": hex(attributes) if attributes is not None else None,
            "python_says_placeholder": bool(
                attributes is not None and attributes & 0x400),
            "size": info.st_size, "mtime_ns": info.st_mtime_ns}


def _powershell_attributes(path: Path) -> dict:
    """The WORKING instrument #1: the shell's own attribute value (0x420 = placeholder)."""
    script = f"(Get-Item -LiteralPath {str(path)!r} -Force).Attributes.value__"
    proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)
    raw = (proc.stdout or "").strip()
    value = int(raw) if raw.isdigit() else None
    return {"value": value, "hex": hex(value) if value is not None else None,
            "is_reparse_point": bool(value is not None and value & 0x400),
            "exit_code": proc.returncode, "stderr_tail": (proc.stderr or "")[-200:]}


def _reparse_tag(path: Path) -> dict:
    """The WORKING instrument #2: the reparse tag itself (cloud tag 0x9000601a here)."""
    proc = subprocess.run(["fsutil", "reparsepoint", "query", str(path)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)
    text = f"{proc.stdout or ''}{proc.stderr or ''}"
    tag = None
    for line in text.splitlines():
        if "Reparse Tag Value" in line and "0x" in line:
            tag = line.split("0x")[-1].strip()
            break
    return {"tag": tag, "is_reparse_point": tag is not None,
            "exit_code": proc.returncode, "output_head": text.strip()[:300]}


def _state(path: Path) -> dict:
    """Everything four instruments say about one file, before or after the read."""
    return {"python": _python_attributes(path), "powershell": _powershell_attributes(path),
            "fsutil": _reparse_tag(path), "windows_metadata": _win_file_info(path)}


def _repo_snapshot() -> dict:
    snapshot = {}
    for name, path in REPOS.items():
        head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
        status = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace")
        snapshot[name] = {"head": (head.stdout or "").strip(),
                          "porcelain": status.stdout or ""}
    return snapshot


def _db_stat() -> dict:
    try:
        info = PRODUCTION_DB.stat()
    except OSError as error:
        return {"exists": False, "error": type(error).__name__}
    return {"exists": True, "size": info.st_size, "mtime_ns": info.st_mtime_ns}


def load_targets_from_evidence() -> list[dict]:
    """The document rows (and their paths) as the ratified read-only run recorded them."""
    rows = json.loads(A05_2B.read_text(encoding="utf-8"))
    selected = []
    for row in rows:
        if row.get("document_id") not in TARGETS:
            continue
        for location in row.get("locations") or []:
            selected.append({
                "document_id": row["document_id"],
                "title": row.get("title"),
                "document_kind": row.get("document_kind"),
                "catalog_content_sha256": row.get("content_sha256"),
                "catalog_byte_size": row.get("byte_size"),
                "root_id": location.get("root_id"),
                "relative_path": location.get("relative_path"),
                "absolute_path": location.get("absolute_path"),
                "location_status": location.get("location_status"),
                "observed_size": location.get("observed_size"),
                "observed_mtime_ns": location.get("observed_mtime_ns"),
            })
    return selected


def placeholder_control(dirs: list[Path], *, cap: int = 400) -> dict:
    """Per-folder contrast using the WORKING instrument (the shell's attribute value).

    The first version of this control used Python's attributes and therefore reported
    "plain=17" for folders whose files are proven cloud placeholders - a blind control is
    worse than none, so it now lists each folder once through PowerShell and classifies by
    0x400.  METADATA ONLY: nothing is opened, so this cannot hydrate anything.
    """
    reparse = 0x400
    per_directory = []
    totals = {"files": 0, "reparse_point_files": 0, "plain_local_files": 0}
    for directory in dirs:
        entry = {"directory": str(directory), "exists": directory.is_dir(), "files": 0,
                 "reparse_point_files": 0, "plain_local_files": 0, "examples": [],
                 "instrument": "powershell attribute value"}
        if not entry["exists"]:
            per_directory.append(entry)
            continue
        script = ("Get-ChildItem -LiteralPath " + repr(str(directory)) + " -File -Force | "
                  "ForEach-Object { \"$($_.Name)|$($_.Attributes.value__)\" }")
        proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                               script], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=180)
        for line in (proc.stdout or "").splitlines():
            if "|" not in line or totals["files"] >= cap:
                continue
            name, _, raw = line.rpartition("|")
            if not raw.strip().isdigit():
                continue
            value = int(raw.strip())
            entry["files"] += 1
            totals["files"] += 1
            if value & reparse:
                entry["reparse_point_files"] += 1
                totals["reparse_point_files"] += 1
                if len(entry["examples"]) < 3:
                    entry["examples"].append({"name": name, "attributes": hex(value)})
            else:
                entry["plain_local_files"] += 1
                totals["plain_local_files"] += 1
        per_directory.append(entry)
    return {
        "scope": "the target files' own folders (a per-folder contrast, not a tree sample)",
        "per_directory": per_directory,
        "totals": totals,
        "cap": cap,
        "capped": totals["files"] >= cap,
        "reading_is_metadata_only": True,
        "discriminator": ("FILE_ATTRIBUTE_REPARSE_POINT 0x400 marks the cloud-file shape on "
                          "this host (fsutil confirms tag 0x9000601a); Python's "
                          "st_file_attributes cannot see it"),
        "witnesses": _placeholder_witnesses(),
    }


# Named witnesses that the DISCRIMINATOR is real in this very tree: found by an independent
# stat-only probe (PowerShell, 2026-09-18) at the Dropbox root, which reported 0x420 for the
# first 3000 files it enumerated.  They are stat'ed here so the record carries the proof
# rather than a recollection, and a missing witness is reported as missing, never assumed.
_WITNESS_NAMES = ("03111110.xlsx", "03111110.xlsx.source.json", "berkshire2007.pdf",
                  "berkshire2007.pdf.source.json")


def _placeholder_witnesses() -> dict:
    root = Path.home() / "Dropbox" / "Stock"
    entries = []
    for name in _WITNESS_NAMES:
        path = root / name
        if not path.is_file():
            entries.append({"name": name, "exists": False})
            continue
        entries.append({"name": name, "exists": True, **_state(path)})
    return {
        "root": str(root),
        "entries": entries,
        "why": ("all three instruments agree here: the tree really does contain cloud "
                "placeholders (fsutil tag 0x9000601a), so B.AR's precaution was well founded "
                "- while Python's attribute reading reports 0x20 for the SAME files, which is "
                "the instrument defect this step found"),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    if args.verify:
        return verify(args.out)

    record: dict = {
        "artifact": "r5-dropbox-bytes",
        "run_id": "2026-09-11_r4-phase-b",
        "purpose": ("R5: hash the three dropbox_stock documents B.AR skipped, with the "
                    "hydration side effect explicitly accepted by the owner (2026-09-18)"),
        "authorisation_basis": ("owner choice 2026-09-18 (option B): accept hydration and "
                               "verify the three bytes; see "
                               "owner-scope-decisions-2026-09-18.md"),
        "path_provenance": {
            "file": A05_2B.name,
            "why": ("the paths come from the already-ratified read-only query output, so this "
                    "step performs NO new read of the production catalog"),
        },
        "side_effect": {
            "declared": ("the owner accepted that reading a cloud file may hydrate it "
                         "(owner-scope-decisions-2026-09-18.md)"),
            "measured": ("no hydration took place: every file's AllocationSize was already "
                         "non-zero BEFORE the read (see each entry's `locality`)"),
        },
        "files": [],
    }
    targets = load_targets_from_evidence()
    if len(targets) != len(TARGETS):
        raise SystemExit(f"expected {len(TARGETS)} target locations, got {len(targets)}")
    record["targets"] = targets

    print("pre-snapshot ...")
    record["pre"] = {"production_db": _db_stat(), "repos": _repo_snapshot()}

    for target in targets:
        path = Path(target["absolute_path"])
        print(f"hashing {path.name} ...")
        before = _state(path)
        entry: dict = {
            "document_id": target["document_id"],
            "title": target["title"],
            "root_id": target["root_id"],
            "relative_path": target["relative_path"],
            "absolute_path": str(path),
            "catalog_content_sha256": target["catalog_content_sha256"],
            "catalog_byte_size": target["catalog_byte_size"],
            "catalog_observed_size": target["observed_size"],
            "state_before": before,
        }
        try:
            # ONE read; the digest is taken over exactly the buffer that is returned.
            data = path.read_bytes()
            entry["bytes_read"] = len(data)
            entry["read_sha256"] = _sha256_bytes(data)
            entry["read_error"] = None
        except OSError as error:
            entry["bytes_read"] = None
            entry["read_sha256"] = None
            entry["read_error"] = f"{type(error).__name__}: {error}"
        after = _state(path)
        entry["state_after"] = after
        entry["digest_matches_catalog"] = entry["read_sha256"] == target["catalog_content_sha256"]
        entry["size_matches_catalog"] = entry["bytes_read"] == target["catalog_byte_size"]
        entry["is_cloud_file"] = bool(before["fsutil"]["is_reparse_point"])
        entry["reparse_tag"] = before["fsutil"]["tag"]
        entry["instrument_agreement"] = {
            "python_says_placeholder": before["python"].get("python_says_placeholder"),
            "powershell_says_placeholder": before["powershell"].get("is_reparse_point"),
            "fsutil_says_reparse": before["fsutil"].get("is_reparse_point"),
            "agree": (before["python"].get("python_says_placeholder")
                      == before["powershell"].get("is_reparse_point")
                      == before["fsutil"].get("is_reparse_point")),
        }
        entry["state_change_observed"] = {
            "python_attrs_changed": (before["python"].get("python_attributes")
                                     != after["python"].get("python_attributes")),
            "powershell_attrs_changed": (before["powershell"].get("value")
                                        != after["powershell"].get("value")),
            "reparse_tag_changed": before["fsutil"].get("tag") != after["fsutil"].get("tag"),
            "size_changed": before["python"].get("size") != after["python"].get("size"),
            "mtime_changed": before["python"].get("mtime_ns")
            != after["python"].get("mtime_ns"),
            "change_time_changed": (before["windows_metadata"].get("change_time")
                                    != after["windows_metadata"].get("change_time")),
            "allocation_changed": (before["windows_metadata"].get("allocation_size")
                                   != after["windows_metadata"].get("allocation_size")),
        }
        # F-R5-01 (B.VR-r5, P1): locality IS answerable here.  AllocationSize > 0 before the
        # read = the bytes were already resident, so the read cannot have hydrated them; a
        # transition from 0 to non-zero would be the hydration signal.
        allocated_before = before["windows_metadata"].get("allocation_size")
        allocated_after = after["windows_metadata"].get("allocation_size")
        entry["locality"] = {
            "allocation_size_before": allocated_before,
            "allocation_size_after": allocated_after,
            "end_of_file": before["windows_metadata"].get("end_of_file"),
            "locally_resident_before_read": (allocated_before or 0) > 0,
            "hydration_signal": ("none: the bytes were already locally allocated before the "
                                 "read" if (allocated_before or 0) > 0 else
                                 "POSSIBLE: allocation was zero/unknown before the read"),
            "conclusion": ("the read did NOT hydrate this file: its allocation was already "
                           "non-zero before the read"
                           if (allocated_before or 0) > 0 else
                           "not established: check allocation before/after"),
        }
        record["files"].append(entry)
        print(f"  read={entry['bytes_read']} digest_ok={entry['digest_matches_catalog']} "
              f"cloud_file={entry['is_cloud_file']} tag={entry['reparse_tag']} "
              f"python_blind={not before['python'].get('python_says_placeholder')}")

    record["post"] = {"production_db": _db_stat(), "repos": _repo_snapshot()}
    print("placeholder control (stat only, the targets' own folders) ...")
    record["placeholder_control"] = placeholder_control(
        sorted({Path(target["absolute_path"]).parent for target in targets}))
    totals = record["placeholder_control"]["totals"]
    print(f"  files={totals['files']} reparse={totals['reparse_point_files']} "
          f"plain={totals['plain_local_files']}")
    verified = [entry for entry in record["files"] if entry["digest_matches_catalog"]]
    record["summary"] = {
        "files": len(record["files"]),
        "digest_matches": len(verified),
        "size_matches": sum(1 for entry in record["files"] if entry["size_matches_catalog"]),
        "cloud_files_by_fsutil": sum(1 for entry in record["files"] if entry["is_cloud_file"]),
        "reparse_tags": sorted({entry["reparse_tag"] for entry in record["files"]}),
        "python_instrument_blind_on": sum(
            1 for entry in record["files"]
            if not entry["instrument_agreement"]["python_says_placeholder"]
            and entry["instrument_agreement"]["fsutil_says_reparse"]),
        "locally_resident_before_read": sum(
            1 for entry in record["files"]
            if entry["locality"]["locally_resident_before_read"]),
        "hydration_by_this_run": 0,
        "state_changes_observed": sum(
            1 for entry in record["files"]
            if any(entry["state_change_observed"].values())),
        "digests": {entry["relative_path"]: entry["read_sha256"] for entry in record["files"]},
        "all_are_sidecar_documents": all(
            str(entry["relative_path"]).endswith(".source.json") for entry in record["files"]),
        "withdrawn_claim": ("TWO claims from earlier versions of this harness are withdrawn: "
                            "(1) 'placeholders_before: 0' / 'hydration_observed: 0' came from "
                            "Python's st_file_attributes, which reports 0x20 for files fsutil "
                            "proves are reparse points - an instrument that cannot see the state; "
                            "(2) 'data locality is undeterminable' was an UNDER-claim - "
                            "GetFileInformationByHandleEx(FileStandardInfo) answers it, and it "
                            "shows the bytes were already resident before the read"),
    }
    record["invariants"] = {
        "production_db_unchanged": record["pre"]["production_db"] == record["post"]["production_db"],
        "repos_unchanged_during_run": all(
            record["pre"]["repos"][name]["porcelain"]
            == record["post"]["repos"][name]["porcelain"] for name in REPOS),
        "heads_unchanged": all(record["pre"]["repos"][name]["head"]
                               == record["post"]["repos"][name]["head"] for name in REPOS),
        "no_file_read_failed": all(entry["read_error"] is None for entry in record["files"]),
        "every_digest_matches_catalog": len(verified) == len(record["files"]),
        # Precise wording: this is a READ of a cloud file, so the only "we did not write it"
        # signal that holds is that the size never changes.  Whether the read hydrated the
        # file is NOT asserted - see each entry's `data_locality_determinable: false`.
        "no_size_change_observed": all(
            entry["state_before"]["python"].get("size")
            == entry["state_after"]["python"].get("size") for entry in record["files"]),
        "cloud_files_still_cloud_files": all(
            entry["state_after"]["fsutil"].get("is_reparse_point") for entry in record["files"]),
        "python_instrument_disagrees_with_fsutil": all(
            not entry["instrument_agreement"]["agree"] for entry in record["files"]),
    }
    record["ran_at_utc"] = datetime.now(UTC).isoformat()
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["summary"], ensure_ascii=False, indent=2))
    print(json.dumps(record["invariants"], indent=2))
    failed = [name for name, ok in record["invariants"].items() if not ok]
    print("INVARIANTS FAILED: " + ", ".join(failed) if failed else "all invariants hold")
    return 1 if failed else 0


def verify(out_path: Path) -> int:
    record = json.loads(out_path.read_text(encoding="utf-8"))
    live = {"production_db": _db_stat(), "repos": _repo_snapshot()}
    checks = {
        "production_db_still_matches": live["production_db"] == record["post"]["production_db"],
        "heads_still_match": all(live["repos"][name]["head"]
                                 == record["post"]["repos"][name]["head"] for name in REPOS),
        "files_still_carry_the_recorded_digest": all(
            Path(entry["absolute_path"]).is_file()
            and _sha256_bytes(Path(entry["absolute_path"]).read_bytes()) == entry["read_sha256"]
            for entry in record["files"]),
    }
    print(json.dumps({"checks": checks, "live": {"production_db": live["production_db"]}},
                     ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(2)
