"""Review-side differential + end-to-end behaviour checks (READ-ONLY).

B1  Redaction surface (SECURITY FACE).  Load HEAD's pre-split (complexity 27)
    `_redact_assignments` alongside the worktree's post-split version and
    differential-fuzz them on adversarial `key = value` inputs.  A dropped or
    weakened redaction branch surfaces as an output divergence.
    Harness soundness is asserted BEFORE any result is trusted.

B2  String-constant multiset pre-image vs worktree, per file: proves no
    error / refusal / receipt / problem-message string was dropped or reworded.

B3  archive_retired_evidence end-to-end with the REQUIRED `now=` kwarg -- which
    the in-repo contract test cannot do (its call site never passes `now`, so it
    dies at argument binding and exercises ZERO body code):
      * real export of 6 rows, pre-image body vs worktree body
      * report / row order / gz text / manifest payload must agree
      * report.archive_sha256 must equal the sha256 of the PUBLISHED bytes
      * negative-path invariants (reconciliation mismatch, self-verification
        mismatch) must raise the SAME exception type and message in both bodies

GUARDED with __main__: company-wiki's scan/normalize uses multiprocessing on
Windows and an unguarded __main__ is re-executed by every spawn child.
"""

from __future__ import annotations

import ast
import gzip
import hashlib
import importlib.util
import json
import random
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import types
from datetime import datetime, timezone
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SRC = WIKI / "src" / "company_wiki" / "source_catalog"
C_RUN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
         r"\2026-09-19-three-project-history-audit\execution_runs"
         r"\RATCHET-FIX-C\a20260927-01")
GATE = WIKI / "tests" / "contract" / "test_fc1204_complexity_ratchet.py"

sys.path.insert(0, str(WIKI / "src"))
FAILURES: list[str] = []
NOTES: list[str] = []


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def git_show(rel: str) -> str:
    cp = subprocess.run(["git", "-C", str(WIKI), "show", f"HEAD:{rel}"],
                        capture_output=True)
    assert cp.returncode == 0, f"git show failed for {rel}"
    return cp.stdout.decode("utf-8")


_gate_spec = importlib.util.spec_from_file_location("gate", GATE)
_gate = importlib.util.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(_gate)


# ============================================================ B1
def b1() -> None:
    print("=" * 78)
    print("B1  REDACTION SURFACE — HEAD (pre-split, 27) vs WORKTREE (post-split)")
    print("=" * 78)
    from company_wiki.source_catalog import observability as obs

    head_src = git_show("src/company_wiki/source_catalog/observability.py")
    cur_src = (SRC / "observability.py").read_text(encoding="utf-8")
    print(f"HEAD sha256     = {sha(head_src.encode('utf-8'))}")
    print(f"worktree sha256 = {sha(cur_src.encode('utf-8'))}")

    # exec EVERY HEAD top-level def into a copy of the live namespace; the live
    # module object is never mutated, so the worktree stays pristine.
    tree = ast.parse(head_src)
    head_globals = dict(obs.__dict__)
    head_globals["__name__"] = obs.__name__ + "_headcopy"
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            seg = ast.get_source_segment(head_src, node)
            exec(compile(ast.parse(seg), "<head>", "exec"), head_globals)

    head_assign = head_globals["_redact_assignments"]
    post_assign = obs._redact_assignments
    head_metric = 1 + _gate._mccabe(ast.parse(ast.get_source_segment(
        head_src, next(n for n in tree.body
                       if isinstance(n, ast.FunctionDef)
                       and n.name == "_redact_assignments"))))
    print(f"harness: HEAD copy metric={head_metric} (expect 27), "
          f"distinct-from-worktree={head_assign is not post_assign} (expect True)")
    if head_metric != 27 or head_assign is post_assign:
        FAILURES.append("B1 harness broken (HEAD copy not loaded)")
        return

    head_defs = {n.name: ast.get_source_segment(head_src, n) for n in tree.body
                 if isinstance(n, ast.FunctionDef)}
    cur_defs = {n.name: ast.get_source_segment(cur_src, n)
                for n in ast.parse(cur_src).body
                if isinstance(n, ast.FunctionDef)}
    changed = sorted(k for k in head_defs.keys() & cur_defs.keys()
                     if head_defs[k] != cur_defs[k])
    print(f"changed defs  = {changed}")
    print(f"removed defs  = {sorted(head_defs.keys() - cur_defs.keys())} (expect [])")
    print(f"new defs      = {sorted(cur_defs.keys() - head_defs.keys())}")
    if head_defs.keys() - cur_defs.keys():
        FAILURES.append("B1 a top-level function was DELETED by the split")

    # transitive closure of the redaction entry points: every member is exec'd
    # from HEAD, therefore by construction HEAD's version.
    def calls(seg: str) -> set[str]:
        return {n.func.id for n in ast.walk(ast.parse(seg))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}

    closure = {"redact_text", "redact_and_truncate", "_redact_assignments",
               "_redact_detail"}
    frontier = set(closure)
    while frontier:
        nxt = {c for name in frontier if name in head_defs
               for c in calls(head_defs[name]) if c in head_defs} - closure
        closure |= nxt
        frontier = nxt
    print(f"redaction call-closure ({len(closure)}): {sorted(closure)}")

    def consts(src: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for n in ast.parse(src).body:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = ast.get_source_segment(src, n.value)
        return out

    hc, cc = consts(head_src), consts(cur_src)
    cdiff = sorted(k for k in hc.keys() & cc.keys() if hc[k] != cc[k])
    print(f"changed module constants = {cdiff} (expect [])")
    if cdiff:
        FAILURES.append(f"B1 redaction constants changed: {cdiff}")
        return
    if head_globals["exception_cause_types"].__code__.co_filename != "<head>":
        FAILURES.append("B1 harness: HEAD defs did not win")
        return
    print("harness self-check OK (HEAD closure + identical constants)")

    TOKENS = [
        "token", "password", "secret", "api_key", "apikey", "authorization",
        "credential", "cmd", "doc", "stage", "status", "note", "well", "x",
        "TOKEN", "Token", "tOkEn", "key", "keys", "token_x", "x_token",
        "=", ":", "==", "::", " ", "  ", "\t", "\n", "\r\n", "", "'", '"',
        "'''", '"""', "\\", "'\"", "v", "value", "s3cret", "a-b_c.d",
        "?", "&", "#", "%", "$", "/", "-", "_", ",", ";", "|", "(", ")", "[",
        "]", "{", "}", "<", ">", "@", "!", "*", "+", "0", "17",
        "https://example.invalid/?token=x&stage=scan",
    ]
    SEPS = ["", " ", "  ", "\t", "\n", "\r\n", " = ", "= ", " =", ":", ": ", " : "]
    rng = random.Random(20260927)
    N = 400_000
    mismatch = None
    for _ in range(N):
        s = "".join(rng.choice(TOKENS) + rng.choice(SEPS)
                    for _ in range(rng.randint(1, 9)))
        if head_assign(s) != post_assign(s):
            mismatch = (s, head_assign(s), post_assign(s))
            break
    if mismatch:
        print("FAIL divergence:", repr(mismatch[0]))
        print("   HEAD    :", repr(mismatch[1]))
        print("   worktree:", repr(mismatch[2]))
        FAILURES.append(f"B1 redaction divergence on {mismatch[0]!r}")
    else:
        print(f"PASS  {N} fuzzed inputs: HEAD == worktree byte-identical")

    TARGETED = [
        "cmd: --token=private-value\ndoc=17\n"
        "url=https://example.invalid/?token=another-secret&stage=scan\n"
        'token = "quoted secret"\nstatus=failed',
        "token=", "token= ", "token=  ", "token", "token:", "token: ",
        "token='", 'token="', "token='unterminated", 'token="unterminated',
        "=token", "xtoken=1", "tokenx=1", "token = 1", "token  =  1",
        "a token = secret b", "token\t=\tsecret", "token\n=\nsecret",
        "token=secret\n", "\ntoken=secret", "token=secret doc=17",
        "token=secret,doc=17", "token:a:b", "token::a", "token==a",
        "password=p@ss word=2", "token=$(shell)", "token=`cmd`",
        "TOKEN=abc", "tOkEn=abc", "token ='a'", 'token="a"',
        "url/?api_key=abc&x=1", "token=&stage=scan", "token=\nstage=scan",
    ]
    bad = [s for s in TARGETED if head_assign(s) != post_assign(s)]
    lost = [s for s in TARGETED
            if obs.REDACT in head_assign(s) and obs.REDACT not in post_assign(s)]
    print(f"{'PASS' if not bad else 'FAIL'}  {len(TARGETED)} targeted inputs identical")
    print(f"{'PASS' if not lost else 'FAIL'}  no targeted case lost its <redacted>")
    if bad:
        FAILURES.append(f"B1 targeted mismatch: {bad!r}")
    if lost:
        FAILURES.append(f"B1 redaction REGRESSION on: {lost!r}")

    # second axis: redaction must never be a no-op where HEAD redacted
    rng2 = random.Random(7)
    head_hits = post_hits = 0
    weaker = []
    for _ in range(60_000):
        s = "".join(rng2.choice(TOKENS) + rng2.choice(SEPS)
                    for _ in range(rng2.randint(1, 9)))
        h = obs.REDACT in head_assign(s)
        p = obs.REDACT in post_assign(s)
        head_hits += h
        post_hits += p
        if h and not p:
            weaker.append(s)
            break
    print(f"PASS  redaction-rate axis: HEAD hit {head_hits}, worktree hit "
          f"{post_hits} (worktree never weaker)" if not weaker
          else f"FAIL  worktree weaker on {weaker[0]!r}")
    if weaker:
        FAILURES.append(f"B1 worktree redacts LESS than HEAD: {weaker[0]!r}")


# ============================================================ B2
def b2() -> None:
    print()
    print("=" * 78)
    print("B2  STRING-CONSTANT MULTISET  pre-image vs worktree")
    print("=" * 78)

    def strs(text: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for n in ast.walk(ast.parse(text)):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                out[n.value] = out.get(n.value, 0) + 1
        return out

    for rel in ("archive_retired_evidence.py", "prune_retired_evidence.py",
                "observability.py"):
        pre = Path(C_RUN) / "pre_image" / rel
        label = "pre_image" if pre.exists() else "HEAD"
        pre_text = (pre.read_text(encoding="utf-8") if pre.exists()
                    else git_show(f"src/company_wiki/source_catalog/{rel}"))
        a, b = strs(pre_text), strs((SRC / rel).read_text(encoding="utf-8"))
        missing = {k: v for k, v in a.items() if b.get(k, 0) < v}
        added = {k: v for k, v in b.items() if a.get(k, 0) < v}
        # ignore prose: only short constants carry behaviour (messages, codes)
        behaviour = {k: v for k, v in missing.items() if len(k) < 200}
        prose = {k: v for k, v in missing.items() if len(k) >= 200}
        print(f"\n{rel} [{label}] {sum(a.values())} -> {sum(b.values())} consts")
        print(f"  dropped/reduced SHORT consts (behaviour): {len(behaviour)}")
        for k, v in list(behaviour.items())[:15]:
            print(f"     {v}x {k!r}")
        print(f"  dropped/reduced LONG consts (docstrings): {len(prose)}")
        for k in list(prose)[:3]:
            print(f"     1x {k[:80]!r}...")
        print(f"  added: {len(added)}")
        if behaviour:
            FAILURES.append(f"B2 {rel}: behaviour strings dropped: "
                            f"{list(behaviour)[:6]}")


# ============================================================ B3
ANNUAL = (
    "第一节 释义\n\n释义：本报告使用的术语与定义说明，包括公司与关联方的界定，以及财务指标的计量口径说明。\n\n"
    "第三节 公司业务概要\n\n主营业务：公司主要从事半导体设备的研发、生产与销售，产品覆盖刻蚀、薄膜沉积、清洗等关键工艺环节。\n\n"
    "第四节 经营情况讨论与分析\n\n经营情况：报告期内公司营业收入稳步增长，主要得益于先进制程设备出货量提升与国产替代进程加速。\n"
)
NOW = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)
TOKEN_RE = __import__("re").compile(r"retired-evidence-[0-9a-f]{16}")

import company_wiki.source_catalog as cw_module  # noqa: E402
import company_wiki.source_catalog.archive_retired_evidence as real_archive  # noqa: E402
from company_wiki.source_catalog.store import retire_document  # noqa: E402


def build_catalog(tmp: Path):
    project = tmp / "project"
    source_root = tmp / "sources"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "a.txt").write_text(ANNUAL, encoding="utf-8")
    cat = cw_module.SourceCatalog(cw_module.CatalogConfig(
        project_root=project,
        catalog_dir=project / ".source_catalog",
        roots=(cw_module.RootSpec("external", source_root, "directory"),),
    ))
    cat.scan()
    cat.normalize()
    doc = cat.store.fetchone("SELECT document_id FROM documents")
    retire_document(cat.store, document_id=doc["document_id"],
                    reason="test", created_by="test")
    return cat


def load_variant(text: str, tag: str) -> types.ModuleType:
    """Load a *variant* of archive_retired_evidence.py as its own module."""
    name = f"_variant_archive_{tag}"
    mod = types.ModuleType(name)
    mod.__dict__.update({k: v for k, v in real_archive.__dict__.items()
                         if not k.startswith("__")})
    mod.__dict__["__name__"] = name
    sys.modules[name] = mod  # dataclasses resolves sys.modules[cls.__module__]
    tree = ast.parse(text)
    keep = [n for n in tree.body
            if not isinstance(n, (ast.Import, ast.ImportFrom))]
    body = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(body)
    exec(compile(body, f"<{tag}>", "exec"), mod.__dict__)
    # sanity: this variant's own body must be the one in force
    assert mod.archive_retired_evidence.__code__.co_filename == f"<{tag}>"
    return mod


def run_variant(text: str, tag: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"rfrv-arch-{tag}-"))
    try:
        cat = build_catalog(tmp)
        n_retired = cat.store.fetchone(
            "SELECT COUNT(*) FROM evidence_spans WHERE document_id IN "
            "(SELECT document_id FROM documents WHERE source_status='retired')")[0]
        mod = load_variant(text, tag)
        rep = mod.archive_retired_evidence(cat.config.database_path,
                                           tmp / "manifests", now=NOW)
        ap = Path(rep.archive_path)
        man_path = ap.parent / f"{ap.name}.manifest.json"
        man = json.loads(man_path.read_text(encoding="utf-8"))
        raw = ap.read_bytes()
        with gzip.open(ap, "rt", encoding="utf-8") as fh:
            gz = fh.read()
        rows = [json.loads(ln) for ln in gz.splitlines()]
        return {
            "harness_retired_spans": n_retired,
            "ok": rep.ok,
            "rows_written": rep.rows_written,
            "rows_in_catalog": rep.rows_in_catalog,
            "actual_sha": sha(raw),
            "archive_bytes": len(raw),
            "name_shape": TOKEN_RE.sub("retired-evidence-<token>", ap.name),
            "manifest_name_shape": TOKEN_RE.sub(
                "retired-evidence-<token>", man_path.name),
            "gz_text_sha256": sha(gz.encode("utf-8")),
            "row_span_ids": [r["span_id"] for r in rows],
            "row_count": len(rows),
            "manifest": {k: v for k, v in man.items()
                         if k not in ("archive_path", "archive_sha256")},
            "dir_shape": sorted(TOKEN_RE.sub("retired-evidence-<token>", p.name)
                                for p in ap.parent.iterdir()),
            "tmp_leftovers": sorted(p.name for p in ap.parent.glob("*.partial*")),
            "manifest_ok": man.get("ok"),
            "manifest_problems": man.get("problems"),
            "manifest_archive_sha256": man.get("archive_sha256"),
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def negative_paths(text: str, tag: str) -> dict:
    """Force the two fail-closed invariants and record the exception identity."""
    out: dict = {}
    # (1) self-verification mismatch: corrupt the temp file just before verify
    tmp = Path(tempfile.mkdtemp(prefix=f"rfrv-neg-{tag}-"))
    try:
        cat = build_catalog(tmp)
        mod = load_variant(text, tag)
        orig_verify = mod._verify_snapshot

        def skewed(path, _orig=orig_verify):
            n, d = _orig(path)
            return n, {k: "0" * 64 for k in d}  # silently wrong digests

        mod._verify_snapshot = skewed
        try:
            mod.archive_retired_evidence(cat.config.database_path,
                                         tmp / "manifests", now=NOW)
            out["selfcheck"] = "NO-RAISE"
        except BaseException as exc:  # noqa: BLE001
            out["selfcheck"] = (type(exc).__name__, str(exc))
        finally:
            mod._verify_snapshot = orig_verify
        out["selfcheck_published"] = sorted(
            p.name.replace(".manifest.json", "")
            for p in (tmp / "manifests").rglob("*.manifest.json"))
        out["selfcheck_partials"] = sorted(
            p.name for p in (tmp / "manifests").rglob("*.partial*"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # (2) reconciliation mismatch: delete a span while the stream is running
    tmp = Path(tempfile.mkdtemp(prefix=f"rfrv-neg2-{tag}-"))
    try:
        cat = build_catalog(tmp)
        mod = load_variant(text, tag)
        db = cat.config.database_path
        fired = {"done": False}

        def hook(sql: str) -> None:
            if fired["done"] or "ORDER BY e.span_id" not in sql:
                return
            fired["done"] = True
            con = sqlite3.connect(f"file:{db}", uri=True)
            try:
                con.execute("DELETE FROM evidence_spans WHERE span_id = "
                            "(SELECT span_id FROM evidence_spans LIMIT 1)")
                con.commit()
            finally:
                con.close()

        orig_connect = mod.sqlite3.connect

        def traced(*a, **k):
            con = orig_connect(*a, **k)
            con.set_trace_callback(hook)
            return con

        mod.sqlite3 = types.SimpleNamespace(connect=traced, Row=sqlite3.Row)
        mod.sqlite3.Row = sqlite3.Row
        try:
            mod.archive_retired_evidence(db, tmp / "manifests", now=NOW)
            out["reconcile"] = "NO-RAISE"
        except BaseException as exc:  # noqa: BLE001
            out["reconcile"] = (type(exc).__name__, str(exc))
        finally:
            mod.sqlite3 = sqlite3
        out["reconcile_hook_fired"] = fired["done"]
        out["reconcile_published"] = sorted(
            p.name for p in (tmp / "manifests").rglob("*.json.gz"))
        out["reconcile_partials"] = sorted(
            p.name for p in (tmp / "manifests").rglob("*.partial*"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def b3() -> None:
    print()
    print("=" * 78)
    print("B3  archive END-TO-END (now= supplied) — HEAD body vs worktree body")
    print("=" * 78)
    head_text = git_show("src/company_wiki/source_catalog/archive_retired_evidence.py")
    post_text = (SRC / "archive_retired_evidence.py").read_text(encoding="utf-8")
    pre, post = run_variant(head_text, "pre"), run_variant(post_text, "post")

    for tag, r in (("pre", pre), ("post", post)):
        print(f"\n[{tag}] rows={r['rows_written']}/{r['rows_in_catalog']} "
              f"ok={r['ok']} name={r['name_shape']} bytes={r['archive_bytes']}")
        print(f"      retired spans in harness catalog = {r['harness_retired_spans']} "
              f"(must be >0 or the body is never exercised)")
        print(f"      gz_text_sha256     = {r['gz_text_sha256']}")
        print(f"      actual file sha256 = {r['actual_sha']}")
        print(f"      manifest archive_sha256 = {r['manifest_archive_sha256']}")
        print(f"      dir = {r['dir_shape']}  partials={r['tmp_leftovers']}")
        print(f"      span_ids[{r['row_count']}] first={r['row_span_ids'][:1]}")

    if pre["harness_retired_spans"] == 0 or post["harness_retired_spans"] == 0:
        FAILURES.append("B3 harness invalid: 0 retired spans, body not exercised")
        return

    checks = [
        ("rows written > 0 and == catalog", pre["rows_written"] > 0
         and pre["rows_written"] == pre["rows_in_catalog"]
         and post["rows_written"] == post["rows_in_catalog"]),
        ("ok True both", pre["ok"] is True and post["ok"] is True),
        ("row count equal", pre["row_count"] == post["row_count"]),
        ("row ORDER equal (span_id sequence)", pre["row_span_ids"] == post["row_span_ids"]),
        ("gz text identical (deterministic content)", pre["gz_text_sha256"] == post["gz_text_sha256"]),
        ("archive bytes equal", pre["archive_bytes"] == post["archive_bytes"]),
        ("filename shape equal", pre["name_shape"] == post["name_shape"]),
        ("manifest filename shape equal", pre["manifest_name_shape"] == post["manifest_name_shape"]),
        ("dir shape equal", pre["dir_shape"] == post["dir_shape"]),
        ("no .partial leftovers either run",
         not pre["tmp_leftovers"] and not post["tmp_leftovers"]),
        ("manifest sha == sha of PUBLISHED bytes (pre)",
         pre["manifest_archive_sha256"].upper() == pre["actual_sha"]),
        ("manifest sha == sha of PUBLISHED bytes (post)",
         post["manifest_archive_sha256"].upper() == post["actual_sha"]),
        ("manifest sha is lowercase hex (repo convention, both)",
         pre["manifest_archive_sha256"] == pre["manifest_archive_sha256"].lower()
         and post["manifest_archive_sha256"] == post["manifest_archive_sha256"].lower()),
        ("manifest archive_bytes == real file size (both)",
         pre["manifest"]["archive_bytes"] == pre["archive_bytes"]
         and post["manifest"]["archive_bytes"] == post["archive_bytes"]),
        ("manifest rows_in_archive == real row count (both)",
         pre["manifest"]["rows_in_archive"] == pre["row_count"]
         and post["manifest"]["rows_in_archive"] == post["row_count"]),
        ("manifest ok True + problems [] both",
         pre["manifest_ok"] is True and post["manifest_ok"] is True
         and pre["manifest_problems"] == [] and post["manifest_problems"] == []),
        ("manifest payload identical (path excluded)",
         pre["manifest"] == post["manifest"]),
    ]
    print()
    for label, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            FAILURES.append(f"B3 {label}")

    print("\n  negative paths (fail-closed invariants):")
    npre, npost = negative_paths(head_text, "pre"), negative_paths(post_text, "post")
    for key in ("selfcheck", "reconcile"):
        same = npre[key] == npost[key]
        print(f"  {'PASS' if same else 'FAIL'}  {key}: pre={npre[key]} post={npost[key]}")
        if not same:
            FAILURES.append(f"B3 {key} differs: {npre[key]} vs {npost[key]}")
    for key in ("selfcheck_published", "selfcheck_partials",
                "reconcile_published", "reconcile_partials",
                "reconcile_hook_fired"):
        same = npre[key] == npost[key]
        print(f"  {'PASS' if same else 'FAIL'}  {key}: pre={npre[key]} post={npost[key]}")
        if not same:
            FAILURES.append(f"B3 {key} differs")


def main() -> int:
    b1()
    b2()
    b3()
    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    if FAILURES:
        for f in FAILURES:
            print("FAIL:", f)
        return 1
    print("ALL REVIEW BEHAVIOUR CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
