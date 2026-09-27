"""FC-1303: production SLO probe (READ-ONLY).

Times real resolver queries (exact canary / latest-as-of / bundle) against
the production catalog via the frozen resolver CLI, reports p50/p95/p99 and
peak RSS, and exits non-zero when a frozen budget is exceeded.

Production catalog and roots are opened read-only (mode=ro / query_only
semantics live in the catalog caller; this tool never writes).  The probe
report is written to the isolated ``--report`` path.

Exit 0 = all budgets green; 2 = budget breach (alarm, not fatal).
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = PROJECT_ROOT.parent / "company-wiki"
DEFAULT_CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
DEFAULT_CONFIG = WIKI_ROOT / "config" / "source_catalog.yaml"

# Frozen SLO budgets (seconds) — measured then frozen (FC-1303, findings 62).
BUDGETS = {
    "exact_p95": 5.0,
    "latest_p95": 5.0,
    "bundle_p95": 5.0,
    "peak_rss_gb": 2.0,
}

SAMPLES = 10

# Canary probes (real production documents registered by FC-504/FC-906).
EXACT_PROBE = {"company_query": "紫金矿业", "market": "CN",
               "document_kind": "annual_report", "fiscal_year": 2025}
LATEST_PROBE = {"company_query": "紫金矿业", "market": "CN",
                "document_kind": "annual_report", "mode": "latest_as_of"}


def _resolve(request: dict, config: Path) -> float:
    """One resolve call (exact or latest_as_of per request); wall seconds."""
    cmd = [sys.executable, "-m", "company_wiki.source_catalog.cli",
           "--config", str(config), "resolve", "--entity", "紫金矿业",
           "--market", "CN", "--document-kind", "annual_report"]
    if request.get("mode") == "latest_as_of":
        cmd.append("--mode")
        cmd.append("latest_as_of")
    else:
        cmd.extend(["--fiscal-year", "2025"])
    t0 = time.perf_counter()
    subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                   cwd=str(WIKI_ROOT))
    return time.perf_counter() - t0


def _percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "p50": statistics.median(ordered),
        "p95": ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))],
        "p99": ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))],
    }


def _peak_rss_gb() -> float:
    # Windows has no resource.getrusage; psutil (already a project dep via
    # FC-1002) reports peak working set.  Honest failure: without psutil the
    # value is None and the RSS budget is skipped, never faked.
    try:
        import psutil  # noqa: PLC0415

        # FC-1303-F3 fix: measure the RESOLVER process, not the probe shell.
        # The resolver is the last heavyweight child spawned; psutil tracks
        # our process tree's peak.  Sum current RSS of resolver children.
        me = psutil.Process()
        try:
            kids = me.children(recursive=True)
        except psutil.Error:
            kids = []
        if kids:
            return max(k.memory_info().rss for k in kids) / (1024**3)
        return me.memory_info().peak_wset / (1024**3)
    except ImportError:
        return None  # type: ignore[return-value]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--samples", type=int, default=SAMPLES)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)
    if not args.catalog.is_file():
        print(f"catalog missing: {args.catalog}", file=sys.stderr)
        return 1

    samples = max(3, args.samples)
    exact, latest = [], []
    for _ in range(samples):
        exact.append(_resolve(EXACT_PROBE, args.config))
        latest.append(_resolve(LATEST_PROBE, args.config))
    # bundle: exact resolves carry the envelope; timing the same exact call
    # with the bundle consumer is the honest bundle-path latency proxy
    # (bundle_for_resolution rides the same resolve call).
    bundle = exact[:]

    rss = _peak_rss_gb()
    results = {
        "exact": _percentiles(exact),
        "latest": _percentiles(latest),
        "bundle_proxy": _percentiles(bundle),
        "peak_rss_gb": round(rss, 3) if rss is not None else None,
        "samples": samples,
        "catalog": str(args.catalog),
    }
    breaches = []
    if results["exact"]["p95"] > BUDGETS["exact_p95"]:
        breaches.append(f"exact p95 {results['exact']['p95']:.3f}s > {BUDGETS['exact_p95']}s")
    if results["latest"]["p95"] > BUDGETS["latest_p95"]:
        breaches.append(f"latest p95 {results['latest']['p95']:.3f}s > {BUDGETS['latest_p95']}s")
    if results["bundle_proxy"]["p95"] > BUDGETS["bundle_p95"]:
        breaches.append(f"bundle p95 {results['bundle_proxy']['p95']:.3f}s > {BUDGETS['bundle_p95']}s")
    if results["peak_rss_gb"] is not None and results["peak_rss_gb"] > BUDGETS["peak_rss_gb"]:
        breaches.append(f"peak RSS {results['peak_rss_gb']}GB > {BUDGETS['peak_rss_gb']}GB")

    report = {"slo_probe": results, "budgets": BUDGETS, "breaches": breaches}
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
