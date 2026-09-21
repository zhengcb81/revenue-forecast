import os, sys, json, hashlib, base64, copy
from pathlib import Path
ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B1-I08C-product-fixes\a20260921-01")
REPO = ATT / "reviewer" / "scratch" / "fixed_rf"
sys.path.insert(0, str(REPO/"tests")); sys.path.insert(0, str(REPO/"scripts")); sys.path.insert(0, str(ATT))
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
os.environ["REVENUE_PUBLICATION_REGISTRY"]=str(ATT/"reviewer"/"registry_r13"/"publications.jsonl")
import revenue_core
print("provider env:", os.environ.get("REVENUE_ATTESTATION_PROVIDER"))
print("trust env   :", os.environ.get("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"))
print("capability  :", revenue_core.attestation_capability())
print("last failure:", revenue_core.attestation_last_failure())
