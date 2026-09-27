"""B.VR(B03) independent probe: is ``_inside_configured_roots`` correct at its
edges?

Reviewer-owned; touches nothing but its own temp directories.  Two layers:

* raw ``os.path.realpath`` / ``os.path.normcase`` semantics on this host
  (drive roots, junctions, symlinks, non-existent paths);
* the real ``_inside_configured_roots`` called with hand-built ``RootSpec``
  tuples, plus the full entry point where bytes matter.

Usage: python b03_review_paths.py <out.json>
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceHandle,
    SourceResolver,
    _inside_configured_roots,
)

BODY = b"%PDF-1.4 path-probe-bytes"
DIGEST = hashlib.sha256(BODY).hexdigest()
OUT: dict = {"probe": "b03_review_paths", "wiki_head": ""}
ROWS: list[dict] = []


def head() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(WIKI), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def root(path, kind="company_raw", root_id="r1") -> RootSpec:
    return RootSpec(root_id, Path(path), kind, priority=10)


def handle_for(path: str) -> SourceHandle:
    return SourceHandle(
        schema_version="1.0",
        document_id="urn:company-wiki:document:sha256:" + "a" * 64,
        source_id="urn:company-wiki:source:sha256:" + DIGEST,
        entity_ids=("ent-acme",),
        title="Acme 2025",
        source_type="filing",
        document_kind="annual_report",
        published_date="2026-02-20",
        fiscal_year=2025,
        fiscal_period="FY",
        form_type="10-K",
        language="en",
        provider="sec",
        provider_document_id="doc-1",
        https_url="https://sec.gov/x",
        canonical_location_id="loc-1",
        canonical_path=str(path),
        content_sha256=DIGEST,
        snapshot_sha256=DIGEST,
        mime_type="application/pdf",
        byte_size=len(BODY),
        retrieved_at="2026-02-21T00:00:00+00:00",
        collector_name="probe",
        collector_version="1",
        source_status="active",
        duplicate_group_id="dup-1",
        exact_duplicate_location_count=1,
        capture_ready=True,
        missing_capture_fields=(),
    )


def resolver_for(roots: tuple[RootSpec, ...], base: Path) -> SourceResolver:
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=base,
            catalog_dir=base / ".source_catalog",
            reusable_root_kinds=("company_raw", "directory"),
            roots=roots,
        )
    )
    return SourceResolver(catalog)


def inside(path, roots) -> bool:
    return _inside_configured_roots(Path(path), tuple(roots))


def record(name: str, **kw) -> None:
    ROWS.append({"test": name, **kw})


def mklink_junction(link: Path, target: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    text = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, text.strip()[:200]


def main(argv):
    out_path = Path(argv[1]) if len(argv) > 1 else Path(tempfile.gettempdir()) / "b03_review_paths.json"
    OUT["wiki_head"] = head()
    base = Path(tempfile.mkdtemp(prefix="b03path-"))
    companies = base / "companies"
    companies_extra = base / "companies_extra"
    companies_x = base / "companies_x"
    outside = base / "outside"
    for d in (companies, companies_extra, companies_x, outside):
        d.mkdir(parents=True, exist_ok=True)
    (companies / "2025.pdf").write_bytes(BODY)
    (companies_extra / "2025.pdf").write_bytes(BODY)
    (companies_x / "2025.pdf").write_bytes(BODY)
    (outside / "2025.pdf").write_bytes(BODY)

    # --- raw realpath semantics ------------------------------------------
    OUT["realpath_semantics"] = {
        "C:\\": os.path.realpath("C:\\"),
        "C:\\Users": os.path.realpath("C:\\Users"),
        "C:\\Users\\": os.path.realpath("C:\\Users\\"),
        "trailing_sep_root": os.path.realpath(str(companies) + os.sep),
        "nonexistent_under_existing": os.path.realpath(str(companies / "nope" / "2025.pdf")),
        "normcase_drive": os.path.normcase("C:\\Users\\X"),
    }

    # --- symlink / junction capability -----------------------------------
    link = base / "link_to_companies"
    sym_ok, sym_msg = (False, "")
    try:
        os.symlink(companies, link, target_is_directory=True)
        sym_ok, sym_msg = True, "os.symlink ok"
    except (OSError, NotImplementedError) as exc:
        sym_msg = f"{type(exc).__name__}: {exc}"
    junc = base / "junc_to_companies"
    junc_ok, junc_msg = mklink_junction(junc, companies)
    OUT["capabilities"] = {
        "symlink_dir": {"ok": sym_ok, "msg": sym_msg},
        "junction_dir": {"ok": junc_ok, "msg": junc_msg},
    }
    escape = companies / "escape"
    esc_ok, esc_msg = mklink_junction(escape, outside)
    OUT["capabilities"]["junction_inside_root"] = {"ok": esc_ok, "msg": esc_msg}

    # --- containment matrix ----------------------------------------------
    roots_two = (root(companies), root(companies_extra, root_id="r2"))
    cases = [
        ("plain_inside", companies / "2025.pdf", roots_two, True),
        ("other_root_inside", companies_extra / "2025.pdf", roots_two, True),
        ("textual_prefix_sibling", companies_x / "2025.pdf", roots_two, False),
        ("case_variant_of_target", Path(str(companies / "2025.pdf").upper()), roots_two, True),
        ("case_variant_of_root", companies / "2025.pdf",
         (root(Path(str(companies).upper())),), True),
        ("dotdot_escape", companies / ".." / "outside" / "2025.pdf", roots_two, False),
        ("file_path_equals_root", companies, (root(companies),), True),
        ("root_with_trailing_sep", companies / "2025.pdf",
         (root(str(companies) + os.sep),), True),
        ("nonexistent_under_root", companies / "nope" / "deep" / "2025.pdf",
         (root(companies),), True),
        ("drive_root_root", Path("C:\\Users"), (root("C:\\"),), None),
        ("drive_root_file", Path(r"C:\Windows\win.ini"), (root("C:\\"),), None),
        ("hardlink_to_outside", companies / "hardlink.pdf", (root(companies),), True),
        ("unc_style_root", Path(r"\\localhost\C$\Windows"), (root(r"\\localhost\C$"),), None),
    ]
    os.link(outside / "2025.pdf", companies / "hardlink.pdf")

    if sym_ok:
        cases.append(("symlinked_root_config", link / "2025.pdf", (root(link),), True))
        cases.append(("target_reached_through_symlink",
                      link / "2025.pdf", (root(companies),), True))
    if junc_ok:
        cases.append(("junction_root_config", junc / "2025.pdf", (root(junc),), True))
    if esc_ok:
        cases.append(("junction_escape_inside_root",
                      escape / "2025.pdf", (root(companies),), False))
        cases.append(("nonexistent_under_junction_escape",
                      escape / "nothere.pdf", (root(companies),), False))

    for name, path, rs, expect in cases:
        got = inside(path, rs)
        record(
            "containment::" + name,
            path=str(path),
            roots=[str(r.path) for r in rs],
            inside=got,
            expected=expect,
            matches_expectation=(expect is None or got == expect),
            note="expected=None -> report only (host/policy dependent)",
        )

    # --- end-to-end: does a junction escape actually leak bytes? ----------
    if esc_ok:
        res = resolver_for((root(companies, "company_raw"),), base)
        out = res.read_verified_bytes(handle_for(escape / "2025.pdf"))
        record(
            "entrypoint::junction_escape",
            status=out.status, reason=out.reason, data_is_none=out.data is None,
            bytes_leaked=out.data is not None,
        )
        out2 = res.read_verified_bytes(handle_for(outside / "2025.pdf"))
        record(
            "entrypoint::plain_outside",
            status=out2.status, reason=out2.reason, data_is_none=out2.data is None,
            bytes_leaked=out2.data is not None,
        )
    # hardlink: outside bytes reached through an inside name
    res = resolver_for((root(companies, "company_raw"),), base)
    out = res.read_verified_bytes(handle_for(companies / "hardlink.pdf"))
    record(
        "entrypoint::hardlink_to_outside_bytes",
        status=out.status, reason=out.reason,
        bytes_served=out.data is not None,
        same_bytes_as_outside=(out.data == BODY),
        note="hardlink inside the root; realpath does not resolve hardlinks",
    )
    # drive-root: a legitimate file under a drive-root root
    res_c = resolver_for((root("C:\\"),), base)
    out = res_c.read_verified_bytes(handle_for(r"C:\Windows\win.ini"))
    record(
        "entrypoint::drive_root_root",
        status=out.status, reason=out.reason, detail=out.detail,
        refused_before_reading=(out.status == "not_found"),
        note="root configured as a drive root",
    )

    OUT["results"] = ROWS
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(OUT, fh, ensure_ascii=False, indent=2)
    print(f"wrote {out_path} ({len(ROWS)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
