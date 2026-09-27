# WC-1 / I-14-D-R8 handoff — a20260923-01

- card: **WC-1**（REGISTRY-CLOSURE 立卡，I-14-D r8 残差一轮：REM-06 / REM-67③=R3-05 /
  R5-08 / R3-07）｜attempt：`execution_runs\I-14-D-R8\a20260923-01`
- **status: `review_pending`** — NINE-STEP executed to the review gate; verdict authority =
  the independent reviewer. **`implementer_signed: false`**（本实现者不自签，不载验收语）.
- **`disclosure_adaptation: unmapped`**｜**`accuracy: unproven`**（canonical 缺省：本卡无对外
  披露适配映射；全部主张未经独立复核前一律 unproven）.

## Deliverables (8 + evidence)

| file | content |
|---|---|
| `oracle.md` + `oracle.sha256` | 4 residuals frozen BEFORE any run + dispositions chosen + rows/directions/sweeps/protocol + **CORRECTION W1**（append-only，pre-run pin prefix-proved）|
| `binding.json` | pins: WC-1 decision `a68ed77f…` spec sha, base `2f644994…`, production `edcbeccb…`, base tree `c5608c4b…`, harness bases `85a1b064…`/`8f5feffd…`, register `5348278f…`, oracle 双 pin（pre/post correction）, `changes_diff_sha256 baec3153…`, writes scope |
| `commands.md` | step-by-step command log incl. every failed attempt（rc + evidence pointers）|
| `decision.md` | per-item verdict table + spec citations + frozen-cell matrix audit + diff file list with before/after shas + disclosures + carried |
| `changes.diff` | 9161 B / `baec3153…` — 1 source file × 2 targets = 6 hunks: K1(REM-06 `key_is_credential`+`_KEY_TRAILING_DIGITS`) and K2(`_AUTH_SCHEME_SPLIT` value-delimiter prefix) |
| `evidence\` | RED/GREEN/base/mutant raw runs（json+stdout+rc）, both sweeps + count diag, production apply-check, prefix proof, build logs incl. failed attempts, `final_integrity.json`, `final_hashes.json` |
| `harness\` | freeze arithmetic, build, mutants, sweeps, diff builder, integrity (all re-runnable) |
| `recovery.md` | reproduction commands, scratch locations, undo facts, resume point |

## Per-item verdicts (detail + judged evidence in decision.md §1)

1. **REM-06 → fixed-with-rgm**（code）: digit-suffix normalization in `key_is_credential`
   (token2/secret2/password2/api_key2 通过原 split 规则解析) + 5/5 instrument rows +
   4 untouched counters（过度脱敏定价）. RED/GREEN exact；MUT-A kills exactly 5+5；key sweep
   old\new=∅ / new\old=114⊆digit-vocab（120−114 审计= `secret_key*` 本已 old-true）.
2. **R3-05 → fixed-with-rgm**（code，未走 registered_open，依父令「发现的缺陷都要全部修复」）:
   after-break value 可以以六种 value-delimiter 起始（quoted 先试、单行 N29 守卫不变）;
   RED/GREEN exact；MUT-B kills exactly 6+2；value sweep old\new=∅ / new\old=恰好六形；
   over-redaction 两行定价.
3. **R5-08 → fixed-with-rgm (record-level)**: 每仪器一行 marker 载荷行
   （rule `open-two-token-then-wrap-marker` / oracle `R3c-…`）→ `registered_open_leaking`
   与 `registered_open_confirmed` 现在都看得见 marker 形.
4. **R3-07 → closed-now-with-proof**: ③ 的补行使 C10 残差族同时携带 marker 与 non-marker
   （R3a/R3b `S39` + R3c marker，两仪器实测）; 封存 `handoff_r3.json` 未回改; 声明域在
   oracle 4d（R3b 无 marker 孪生=声明的不对称）.

Counts: rule 95→**113**；oracle 44→**61**；rule rc 3/negative 仍为 r3 起的 by-design
（不宣称 rc 0）；oracle r8_fixed rc 0.

## Lineage carried

- **I-14-D a20260919-01**（r6/r7 世代）: r7 verdict `accepted_scoped`
  （status authority `reviewer_report_r7.md` sha `cc6da8d3…` = sidecar，本卡重算一致）；
  r6 pins（tree `2f644994…`、harness `85a1b064…`/`8f5feffd…`、r7 counts 44/95）本卡全部
  重算复核后才动 r8 分支；**封存 attempt 零写入**（r8 harness = 本 attempt 新文件；
  树 = iso 复制）. handoff_r6 的 r7 block lineage + F-REV-R6-01..05 处置原样携带.
- **REGISTRY-CLOSURE**: spec 卡（decision `a68ed77f…`）；其 J1/J2 与本卡 K1/K2 同纪律
  （changes.diff-only，未落盘）. 其 42 条处置行中本卡承接 4 条（A2/A10③/C9b/C10f 路由）.
- **goal-item①**: 本卡关闭其最后残差面；**另记 context：goal-item① I-08-C 亦已经由 sibling
  `I-08-C-RESIDUAL` 关闭**（其 attempt `a20260923-01` 在盘，decision/handoff 可核）——
  两处合起来构成 goal-item① 的完整闭合叙事.

## carried / boundaries（随下游）

1. `changes.diff` **未应用**（sources read-only；落盘=下一批晋升/修批，owner 决定）.
2. WC-2..WC-6 未触碰（oracle §7 非目标）；I-14-C real-exit pytest 套件本卡未跑（会写
   company-wiki 测试目录→生产零写风险），声明为晋升批次的随行事项.
3. Value-start `\r \v \f`、delimiter+space、单行 delimiter 值 = 声明开放（oracle 4a）.
4. R3b marker 孪生缺失=声明的不对称（oracle 4d）.
5. CORRECTION W1 只更正一个误预测仪器格；行级冻结期望零改动（prefix proof 在案）.
6. 本卡零回改: 封存载体/生产源未动，登记册历史行未动（`evidence/final_integrity.json` 复核：
   sealed I-14-D 与 company-wiki/src 在本 attempt 创建时刻之后零文件改动；登记册在本卡
   session 内被**并行卡外部追加**——本卡命令日志无登记册写入，其引用行按行级逐条复核仍在
   = `register_drift`，见 decision §4.8）.

## reproduce (reviewer quick path)

见 `recovery.md` 的命令块；最短复核链 = `build_r8.py` → red/green 四跑 → 两 sweep →
`make_changes_diff.py` → `final_integrity.py`，全部 rc 归档于 `evidence/*.rc.txt`。
