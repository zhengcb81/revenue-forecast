"""One-shot: make the vacuity carrier reproduce the I-05-B layout exactly.

The carrier keeps its ORIGINAL import block:
    ISO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ISO_ROOT / "checkout_scripts"))
So placing the I-05-B frozen checkout at `<vacuity>/checkout_scripts` makes the
file import exactly the bytes that run did — no code change to the carrier.
"""
from pathlib import Path
import shutil

ATTEMPT = Path(__file__).resolve().parents[1]
VACUITY = ATTEMPT / "scratch" / "vacuity"
I05B_ISO = Path(
    "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs/"
    "I-05-B/a20260919-01/iso/checkout_scripts")

target = VACUITY / "checkout_scripts"
if target.exists():
    shutil.rmtree(target)
shutil.copytree(I05B_ISO, target)
print(f"copied {I05B_ISO}")
print(f"    -> {target}")
for path in sorted(target.rglob("*.py")):
    print("   ", path.relative_to(target))
