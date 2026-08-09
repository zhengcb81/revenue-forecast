"""WU-101: three-repo immutable baseline capture + gate (BASE-01..04).

Captures, for the data-lake refactor plan: repo HEAD/branch/dirty paths,
plan hash, config byte hashes, pytest collect-only node IDs, and the
user-dirty allowlist (llm_cost_log.csv, source_manifests/archive) that no
WU may ever touch.  ``--check`` re-verifies the current state against a
captured baseline; any drift fails the gate.

Exit codes: 0 = capture written / check passed; 1 = drift or usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = PLAN_DIR / "baselines" / "WU-101-baseline.json"

# WU-101: these user-owned dirty paths must never enter an implementation
# allowlist; any WU touching them must stop immediately.
USER_DIRTY = [
    "llm_cost_log.csv",
    "source_manifests/archive",
]

REPOS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}

CONFIG_FILES = {
    "revenue": ["config/company_wiki.json"],
    "filing": ["config/company_wiki.json"],
    "wiki": ["config/source_catalog.yaml", "config/source_catalog_worker.yaml"],
}

# pytest suite roots per repo (run from the repo root); filing excludes the
# live-tool suites that CI already excludes by explicit reason.
SUITE_ARGS = {
    "revenue": ["tests", "tools/tests"],
    "filing": [
        "tests",
        "--ignore=tests/test_real_tool_conformance.py",
        "--ignore=tests/test_e2e_download.py",
    ],
    "wiki": ["tests/unit", "tests/contract"],
}
COLLECT_COMMANDS = {
    name: ["-m", "pytest", *suite, "--collect-only", "-q"]
    for name, suite in SUITE_ARGS.items()
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def capture_manifest(
    repos: dict,
    collection: dict,
    config_hashes: dict,
    plan_hash: str,
    user_dirty: list[str],
) -> dict:
    """Deterministic baseline payload (no timestamps; caller stamps the file)."""
    return {
        "plan_hash": plan_hash,
        "repos": repos,
        "collection": collection,
        "user_dirty": sorted(user_dirty),
        "config_hashes": dict(sorted(config_hashes.items())),
    }


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True, timeout=60,
    ).stdout.strip()


def collect_repo_state(repo_name: str, repo: Path) -> dict:
    return {
        "path": str(repo),
        "head": _git(repo, "rev-parse", "HEAD"),
        "branch": _git(repo, "branch", "--show-current"),
        "dirty": _git(repo, "status", "--short").splitlines(),
    }


def _parse_collect_output(stdout: str) -> list[str]:
    """Extract node IDs from either the plain nodeid format (``path::name``)
    or the tree format (``<Dir>/<Module>/<Function>``) that repo pytest.ini
    console style can produce (wiki)."""
    plain = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and "::" in line and not line.strip().startswith("=")
    ]
    if plain:
        return plain
    nodes: list[str] = []
    stack: list[tuple[int, str, bool]] = []  # (indent, name, is_module)
    for raw_line in stdout.splitlines():
        if not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if stripped.startswith("<Dir "):
            name = stripped[len("<Dir "):-1]
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, name, False))
        elif stripped.startswith("<Module "):
            name = stripped[len("<Module "):-1]
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, name, True))
        elif stripped.startswith("<Function "):
            name = stripped[len("<Function "):-1]
            # reconstruct: dirs (skip the repo-name root Dir) + module + name
            dirs = [entry[1] for entry in stack if not entry[2]]
            module = next((entry[1] for entry in reversed(stack) if entry[2]), "")
            parts = [p for p in dirs if p and p != Path(module).name]
            # drop the repo-root Dir (first entry) if present
            if parts and len(dirs) > 0:
                parts = parts[1:]
            nodes.append("/".join(parts + [module, name]))
    return nodes


def _run_summary_counts(repo_name: str, repo: Path) -> dict[str, int]:
    """Execute the repo suite once (-q -rs, no cache) and count
    skipped/xfailed from the summary line — collect-only cannot distinguish
    skip-marked nodes (BASE-03 reviewer finding)."""
    command = [
        sys.executable, "-m", "pytest", *SUITE_ARGS[repo_name],
        "-q", "-rs", "-p", "no:cacheprovider",
    ]
    proc = subprocess.run(
        command, cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=1800, check=False,
    )
    counts: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        for match in re.finditer(r"(\d+) (passed|failed|error|skipped|xfailed)", line):
            counts[match.group(2)] = counts.get(match.group(2), 0) + int(match.group(1))
    return counts


def collect_node_ids(repo_name: str, repo: Path, *, with_skip_counts: bool = False) -> dict:
    """Run collect-only and return node IDs; optionally execution-time
    skipped/xfailed counts (BASE-03 real detection)."""
    command = [sys.executable, *COLLECT_COMMANDS[repo_name]]
    proc = subprocess.run(
        command, cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"{repo_name} collect-only failed (exit {proc.returncode}): "
            f"{proc.stderr.strip()[-800:]}"
        )
    entry: dict = {"node_ids": _parse_collect_output(proc.stdout), "skipped": 0, "xfailed": 0}
    if with_skip_counts:
        counts = _run_summary_counts(repo_name, repo)
        entry["skipped"] = counts.get("skipped", 0)
        entry["xfailed"] = counts.get("xfailed", 0)
    return entry


def capture(
    *,
    baseline_path: Path = DEFAULT_BASELINE,
    repos: dict[str, Path] | None = None,
    with_skip_counts: bool = False,
) -> dict:
    repos = repos or REPOS
    config_hashes: dict[str, str] = {}
    for repo_name, files in CONFIG_FILES.items():
        for relative in files:
            path = repos[repo_name] / relative
            if not path.is_file():
                raise FileNotFoundError(f"config missing: {path}")
            config_hashes[str(path)] = sha256_file(path)
    plan_hash = sha256_file(PLAN_DIR / "task_plan.md")
    collection = {}
    for repo_name, repo in repos.items():
        collection[repo_name] = collect_node_ids(
            repo_name, repo, with_skip_counts=with_skip_counts
        )
    repo_states = {
        name: collect_repo_state(name, repo) for name, repo in repos.items()
    }
    return capture_manifest(repo_states, collection, config_hashes, plan_hash, USER_DIRTY)


# ---- gate verifiers (pure functions, unit-tested) ----

def verify_head(baseline: dict, current_heads: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for repo_name, repo_info in (baseline.get("repos") or {}).items():
        expected = repo_info.get("head")
        actual = current_heads.get(repo_name)
        if actual is None:
            problems.append(f"{repo_name}: current HEAD missing")
        elif actual != expected:
            problems.append(
                f"{repo_name}: HEAD {actual} != baseline {expected} (BASE-01)"
            )
    return problems


def verify_dirty_allowlist(baseline: dict, allowed_files: list[str]) -> list[str]:
    problems: list[str] = []
    user_dirty = set(baseline.get("user_dirty") or [])
    for allowed in allowed_files or []:
        normalized = allowed.replace("\\", "/")
        if any(
            normalized == dirty or normalized.startswith(dirty.rstrip("/") + "/")
            for dirty in user_dirty
        ):
            problems.append(
                f"user-dirty path {allowed!r} is in the implementation "
                "allowlist (BASE-02)"
            )
    return problems


def verify_collection(baseline: dict, current: dict) -> list[str]:
    problems: list[str] = []
    for repo_name, baseline_entry in (baseline.get("collection") or {}).items():
        expected = set(baseline_entry.get("node_ids") or [])
        current_entry = current.get(repo_name) or {}
        actual = set(current_entry.get("node_ids") or [])
        for node in sorted(expected - actual):
            problems.append(f"{repo_name}: collected node disappeared: {node} (BASE-03)")
        added = sorted(actual - expected)
        if added:
            problems.append(
                f"{repo_name}: {len(added)} node(s) collected now but absent from "
                f"baseline (baseline drift or legit add without plan revision): "
                f"{added[:3]} (BASE-03)"
            )
        # execution-time skip/xfail counts must not grow without explanation
        for marker in ("skipped", "xfailed"):
            expected_count = baseline_entry.get(marker) or 0
            actual_count = (current_entry or {}).get(marker) or 0
            if actual_count > expected_count:
                problems.append(
                    f"{repo_name}: {marker} count {actual_count} > baseline "
                    f"{expected_count} (BASE-03)"
                )
    return problems


def verify_plan_hash(plan_path: Path, expected: str) -> list[str]:
    actual = sha256_file(plan_path)
    if actual != expected:
        return [
            f"plan_hash {actual[:12]} != baseline {expected[:12]} "
            "(BASE-04: plan changed, receipts must re-validate)"
        ]
    return []


def verify_config_hashes(expected: dict, actual: dict) -> list[str]:
    problems: list[str] = []
    for path, expected_hash in (expected or {}).items():
        actual_hash = actual.get(path)
        if actual_hash != expected_hash:
            problems.append(
                f"config {Path(path).name}: hash {str(actual_hash)[:12]} != "
                f"baseline {expected_hash[:12]}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="WU-101 baseline capture/gate")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument(
        "--allowed-files", type=Path, default=None,
        help="comma/newline-separated implementation allowlist file; every entry "
             "is checked against the user-dirty paths (BASE-02)",
    )
    parser.add_argument(
        "--with-skip-counts", action="store_true",
        help="also execute each suite once to capture real skipped/xfailed counts "
             "(BASE-03; slow, ~5-8 min across repos)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true", help="write baseline JSON")
    group.add_argument("--check", action="store_true", help="verify state vs baseline")
    args = parser.parse_args()

    if args.capture:
        manifest = capture(baseline_path=args.baseline, with_skip_counts=args.with_skip_counts)
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"baseline written: {args.baseline}")
        print(f"heads: " + ", ".join(
            f"{name}={info['head'][:7]}" for name, info in manifest["repos"].items()
        ))
        print(f"collection: " + ", ".join(
            f"{name}={len(entry['node_ids'])}" for name, entry in manifest["collection"].items()
        ))
        if args.with_skip_counts:
            print(f"skip counts: " + ", ".join(
                f"{name}=skipped{entry.get('skipped', 0)}/xfailed{entry.get('xfailed', 0)}"
                for name, entry in manifest["collection"].items()
            ))
        return 0

    if not args.baseline.is_file():
        print(f"missing baseline: {args.baseline} (run --capture first)")
        return 1
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    problems: list[str] = []
    current_heads = {}
    for repo_name, repo in REPOS.items():
        current_heads[repo_name] = _git(repo, "rev-parse", "HEAD")
    problems.extend(verify_head(baseline, current_heads))
    problems.extend(verify_plan_hash(PLAN_DIR / "task_plan.md", baseline.get("plan_hash", "")))
    current_configs = {}
    for repo_name, files in CONFIG_FILES.items():
        for relative in files:
            path = REPOS[repo_name] / relative
            if path.is_file():
                current_configs[str(path)] = sha256_file(path)
    problems.extend(verify_config_hashes(baseline.get("config_hashes") or {}, current_configs))
    if args.allowed_files is not None and args.allowed_files.is_file():
        allowed = [
            line.strip() for line in
            args.allowed_files.read_text(encoding="utf-8").replace(",", "\n").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        problems.extend(verify_dirty_allowlist(baseline, allowed))
    current_collection = {}
    for repo_name, repo in REPOS.items():
        current_collection[repo_name] = collect_node_ids(
            repo_name, repo, with_skip_counts=args.with_skip_counts
        )
    problems.extend(verify_collection(baseline, current_collection))
    for problem in problems:
        print(f"BASELINE-GATE: {problem}")
    if not problems:
        print("OK: baseline intact (heads/config/plan/collection)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
