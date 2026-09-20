"""I-14-A: the frozen fixture specification, shared by every evidence producer.

One source of truth so the probe's own report, the pytest suite, the CLI
comparison and the independent verifier cannot drift apart.  Values come from
oracle.md sections 3-5 and were frozen before any run.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
FIXTURES = ATTEMPT / "iso" / "fixtures"
PYTHON = str(ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe")

# A config whose catalog_dir points at the attempt's own catalog directory, so
# every fixture run is bound to an attempt-owned catalog and never to the
# production one.  Written by run_probe_cases.py on first use.
FIXTURE_ROOT = ATTEMPT / "iso" / "fixture_root"
FIXTURE_CATALOG_DIR = FIXTURE_ROOT / "catalog"
FIXTURE_CATALOG = FIXTURE_CATALOG_DIR / "catalog.sqlite3"
FIXTURE_CONFIG = FIXTURE_ROOT / "config" / "source_catalog.yaml"
# A second catalog, used only to prove the mismatch refusal.
MISMATCH_CATALOG = FIXTURE_ROOT / "other_catalog" / "catalog.sqlite3"

FIXTURE_SCRIPTS = {
    "F1": FIXTURES / "exit7_success_stdout.py",
    "F2": FIXTURES / "exit0_business_failure.py",
    "F3": FIXTURES / "alive_allocate_then_exit.py",
    "F4": FIXTURES / "instant_exit_no_sample.py",
}

# The argv the probe appends to the template.  Frozen: these are exactly the
# flags the production probe asks the resolver for.
EXACT_ARGV_TAIL = ["--company-query", "紫金矿业", "--market", "CN",
                   "--document-kind", "annual_report", "--fiscal-year", "2025"]
LATEST_ARGV_TAIL = ["--company-query", "紫金矿业", "--market", "CN",
                    "--document-kind", "annual_report", "--mode", "latest_as_of"]

CASES = {
    # id: (fixture key, extra probe argv, frozen expectation)
    "E0-baseline-F4": {
        "fixture": "F4",
        "purpose": "clean baseline: valid success output; a fast child still yields "
                   "one live sample because the sampler reads at spawn time",
        "expect_rc": 2,
        "expect_business": {
            "calls_failed": 0,
            "peak_rss_gt": 0.0,
            "peak_rss_source": "live_sample",
            "rss_sample_count_min_gte": 1,
            "rss_pids_include_child_pids": True,
            "fixture_pid_is_in_samples": True,
        },
    },
    "E1a-F1-exit7-success-stdout": {
        "fixture": "F1",
        "purpose": "non-zero rc with success-shaped stdout must be a measurement failure",
        "expect_rc": 4,
        "expect_business": {
            "calls_failed": 6,
            "failed_kind_subprocess_rc": 6,
            "raw_returncode_all": 7,
            "exact_succeeded_count": 0,
            "latest_succeeded_count": 0,
        },
    },
    "E1b-F2-exit0-business-failure": {
        "fixture": "F2",
        "purpose": "rc 0 with a failed business status must be a measurement failure",
        "expect_rc": 4,
        "expect_business": {
            "calls_failed": 6,
            "failed_kind_business_status": 6,
            "raw_returncode_all": 0,
        },
    },
    "E1c-F3-alive-allocate": {
        "fixture": "F3",
        "purpose": "RSS sampled while the child is alive, keyed to the child pid",
        "expect_rc": 2,
        "expect_business": {
            "calls_failed": 0,
            "peak_rss_gt": 0.0,
            "peak_rss_source": "live_sample",
            "rss_sample_count_min_gte": 10,
            "rss_pids_include_child_pids": True,
            "fixture_pid_is_in_samples": True,
        },
    },
    "E2-F3-sampler-disabled": {
        "fixture": "F3",
        "extra_argv": ["--rss-sampler", "none"],
        "purpose": "a collector that collected nothing must say 'uncollected', "
                   "never 0.0, and must never be green",
        "expect_rc": 2,
        "expect_business": {
            "calls_failed": 0,
            "peak_rss_is_null": True,
            "peak_rss_source": "sampler_disabled",
            "breach_contains": "peak RSS not measured",
        },
    },
    "E3-F4-instant-exit": {
        "fixture": "F4",
        "purpose": "control: a valid, very fast child is still sampled at spawn time "
                   "and must not be recorded as uncollected",
        "expect_rc": 2,
        "expect_business": {
            "calls_failed": 0,
            "peak_rss_gt": 0.0,
            "peak_rss_source": "live_sample",
        },
    },
    "E7-F4-no-bundle-measurement": {
        "fixture": "F4",
        "purpose": "bundle must not be qualified by a copied exact latency",
        "expect_rc": 2,
        "expect_business": {
            "calls_failed": 0,
            "bundle_measured": False,
            "bundle_basis": "unmeasured",
            "breach_contains": "bundle",
        },
    },
    "E7b-F4-bundle-copy-control": {
        "fixture": "F4",
        "extra_argv": [],
        "excluded_from_all": True,
        "purpose": "see harness/run_bundle_control.py — the copied-exact control "
                   "needs its own run to derive the copy from, so it is not part "
                   "of the --all sweep",
        "expect_rc": 0,
        "expect_business": {"calls_failed": 0},
    },
}

BUDGETS_FROZEN = {"exact_p95": 5.0, "latest_p95": 5.0, "bundle_p95": 5.0,
                  "peak_rss_gb": 2.0}

# E6: expected percentiles recomputed by hand in oracle.md section 4.
PERCENTILE_CASES = [
    ([0.1, 0.2, 0.3, 0.4, 0.5], {"p50": 0.3, "p95": 0.5, "p99": 0.5}),
    ([float(v) for v in range(1, 11)], {"p50": 5.5, "p95": 10.0, "p99": 10.0}),
    ([1.0], {"p50": 1.0, "p95": 1.0, "p99": 1.0}),
    ([0.4, 0.1, 0.9, 0.2], {"p50": 0.30000000000000004, "p95": 0.9, "p99": 0.9}),
]

PROBE_CASES_TIMEOUT_SECONDS = 300


def fixture_template(key: str) -> list[str]:
    return [PYTHON, "-X", "utf8", "-B", str(FIXTURE_SCRIPTS[key])]


def case_argv(case_id: str) -> list[str]:
    return copy.deepcopy(CASES[case_id].get("extra_argv", []))


def ensure_fixture_root() -> dict:
    """Create the attempt-owned fixture catalog + config (+ a second catalog)."""
    import sqlite3

    for path in (FIXTURE_CATALOG, MISMATCH_CATALOG):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        con = sqlite3.connect(path)
        try:
            con.execute("CREATE TABLE probe_marker (id INTEGER PRIMARY KEY, note TEXT)")
            con.execute("INSERT INTO probe_marker (note) VALUES (?)",
                        ("i14a fixture catalog",))
            con.commit()
        finally:
            con.close()
    FIXTURE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    config_text = (
        'schema_version: "1.0"\n'
        f'catalog_dir: "{FIXTURE_CATALOG_DIR.as_posix()}"\n'
        'reusable_root_kinds: [company_raw]\n'
        'roots:\n'
        '  - root_id: company_raw\n'
        '    kind: company_raw\n'
        f'    path: "{(FIXTURE_ROOT / "companies").as_posix()}"\n'
        '    priority: 10\n'
        '    privacy_class: public\n'
    )
    FIXTURE_CONFIG.write_text(config_text, encoding="utf-8")
    # The mismatch config names the OTHER catalog while the probe is told to use
    # the fixture catalog: config_catalog_dir != --catalog.
    mismatch_config = FIXTURE_ROOT / "config" / "mismatch_source_catalog.yaml"
    mismatch_config.write_text(
        config_text.replace(FIXTURE_CATALOG_DIR.as_posix(),
                            MISMATCH_CATALOG.parent.as_posix()),
        encoding="utf-8")
    # An accepted config whose catalog_dir IS the fixture catalog, but written
    # unquoted so the probe's small scalar reader has nothing to strip.
    plain_config = FIXTURE_ROOT / "config" / "plain_source_catalog.yaml"
    plain_config.write_text(
        config_text.replace(f'"{FIXTURE_CATALOG_DIR.as_posix()}"',
                            FIXTURE_CATALOG_DIR.as_posix()),
        encoding="utf-8")
    return {
        "fixture_catalog": str(FIXTURE_CATALOG),
        "fixture_config": str(FIXTURE_CONFIG),
        "mismatch_config": str(mismatch_config),
        "plain_config": str(plain_config),
        "python": PYTHON,
        "python_exists": Path(PYTHON).is_file(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(ensure_fixture_root(), ensure_ascii=False, indent=2))
    print(json.dumps({"cases": list(CASES), "python": sys.executable},
                     ensure_ascii=False, indent=2))
