"""WC-1 / I-14-D-R8: build changes.diff for BOTH delivery targets (step 8/9).

Target A = the r6 generation tree  (iso/r8_base -> iso/r8_fixed, canonical path
            execution_runs/I-14-D/a20260919-01/iso/product_narrow_r6/...)
Target B = the production company-wiki copy: the SAME three literal edits are
            applied IN MEMORY to the read-only production bytes (each asserted to
            occur exactly once), the result is py_compile-checked, then grafted onto
            a %TEMP% copy of r8_base and run through BOTH instruments (must be
            GREEN = identical verdicts to r8_fixed).  Production is never written.

Output: <attempt>/changes.diff + evidence/production_apply.json
Run:    python -B harness/make_changes_diff.py
"""

from __future__ import annotations

import difflib
import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
I14D = ATT.parent.parent / "I-14-D" / "a20260919-01"
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog"
            r"\observability.py")
OBS_REL = Path("company_wiki") / "source_catalog" / "observability.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_r8  # noqa: E402

PROD_PIN = "edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e"
R6_PIN = "2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464"
PY = sys.executable

HEADER = """# WC-1 / I-14-D-R8 a20260923-01 -- changes.diff
# ONLY the code fixes the WC-1 work card demanded (REGISTRY-CLOSURE decision.md
# L84-85), 2 code changes x 2 delivery targets, nothing else:
#
# K1 (REM-06 / WC-1 1): key_is_credential strips a trailing digit run from each
#   split component before the atom-table lookup -- token2/secret2/password2/
#   api_key2 become credential keys through the SAME split rules as the plain
#   family; a pure-digit component is left as-is.  Pure ADDITION to the accepted
#   key set: bidirectional sweep old-minus-new = [] over the frozen 350-key domain
#   (evidence/key_domain_sweep.json), 4 untouched counter rows (monkey2/oauth2/
#   secretary2/tokenizer2) stay untouched on every tree (evidence/*_rule*.json
#   touched_but_should_not_be), MUT-A kills exactly the 5 REM-06 rows
#   (evidence/mutA_rule_*.json).
# K2 (F-REV-R3-05 / WC-1 2): the after-break value may start with one of the six
#   value delimiters (, ; & | " '); quoted alternatives stay FIRST so terminated
#   quoted values match byte-identically.  Scope frozen in oracle.md 1/4a: after
#   the break run only, delimiter IMMEDIATELY followed by the token; single-line
#   `Authorization: Bot,<secret>` unchanged (row N29).  Bidirectional sweep over
#   the 95 printable ASCII: old-minus-new = [], new-minus-old = exactly those six
#   (evidence/value_start_sweep.json); MUT-B kills exactly the 6 form rows + the
#   2 over-redaction pricing rows (evidence/mutB_rule_*.json).
#
# Matrix: RED on r8_base = 11 oracle + 13 rule failures, exactly the frozen sets;
# GREEN on r8_fixed = oracle 61/61 rc 0 (verdict pass) + rule 113 rows
# fidelity_ok true, registered_open 7/7 (rule rc stays 3 -- negative BY DESIGN
# since r3; no rc 0 claim for the rule table).
# Production target apply-check: evidence/production_apply.json (edits land 1:1,
# py_compile ok, both instruments GREEN on the grafted %TEMP% tree).
#
# Application: standard landing only (later promotion/repair batch, owner's
# decision).  ZERO bytes were written to any production/sealed tree by this card
# (sources read-only; delivery via this diff only).
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_edits_bytes(data: bytes, edits) -> tuple[bytes, list[str]]:
    nl = "\r\n" if b"\r\n" in data else "\n"
    text = data.decode("utf-8")
    applied = []
    for name, old, new in edits:
        old_t = old.replace("\n", nl)
        new_t = new.replace("\n", nl)
        if text.count(old_t) != 1:
            raise SystemExit(f"edit anchor count != 1 for {name}")
        text = text.replace(old_t, new_t)
        applied.append(name)
    return text.encode("utf-8"), applied


def unified(a: bytes, b: bytes, path_a: str, path_b: str) -> str:
    al = a.decode("utf-8").splitlines(keepends=True)
    bl = b.decode("utf-8").splitlines(keepends=True)
    return "".join(difflib.unified_diff(al, bl, fromfile=path_a, tofile=path_b,
                                        n=3))


def run_instruments(src: Path, tag: str, out_dir: Path) -> dict:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": r"C:\Windows\system32",
            "SYSTEMROOT": r"C:\Windows", "TEMP": tempfile.gettempdir(),
            "TMP": tempfile.gettempdir()}
    res = {}
    for name, script in (("oracle", "run_i14d_oracle_r8.py"),
                         ("rule", "run_rule_table_i14d_r8.py")):
        outp = out_dir / f"prodapply_{name}_{tag}.json"
        proc = subprocess.run(
            [PY, "-B", str(ATT / "harness" / script), "--src", str(src),
             "--label", tag, "--out", str(outp)],
            capture_output=True, env=env, cwd=str(ATT))
        report = json.loads(outp.read_text(encoding="utf-8"))
        res[name] = {
            "rc": proc.returncode,
            "verdict": report.get("verdict"),
            "cases": report.get("cases"),
            "entries": report.get("entries"),
            "narrow_must_failed": report.get("narrow_must_failed"),
            "keep_must_failed": report.get("keep_must_failed"),
            "fidelity_ok": report.get("fidelity_ok"),
            "credential_leaks": report.get("credential_leaks"),
            "touched_but_should_not_be": report.get("touched_but_should_not_be"),
            "registered_open": len(report.get("registered_open")
                                   or report.get("registered_open_rows") or []),
            "registered_open_confirmed": len(report.get("registered_open_confirmed")
                                              if name == "oracle"
                                              else report.get("registered_open_leaking")
                                              or []),
            "output": str(outp),
        }
    return res


def main() -> int:
    r6_base = (ATT / "iso" / "r8_base" / OBS_REL).read_bytes()
    r6_fixed = (ATT / "iso" / "r8_fixed" / OBS_REL).read_bytes()
    if sha(r6_base) != R6_PIN:
        raise SystemExit("r8_base pin drift")

    evidence: dict = {
        "target_a": {
            "path": "execution_runs/I-14-D/a20260919-01/iso/product_narrow_r6/"
                    "src/company_wiki/source_catalog/observability.py",
            "before_sha256": sha(r6_base),
            "after_sha256": sha(r6_fixed),
            "bytes_before": len(r6_base),
            "bytes_after": len(r6_fixed),
        },
    }
    diff_a = unified(r6_base, r6_fixed,
                     "a/iso/product_narrow_r6/src/company_wiki/source_catalog/"
                     "observability.py",
                     "b/iso/product_narrow_r6/src/company_wiki/source_catalog/"
                     "observability.py")

    # ---- target B: production, in memory + temp graft ----------------------
    prod = PROD.read_bytes()
    if sha(prod) != PROD_PIN:
        raise SystemExit("production pin drift (file changed under this card)")
    prod_fixed, applied = apply_edits_bytes(prod, build_r8.PRODUCT_EDITS)
    evidence["target_b"] = {
        "path": "company-wiki/src/company_wiki/source_catalog/observability.py",
        "before_sha256": sha(prod),
        "after_sha256": sha(prod_fixed),
        "bytes_before": len(prod),
        "bytes_after": len(prod_fixed),
        "edits_applied_in_memory": applied,
        "production_file_written": False,
        "relation_note": "production = r6 tree minus one dead line at r6 L400; "
                         "both fix regions precede it and are byte-identical "
                         "across targets",
    }

    scratch = Path(tempfile.gettempdir()) / "i14dr8_prodapply"
    if scratch.exists():
        shutil.rmtree(scratch)
    shutil.copytree(ATT / "iso" / "r8_base", scratch / "src",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (scratch / "src" / OBS_REL).write_bytes(prod_fixed)
    pyc = scratch / "src" / OBS_REL
    py_compile.compile(str(pyc), doraise=True)
    evidence["target_b"]["py_compile"] = "ok"

    graft = run_instruments(scratch / "src", "prod_target_r8", ATT / "evidence")
    evidence["target_b"]["instruments_on_grafted_tree"] = graft
    green = (graft["oracle"]["rc"] == 0
             and graft["oracle"]["verdict"] == "pass"
             and graft["oracle"]["cases"] == 61
             and graft["rule"]["fidelity_ok"] is True
             and graft["rule"]["entries"] == 113
             and graft["rule"]["credential_leaks"] == []
             and graft["rule"]["touched_but_should_not_be"] == [])
    evidence["target_b"]["green_match_with_r8_fixed"] = green

    diff_b = unified(prod, prod_fixed,
                     "a/src/company_wiki/source_catalog/observability.py",
                     "b/src/company_wiki/source_catalog/observability.py")

    (ATT / "changes.diff").write_text(HEADER + diff_a + diff_b, encoding="utf-8",
                                      newline="")
    evidence["changes_diff"] = {
        "path": "changes.diff",
        "bytes": (ATT / "changes.diff").stat().st_size,
        "sha256": sha((ATT / "changes.diff").read_bytes()),
        "targets": 2,
    }
    (ATT / "evidence" / "production_apply.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0 if green else 3


if __name__ == "__main__":
    sys.exit(main())
