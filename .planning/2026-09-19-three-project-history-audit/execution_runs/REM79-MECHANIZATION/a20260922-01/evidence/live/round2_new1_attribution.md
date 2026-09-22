# Attribution of the single NEW round-2 finding (progress.md:990)

Fact base (all recomputable from this attempt's evidence):

- `task_plan.md` sha256 `4096a44d…bc687bf` and `findings.md` sha256 `5a6accc…fc8f5a` are
  **byte-identical** between corpus extraction, round-1 scan and round-2 scan
  (`evidence/live/round2_diff.txt` header + `round2_summary.json`
  `plan_hashes_unchanged_since_extraction=false` refers to progress.md alone).
  For these two files the round-1↔round-2 comparison is a pure lexicon comparison:
  task_plan.md 131 → 28, findings.md 37 → 10, **NEW findings = 0** — monotonicity of
  CORRECTION 1 (domain patterns only add, markers only narrow) holds exactly on
  unchanged bytes.
- `progress.md` **DRIFTED**: extraction-time sha256 `e86b91cc052e1d0cc6f103b3ad6e21b96a…`
  → current `efb213c845dab6e3…`, now 1001 lines. Its owner (the parent agent) edits this
  file continuously; round-1's highest flagged progress.md line was 967, round-2's is 990.
- The one NEW key is `progress.md:990 [全部] **交付批（全部 review_pending，零自签）**…`.
  Under the round-1 lexicon that text would have flagged had it existed at round-1 scan
  time (全部 marker, no round-1 domain: no 域/count/D7 enumeration). It is absent from
  the round-1 JSON, therefore the line did not exist — or not in that form — when round 1
  scanned. Attribution: **owner content added/changed between the two scans**, not a
  lexicon regression. CORRECTION 1 cannot create a violation on unchanged bytes by
  construction (see oracle.md CORRECTION 1 §C1.4) and the two byte-stable files prove it.

Caveat recorded honestly: because progress.md drifted, its round-1↔round-2 line-keyed
diff (disappeared/remained counts inside that file) may misalign if lines shifted above
the edit point; progress.md round-2 counts (10) are trustworthy as a fresh scan, its
disappear/cause labels are best-effort. The parent can re-adjudicate progress.md directly
from `evidence/live/round2_live_scan.txt`.
