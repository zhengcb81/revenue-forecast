"""File 3/3: split revenue_core's two over-cap attestation functions into top-level helpers.

Programmatic slicing: every condition, comment and message string is CUT from the original
source text (anchors asserted unique), never retyped. The only new text is control-flow
glue: helper def lines, `return` sentinels, and per-helper local imports of the two
revenue_publication constants (function-local by design: revenue_core <-> revenue_publication
is an import cycle, so these imports can never move to module level).

Targets: _run_attestation_provider 19 -> main <=6; _validate_attestation_response 23 -> main <=6;
all helpers <=6; all other functions untouched.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(sys.argv[1])
text = TARGET.read_text(encoding="utf-8")


def cut(src: str, start_anchor: str, end_anchor: str, label: str) -> str:
    """Slice src[start:end] between two anchors; assert each occurs exactly once."""
    s = src.count(start_anchor)
    e = src.count(end_anchor)
    assert s == 1, f"{label}: start anchor count={s}: {start_anchor[:70]!r}"
    assert e == 1, f"{label}: end anchor count={e}: {end_anchor[:70]!r}"
    i = src.index(start_anchor)
    j = src.index(end_anchor)
    assert i < j, f"{label}: anchor order wrong ({i} >= {j})"
    return src[i:j]


def top_fn(header: str, body: str, footer: str) -> str:
    """Top-level function = header (def + optional prologue) + sliced body + footer."""
    if not body.endswith("\n"):
        body += "\n"
    return header + body + footer + "\n\n\n"


# ------------------------------------------------------------------ block A --
A_START = "def _run_attestation_provider("
A_END = "def _validate_attestation_response("
B_END = "def request_publication_attestation("
a2 = "    resolved = shutil.which(provider) or Path(provider).expanduser()"
a3 = "    try:\n        completed = subprocess.run("
a4 = "    if completed.returncode != 0:"
a5 = "    raw = completed.stdout"
a9 = "    _ATTESTATION_LAST_FAILURE = None"

Ai, Bi, Ci = text.index(A_START), text.index(A_END), text.index(B_END)
assert Ai < Bi < Ci, "block anchors out of order"
blockA = text[Ai:Bi]
blockB = text[Bi:Ci]

a_head = cut(blockA, A_START, a2, "a_head")            # def + docstring + provider-get + absent-if
a_resolve = cut(blockA, a2, a3, "a_resolve")
a_spawn = cut(blockA, a3, a4, "a_spawn")
a_exit = cut(blockA, a4, a5, "a_exit")
a_output = cut(blockA, a5, a9, "a_output")
a_tail = blockA[blockA.index(a9):]                     # clear + return response

# split the exit check: nested if/else classifier -> own helper (CC 7 -> 2 + 6)
y_refuse = '        if "cannot sign" in detail or "no private key" in detail:'
y_ret = "        return None"
assert a_exit.count(y_refuse) == 1, "y_refuse anchor"
assert a_exit.count(y_ret) == 1, "y_ret anchor"
exit_head = a_exit[:a_exit.index(y_refuse)]            # if returncode + detail line
exit_inner = a_exit[a_exit.index(y_refuse):a_exit.index(y_ret)]   # nested if/else records
exit_tail = a_exit[a_exit.index(y_ret):]               # return None (still at 8-indent)
# mechanical dedent of the nested block by one level (4 spaces); messages untouched
exit_inner_dedent = "\n".join(
    (line[4:] if line.startswith("    ") else line) for line in exit_inner.split("\n")
)

# ------------------------------------------------------------------ block B --
b_doc_end = "    from revenue_publication import"
b_missing = "    missing = [field for field in ATTESTATION_RESPONSE_FIELDS if field not in response]"
b_schema = '    if (\n        response["attestation_response_schema_version"]'
b_algo = '    if response["algorithm"] != PUBLICATION_ATTESTATION_ALGORITHM:'
b_fp = '    if (\n        not isinstance(response["fingerprint"], str)'
b_sig = '    if not isinstance(response["signature"], str) or not response["signature"]:'
b_sat = '    if (\n        not isinstance(response["signed_at"], str)'
b_tail_anchor = "    # The signing target is the request object as the provider received it"

b_head = cut(blockB, A_END, b_doc_end, "b_head")       # def line + docstring only
b_fieldset = cut(blockB, b_missing, b_schema, "b_fieldset")
b_echo = cut(blockB, b_schema, b_algo, "b_echo")
b_signer = cut(blockB, b_algo, b_fp, "b_signer")
b_fingerprint = cut(blockB, b_fp, b_sig, "b_fingerprint")
b_signature = cut(blockB, b_sig, b_sat, "b_signature")
b_signed_at = cut(blockB, b_sat, b_tail_anchor, "b_signed_at")
b_tail = blockB[blockB.index(b_tail_anchor):]          # binding comments + verify + return dict

# ------------------------------------------------------- provider helpers (A) --
out: list[str] = []

out.append(top_fn(
    "def _resolve_attestation_provider_file(provider):\n",
    a_resolve,
    "    return resolved",
))
out.append(top_fn(
    "def _spawn_attestation_provider(resolved, request):\n",
    a_spawn,
    "    return completed",
))
out.append(top_fn(
    "def _record_provider_exit_failure(completed, detail):\n",
    exit_inner_dedent,
    "",
))
out.append(top_fn(
    "def _attestation_exit_checked(completed):\n",
    exit_head + "        _record_provider_exit_failure(completed, detail)\n" + exit_tail,
    "    return completed",
))
out.append(top_fn(
    "def _attestation_provider_output(completed):\n",
    a_output,
    "    return response",
))

# ----------------------------------------------------------------- main (A) --
glue_a = (
    "    resolved = _resolve_attestation_provider_file(provider)\n"
    "    if resolved is None:\n"
    "        return None\n"
    "    completed = _spawn_attestation_provider(resolved, request)\n"
    "    if completed is None:\n"
    "        return None\n"
    "    checked = _attestation_exit_checked(completed)\n"
    "    if checked is None:\n"
    "        return None\n"
    "    response = _attestation_provider_output(checked)\n"
    "    if response is None:\n"
    "        return None\n"
)
main_a = a_head + glue_a + a_tail
if not main_a.endswith("\n"):
    main_a += "\n"
out.append(main_a + "\n\n")

# ------------------------------------------------------- response helpers (B) --
out.append(top_fn(
    "def _validate_attestation_field_set(response):\n",
    b_fieldset,
    "",
))
out.append(top_fn(
    "def _validate_attestation_echo(request, response):\n"
    "    from revenue_publication import PUBLICATION_ATTESTATION_SCHEMA_VERSION\n",
    b_echo,
    "",
))
out.append(top_fn(
    "def _validate_attestation_signer(response):\n"
    "    from revenue_publication import PUBLICATION_ATTESTATION_ALGORITHM\n",
    b_signer,
    "",
))
out.append(top_fn(
    "def _validate_attestation_fingerprint(response):\n",
    b_fingerprint,
    "",
))
out.append(top_fn(
    "def _validate_attestation_signature(response):\n",
    b_signature,
    "",
))
out.append(top_fn(
    "def _validate_attestation_signed_at(response):\n",
    b_signed_at,
    "",
))

# ----------------------------------------------------------------- main (B) --
glue_b = (
    "    from revenue_publication import verify_ed25519_signature\n"
    "\n"
    "    _validate_attestation_field_set(response)\n"
    "    _validate_attestation_echo(request, response)\n"
    "    _validate_attestation_signer(response)\n"
    "    _validate_attestation_fingerprint(response)\n"
    "    _validate_attestation_signature(response)\n"
    "    _validate_attestation_signed_at(response)\n"
    "\n"
)
main_b = b_head + glue_b + b_tail
if not main_b.endswith("\n"):
    main_b += "\n"
out.append(main_b + "\n\n")

region = "".join(out)
new_text = text[:Ai] + region + text[Ci:]
TARGET.write_text(new_text, encoding="utf-8", newline="\n")
print(f"region rebuilt: chars {Ai}..{Ci}; new size {TARGET.stat().st_size} B")
