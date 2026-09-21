import os, sys
from pathlib import Path
A = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B1-I08C-product-fixes\a20260921-01")
R = A/"iso"/"fixed"/"rf"
sys.path.insert(0, str(R/"tests")); sys.path.insert(0, str(R/"scripts"))
os.environ["REVENUE_PUBLICATION_REGISTRY"]=str(A/"reviewer"/"registry_len.jsonl")
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None); os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
import revenue_core, revenue_report
from test_recognition_bridge import forecast_document
pkg = revenue_core.run_forecast(forecast_document())
md = revenue_report.render_markdown(pkg)
print("render_markdown bytes:", len(md.encode("utf-8")))
