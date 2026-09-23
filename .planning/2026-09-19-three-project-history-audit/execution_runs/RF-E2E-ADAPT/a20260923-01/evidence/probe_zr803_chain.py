"""zr803 lock-test attribution probe: run the SAME chain the test runs and
show the REAL returncode/stderr (the test's own failure message crashes on
str.decode because the subprocess uses text=True, masking the chain error)."""
import json, os, sqlite3, subprocess, sys, tempfile, shutil
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = RF.parent / "company-wiki"
FILING = RF.parent / "filing-fetch"
sys.path.insert(0, str(RF / "tests"))
sys.path.insert(0, str(RF / "tests" / "e2e_support"))
sys.path.insert(0, str(CW / "src"))

import datetime as _dt
from e2e_support.isolated_lake import IsolatedLake

td = Path(tempfile.mkdtemp(prefix="rf-adapt-zr803-"))
try:
    IsolatedLake(td, seed="zr803").build()
    project = td / "lake" / "project"
    wiki_cfg = td / "wiki.json"
    wiki_cfg.write_text(json.dumps({
        "schema_version": "1.0", "company_wiki_root": str(project)
    }, ensure_ascii=False), encoding="utf-8")
    db = project / ".source_catalog" / "catalog.sqlite3"
    holder = sqlite3.connect(db, timeout=1.0)
    holder.execute("BEGIN EXCLUSIVE")  # exactly like the test
    request = {
        "schema_version": "1.1", "company_query": "紫金矿业", "market": "CN",
        "document_kind": "annual_report", "fiscal_year": 2025,
        "as_of_date": (_dt.date.today() + _dt.timedelta(days=7)).isoformat(),
    }
    env = dict(os.environ); env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(RF / "scripts" / "source_preparation.py"),
             "--company-wiki-config", str(wiki_cfg),
             "--filing-fetch-root", str(FILING),
             "--timeout-seconds", "60"],
            input=json.dumps(request, ensure_ascii=False),
            text=True, encoding="utf-8", capture_output=True,
            cwd=str(RF), env=env, timeout=180, check=False,
        )
        print("LOCK-HELD: returncode =", proc.returncode)
        print("LOCK-HELD stderr tail:", proc.stderr[-500:])
    finally:
        holder.rollback(); holder.close()
    # recovery-after-release leg (second run of the test)
    proc2 = subprocess.run(
        [sys.executable, "-B", str(RF / "scripts" / "source_preparation.py"),
         "--company-wiki-config", str(wiki_cfg),
         "--filing-fetch-root", str(FILING),
         "--timeout-seconds", "60"],
        input=json.dumps(request, ensure_ascii=False),
        text=True, encoding="utf-8", capture_output=True,
        cwd=str(RF), env=env, timeout=180, check=False,
    )
    print("AFTER-RELEASE: returncode =", proc2.returncode)
    print("AFTER-RELEASE stderr tail:", proc2.stderr[-500:])
finally:
    shutil.rmtree(td, ignore_errors=True)
