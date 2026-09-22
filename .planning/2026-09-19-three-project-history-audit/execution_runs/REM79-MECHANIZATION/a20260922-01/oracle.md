# REM79-MECHANIZATION oracle — FROZEN

**Freeze statement (§0).** This oracle was frozen on 2026-09-22 **before any checker code
(naive or real) was written**. The corpus files were built by extraction only (域：本 §0) — no check logic
ran before this freeze. Rule, lexicons, corpus file list + sha256, the expected
detect/not-detect table per file+line, and exit-code semantics below ARE the contract. The
lexicon may not be widened or narrowed after this freeze; any change must be an explicitly
appended, labelled correction (§11), never a silent edit. Machine-readable twin:
`oracle_table.json`, sha256 `366b18253c973306fc1a8ea237c377551bc3be68243e6fc83cf5f247a87edae7`
(hash recorded here at freeze; this file's own hash is recorded in `binding.json`).

## §1 Rule (REM-79, mechanized)

A **line** of a scanned text file that contains a **universal-quantifier marker** from the
frozen lexicon (§3) and contains **no same-line domain qualifier** from the frozen domain
patterns (§2) is a **violation**. This is the letter of REM-79 (域：本 §1): "every universal-quantifier
claim must carry its domain on the same line". History this mechanizes: F-REV-R4-06, F-REV-R5-02,
F-REV-R6-02 (4th generation, committed in the round that legislated the rule), and the
M05-style over-claims of the same species ("the record claims more than the measurement
supports" — findings.md:542).

## §2 Detection semantics

- Line-oriented: the scan unit is one physical line (files decoded UTF-8, split on newlines).
  A domain written on the neighbouring line does not count — by design, that IS the violation.
- Violation ⇔ `markers(line) ≠ ∅ ∧ domain(line) = ∅`.
- No NLP, no cross-line context, no network, stdlib only (域：本 §2).

**Domain patterns (frozen, Python `re` syntax, any one of them on the line satisfies REM-79):**

| id | pattern | meaning |
|---|---|---|
| D1 | the literal character `域` anywhere on the line | explicit domain field (域：… / 域=…) |
| D2 | `(?i)domain\s*[:=]` | `domain:` or `domain =` key |
| D3 | `在[^。；;\n]{1,40}上` | CJK 在…上 scoping phrase |
| D4 | `\d+\s*个` | bounded CJK count (95 个 / 19 个) |
| D5 | `\d+\s*(?:cases?\|rows?\|probes?\|characters\|chars?\|entries\|lines?\|files?\|cards\|tests\|runs?\|trees\|forms?\|instances\|samples\|words?\|tokens?\|bytes\|sites\|revisions?\|rounds?)(?![A-Za-z])` (case-insensitive) | bounded EN count |
| D6 | `×\s*\d+` or `(?<![A-Za-z])N\s*=\s*\d+` | multiplier / N= form |
| D7 | `（[^（）\n]{1,60}(?:、[^（）\n]{1,60}){2,}）` or the ASCII-parenthesis equivalent | bounded-set enumeration in parentheses |

## §3 Frozen lexicons

**Universal markers — CJK literal substrings** (each row carries its own domain note, 域：本词表行):

| marker | kind | note |
|---|---|---|
| `只有` | CJK substring | 域：本词表行 |
| `全部` | CJK substring | 域：本词表行 |
| `没有` | CJK substring | 域：本词表行 |
| `整个族` | CJK substring | 域：本词表行 |
| `零代价` | CJK substring | 域：本词表行 |
| `无一` | CJK substring | 域：本词表行 |
| `每一个` | CJK substring | 域：本词表行 |

**Universal markers — EN, case-insensitive, letter-boundary** (`(?<![A-Za-z])W(?![A-Za-z])`
per word, i.e. bounded by non-letters or string edges; 域：本词表行):

| marker | kind | note |
|---|---|---|
| `only` | EN word-boundary | 域：本词表行 |
| `all` | EN word-boundary | 域：本词表行 |
| `none` | EN word-boundary | 域：本词表行 |
| `every` | EN word-boundary | 域：本词表行 |
| `whole family` | EN phrase, letter-boundary at both ends | 域：本词表行 |
| `zero cost` | EN phrase, letter-boundary at both ends | 域：本词表行 |

Notes on the frozen EN boundaries (域：本词表): `record-only` / `at all;` DO match (hyphen, space and
punctuation are non-letters); `callback`, `allow`, `everyone` do NOT match (letter-adjacent) — 域：本词表的边界注.
These consequences are frozen as-is.

**This oracle's own two corpus-carried lines (verbatim; both appear in
`corpus/neg_domain_lines.md` lines 28 and 30 and are expected NOT to flag):**

- O1: 凡含「只有 / 全部 / 没有 / 整个族 / 零代价 / 无一 / 每一个」或 EN `only` / `all` / `none` / `every` / `whole family` / `zero cost` 形态的断言行，必须同行带域字段（域：本 oracle 冻结词表，§3）。
- O2: 本 oracle 的每一个期望行都同时登记 file、line 与 expect，缺失同行域的登记按未验证处理（域：§5 期望表；机器表 = oracle_table.json）。

## §4 Corpus (frozen file list + hashes, extracted BEFORE this freeze)

Extraction provenance, source-file hashes at extraction and payload hashes:
`evidence/corpus_manifest.json` (written by `harness/build_corpus.py`, extraction only; 域：本 §4).

| file | sha256 | role |
|---|---|---|
| `corpus/pos_i14d_review_L349.md` | `3d02e4c39f15a796dd8ba015f6c31588ba385a35b462af5982e572fb64728844` | POSITIVE (historical FALSE, must flag) |
| `corpus/pos_round76_original.md` | `09892ab4351fc219e356667485055bb32746227874721d739f208e8b9e94ec43` | POSITIVE (historical FALSE, must flag) |
| `corpus/pos_synth_frev_r406.md` | `4279c6957aa6cf792056062edd79d10c29689124bb3b0d1ef4401dc4d45ebbec` | POSITIVE (synthetic F-REV-R4-06 shape) |
| `corpus/pos_synth_frev_r502.md` | `087011fa33587b9526d73d649045d3f074adbb2f8f941bc763057d2d2850b55d` | POSITIVE (synthetic F-REV-R5-02 shape) |
| `corpus/neg_domain_lines.md` | `5312e2211aa65f213d46c4a249d21377c9290798930ac565ca02b1a876de3e9c` | NEGATIVE: marker + same-line domain (must stay clean) |
| `corpus/neg_no_marker_lines.md` | `b38ae80ad07146f83b3c4692216dd67c57da5aa05232993e1fefebb9800d0fa1` | NEGATIVE: no universal marker (must stay clean) |

Sources read-only at extraction (域：本 §4): `task_plan.md` sha256 `4096a44d…bc687bf`, `findings.md`
`5a6acccc…c8f5a`, `progress.md` `e86b91cc…b43a2`, `REMEDIATION_REGISTER.md` `fe6203f6…2fc7b`,
`execution_runs/I-14-D/a20260919-01/review.md` `87519be0…9dd4f` (full values in the manifest).

## §5 Expected detect / not-detect table (per file + line)

The machine form is `oracle_table.json` (sha256 above); it and this table are identical in
content. Each corpus file starts with two comment lines, a blank line, then payloads.

| file | line(s) | expect | reason |
|---|---|---|---|
| `corpus/pos_i14d_review_L349.md` | 4 | **FLAG** | historical FALSE case F-REV-R6-02 site 1 |
| `corpus/pos_i14d_review_L349.md` | 1, 2, 3 | no flag | provenance comments, no marker |
| `corpus/pos_round76_original.md` | 4 | **FLAG** | historical FALSE case F-REV-R6-02 site 3 (reconstructed) |
| `corpus/pos_round76_original.md` | 1, 2, 3 | no flag | provenance comments, no marker |
| `corpus/pos_synth_frev_r406.md` | 4 | **FLAG** | synthetic mirror of F-REV-R4-06 |
| `corpus/pos_synth_frev_r406.md` | 1, 2, 3 | no flag | provenance comments, no marker |
| `corpus/pos_synth_frev_r502.md` | 4 | **FLAG** | synthetic mirror of F-REV-R5-02 |
| `corpus/pos_synth_frev_r502.md` | 1, 2, 3 | no flag | provenance comments, no marker |
| `corpus/neg_domain_lines.md` | 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 | no flag | marker present AND same-line domain present (14 sampled lines, incl. O1/O2 from this oracle) |
| `corpus/neg_no_marker_lines.md` | 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28 | no flag | no universal marker (13 sampled lines) |

Combined run over the six files, in the order listed in `oracle_table.json`:
**exit 1, exactly 4 violations, at line 4 of each of the four POSITIVE files.**
Per-file exits: each POSITIVE file → 1; each NEGATIVE file → 0.

## §6 CLI / output / exit-code contract

```
python tools/check_domain_assertions.py [--json] FILE [FILE ...]
```

- stdout (text): one `path:line:[marker1,marker2] excerpt` line per violation, then
  `N violation(s) across M file(s)`.
- `--json`: one JSON object: `{"tool","rule":"REM-79","files":[{"path","violations":[{"line",
  "markers","excerpt"}]}],"totals":{"files","violations"}}`.
- **exit 0** = clean (zero violations across the given inputs; 域：本次运行收到的输入文件);
  **exit 1** = violations found;
  **exit 2** = usage/IO error (message on stderr).
- stdlib only (域：本 §6), no network, no writes: the checker never modifies any input.

## §7 RED / GREEN protocol and mutation red sets (declared BEFORE runs)

- **RED** = `harness/naive_checker_marker_only.py` (域：本 §7): flags every line carrying a universal
  marker, WITHOUT the domain requirement. It runs against this same table and **must FAIL the
  frozen expectations** — concretely it flags the 14 `neg_domain_lines.md` payloads whose
  expected flag set is empty. Raw stdout preserved under `evidence/red/`.
- **GREEN** = `tools/check_domain_assertions.py` must satisfy this table EXACTLY (域：本 §5): all four
  positives flagged, both negatives clean, per-file exits as in §5, combined run exit 1 with
  4 violations. Raw stdout + `--json` under `evidence/green/`.
- **Mutations (red sets frozen here, before any mutation run):**
  - **MUT-A strip domain** — copy `corpus/neg_domain_lines.md`, delete the substring
    `（**域：…落于本行**）` from payload line 4 (other bytes identical) → checker MUST flag
    line 4 (report exit 1). Red if line 4 stays clean.
  - **MUT-B add domain** — copy `corpus/pos_synth_frev_r406.md`, append
    ` (domain: 19-probe measurement set)` to payload line 4 (other bytes identical) → checker
    MUST report zero violations (exit 0). Red if line 4 still flags.
  - **MUT-C off-by-one** — copy `corpus/pos_synth_frev_r502.md`, insert one empty line at the
    top → payload moves 4 → 5; the report MUST show line **5**, i.e. MISMATCH the oracle
    baseline line 4. Red if the report still says 4 (line numbers would be stale/wrong).

## §8 Known-false cases (historical, expected detections)

| id | original sentence (shape) | where it was falsified | in this corpus |
|---|---|---|---|
| F-REV-R4-06 | "`fix_A_and_B` leaves only the registered `C10` residual" (19 probes → general claim) | task_plan.md:1839/1866, REMEDIATION_REGISTER.md:283 | `corpus/pos_synth_frev_r406.md:4` (synthetic mirror) |
| F-REV-R5-02 | "closes the whole family at zero cost" (19 probes, 4 of family, vs 31 forms) | task_plan.md:1934–1976, progress.md:830 | `corpus/pos_synth_frev_r502.md:4` (synthetic mirror) |
| F-REV-R6-02 site 1 | "[^\s]+` closes every character r4 or r5 closed and every character either leaked, except the space" (unscoped as written; 域：本表登记 = corpus L4) | I-14-D review.md:378–382 (supersession), REMEDIATION_REGISTER.md:370 | `corpus/pos_i14d_review_L349.md:4` (verbatim r6-era line) |
| F-REV-R6-02 site 3 | Round 76 headline "关闭了…每一个字符…只剩空格" before the parent's same-line domain fix | REMEDIATION_REGISTER.md:370 (site 3 = task_plan.md Round 76) | `corpus/pos_round76_original.md:4` (reconstruction rule in §4/manifest; 域：本表) |

## §9 Live scan (record-only; 域：本节)

After GREEN, run the real checker on `<PLAN>/task_plan.md`, `<PLAN>/findings.md`,
`<PLAN>/progress.md`. No oracle expectation applies (these are live files): record the total
count and every `file:line` finding as evidence for the parent, who owns those files (域：本次 live 扫描的三个计划载体). **This
attempt edits no plan file.**

## §10 Declared heuristic limits (frozen honesty clause)

This checker is a lexical heuristic and, as frozen, it CANNOT:

1. catch universal claims written without a lexicon marker (所有 / 均 / 每次 / 一律 / always /
   each / both, or a bare "100%" claim) — the lexicon is the contract, not the semantics;
2. judge whether a present domain is the CORRECT domain — a decorative `域` anywhere on the
   line satisfies D1 even if it scopes a different noun;
3. see domains on adjacent lines (by design) or claims spanning multiple lines;
4. distinguish a lexicon QUOTE (this oracle's §3, rule-statement lines) from a real claim —
   such lines flag unless they themselves carry a domain;
5. parse hand-wavy scoping that matches none of D1–D7 — declared here as a limit (域：本 §10) (e.g. "在实践中", "一般来说",
   "under our tests" with no count) — these false-positive as violations and are reported as
   such, letting a human judge them;
6. decode non-UTF-8 inputs faithfully (bytes are replaced, which can hide markers).

Known trade-off direction: the frozen heuristics prefer false positives over silent misses on
marker-bearing lines, and prefer silence over invention on marker-free lines.

## §11 Corrections policy

Any post-freeze defect discovery is fixed by an APPENDED, dated, labelled `CORRECTION N`
section (never by editing §1–§10); a lexicon/pattern change requires quoting the old and new
text and re-stating which frozen expectations it invalidates. The original frozen bytes stay
reproducible as the prefix of this file.

---

## CORRECTION 1 (2026-09-22) — appended per §11, ordered by the parent agent after its line-by-line adjudication of the round-1 live scan

**Provenance.** Ruling: `evidence/live/parent_adjudication_r1.md` — the parent read each of
the 214 round-1 detections (domain of the ruling: that single reading of
`evidence/live/round1_findings_214.txt`), found true positives = 0, and classified the hits
into three false-positive classes: (a) same-line count/subject/enum qualifiers the frozen
D1–D7 did not parse, (b) existential negations, (c) identifier-internal fragments and quoted
frozen-rule lines. §1–§10 above remain byte-frozen: this section is appended after them; the
pre-correction bytes (sha256
`6faa0ae90a0693ffeb03f9b63a811d4832d12f0e598f1699dcaf29462bdc241f`, 13029 bytes) remain
reproducible as this file's prefix (byte ledger: `evidence/oracle_correction1_ledger.json`).

**Scope: the domain side gets D8/D9; the marker side gets D10 (identifier adjacency).**
The frozen §2 patterns D1–D7 and the §3 lexicons stay as written; the entries below ADD to
them, and `oracle_table.json` (expectations) is NOT changed.

### C1.1 — new domain pattern D8（计数限定）: a same-line numeral+classifier co-occurring with the universal counts as a carried domain （域：本更正）

regex: `(?<!每)(?:[一二三四五六七八九十两几零]+(?:余|多)?|[≈约余近共]?\d+)\s*(?:个|条|张|卡|项|次|行|类|族|组|种|点|位|批|份|轮|代|句|处|人|款|版|节|章|部分)`

samples（域：C1.1 样例行）: 「三个请求全部返回同一 demand_id」(D8=三个)；「八条 case 全部通过」；「剩余 ≈24 张卡全部…」；「四张卡均已落盘」。

Guard: `(?<!每)` excludes `每一个` itself（域：C1.1 guard） — the universal's own quantifier must never satisfy
the domain requirement（域：C1.1 guard，四正样本回归见 C1.4）.

### C1.2 — new domain pattern D9（主语/枚举限定）, same-line co-occurrence （域：本更正）

regex, two alternatives inside one pattern.
A — subject-side determiner within 14 chars before the universal (no clause break):
`(?:剩余|新|旧|既定|原始|当前|本轮|本次|尚未|仍|待|均|上述|下列|该批|该项|此类)[^。！？；\n]{0,14}(?:全部|没有|只有|无一|每一个|整个族|零代价)` （域：C1.2 规则 A）
B — explicit enumeration after 全部/无一/只有（域：C1.2 规则 B）:
`(?:全部|无一|只有)[^。！？；\n]{0,48}[A-Za-z]{1,4}[-_]?\d{1,4}\s*[–\-—+、,，]\s*[A-Za-z]{0,4}[-_]?\d{1,4}` （域：C1.2 规则 B）

samples（域：C1.2 样例行）: 「新实施计划仍全部待实施」(A: 新→全部)；「剩余卡全部…」(A: 剩余)；「全部 M01–M31 + I-00… 均已登记」(B: 枚举)。

D8/D9 are CJK-anchored (domain: the adjudicated 214 detections are CJK-dominant; EN count
scoping stays on the frozen D5).

### C1.3 — D10 registered: identifier-internal `only` and quoted frozen-rule lines （域：本更正）

- **D10a identifiers — handling rule chosen: STOP matching.** EN marker boundaries change
  from old `(?<![A-Za-z])W(?![A-Za-z])` to new `(?<![A-Za-z0-9_])W(?![A-Za-z0-9_])`, for
  W ∈ {only, all, none, every} and the `whole family` / `zero cost` phrases（域：C1.3a 新旧对照）.
  Reason: `fix_A_only` is an identifier fragment（域：C1.3a）, not a quantifier claim — flagging it
  manufactures a violation with zero semantic content; real claims delimit their markers with
  spaces, punctuation or line edges, which are unaffected（域：C1.3a 论证）— `record-only` and
  `at all;` still match, the hyphen/space consequence frozen in §3 is retained（域：C1.3a）.
- **D10b quoted frozen-rule lines — handling rule chosen: KEEP FLAGGED.** Reasons: (1) the
  checker has no knowledge of which text is frozen; (2) an annotation-based skip
  (`[quoted-frozen]`) would be a prose escape hatch any author could use to silence a real
  violation — the exact failure mode REM-79 mechanizes; (3) false positives on quote lines are
  visible and cheap for a human to dismiss, false negatives are silent; (4) compliant carriers
  prove the standing cost is low: this oracle quotes the whole lexicon in §3 and self-scans at
  0 violations（域：evidence/live/selfscan_oracle.txt）.

### C1.4 — why this is not silent widening, and what it cannot touch

- Appended, labelled, dated, old text preserved as byte prefix per §11 (ledger path above) —
  the sanctioned correction path, not a silent edit.
- **D8/D9 ADD domain patterns (no other change)** ⇒ violations shrink monotonically: no line
  can become a violation that was not one before. They cannot flip any frozen §5 expectation:
  negatives were already clean; positives must stay flagged, re-verified by the round-2 GREEN
  run against the UNCHANGED `oracle_table.json`（域：evidence/round2/green/green_verdict.json）.
  RED is untouched by construction — the naive arm applies no domain logic whatsoever, so
  domain-side additions cannot change what it reports; it is re-run anyway for arm consistency
  （域：evidence/round2/red/red_verdict.json）.
- **D10 narrows the marker side solely at alphanumeric/underscore adjacency.** The four frozen
  positives' markers are space- or punctuation-delimited（域：C1.4） (` only `, `every character`,
  `每一个字符`)（域：C1.4），so their flagging is invariant; re-verified by round-2 GREEN. RED
  re-run under the same boundary change reports the identical verdict (its failing lines are
  plain-delimited)（域：C1.4）.
- Frozen expectations invalidated: **0** — stated per §11, proven by the round-2 GREEN exact
  match (4 violations / 0 false positives, per-file exits 1/1/1/1/0/0) and all three mutations（域：C1.4）
  re-passing（域：evidence/round2/verify_summary.json）.
- Declared new limits of CORRECTION 1（域：本更正 limits）: D8 accepts a decorative count
  anywhere on the line (same epistemic class as D1's decorative 域); D9-A's 14-char determiner
  window is heuristic; existential negations carrying neither count nor subject qualifier are
  NOT auto-cleaned by this correction — they stay visible in the narrowed round-2 candidate
  set for owner re-adjudication.

---

## CORRECTION 2 (2026-09-22) — FINAL lexicon iteration, appended per §11 on the parent's order; after this the lexicon freezes at v2 (no CORRECTION 3)

**Provenance.** The parent read all 48 round-2 residuals line-by-line and ruled true
positives = 0（域：裁处全文 = `evidence/live/parent_adjudication_r2_and_c2.md`；48 行原文 =
`evidence/live/round2_live_scan.txt`），classifying them as R-A Chinese-numeral/noun-pair
counts, R-B hyphen/flag/code identifiers, R-C quoted/frozen lines, plus compliant
conditional (只有…时) and subject-internal forms. This correction implements the three（域：CORRECTION 2 自审注）
ordered pattern groups. Pre-correction bytes: 19324 bytes, sha256
`c8a6f20931bbf92aea96b5ea2be9ece19f977bc2f778dcd22a2f1f00c83be824` (the C1 state) —
still reproducible as this file's prefix; ledger `evidence/oracle_correction2_ledger.json`.
Expectations (`oracle_table.json`) remain UNCHANGED.

### C2.1 — D8b (count/noun pairing around the universal; domain-side addition)

One pattern id `D8b` with five sub-forms, each traceable to an adjudicated class（域：本更正
C2.1；样例行均取自 round-2 原文）:

- **b1 count-before**: `(?<![A-Za-z0-9_])(?:[一二三四五六七八九十廿卅]+(?:余|多)?|[≈约余近共]?\d+)\s*[一-鿿]{1,4}[^。！？；\n的过]{0,6}(?:全部|没有|只有|无一|每一个|整个族|零代价)`（域：CORRECTION 2 自审注）
  — covers R-A pairs 五臂全部 / 四前提全部 / 三趟，全部 / 四锚全部 / 三步分诊（全部 / 21 提交全部 /（域：CORRECTION 2 自审注）
  5 变异矩阵全部. The `(?<![A-Za-z0-9_])` guard keeps identifier references like `r5` from（域：CORRECTION 2 自审注）
  counting, and the gap exclusion of 的/过 keeps `两者泄漏过的每一个字符` un-satisfied —（域：CORRECTION 2 自审注）
  both guards exist so the four frozen positives stay flagged（域：C2.1 正样本回归）.
- **b1r range-before**: `[A-Za-z]{0,4}[-_]?\d{1,4}\s*[–\-—]\s*[A-Za-z]{0,4}[-_]?\d{1,4}[^。！？；\n]{0,6}(?:全部|无一|只有)`（域：CORRECTION 2 自审注）
  — covers `C1–C12 全部` (R-A enumeration).（域：CORRECTION 2 自审注）
- **b2 universal-paired bounded NP**: `(?:全部|没有|只有|无一)(?:\s*[一-鿿]{2,6}|\s+[`]?[A-Za-z][A-Za-z0-9_]{2,})`（域：CORRECTION 2 自审注）
  plus EN `(?<![A-Za-z0-9_\-–—])all(?![A-Za-z0-9_\-–—])\s+[A-Z][A-Za-z0-9_+.-]{2,}`（域：CORRECTION 2 自审注）
  — implements the parent's "主语句内限定" rulings: 全部历史通过项 / 全部工作 / 没有正确透传 /（域：CORRECTION 2 自审注）
  只有 M31 / 全部可打印字符 / 全部登记在 / 全部 `ValueError…` / ALL GREEN …（域：裁处 remainder 组）.
  每一个 is deliberately NOT in the b2 marker set: `每一个字符` must not self-satisfy the（域：CORRECTION 2 自审注）
  frozen positive `corpus/pos_round76_original.md:4`（域：C2.1 正样本回归）.
- **b3 conditional**: `只有[^。！？；\n]{0,30}时(?:才|就|方|能|可)?`（域：CORRECTION 2 自审注）
  — the parent's own ruling that conditional 只有…时 forms are compliant（域：裁处 L4/L9/L14）.

**Declared residual policy**: forms outside these five sub-forms (e.g. unpaired exotic
shapes) are NOT patterned here — they go to the parent as the round-3 residual list for
item-by-item ruling; **CORRECTION 3 will not be opened**（域：封轮指令）.

### C2.2 — D10b (hyphen compounds, CLI flags, code calls; marker-side, supersedes the §3 boundary note)

Old EN marker boundary（域：新旧对照）: `(?<![A-Za-z0-9_])W(?![A-Za-z0-9_])`.
New: `(?<![A-Za-z0-9_\-–—])W(?![A-Za-z0-9_\-–—])` for W ∈ {only, all, none, every} and the（域：CORRECTION 2 自审注）
two phrases, PLUS `all` immediately followed (optional spaces) by `(` or `[` is not a marker（域：CORRECTION 2 自审注）
occurrence (code call: `all([...])`, `all(布尔项)`).（域：CORRECTION 2 自审注）

**This SUPERSEDES the sentence frozen in §3 and repeated in CORRECTION 1 §C1.3 that
`record-only` and `at all;` still match**: hyphen-adjacent compounds are identifier/flag（域：CORRECTION 2 自审注）
forms（域：本更正取代声明；旧文本照录于上，新文本 = the "New:" regex above）. Reason, kept
identical to the D10a disposition: `isinstance-only` / `--name-only` / `mock-only` are not（域：CORRECTION 2 自审注）
quantifier claims — flagging them manufactures violations with zero semantic content, and
spaced/punctuation-delimited real claims are unaffected. Space-adjacent `at all;` still（域：CORRECTION 2 自审注）
matches (only hyphen adjacency was removed). Frozen expectations invalidated: **0** — the（域：CORRECTION 2 自审注）
four positives' markers are all space-delimited（域：重跑证明 = evidence/round3/green/green_verdict.json）.

### C2.3 — D11 (quoted/frozen-line skip; marker-side NARROWING — mini-GREEN declared)

Implementation口径, frozen exactly:

- Quote spans on a line, matched left-to-right: paired backtick `` `…` ``; paired double
  quote `"…"`; paired 「…」. A double-quote opener with no closing `"` on the same line
  extends to end-of-line (evidence: `task_plan.md:732` JSON value quote); an unpaired
  backtick does NOT extend (inline-code density makes odd counts common in prose — declared
  asymmetry).
- A marker match whose span lies entirely inside any quote span is not a marker occurrence.
- If the trimmed line starts with `"`, `「`, `>`, or `*"`, the whole line is a quotation and
  all its markers are suppressed. A line starting with a backtick is NOT blanket-suppressed —（域：CORRECTION 2 自审注）
  the frozen positive `corpus/pos_round76_original.md:4` begins with `` `[^\s]+` `` yet
  carries a real claim（域：C2.3 正样本回归）.

**D11 narrows the detection surface**, so the parent-ordered small GREEN verification is
declared HERE, before the sample exists: file `evidence/correction2/quote_samples.md`,
layout = title/src/blank then payloads at lines 4, 6, 8, 10, 12, 14; expected flags =
**[12, 14]**（control lines with spaced markers outside any quote）; expected NOT flagged =
**4** (marker inside backticks), **6** (inside 「」), **8** (inside ""), **10** (line starts
with `>`); expected exit 1. In addition the full frozen corpus must still match
`oracle_table.json` exactly (round-3 GREEN re-run) — belt-and-braces, since D8b/D10b/D11
together touch both decision sides; RED and the 3 mutations are re-run in the same harness
pass for raw evidence, though the parent exempted them（域：论证沿用 CORRECTION 1 §C1.4 —
domain-side additions only shrink violations; marker-side skips shrink detections; neither（域：CORRECTION 2 自审注）
can create one, and every frozen positive's markers are space-delimited）.（域：CORRECTION 2 自审注）

