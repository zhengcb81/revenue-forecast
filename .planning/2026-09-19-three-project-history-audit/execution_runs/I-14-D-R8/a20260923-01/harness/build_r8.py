"""WC-1 / I-14-D-R8 build: isolated copies + literal-asserted fixes + r8 harness rows.

NINE-STEP step 3/9.  Reproducible from the pinned inputs in binding.json:

  1. iso/r8_base  <- copy of I-14-D iso/product_narrow_r6 (src tree, no __pycache__)
                     pin-checked: observability.py == 2f644994...
  2. iso/r8_fixed <- copy of r8_base with FIX-1 (REM-06 key predicate) and
                     FIX-2 (F-REV-R3-05 after-break value delimiter) applied by
                     BYTE-LEVEL literal replacement, each asserted to occur
                     EXACTLY once; py_compile-checked.
  3. harness/run_i14d_oracle_r8.py   <- copy of run_i14d_oracle_r6.py  + 17 frozen rows
     harness/run_rule_table_i14d_r8.py <- copy of run_rule_table_i14d_r6.py + 18 frozen rows
     (row expectations verbatim from oracle.md sections 2-3; anchor = the last r7 row).

Run:  python -B harness/build_r8.py
Writes ONLY inside this attempt directory.  CRLF/LF of each target file is detected
and preserved (byte-level replacement).
"""

from __future__ import annotations

import hashlib
import py_compile
import shutil
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent          # .../I-14-D-R8/a20260923-01
I14D = ATT.parent.parent / "I-14-D" / "a20260919-01"  # sealed predecessor attempt
SRC_R6 = I14D / "iso" / "product_narrow_r6" / "src"
HARNESS_R6 = I14D / "harness"
OBS_REL = Path("company_wiki") / "source_catalog" / "observability.py"

BASE_PIN = "2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464"
ORACLE_BASE_PIN = "85a1b064fa90616a04f0ae34f618576af073bccbaff02b01c5c6ebeb70813f30"
RULE_BASE_PIN = "8f5feffddb6f2931942bb76ab0aa213e82d3fa23f645d0206d063f397b162638"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_tree_clean(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def detect_nl(data: bytes) -> str:
    return "\r\n" if b"\r\n" in data else "\n"


def apply_edits(path: Path, edits: list[tuple[str, str]]) -> dict:
    """Byte-level literal replacements; each old block must occur exactly once."""
    original = path.read_bytes()
    nl = detect_nl(original)
    text = original.decode("utf-8")
    applied = []
    for old, new in edits:
        old_t = old.replace("\n", nl)
        new_t = new.replace("\n", nl)
        count = text.count(old_t)
        if count != 1:
            raise SystemExit(f"EDIT ANCHOR FAILED ({count} != 1) in {path}: {old[:80]!r}")
        text = text.replace(old_t, new_t)
        applied.append({"old_sha256": sha(old_t.encode("utf-8")),
                        "new_sha256": sha(new_t.encode("utf-8"))})
    path.write_bytes(text.encode("utf-8"))
    return {"before_sha256": sha(original), "after_sha256": sha(path.read_bytes()),
            "bytes_before": len(original), "bytes_after": path.stat().st_size,
            "newline": nl.strip("\r"), "edits": applied}


# ---------------------------------------------------------------------------
# FIX-1 (REM-06 / WC-1 ①): digit-suffixed credential keys
# ---------------------------------------------------------------------------
FIX1_CONST_OLD = '''_KEY_COMPONENT_SPLIT = re.compile(r"[_-]+")
'''
FIX1_CONST_NEW = '''_KEY_COMPONENT_SPLIT = re.compile(r"[_-]+")
# r8 / REM-06: trailing digit run of a key component -- `token2` -> `token`.
_KEY_TRAILING_DIGITS = re.compile(r"\\d+$")
'''

FIX1_FUNC_OLD = '''def key_is_credential(key: str) -> bool:
    """True when *key* (as written in the text) is a credential-shaped name."""
    parts = [part for part in _KEY_COMPONENT_SPLIT.split(key.lower()) if part]
    if not parts:
        return False
    if any(part in _SINGLE_ATOMS for part in parts):
        return True
    return any(
        (parts[index], parts[index + 1]) in _PAIR_ATOMS
        for index in range(len(parts) - 1)
    )
'''
FIX1_FUNC_NEW = '''def key_is_credential(key: str) -> bool:
    """True when *key* (as written in the text) is a credential-shaped name.

    r8 / REM-06 (WC-1 1): a component may carry a trailing NUMERIC suffix --
    ``token2``/``secret2``/``password2``/``api_key2`` -- the way env dumps number
    their slots.  Each split component has its trailing digit run stripped before
    the atom-table lookup, so the digit family resolves through the SAME split
    rules as the plain family (single atoms and adjacent pairs alike); a
    component that is nothing but digits is left as-is.  Every key the pre-r8
    predicate accepted is still accepted (a pure-letter component is its own
    normalization), so the predicate only ADDS the digit-suffixed family --
    bidirectional sweep evidence in execution_runs/I-14-D-R8/a20260923-01/
    evidence/key_domain_sweep.json (old-minus-new empty, new-minus-old exactly
    the digit-suffixed credential family within the frozen domain).
    """
    parts = [part for part in _KEY_COMPONENT_SPLIT.split(key.lower()) if part]
    if not parts:
        return False
    parts = [_KEY_TRAILING_DIGITS.sub("", part) or part for part in parts]
    if any(part in _SINGLE_ATOMS for part in parts):
        return True
    return any(
        (parts[index], parts[index + 1]) in _PAIR_ATOMS
        for index in range(len(parts) - 1)
    )
'''

# ---------------------------------------------------------------------------
# FIX-2 (F-REV-R3-05 / WC-1 ②): after-break value may start with a delimiter
# ---------------------------------------------------------------------------
FIX2_OLD = '''_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_PREBREAK_TOKEN + r")[ \\t]*"
                      r"(?:(?:\\r?\\n)[ \\t]*)+"
                      r"(?:" + _AUTH_BARE_VALUE + r"+|\\"[^\\"\\r\\n]*\\"|'[^'\\r\\n]*')")
'''
FIX2_NEW = '''# r8 / F-REV-R3-05 (WC-1 2): after the break run the VALUE may now START with a
# value delimiter -- the six forms `,<secret>` `;<secret>` `&<secret>`
# `|<secret>` `"<secret>` `'<secret>` (reviewer_report_r3.md F-REV-R3-05, all
# six measured in the clear).  The quoted alternatives are tried FIRST, so a
# TERMINATED quoted value still matches whole and byte-identically; the optional
# `[,;&|"' ]*` prefix is consumed as part of the redacted value -- fail-closed
# direction, priced by the over-auth-break-* rows (`Authorization: Bearer` +
# newline + `,doc=17` loses doc=17 exactly like the registered F-REV-R2-02 cost).
# Scope (frozen in oracle.md 1/4a): ONLY after the break run -- single-line
# `Authorization: Bot,<secret>` keeps its bounded behaviour (oracle N29) -- and
# only when the delimiter is IMMEDIATELY followed by the token (delimiter+space
# stays open); value-start `\\r \\v \\f` after the break stays outside this row set.
_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_PREBREAK_TOKEN + r")[ \\t]*"
                      r"(?:(?:\\r?\\n)[ \\t]*)+"
                      r"(?:\\"[^\\"\\r\\n]*\\"|'[^'\\r\\n]*'|[,;&|\\"']*" + _AUTH_BARE_VALUE + r"+)")
'''

PRODUCT_EDITS = [("const", FIX1_CONST_OLD, FIX1_CONST_NEW),
                 ("func", FIX1_FUNC_OLD, FIX1_FUNC_NEW),
                 ("auth", FIX2_OLD, FIX2_NEW)]

# ---------------------------------------------------------------------------
# Oracle rows (17) + rule-table rows (18) — verbatim from oracle.md §2/§3
# ---------------------------------------------------------------------------
ORACLE_ROWS = r'''
    # ---- r8 / WC-1 (I-14-D-R8 a20260923-01): the four REGISTRY-CLOSURE residuals ----
    # Expectations FROZEN in execution_runs/I-14-D-R8/a20260923-01/oracle.md (sha sidecar
    # c6cbf869...) BEFORE any run of this card; lengths are pure arithmetic
    # (harness/freeze_arithmetic.py).  1 = REM-06 digit-suffixed credential keys;
    # 2 = F-REV-R3-05 the six after-break value-delimiter forms + the single-line scope
    # guard; 3 = F-REV-R5-08 marker payload row for the C10 R3a shape (whose presence
    # completes F-REV-R3-07's both_marker_and_non_marker promise at row level; domain:
    # oracle.md 4c/4d).  RED on r8_base: N14-N18 + N23-N28 only; GREEN on r8_fixed: all.
    ("N14-digit-token2-pair", "narrow_must",
     "token=" + M + " token2=" + S39 + " b=2",
     "token=" + R + " token2=" + R + " b=2",
     ["b=2"], 38, ""),
    ("N15-digit-secret2", "narrow_must",
     "secret2=" + S39, "secret2=" + R, [], 18, ""),
    ("N16-digit-password2", "narrow_must",
     "password2=" + M, "password2=" + R, [], 20, ""),
    ("N17-digit-api-key2", "narrow_must",
     "api_key2=" + M, "api_key2=" + R, [], 19, ""),
    ("N18-digit-env-secret2", "narrow_must",
     "export SECRET2=" + S39, "export SECRET2=" + R, [], 25, ""),
    ("N19-untouched-oauth2", "keep_must",
     "oauth2=abc123 request_id=req-1", "oauth2=abc123 request_id=req-1", [], 30, ""),
    ("N20-untouched-monkey2", "keep_must",
     "monkey2=banana", "monkey2=banana", [], 14, ""),
    ("N21-untouched-secretary2", "keep_must",
     "secretary2=alice", "secretary2=alice", [], 16, ""),
    ("N22-untouched-tokenizer2", "keep_must",
     "tokenizer2=whitespace", "tokenizer2=whitespace", [], 21, ""),
    ("N23-auth-break-comma", "narrow_must",
     "Authorization: Bot\n," + S39, "Authorization: " + R, [], 25, ""),
    ("N24-auth-break-semicolon", "narrow_must",
     "Authorization: Bot\n;" + S39, "Authorization: " + R, [], 25, ""),
    ("N25-auth-break-ampersand", "narrow_must",
     "Authorization: Bot\n&" + S39, "Authorization: " + R, [], 25, ""),
    ("N26-auth-break-pipe", "narrow_must",
     "Authorization: Bot\n|" + S39, "Authorization: " + R, [], 25, ""),
    ("N27-auth-break-dquote", "narrow_must",
     'Authorization: Bot\n"' + S39, "Authorization: " + R, [], 25, ""),
    ("N28-auth-break-squote", "narrow_must",
     "Authorization: Bot\n'" + S39, "Authorization: " + R, [], 25, ""),
    ("N29-auth-sameline-comma-kept", "keep_must",
     "Authorization: Bot," + S39,
     "Authorization: " + R + "," + S39, [], 65, ""),
    ("R3c-two-token-then-wrap-marker", "registered_open",
     "Authorization: Bearer abc\n" + M,
     "Authorization: " + R + "\n" + M,
     [M], 47,
     "Authorization: " + R + "\n" + M),
]
'''

RULE_ROWS = r'''
    # ---- r8 / WC-1 (I-14-D-R8 a20260923-01): 18 new rows, expectations FROZEN in
    # execution_runs/I-14-D-R8/a20260923-01/oracle.md section 3 (95 -> 113 rows).
    # 1 = REM-06 digit-suffixed keys (+4 untouched counters = the over-redaction PRICE
    # of the key widening: monkey/oauth/secretary/tokenizer + digit suffix MUST stay
    # untouched); 2 = F-REV-R3-05 the six after-break value-delimiter forms are now
    # redacted (+2 over_redaction rows pricing the fail-closed cost on diagnostic keys);
    # 3 = F-REV-R5-08 marker payload row for the C10 R3a shape -- kind registered_open,
    # so registered_open_leaking (marker path) now SEES the marker form; with it the
    # F-REV-R3-07 both_marker_and_non_marker promise is met at row level (domain:
    # oracle.md 4c/4d).  RED on r8_base: the 13 fixed-behaviour rows; GREEN on
    # r8_fixed: all 113 (rc stays 3 / negative BY DESIGN since r3: registered_open
    # rows leak as declared -- no rc 0 claim is made for the rule table).
    ("cred-digit-token2-pair", "token=" + MARKER + " token2=" + REVIEWER_SECRET + " b=2",
     "token=" + R + " token2=" + R + " b=2", "credential"),
    ("cred-digit-secret2", "secret2=" + REVIEWER_SECRET, "secret2=" + R, "credential"),
    ("cred-digit-password2", "password2=" + MARKER, "password2=" + R, "credential"),
    ("cred-digit-api-key2", "api_key2=" + MARKER, "api_key2=" + R, "credential"),
    ("cred-digit-env-secret2", "export SECRET2=" + REVIEWER_SECRET,
     "export SECRET2=" + R, "credential"),
    ("untouched-oauth2", "oauth2=abc123 request_id=req-1",
     "oauth2=abc123 request_id=req-1", "untouched"),
    ("untouched-monkey2", "monkey2=banana", "monkey2=banana", "untouched"),
    ("untouched-secretary2", "secretary2=alice", "secretary2=alice", "untouched"),
    ("untouched-tokenizer2", "tokenizer2=whitespace", "tokenizer2=whitespace", "untouched"),
    ("cred-auth-break-comma-secret", "Authorization: Bot\n," + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-break-semicolon-secret", "Authorization: Bot\n;" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-break-ampersand-secret", "Authorization: Bot\n&" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-break-pipe-secret", "Authorization: Bot\n|" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-break-dquote-secret", 'Authorization: Bot\n"' + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-break-squote-secret", "Authorization: Bot\n'" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("over-auth-break-comma-then-key", "Authorization: Bearer\n,doc=17",
     "Authorization: " + R, "over_redaction"),
    ("over-auth-break-dquote-then-key", 'Authorization: Bearer\n"doc=17',
     "Authorization: " + R, "over_redaction"),
    ("open-two-token-then-wrap-marker", "Authorization: Bearer abc\n" + MARKER,
     "Authorization: " + R + "\n" + MARKER, "registered_open"),
]
'''

ORACLE_ANCHOR = r'''     "Authorization: " + R + "\ft\n" + M + "\n" + S39),
]'''
RULE_ANCHOR = r'''     "Authorization: " + R + "\ft\n" + MARKER + "\n" + REVIEWER_SECRET, "registered_open"),
]'''


def extend_rows(src: Path, dst: Path, anchor: str, rows: str) -> dict:
    data = src.read_bytes()
    if sha(data) not in (ORACLE_BASE_PIN, RULE_BASE_PIN):
        raise SystemExit(f"unexpected base harness sha: {src}")
    nl = detect_nl(data)
    text = data.decode("utf-8")
    anchor_t = anchor.replace("\n", nl)
    if text.count(anchor_t) != 1:
        raise SystemExit(f"row anchor failed in {src}: {anchor[:60]!r}")
    insert = rows.rstrip("\n").replace("\n", nl) + nl
    # splice rows in place of the anchor's trailing "]" so the anchor line stays
    head, _, tail = text.partition(anchor_t)
    new_text = head + anchor_t[: -len("]".replace("\n", nl))] + insert + tail
    dst.write_bytes(new_text.encode("utf-8"))
    return {"base_sha256": sha(data), "new_sha256": sha(dst.read_bytes()),
            "bytes_base": len(data), "bytes_new": dst.stat().st_size}


def main() -> int:
    report: dict = {"steps": []}

    # -- pins ---------------------------------------------------------------
    base_obs = SRC_R6 / OBS_REL
    if sha(base_obs.read_bytes()) != BASE_PIN:
        raise SystemExit("r6 base observability pin mismatch")
    report["steps"].append({"pin_r6_tree": BASE_PIN, "ok": True})

    # -- 1. r8_base ---------------------------------------------------------
    copy_tree_clean(SRC_R6, ATT / "iso" / "r8_base")
    base_copy = ATT / "iso" / "r8_base" / OBS_REL
    if sha(base_copy.read_bytes()) != BASE_PIN:
        raise SystemExit("r8_base copy pin mismatch")
    report["steps"].append({"iso_r8_base": "copied, observability.py pin verified"})

    # -- 2. r8_fixed --------------------------------------------------------
    copy_tree_clean(ATT / "iso" / "r8_base", ATT / "iso" / "r8_fixed")
    fixed_obs = ATT / "iso" / "r8_fixed" / OBS_REL
    edits = [(name, old, new) for name, old, new in PRODUCT_EDITS]
    res = apply_edits(fixed_obs, [(o, n) for _n, o, n in edits])
    res["edit_names"] = [n for n, _o, _n in edits]
    py_compile.compile(str(fixed_obs), doraise=True)
    res["py_compile"] = "ok"
    report["steps"].append({"iso_r8_fixed": res})

    # -- 3. harness copies --------------------------------------------------
    h = ATT / "harness"
    report["steps"].append({"oracle_r8": extend_rows(
        HARNESS_R6 / "run_i14d_oracle_r6.py",
        h / "run_i14d_oracle_r8.py", ORACLE_ANCHOR, ORACLE_ROWS)})
    report["steps"].append({"rule_r8": extend_rows(
        HARNESS_R6 / "run_rule_table_i14d_r6.py",
        h / "run_rule_table_i14d_r8.py", RULE_ANCHOR, RULE_ROWS)})
    for name in ("run_i14d_oracle_r8.py", "run_rule_table_i14d_r8.py"):
        py_compile.compile(str(h / name), doraise=True)
    report["steps"].append({"harness_py_compile": "ok"})

    import json
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
