# T1-13 — decision record: I-09-A `review.md:80` citation-column repair

**Attempt**: `execution_runs/T1-13/a20260920-01`
**Card under test**: `I-09-A` / `a20260919-01`
**Authority**: `OWNER_DECISIONS.md` §13 **T1-13** (TIER-1, owner-severable)
**Status of this attempt**: `planned` — **NOT** `accepted`.
**Headline**: the authorised edit **already existed in the worktree but was uncommitted and
undocumented**. This card verifies it against T1-13's three boundaries, supplies the
pre-image hash + diff the owner required, and records the provenance that makes the edit
**legitimate rather than a silent rewrite**.

---

## 1. The authority, verbatim

> | T1-13 | **第八节第 13 项：I-09-A 的 `review.md:80` 出处列** | **授权改该行出处列**以实现
> 闭合。**边界**：只改该行的**出处列**，不动任何数值、不动 reviewer 其余字节，改动须附
> 前像 hash + diff。 |

Three boundaries, each severable, each checked:

| # | Boundary | Check |
|---|----------|-------|
| B-1 | 只改该行的**出处列** | row's other cells byte-identical |
| B-2 | **不动任何数值** | metric cell byte-identical **and** its numeric multiset preserved |
| B-3 | **不动 reviewer 其余字节** | every other line byte-identical; line count unchanged |
| — | 改动须附**前像 hash + diff** | `t13_changes.diff` + both hashes recorded |

---

## 2. State on arrival — the edit was present but unowned

This is the substantive finding of this card, and it changes what the card *is*.

At the start of this attempt:

* `review.md` carried an **uncommitted** worktree modification (`+445 B`, one line);
* **no `T1-13` attempt directory existed** — the edit had no decision record, no boundary
  verification, and **not the pre-image hash + diff** that T1-13 explicitly requires.

So the edit had been made without the paperwork the owner conditioned it on. This card
**supplies that paperwork**, and — more importantly — establishes **why the edit is
permitted at all**.

### 2.1 Why the edit is legitimate (B-4 — the direction-of-trust check)

Editing a reviewer's bytes is only defensible if the pre-image is **known to be defective**.
That is established here from three independent on-disk sources:

**① `errata.md` section R-1 declares the defect and names this exact minimal fix:**

> | **`review.md:80`（§4 数据表行）** | **仍是旧措辞**… **该行保持原样、未修**（其行末"注"已披露 270 行的后续读数，但**出处与数值仍不可互证**） |
>
> **未修理由**：本轮边界为"**只许追加**"，且 `review.md` 的既有字节（含 reviewer 自行追加的
> §R）**不得改动**；**若 owner 允许改 `review.md`，最小修法是仅改 `:80` 的出处列**（改为
> "本 attempt 期间一次快照读数，该文件其后被重抓"）。

**② `handoff.json` records it as a defect left to the owner:**
`review_round_3.known_gaps[0]` = *"`review.md:80` still pairs '132 lines / 126 real entries' with a
source file that now holds 270 lines; declared UNFIXED by errata.md section R-1 and **left to the
owner** (fixing it would require editing bytes the reviewer owns)"*.

**③ The pre-image still carries the defective citation**, verbatim:
`` `before/git_status_before.txt`、`after/git_status_after.txt` `` — i.e. it cites
`after/git_status_after.txt` (now 270 lines) as the source for the `132 / 126` reading, which
that file **no longer reproduces**.

**The reasoning chain closes:**

1. `errata.md:319` says the fix is *permitted only if the owner allows it*, and says the minimal
   fix is *"change only line 80's citation column"*;
2. `handoff.json` records the item as *"left to the owner"*;
3. **T1-13 is precisely that allowance**, and its boundary is **the same minimal fix** —
   citation column only.

⇒ This is a **licensed repair of a declared defect**, not an unexplained alteration.
**B-4 holds.**

---

## 3. Verification — four propositions

Script: `scripts/verify_t13.py`.

| # | Proposition | Result |
|---|-------------|--------|
| **B-1** | only the citation cell of the row changed | **holds** — cells identical `[0, 1]`, changed `[2]` |
| **B-2** | no number changed in the metric cell | **holds** — cell byte-identical; numeric multiset `['148','142','132','126','124','270']` **identical** |
| **B-3** | no other reviewer byte changed | **holds** — changed lines `[80]`, 300 → 300 lines |
| **B-4** | it repairs a defect `errata.md` declared and left to the owner | **holds** — all six sub-checks true |

### 3.1 The three cells

Line 80 is a markdown table row with **three** ` | `-separated cells:

| cell | content | changed? |
|------|---------|----------|
| `[0]` | row label: `revenue-forecast \`git status\` 行数（…勘误 E-6 统一口径）` | **no** |
| `[1]` | **the measured values**: `before 快照 = 148 行 / 142 真实条目；after 快照…= 132 行 / 126…` | **no** |
| `[2]` | the **citation** | **yes** |

**B-1 and B-2 are checked separately on purpose.** "Only the citation column changed" and "no
number changed" can fail independently: a new number could be *introduced into* the citation
column while the column-level check still passed. B-2 closes that by asserting the **metric**
cell — where the measured claims live — is byte-identical *and* that its numeric multiset is
unchanged. Both hold. **The measured claims `148/142/132/126/124/270` are untouched.**

### 3.2 Hashes (the owner required the pre-image hash)

| | |
|---|---|
| **pre-image** (`git show HEAD:<path>`) | `ab551696ce50f78221104c9cbebd3d775d9f84550d18cb9160d2224222ddb960` / **34110 B** |
| **post-image** (on disk) | `9fafca93adf8820fabe60d0425dec71057f6417a35785c57506e33320d98d45c` / **34555 B** |
| delta | **+445 B**, one line |

Attachment: **`t13_changes.diff`** (1810 B / `76ef3e16cc67e78cc943174310cfc269e239750c7283c35cc84dba96c7682696`) —
records both hashes and the single-cell replacement.

---

## 4. An error made and corrected in this card

The first run of `verify_t13.py` printed **`FATAL: line count changed`** — a false alarm.

**Root cause**: `REPO = EXEC.parents[1]` resolved to `<root>/.planning`, **one level too high**
(it should be `EXEC.parents[2]`). The relative path was therefore computed against the wrong
base while `cwd` was the real repo root, so `git show HEAD:<wrong-path>` returned **empty
stdout** — and the empty pre-image then tripped the line-count guard, which reported a
*content* problem that did not exist.

**Two fixes applied:**

1. `REPO = EXEC.parents[2]`, with the off-by-one documented in a comment;
2. A **path sanity guard** (`git rev-parse --show-toplevel` must equal `REPO`) and an
   **empty-pre-image guard** that fails loudly (`rc=2`) instead of falling through to a
   misleading verdict.

**This is the same class of mistake as the T1-6 path-depth bug** (`RUN.parent / "M24"` giving
`T1-6/M24`). Two occurrences in two cards is a pattern, not bad luck — hence the guard is
**structural** (it refuses to run against a wrong root) rather than a corrected constant that
the next script would have to rediscover.

**The lesson generalises**: *an empty result and a negative result must never share a code
path.* The guard now distinguishes "I could not read the input" from "the input says no".

---

## 5. What this card therefore delivers

| Item | Status |
|------|--------|
| B-1 / B-2 / B-3 boundary verification | **PASS (3/3)** |
| B-4 legitimacy (direction of trust) | **PASS** |
| pre-image hash, as required | **supplied** |
| diff, as required | **supplied** (`t13_changes.diff`) |
| attempt record | **created** (this file + `handoff.json`) |

**No new edit was made.** The worktree edit that already existed was verified, not authored.
If the reviewer prefers the wording be adjusted, that is a fresh edit requiring its own
authorisation — this card certifies *the existing* edit against the stated boundaries.

---

## 6. Boundaries held

| Boundary | Check | Result |
|----------|-------|--------|
| Only line 80's citation cell changed | B-1/B-2/B-3 | **exactly so** |
| No number changed | B-2 | **metric cell byte-identical** |
| No other reviewer byte changed | B-3 | **changed lines = [80]** |
| No edit to `errata.md` / `handoff.json` / `binding.json` / `oracle.md` | read-only | **0 writes** |
| No product file touched | `git diff HEAD --name-only` | all under `.planning/` |
| No `status` transition | — | **none** |
| Emitted JSON parses | `json.load` | **OK** |

The only files this card writes are its own, inside its own attempt directory.

---

## 7. Next action

1. Independent reviewer confirms B-1…B-4 and accepts the licence chain in §2.1.
2. The `review.md` edit should then be **committed** — it has sat uncommitted, which is itself
   the exposure T1-27 warns about.
3. **Note for the reviewer**: `errata.md` §R-1's "known gap" entry and
   `handoff.json.review_round_3.known_gaps[0]` now describe a defect that has been repaired.
   Per T1-12 ① form, those should be **superseded by an additive note** — *not* rewritten.
   This card does **not** make that change (outside T1-13's authority).
