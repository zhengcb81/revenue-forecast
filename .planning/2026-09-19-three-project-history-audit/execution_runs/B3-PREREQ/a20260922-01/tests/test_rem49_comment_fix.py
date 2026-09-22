"""REM-49 / CF-1 — property test: the call-site comment is corrected, with ZERO
behaviour delta.

Baseline (B3's accepted bytes, read-only): b3_reference/iso/fixed/rf_scripts/source_preparation.py
Subject (this attempt's copy)          : iso/fixed2/rf_scripts/source_preparation.py

Properties:
  C0  the files differ at all (a fix happened);
  C1  EVERY changed line in the byte diff is comment-only (both sides `#…`);
  C2  `tokenize` streams are identical outside COMMENT tokens AND `ast.dump`
      is byte-identical  => zero behaviour delta at both the token and AST level;
  C3  both files `py_compile` cleanly;
  C4  the doubly-wrong wording is gone from the subject and the corrected
      wording (reviewer §4 suggested text) is present; the baseline still
      carries the old wording (fixture sanity).
"""
from __future__ import annotations

import ast
import difflib
import io
import py_compile
import tokenize
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
BASELINE = ATTEMPT / "b3_reference" / "iso" / "fixed" / "rf_scripts" / "source_preparation.py"
SUBJECT = ATTEMPT / "iso" / "fixed2" / "rf_scripts" / "source_preparation.py"

OLD_PHRASE = "the DAG closure of the non-reusable roles"
NEW_PHRASE = "requested missing roles + their non-reusable ancestors"


def test_c0_the_comment_fix_changed_the_file():
    assert BASELINE.is_file() and SUBJECT.is_file()
    assert BASELINE.read_bytes() != SUBJECT.read_bytes(), (
        "no change at all: the REM-49 comment fix is missing")


def test_c1_every_changed_line_is_comment_only():
    base = BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
    subj = SUBJECT.read_text(encoding="utf-8").splitlines(keepends=True)
    changes = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, subj).get_opcodes():
        if tag == "equal":
            continue
        changes += 1
        for line in base[i1:i2] + subj[j1:j2]:
            assert line.strip().startswith("#"), (
                f"non-comment line touched ({tag}): {line!r}")
    assert changes > 0, "expected at least one changed hunk"


def test_c2_tokens_and_ast_are_identical():
    base_src = BASELINE.read_text(encoding="utf-8")
    subj_src = SUBJECT.read_text(encoding="utf-8")
    # AST: comments never enter the AST, so identical AST == zero behaviour delta.
    assert ast.dump(ast.parse(base_src)) == ast.dump(ast.parse(subj_src)), (
        "AST changed — this is no longer a comment-only fix")
    # Token stream: everything except COMMENT tokens must match exactly.
    def tokens(src: str):
        return [
            (tok.type, tok.string)
            for tok in tokenize.generate_tokens(io.StringIO(src).readline)
            if tok.type != tokenize.COMMENT
        ]
    assert tokens(base_src) == tokens(subj_src), (
        "token stream (minus comments) changed — behaviour-bearing content differs")


def test_c3_both_files_compile(tmp_path: Path):
    for index, path in enumerate((BASELINE, SUBJECT)):
        py_compile.compile(
            str(path), cfile=str(tmp_path / f"sp_{index}.pyc"), doraise=True)


def test_c4_comment_wording_is_corrected():
    base_src = BASELINE.read_text(encoding="utf-8")
    subj_src = SUBJECT.read_text(encoding="utf-8")
    assert OLD_PHRASE in base_src, "fixture broken: baseline lost the old wording"
    assert OLD_PHRASE not in subj_src, (
        "REM-49 not fixed: the doubly-wrong wording is still present")
    assert NEW_PHRASE in subj_src, (
        f"REM-49 not fixed: corrected wording {NEW_PHRASE!r} is absent")
