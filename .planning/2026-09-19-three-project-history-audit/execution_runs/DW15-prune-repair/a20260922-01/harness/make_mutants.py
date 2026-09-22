"""DW15-REPAIR mutation builder: one defect-fix reverted per mutant copy.

Each mutation is an exact-string replacement over a fresh copy of iso/fixed.
A replacement that does not match EXACTLY once aborts the build, so a mutant
can never silently diverge from its declared revert.

Declared red sets are frozen in oracle.md §3; this script does not compute them.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
FIXED = ATTEMPT / "iso" / "fixed"
MUTANTS = ATTEMPT / "mutants"

PRUNE = Path("company_wiki") / "source_catalog" / "prune_retired_evidence.py"
ARCHIVE = Path("company_wiki") / "source_catalog" / "archive_retired_evidence.py"

M1 = [  # D1 revert: no verified manifest -> original authorisation
    (PRUNE,
     "    archive_root = Path(archive_root)\n"
     "    retired, span_rows = _counts(config.database_path)",
     "    archive_root = Path(archive_root)\n"
     "    m1_due = [False]  # M1 MUTATION state\n"
     "    retired, span_rows = _counts(config.database_path)"),
    (PRUNE,
     "    if plan is None:\n"
     "        built_plan, verified, manifest_problems = _build_plan(\n"
     "            config, archive_root, now, retention_days)\n"
     "        active_plan = built_plan\n"
     "    else:",
     "    if plan is None:\n"
     "        built_plan, verified, manifest_problems = _build_plan(\n"
     "            config, archive_root, now, retention_days)\n"
     "        active_plan = built_plan\n"
     "        if not verified:\n"
     "            # M1 MUTATION: original authorisation — directory age,\n"
     "            # selection = every retired span (original _DELETE_BATCH)\n"
     "            active_plan, m1_due[0] = _m1_plan(config, archive_root, now,\n"
     "                                              retention_days)\n"
     "    else:"),
    (PRUNE,
     "    due = bool(active_plan.archives) and any(\n"
     "        _is_due(va, now, active_plan.retention_days)\n"
     "        for va in active_plan.archives)",
     "    due = m1_due[0] or (bool(active_plan.archives) and any(\n"
     "        _is_due(va, now, active_plan.retention_days)\n"
     "        for va in active_plan.archives))"),
    (PRUNE,
     "from datetime import datetime, timezone",
     "from datetime import date, datetime, timezone"),
    (PRUNE,
     '__all__ = ["PrunePlan", "PruneRefused", "PruneReport", "RETENTION_DAYS",\n'
     '           "VerifiedArchive", "prune_retired_evidence"]',
     'def _iso_date(name: str) -> bool:\n'
     '    try:\n'
     '        date.fromisoformat(name)\n'
     '        return True\n'
     '    except ValueError:\n'
     '        return False\n'
     '\n'
     '\n'
     'def _m1_plan(config, archive_root, now, retention_days):\n'
     '    """M1 MUTATION: original authorisation — oldest archive directory age\n'
     '    against the injected clock; selection = all retired spans."""\n'
     '    archive_dir = archive_root / "archive"\n'
     '    names = sorted(d.name for d in archive_dir.iterdir()\n'
     '                   if d.is_dir() and len(d.name) == 10 and _iso_date(d.name)\n'
     '                   ) if archive_dir.exists() else []\n'
     '    oldest = names[0] if names else None\n'
     '    due = oldest is not None and (\n'
     '        now.astimezone(timezone.utc).date()\n'
     '        - date.fromisoformat(oldest)).days >= retention_days\n'
     '    if not due:\n'
     '        empty = PrunePlan((), {}, (), retention_days,\n'
     '                          PrunePlan.compute_hash([], {}, (), retention_days))\n'
     '        return empty, False\n'
     '    conn = sqlite3.connect(f"file:{config.database_path}?mode=ro", uri=True)\n'
     '    conn.row_factory = sqlite3.Row\n'
     '    try:\n'
     '        ids = [r[0] for r in conn.execute(\n'
     '            "SELECT span_id FROM evidence_spans WHERE document_id IN "\n'
     '            "(SELECT document_id FROM documents WHERE source_status=\'retired\') "\n'
     '            "ORDER BY span_id")]\n'
     '    finally:\n'
     '        conn.close()\n'
     '    states = _span_states(config.database_path, ids)\n'
     '    digests = {sid: states[sid][0] for sid in ids if sid in states}\n'
     '    plan_ids = sorted(digests)\n'
     '    return (PrunePlan(tuple(plan_ids), digests, (), retention_days,\n'
     '                      PrunePlan.compute_hash(plan_ids, digests, (),\n'
     '                                              retention_days)), True)\n'
     '\n'
     '\n'
     '__all__ = ["PrunePlan", "PruneRefused", "PruneReport", "RETENTION_DAYS",\n'
     '           "VerifiedArchive", "prune_retired_evidence"]'),
]

M2 = [  # D2 revert: fixed output names, published file may be overwritten
    (ARCHIVE,
     '    out_path = out_dir / f"retired-evidence-{token}.jsonl.gz"\n'
     '    if out_path.exists():\n'
     '        raise FileExistsError(f"snapshot path already published: {out_path}")\n',
     '    out_path = out_dir / "retired-evidence.jsonl.gz"  # M2 MUTATION\n'),
    (ARCHIVE,
     '    if final_path.exists():\n'
     '        raise FileExistsError(f"snapshot path already published: {final_path}")\n'
     '    try:\n'
     '        os.link(temp_path, final_path)   # atomic; fails if the target exists\n'
     '        temp_path.unlink()\n'
     '    except (AttributeError, NotImplementedError, OSError):\n'
     '        if final_path.exists():\n'
     '            raise FileExistsError(f"snapshot path already published: {final_path}")\n'
     '        os.rename(temp_path, final_path)',
     '    os.replace(temp_path, final_path)  # M2 MUTATION: overwrite (original)'),
    (PRUNE,
     '        receipt_file = config.catalog_dir / "artifacts" / "gates" / (\n'
     '            f"prune-retired-{uuid.uuid4().hex[:16]}.json")',
     '        receipt_file = config.catalog_dir / "artifacts" / "gates" / (\n'
     '            "prune-retired.json")  # M2 MUTATION'),
]

M3 = [  # D3 revert: retention clock = archive directory name vs wall clock
    (PRUNE,
     "from datetime import datetime, timezone",
     "from datetime import date, datetime, timezone"),
    (PRUNE,
     'def _is_due(archive: VerifiedArchive, now: datetime,\n'
     '            retention_days: int) -> bool:\n'
     '    """D3: the retention clock is verified_completed_at vs the injected now —\n'
     '    never a directory name, never the machine clock (W15-R3)."""\n'
     '    age = now.astimezone(timezone.utc) - _parse_utc(archive.verified_completed_at)\n'
     '    return age.days >= retention_days',
     'def _is_due(archive: VerifiedArchive, now: datetime,\n'
     '            retention_days: int) -> bool:\n'
     '    """M3 MUTATION: original clock — directory name vs the wall clock."""\n'
     '    day = Path(archive.archive_path).parent.name\n'
     '    try:\n'
     '        dir_date = date.fromisoformat(day)\n'
     '    except ValueError:\n'
     '        return False\n'
     '    return (datetime.now(timezone.utc).date() - dir_date).days >= retention_days'),
]

M4 = [  # D4 revert: plan trusted, rows never re-verified before/in the delete
    (PRUNE,
     '            live_digest, status = state\n'
     '            if status != "retired":\n'
     '                raise PruneRefused(\n'
     '                    f"document of {span_id} is no longer retired; whole apply refused")\n'
     '            if live_digest != active_plan.row_digests[span_id]:\n'
     '                raise PruneRefused(\n'
     '                    f"row {span_id} changed since the plan was frozen; whole apply refused")\n',
     '            # M4 MUTATION: digest/status re-verification removed\n'),
    (PRUNE,
     '                for span_id in batch:\n'
     '                    row = rows.get(span_id)\n'
     '                    if row is None:\n'
     '                        raise PruneRefused(\n'
     '                            f"row {span_id} vanished mid-apply; whole apply refused")\n'
     '                    digest_row = {key: row[key] for key in row.keys()\n'
     '                                  if key != "__source_status"}\n'
     '                    if row["__source_status"] != "retired":\n'
     '                        raise PruneRefused(\n'
     '                            f"document of {span_id} reactivated mid-apply; "\n'
     '                            "whole apply refused")\n'
     '                    if _row_digest(digest_row) != active_plan.row_digests[span_id]:\n'
     '                        raise PruneRefused(\n'
     '                            f"row {span_id} changed mid-apply; whole apply refused")\n',
     '                # M4 MUTATION: in-transaction re-verification removed\n'),
]

M5 = [  # D5 revert: snapshot written straight to its published path; no
        # pending receipt before the first delete
    (ARCHIVE,
     '        with gzip.open(tmp_path, "wt", encoding="utf-8", newline="\\n") as fh:',
     '        with gzip.open(out_path, "wt", encoding="utf-8", newline="\\n") as fh:  # M5'),
    (ARCHIVE,
     '        _fsync_file(tmp_path)\n'
     '        verified_count, verified_digests = _verify_snapshot(tmp_path)',
     '        _fsync_file(out_path)\n'
     '        verified_count, verified_digests = _verify_snapshot(out_path)'),
    (ARCHIVE,
     '        _publish(tmp_path, out_path)',
     '        os.replace(tmp_path, out_path) if tmp_path.exists() else None  # M5'),
    (PRUNE,
     '        receipt_file.parent.mkdir(parents=True, exist_ok=True)\n'
     '        _atomic_write_json(receipt_file, receipt)\n'
     '        receipt_path = str(receipt_file.resolve())',
     '        receipt_file.parent.mkdir(parents=True, exist_ok=True)\n'
     '        # M5 MUTATION: no pending receipt before the first delete\n'
     '        receipt_path = str(receipt_file.resolve())'),
]

MUTATIONS = {"m1": M1, "m2": M2, "m3": M3, "m4": M4, "m5": M5}


def build(name: str, edits) -> Path:
    target = MUTANTS / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(FIXED, target, ignore=shutil.ignore_patterns("__pycache__"))
    for rel, old, new in edits:
        path = target / rel
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"mutation {name}: anchor in {rel} matched {count} times "
                f"(expected exactly 1); mutant NOT built")
        path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"mutation {name}: {len(edits)} edit(s) applied to {target}")
    return target


if __name__ == "__main__":
    names = sys.argv[1:] or list(MUTATIONS)
    for mutation_name in names:
        build(mutation_name, MUTATIONS[mutation_name])
