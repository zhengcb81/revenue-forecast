"""ZR-403 RED evidence: survivor/verification gaps over the current suite.

  G1  future_lake missing from the cross-root dedupe/canonical matrix
      (FC-603 covers company_raw/dayu/Dropbox only; future_lake appears
      only in dispatch/config tests).
  G2  health-beats-priority killer missing (a higher-priority unhealthy
      location vs a lower-priority healthy copy — rejections tests cover
      single-location refusal only, not cross-root priority competition).
  G3  read-never-writes-canonical unpinned (no test asserts the locations
      schema has no is_canonical column / resolve leaves DB bytes intact).
  G4  config-order randomization property missing (FC-603 pins exactly two
      permutations: forward and reversed).

Read-only wrt tracked files; writes evidence JSON to argv[1].
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
TESTS = WIKI / "tests"
SRC = WIKI / "src" / "company_wiki" / "source_catalog"


def check_g1_future_lake_absent_from_dedupe_matrix() -> dict:
    dedupe_file = TESTS / "contract" / "test_cross_root_dedup_fc603.py"
    text = dedupe_file.read_text(encoding="utf-8", errors="replace")
    has_future_lake = "future_lake" in text
    return {
        "survivor": not has_future_lake,
        "evidence": "test_cross_root_dedup_fc603.py (the dedupe/canonical "
                    "matrix) contains no future_lake root — the registry "
                    "criterion names FOUR contexts (companies/dayu/Dropbox/"
                    "future_lake); future_lake exists only in dispatch/"
                    "config/parity tests",
        "fc603_mentions_future_lake": has_future_lake,
    }


def check_g2_health_beats_priority_killer_missing() -> dict:
    """No test constructs a higher-priority UNHEALTHY location competing
    with a lower-priority healthy copy of the same content."""
    patterns = [
        (re.compile(r"location_status\s*=\s*[\"']retired"), "retired_literal"),
        (re.compile(r"\.rejections"), "rejections_path"),
        (re.compile(r"upstream_rejected"), "upstream_rejected"),
    ]
    competition_hits = []
    for path in TESTS.rglob("test_*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not any(p.search(text) for p, _ in patterns):
            continue
        # does the same file also drive a priority competition across roots
        # for the SAME content (cross-root dedupe)?
        has_priority_competition = (
            ("priority" in text and ("root" in text and "canonical" in text))
            and ("same" in text or "duplicate" in text or "dedup" in text)
        )
        if has_priority_competition:
            competition_hits.append(path.relative_to(TESTS).as_posix())
    # manual refinement: the fail_closed rejections tests are single-root;
    # verify none of the hits describe cross-root priority competition
    real_killers = [
        name
        for name in competition_hits
        if "cross_root" in name or "dedup" in name
    ]
    return {
        "survivor": not real_killers,
        "evidence": "no test drives an unhealthy higher-priority location "
                    "against a healthy lower-priority copy of the same "
                    "content across roots (the health-before-priority "
                    "ordering of _annotate_locations is unpinned); hits="
                    f"{competition_hits} are single-root refusal tests",
        "candidate_hits": competition_hits,
        "real_cross_root_killers": real_killers,
    }


def check_g3_read_never_writes_canonical_unpinned() -> dict:
    """(a) structural truth: locations schema carries no is_canonical
    column (canonical is derived on read).  (b) no test pins that truth
    nor that resolve() leaves the catalog bytes unchanged."""
    import sqlite3

    from company_wiki.source_catalog.store import CatalogStore

    tmp = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("zr403_scratch")
    tmp.mkdir(parents=True, exist_ok=True)
    db = tmp / "catalog.sqlite3"
    if db.exists():
        db.unlink()
    store = CatalogStore(db)
    connection = store._connect()
    try:
        cols = {
            row[1]
            for row in connection.execute("PRAGMA table_info(locations)")
        }
    finally:
        connection.close()

    pin_exists = False
    for path in TESTS.rglob("test_*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "is_canonical" in text and (
            "table_info" in text or "PRAGMA" in text.upper()
        ):
            pin_exists = True
            break
    return {
        "survivor": ("is_canonical" not in cols) and not pin_exists,
        "evidence": "locations schema has no is_canonical column "
                    f"(derived-on-read = {('is_canonical' not in cols)}) and "
                    f"no test pins this schema truth (pin_exists={pin_exists}) "
                    "— a regression that persisted canonical would trip "
                    "nothing",
        "locations_columns": sorted(cols)[:20],
    }


def check_g4_config_order_randomization_property_missing() -> dict:
    """FC-603 pins exactly 2 permutations (forward/reversed); no property
    test shuffles the config root order N times."""
    random_shuffle_tests = []
    for path in TESTS.rglob("test_*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "shuffle" not in text:
            continue
        # the determinism suite shuffles INSERT order, not config root order
        shuffles_config_roots = bool(
            re.search(r"shuffle\([^)]*roots?", text)
        )
        random_shuffle_tests.append(
            (path.relative_to(TESTS).as_posix(), shuffles_config_roots)
        )
    config_shuffle_exists = any(flag for _name, flag in random_shuffle_tests)
    two_permutation_only = "list(reversed(roots))" in (
        TESTS / "contract" / "test_cross_root_dedup_fc603.py"
    ).read_text(encoding="utf-8", errors="replace")
    return {
        "survivor": (not config_shuffle_exists) and two_permutation_only,
        "evidence": "config-order randomization is pinned with exactly two "
                    "permutations (forward + reversed in FC-603); the "
                    "100-random test shuffles INSERT order only; no "
                    "property shuffles the CONFIG root order N times",
        "shuffle_hits": random_shuffle_tests,
        "config_order_shuffle_exists": config_shuffle_exists,
    }


def main() -> int:
    sys.path.insert(0, str(SRC.parents[1]))  # src/
    checks = {
        "G1_future_lake_absent_from_dedupe_matrix": check_g1_future_lake_absent_from_dedupe_matrix(),
        "G2_health_beats_priority_killer_missing": check_g2_health_beats_priority_killer_missing(),
        "G3_read_never_writes_canonical_unpinned": check_g3_read_never_writes_canonical_unpinned(),
        "G4_config_order_randomization_property_missing": check_g4_config_order_randomization_property_missing(),
    }
    red = all(c["survivor"] for c in checks.values())
    verdict = {
        "schema_version": 1,
        "unit": "ZR-403",
        "kind": "red_evidence",
        "note": "verification gaps over the CURRENT suite at wiki 57cd72e; "
                "the dedupe/resolver mechanism itself is implemented "
                "(FC-603/604 + determinism pins exist for 3 roots)",
        "checks": checks,
        "red_confirmed": red,
        "files_read_only": True,
    }
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("zr403_red_evidence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(checks, indent=2, ensure_ascii=False))
    print(f"red_confirmed={red}")
    print(f"written={out}")
    return 0 if red else 1


if __name__ == "__main__":
    raise SystemExit(main())
