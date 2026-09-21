"""Reviewer (r3) byte-pin recomputation. Recomputes every hash from the bytes.

A hand-written hash looks identical to a real one, so every registered value in
DISPATCH.md and handoff_r3.json is recomputed here from the file on disk.

Run with the attempt's iso venv python.  Read-only w.r.t. the attempt.
"""
import hashlib
import json
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
OUT = Path(__file__).resolve().parent / "hashcheck.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# (label, relative path, registered sha256, registered bytes or None)
PINS = [
    ("reviewer_report.md (r1)", "reviewer_report.md",
     "499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b", 37659),
    ("reviewer_report_r2.md", "reviewer_report_r2.md",
     "58f92dd7e3a3f66639dbdab4743455a878c4122500ac2d8d132e2eae2bee6c2c", 39824),
    ("iso/product_narrow_r3 observability.py", "iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py",
     "a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda", 42839),
    ("harness/run_i14d_oracle.py", "harness/run_i14d_oracle.py",
     "f7c94c60ce8dffda8d58786d6b20787ff11e4c5c22f06ec1ba1e0307d96a4fe2", 11043),
    ("harness/run_rule_table_i14d.py", "harness/run_rule_table_i14d.py",
     "01a3187e9d5062db316fa89e3fc0feb40f862c782a7ce782aa458c6a0f4f7ed6", 19378),
    ("harness/apply_i14d_narrow.py", "harness/apply_i14d_narrow.py",
     "8204b2f971aedd69231e697e580dc93e77f4a597b6c7a1d9c55a3c91ec23bae5", 19773),
    ("harness/authsplit_probe.py", "harness/authsplit_probe.py",
     "649d55277870bd844c13d461088986a2ca4efc9edea0db13003a3b91dd50b151", 5699),
    ("scratch/oracle_r3.json", "scratch/oracle_r3.json",
     "c436d62159c5a19b7fa8d2afe6f0aac9c265af98a52c6a669b0a327b69217cf1", 13316),
    ("scratch/rule_r3.json", "scratch/rule_r3.json",
     "11f5cb18024e00ed77b25976c1b121613ecf098e330df86ac7c6b468912f4130", 28167),
    ("oracle.md (r3 after)", "oracle.md",
     "e85cb05bc278ce4b5281f84fe7bc75330f247a73a14e040ce16347428ac2015a", 27119),
    ("fix_record.md (r3 after)", "fix_record.md",
     "51554127d4c7a8217a4c5c59ddef27d6bcf68c4c03e0a9108d89b535cdb59b73", 12045),
    ("binding.json (r3 after)", "binding.json",
     "2cd31277ff3a4998c6a048c12cb44ad957960826c0adc5103fc5c500c4299b79", 10888),
    ("review.md (r3 after)", "review.md",
     "d9a4ef28cdb5f804b49463399dd45c85d53319864ce63f1ba2360d48715a1bea", 6586),
    ("handoff_r3.json", "handoff_r3.json", None, 9788),
    ("iso/product_base observability.py", "iso/product_base/src/company_wiki/source_catalog/observability.py",
     "c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c", 40060),
    ("iso/product_narrow (r2) observability.py", "iso/product_narrow/src/company_wiki/source_catalog/observability.py",
     "2aa5ed1a219084a67f040388072aa94d7432c63414b6692060f1b4d6b4e12bde", 41432),
    ("iso/product_mut_authsplit observability.py", "iso/product_mut_authsplit/src/company_wiki/source_catalog/observability.py",
     "e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0", 40476),
    ("iso/product_mut_greedy observability.py", "iso/product_mut_greedy/src/company_wiki/source_catalog/observability.py",
     "bc857d411a5363674fff93366f8e6eb717edb670cf2d95178554f81c4984738b", 41638),
    ("iso/product_mut_authnl observability.py", "iso/product_mut_authnl/src/company_wiki/source_catalog/observability.py",
     "a36e90b62e2206f7017d448f8b051c56448fb24102a2c9def82f384ea39e5137", 41429),
    ("iso/product_mut_auth1_r2 observability.py", "iso/product_mut_auth1_r2/src/company_wiki/source_catalog/observability.py",
     "ef450712f13274af82da244b6cea0e3294892ae8d1232ff0c57f3137cc3ecf82", 41427),
    ("production anchor scripts/model_registry.py",
     r"C:\Users\郑曾波\Projects\revenue-forecast\scripts\model_registry.py",
     "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f", 26446),
]


def main() -> int:
    rows, bad = [], 0
    for label, rel, reg_sha, reg_bytes in PINS:
        p = (ATT / rel) if not rel.startswith("..") else (ATT / rel)
        p = p.resolve()
        if not p.exists():
            rows.append({"label": label, "path": str(p), "exists": False})
            bad += 1
            continue
        got_sha, got_bytes = sha(p), p.stat().st_size
        ok_sha = (reg_sha is None) or (got_sha == reg_sha)
        ok_bytes = (reg_bytes is None) or (got_bytes == reg_bytes)
        rows.append({"label": label, "path": str(p), "exists": True,
                     "sha256": got_sha, "bytes": got_bytes,
                     "registered_sha256": reg_sha, "registered_bytes": reg_bytes,
                     "sha_ok": ok_sha, "bytes_ok": ok_bytes,
                     "ok": ok_sha and ok_bytes})
        if not (ok_sha and ok_bytes):
            bad += 1
    out = {"checks": len(rows), "mismatches": bad, "rows": rows}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in rows:
        if not r.get("ok"):
            print("MISMATCH", r["label"], "sha_ok", r.get("sha_ok"),
                  "bytes_ok", r.get("bytes_ok"),
                  "got", r.get("sha256"), r.get("bytes"),
                  "registered", r.get("registered_sha256"), r.get("registered_bytes"))
    print("checked", len(rows), "mismatches", bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
