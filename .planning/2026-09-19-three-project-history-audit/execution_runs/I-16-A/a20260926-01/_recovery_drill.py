#!/usr/bin/env python3
"""I-16-A 隔离恢复演练（全部写入本 attempt 目录；产品三仓只读）。

演练项：
  R1 snapshot → 隔离还原，逐文件 sha256 相等（dirty/untracked 层可恢复）
  R2 DB backup → migrate(v0→v1) → 二次 migrate 只读校验 → 从备份 restore 字节相等（迁移可逆）
  R3 更高 user_version（99）→ fail-closed 抛错，且文件字节不变
  R4 v1 结构漂移 → fail-closed（SchemaDriftError），校验过程不再改动文件
  R5 registry 兼容边界：user_version < 目标 → 自动 bump；> 目标 → 旧代码不校验、静默接受
产出 recovery_drill.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(CW / "src"))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rec(checks: list, cid: str, ok: bool, detail) -> None:
    checks.append({"id": cid, "ok": bool(ok), "detail": detail})


def drill_snapshot(checks: list) -> dict:
    man = json.loads((HERE / "snapshot_manifest.json").read_text(encoding="utf-8"))
    out_root = HERE / "drill_restore"
    mismatch, restored = [], 0
    for row in man["files"]:
        src = HERE / row["snapshot_path"]
        dst = out_root / row["repo"] / Path(row["source_path"]).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dst.write_bytes(data)
        restored += 1
        if hashlib.sha256(data).hexdigest() != row["source_sha256"]:
            mismatch.append(row["source_path"])
    ok = (not mismatch) and restored == man["file_count"] and man["all_match"]
    rec(checks, "R1_snapshot_restore_byte_identical", ok,
        {"restored": restored, "expected": man["file_count"], "mismatch": mismatch})
    return {"restored": restored, "mismatch": mismatch, "ok": ok}


def make_v0_db(p: Path) -> None:
    """构造“已存在的 v0 空库”：有 SQLite 页但无业务表（分类 = v0_empty）。"""
    if p.exists():
        p.unlink()
    conn = sqlite3.connect(str(p))
    conn.execute("CREATE TABLE tmp_scratch(x INTEGER)")
    conn.execute("INSERT INTO tmp_scratch VALUES (1)")
    conn.commit()
    conn.execute("DROP TABLE tmp_scratch")
    conn.commit()
    conn.execute("PRAGMA user_version = 0")
    conn.commit()
    conn.close()


def drill_db(checks: list) -> dict:
    from company_wiki.automation import migrations as mig

    root = HERE / "drill_db"
    root.mkdir(exist_ok=True)
    out: dict = {}

    # R2: backup → migrate → 只读复验 → restore 字节相等
    db = root / "v0_empty.sqlite3"
    make_v0_db(db)
    before = sha256(db)
    backup_holder: dict = {}

    def hook(path: Path, from_v: int, to_v: int) -> Path:
        bak = path.with_suffix(path.suffix + ".pre_migrate.bak")
        shutil.copyfile(path, bak)
        backup_holder["backup"] = str(bak)
        backup_holder["from"] = from_v
        backup_holder["to"] = to_v
        return bak

    report = mig.migrate_database(db, backup_hook=hook)
    after_migrate = sha256(db)
    report2 = mig.migrate_database(db, backup_hook=hook)  # 已 v1 → 只读校验
    after_validate = sha256(db)
    backup = Path(backup_holder.get("backup", ""))
    shutil.copyfile(backup, db)
    after_restore = sha256(db)
    r2_ok = backup.exists() and after_restore == before
    rec(checks, "R2_backup_migrate_restore_byte_identical", r2_ok,
        {"sha_before": before, "sha_after_migrate": after_migrate,
         "sha_after_validate": after_validate, "sha_after_restore": after_restore,
         "backup": backup_holder, "report_from": getattr(report, "from_version", None),
         "report_to": getattr(report, "to_version", None),
         "second_call_is_readonly": after_validate == after_migrate,
         "byte_identical_restore": after_restore == before})
    out["R2"] = {"sha_before": before, "sha_after_migrate": after_migrate,
                 "sha_after_restore": after_restore, "byte_identical": after_restore == before,
                 "backup": backup_holder,
                 "second_migrate_readonly": after_validate == after_migrate}

    # R3: 更高 user_version → fail-closed 且字节不变
    db3 = root / "newer.sqlite3"
    if db3.exists():
        db3.unlink()
    conn = sqlite3.connect(str(db3))
    conn.execute("CREATE TABLE t(x)")
    conn.commit()
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()
    b3 = sha256(db3)
    err3 = None
    try:
        mig.migrate_database(db3, backup_hook=hook)
    except Exception as exc:  # noqa: BLE001
        err3 = f"{type(exc).__name__}: {exc}"
    a3 = sha256(db3)
    r3_ok = err3 is not None and "UnsupportedSchemaVersionError" in err3 and a3 == b3
    rec(checks, "R3_newer_user_version_fail_closed_unchanged", r3_ok,
        {"error": err3, "sha_before": b3, "sha_after": a3, "unchanged": a3 == b3})
    out["R3"] = {"error": err3, "unchanged": a3 == b3}

    # R4: v1 结构漂移 → fail-closed，校验不再改文件
    db4 = root / "drift.sqlite3"
    make_v0_db(db4)
    mig.migrate_database(db4, backup_hook=hook)
    conn = sqlite3.connect(str(db4))
    conn.execute("CREATE TABLE extra_drift(x)")
    conn.commit()
    conn.close()
    b4 = sha256(db4)
    err4 = None
    try:
        mig.validate_database(db4)
    except Exception as exc:  # noqa: BLE001
        err4 = f"{type(exc).__name__}: {exc}"
    a4 = sha256(db4)
    r4_ok = err4 is not None and a4 == b4
    rec(checks, "R4_schema_drift_fail_closed_readonly", r4_ok,
        {"error": err4, "sha_before": b4, "sha_after": a4, "readonly": a4 == b4})
    out["R4"] = {"error": err4, "readonly": a4 == b4}

    # R5: registry 前向兼容边界（source_registry 自动 bump vs 无更高版本守卫）
    from company_wiki.source_registry import SourceRegistry

    reg_rows = {}
    for case, pre_version in (("r1_bump_from_0", 0), ("r2_silently_accept_9", 9)):
        p = root / f"registry_{case}.sqlite3"
        if p.exists():
            p.unlink()
        conn = sqlite3.connect(str(p))
        if pre_version:
            conn.execute(f"PRAGMA user_version = {pre_version}")
        conn.commit()
        conn.close()
        before_uv = sqlite3.connect(str(p)).execute("PRAGMA user_version").fetchone()[0]
        reg = SourceRegistry(p)
        reg.close()
        conn = sqlite3.connect(str(p))
        after_uv = conn.execute("PRAGMA user_version").fetchone()[0]
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()]
        conn.close()
        reg_rows[case] = {"user_version_before": before_uv, "user_version_after": after_uv,
                          "tables": sorted(tables)}
    r5_ok = (
        reg_rows["r1_bump_from_0"]["user_version_after"] == 1
        and reg_rows["r1_bump_from_0"]["tables"] != []
        and reg_rows["r2_silently_accept_9"]["user_version_after"] == 9
        and reg_rows["r2_silently_accept_9"]["tables"] == []
    )
    rec(checks, "R5_registry_compat_boundary_observed", r5_ok, reg_rows)
    out["R5"] = reg_rows
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(HERE / "combo_manifest.json"))
    args = ap.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    checks: list = []
    snap = drill_snapshot(checks)
    db = drill_db(checks)
    catalog = manifest.get("data_layer", {}).get("catalog") or {}
    all_ok = all(c["ok"] for c in checks)
    result = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": "隔离（本 attempt 目录）；产品三仓只读",
        "checks": checks,
        "snapshot_restore": snap,
        "db": db,
        "production_catalog_anchor": {
            "path": catalog.get("path"),
            "bytes": catalog.get("bytes"),
            "sha256_at_bind": catalog.get("sha256"),
            "mtime_utc": catalog.get("mtime_utc"),
            "user_version": catalog.get("user_version"),
            "note": "生产库本卡只读；部署窗口须复核 size/mtime/sha256 与本锚点一致",
        },
        "migration_reversible": bool(
            all_ok
        ),
        "recovery_provable": bool(all_ok),
        "compat_boundary": {
            "catalog_automation": "user_version > SCHEMA_VERSION → UnsupportedSchemaVersionError（fail-closed，文件字节不变）；== → 只读校验；< → 单事务迁移 + backup_hook",
            "registry_source": "user_version < 1 → CREATE + bump 到 1；> 1 → 旧代码不校验、静默接受（**无 fail-closed 前向守卫**，边界风险登记）",
            "raw": "raw 层由 acquisition 追加写入；部署不改 raw 字节；本卡零写（见 combo_manifest.raw）",
        },
        "all_checks_ok": all_ok,
    }
    (HERE / "recovery_drill.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("recovery_drill.json ok=" + str(all_ok) +
          " checks=" + ",".join(f"{c['id']}={c['ok']}" for c in checks))
    return 0 if all_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
