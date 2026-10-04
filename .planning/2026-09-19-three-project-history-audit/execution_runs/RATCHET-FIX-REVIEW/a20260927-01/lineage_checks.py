"""C1  Are the 5 reds caused by this delta, or pre-existing?

Method: the failures are `TypeError: <fn>() missing 1 required keyword-only
argument: 'now'`, raised at CALL BINDING (before any body runs).  So load each
module's HEAD/pre-image body AND its worktree body into the same process and
attempt the exact call the contract test makes.  If BOTH bodies fail with the
identical TypeError against the identical call site, the delta cannot be the
cause -- the body is never entered.

C2  "Legacy fork" check: is any pre-delta function left behind in the file
    after the split?  Count top-level defs and compare the symbol set before
    vs after; a leftover old body would show up as a def that still exists but
    is no longer referenced from the entry point.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SRC = WIKI / "src" / "company_wiki" / "source_catalog"
C_RUN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
         r"\2026-09-19-three-project-history-audit\execution_runs"
         r"\RATCHET-FIX-C\a20260927-01")
sys.path.insert(0, str(WIKI / "src"))
FAILURES: list[str] = []


def git_show(rel: str) -> str:
    cp = subprocess.run(["git", "-C", str(WIKI), "show", f"HEAD:{rel}"],
                        capture_output=True)
    assert cp.returncode == 0, rel
    return cp.stdout.decode("utf-8")


def load_variant(real_mod: types.ModuleType, text: str, tag: str):
    name = f"_variant_{real_mod.__name__.rsplit('.', 1)[-1]}_{tag}"
    mod = types.ModuleType(name)
    mod.__dict__.update({k: v for k, v in real_mod.__dict__.items()
                         if not k.startswith("__")})
    mod.__dict__["__name__"] = name
    sys.modules[name] = mod
    tree = ast.parse(text)
    keep = [n for n in tree.body
            if not isinstance(n, (ast.Import, ast.ImportFrom))]
    body = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(body)
    exec(compile(body, f"<{tag}>", "exec"), mod.__dict__)
    return mod


print("=" * 78)
print("C1  CALL-BINDING PROOF — pre-image body vs worktree body, same call")
print("=" * 78)
import company_wiki.source_catalog.archive_retired_evidence as real_arch  # noqa: E402
import company_wiki.source_catalog.prune_retired_evidence as real_prune  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="rfrv-bind-"))
try:
    variants = {
        "archive": (
            real_arch, "archive_retired_evidence",
            [git_show("src/company_wiki/source_catalog/archive_retired_evidence.py"),
             (SRC / "archive_retired_evidence.py").read_text(encoding="utf-8")],
            ("db.sqlite3", tmp / "manifests"),
        ),
        "prune": (
            real_prune, "prune_retired_evidence",
            [(Path(C_RUN) / "pre_image" / "prune_retired_evidence.py").read_text(encoding="utf-8"),
             (SRC / "prune_retired_evidence.py").read_text(encoding="utf-8")],
            (None, tmp / "archive"),
        ),
    }
    for tag, (real_mod, fname, texts, args) in variants.items():
        print(f"\n[{tag}] call: {fname}{args}")
        for label, text in zip(("PRE", "POST"), texts):
            mod = load_variant(real_mod, text, f"{tag}_{label}")
            fn = getattr(mod, fname)
            sig = inspect.signature(fn)
            now_param = sig.parameters.get("now")
            try:
                fn(*args)
                out = "NO-RAISE"
            except TypeError as exc:
                out = f"TypeError: {exc}"
            except Exception as exc:  # noqa: BLE001
                out = f"{type(exc).__name__}: {exc}"
            print(f"  {label:4s} now-kwonly={now_param is not None and now_param.kind is inspect.Parameter.KEYWORD_ONLY}"
                  f" default={now_param.default if now_param else '-'!r}")
            print(f"       -> {out}")
            setattr(sys.modules["__main__"], f"_{tag}_{label}_out", out)
        pre_out = getattr(sys.modules["__main__"], f"_{tag}_PRE_out")
        post_out = getattr(sys.modules["__main__"], f"_{tag}_POST_out")
        same = pre_out == post_out
        print(f"  {'PASS' if same else 'FAIL'}  pre-image and worktree fail IDENTICALLY -> "
              f"delta cannot cause it (body never entered)")
        if not same:
            FAILURES.append(f"C1 {tag}: pre={pre_out} post={post_out}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("=" * 78)
print("C2  LEGACY-FORK CHECK — top-level def sets, pre-image vs worktree")
print("=" * 78)
for rel, pre_text in (
    ("archive_retired_evidence.py",
     git_show("src/company_wiki/source_catalog/archive_retired_evidence.py")),
    ("prune_retired_evidence.py",
     (Path(C_RUN) / "pre_image" / "prune_retired_evidence.py").read_text(encoding="utf-8")),
    ("observability.py",
     (Path(C_RUN) / "pre_image" / "observability.py").read_text(encoding="utf-8")),
):
    cur_text = (SRC / rel).read_text(encoding="utf-8")
    pre_defs = {n.name for n in ast.parse(pre_text).body
                if isinstance(n, ast.FunctionDef)}
    cur_defs = {n.name for n in ast.parse(cur_text).body
                if isinstance(n, ast.FunctionDef)}
    removed = sorted(pre_defs - cur_defs)
    added = sorted(cur_defs - pre_defs)

    # A "legacy fork" = a pre-delta function body still present but no longer
    # driven by the new entry point.  Two precise signals:
    #   (i)  any function the delta ADDED that nothing reaches, and
    #   (ii) any pre-existing function whose reachability CHANGED to unreachable.
    # Reachability counts ast.Name references anywhere (not just Call nodes), so
    # `field(default_factory=_utc_now_iso)` counts.
    def unreachable(text: str) -> set[str]:
        tree = ast.parse(text)
        defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        names_in = {name: {n.id for n in ast.walk(node)
                           if isinstance(n, ast.Name) and n.id in defs}
                    for name, node in defs.items()}
        # every def that is referenced from module scope (decorators, class
        # bodies, dataclass field defaults, module-level expressions) is rooted
        top_refs = {n.id for node in tree.body
                    if not isinstance(node, ast.FunctionDef)
                    for n in ast.walk(node)
                    if isinstance(n, ast.Name) and n.id in defs}
        roots = ({n for n in defs if not n.startswith("_")} | top_refs)
        reach, frontier = set(roots), set(roots)
        while frontier:
            nxt = set()
            for n in frontier:
                nxt |= names_in.get(n, set()) - reach
            reach |= nxt
            frontier = nxt
        return set(defs) - reach

    pre_orph, cur_orph = unreachable(pre_text), unreachable(cur_text)
    new_orphans = sorted(cur_orph & set(added))
    regressed = sorted(cur_orph - pre_orph)
    print(f"\n{rel}")
    print(f"  defs pre={len(pre_defs)} post={len(cur_defs)}")
    print(f"  REMOVED defs: {removed}  (nothing was deleted)")
    print(f"  added defs ({len(added)}): {added}")
    print(f"  unreachable pre={sorted(pre_orph)} post={sorted(cur_orph)}")
    print(f"  {'PASS' if not new_orphans else 'FAIL'}  newly-added defs that are "
          f"unreachable (legacy fork): {new_orphans}")
    print(f"  {'PASS' if not regressed else 'FAIL'}  pre-existing defs that "
          f"BECAME unreachable: {regressed}")
    if removed:
        FAILURES.append(f"C2 {rel}: defs removed {removed}")
    if new_orphans:
        FAILURES.append(f"C2 {rel}: orphaned new defs {new_orphans}")
    if regressed:
        FAILURES.append(f"C2 {rel}: defs became unreachable {regressed}")

print()
print("=" * 78)
print("SUMMARY")
print("=" * 78)
if FAILURES:
    for f in FAILURES:
        print("FAIL:", f)
    sys.exit(1)
print("ALL LINEAGE / FORK CHECKS PASS")
