#!/usr/bin/env python3
"""REM79-MECHANIZATION corpus builder (attempt-local tooling).

Extracts verbatim lines from the current carriers (READ-ONLY), writes the frozen
corpus files for the REM-79 domain-assertion oracle, and emits
evidence/corpus_manifest.json with source file hashes, source line numbers and
payload hashes.

This script performs NO check logic: extraction + hashing only. The frozen
expectations are hand-declared in oracle_table.json / oracle.md.
"""
import hashlib
import json
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ATTEMPT = HARNESS.parent
PLAN = ATTEMPT.parents[2]  # a20260922-01 -> REM79-MECHANIZATION -> execution_runs -> PLAN
CORPUS = ATTEMPT / "corpus"
EVID = ATTEMPT / "evidence"

REVIEW_I14D = "execution_runs/I-14-D/a20260919-01/review.md"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_lines(rel: str):
    """Return (whole-file sha256, list of lines with \\r stripped)."""
    raw = (PLAN / rel).read_bytes()
    text = raw.decode("utf-8")
    lines = [ln[:-1] if ln.endswith("\r") else ln for ln in text.split("\n")]
    if lines and lines[-1] == "":
        lines.pop()  # trailing newline artefact
    return sha256_bytes(raw), lines


def main() -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "rem79-corpus-manifest/1",
        "built_by": "harness/build_corpus.py",
        "note": "extraction only; no check logic runs in this step",
        "source_files": {},
        "corpus_files": {},
        "samples": [],
    }

    # cache of sources -------------------------------------------------------
    cache = {}

    def src(rel: str):
        if rel not in cache:
            digest, lns = load_lines(rel)
            cache[rel] = (digest, lns)
            manifest["source_files"][rel] = {
                "sha256_at_extraction": digest,
                "bytes_at_extraction": (PLAN / rel).stat().st_size,
            }
        return cache[rel]

    # ------------------------------------------------------------------ POS 1
    payload_lines = {}
    i14d_sha, i14d_lines = src(REVIEW_I14D)
    p1 = i14d_lines[348]  # 1-based line 349
    f = "corpus/pos_i14d_review_L349.md"
    body = [
        "<!-- REM79 corpus POSITIVE-1 (historical FALSE case): I-14-D review.md line 349, "
        "r6-era bytes; F-REV-R6-02 site 1; frozen expectation: FLAG line 4 -->",
        "<!-- src: execution_runs/I-14-D/a20260919-01/review.md line 349 (1-based), extracted "
        "verbatim at corpus build; source file sha256 recorded in evidence/corpus_manifest.json -->",
        "",
        p1,
    ]
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    payload_lines[f] = 4
    manifest["samples"].append({
        "corpus_file": f, "payload_line": 4, "kind": "positive_historical",
        "source_file": REVIEW_I14D, "source_line": 349,
        "source_file_sha256": i14d_sha,
        "payload_sha256": sha256_bytes(p1.encode("utf-8")),
        "provenance": "F-REV-R6-02 site 1: r6-era unscoped universal headline (byte-preserved inside review.md's r6 prefix)",
    })

    # ------------------------------------------------------------------ POS 2
    tp_sha, tp_lines = src("task_plan.md")
    original = tp_lines[1993]  # 1-based line 1994 (live, parent-fixed)
    start = original.index("（**域：")
    end = original.index("落于本行**）") + len("落于本行**）")
    p2 = original[:start] + original[end:]
    assert "域" not in p2, "domain parenthetical not fully stripped"
    assert "每一个" in p2, "universal marker lost during reconstruction"
    f = "corpus/pos_round76_original.md"
    body = [
        "<!-- REM79 corpus POSITIVE-2 (historical FALSE case): task_plan.md Round 76 headline "
        "sentence BEFORE the same-line domain fix; F-REV-R6-02 site 3; frozen expectation: FLAG line 4 -->",
        "<!-- reconstructed: task_plan.md line 1994 minus the parent-applied parenthetical "
        "domain （**域：…落于本行**）; reconstruction rule + source sha256 in evidence/corpus_manifest.json -->",
        "",
        p2,
    ]
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    payload_lines[f] = 4
    manifest["samples"].append({
        "corpus_file": f, "payload_line": 4, "kind": "positive_historical",
        "source_file": "task_plan.md", "source_line": 1994,
        "source_file_sha256": tp_sha,
        "reconstruction": "live line 1994 with the substring （**域：…落于本行**） deleted "
                          "(the parenthetical that F-REV-R6-02 site 3 correction added); "
                          "the remainder is the Round 76 r6-era sentence",
        "original_line_sha256": sha256_bytes(original.encode("utf-8")),
        "payload_sha256": sha256_bytes(p2.encode("utf-8")),
    })

    # ------------------------------------------------------------------ POS 3
    p3 = ("Post-fix verification: `fix_A_and_B` leaves only the registered `C10` residual; "
          "no other residual form was inspected.")
    f = "corpus/pos_synth_frev_r406.md"
    body = [
        "<!-- REM79 corpus POSITIVE-3 (synthetic): mirrors the F-REV-R4-06 sentence shape — "
        "a probe-priced result written as a general claim; frozen expectation: FLAG line 4 -->",
        "<!-- synthetic author: REM79-MECHANIZATION implementer; historical template quoted at "
        "REMEDIATION_REGISTER.md line 283 (the C4.5 sentence) -->",
        "",
        p3,
    ]
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    payload_lines[f] = 4
    manifest["samples"].append({
        "corpus_file": f, "payload_line": 4, "kind": "positive_synthetic",
        "mirrors": "F-REV-R4-06 / oracle.md C4.5 shape: 'leaves only the registered C10 residual'",
        "template_quoted_at": "REMEDIATION_REGISTER.md:283",
        "payload_sha256": sha256_bytes(p3.encode("utf-8")),
    })

    # ------------------------------------------------------------------ POS 4
    p4 = ("On the r5 measurement set, `redact_class_v5` closes the whole family at zero cost — "
          "the fix is complete.")
    f = "corpus/pos_synth_frev_r502.md"
    body = [
        "<!-- REM79 corpus POSITIVE-4 (synthetic): mirrors the F-REV-R5-02 sentence shape — "
        "19 probes (4 of family) priced as full closure at no charge; frozen expectation: FLAG line 4 -->",
        "<!-- synthetic author: REM79-MECHANIZATION implementer; original sentence quoted at "
        "task_plan.md Round 75/76 lineage and findings.md Round 74 lineage -->",
        "",
        p4,
    ]
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    payload_lines[f] = 4
    manifest["samples"].append({
        "corpus_file": f, "payload_line": 4, "kind": "positive_synthetic",
        "mirrors": "F-REV-R5-02 shape: 'closes the whole family at zero cost'",
        "template_quoted_at": "task_plan.md:1976 (Round 76 correction of Round 75)",
        "payload_sha256": sha256_bytes(p4.encode("utf-8")),
    })

    # ------------------------------------------------------------- NEG-A (domain)
    neg_a_src = [
        ("task_plan.md", 1994),
        ("task_plan.md", 1977),
        ("task_plan.md", 1952),
        ("task_plan.md", 2018),
        ("findings.md", 503),
        ("findings.md", 528),
        ("findings.md", 544),
        ("progress.md", 800),
        ("REMEDIATION_REGISTER.md", 331),
        ("REMEDIATION_REGISTER.md", 291),
        (REVIEW_I14D, 382),
        (REVIEW_I14D, 415),
    ]
    oracle_own = [
        "凡含「只有 / 全部 / 没有 / 整个族 / 零代价 / 无一 / 每一个」或 EN `only` / `all` / `none` / "
        "`every` / `whole family` / `zero cost` 形态的断言行，必须同行带域字段（域：本 oracle 冻结词表，§3）。",
        "本 oracle 的每一个期望行都同时登记 file、line 与 expect，缺失同行域的登记按未验证处理"
        "（域：§5 期望表；机器表 = oracle_table.json）。",
    ]
    f = "corpus/neg_domain_lines.md"
    body = [
        "<!-- REM79 corpus NEGATIVE-A: lines pairing a universal quantifier with a same-line "
        "domain qualifier; frozen expectation: zero flags (oracle table below) -->",
        "",
    ]
    samples = []
    for rel, ln in neg_a_src:
        _, lns = src(rel)
        samples.append((f"<!-- src: {rel}:{ln} -->", lns[ln - 1],
                        {"source_file": rel, "source_line": ln}))
    for idx, txt in enumerate(oracle_own, start=1):
        samples.append(
            (f"<!-- origin: this oracle's own text; appears verbatim in oracle.md section 3 as line O{idx} -->",
             txt, {"source_file": "oracle.md (self)", "source_line": f"O{idx}"}))
    for comment, payload, meta in samples:
        body.append(comment)
        body.append(payload)
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    for i, (comment, payload, meta) in enumerate(samples):
        lineno = 4 + 2 * i
        manifest["samples"].append({
            "corpus_file": f, "payload_line": lineno, "kind": "negative_domain",
            "payload_sha256": sha256_bytes(payload.encode("utf-8")), **meta,
        })

    # ---------------------------------------------------------- NEG-B (no marker)
    neg_b_src = [
        ("task_plan.md", 1970),
        ("task_plan.md", 1972),
        ("task_plan.md", 1979),
        ("task_plan.md", 1988),
        ("task_plan.md", 1996),
        ("task_plan.md", 1999),
        ("task_plan.md", 2012),
        ("task_plan.md", 2004),
        ("task_plan.md", 2010),
        (REVIEW_I14D, 343),
        (REVIEW_I14D, 347),
        (REVIEW_I14D, 397),
        (REVIEW_I14D, 404),
    ]
    f = "corpus/neg_no_marker_lines.md"
    body = [
        "<!-- REM79 corpus NEGATIVE-B: lines that carry no universal-quantifier marker; frozen "
        "expectation: zero flags (oracle table below) -->",
        "",
    ]
    samples = []
    for rel, ln in neg_b_src:
        _, lns = src(rel)
        samples.append((f"<!-- src: {rel}:{ln} -->", lns[ln - 1]))
    for comment, payload in samples:
        body.append(comment)
        body.append(payload)
    (ATTEMPT / f).write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    for i, (comment, payload) in enumerate(samples):
        lineno = 4 + 2 * i
        manifest["samples"].append({
            "corpus_file": f, "payload_line": lineno, "kind": "negative_no_marker",
            "payload_sha256": sha256_bytes(payload.encode("utf-8")),
            "source_file": neg_b_src[i][0], "source_line": neg_b_src[i][1],
        })

    # ------------------------------------------------------------- corpus hashes
    for path in sorted(CORPUS.glob("*.md")):
        raw = path.read_bytes()
        rel = f"corpus/{path.name}"
        n_lines = len(raw.decode("utf-8").split("\n"))
        manifest["corpus_files"][rel] = {
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "line_count": n_lines,
            "payload_line": payload_lines.get(rel),
        }

    (EVID / "corpus_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"corpus files written: {len(manifest['corpus_files'])}")
    print(f"samples extracted:    {len(manifest['samples'])}")
    for rel, meta in manifest["corpus_files"].items():
        print(f"  {rel}  sha256={meta['sha256'][:16]}…  lines={meta['line_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
