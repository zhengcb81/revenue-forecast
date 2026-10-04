"""Prove the prune_retired_evidence call SIGNATURE is unchanged pre/post:
the 3 contract tests fail with `TypeError: missing keyword-only 'now'`, which
is raised at call binding against the signature — if the signature is
byte-identical between pre-image and post-image, those failures are
pre-existing (introduced by ac4ebd0's `now` requirement; test file last
touched in b6c97b8) and NOT caused by the FC-1204 split.
"""
import importlib.util
import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(REPO / "src"))
OUT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pre = load("company_wiki.source_catalog._probe_pre",
           OUT / "pre_image" / "prune_retired_evidence.py")
post = load("company_wiki.source_catalog._probe_post",
            REPO / "src/company_wiki/source_catalog/prune_retired_evidence.py")

sig_pre = str(inspect.signature(pre.prune_retired_evidence))
sig_post = str(inspect.signature(post.prune_retired_evidence))
print("pre :", sig_pre)
print("post:", sig_post)
print("IDENTICAL" if sig_pre == sig_post else "DIFFERENT")
sys.exit(0 if sig_pre == sig_post else 1)
