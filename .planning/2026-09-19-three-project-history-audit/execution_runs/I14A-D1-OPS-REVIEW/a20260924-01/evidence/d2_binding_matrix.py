"""D2 confirmation matrix: ``catalog_dir`` vs ``--catalog`` binding, exercised.

The D2 decision (decision.md D2 / card clause 6) claims:
  * ``catalog_dir`` is a directory, ``--catalog`` is the sqlite file;
  * accepted only when the file lives inside the configured directory under one
    of the two catalog names the product itself uses (``catalog.sqlite3``,
    ``catalog.db``);
  * otherwise exit 3, ``error=catalog_config_mismatch``, nothing measured;
  * the small scalar reader fails CLOSED on forms it does not understand
    (block scalars, anchors, residual ``${...}``) — refuse, never guess.

Every row below builds a config in THIS attempt's evidence directory and runs
the patched probe as a subprocess.  Nothing under the sealed I-14-A attempt is
written.

Usage: python d2_binding_matrix.py <probe.py> <fixture_catalog> <template.json> <out.json>
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build_configs(root: Path, catalog_dir: Path) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    body = (
        'schema_version: "1.0"\n'
        'reusable_root_kinds: [company_raw]\n'
        'roots:\n'
        '  - root_id: company_raw\n'
        '    kind: company_raw\n'
        f'    path: "{(root / "companies").as_posix()}"\n'
        '    priority: 10\n'
        '    privacy_class: public\n'
    )
    cfgs = {
        # forms the small reader is documented to understand
        "cfg_quoted.yaml": f'catalog_dir: "{catalog_dir.as_posix()}"\n' + body,
        "cfg_bare.yaml": f"catalog_dir: {catalog_dir.as_posix()}\n" + body,
        "cfg_comment.yaml": f'catalog_dir: "{catalog_dir.as_posix()}"  # inline comment\n' + body,
        # forms the small reader does NOT understand -> must refuse, not guess
        "cfg_block_scalar.yaml": "catalog_dir: |\n  " + catalog_dir.as_posix() + "\n" + body,
        "cfg_anchor.yaml": f"catalog_dir: &anchor {catalog_dir.as_posix()}\n" + body,
        "cfg_residual_var.yaml": 'catalog_dir: "${UNDEFINED_THING}/x"\n' + body,
        "cfg_missing_key.yaml": 'schema_version: "1.0"\n' + body,
        # right directory, used for the filename rules
        "cfg_ok_dir.yaml": f'catalog_dir: "{catalog_dir.as_posix()}"\n' + body,
    }
    for name, text in cfgs.items():
        (root / name).write_text(text, encoding="utf-8")
    paths = {name: str(root / name) for name in cfgs}

    # ``${PROJECT_ROOT}`` expansion: the probe defines PROJECT_ROOT as
    # ``config.resolve().parents[1]``, so a config living in
    # ``<fixture_root>/config/`` that says "${PROJECT_ROOT}/catalog" must land on
    # the fixture catalog directory.  This one file has to sit inside
    # fixture_root for that arithmetic to work; it is written into THIS
    # attempt's own copy of fixture_root, never into the sealed I-14-A attempt.
    projroot_config = catalog_dir.parent / "config" / "i14a_d2_project_root.yaml"
    projroot_config.write_text('catalog_dir: "${PROJECT_ROOT}/catalog"\n' + body,
                               encoding="utf-8")
    paths["cfg_project_root.yaml"] = str(projroot_config)
    return paths


def main() -> int:
    probe = Path(sys.argv[1])
    fixture_catalog = Path(sys.argv[2])   # .../fixture_root/catalog/catalog.sqlite3
    template = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[4])

    fixture_catalog_dir = fixture_catalog.parent
    other_catalog_dir = fixture_catalog_dir.parent / "other_catalog"
    cfg_dir = HERE / "d2_configs"
    cfgs = build_configs(cfg_dir, fixture_catalog_dir)

    # a file in the configured directory whose name is NOT one of the two names
    odd_name = fixture_catalog_dir / "weird_name.sqlite3"
    odd_name.write_bytes(fixture_catalog.read_bytes())

    rows = []

    def run(name: str, config: Path, catalog: Path, expect_rc: int,
            expect_error: str | None, expect_consistent: bool) -> None:
        report = HERE / "d2_reports" / f"{name}.json"
        report.parent.mkdir(parents=True, exist_ok=True)
        argv = [sys.executable, "-X", "utf8", "-B", str(probe),
                "--catalog", str(catalog), "--config", str(config),
                "--samples", "3", "--report", str(report),
                "--resolve-cmd", json.dumps(template),
                "--resolve-cwd", str(report.parent)]
        proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=300)
        data = {}
        if report.is_file():
            data = json.loads(report.read_text(encoding="utf-8"))
        binding = data.get("binding", {}) or {}
        row = {
            "case": name,
            "raw_returncode": proc.returncode,
            "expect_rc": expect_rc,
            "rc_ok": proc.returncode == expect_rc,
            "error": data.get("error"),
            "expect_error": expect_error,
            "error_ok": data.get("error") == expect_error,
            "consistent": binding.get("consistent"),
            "expect_consistent": expect_consistent,
            "consistent_ok": (binding.get("consistent") is expect_consistent),
            "measured": data.get("measured"),
            "resolve_calls_spawned": len(data.get("per_call") or []),
            "configured_catalog_dir": binding.get("configured_catalog_dir"),
            "parser_error_detail": binding.get("detail"),
            "stderr_head": (proc.stderr or "")[:200],
        }
        rows.append(row)

    # understood forms, consistent -> measured (exit 2: bundle unmeasured breach)
    run("quoted_consistent", cfgs["cfg_quoted.yaml"], fixture_catalog, 2, None, True)
    run("bare_consistent", cfgs["cfg_bare.yaml"], fixture_catalog, 2, None, True)
    run("inline_comment_consistent", cfgs["cfg_comment.yaml"], fixture_catalog, 2, None, True)
    run("project_root_expansion_consistent", cfgs["cfg_project_root.yaml"],
        fixture_catalog, 2, None, True)
    # catalog.db is the product's second known name
    catalog_db = fixture_catalog_dir / "catalog.db"
    catalog_db.write_bytes(fixture_catalog.read_bytes())
    run("catalog_db_name_consistent", cfgs["cfg_ok_dir.yaml"], catalog_db, 2, None, True)
    # refusals
    run("mismatch_other_dir", cfgs["cfg_ok_dir.yaml"],
        other_catalog_dir / "catalog.sqlite3", 3, "catalog_config_mismatch", False)
    run("right_dir_odd_filename", cfgs["cfg_ok_dir.yaml"], odd_name, 3,
        "catalog_config_mismatch", False)
    # a block scalar parses to the literal "|", which is not the configured dir
    run("block_scalar_refused", cfgs["cfg_block_scalar.yaml"], fixture_catalog, 3,
        "catalog_config_mismatch", False)
    run("anchor_refused", cfgs["cfg_anchor.yaml"], fixture_catalog, 3,
        "catalog_config_mismatch", False)
    # residual ${...} and a missing key both raise ValueError inside the reader
    run("residual_variable_refused", cfgs["cfg_residual_var.yaml"], fixture_catalog, 3,
        "config_unreadable_by_probe_parser", False)
    run("missing_key_refused", cfgs["cfg_missing_key.yaml"], fixture_catalog, 3,
        "config_unreadable_by_probe_parser", False)

    doc = {
        "probe": str(probe),
        "rows": rows,
        "all_rc_ok": all(r["rc_ok"] for r in rows),
        "all_error_ok": all(r["error_ok"] for r in rows),
        "all_consistent_ok": all(r["consistent_ok"] for r in rows),
        "refused_rows_spawned_no_resolve_call": all(
            r["resolve_calls_spawned"] == 0 for r in rows if r["raw_returncode"] == 3),
        "accepted_rows_spawned_6_resolve_calls": all(
            r["resolve_calls_spawned"] == 6 for r in rows if r["raw_returncode"] == 2),
    }
    doc["all_ok"] = (doc["all_rc_ok"] and doc["all_error_ok"] and doc["all_consistent_ok"]
                     and doc["refused_rows_spawned_no_resolve_call"]
                     and doc["accepted_rows_spawned_6_resolve_calls"])
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0 if doc["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
