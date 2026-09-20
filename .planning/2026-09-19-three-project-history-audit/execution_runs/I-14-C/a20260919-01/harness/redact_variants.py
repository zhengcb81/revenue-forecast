"""I-14-C r3: measure candidate redactor designs before choosing one.

The r2 review recommended option (a) - "linear candidate ``[A-Za-z0-9_-]+`` for the key,
then validate against the atom table in Python".  That is measured here rather than assumed:
a key-candidate quantifier still backtracks once per start position if the value cannot
match, so variant A1 is compared against a hand-written scanner (A2) and a bounded
quantifier (B), on adversarial shapes.

    python redact_variants.py --bench --out <attempt>/r3/variants.json [--timeout 20]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

MARKER = "SYNTHETIC_AUDIT_TOKEN"
REDACT = "<redacted>"

SINGLE_ATOMS = frozenset({"token", "secret", "password", "passwd", "pwd", "apikey",
                          "credential", "passphrase"})
PAIR_ATOMS = frozenset({("api", "key"), ("secret", "key"), ("private", "key"),
                        ("access", "key"), ("api", "token"), ("access", "token"),
                        ("auth", "token"), ("session", "token"), ("bot", "token"),
                        ("refresh", "token"), ("id", "token"), ("client", "secret")})

_QUOTED_VALUE = r"\"[^\"\r\n]*\"|'[^'\r\n]*'"
_BARE_VALUE = r"[^\s,;&\"'|]+(?:\s+[^\s,;&\"'|]+)*"
_VALUE = r"(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"


def key_is_credential(key: str) -> bool:
    parts = [p for p in re.split(r"[_-]+", key.lower()) if p]
    if not parts:
        return False
    if any(p in SINGLE_ATOMS for p in parts):
        return True
    return any((parts[i], parts[i + 1]) in PAIR_ATOMS for i in range(len(parts) - 1))


# --- variant T2: the r2 nested-star rule (the specimen) ----------------------
_T2_ATOMS = ("token", "secret", "password", "passwd", "pwd", "apikey",
             r"api[_-]?key", r"access[_-]?key", r"private[_-]?key",
             r"auth[_-]?token", r"client[_-]?secret", "credential", "passphrase")
_T2_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?P<key>(?:[A-Za-z0-9]+[_-])*(?:"
    + "|".join(_T2_ATOMS) + r")(?:[_-][A-Za-z0-9]+)*\b\s*[:=]\s*)" + _VALUE)


def redact_t2(text: str) -> str:
    return _T2_PATTERN.sub(lambda m: m.group("key") + REDACT, text)


# --- variant A1: linear key candidate + Python-side validation ---------------
_A1_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?P<key>[A-Za-z0-9_-]+)(?P<sep>\s*[:=]\s*)" + _VALUE)


def redact_a1(text: str) -> str:
    def repl(match: re.Match) -> str:
        if not key_is_credential(match.group("key")):
            return match.group(0)
        return match.group("key") + match.group("sep") + REDACT

    return _A1_PATTERN.sub(repl, text)


# --- variant B: bounded nested quantifier -----------------------------------
_B_ATOMS = _T2_ATOMS
_B_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?P<key>(?:[A-Za-z0-9]+[_-]){0,8}(?:"
    + "|".join(_B_ATOMS) + r")(?:[_-][A-Za-z0-9]+){0,8}\b\s*[:=]\s*)" + _VALUE)


def redact_b(text: str) -> str:
    return _B_PATTERN.sub(lambda m: m.group("key") + REDACT, text)


# --- variant A2: hand-written scanner (find separator, walk back over the key)
_KEY_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
_SEPARATORS = frozenset(":=")
_SPACE = frozenset(" \t")


def redact_a2(text: str) -> str:
    """O(n) scan: for every `:`/`=` find the maximal key run before it, validate, redact."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        if char not in _SEPARATORS:
            out.append(char)
            i += 1
            continue
        # walk back over whitespace then over the key characters
        j = i
        while j > 0 and text[j - 1] in _SPACE:
            j -= 1
        end = j
        while j > 0 and text[j - 1] in _KEY_CHARS:
            j -= 1
        key = text[j:end]
        boundary_ok = j == 0 or text[j - 1] not in _KEY_CHARS
        if not (key and boundary_ok and key_is_credential(key)):
            out.append(char)
            i += 1
            continue
        # redact the value: quoted string, or one bare word
        k = i + 1
        while k < n and text[k] in _SPACE:
            k += 1
        if k < n and text[k] in "\"'":
            quote = text[k]
            close = text.find(quote, k + 1)
            value_end = n if close == -1 else close + 1
        else:
            value_end = k
            while value_end < n and text[value_end] not in " \t,;&\"'|\r\n":
                value_end += 1
        if value_end <= k:
            out.append(char)
            i += 1
            continue
        out.append(text[j:i])          # key + whitespace
        out.append(char)               # the separator
        out.append(text[i + 1:k])      # whitespace after the separator
        out.append(REDACT)
        i = value_end
    return "".join(out)


VARIANTS = {"T2-nested-star": redact_t2, "A1-candidate+python": redact_a1,
            "A2-scanner": redact_a2, "B-bounded": redact_b}

SHAPES = {
    "underscore-segments": lambda k: ("a_" * k) + "=",
    "dash-segments": lambda k: ("a-" * k) + "=",
    "segments-no-separator": lambda k: ("a_" * k)[:-1],
    "segments-then-atom": lambda k: ("a_" * k) + "token=ZZZ",
    "quoted-never-closed": lambda k: ("a_" * k) + '="' + ("b" * 500),
    "long-single-token": lambda k: ("a" * k) + "=",
    "many-empty-pairs": lambda k: "k=" * k,
}
KS = [200, 500, 1000, 2000, 4000, 8000, 16000, 40000]

CORRECTNESS = [
    ("GITHUB_TOKEN=" + MARKER, False), ("my_access_token=" + MARKER, False),
    ("SLACK_BOT_TOKEN=" + MARKER, False), ("AWS_SECRET_ACCESS_KEY=" + MARKER, False),
    ("AWS_ACCESS_KEY_ID=" + MARKER, False), ("AWS_SECRET_ACCESS_KEY_ID=" + MARKER, False),
    ("GH_TOKEN=" + MARKER, False), ("client_secret=" + MARKER, False),
    ("MY_APP_PASSWORD=" + MARKER, False), ("db.passwd=" + MARKER, False),
    ("api_key=" + MARKER, False), ("apikey=" + MARKER, False),
    ("private_key=" + MARKER, False), ("auth_token=" + MARKER, False),
    ("token=" + MARKER, False), ("password: '" + MARKER + "'", False),
    ("GET /x?token=" + MARKER + "&page=2", False),
    ("Authorization: Bearer " + MARKER, False),
    ("Authorization: " + MARKER, False),
    ("upload failed for digest=" + MARKER, True),
    ("monkey=banana", False), ("oauth=abc123", False), ("secretary=alice", False),
    ("tokenizer=whitespace", False), ("keyboard=us", False),
    ("key=value", False), ("pwd=/home/user", None),
    ("document not in catalog: doc-1", False),
    ("stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", False),
    ('{"api_key": "' + MARKER + '"}', None),
]


def _child(variant: str, k: int, shape: str) -> int:
    text = SHAPES[shape](k)
    fn = VARIANTS[variant]
    start = time.perf_counter()
    out = fn(text)
    elapsed = time.perf_counter() - start
    print(json.dumps({"seconds": elapsed, "changed": out != text, "in_len": len(text)}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--one")
    parser.add_argument("--variant")
    parser.add_argument("--shape")
    args = parser.parse_args(argv)
    if args.one is not None:
        return _child(args.variant, int(args.one), args.shape)

    report: dict = {"correctness": {}, "timings": {}, "timeout_seconds": args.timeout}
    for name, fn in VARIANTS.items():
        rows = []
        for text, expect_redacted in CORRECTNESS:
            out = fn(text)
            rows.append({"in": text, "out": out, "marker_survives": MARKER in out,
                         "expect_marker_survives": expect_redacted,
                         "changed": out != text})
        report["correctness"][name] = rows

    here = str(Path(__file__).resolve())
    for name in VARIANTS:
        report["timings"][name] = {}
        for shape in SHAPES:
            report["timings"][name][shape] = {}
            for k in KS:
                argv2 = [sys.executable, "-X", "utf8", "-B", here, "--one", str(k),
                         "--variant", name, "--shape", shape]
                try:
                    proc = subprocess.run(argv2, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          timeout=args.timeout)
                    payload = json.loads(proc.stdout.decode().strip() or "{}")
                    report["timings"][name][shape][str(k)] = round(
                        payload.get("seconds", -1), 4)
                except subprocess.TimeoutExpired:
                    report["timings"][name][shape][str(k)] = "TIMEOUT"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    for name in VARIANTS:
        bad = [r["in"] for r in report["correctness"][name]
               if r["expect_marker_survives"] is not None
               and r["marker_survives"] is not r["expect_marker_survives"]]
        print(json.dumps({"variant": name, "mismatches": bad,
                          "timings": report["timings"][name]},
                         indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
