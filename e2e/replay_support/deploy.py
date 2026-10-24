"""Frozen-Git deployment of the three production repos (W14 E02).

The chain must execute code from frozen Git objects of the caller-named
repos/commits, deployed into an owned scratch directory — never from the
changing workspaces and never from an editable install.  Every failure here
is a named ``environment_unavailable`` condition with the concrete missing
object; it is never a scenario pass or skip.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class DeployError(RuntimeError):
    """A concrete environment gap; message starts with environment_unavailable."""

    def __init__(self, detail: str):
        super().__init__(f"environment_unavailable: {detail}")


@dataclass(frozen=True)
class RepoSpec:
    role: str          # "rf" | "cwp" | "ff"
    repo: Path
    commit: str

    def __post_init__(self) -> None:
        if not isinstance(self.repo, Path):
            raise DeployError(f"{self.role}: repo path must be a Path")
        if not isinstance(self.commit, str) or not self.commit.strip():
            raise DeployError(f"{self.role}: commit must be non-empty text")


def _git(repo: Path, *args: str, timeout: float = 120.0) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False, env=env,
    )


def resolve_commit(repo: Path, commit: str) -> str:
    """Full object name for a commit that must already exist."""
    if not repo.is_dir():
        raise DeployError(f"repository absent: {repo}")
    proc = _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if proc.returncode != 0:
        raise DeployError(
            f"commit object {commit!r} not found in {repo}: "
            f"{(proc.stderr or proc.stdout).strip()[:200]}")
    return proc.stdout.strip()


def repo_head(repo: Path) -> str:
    proc = _git(repo, "rev-parse", "HEAD")
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def export_tree(
    repo: Path, commit: str, paths: tuple[str, ...], dest: Path,
) -> dict:
    """``git archive`` the named tracked paths at ``commit`` into ``dest``.

    Returns {files, bytes, sha256_by_relpath} for the deployed tree.  Only
    Git objects are read; the repo workspace is never touched.
    """
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
        tar_path = Path(tmp.name)
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "archive", "--format=tar", commit, "--", *paths],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300, check=False)
        if proc.returncode != 0 or not proc.stdout:
            raise DeployError(
                f"git archive failed for {commit} paths {list(paths)} in {repo}: "
                f"{proc.stderr.decode('utf-8', 'replace').strip()[:300]}")
        tar_path.write_bytes(proc.stdout)
        with tarfile.open(tar_path, "r:") as archive:
            try:
                archive.extractall(dest, filter="data")
            except TypeError:  # Python < 3.12 without the filter argument
                archive.extractall(dest)
    finally:
        tar_path.unlink(missing_ok=True)
    manifest: dict[str, str] = {}
    total = 0
    for p in sorted(dest.rglob("*")):
        if p.is_file():
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            manifest[p.relative_to(dest).as_posix()] = digest
            total += p.stat().st_size
    return {"files": len(manifest), "bytes": total, "sha256_by_relpath": manifest}


def deployment_plan(role: str) -> tuple[str, ...]:
    """Tracked paths each role needs to run the offline chain (no secrets)."""
    if role == "rf":
        return ("scripts",)
    if role == "ff":
        return ("scripts", "tests/e2e_support")
    if role == "cwp":
        return ("src/company_wiki", "config/models.yaml", "config/resource_budget.yaml")
    raise DeployError(f"unknown deployment role {role!r}")


def provenance(spec: RepoSpec, dest: Path, export_info: dict) -> dict:
    return {
        "role": spec.role,
        "repo": str(spec.repo),
        "requested_commit": spec.commit,
        "resolved_commit": resolve_commit(spec.repo, spec.commit),
        "repo_head_at_run": repo_head(spec.repo),
        "deployed_root": str(dest),
        "deployed_files": export_info["files"],
        "deployed_bytes": export_info["bytes"],
        "tree_sha256": hashlib.sha256(json.dumps(
            export_info["sha256_by_relpath"], sort_keys=True).encode()).hexdigest(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


class FrozenDeployment:
    """Three-repo deployment in one scratch root, with provenance records."""

    def __init__(self, scratch: Path, rf: RepoSpec, cwp: RepoSpec, ff: RepoSpec):
        self.scratch = scratch
        self.specs = {"rf": rf, "cwp": cwp, "ff": ff}
        self.provenance: dict[str, dict] = {}
        self.roots: dict[str, Path] = {}

    def build(self) -> "FrozenDeployment":
        self.scratch.mkdir(parents=True, exist_ok=True)
        for role, spec in self.specs.items():
            commit = resolve_commit(spec.repo, spec.commit)
            dest = self.scratch / role
            info = export_tree(spec.repo, commit, deployment_plan(role), dest)
            self.roots[role] = dest
            self.provenance[role] = provenance(spec, dest, info)
        return self

    @property
    def rf_scripts(self) -> Path:
        return self.roots["rf"] / "scripts"

    @property
    def cwp_src(self) -> Path:
        return self.roots["cwp"] / "src"

    @property
    def cwp_config(self) -> Path:
        return self.roots["cwp"] / "config"

    @property
    def ff_scripts(self) -> Path:
        return self.roots["ff"] / "scripts"

    @property
    def ff_isolated_wiki(self) -> Path:
        return self.roots["ff"] / "tests" / "e2e_support" / "isolated_wiki.py"
