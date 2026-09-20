# T1-14 — decision record: I-11-A OPEN-1 register verification

**Attempt**: `execution_runs/T1-14/a20260920-01`
**Card under test**: `I-11-A` / `a20260919-01`
**Authority**: `OWNER_DECISIONS.md` §13 **T1-14** (TIER-1, owner-severable)
**Status of this attempt**: `planned` — **NOT** `accepted`.
**Headline**: T1-14's substantive condition **already holds on disk**. **No edit was made.**

---

## 1. The authority, verbatim

> | T1-14 | **第八节第 14 项：I-11-A 两条 reviewer 独立意见** | **均采纳**：**OPEN-1** 允许
> `pdftotext.exe` 作**交叉核对路径**，**永不作为任何被引用数值的唯一来源**；须把绝对路径 +
> sha256 `252d2b34…` 写进 `binding.json`、**禁止为取文升级 Git**。**OPEN-8** 接受以
> `P1_vs_prior_offset.json` 择优规则为准，**不回改 oracle 正文**。 |

Decomposed into its four severable obligations:

| # | Obligation | Kind |
|---|-----------|------|
| O-1 | `pdftotext.exe` is allowed **only** as a cross-check path | policy |
| O-2 | It is **never** the sole source of any cited number | policy |
| O-3 | Its **absolute path + sha256 `252d2b34…`** must be written into `binding.json` | artifact |
| O-4 | **Upgrading Git to obtain text extraction is forbidden** | prohibition |
| O-5 | OPEN-8: adopt `P1_vs_prior_offset.json` as the tie-break rule; **do not edit oracle prose** | policy |

**O-3 is the only one that is a thing-to-do.** O-1, O-2, O-5 are standing rules; O-4 is a
standing prohibition. This card's action is therefore narrowly about **O-3**, with O-4
checked as a condition rather than performed as a task.

---

## 2. Finding: O-3 is already satisfied

`I-11-A/a20260919-01/binding.json` → `external_tools.pdftotext` already carries:

```json
{
  "path": "C:/Program Files/Git/mingw64/bin/pdftotext.exe",
  "version": "pdftotext version 4.00 (Xpdf, Copyright 1996-2017 Glyph & Cog, LLC)",
  "sha256": "252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0",
  "role": "independent second extraction path (no shared code with tools/pdf_text.py), read-only, no network",
  "registered_as": "OPEN-1 (owner sign-off on using a repo-external console tool)",
  "reviewer_opinion": "the independent reviewer recommends ALLOW but DOWNGRADE it to a cross-check path: fix the absolute path + sha256 here (done), never upgrade Git to obtain text-extraction capability, and note that strictly speaking it does not satisfy 'reproducible inside the isolated copy'; the restore rule in decision.md DEC-1 already handles a hash change"
}
```

The registered sha256 begins `252d2b34…` — matching the value T1-14 names.

**But "the field exists" and "the field is true" are different facts.** A register that
records a hash is worthless if the recorded hash is not the hash of the tool that actually
runs. So the register was **verified**, not merely read.

---

## 3. Verification — four propositions, each checked separately

Script: `scripts/verify_t14.py`. Each proposition is a distinct falsifiable claim, because
collapsing them would hide exactly the failure modes that matter.

| # | Claim | Result |
|---|-------|--------|
| **P-1** | `binding.json` registers an **absolute** path and a **64-hex** sha256 | **holds** |
| **P-2** | the registered sha256 **equals** the hash of the binary **actually at that path** | **holds** |
| **P-3** | the on-disk binary is **the version the register names** | **holds** |
| **P-4** | the Git install tree was **not modified after** the register was written | **holds** |

### 3.1 P-1 — the field is well formed

* `path` = `C:/Program Files/Git/mingw64/bin/pdftotext.exe` → drive-letter absolute, not relative;
* `sha256` = 64 characters, all hex.

A relative path would silently resolve against whatever cwd a future run happened to have —
the exact class of bug `I-00-B` was written to prevent. Absolute is therefore a substantive
requirement, not a formality.

### 3.2 P-2 — the register is *true*, not just *present*

| | |
|---|---|
| registered | `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0` |
| on disk | `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0` |
| size | `1537966` bytes |

**Exact match.** This is the proposition that gives O-3 its meaning.

### 3.3 P-3 — the hash is not "some file at that path"

`pdftotext -v` reports `pdftotext version 4.00`, matching the register's
`pdftotext version 4.00 (Xpdf, …)`. Without this check, a *different* tool could have been
swapped in at the same path **and** the register updated to match — the hash would agree
while the recorded version string became a lie. P-3 closes that gap.

### 3.4 P-4 — no Git upgrade was performed (evidence, with its limits stated)

| | |
|---|---|
| Git install tree mtime | **2025-11-08 10:56:42** |
| `binding.json` mtime | **2026-09-20 15:48:16** |
| gap | **≈ 316 days** |

The Git tree **predates** the card by nearly a year, so the card did not cause an upgrade.
Current Git is `2.55.0.windows.3`.

**Stated limit — this is evidence, not proof.** An in-place patch that preserved mtimes
would not be caught by this method. The proposition is reported as **held on the available
evidence**, with the caveat recorded in the JSON rather than suppressed. Claiming more than
the method supports would be exactly the kind of over-reach this project's discipline exists
to prevent.

---

## 4. Why no edit was made (the severability point)

The instinct on receiving T1-14 is to go write something into `binding.json`. **That would be
wrong**, for three separate reasons:

1. **The field already exists and already verifies.** Re-writing an identical value produces a
   diff with no information, and needlessly invalidates a frozen artifact's hash.
2. **`binding.json` is a frozen artifact of an attempt whose `handoff_status` is
   `review_pending`.** Writing into it would change what the reviewer is being asked to review,
   after the fact.
3. **The owner's authority here is to *decide* the disposition, not to author a redundant
   edit.** Executing a no-op edit would look like progress while changing nothing.

**Owner authority is permission, not obligation.** T1-14 says the path and hash *must be in*
`binding.json`. It is already there, and it is true. The obligation is **discharged**.

---

## 5. What this card therefore records

**A verification, plus a disposition** — not a change:

* O-1 / O-2 (cross-check only, never sole source): **standing rules, already reflected in the
  register's own `role` and `reviewer_opinion` fields**; no action available or needed.
* O-3 (absolute path + sha256 in `binding.json`): **SATISFIED** — verified by P-1/P-2/P-3.
* O-4 (no Git upgrade for extraction): **held** — P-4, with its evidentiary caveat recorded.
* O-5 (OPEN-8, do not edit oracle prose): **no edit made**; noted as a standing instruction.

All five dispositions are `no change required`. The card closes as a **verified no-op**.

---

## 6. Boundaries held

| Boundary | Check | Result |
|----------|-------|--------|
| No edit to `I-11-A/binding.json` | read-only; file mtime unchanged | **not written** |
| No edit to any I-11-A artifact | — | **0 writes** |
| No product file touched | `git diff HEAD --name-only` | all under `.planning/` |
| No Git install / upgrade | P-4 | **none performed** |
| No `status` transition | — | **none** |
| No proxy signature | — | **none** |
| Emitted JSON parses | `json.load` | **OK** |

The only file this card writes is its own `t14_register_verification.json`, inside its own
attempt directory.

---

## 7. Next action

1. Independent reviewer confirms the P-1…P-4 readings (in particular that P-2's match is
   against the binary's real bytes, not a cached value).
2. On confirmation, T1-14 can be marked **discharged as a verified no-op** — the substantive
   requirement holds and no artifact moved.
3. **OPEN-8 (O-5)** remains a standing instruction for future work on I-11-A: adopt
   `P1_vs_prior_offset.json` as the tie-break rule and leave the oracle prose alone. It is
   recorded here so it is not lost, but it requires no action now.
