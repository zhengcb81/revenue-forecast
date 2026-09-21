"""Build the four mutation variants used for the RED->GREEN proof.

Each variant reverts EXACTLY ONE fix in a separate copy, so the fixed tree is
never mutated.  No file writes into the fixed tree or the production repos.
"""
from pathlib import Path
import hashlib
import shutil

ATTEMPT = Path(__file__).resolve().parents[1]
FIXED = ATTEMPT / "iso" / "fixed"
MUT = ATTEMPT / "scratch" / "mutants"

CWS_REL = Path("rf_scripts") / "company_wiki_source.py"
W05C_REL = Path("tests") / "test_w05c_minimal_production.py"
W05B_REL = Path("tests") / "test_w05b_verified_artifact_read.py"

# (mutation id, description, relative file, old text, new text)
MUTATIONS = [
    (
        "M1-rem11-bundle-none-closure",
        "revert REM-11: bundle=None back to the downstream closure of `roles`",
        CWS_REL,
        "return [], _production_scope(roles, set(), [])",
        "return [], sorted({r for role in roles for r in _dag_closure(role)})",
    ),
    (
        "M2-rem13-docstring-old-wording",
        "revert REM-13: docstring back to the pre-I-05-C downstream wording",
        CWS_REL,
        """    - ``producer_events`` — roles that must be (re)produced for THIS request:
      each requested role that is not readable, plus every ancestor of those
      roles that is not reusable.  It is NOT the downstream closure of the
      requested roles — an unrequested dependent is never produced
      (AR-02/AR-03, I-05-C step 2).""",
        """    - ``producer_events`` — roles that must be (re)produced = the DAG closure
      (role + transitive dependents over ROLE_DEPENDENCIES) of the
      non-reusable roles — never a blind full recompute (AR-02/AR-03).""",
    ),
    (
        "M3-rem14-json-misattribution",
        "revert REM-14: row 3 test name back to the misattributed diverge test",
        Path("tests") / "retry-count-vs-artifact-count.json",
        '"test": "test_invocation_trace_accuracy",',
        '"test": "test_retry_count_vs_artifact_count_diverge",',
    ),
    (
        "M4-rem12-stale-iso-binding",
        "revert REM-12: bind the module the way the vacuous I-05-C run did "
        "(I-05-B attempt's frozen iso checkout copy)",
        W05B_REL,
        """_FIXED_ORIGIN = (ISO_ROOT / "rf_scripts" / "company_wiki_source.py").resolve()""",
        """_FIXED_ORIGIN = Path(
    "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs/"
    "I-05-B/a20260919-01/iso/checkout_scripts/company_wiki_source.py").resolve()""",
    ),
]


def build() -> None:
    if MUT.exists():
        shutil.rmtree(MUT)
    for mut_id, description, rel, old, new in MUTATIONS:
        target_dir = MUT / mut_id
        shutil.copytree(FIXED, target_dir)
        path = target_dir / rel
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"{mut_id}: expected exactly 1 occurrence in {rel}, found "
                f"{count}\n--- searched for ---\n{old}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        new_sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        print(f"{mut_id}")
        print(f"   file   : {rel}")
        print(f"   why    : {description}")
        print(f"   new sha: {new_sha}")
    print(f"\nbuilt {len(MUTATIONS)} variants under {MUT}")


if __name__ == "__main__":
    build()
