"""Post-refactor prose fixes (restore promotion-payload docstrings byte-exact):

1. revenue_publication.validate_publication_attestation: drop the added refactor
   paragraph so the original docstring literal survives (literal parity missing=0).
2. model_registry.calculate_registered_model: the promotion payload had NO docstring;
   drop the added one (helper docstrings stay, they are disclosed additions).
"""
from __future__ import annotations

import sys
from pathlib import Path

ISO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:\Users\郑曾波\AppData\Local\Temp\rf-rest-b\iso_after\scripts")

# --- 1. revenue_publication ---
pub = ISO / "revenue_publication.py"
t = pub.read_text(encoding="utf-8")
old_tail = '''    * ``attestation_signature_invalid`` (E14) — Ed25519 verification failed.

    Ratchet refactor (RF-RATCHET-REST-B): the field/format checks live in the
    top-level helpers above; check order, messages, exceptions and the
    verification tail are byte-identical to the promotion payload this file was
    promoted as (bc2bb4a3...).
    """'''
new_tail = '''    * ``attestation_signature_invalid`` (E14) — Ed25519 verification failed.
    """'''
assert t.count(old_tail) == 1, "publication docstring tail anchor"
t = t.replace(old_tail, new_tail, 1)
pub.write_text(t, encoding="utf-8", newline="\n")
print("publication docstring restored")

# --- 2. model_registry ---
reg = ISO / "model_registry.py"
t = reg.read_text(encoding="utf-8")
old_doc = ''') -> list[float]:
    """Pure registered-model calculation: validate, normalize, run, check.

    Ratchet refactor (RF-RATCHET-REST-B): the validation stages live in the
    top-level helpers above; behavior — evaluation order, error types, error
    message strings and returned values — are byte-identical to the promotion
    payload this file was promoted as (62f864b9...).
    """
    spec = _resolve_model_spec(model_id)'''
new_doc = ''') -> list[float]:
    spec = _resolve_model_spec(model_id)'''
assert t.count(old_doc) == 1, "registry main docstring anchor"
t = t.replace(old_doc, new_doc, 1)
reg.write_text(t, encoding="utf-8", newline="\n")
print("registry docstring removed")
