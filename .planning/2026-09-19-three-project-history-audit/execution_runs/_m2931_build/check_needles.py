import io
import sys

sys.path.insert(0, r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_m2931_build")
import importlib.util

spec = importlib.util.spec_from_file_location(
    "abp",
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_m2931_build\apply_bounded_pass.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

target = sys.argv[1]
text = io.open(target, encoding="utf-8", newline="").read()
print("target", target)
print("has CR:", "\r" in text)
for name in ("OLD_M31_CONSTANT", "NEW_M31_CONSTANT", "OLD_OQ04", "NEW_OQ04", "OLD_OQ05", "NEW_OQ05"):
    needle = getattr(m, name)
    print("%-20s len=%-5d found=%s" % (name, len(needle), needle in text))
print("has STALE SOURCE WARNING:", "STALE SOURCE WARNING" in text)
print("has M31 CARD-TEXT CONSTANT CORRECTED:", "M31 CARD-TEXT CONSTANT CORRECTED" in text)
