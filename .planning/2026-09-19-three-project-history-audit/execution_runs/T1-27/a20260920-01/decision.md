# T1-27 — decision record: append-block storage hygiene

**Attempt**: `execution_runs/T1-27/a20260920-01`
**Authority**: `OWNER_DECISIONS.md` §13 **T1-27** (TIER-1, owner-severable)
**Status of this attempt**: `planned` — **NOT** `accepted`.
**Headline**: all three halves of the mitigation are **in place and verified**. **No edit was made**
to any artifact — the mitigation is a *practice*, and this card's job is to confirm it is being
practised plus record the structural fix that removes the trigger.

---

## 1. The authority, verbatim

> | T1-27 | **第九节第 18 项：追加块存储脆弱性** | **采纳缓解建议**：**授权编排层更频繁地提交
> `.planning`**（关键 attempt 的追加块尽早入库），并在每次提交后强制核对 hook 的
> `[INFO] Restored changes from <patch>` 行。 |

And the risk it responds to, `OWNER_DECISIONS.md` line 108:

> 18. **【需你知悉】追加块的存储脆弱性**：M25–M28 的 `review.md` 基座现含漂移期文本，且追加的
> reviewer 裁决块**只存在于工作树**——一次 `git checkout -- .` 会把它退回已提交的纯基座并
> **丢掉追加块**… 同理，**若我再次提交后 hook 失败，未提交的 attempt 追加成果同样处于风险中**。

**The failure mode is not hypothetical.** It has already occurred once, recorded in
`execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`
(8505 B / `c326e38e489ff12d19d1481b7f2ef51cb26226094ebc6ad0d79dbcd34f36eb14`):

> 父 agent 的 `git commit/push` 作业触发仓库自带 pre-commit 门，该门 04:35:31 把未暂存改动导出
> 为补丁（557,924 B），随后 `git checkout -- .` 因 3 个被并发占用的 scratch 文件
> `unable to unlink … Invalid argument` **返回 255**，补丁**未被回放** ⇒ 生产工作树被重置到
> HEAD（`scripts/model_registry.py` 由锚定 `9ec65295…`/26446 B 变为 HEAD 版
> `1f2639e1…`/19703 B，本批四模型与 `driver_bounds` 机制整体消失）。

So the hook's contract is **stash → `git checkout -- .` → replay**. If **replay fails**, the
worktree stays reset to HEAD and the stashed content is **silently lost** from the worktree —
recoverable only from the patch file in `~/.cache/pre-commit/`.

---

## 2. The mitigation has three separable halves — all checked

The owner's sentence names two things (commit more often; verify the hook line after each
commit). The incident record names a **third**, structural, one (the root cause). Checking only
the named two would leave the trigger in place — so all three were audited.

Script: `scripts/audit_t27.py`.

| # | Claim | Result |
|---|-------|--------|
| **H-1** | key attempts' appended blocks reach the repository **early** (small exposure window) | **holds** |
| **H-2** | the hook's `[INFO] Restored changes from <patch>` line **was verified** after each commit | **holds** |
| **H-3** | the incident's **root cause** is structurally removed | **holds** |

### 2.1 H-1 — commit frequency (practised, not merely recorded)

| | |
|---|---|
| commits touching this plan (all time) | **41** |
| most recent | **`b9639b8c`** |
| this session's commits | **`3a7f9c2c`** (T1-6), **`b9639b8c`** (T1-14) |
| tracked-but-uncommitted files under the plan right now | 11 |

**Two commits, one per completed card** — not a batch accumulated to the end of the session.
That is the mitigation *in operation*: each card's appended block entered the repository as soon
as the card was complete, shrinking the window during which a failed hook replay could lose it.

The remaining 11 uncommitted files predate this session and are unrelated to T1-6/T1-14
(the `execution_v2/*` and `OWNER_DECISIONS.md` set already visible before this round).

### 2.2 H-2 — post-commit verification

| | |
|---|---|
| anchor `scripts/model_registry.py` | **`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`** — **intact** |
| this session's stash patches present | **yes** (`patch1789930457-49332`, `patch1789930650-30396`) |
| hook emitted `[INFO] Restored changes from …` on both commits | **yes, observed** |

Both commits printed:

```
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to C:\Users\郑曾波\.cache\pre-commit\patch….
ruff check …Skipped
mypy public contracts …Skipped
host assumption guard …Skipped
[INFO] Restored changes from C:\Users\郑曾波\.cache\pre-commit\patch….
```

**The `[INFO] Restored changes from …` line is present** — so the replay succeeded and nothing
was lost. Had only `Stashing` appeared, or had `Rolling back fixes` appeared, that would be a
**red alert** requiring: sample the production anchors → replay the patch's
`--exclude=.planning/*` subset → recompute → record the time.

**Stated limit — this is evidence, not proof.** A post-hoc audit cannot re-observe a past hook
line. What it *can* honestly assert is: the anchor is intact **now**, and this session's stash
patches are on disk. The per-commit check is a *discipline*, evidenced by those two patches plus
the intact anchor — not something a later script can replay. The JSON records this limit rather
than eliding it.

### 2.3 H-3 — the root cause, which is the part that actually matters

The incident's trigger was **3 embedded `.git` directories** inside attempts, which made the
parent repo recurse into them, report `fatal: bad object HEAD`, and destabilise the
stash/checkout sequence. Each is now covered by a **path-shaped** gitignore rule:

| embedded repo | covering rule |
|---|---|
| `I-06-A/a20260919-01/iso/ff/.git` | `*/a*/iso/` |
| `I-14-C/a20260919-01/r5/diff-apply-check/tree/.git` | `*/a*/r5/diff-apply-check/` |
| `I-14-C/a20260919-01/r5/diff-repo/.git` | `*/a*/r5/diff-repo/` |

**all 3 covered, 0 uncovered**, and `git status` reports **no `bad object`**.

**The embedded repos are still on disk — nothing was deleted.** Deleting an attempt's working
state would destroy evidence. What changed is that the parent repo no longer *traverses* them.
The `.gitignore` comment says so explicitly:

> They must never be versioned AND must never be traversed by the parent repository: an embedded
> `.git` makes git treat the directory as a submodule, which breaks `git status` / `git add` and
> made the pre-push hook's stash/checkout sequence fail.

**Why H-3 is the half that matters most**: H-1 and H-2 are *procedural* — they limit the blast
radius but leave the trigger armed. H-3 removes the trigger. **A procedure that has to fire
frequently is strictly worse than a cause that is gone**, and the owner's two-part mitigation,
taken alone, would have been exactly that: a discipline of re-checking after every commit,
forever, for a problem that could be deleted. It has been deleted (as a traversal hazard).

---

## 3. Why no edit was made

T1-27's two instructed actions are both **already in force**:

* **"授权编排层更频繁地提交 `.planning`"** — an *authorisation*, not a task to be scheduled.
  It is exercised by committing per-card (H-1).
* **"每次提交后强制核对 hook 的 … 行"** — a *standing discipline*. It was performed on both of
  this session's commits (H-2).

Neither is an artifact edit. The third half (H-3) was implemented earlier as a `.gitignore`
change that this card **verifies** rather than re-makes. Writing anything now would be
duplicating working state — the same reasoning as T1-14.

---

## 4. Standing discipline to carry forward

Recorded here so it is not lost:

1. **Commit per completed card**, not per session. (Practised this round: 2 cards → 2 commits.)
2. **After every commit, check for `[INFO] Restored changes from <patch>`.**
   * `Stashing` + `Restored` → normal.
   * `Stashing` but **no** `Restored` → **red alert**.
   * `Rolling back fixes` → **red alert**.
   On red alert: sample production anchors → replay the patch's `--exclude=.planning/*` subset →
   recompute → **record the time** (the window matters, because a hash taken inside it is a
   false alarm, not a finding).
3. **Never let the window be large for a card that is finished.** A finished card's block should
   be in the repository before the next card starts.
4. **Do not delete embedded scratch repos; ignore them by path shape.** The three rules above are
   the model — each maps to the directory that actually contains the `.git`.

---

## 5. Boundaries held

| Boundary | Check | Result |
|----------|-------|--------|
| No artifact edited | this attempt writes only its own files | **0 external writes** |
| No `.gitignore` re-edit | existing rules verified, not changed | **not written** |
| No deletion of embedded repos | all 3 still on disk | **intact** |
| Production anchor intact | `9ec65295…` | **match** |
| No product file touched | `git diff HEAD --name-only` | all under `.planning/` |
| No `status` transition | — | **none** |
| Emitted JSON parses | `json.load` | **OK** |

---

## 6. Next action

1. Independent reviewer confirms H-1/H-2/H-3 readings.
2. On confirmation, T1-27 is **discharged as a verified standing discipline** — no artifact
   change, and the discipline is recorded in §4 for future rounds.
3. **The pattern worth generalising**: two of this round's three cards (T1-14, T1-27) closed as
   *verified no-ops* — the requirement already held. The instinct to "do something" on receiving
   an authorisation is the failure mode those cards exist to resist. **Verify first; edit only
   if the verification fails.**
