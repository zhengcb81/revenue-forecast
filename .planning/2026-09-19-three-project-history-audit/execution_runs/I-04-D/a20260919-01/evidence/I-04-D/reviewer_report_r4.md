# I-04-D r4 stable-seal final point review — VERDICT: `accepted_scoped`

Reviewer: independent (delegated subagent). My writes: `%TEMP%\i04d-review-20260920-045256\` only.
This verdict **supersedes** my r1 `changes_required` (04:5x) and my r2 `changes_required`.
Final frozen revision (my samples 2026-09-20 05:34:15–05:35:11 local; local = UTC+1):

```
review.md        37191  81516b2ac06a41dca5978e744b540f8b2f33d7ba28297e7c792c32f9c50fcf09
handoff.json     55936  733cb40d29d6d11dc369fb81a60fc7822639ac839c98b880d4970e75e41687f6
oracle.md        42257  428a0a96a4faf12c4cff9aa625ed9c731d9e2e86ff43e5e2afe84cdbaa623f1d
evidence/hashes.txt 3977 9f6810bbc4e9225c93c5a81796ddf47aae5df6ed596c6b4509a56318906f0df1
iso/.../fetch_filing.py   126274  a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198
iso/.../i04d_schedule.py   35388  fd163a2702866ce0fe4988e962179c3f67c8adc9d2d01480f04f7f4439044ae2
iso/.../tests/test_fetch_filing_lease.py 30422 27f492b15e33031300e8ecd7946919258f4ff24df16eb72e6dfc895578a4056d
after/scheduler-run-final.txt 5002 3df2bcc376737ec401c0cabbf3e521939477ca26d94290452b7dc9d783fcebea
after/i04d-suite-final.txt      206 6503819d16fe609fd08f1e0541a70fe4353ffd3cb80fffb809ed7c4503e129a0
after/stable_seal_proof.txt     203 def44bf2642d1b504592418af7ddfd15853e2b34002b853a5af10ecf8f9d405b
recovery/r2_corrections.md     1385 7d080f684138f6eea705a35059e6ce93e245e6cbcd934377ea4fee2d780e7ead
```

## 1. My fixed checklist — every item run by me on the sealed bytes

| # | Item | My independent result |
|---|---|---|
| ① | ≥2 min zero writes after the seal | **PASS under a stated predicate.** Seal mtime 05:31:21.623 local = `2026-09-20T04:31:21Z` (matches `sealed_at_utc`). Literal `files_newer_than_seal` = **1**; the single file is `after/stable_seal_proof.txt` (04:33:37Z), i.e. the proof artifact itself. **Predicate ZW(s, E): "no file under `<A>` other than the members of E has mtime > s"**, with `s` = the seal's mtime and `E = {after/stable_seal_proof.txt}` ⇒ **0**, held across my samples at 04:34:15Z, 04:34:24Z, 04:35:11Z (≥3.8 min). Note the proof file is written at 04:33:37Z, one second *after* its own recorded `checked_at_utc 04:33:36Z` — document the predicate this way; the unqualified "zero writes" is false literally (as the parent's naive count correctly showed). |
| ② | manifest row-by-row vs disk | **PASS.** `hashes.txt` 3,977 B = **47 lines = 16 header (`#`) + 30 data rows + 1 blank** ⇒ the claimed `rows: 30` means **data rows**; the parent's "46 non-empty lines" = 16 + 30, same file, both correct. All **30/30** data rows match sha256 + byte size; there is **no self-referential row** for `hashes.txt`, which is why `structure_failures: NONE` is achievable. |
| ③ | all `*.json` parse (my own run) + handoff digest fields | **PASS.** My own full-tree parse: **825 `*.json`, 0 failures** (scope: all of `<A>`; the exclusions `venv/site-packages/__pycache__/.i04d-test-runs` matched nothing). Their `after/all_json_parse_check.txt` (489 B, mtime **05:24:16.502**) records `checked_ok: 763` — that count is a **stale snapshot taken before the r4 evidence re-run** added ~62 case JSON files; the fact it asserts still holds at 825/825 (P3 bookkeeping, see §3). `handoff.json` parses (52 keys) and — verified by me — **does not claim its own hash**; `defect_ledger_count = 10`; `ready_for_stable_seal = true`, `ready_for_r3_review = false`. |
| ④ | `evidence/run/` + suite produced by the **final** harness bytes | **PASS.** Final scheduler `fd163a27…` mtime 05:23:26.921; all **19** `evidence/run/*/summary.json` are newer (05:27:53.254–05:28:08.228). My own re-run with those exact bytes: **rc=0**, 19/19 `harness_error` empty, **18/19 identical on every protocol observable**; the single difference (F-L8g-UNKNOWN) is only the scheduler's own pid embedded in the case's synthetic ledger (`pid 35572` vs my `30536`) and therefore its sha256 — a per-run artifact, not a divergence. Suite: `after/i04d-suite-final.txt` = `21 passed`, rc=0, and **my own run on the final bytes = 21 passed, rc=0**. Stale generation preserved separately (`evidence/run-r2-stale/`, `after/i04d-green-r2-stale.txt` = `f8220c7d…`), so nothing was overwritten silently. |
| ⑤ | moved markdown still line-identical | **PASS.** `recovery/r2_corrections.md` vs the appended literal in `scratch/rework_r2_final.py`: **15/15 non-blank lines identical, same order**; bytes differ only by blank-line padding (byte-level equality was already narrowed to content equality). The file's sha256 `7d080f684138f6ee…` equals the `appendix sha256` recorded at move time in `after/handoff_json_revalidation.txt`. |
| ⑥ | production + `reviews` restated at my sampling time | **PASS** (05:35:00 local): `filing-fetch/scripts/fetch_filing.py 046cc7dc4e3ff2f4…`; `company-wiki …/control.py 553a35607be39c57…`, `store.py 1a7832404c39da85…`, `cli.py fad88c60294a7fb7…`, `lock.py 2303d3e5a4a79007…`; `catalog.sqlite3` 49,677,344,768 B @ `2026-09-19T06:31:35Z`; `catalog.sqlite3-wal` 0 B; `<PLAN>\reviews` dir mtime 2026-09-19 09:14:20.083, 12 top-level entries, recursive newest file `final_review_checks.json` @ 2026-09-19 10:05:32.273. (Some `reviews` sub-directories carry pre-existing ACL denials; not my writes.) Only read-only git was used. |

Additional verifications: F-L5 coexistence still measured on the sealed evidence (pause=1, resume=1,
A=`released_last`, B=`released_joined`, `B.after_enter.lease_set` = two leases, `generation=1`); the
two in-place edits inside the `oracle.md` append region are disclosed in
`handoff.oracle_frozen_region_in_place_edits` with the front image (the frozen §0–§4 body is
untouched); `review.md:141` now reads **10 项**.

## 2. Granted scope

r1's seven granted items (isolated deterministic build; `changes.diff` scope/paths/reproduction; 19
reproducible barrier cases; protocol behaviour in the non-gate cases; real multi-process; production
zero-change + `reviews` untouched; RED-first substance) **plus** the r2/r4 additions: the gate matcher
honours the named point (verified by my own unnamed-point probe); the contract suite is **green 21/0
rc=0** and RED over the **delivered** suite is **18F/1P/2S rc=1**; the F-L6b/W1b invariant-only
assertions are **not trivially satisfiable** (my own single-point M5 mutant makes the suite red,
`assert 0 == 1` at `:103`); immutable evidence generations are preserved; the seal is stable under the
stated predicate; the manifest is self-consistent with no self-row; `handoff.json` is valid JSON and
does not self-attest; and the moved corrections are content-identical.

## 3. Not granted / carried reservations (unchanged, not blocking)

1. **No implementer-side mutation proof**: M1–M11 unrun; the only mutation evidence is my
   reviewer-side M5 counterexample. ⇒ *no assertion is proven falsifiable by the delivery itself.*
2. N5/N6/N7 still have **no scheduler-level record** (unit assertions only).
3. No dedicated **live third-party owner** case.
4. No deterministic case for **A's release concurrent with B's acquire** (F-L6b degenerates to
   sequential cycles in every observed run).
5. POSIX/`fcntl.flock`, SMB/NFS, real company-wiki worker, real catalog concurrency, providers and
   network: never executed.
6. `oracle.md` R2-3 (owner ruling on "owner record present but no lineage evidence") is **handed over
   unsigned**; not a sign-off condition for this card.
7. P3 bookkeeping (recorded, not blocking): the parse-check artifact's `checked_ok: 763` is a stale
   05:24:16 snapshot (my count on the sealed tree: 825, 0 failures); the seal-proof file's own write
   (04:33:37Z) postdates its recorded `checked_at_utc` (04:33:36Z), so "zero writes" is only true
   under predicate ZW above; and the r3 in-place edits inside the oracle append region mean the
   "content-append-only" property I certified for r2 no longer holds (disclosed, with front image).

## 4. Why the r2 §11 block was never appended, and the §9 area

`handoff.json.r2_verdict_append_blocked = {appended: false, blocked: true, reason: …}` — correct and
verifiable: my r2 block was conditioned on `review.md` being 36,996 B / `c47770ea…`, and the r3
rewrite changed it (now 37,191 B / `81516b2a…`), so appending would have broken the prefix rule.
For the record: `review.md` **does** contain a reserved reviewer verdict area — `## §9 判决栏（留空，
只允许 reviewer 填写）` with an empty `verdict/reviewer/date/scope_of_acceptance/still_required/
reserved_cases` fence — but **no reviewer verdict had ever been appended** to this file before now
(my r1 §10 and r2 §11 were both blocked by the same prefix rule). The block below is therefore the
first reviewer verdict to land in `review.md`.

## 5. Paste-ready block for `<A>\review.md` (append-only)

Precondition: `review.md` must be **37,191 B** and hash
**`81516b2ac06a41dca5978e744b540f8b2f33d7ba28297e7c792c32f9c50fcf09`**. If not, STOP — the tree
moved. After appending, publish the new size + sha256 and verify the previous bytes are an **exact byte
prefix** of the new file (r2 proved that a whole-file rewrite can change line endings while preserving
content, so only a byte-prefix test is conclusive).

```markdown
---

## §10 独立验收最终裁决（reviewer；本裁决**取代** 04:5x 的 r1 `changes_required` 与我随后的 r2 `changes_required`）

verdict:            accepted_scoped
reviewer:           independent reviewer (delegated subagent；scratch %TEMP%\i04d-review-20260920-045256)
reviewed_revision:  review.md 81516b2a…(37191B) / handoff.json 733cb40d…(55936B) / oracle.md 428a0a96…(42257B)
                    / evidence/hashes.txt 9f6810bb…(3977B, 30 data rows) / iso impl a72546c5…(126274B)
                    / iso scheduler fd163a27…(35388B) / suite 27f492b1…(30422B)
                    / after/scheduler-run-final.txt 3df2bcc3… / after/i04d-suite-final.txt 6503819d…
                    / after/stable_seal_proof.txt def44bf2… / recovery/r2_corrections.md 7d080f68…
sealed_at:          2026-09-20T04:31:21Z（= 本地 05:31:21；与 hashes.txt mtime 一致）
sampled_at:         2026-09-20 05:34:15–05:35:11 local

### 授予的资格（全部由 reviewer 独立复算）
1. 隔离实现可复现：dc593a75…(56405B) + patch_i04d.py(a730362c…) → a72546c5…(126274B)，逐字节相同；
   基线 hash 不符时 patcher 拒写；changes.diff 4 added/0 removed/1 modified、POSIX 相对路径、
   reviewer 重算内容一致（归一化 dd769819…）。
2. gate 缺陷已修并被我独立证明：`fetch_filing.py:999-1000/:1007-1012` 要求 `name == point`；
   reviewer 自造探针（`gate:NO-SUCH-POINT@A`，fence 预置）不产生 `.reached`、rc=0、stderr 0 字节。
3. 契约套件 **21 passed / 0 failed, rc=0**（reviewer 在最终字节上自跑）；RED 是对**交付版套件**所出：
   同字节基线 dc593a75… → **18 failed / 1 passed / 2 skipped, rc=1**（reviewer 自跑，与
   before/i04d-red.txt 一致；当次套件已存档 before/test_fetch_filing_lease.delivered.py）。
4. 主证据由**最终 harness 字节**产生：19 例 summary mtime 05:27:53–05:28:08 全晚于
   scheduler fd163a27…(05:23:26)；reviewer 用相同字节重跑 **rc=0**，19/19 harness_error 为空，
   18/19 全部协议可观测量逐一相同，第 19 例（F-L8g-UNKNOWN）仅"调度器自身 pid 写入合成账本"
   导致 pid/sha 不同；旧世代保留在 evidence/run-r2-stale/，未被覆盖。
5. F-L5 共存性：pause=1/resume=1、A=released_last、B=released_joined、
   B.after_enter.lease_set 两条同代(gen=1)租约。
6. 只断言不变量的 F-L6b/W1b 断言**非平凡**：reviewer 单点 M5 变异体（去掉 ADR-10e owner 移交，
   sha256 82b4fdc48f60…）令套件变红（`test_fetch_filing_lease.py:103`，`assert 0 == 1`）。该反例属
   reviewer 侧，不计入交付的变异证明。
7. 封盘稳定且自洽：清单 30 数据行 = 47 行文件 − 16 表头行 − 1 空行，**30/30 与磁盘一致**、
   无自指行；谓词 ZW = "除 after/stable_seal_proof.txt 外，<A> 下无文件 mtime > 封盘时刻" ⇒ 0，
   在 04:34:15Z/04:34:24Z/04:35:11Z 三次采样均成立（字面计数为 1，即证明文件自身，
   其写入 04:33:37Z 晚于其记录的 checked_at 04:33:36Z）。
8. handoff.json 合法 JSON（52 键）、**不自称自身哈希**、defect_ledger_count=10、
   ready_for_stable_seal=true / ready_for_r3_review=false；被移出的更正文本与追加原文
   **15/15 非空行逐行一致**（字节级不同，已在文档中收窄为"内容一致"），
   recovery/r2_corrections.md 的 sha256 与移动时记录的 appendix sha256 相同。
9. 生产三仓零写入与 `<PLAN>\reviews` 未写（reviewer 采样 2026-09-20 05:35:00 local）：
   filing-fetch 046cc7dc…、wiki 553a3560…/1a783240…/fad88c60…/2303d3e5…、
   catalog 49,677,344,768 B @ 2026-09-19T06:31:35Z、-wal 0 B；reviews 目录 mtime 09:14:20.083、
   递归最新 final_review_checks.json @ 10:05:32.273。reviewer 全程只用只读 git。

### 未授予 / 保留范围（照旧，未删未弱化）
- **无实现者侧变异证明**（M1–M11 未跑）：交付本身**没有证明任何断言可证伪**；唯一变异证据是
  reviewer 侧 M5 单点反例，最小清单 M2/M5/M8/M10/M4 仍待跑。
- N5/N6/N7 无调度器级原始记录（仅单元断言）。
- 无"存活第三方 owner"专用用例；无"A 释放与 B 获取并发"的确定性用例。
- POSIX(fcntl.flock)/SMB/NFS、真实 worker/catalog/provider/联网 未执行。
- `oracle.md` R2-3 的 owner 裁定项**原样移交**，不作为本卡签收条件。
- P3 记账：after/all_json_parse_check.txt 的 checked_ok=763 是 05:24:16 的旧快照
  （reviewer 在封盘树上实测 825 个 *.json、0 失败）；封盘证明文件自身写入晚于其 checked_at
  （故"零写入"必须按谓词 ZW 表述）；r3 对 oracle 追加区做过两处就地编辑（已在 handoff 登记并附前像，
  故 r2 时认证的"内容上只追加"自 r3 起不再成立；冻结 §0–§4 正文未受影响）。

### 关于 r2 裁决块未追加
r2 的 §11 块以 review.md = 36996 B / c47770ea… 为前提，r3 重写后该前提失效，
`handoff.r2_verdict_append_blocked` 已如实登记（appended=false）。本文件确实有 reviewer 裁决区
（§9 判决栏，此前一直为空），但**此前从未有 reviewer 裁决被追加进本文件**；本块是该文件中的
第一份 reviewer 裁决。

### 恢复规则
本裁决不改变生产仓任何字节，不删除任何临时 owner 状态，reviewer 未写 `<PLAN>\reviews`、
未运行任何 git 写命令；reviewer 的全部实验只在 `%TEMP%\i04d-review-20260920-045256\`。
后续接手者：先按 evidence/hashes.txt（30 数据行）逐行校 hash，再读 handoff.json
（ready_for_stable_seal=true / ready_for_r3_review=false）与 oracle.md R2-3（待 owner 裁定）。
```
