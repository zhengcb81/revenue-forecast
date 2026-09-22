"""Independent hash recomputation for the I-14-D r5 review. Read-only."""
import hashlib, json, os, sys

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
BK = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_bookkeeping_20260922_round74"
MEAS = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_r5_measure_20260922"
MEAS4 = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_r4_measure_20260922"

def h(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()

# label -> (path, registered_bytes_or_None, registered_sha_prefix_or_None, where_registered)
REG = [
 ("r5 product copy", os.path.join(ATT, r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py"), 43362, "ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45", "handoff_r5 product_copy / oracle C5.6"),
 ("r4 product copy", os.path.join(ATT, r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py"), 42829, "15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1", "handoff_r4 product_copy / oracle C4.5"),
 ("r3 product copy", os.path.join(ATT, r"iso\product_narrow_r3\src\company_wiki\source_catalog\observability.py"), 42839, "a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda", "handoff_r3 what_changed.product_copy"),
 ("r2 product copy", os.path.join(ATT, r"iso\product_narrow\src\company_wiki\source_catalog\observability.py"), None, None, "no carrier pin located yet"),
 ("base product copy", os.path.join(ATT, r"iso\product_base\src\company_wiki\source_catalog\observability.py"), None, "c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c", "oracle.md section 0 table (r5-final T4)"),
 ("reviewer_report_r4.md", os.path.join(ATT, "reviewer_report_r4.md"), 51860, "f27a85a51596075b795d885a5ca5120bcd4ccbf057ce9c3d9f9075ff9d294bc6", "DISPATCH.md table"),
 ("reviewer_report_r3.md", os.path.join(ATT, "reviewer_report_r3.md"), 44008, "c617c43a7f674b6b9098a252c10aa354f3634d4c345aa5133d75287e26aa003b", "review.md r3 verdict"),
 ("reviewer_report_r2.md", os.path.join(ATT, "reviewer_report_r2.md"), 39824, "58f92dd7e3a3f66639dbdab4743455a878c4122500ac2d8d132e2eae2bee6c2c", "review.md r3 verdict history"),
 ("reviewer_report.md (r1)", os.path.join(ATT, "reviewer_report.md"), 37659, "499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b", "review.md r1 verdict / oracle C2"),
 ("harness/run_i14d_oracle.py (r3 pin)", os.path.join(ATT, "harness", "run_i14d_oracle.py"), 11043, "f7c94c60ce8dffda8d58786d6b20787ff11e4c5c22f06ec1ba1e0307d96a4fe2", "handoff_r3/r4/r5"),
 ("harness/run_rule_table_i14d.py (r3 pin)", os.path.join(ATT, "harness", "run_rule_table_i14d.py"), 19378, "01a3187e9d5062db316fa89e3fc0feb40f862c782a7ce782aa458c6a0f4f7ed6", "handoff_r3/r4/r5"),
 ("harness/run_i14d_oracle_r4.py", os.path.join(ATT, "harness", "run_i14d_oracle_r4.py"), 12316, "240d181c9fb8f21c42d2d4aaa364936b0fabde7d23dedf0bdd356d497765d13f", "handoff_r4/r5"),
 ("harness/run_rule_table_i14d_r4.py", os.path.join(ATT, "harness", "run_rule_table_i14d_r4.py"), 20006, "610ce4b84903d224aef60a54dd4a5f46872efadeddad869989d86e0418e45aa5", "handoff_r4/r5"),
 ("harness/run_i14d_oracle_r5.py", os.path.join(ATT, "harness", "run_i14d_oracle_r5.py"), 13293, "38a22101cadb07bdb1a017ce9c6c4dad6f126685b242c21d76f2ff69368bb6d6", "handoff_r5"),
 ("harness/run_rule_table_i14d_r5.py", os.path.join(ATT, "harness", "run_rule_table_i14d_r5.py"), 20600, "1e51373a083beda724c23fa63f36f2889fd7a9e1fddec4084b6dc4efe966d689", "handoff_r5"),
 ("handoff_r5.json", os.path.join(ATT, "handoff_r5.json"), 6960, None, "DISPATCH.md table"),
 ("oracle.md (r5 after)", os.path.join(ATT, "oracle.md"), 36533, "e666b637ad3468b79803102b87b31641b102a91936dfa9731567a1abdd45e9c1", "handoff_r5 generation_carriers"),
 ("review.md (r5 after)", os.path.join(ATT, "review.md"), 17860, "0edecc129eec1ca5dc44a2cf79d13fdc590fb58bc86fd5f5da1837df895014a3", "handoff_r5 generation_carriers"),
 # bookkeeping copies
 ("BK i14d_base_observability.py", os.path.join(BK, "i14d_base_observability.py"), None, None, "bookkeeping"),
 ("BK i14d_r2_observability.py", os.path.join(BK, "i14d_r2_observability.py"), None, None, "bookkeeping"),
 ("BK i14d_r3_observability.py", os.path.join(BK, "i14d_r3_observability.py"), None, "a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda", "must equal r3 product copy"),
 ("BK i14d_r4_observability.py", os.path.join(BK, "i14d_r4_observability.py"), None, "15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1", "must equal r4 product copy"),
 ("BK i14d_r5_observability.py", os.path.join(BK, "i14d_r5_observability.py"), None, "ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45", "must equal r5 product copy"),
 # measurement evidence (paths to be resolved)
 ("_r5_measure/r5_measurement.json", os.path.join(MEAS, "r5_measurement.json"), 1901, "6f962dfea9bb5066dadb319ed9370529f351e5fec1f9b295168ca8c6059a75de", "handoff_r5 evidence"),
]

print("== REGISTERED-ARTEFACT HASH RECOMPUTATION ==")
fails = []
for label, path, rbytes, rsha, where in REG:
    if not os.path.exists(path):
        print(f"MISSING  {label}: {path}")
        fails.append((label, "missing"))
        continue
    n, s = h(path)
    okb = (rbytes is None) or (n == rbytes)
    oks = (rsha is None) or (s == rsha)
    mark = "OK " if (okb and oks) else "BAD"
    print(f"{mark} {label}: bytes={n} (reg {rbytes}) sha256={s} (reg {str(rsha)[:12]}...) [{where}]")
    if not (okb and oks):
        fails.append((label, f"bytes {n} vs {rbytes}; sha {s} vs {rsha}"))

print()
print("== RESOLVE _r5_measure_20260922 CONTENTS ==")
for root in (MEAS, MEAS4):
    print(f"--- {root} ---")
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            p = os.path.join(root, fn)
            if os.path.isfile(p):
                n, s = h(p)
                print(f"  {fn}: {n} B  {s}")
    else:
        print("  (absent)")

print()
print("== FAILURES ==", fails if fails else "none")
