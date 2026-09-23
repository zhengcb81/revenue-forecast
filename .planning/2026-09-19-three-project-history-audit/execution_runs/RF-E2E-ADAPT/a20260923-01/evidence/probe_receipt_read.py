import json, shutil, sqlite3, sys, tempfile
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(RF / "scripts"))
sys.path.insert(0, str(RF / "tests"))
sys.path.insert(0, str(CW / "src"))
from e2e_support.isolated_lake import IsolatedLake  # noqa: E402

td = Path(tempfile.mkdtemp(prefix="rf-adapt-probe-"))
try:
    m = IsolatedLake(td, seed="fc1002").build()
    con = sqlite3.connect(m.catalog_path)
    row = con.execute(
        "SELECT document_id, metadata_json FROM documents LIMIT 1"
    ).fetchone()
    meta = json.loads(row[1] or "{}")
    receipt = meta.get("prompt_injection_review")
    print("FIXTURE RECEIPT KEYS:", sorted(receipt.keys()) if isinstance(receipt, dict) else receipt)

    class Store:
        def fetchone(self, sql, params=()):
            return con.execute(sql, tuple(params)).fetchone()

    from company_wiki.source_catalog.prompt_injection import read_prompt_injection_review

    res = read_prompt_injection_review(Store(), row[0])
    print("read_prompt_injection_review ->", res)
    print("=> envelope prompt_injection_status:", (res or {}).get("status", "not_reviewed"))

    # simulate the contract-field addition (state_domain) only:
    receipt2 = dict(receipt)
    receipt2["state_domain"] = "review"
    meta["prompt_injection_review"] = receipt2
    con.execute(
        "UPDATE documents SET metadata_json=? WHERE document_id=?",
        (json.dumps(meta, ensure_ascii=False), row[0]),
    )
    con.commit()
    res2 = read_prompt_injection_review(Store(), row[0])
    print("WITH state_domain added ->", (res2 or {}).get("status"))
finally:
    shutil.rmtree(td, ignore_errors=True)
