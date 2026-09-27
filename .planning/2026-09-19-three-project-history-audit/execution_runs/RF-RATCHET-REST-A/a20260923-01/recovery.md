# RF-RATCHET-REST-A — Step 8: RECOVERY (revert 3)

## State discipline
- Production RF sources were **never written** during this attempt (verified: the 3 source
  sha256s re-checked at finalize == binding before-shas; all edits lived in
  `refactored/` iso copies; all pytest/bytecode confined to `%TEMP%\rf-rest-a-iso2`
  (`PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`) and this attempt dir).
- Git was never mutated (read-only `log`/`diff`/`show`); no worktrees, no index writes.

## If the delivered changes must be reverted (3 files)
Delivery is `changes.diff` (exactly 3 files, asserted). Any of:

1. **Not yet applied (normal case):** discard — nothing in `scripts/` was touched.
2. **Applied, want undo:** `git apply -R changes.diff` (or `git checkout -- scripts/forecast/calc.py scripts/generate_input_template.py scripts/research/targets.py` / `git restore …`) — restores the pinned before-shas:
   - `scripts/forecast/calc.py` → `BC4F33D92738029AE1E146E6323A23E818C3ABEB7CDF173C9BCFA4C462B02F79`
   - `scripts/generate_input_template.py` → `F7C57911D5F85204B04D07DE02FDCF9BCDB2315CF0236181CD727986292870B1`
   - `scripts/research/targets.py` → `1C885DEAF4168BACBD7D445EC6E76DA93193132FCE3B6CA67FBED4E6C910C48B`
3. **Byte-exact fallback** (if git history is unavailable): pristine bytes are also kept as
   `pre70dd/` (pre-images, older baseline) — NOT the before-state; the before-state bytes are
   recoverable from the pinned shas via git (`git show HEAD:<path>` at attempt time commit
   `b7a6a116`) or by reverse-applying `changes.diff`.

The frozen ratchet table (`tools/tests/test_complexity_ratchet.py`, sha `EB1A36CF…`) was never
modified — no cap changes to undo. If a scratch table edit ever leaked (it must not), re-verify:
`sha256(tools/tests/test_complexity_ratchet.py) == EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A`.

## Scratch cleanup (safe, TEMP/attempt only)
- `%TEMP%\rf-rest-a-iso2` — iso copy (delete anytime)
- `%TEMP%\rf-rest-a-iso` — killed first copy attempt (delete anytime)
- `<attempt>/scratch/*` — mutation/green scratch roots (copies + patched scratch tables; delete anytime)
- `<attempt>/pre70dd/*.blob` — pre-image bytes (keep as evidence; tiny)
