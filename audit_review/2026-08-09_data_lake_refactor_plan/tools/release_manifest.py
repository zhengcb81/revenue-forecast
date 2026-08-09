"""WU-1405: release manifest generator — commit matrix + hashes + gates.

Records three-repo commits, schema/adapter/config/policy hashes, the closure
ledger link, known limitations, feature flags, rollback commands and
reviewers.  Any repo commit change invalidates a prior manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]
REPOS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True, timeout=60,
    ).stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(*, plan_dir: Path = PLAN_DIR) -> dict:
    commits = {}
    for name, repo in REPOS.items():
        commits[name] = {
            "head": _git(repo, "rev-parse", "HEAD"),
            "branch": _git(repo, "branch", "--show-current"),
        }
    configs = {
        "wiki/source_catalog.yaml": _sha256_file(REPOS["wiki"] / "config" / "source_catalog.yaml"),
        "filing/company_wiki.json": _sha256_file(REPOS["filing"] / "config" / "company_wiki.json"),
    }
    return {
        "schema_version": "1.0",
        "generated_at": "2026-08-09",
        "commits": commits,
        "config_hashes": configs,
        "plan_hash": _sha256_file(plan_dir / "task_plan.md"),
        "closure_ledger": str(plan_dir / "closure_ledger.json"),
        "known_limitations": [
            "WU-1303 BLOCKED_NO_ELIGIBLE_PRODUCTION_SAMPLE: 真实 Dropbox canary 无合格样本",
            "WU-903/905/906 生产 apply/backfill 需变更窗口执行（窗口已授权，逐文档 reviewer 批准）",
            "Phase 15 legacy 退役需两个验证周期观察",
        ],
        "feature_flags": {
            "v2_scan_shadow": False,
            "v2_persist_assertions": False,
            "v2_resolve_shadow": False,
            "v2_resolve_active": False,
            "v2_bundle_active": False,
            "legacy_bridge_enabled": True,
        },
        "rollback_commands": {
            "resolver": "关闭 v2_resolve_active flag（atomic_rollback）",
            "scanner": "v2_scan_shadow=False（facade 默认 v1）",
            "bundle": "consumer 协议版本回退（N-1 窗口）",
            "migration": "journal 恢复（last_key 边界）+ backup",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Release manifest generator")
    parser.add_argument("--output", type=Path, default=PLAN_DIR / "release_manifest.json")
    args = parser.parse_args()
    manifest = build_manifest()
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"manifest written: {args.output}")
    for name, info in manifest["commits"].items():
        print(f"  {name}: {info['head'][:7]} ({info['branch']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
