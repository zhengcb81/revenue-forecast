#!/usr/bin/env python3
"""I-16-A 组合绑定器（只读产品三仓；唯一写入 = 本 attempt 目录）。

产出：
  combo_manifest.json  —— 拟部署完整组合绑定（三仓 commit + dirty 内容 hash、安装副本 hash、
                          解释器/依赖、config/policy/flags/schema 版本与真实加载模块）
  snapshot/…           —— dirty/untracked 层字节快照（可逆准备）
  snapshot_manifest.json
用法：
  python -X utf8 -B _bind_combo.py --probe probe_bind.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
DAYU = Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent")
SP = Path(r"C:\Miniconda\Lib\site-packages")
VENV_SP = DAYU / ".venv" / "Lib" / "site-packages"
VENV_PY = DAYU / ".venv" / "Scripts" / "python.exe"

REPOS = {"RF": RF, "CW": CW, "DAYU": DAYU}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> tuple[int, str, str]:
    r = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, cwd=str(repo)
    )
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    return r.returncode, out, err


def git_lines(repo: Path, *args: str) -> list[str]:
    rc, out, _ = git(repo, *args)
    if rc != 0:
        return []
    return [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("warning:")]


def rel_repo_file(repo: Path, rel: str) -> Path:
    return repo / Path(rel.replace("/", "/"))


def bind_repo(name: str, repo: Path) -> dict:
    rc_head, head, _ = git(repo, "rev-parse", "HEAD")
    rc_meta, meta, _ = git(repo, "log", "-1", "--format=%H|%cI|%s")
    diff = git_lines(repo, "-c", "core.quotepath=false", "diff", "HEAD", "--name-only")
    staged = git_lines(repo, "-c", "core.quotepath=false", "diff", "--cached", "--name-only")
    untracked = git_lines(
        repo, "-c", "core.quotepath=false", "ls-files", "--others", "--exclude-standard"
    )
    diff_np = [p for p in diff if not p.startswith(".planning")]
    untr_np = [p for p in untracked if not p.startswith(".planning")]

    dirty = []
    for rel in diff_np:
        p = rel_repo_file(repo, rel)
        if p.is_file():
            dirty.append(
                {"path": rel, "sha256": sha256(p), "bytes": p.stat().st_size, "state": "modified"}
            )
        else:
            dirty.append({"path": rel, "sha256": None, "bytes": None, "state": "deleted_or_dir"})
    for rel in untr_np:
        p = rel_repo_file(repo, rel)
        if p.is_file():
            dirty.append(
                {"path": rel, "sha256": sha256(p), "bytes": p.stat().st_size, "state": "untracked"}
            )
    digest = hashlib.sha256(
        "\n".join(
            f"{d['state']}|{d['path']}|{d['sha256']}" for d in sorted(dirty, key=lambda x: x["path"])
        ).encode("utf-8")
    ).hexdigest()
    parts = meta.strip().split("|", 2) if rc_meta == 0 else ["", "", ""]
    return {
        "path": str(repo),
        "head": head.strip() if rc_head == 0 else None,
        "head_meta": {
            "hash": parts[0],
            "date": parts[1] if len(parts) > 1 else "",
            "subject": parts[2] if len(parts) > 2 else "",
        },
        "git_diff_total": len(diff),
        "git_diff_non_planning": len(diff_np),
        "staged_non_planning": [p for p in staged if not p.startswith(".planning")],
        "untracked_non_planning": untr_np,
        "dirty_content": dirty,
        "dirty_content_digest_sha256": digest,
        "dirty_content_count": len(dirty),
        "git_status_run": False,
        "git_writes": 0,
    }


def bind_install() -> dict:
    def info(dist_dir: Path) -> dict:
        d: dict = {"dist_info": str(dist_dir), "files": {}}
        for fname in ("direct_url.json", "METADATA", "RECORD", "INSTALLER", "WHEEL", "top_level.txt"):
            f = dist_dir / fname
            if f.exists():
                d["files"][fname] = {"path": str(f), "sha256": sha256(f), "bytes": f.stat().st_size}
        du = dist_dir / "direct_url.json"
        if du.exists():
            payload = json.loads(du.read_text(encoding="utf-8"))
            d["editable"] = bool(payload.get("dir_info", {}).get("editable"))
            d["url"] = payload.get("url")
        return d

    out: dict = {"company_wiki": info(SP / "company_wiki-0.1.0.dist-info"),
                 "dayu_agent_miniconda": info(SP / "dayu_agent-0.1.4.dist-info"),
                 "dayu_agent_venv": info(VENV_SP / "dayu_agent-0.1.4.dist-info")}
    for key, pth in (
        ("pth_company_wiki", SP / "__editable__.company_wiki-0.1.0.pth"),
        ("pth_dayu_miniconda", SP / "__editable__.dayu_agent-0.1.4.pth"),
        ("finder_dayu_miniconda", SP / "__editable___dayu_agent_0_1_4_finder.py"),
        ("pth_dayu_venv", VENV_SP / "__editable__.dayu_agent-0.1.4.pth"),
        ("finder_dayu_venv", VENV_SP / "__editable___dayu_agent_0_1_4_finder.py"),
    ):
        if pth.exists():
            txt = pth.read_text(encoding="utf-8", errors="replace")
            out[key] = {
                "path": str(pth),
                "sha256": sha256(pth),
                "bytes": pth.stat().st_size,
                "content": txt.strip()[:400],
            }
    return out


def bind_config_values() -> dict:
    import yaml  # pyyaml（已装）

    rf_cw = json.loads((RF / "config" / "company_wiki.json").read_text(encoding="utf-8"))
    rf_ff = json.loads((RF / "config" / "filing_fetch.json").read_text(encoding="utf-8"))
    cw_sc = yaml.safe_load((CW / "config" / "source_catalog.yaml").read_text(encoding="utf-8"))
    cw_wk = yaml.safe_load((CW / "config" / "source_catalog_worker.yaml").read_text(encoding="utf-8"))
    consts = (RF / "scripts" / "contracts" / "constants.py").read_text(encoding="utf-8")
    pol = (RF / "scripts" / "confidence_policy.py").read_text(encoding="utf-8")
    mig = (CW / "src" / "company_wiki" / "automation" / "migrations.py").read_text(encoding="utf-8")
    comp = (
        CW / "src" / "company_wiki" / "source_contract" / "compatibility.py"
    ).read_text(encoding="utf-8")

    def grab(pattern: str, text: str, flags: int = 0):
        m = re.search(pattern, text, flags)
        return m.group(1) if m else None

    return {
        "RF_config_company_wiki_schema_version": rf_cw.get("schema_version"),
        "RF_config_filing_fetch_schema_version": rf_ff.get("schema_version"),
        "CW_source_catalog_schema_version": str(cw_sc.get("schema_version")),
        "CW_source_catalog_worker_schema_version": str(cw_wk.get("schema_version")),
        "CW_source_catalog_catalog_dir": cw_sc.get("catalog_dir"),
        "CW_source_catalog_roots": [
            {"root_id": r.get("root_id"), "kind": r.get("kind"), "path": r.get("path"),
             "read_only": r.get("read_only", False)}
            for r in (cw_sc.get("roots") or [])
        ],
        "FORECAST_SCHEMA_VERSION": grab(r'FORECAST_SCHEMA_VERSION\s*=\s*"([^"]+)"', consts),
        "OPT_IN_SCHEMA_VERSION": grab(r'OPT_IN_SCHEMA_VERSION\s*=\s*"([^"]+)"', consts),
        "CONFIDENCE_POLICY_VERSION": grab(r'CONFIDENCE_POLICY_VERSION\s*=\s*"([^"]+)"', pol),
        "CW_AUTOMATION_SCHEMA_VERSION": int(
            grab(r"^SCHEMA_VERSION\s*=\s*(\d+)", mig, re.M) or -1
        ),
        "SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION": grab(
            r'SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION\s*=\s*"([^"]+)"', comp
        ),
    }


def bind_worker_runtime() -> dict:
    p = CW / "config" / ".source_catalog" / "worker_runtime.json"
    rt = json.loads(p.read_text(encoding="utf-8"))
    files = []
    for item in rt.get("loaded_code_files", []):
        rel = item["path"]
        fp = CW / rel.replace("/", "/")
        cur = sha256(fp) if fp.is_file() else None
        entry = {"path": rel, "recorded_sha256": item["sha256"], "current_sha256": cur,
                 "matches_current": cur == item["sha256"]}
        if not entry["matches_current"]:
            # 在该路径的全部历史修订中检索（只读）
            rc, out, _ = git(CW, "log", "--format=%H", "-n", "60", "--", rel)
            revs = [x for x in out.splitlines() if x.strip()] if rc == 0 else []
            hit = None
            for rev in revs:
                r2 = subprocess.run(
                    ["git", "-C", str(CW), "show", f"{rev}:{rel}"], capture_output=True
                )
                if r2.stdout and hashlib.sha256(r2.stdout).hexdigest() == item["sha256"]:
                    hit = rev
                    break
            entry["history_scan"] = {"revs_scanned": len(revs), "found_rev": hit}
        files.append(entry)
    heartbeat = rt.get("heartbeat_at")
    return {
        "path": str(p),
        "sha256": sha256(p),
        "executable": rt.get("executable"),
        "worker_status": rt.get("worker_status"),
        "pid": rt.get("pid"),
        "heartbeat_at_epoch": heartbeat,
        "heartbeat_utc": datetime.fromtimestamp(heartbeat, timezone.utc).isoformat()
        if heartbeat
        else None,
        "code_version": rt.get("code_version"),
        "loaded_code_fingerprint": rt.get("loaded_code_fingerprint"),
        "loaded_code_files": files,
        "worker_control_json_exists": (CW / "config" / ".source_catalog" / "worker_control.json").exists(),
        "worker_control_root_exists": (CW / ".source_catalog" / "worker_control.json").exists(),
    }


def bind_data_layer(hash_catalog: bool) -> dict:
    cat = CW / ".source_catalog" / "catalog.sqlite3"
    small = CW / "config" / ".source_catalog" / "catalog.sqlite3"
    out: dict = {"catalog": None, "catalog_small": None, "registry_behavior": {}, "raw": {}}
    for key, p in (("catalog", cat), ("catalog_small", small)):
        if not p.exists():
            out[key] = {"exists": False, "path": str(p)}
            continue
        st = p.stat()
        rec: dict = {"exists": True, "path": str(p), "bytes": st.st_size,
                     "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}
        if hash_catalog and st.st_size <= 8 * 1024 * 1024:
            rec["sha256"] = sha256(p)
        elif hash_catalog:
            t0 = time.time()
            rec["sha256"] = sha256(p)
            rec["sha256_elapsed_seconds"] = round(time.time() - t0, 2)
        # 只读打开，读 user_version
        try:
            import sqlite3

            uri = "file:" + str(p).replace("\\", "/") + "?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            rec["user_version"] = conn.execute("PRAGMA user_version").fetchone()[0]
            rec["table_count"] = len(
                conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            )
            conn.close()
        except Exception as exc:  # noqa: BLE001
            rec["sqlite_read_error"] = f"{type(exc).__name__}: {exc}"
        out[key] = rec
    out["raw"] = {
        "config_file": str(CW / "config" / "source_catalog.yaml"),
        "config_sha256": sha256(CW / "config" / "source_catalog.yaml"),
        "raw_roots": [
            r for r in (bind_config_values_cache()["CW_source_catalog_roots"] or [])
        ],
        "note": "raw 层由 acquisition 写入；本卡零写；部署步骤不触及 raw 字节",
    }
    return out


_CONFIG_VALUES: dict | None = None


def bind_config_values_cache() -> dict:
    global _CONFIG_VALUES
    if _CONFIG_VALUES is None:
        _CONFIG_VALUES = bind_config_values()
    return _CONFIG_VALUES


ARTIFACT_KEYS: dict[str, Path] = {
    "cfg_rf_company_wiki_json": RF / "config" / "company_wiki.json",
    "cfg_rf_filing_fetch_json": RF / "config" / "filing_fetch.json",
    "cfg_cw_source_catalog_yaml": CW / "config" / "source_catalog.yaml",
    "cfg_cw_source_catalog_worker_yaml": CW / "config" / "source_catalog_worker.yaml",
    "inst_cw_pth": SP / "__editable__.company_wiki-0.1.0.pth",
    "inst_cw_direct_url": SP / "company_wiki-0.1.0.dist-info" / "direct_url.json",
    "inst_cw_metadata": SP / "company_wiki-0.1.0.dist-info" / "METADATA",
    "inst_cw_record": SP / "company_wiki-0.1.0.dist-info" / "RECORD",
    "inst_dayu_pth": SP / "__editable__.dayu_agent-0.1.4.pth",
    "inst_dayu_finder": SP / "__editable___dayu_agent_0_1_4_finder.py",
    "inst_dayu_direct_url": SP / "dayu_agent-0.1.4.dist-info" / "direct_url.json",
    "inst_dayu_metadata": SP / "dayu_agent-0.1.4.dist-info" / "METADATA",
    "inst_dayu_record": SP / "dayu_agent-0.1.4.dist-info" / "RECORD",
    "inst_dayu_venv_pth": VENV_SP / "__editable__.dayu_agent-0.1.4.pth",
    "inst_dayu_venv_finder": VENV_SP / "__editable___dayu_agent_0_1_4_finder.py",
    "inst_dayu_venv_direct_url": VENV_SP / "dayu_agent-0.1.4.dist-info" / "direct_url.json",
    "mod_rf_forecast_constants": RF / "scripts" / "contracts" / "constants.py",
    "mod_rf_confidence_policy": RF / "scripts" / "confidence_policy.py",
    "mod_cw_migrations": CW / "src" / "company_wiki" / "automation" / "migrations.py",
    "mod_cw_compatibility": CW / "src" / "company_wiki" / "source_contract" / "compatibility.py",
    "mod_cw_evidence_query": CW / "src" / "company_wiki" / "source_catalog" / "evidence_query.py",
    "worker_runtime_json": CW / "config" / ".source_catalog" / "worker_runtime.json",
}
for _i, _p in enumerate(sorted(
    [CW / "src" / "company_wiki" / "source_catalog" / f
     for f in ("__init__.py", "artifact_dag.py", "dayu_cli_adapter.py", "error_taxonomy.py")]
    + [CW / "tests" / "contract" / "test_source_catalog_evidence_query.py",
       CW / "tests" / "unit" / "test_error_taxonomy.py",
       CW / "CLAUDE.md", CW / "README.md",
       DAYU / "dayu" / "fins" / "downloaders" / "sec_downloader.py"]
)):
    ARTIFACT_KEYS[f"dirty_{_i:02d}_{_p.name}"] = _p


def bind_artifacts() -> list[dict]:
    out = []
    for i, (key, p) in enumerate(sorted(ARTIFACT_KEYS.items())):
        if not p.exists():
            out.append({"key": key, "live_path": str(p), "exists": False})
            continue
        out.append(
            {
                "key": key,
                "live_path": str(p),
                "iso_relpath": f"artifacts/{i:03d}_{key}{p.suffix}",
                "sha256": sha256(p),
                "bytes": p.stat().st_size,
                "exists": True,
            }
        )
    return out


def make_snapshot(dirty_entries: dict[str, list[dict]]) -> dict:
    snap = HERE / "snapshot"
    rows = []
    for repo_name, entries in dirty_entries.items():
        for e in entries:
            if not e.get("sha256"):
                continue
            src = Path(e["path"])
            if not src.is_absolute():
                src = REPOS[repo_name] / Path(e["path"].replace("/", "/"))
            dst = snap / repo_name / e["path"].replace("/", "__")
            dst.parent.mkdir(parents=True, exist_ok=True)
            data = src.read_bytes()
            dst.write_bytes(data)
            got = hashlib.sha256(data).hexdigest()
            rows.append(
                {
                    "repo": repo_name,
                    "source_path": str(src),
                    "snapshot_path": str(dst.relative_to(HERE)).replace("\\", "/"),
                    "bytes": len(data),
                    "source_sha256": got,
                    "snapshot_sha256": got,
                    "match": got == e["sha256"],
                    "state": e.get("state"),
                }
            )
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(rows),
        "all_match": all(r["match"] for r in rows),
        "files": rows,
        "reversible": True,
        "reversal": "删除 snapshot/ 即回到未准备状态；本卡未改动任何产品字节",
    }
    (HERE / "snapshot_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--hash-catalog", action="store_true")
    args = ap.parse_args()

    probe = json.loads(Path(args.probe).read_text(encoding="utf-8"))
    repos = {name: bind_repo(name, path) for name, path in REPOS.items()}
    install = bind_install()
    config_values = bind_config_values()
    worker = bind_worker_runtime()
    data_layer = bind_data_layer(args.hash_catalog)
    artifacts = bind_artifacts()
    snapshot = make_snapshot(
        {name: [d for d in repos[name]["dirty_content"]] for name in REPOS}
    )

    manifest = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "bound_at_utc": datetime.now(timezone.utc).isoformat(),
        "write_surface": str(HERE),
        "product_repos_read_only": True,
        "git_status_run": False,
        "git_writes": 0,
        "network_used": False,
        "repos": repos,
        "install": install,
        "interpreter": probe["interpreter"],
        "packages": probe["packages"],
        "constants_from_probe": probe["constants"],
        "modules_from_probe": {
            k: {"origin": v.get("origin"), "sha256": v.get("sha256"),
                "load_method": v.get("load_method"), "import_status": v.get("import_status")}
            for k, v in probe.get("modules", {}).items()
        },
        "config_policy_flags_schema": config_values,
        "config_policy_flags_schema_files": [
            {"key": k, "path": str(v), "sha256": sha256(v)}
            for k, v in {
                "RF_company_wiki": RF / "config" / "company_wiki.json",
                "RF_filing_fetch": RF / "config" / "filing_fetch.json",
                "CW_source_catalog": CW / "config" / "source_catalog.yaml",
                "CW_source_catalog_worker": CW / "config" / "source_catalog_worker.yaml",
                "CW_config_yaml": CW / "config.yaml",
            }.items()
            if v.exists()
        ],
        "worker_runtime": worker,
        "data_layer": data_layer,
        "artifacts": artifacts,
        "snapshot": {
            "file_count": snapshot["file_count"],
            "all_match": snapshot["all_match"],
            "manifest": "snapshot_manifest.json",
        },
        "adapter_interpreter": {
            "path": str(VENV_PY),
            "exists": VENV_PY.exists(),
            "used_by": "RF/config/company_wiki.json hk/us adapters -> python -m dayu.cli",
        },
        "expected_modules": probe.get("modules", {}),
    }
    (HERE / "combo_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(
        "manifest_written combo_manifest.json repos="
        + ",".join(
            f"{k}:{(v['head'] or '?')[:12]}/dirty={v['dirty_content_count']}" for k, v in repos.items()
        )
        + f" artifacts={len(artifacts)} snapshot={snapshot['file_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
