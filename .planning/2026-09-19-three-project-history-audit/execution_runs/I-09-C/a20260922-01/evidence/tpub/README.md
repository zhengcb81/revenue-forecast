--- T-PUB supersession note ---
# T-PUB run records

- 	pub_template.txt — FIRST run of the 4-file T-PUB template: exit=1, 8 failed / 40 passed.
  All 8 failures were ModuleNotFoundError: No module named '_cffi_backend' inside
  	ests/test_attestation.py (Ed25519 import) — an ENVIRONMENT defect of THIS card's
  merged venv (the pure-python site-packages copy missed _cffi_backend.cp313-win_amd64.pyd),
  NOT a product/test failure. Preserved verbatim; not overwritten.
- 	pub_template_rerun.txt — after copying the missing extension binary from the sibling
  attempt venv (same base interpreter 3.13.9), same argv/env: the honest rerun.
- 	pub_i09b.txt — 	ests/test_i09b_commit_protocol.py (the new node bound this card): exit=0.
- Identity proof that the failing tests are THIS tree's bytes: my 	ests/test_attestation.py
  sha256 = 17934e28a894ff1d3d95cb14d1665fb3ba27f7e6c587d916f2cdd4d2f547f5c4 = I-09-B's copy;
  traceback line numbers 466/355 match this file exactly (pytest's shortened display path is cosmetic).
