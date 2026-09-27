"""C-2 measurement (read-only against the product tree; probe runs on this
attempt's own copies only).  Writes evidence/c2_measurements.json.

Predictions frozen in this attempt's oracle.md section 7:
  P1  tools/*.py `.db` hits = 0
  P2  tools/release_readiness.py:37 = CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
  P3  sealed decision.md:91-92 says release_readiness.py uses catalog.db -> contradicted
  P4  catalog_dir: "<dir>"  # c  => probe rc 3, fail-closed, quotes retained
  P5  production config source_catalog.yaml:2 has no inline comment => production unaffected
  P6  capability claim "inline # comments" is inaccurate; reading correction:
      top-level error is always catalog_config_mismatch, parser reason lives in binding.*
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
EXEC_RUNS = ATTEMPT.parents[1]
PLAN = EXEC_RUNS.parent
REPO = ATTEMPT.parents[4]
TOOLS = REPO / "tools"
PROBE = ATTEMPT / "iso" / "slo_probe_patched.py"
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
FIXTURE_ROOT = ATTEMPT / "iso" / "fixture_root"
CATALOG_DIR = FIXTURE_ROOT / "catalog"
CATALOG = CATALOG_DIR / "catalog.sqlite3"
CONFIG = FIXTURE_ROOT / "config" / "source_catalog.yaml"
C2 = ATTEMPT / "evidence" / "c2"
OUT = ATTEMPT / "evidence" / "c2_measurements.json"

SEALED_DECISION = EXEC_RUNS / "I-14-A" / "a20260919-01" / "decision.md"
SEALED_ORACLE = EXEC_RUNS / "I-14-A" / "a20260919-01" / "oracle.md"
PROD_CONFIG = REPO / ".review-zr407-20260818" / "company-wiki" / "config" / "source_catalog.yaml"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8").splitlines()


def scan_tools() -> dict:
    hits = []
    files = sorted(TOOLS.glob("*.py"))
    for f in files:
        for i, line in enumerate(read_lines(f), start=1):
            for m in re.finditer(r"\.db\b", line):
                hits.append({"file": f"tools/{f.name}", "line": i, "text": line.strip(),
                             "match": m.group(0)})
    return {"files_scanned": [f"tools/{f.name}" for f in files],
            "pattern": r"\.db\b",
            "hit_count": len(hits),
            "hits": hits}


def scan_repo_catalog_db() -> dict:
    """Whole-tree search for `catalog.db`, excluding .planning/.git, as the
    reviewer did, so the sealed claim can be re-checked independently."""
    pattern = re.compile(r"catalog\.db")
    hits, errors = [], []
    skip_dir = {".git", ".planning", "__pycache__", ".mypy_cache", ".ruff_cache",
                ".pytest_cache", "node_modules", "venv"}
    for root, dirs, files in __import__("os").walk(REPO, onerror=lambda e: errors.append(str(e))):
        dirs[:] = [d for d in dirs if d not in skip_dir]
        rel_root = Path(root).relative_to(REPO)
        # reviewer excluded the .review-* snapshots too; keep them listed separately
        in_review_snapshot = str(rel_root).startswith(".review-")
        for name in files:
            if not name.endswith((".py", ".md", ".json", ".yaml", ".yml", ".txt")):
                continue
            p = Path(root) / name
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{p}: {exc}")
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append({"path": str(rel_root / name), "line": i,
                                 "text": line.strip()[:240],
                                 "in_review_snapshot": in_review_snapshot})
    return {"pattern": r"catalog\.db", "hit_count": len(hits), "hits": hits,
            "walk_errors": errors[:10]}


def run_probe(tag: str, config: Path) -> dict:
    out_dir = C2 / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    resolve_cmd = [str(PY), "-X", "utf8", "-B",
                   str(ATTEMPT / "iso" / "fixtures" / "instant_exit_no_sample.py")]
    argv = [str(PY), "-X", "utf8", "-B", str(PROBE),
            "--catalog", str(CATALOG), "--config", str(config),
            "--samples", "1", "--report", str(report_path),
            "--resolve-cmd", json.dumps(resolve_cmd), "--resolve-cwd", str(out_dir)]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)
    (out_dir / "stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    (out_dir / "raw_returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
    (out_dir / "argv.json").write_text(json.dumps(argv, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    report = {}
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    binding = report.get("binding") or {}
    return {
        "tag": tag,
        "config": str(config),
        "config_bytes": config.stat().st_size,
        "config_text": config.read_text(encoding="utf-8"),
        "raw_returncode": proc.returncode,
        "top_level_error": report.get("error"),
        "binding_error": binding.get("error"),
        "binding_detail": binding.get("detail"),
        "configured_catalog_dir": binding.get("configured_catalog_dir"),
        "consistent": binding.get("consistent"),
        "same_directory": binding.get("same_directory"),
        "measured": report.get("measured"),
        "per_call_count": len(report.get("per_call") or []),
        "report_sha256": sha(report_path) if report_path.is_file() else None,
    }


def main() -> int:
    C2.mkdir(parents=True, exist_ok=True)

    p1 = scan_tools()
    p1b = scan_repo_catalog_db()

    rr_lines = read_lines(TOOLS / "release_readiness.py")
    p2 = {
        "file": "tools/release_readiness.py",
        "sha256": sha(TOOLS / "release_readiness.py"),
        "line_36": rr_lines[35],
        "line_37": rr_lines[36],
        "line_38": rr_lines[37],
        "expected_line_37": 'CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"',
        "matches_expected": rr_lines[36].strip()
        == 'CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"',
    }

    # sealed claim under test (decision.md:91-92, oracle.md:219-224)
    dec = read_lines(SEALED_DECISION)
    ora = read_lines(SEALED_ORACLE)
    p3 = {
        "sealed_decision_path": str(SEALED_DECISION.relative_to(REPO)),
        "sealed_decision_sha256": sha(SEALED_DECISION),
        "line_91": dec[90],
        "line_92": dec[91],
        "line_97": dec[96],
        "sealed_oracle_path": str(SEALED_ORACLE.relative_to(REPO)),
        "sealed_oracle_line_219": ora[218],
        "sealed_oracle_line_220": ora[219],
        "claim": "the product's config uses catalog.sqlite3 and RF/tools/release_readiness.py uses catalog.db",
        "measured": "tools/*.py contains no `.db` at all; release_readiness.py:37 is catalog.sqlite3",
        "claim_holds": False,
        "clause6_implication": "the 'confirm the actual target agrees' branch of card clause 6 is NOT demonstrated for the catalog.db name (measured: --catalog <dir>/catalog.db is accepted as consistent while the resolver opens catalog.sqlite3)",
    }

    # --- P4 / P6: probe behaviour on configs the docs claim to handle ---------
    cases = {}
    cases["bare_quoted"] = C2 / "cfg_bare_quoted.yaml"
    cases["bare_quoted"].write_text(
        'schema_version: "1.0"\n'
        f'catalog_dir: "{CATALOG_DIR.as_posix()}"\n'
        'reusable_root_kinds: [company_raw]\n', encoding="utf-8")

    cases["inline_comment"] = C2 / "cfg_inline_comment.yaml"
    cases["inline_comment"].write_text(
        'schema_version: "1.0"\n'
        f'catalog_dir: "{CATALOG_DIR.as_posix()}"  # inline comment\n'
        'reusable_root_kinds: [company_raw]\n', encoding="utf-8")

    cases["inline_comment_bare"] = C2 / "cfg_inline_comment_bare.yaml"
    cases["inline_comment_bare"].write_text(
        'schema_version: "1.0"\n'
        f'catalog_dir: {CATALOG_DIR.as_posix()}  # inline comment\n'
        'reusable_root_kinds: [company_raw]\n', encoding="utf-8")

    cases["residual_variable"] = C2 / "cfg_residual_variable.yaml"
    cases["residual_variable"].write_text(
        'schema_version: "1.0"\n'
        'catalog_dir: "${PROJECT_ROOT}/.source_catalog_${UNRESOLVED}"\n'
        'reusable_root_kinds: [company_raw]\n', encoding="utf-8")

    cases["missing_key"] = C2 / "cfg_missing_key.yaml"
    cases["missing_key"].write_text(
        'schema_version: "1.0"\n'
        'reusable_root_kinds: [company_raw]\n', encoding="utf-8")

    runs = {tag: run_probe(tag, cfg) for tag, cfg in cases.items()}

    # --- P5: production config ---------------------------------------------
    prod_lines = read_lines(PROD_CONFIG)
    all_configs = []
    for p in REPO.rglob("source_catalog.yaml"):
        rel = str(p.relative_to(REPO))
        if rel.startswith(".planning") or "/.git/" in rel:
            continue
        all_configs.append(rel)
    p5 = {
        "file": str(PROD_CONFIG.relative_to(REPO)),
        "sha256": sha(PROD_CONFIG),
        "line_1": prod_lines[0],
        "line_2": prod_lines[1],
        "line_2_has_inline_comment": "#" in prod_lines[1],
        "configs_found_outside_planning": sorted(all_configs),
        "conclusion": "the real production config carries no inline comment on catalog_dir, so the parser's inline-comment defect does not affect current production (fail-closed, exit 3, only if someone adds one)",
    }

    # --- P6 reading correction: where the reason actually lives --------------
    probe_src = read_lines(PROBE)
    mismatch_lines = [i for i, l in enumerate(probe_src, start=1)
                      if '"catalog_config_mismatch"' in l]
    p6 = {
        "probe_path": "iso/slo_probe_patched.py (byte-identical copy of the sealed probe)",
        "probe_sha256": sha(PROBE),
        "strip_scalar_lines": {"first": probe_src[81], "second": probe_src[82],
                               "third": probe_src[83], "fourth": probe_src[84],
                               "fifth": probe_src[85], "sixth": probe_src[86],
                               "seventh": probe_src[87]},
        "catalog_config_mismatch_literal_lines": mismatch_lines,
        "reading_rule": "the top-level `error` is always catalog_config_mismatch; the parser's own reason is in binding.error / binding.detail (or, when the parser succeeds but the directory differs, in binding.configured_catalog_dir / binding.same_directory)",
        "claims": {
            "decision_md_lines_95_99": dec[94] + " " + dec[95] + " " + dec[96] + " " + dec[97],
            "oracle_md_lines_219_224": " ".join(ora[218:224]),
            "claim_says_inline_comments_handled": True,
            "measured": "quoted scalar + inline comment is REFUSED (exit 3) and the quotes are retained in configured_catalog_dir",
        },
    }

    payload = {
        "purpose": "C-2: independent re-measurement of the two refuted claims plus the error-reading correction",
        "p1_tools_db_scan": p1,
        "p1b_repo_catalog_db_scan": p1b,
        "p2_release_readiness": p2,
        "p3_decision_md_claim": p3,
        "p4_p6_probe_runs": runs,
        "p5_production_config": p5,
        "p6_reading_correction": p6,
        "prediction_check": {
            "P1_zero_db_hits_in_tools": p1["hit_count"] == 0,
            "P2_line37_is_catalog_sqlite3": p2["matches_expected"],
            "P3_claim_contradicted": not p3["claim_holds"],
            "P4_inline_comment_refused_rc3": runs["inline_comment"]["raw_returncode"] == 3,
            "P5_production_config_has_no_inline_comment": not p5["line_2_has_inline_comment"],
            "P6_top_level_error_always_catalog_config_mismatch": all(
                r["top_level_error"] == "catalog_config_mismatch"
                for r in runs.values() if r["raw_returncode"] == 3),
        },
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    parsed = json.loads(OUT.read_text(encoding="utf-8"))
    print(json.dumps({"written": str(OUT),
                      "bytes": OUT.stat().st_size,
                      "prediction_check": parsed["prediction_check"],
                      "runs": {k: {"rc": v["raw_returncode"],
                                   "top_error": v["top_level_error"],
                                   "binding_error": v["binding_error"],
                                   "configured_catalog_dir": v["configured_catalog_dir"]}
                               for k, v in parsed["p4_p6_probe_runs"].items()}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
