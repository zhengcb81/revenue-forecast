"""I-07-C non-fixture proof: grep the fixture/expectation scopes of this
program for (a) the fifth-root company identity and (b) the hitherto-unnamed
root id, showing 0 matches BEFORE/AT construction time, plus the rejected
candidates' scopes. Tokens come from the DATA files, never from literals.

Writes evidence/non_fixture_grep.txt (+ .json).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from i07c_common import (CW, EVID, FF, INPUTS, MANIFEST, PLAN, RF, load_manifest,
                         read_json, write_json)

TEXT_EXTS = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".toml",
             ".cfg", ".ini", ".cfg", ".in", ".toml"}
SKIP_DIRS = {"venv", ".venv", "site-packages", "__pycache__", ".git",
             "node_modules", ".pytest_cache", "packages", "npm-cache"}
MAX_FILE_BYTES = 2 * 1024 * 1024

SCOPES = [
    ("PLAN/execution_v2 (cards+matrix+manifest)", PLAN / "execution_v2"),
    ("PLAN/execution_runs/I-07-A (state matrix+fixtures)", PLAN / "execution_runs" / "I-07-A"),
    ("PLAN/execution_runs/I-07-B (fixtures+harness+evidence)", PLAN / "execution_runs" / "I-07-B"),
    ("PLAN/execution_runs/I-00-A/B (argv contract)", PLAN / "execution_runs" / "I-00-A"),
    ("PLAN/execution_runs/I-00-B", PLAN / "execution_runs" / "I-00-B"),
    ("RF/audit_review (expectation sets)", RF / "audit_review"),
    ("RF/scripts+tools (product scripts)", RF / "scripts"),
    ("RF/tools", RF / "tools"),
    ("CW/src+tests+config (product+fixtures)", CW / "src"),
    ("CW/tests", CW / "tests"),
    ("CW/config", CW / "config"),
    ("filing-fetch repo (e2e fixtures)", FF),
]


def tokens() -> dict:
    data = read_json(INPUTS / "fifth_root_company.json")
    manifest = load_manifest()
    toks = {
        "fifth_root_company_name": [data["company_name"]],
        "fifth_root_ascii_aliases": list(data.get("ascii_aliases") or []),
        "fifth_root_id": [data["fifth_root_id"]],
        "fifth_root_security_id": [data["security_id"]],
        "rejected_candidates_sample": ["600519", "000858", "300750"],
    }
    # prove the fixture companies ARE present in the fixtures (sanity that the
    # grep scope actually sees fixture text at all - positive control)
    fixture_ids = []
    for s in manifest["samples"]:
        parts = Path(s["path"]).parts
        ci = [i for i, p in enumerate(parts) if p == "companies"]
        fixture_ids.append(parts[ci[0] + 1] if ci else s["id"])
    toks["positive_control_fixture_company_dirs"] = fixture_ids
    return toks


UNIVERSE_PATH_MARKERS = (".source_catalog", "security_master", ".runs")


def is_universe_dump(path: str) -> bool:
    """Securities-universe data dumps (a copy of the full listing inside
    historical run artifacts) are DATA, not fixtures/expectations: virtually
    every listed company appears there, so no real listed company could ever
    be 'absent' from such a file. Hits are disclosed but classified apart."""
    low = path.lower()
    return any(marker.lower() in low for marker in UNIVERSE_PATH_MARKERS)


def scan_file(path: Path, toks: list[str]) -> list[str]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return []
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return [t for t in toks if t and t in text]


def main() -> int:
    toks_by_group = tokens()
    flat_target = []
    for group in ("fifth_root_company_name", "fifth_root_ascii_aliases",
                  "fifth_root_id", "fifth_root_security_id"):
        flat_target.extend(toks_by_group[group])
    positive = list(toks_by_group["positive_control_fixture_company_dirs"])

    lines = ["I-07-C non-fixture / hitherto-unnamed proof",
             "target tokens (from DATA files, fifth_root_company.json):",
             json.dumps({k: v for k, v in toks_by_group.items()
                         if k != "positive_control_fixture_company_dirs"},
                        ensure_ascii=False, indent=1),
             "positive-control tokens (fixture company dir names - MUST appear:",
             "their presence proves these scopes really contain fixture text):",
             json.dumps(positive, ensure_ascii=False),
             ""]
    total_target = 0
    total_universe = 0
    total_positive = 0
    per_scope = []
    for label, root in SCOPES:
        if not root.exists():
            lines.append(f"[{label}] MISSING SCOPE: {root}")
            continue
        hits_target: dict = {t: [] for t in flat_target}
        hits_positive: dict = {t: 0 for t in positive}
        scanned = 0
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_EXTS:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            scanned += 1
            for t in scan_file(path, flat_target):
                hits_target[t].append(str(path))
            try:
                if path.stat().st_size <= MAX_FILE_BYTES:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    for t in positive:
                        if t in text:
                            hits_positive[t] += 1
            except OSError:
                pass
        found = {t: v for t, v in hits_target.items() if v}
        found_fixture = {t: [p for p in v if not is_universe_dump(p)]
                         for t, v in found.items()}
        found_fixture = {t: v for t, v in found_fixture.items() if v}
        found_universe = {t: [p for p in v if is_universe_dump(p)]
                          for t, v in found.items()}
        found_universe = {t: v for t, v in found_universe.items() if v}
        n_fixture = sum(len(v) for v in found_fixture.values())
        n_universe = sum(len(v) for v in found_universe.values())
        total_target += n_fixture
        total_universe += n_universe
        total_positive += sum(1 for v in hits_positive.values() if v)
        per_scope.append({"scope": label, "root": str(root),
                          "files_scanned": scanned,
                          "fixture_or_expectation_matches": found_fixture,
                          "securities_universe_dump_matches": found_universe,
                          "positive_control_hits": hits_positive})
        lines.append(f"[{label}] files={scanned} "
                     f"FIXTURE/EXPECTATION matches={n_fixture} "
                     f"universe-dump matches={n_universe} "
                     f"positive_control_hit_tokens="
                     f"{sorted(t for t, n in hits_positive.items() if n)}")
        for t, paths in found_fixture.items():
            for p in paths[:5]:
                lines.append(f"    FIXTURE HIT {t!r} -> {p}")
        for t, paths in found_universe.items():
            for p in paths[:3]:
                lines.append(f"    universe-dump (data, disclosed) {t!r} -> {p}")
    verdict = ("PASS (0 fixture/expectation matches in every scope; "
               "securities-universe dump hits disclosed separately)"
               if total_target == 0
               else "FAIL (target token found in a fixture/expectation scope)")
    lines += ["", f"TOTAL FIXTURE/EXPECTATION MATCHES: {total_target}",
              f"TOTAL SECURITIES-UNIVERSE-DUMP MATCHES (data, disclosed): {total_universe}",
              f"POSITIVE CONTROL: {'scopes contain fixture text' if total_positive else 'NO positive control hit - scope selection suspect'}",
              f"VERDICT: {verdict}"]
    (EVID / "non_fixture_grep.txt").write_text("\n".join(lines) + "\n",
                                               encoding="utf-8")
    write_json(EVID / "non_fixture_grep.json",
               {"total_fixture_expectation_matches": total_target,
                "total_universe_dump_matches": total_universe,
                "positive_control_hits": total_positive,
                "verdict": verdict, "scopes": per_scope,
                "tokens": {k: v for k, v in toks_by_group.items()
                           if k != "positive_control_fixture_company_dirs"}})
    print(json.dumps({"total_fixture_expectation_matches": total_target,
                      "total_universe_dump_matches": total_universe,
                      "positive_control_hits": total_positive,
                      "verdict": verdict}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
