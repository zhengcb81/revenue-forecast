# Parent adjudication of round-2 live scan + CORRECTION 2 order (transcribed, 2026-09-22)

Source: parent agent session-bfecd191-fbc3-4a66-8ed1-6562479bf102 message to this attempt,
transcribed so the ruling and the final-round order survive independent of the session
transcript. Companion files: round-1 ruling in `parent_adjudication_r1.md`, round-2 raw
48-line scan in `round2_live_scan.txt`.

## ① Adjudication of the 48 round-2 residuals (one line-by-line reading by the parent)

**True positives = 0.** All residuals fall into residual false-positive classes:

- **R-A Chinese-numeral / noun-pair counts** (D8 recognized Arabic-numeral+classifier only):
  L6 五臂全部、L10 四前提全部、L32/L43 三趟全部、L38 四锚全部、L35 三步分诊、
  L37 21 提交全部、L47 5 变异全部、L17/L46 C1–C12 全部（枚举）— the same-line qualifier
  is present; compliant.
- **R-B hyphen / flag / code identifiers** (D10a covered underscore only):
  L8 `isinstance-only`、L31/L42 `--name-only`、L34/L41 `mock-only`、
  L15 `all([...])` code、L11 `all(布尔项)` code、L16 `claims_all_three_fail`
  (underscore-word `all` — confirm D10a covers it) — identifier/code/flag forms; compliant.
- **R-C frozen / quoted / historical-state lines**: L3 (M24 binding verbatim quote),
  L7 (frozen rule JSON), L28 (owner quotation), L39/L40 (historical state string
  RESOLVED rows) — quotation is its own domain; compliant.
- **Remainder**: conditional 只有…时 forms (L4/L9/L14) and subject-internal qualifiers
  (L1/L2/L12/L13/L22/L23/L25 「全部可打印字符」which IS its own domain /L26/L27/L29/L30/
  L33/L36/L44/L45/L48) — all compliant.

## ② CORRECTION 2 — the FINAL lexicon iteration; lexicon freezes at v2 afterwards

Append-only oracle correction with three pattern groups:

- **D8b Chinese numerals**: 一二三四五六七八九十廿卅 paired with classifier/noun
  (五臂/四前提/三趟/四锚/三步, and Arabic+noun forms like 21 提交 / 5 变异) count as a
  carried same-line domain;
- **D10b hyphen & flag forms**: `-only` hyphen compounds, `--name-only` CLI flags,
  `all(`/`all[` code-call forms — grouped into skip (or domain), following the D10a
  disposition; reasoning to be written down;
- **D11 quoted-line skip**: frozen quotations / utterances / historical state strings
  wrapped in `"`, `「`, `*"`, or backticks — skip when the line starts with the quotation
  or when the marker hit lands inside the quoted span; implementation detail to be stated
  (e.g. "marker hit falls within a quote span").

After CORRECTION 2: re-run GREEN + live scan; produce `round3_summary` (residual expected
to approach 0) and `round3_diff`. **NO CORRECTION 3 will be opened** — any residual after
round 3 goes directly to the parent as a per-line list for item-by-item ruling (bounds the
iteration).

## ③ Delivery closing order

CORRECTION 2 → round-3 evidence → final handoff/binding/commands updates (round-1 ruling,
round-2 ruling, round-3 results all into carried findings and the evidence index) → final
self-contained report to the parent → the parent dispatches independent review.
RED / GREEN / the 3 mutations need NOT be re-run (both corrections loosen the domain
decision rather than narrow the detection surface — reuse the argument already written);
**if D11 quoted-line skip counts as detection-surface narrowing, a small GREEN verification
against a quoted-line sample group is required and must be declared in the correction.**

## ④ Quality confirmations

Round-2 monotonicity proof (byte-stable files 131→28 / 37→10 / NEW=0), the progress.md
drift attribution (parent's Round 85 write; `plan_hashes_unchanged=false` refers to that
file only), and oracle self-scan round-2 = 0 violations: method confirmed correct.
