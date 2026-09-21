# I-14-D decision.md

Status: **one scope sub-decision recorded (D1); everything else is implementer-level
and was resolved inside the frozen oracle.** The implementer does not self-accept;
`handoff.json` status stays `review_pending`.

## D1 — what "single token" means on the authorization/bearer path

The card prescribes: "裸值只吃**单个 token**（遇空白即停）". Applied verbatim to the
**assignment scanner** (`token=<value>`), that is exactly the fix for the measured
C13 defect (F-I14C-R4-02: 112 chars in → 34 out) and is what this card implements.

Applied verbatim to the **authorization/bearer regex** it would LEAK:

- `Authorization: Bearer <secret>` — value = `Bearer` only → the secret survives.
- `authorization: token <secret>` — same failure.

The r5-final code documents why the auth value is multi-word (observability.py
lines 273-277): the real shapes `Authorization: Bearer <secret>` /
`Authorization: token <secret>` put a scheme word in front of the secret, and five
frozen I-14-C rule-table entries plus `REDACT_CASES` pin that those forms keep
redacting. I-14-D's negative clause also requires 纯合成 marker 必须仍被脱敏.

### Options considered

1. **(CHOSEN) Assignment path: strict single token (stop at ANY whitespace,
   including newlines). Authorization path: token run bounded to ONE LINE
   (joins are `[ \t]+`, never `\n`/`\r`), still able to carry the one scheme word.**
   - Fixes C13 on BOTH paths: an auth value can no longer cross a newline, so
     `Authorization: Bearer <m>\ndoc=17\nstage=…` keeps its diagnostics
     (oracle N5; mutation M2 proves the line-bound is load-bearing).
   - Every I-14-C auth expectation stays byte-identical on single-line inputs:
     the 5 auth rule-table rows, `FIDELITY_CASES` auth pairs, the E1 baseline
     (`Authorization: <redacted>`, len 25) — oracle N5b freezes this keep.
   - Rejected consequence, registered as a NEW residual (oracle N13): a bare
     secret containing whitespace is redacted only up to its first token
     (`password: iron steel` → `password: <redacted> steel`); the quoted form
     still gives full coverage. Same class of residual on the auth path when a
     secret is split across a newline.
2. *(rejected)* **Strict single token everywhere + move the scheme word into the
   KEY** (`authorization\s*[:=]\s*(?:\S+\s+)?`). Keeps the marker redacted, but
   rewrites five frozen I-14-C envelopes (`Authorization: Bearer <redacted>` etc.),
   the E1 helper-only exact assertion, and moves output the card never asked to
   move. Larger blast radius than the defect requires. (Mutation M3 demonstrates
   the leak that any scheme-ignoring variant produces.)
3. *(rejected)* **Leave the auth regex untouched (multi-word `\s+` joins).**
   Smallest diff, but C13 then remains OPEN on the auth path — a credential in an
   `Authorization:` header still deletes the following multi-line diagnostic block.
   The card's exit clause (裸值不再跨行吞掉后续诊断键) covers 裸值, not just the
   scanner; leaving half the surface swallowed would not meet it. (Mutation M2 is
   exactly this tree and its oracle case fails.)

### Why this is implementer-level, not a deferred professional decision

The card itself is the owner's decision to narrow (its title and clause 2); the
frozen I-14-C text already documents the scheme shapes as the reason the auth value
was multi-word; option 1 preserves every frozen I-14-C expectation that does not
itself encode the C13 swallow. The choice, its cost (N13 residual), the rejected
alternatives and the recovery rule are recorded here and in the frozen oracle for
the independent reviewer to confirm or overturn at review. If the reviewer prefers
option 2's envelopes, the change is one regex group and the oracle's auth rows are
rewritten then — nothing else in this attempt depends on it.

## NA items

- No schema/migration/transaction decision: nothing persisted changes shape
  (`message_redacted` values change content/length exactly as the card intends).
- No statistical/threshold decision. The E4b baseline move (193 → 314 pre-truncation
  / 200 persisted) is a hand-computed consequence of the frozen semantics, frozen in
  oracle.md §N4 for the reviewer to re-derive — not a threshold choice.
- No cross-repo contract change: `error_taxonomy.structured_error` is untouched;
  only the redactor's value semantics change, inside the card's allowlist
  ("the existing redactor", same scope wording I-14-C used).
