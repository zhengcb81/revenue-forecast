"""Emit provenance.json for OPEN5-PEND5B-OCR-CAPABILITY (a20260924-01).

Sources: _dl/build_receipts.json, _work/*.json probe outputs, on-disk hashes,
measured git audit numbers. All JSON UTF-8 (no BOM) + LF, reparsed after write.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
DL = os.path.join(ATTEMPT, "_dl")
WORK = os.path.join(ATTEMPT, "_work")


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmeta(p: str) -> dict:
    return {"path": os.path.relpath(p, ATTEMPT).replace("\\", "/"),
            "bytes": os.path.getsize(p), "sha256": sha256_file(p)}


def load(p: str):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def git_audit() -> dict:
    import subprocess

    def git(*args, cwd=None):
        r = subprocess.run(["git", "-c", "core.quotepath=false", *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           cwd=cwd or ATTEMPT)
        if r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed rc={r.returncode}: {r.stderr[:300]}")
        return [ln for ln in (r.stdout or "").splitlines() if ln]

    def stripq(s: str) -> str:
        s = s.strip()
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            s = s[1:-1]
        return s

    # git diff paths are repo-root-relative already; ls-files needs --full-name
    # AND must run from the repo root (cwd scopes --others to the subtree).
    diff = [stripq(x) for x in git("diff", "HEAD", "--name-only")]
    nonplan = [x for x in diff if not x.startswith(".planning/")]
    toplevel = git("rev-parse", "--show-toplevel")[0]
    un = [stripq(x) for x in git("ls-files", "--others", "--exclude-standard",
                                  "--full-name", cwd=toplevel)]
    unnplan = [x for x in un if not x.startswith(".planning/")]
    return {
        "measured_utc": utc_now(),
        "workspace": "C:/Users/郑曾波/Projects/revenue-forecast",
        "git_diff_HEAD_total": len(diff),
        "git_diff_non_planning": len(nonplan),
        "git_diff_non_planning_paths": nonplan[:20],
        "git_untracked_non_planning": len(unnplan),
        "git_untracked_non_planning_prefixes": sorted(
            {x.split("/")[0] for x in unnplan}
        ),
        "git_untracked_non_planning_by_this_card": len(
            [x for x in unnplan if "OPEN5-PEND5B" in x]
        ),
        "git_writes_performed_by_this_card": 0,
        "note": "read-only git commands only (diff HEAD / ls-files --others); no add/commit/checkout/stash/reset",
    }


def main() -> int:
    receipts = load(os.path.join(DL, "build_receipts.json"))
    agg = load(os.path.join(WORK, "hk_probe_aggregate.json"))
    install_report = load(os.path.join(DL, "install_report.json"))
    verify = load(os.path.join(DL, "verify.json"))

    entries = []
    add = entries.append

    # ---- authorization ----
    add({
        "id": "auth-01", "kind": "authorization",
        "source": ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md",
        "section": "§二十六（2026-09-24 深夜，原话逐字）第 2 行",
        "quote": "| **2** | **`PEND-5b`** 装 OCR 引擎（`OPEN-5` 恢复路径 S1 的另一半） | **「要」**（澄清答确认） | 派 `fc80192e` = `OPEN5-PEND5B-OCR-CAPABILITY`。硬边界：**安装只许落在本卡隔离 venv**、**默认禁止系统级安装**；若必须系统二进制（tesseract 类）⇒ **不装、报 `BLOCKED-NEEDS-SYSTEM-BINARY`** 交 owner 再裁；**单件下载 > 200 MB 须先报体积**；**OCR 产物必标 `ocr_reconstruction`、永不冒充 origin 文本**；**先在 CN-ZIJIN 可读样本自检通过才许打 HK 探针**（依 `OPEN5-ENVOWNER` 的 S2 次序） |",
        "chain": "owner 首答「1，授权，2，要」→ 父一次澄清提问 → owner 答「两项都要（PEND-5b 装 + E1 交会计面）」⇒ 本项 = PEND-5b 装 OCR 引擎授权",
    })
    add({
        "id": "auth-02", "kind": "authorization_context",
        "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md",
        "quotes": [
            "RC-1（文件层，决定性）：正文中文以 Type0 / Identity-H 的子集 CJK 字体排版…字体字典无 `/ToUnicode`，且内嵌子集 TrueType 无 `cmap` 表（探针 D/F）⇒ 文档内部根本不存在码→Unicode 映射。",
            "「换工具 / 装个 PDF 库」不是恢复路径（探针 C/E 已证 5 个库同结果）",
            "S2：先在已知可读样本（CN-ZIJIN-AR2025）上验证该路径能读出锚词，再对 HK 样本跑同一探针",
        ],
    })

    # ---- read-only inputs ----
    add({
        "id": "input-01", "kind": "local_file_read_only",
        "path": agg["hk_probe"]["file"],
        "role": "HK-XIAOMI-AR2025 target (read-only)",
        "bytes": agg["hk_probe"]["bytes"], "sha256": agg["hk_probe"]["sha256"],
        "page_count": agg["hk_probe"]["page_count"],
        "writes_to_this_file": 0,
    })
    add({
        "id": "input-02", "kind": "local_file_read_only",
        "path": agg["self_check_on_readable_sample"]["file"],
        "role": "CN-ZIJIN-AR2025 readable sample for S2 gate (read-only)",
        "bytes": agg["self_check_on_readable_sample"]["bytes"],
        "sha256": agg["self_check_on_readable_sample"]["sha256"],
        "writes_to_this_file": 0,
    })

    # ---- environment probes ----
    for pid, cmd, obs, note in [
        ("env-01", "python -c: tempfile.mkdtemp()/os.mkdir(mode) write test in plan dir AND platform TEMP",
         "mkdtemp: PermissionError [Errno 13]; mkdir 0o700: [Errno 13]; mkdir 0o777: OK",
         "sandbox hazard reproduced (matches card discipline #6); drove shim + workaround choices"),
        ("env-02", "urllib GET https://pypi.org/simple/six/ , /simple/rapidocr/ , /simple/onnxruntime/",
         "HTTP 200 in 0.00-0.36s", "network egress to PyPI healthy via urllib"),
        ("env-03", "Invoke-WebRequest HEAD pypi.org / files.pythonhosted.org / google.com",
         "ERR: 基础连接已经关闭: 接收时发生错误 (PS 5.1 TLS)",
         "PowerShell stack unusable for downloads; python urllib works"),
        ("env-04", "python -m pip --isolated download --no-deps six (no shim)",
         "rc=2,11.7s: Error [Errno 13] Permission denied ... pip-unpack-*\\six-1.17.0-py2.py3-none-any.whl.metadata",
         "pip network OK but dies on sandbox-broken mkdtemp dir"),
        ("env-05", "python -m pip --isolated download --no-deps rapidocr (+PYTHONPATH shim, TMP=attempt/_tmp)",
         "150s harness timeout; _dl/pip_dl2.log last line 'Getting page https://pypi.org/simple/rapidocr/'",
         "pip index fetch hung"),
        ("env-06", "python -m pip (non-isolated) download rapidocr onnxruntime pypdfium2 (+shim, TMP)",
         "killed after ~10min; _dl/pip_download.log last line 'Getting page https://pypi.org/simple/rapidocr/'",
         "same hang without --isolated"),
        ("env-07", "python -m pip --isolated download rapidocr (shim, TEMP removed = confounded control)",
         "130s harness timeout", "third bounded pip attempt; pip route abandoned after this"),
        ("env-08", "python -m venv venv (shim active) then -m ensurepip",
         "venv created (py3.13.9); first ensurepip failed without inherited PYTHONPATH; re-run with shim: pip-25.2 installed",
         "card venv has pip available but pip network path unusable"),
    ]:
        add({"id": pid, "kind": "environment_probe", "command": cmd,
             "observation": obs, "note": note})

    # ---- install / build ----
    add({
        "id": "install-01", "kind": "install_scope",
        "venv": "venv/ (this card's isolated venv, Python 3.13.9 base)",
        "site_packages": "venv/Lib/site-packages",
        "system_level_changes": {
            "PATH": 0, "windows_packages": 0, "global_site_packages_writes": 0,
            "system_python_packages_installed": 0,
        },
        "pip_used_for_install": False,
        "install_mechanism": "urllib download of PEP427 wheels + direct extraction into venv site-packages (build_env.py)",
        "shim": {
            "path": "_shim/sitecustomize.py",
            "activation": "PYTHONPATH=<shim dir> for specific process invocations only",
            "effect": "forces os.mkdir mode 0o777 so sandbox-created temp dirs stay writable",
            "system_level": False,
        },
    })
    add({
        "id": "install-02", "kind": "build_run",
        "script": fmeta(os.path.join(WORK, "build_env.py")),
        "final_rc": 0,
        "verify_all_ok": verify["all_ok"],
        "imports": {k: v["ok"] for k, v in verify["imports"].items()},
        "bundled_models": verify["rapidocr_models"],
        "bundled_model_total_bytes": verify["rapidocr_model_total_bytes"],
        "install_report": {**fmeta(os.path.join(DL, "install_report.json")),
                           "extract_failure_count": install_report.get("extract_failure_count", 0),
                           "collision_note": "collisions are re-extraction overwrites from earlier build rounds in this same attempt"},
        "receipts_file": fmeta(os.path.join(DL, "build_receipts.json")),
        "pip_download_logs": [fmeta(p) for p in
                              (os.path.join(DL, "pip_download.log"),
                               os.path.join(DL, "pip_dl2.log"), os.path.join(DL, "pip_dl3.log"))
                              if os.path.exists(p)],
        "logs": [fmeta(os.path.join(DL, "build_env.log"))],
    })

    # ---- downloads ----
    for i, d in enumerate(receipts["downloads"], 1):
        add({
            "id": f"dl-{i:02d}", "kind": "external_download",
            "url": d.get("upstream_url") or d.get("url"),
            "retrieved_utc": d.get("retrieved_utc"),
            "bytes": d.get("local_bytes"), "sha256": d.get("local_sha256"),
            "sha256_match_upstream": d.get("upstream_sha256") == d.get("local_sha256")
            if d.get("upstream_sha256") else d.get("sha256_match"),
            "purpose": d.get("purpose"), "project": d.get("project") or d.get("project"),
            "version": d.get("version"), "kind_of_artifact": d.get("kind", "wheel"),
            "index_url": d.get("index_url"),
            "over_200mb": (d.get("local_bytes") or 0) > 200 * 1024 * 1024,
        })

    # orphan mistaken pick (downloaded during a superseded build round, kept on disk)
    orphan = os.path.join(DL, "antlr4_python3_runtime-4.13.2-py3-none-any.whl")
    if os.path.exists(orphan):
        add({
            "id": "dl-orphan-01", "kind": "external_download_unused",
            "url": "https://pypi.org/simple/antlr4-python3-runtime/ (exact href recorded there; file served from files.pythonhosted.org)",
            "file": "antlr4_python3_runtime-4.13.2-py3-none-any.whl",
            "retrieved_utc": datetime.datetime.fromtimestamp(
                os.path.getmtime(orphan), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bytes": os.path.getsize(orphan), "sha256": sha256_file(orphan),
            "purpose": "superseded pick during resolver development; omegaconf pins antlr4==4.9.* so 4.13.2 was replaced by the 4.9.3 sdist; kept for audit, NOT installed (install_sdist wipes and installs 4.9.3)",
            "installed": False,
        })

    add({
        "id": "dl-index-01", "kind": "external_metadata_fetch",
        "urls": sorted({d["index_url"] for d in receipts["downloads"] if d.get("index_url")}),
        "purpose": "PEP 503 simple index pages (candidate listing, requires-python, yanked flags, sha256 fragments)",
        "transient": True, "retained_bytes": 0, "sha256": None,
        "note": "fetched in-memory by build_env.py; not retained on disk; wheel digests verified against #sha256 fragments",
    })
    add({
        "id": "dl-index-02", "kind": "external_metadata_fetch",
        "urls": ["https://pypi.org/pypi/rapidocr-onnxruntime/json",
                 "https://pypi.org/pypi/rapidocr/json"],
        "purpose": "backend selection research (requires_python / deps / wheel sizes)",
        "transient": True, "retained_bytes": 0,
    })

    # ---- render + OCR ----
    cn = agg["self_check_on_readable_sample"]
    add({
        "id": "ocr-01", "kind": "self_check_render_ocr",
        "order": "ran BEFORE any HK probe (S2 sequence)",
        "gate_passed": cn["gate_passed"],
        "file": cn["file"], "page": cn["page"], "dpi": agg["hk_probe"]["dpi"],
        "anchors": cn["anchors"], "anchor_hit_pages": cn["anchor_hit_pages"],
        "text_layer_anchor_hit_pages": cn["text_layer_anchor_hit_pages"],
        "ocr_ms": cn["ocr_ms"], "ocr_chars": cn["ocr_chars"], "score_mean": cn["score_mean"],
        "artifact": next(s for s in agg["source_jsons"] if s["path"].endswith("cn_selfcheck.json")),
        "png": "rendered at _work/cn/cn_p0001.png (path+bytes+sha256 inside artifact)",
    })
    for r in agg["hk_probe"]["rounds"]:
        add({
            "id": f"ocr-hk-{r['json']}", "kind": "hk_probe_render_ocr",
            "artifact": {"path": "_work/" + r["json"], "sha256": r["json_sha256"]},
            "pages": r["pages"], "wall_ms": r["wall_ms"],
            "ocr_reconstruction": True,
        })
    add({
        "id": "ocr-agg-01", "kind": "aggregated_result",
        "artifact": fmeta(os.path.join(WORK, "hk_probe_aggregate.json")),
        "pages_probed": agg["hk_probe"]["pages_probed_count"],
        "anchors_hit": agg["hk_probe"]["anchors_hit"],
        "anchors_missed": agg["hk_probe"]["anchors_missed"],
        "ocr_anchor_page_hits": agg["hk_probe"]["ocr_total_anchor_hits"],
        "text_layer_anchor_page_hits": agg["hk_probe"]["text_layer_total_anchor_hits"],
        "ocr_errors": agg["hk_probe"]["ocr_error_count"],
        "total_ocr_chars": agg["hk_probe"]["total_ocr_chars"],
        "total_wall_ms": agg["hk_probe"]["total_wall_ms"],
    })

    # ---- git audit ----
    add({"id": "git-01", "kind": "git_audit", **git_audit()})
    add({
        "id": "git-02", "kind": "git_audit_other_repo",
        "repo": "C:/Users/郑曾波/Projects/company-wiki",
        "diff_HEAD_total": 3,
        "files": ["CLAUDE.md", "README.md", "src/company_wiki/source_catalog/artifact_dag.py"],
        "mtime": "2026-09-23 13:08:38 (before this card's session start 2026-09-25)",
        "by_this_card": False,
        "note": "read-only inspection via git diff; this card performed zero writes there (only read the two source PDFs)",
    })

    # ---- write face ----
    top = {}
    total_files = total_bytes = 0
    for root, _dirs, files in os.walk(ATTEMPT):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            rel = os.path.relpath(p, ATTEMPT).replace("\\", "/")
            seg = rel.split("/")[0]
            c, b = top.get(seg, (0, 0))
            top[seg] = (c + 1, b + sz)
            total_files += 1
            total_bytes += sz
    png_bytes = 0
    png_count = 0
    for p in [os.path.join(WORK, f) for f in os.listdir(WORK) if f.startswith("cn_selfcheck") or f.startswith("hk_probe")]:
        if not p.endswith(".json"):
            continue
        j = load(p)
        for pg in j.get("pages", []):
            if "png" in pg:
                png_count += 1
                png_bytes += pg["png_bytes"]

    add({
        "id": "writeface-01", "kind": "write_face",
        "root": "execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/",
        "files_total": total_files, "bytes_total": total_bytes,
        "by_top_segment": {k: {"files": v[0], "bytes": v[1]} for k, v in sorted(top.items())},
        "rendered_pngs": {"count": png_count, "bytes": png_bytes,
                          "hashes": "per-page png sha256 recorded inside _work/*.json probe artifacts"},
        "outside_attempt_dir": 0,
        "outside_planning_dir": 0,
        "git_writes": 0,
    })

    doc = {
        "card": "OPEN5-PEND5B-OCR-CAPABILITY",
        "attempt": "a20260924-01",
        "role": "capability_landing",
        "authorized_by": "OWNER_DECISIONS §二十六 #2",
        "generated_utc": utc_now(),
        "network_used": True,
        "downloads_summary": {
            "count": receipts["count"] + 1,
            "total_bytes_chosen": receipts["total_bytes"],
            "largest_single_bytes": receipts["largest_single_bytes"],
            "any_over_200mb": receipts["any_over_200mb"],
            "all_sha256_verified": all(
                d.get("sha256_match") for d in receipts["downloads"]
            ),
            "orphan_extra_bytes": os.path.getsize(orphan) if os.path.exists(orphan) else 0,
            "note": "plus transient index/metadata page fetches (not retained) and one pip diagnostic fetch of six-1.17.0 wheel (11,050 B, into pip temp, deleted with temp)",
        },
        "ocr_reconstruction_disclaimer": True,
        "entries": entries,
    }

    out_path = os.path.join(ATTEMPT, "provenance.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(out_path, "r", encoding="utf-8") as f:
        json.load(f)
    # BOM check
    with open(out_path, "rb") as f:
        head = f.read(3)
    print("wrote", out_path, "entries=", len(entries), "bom=", head == b"\xef\xbb\xbf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
