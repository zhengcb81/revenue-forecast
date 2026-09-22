# REM79-MECHANIZATION decision record

Card: **REM79-MECHANIZATION** (plan-level, method) — turn REM-79 ("every universal-quantifier
claim must carry its domain on the same line") from prose into an automatic checker with a
red-green proof. Plan-scoped tooling; **not** product code.

Attempt: `execution_runs/REM79-MECHANIZATION/a20260922-01`.

## Why this card exists (the failure being mechanized)

The prose rule has been written down and violated repeatedly in this plan's own history:

- **F-REV-R4-06** — `oracle.md` C4.5 `fix_A_and_B leaves only the registered C10 residual`
  priced on 19 probes, written as a general claim (3 copies at the time).
- **F-REV-R5-02** — "closes the whole family at zero cost", priced on 19 probes of a 31-form
  family; written one paragraph above the correction that declared the structurally identical
  R4 sentence false. Third generation of the same species.
- **F-REV-R6-02** — the r6 headline universal `[^\s]+` closes every character r4 or r5 closed…
  appeared at 3 sites (`I-14-D/review.md:349`, `oracle.md:649-651`, `task_plan.md:1994`) without
  a same-line domain — in the very round that legislated the rule. Fourth generation.
- **M05-style over-claims** — the same "record claims more than the measurement supports"
  species appears across the M-batch audit lines (recorded in findings.md lineage).

`findings.md:542` states the conclusion this card operationalizes: after a rule written down
three times and violated three times, the next step is not to write it a fourth time.

## Design decisions (frozen details live in oracle.md)

1. **Rule semantics.** Line-oriented scan: a line that contains at least one **universal
   marker** (frozen CJK + EN lexicons) and contains **no same-line domain qualifier** (frozen
   domain patterns D1–D7) is a **violation**. No cross-line context, no NLP: deliberately a
   same-line heuristic, matching the letter of REM-79. Every lexicon/pattern is frozen in
   `oracle.md` before any checker code exists; no silent widening after freeze (corrections
   only by explicit appended correction).
2. **Known-false historical cases are the positive corpus** (must FLAG): I-14-D `review.md`
   L349 r6-era line (extracted verbatim), the reconstructed pre-fix Round 76 sentence from
   `task_plan.md:1994`, and two synthetic snippets mirroring the F-REV-R4-06 and F-REV-R5-02
   sentence shapes. The M05-era pattern is represented through the two synthetics (no single
   M05 sentence is quoted as a carrier here; the spec-required four positives are all present).
3. **Negatives.** (a) 14 lines pairing a universal marker with a same-line domain, extracted
   verbatim from current carriers (task_plan/findings/progress/REMEDIATION_REGISTER and
   I-14-D review.md), including **two lines that this oracle itself carries verbatim**; (b) 13
   lines carrying no universal marker at all. Both classes must stay clean.
4. **Checker.** Single stdlib-only Python script `tools/check_domain_assertions.py`, no
   network: `check [--json] FILE...`; exit 0 = clean, 1 = violations (file:line:marker
   excerpts), 2 = usage/IO error. The deliberately-naive RED variant (marker detection without
   the domain requirement) lives at `harness/naive_checker_marker_only.py` and is run against
   the SAME frozen oracle table; it must fail it (it flags the domain-carrying negatives).
5. **Protocol order.** corpus build (extraction only, no check logic) → `oracle_table.json` +
   `oracle.md` FROZEN → checker written → RED → GREEN → 3 pre-declared mutations → live scan
   of plan `task_plan.md` / `findings.md` / `progress.md` (read-only; findings are reported to
   the parent, no plan file is edited by this attempt).
6. **Mutations (red sets declared in the frozen oracle before any run).**
   (a) strip a domain qualifier from a negative payload → that line must FLAG;
   (b) add a domain qualifier to a positive payload → that line must go CLEAN;
   (c) shift a payload by one line → the reported line number must MISMATCH the oracle
   baseline (proves reports carry true line numbers).
7. **Boundaries.** Writes only inside this attempt. Plan files, product, and other attempts
   are read-only. No git writes, no pytest (plain subprocess asserts inside the attempt's own
   harness). Handoff is `status=review_pending`, never self-signed,
   `disclosure_adaptation=unmapped`, `accuracy=unproven`.
8. **Honest limits declared up front** (also restated in oracle.md and the final report):
   the checker is a lexical heuristic — it cannot see claims expressed without the frozen
   markers (e.g. 所有 / 均 / 每次 / always / every↔"each"), cannot verify that a present domain
   is the RIGHT domain, treats a decorative `域` anywhere on the line as sufficient, is
   line-bound (a domain on the next line does not count, by design), and will false-positive
   on quoted lexicon/example lines. These limits are properties of the frozen contract, not
   bugs to patch after freeze.

## Post-delivery addendum — oracle CORRECTION 1 (parent-ordered, 2026-09-22)

The parent adjudicated all 214 round-1 live detections by line-by-line reading (true
positives = 0; three false-positive classes) and ordered the protocol path instead of file
edits on either side: append CORRECTION 1 to the oracle (ruling recorded in
`evidence/live/parent_adjudication_r1.md`). Choices this implementer had to make inside
that correction, and why:

- **D8/D9 are domain-side additions only** — chosen shapes: same-line numeral+classifier
  with a `(?<!每)` guard (so 每一个 can never self-satisfy its own domain), a 14-char
  subject-determiner window, and a post-marker identifier-range enumeration. Rationale:
  they parse scoping that was semantically present all along, they are monotone (can only
  clear violations, never create one), and they leave the frozen expectation table
  untouched — re-proven by round-2 GREEN exact match.
- **D10a identifier `only`: STOP matching** (marker boundary excludes `[A-Za-z0-9_]`
  adjacency) — `fix_A_only` is not a quantifier claim; flagging it manufactures violations
  with zero semantic content. Hyphen/space-adjacent `record-only` still matches, as the
  frozen §3 boundary note requires.
- **D10b quoted frozen-rule lines: KEEP FLAGGED** — a `[quoted-frozen]` skip annotation
  would be a prose escape hatch any author could use to silence a real violation (the very
  failure mode REM-79 mechanizes), and the tool cannot verify frozenness; visible
  false positives on quote lines are the cheaper error than silent false negatives.
- **RED re-run** despite the parent's "not required": cheap, and it proves the oracle
  §C1.4 argument (domain-blind arm unaffected by domain additions) with raw evidence
  instead of prose.

## Post-delivery addendum 2 — oracle CORRECTION 2 (parent-ordered, FINAL iteration, 2026-09-22)

After the parent adjudicated all 48 round-2 residuals as compliant (true positives = 0;
classes R-A Chinese-numeral counts, R-B hyphen/flag/code identifiers, R-C quoted lines),
it ordered one final lexicon iteration and closed the lexicon (v2 freeze; **no CORRECTION
3** — residuals after round 3 go to the parent item-by-item). Choices made inside it:

- **D8b built as five sub-forms** (b1 numeral+noun before the universal with 的/过 gap
  exclusion and identifier-digit guard; b1r id-range; b2 universal-paired bounded NP in
  CJK/Latin/ALL-GREEN flavours with 每一个 deliberately excluded; b3 conditional 只有…时).
  Every guard exists to keep the four frozen positives flagging — re-proven by round-3
  GREEN exact match, not by assertion.
- **D10b superseded §3's frozen `record-only`-matches note** (old/new quoted in oracle
  §C2.2): hyphen-adjacent compounds and `all(`/`all[` are identifier/code forms, not
  quantifier claims — same rationale as D10a. Expectations invalidated: 0.
- **D11 quoted-line skip reverses my CORRECTION 1 keep-flagged choice**, on the owner's
  explicit ruling that quotations are their own domain. Because this narrows the detection
  surface, the quote-sample mini-GREEN was declared in the correction text BEFORE the
  sample existed (oracle §C2.3), then run: PASS. The resulting escape-hatch risk (a real
  claim hidden inside quotes is silently skipped) is recorded in handoff
  `remaining_gaps_honest` so the owner carries it knowingly.
- **The 2-line residual is handed up, not patched**: task_plan.md:1630 (count sits AFTER
  the universal — outside the five frozen sub-forms) and findings.md:633 (uppercase ALL vs
  the lowercase `all` literal in b2en). Fixing either would require CORRECTION 3, which the
  owner forbade — the anti-unbounded-iteration rule outranks a clean scan.
