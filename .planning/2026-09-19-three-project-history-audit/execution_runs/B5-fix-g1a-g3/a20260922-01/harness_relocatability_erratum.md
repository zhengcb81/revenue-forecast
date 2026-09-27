# harness_relocatability_erratum.md — B5 harness 可重定位性缺陷勘误 + 修复版脚本副本（原脚本不动）

- by：BOOKKEEP-REPAIR / a20260923-01（父派单 #19；AUDIT-DESIGN §0 审计事故根因 + 登记册 §72(3)「harness 可重定位性缺陷」）
- 对象：`execution_runs/B5-fix-g1a-g3/a20260922-01/scripts/verify_append_fixed.py`、`scripts/verify_boundaries.py`
- 形态：**追加式勘误文件 + `scripts_fixed/` 修复版副本**；**原脚本 0 字节改动**（before/after sha 自证，见 §3）。

## 1. 缺陷（事故根因，如实）

两脚本**内嵌绝对输出路径**：

- `verify_append_fixed.py:25-26`：`PLAN = r"C:\Users\郑曾波\…\2026-09-19-three-project-history-audit"`、`ATTEMPT = …/B5-fix-g1a-g3/a20260922-01`（常量）；`:162` `dest = os.path.join(ATTEMPT, "evidence", "start_here_append_proof_fixed.json")`。
- `verify_boundaries.py:22-26`：同族常量（`PLAN`/`ATTEMPT`/`B5`/`PROD`）；`:177` `dest = os.path.join(ATTEMPT, "evidence", "boundary_verification.json")`。

⇒ **重跑即写回历史 attempt**。AUDIT-DESIGN 审计事故（其 §0 自陈）：在 %TEMP% 副本上重跑时仍写回了原 attempt 的
`evidence/start_here_append_proof_fixed.json` 与 `evidence/boundary_verification.json`（已 %TEMP% 前像逐字节还原，
sha == B5 handoff:94-95 记录值 `7c4c95dc…`/`0aacaac8…`，净影响=两文件 mtime 变）——违反 `review_and_handoff.md:33`
「复制逻辑到新 attempt 输出目录并绑定当前代码」与「历史 rc 与其证据一律不动」纪律；任何人重放历史卡都会污染历史 attempt。

## 2. 修复（`scripts_fixed/` 副本；输出可重定位）

| 文件 | 修复要点 |
|---|---|
| `scripts_fixed/verify_append_fixed.py` | ①输出根 `OUT_DIR` = `argv[1]` > env `B5FIX_OUT_DIR` > 历史默认位；`dest` 改挂 `OUT_DIR`；②输入根 `PLAN` 可 env `B5FIX_PLAN` 覆盖；③文件头 banner 注明「RELOCATABLE-OUTPUT FIX COPY / 原脚本不动 / 重跑必须用本副本且输出指向新 attempt」 |
| `scripts_fixed/verify_boundaries.py` | 同上 + `PROD` 可 env `B5FIX_PROD` 覆盖 |

**重跑规则（明记）**：**重跑请用修复版且输出指向新 attempt**——
`python scripts_fixed/verify_append_fixed.py <新attempt>/evidence`（或 `B5FIX_OUT_DIR=<新attempt>/evidence`）；
校验逻辑、判据、常量钉值（PRE/POST1 sha、BATCH_SHA、PROD_SHA 等）**逐字未动**（diff 仅头注+输出路由行）。

## 3. 原值留痕（原脚本不动的自证）

| 文件 | before sha256（创建副本前） | after sha256（创建副本后复算） | bytes | 结论 |
|---|---|---|---|---|
| `scripts/verify_append_fixed.py` | `71dbaf29ced7529763343263f5442bc298ad893b7a680145d2a9a54f20c13603` | `71dbaf29ced7529763343263f5442bc298ad893b7a680145d2a9a54f20c13603` | 9980 | **逐字不动** |
| `scripts/verify_boundaries.py` | `e8f89b73a88ba19f23c10bc4607781afdf655af2b7750985f07bf62beadfbe88` | `e8f89b73a88ba19f23c10bc4607781afdf655af2b7750985f07bf62beadfbe88` | 10467 | **逐字不动** |
| `scripts_fixed/verify_append_fixed.py` | —（新建） | `658c852bd4e4e5d2bb6615a600843ce30616d2d8b941c55bee33578b3e8beb43` | 10618 | 修复版；`ast.parse` 通过 |
| `scripts_fixed/verify_boundaries.py` | —（新建） | `43d77933f962df2f88bf59c3ce4f4dac5e16c076a3ea994050282bc25f2a1dd2` | 11137 | 修复版；`ast.parse` 通过 |

## 4. 边界 + 登记行（供父折入 `REMEDIATION_REGISTER.md`）

- 本勘误 0 字节写入原脚本、既有 evidence（`start_here_append_proof_fixed.json`/`boundary_verification.json` 等）、任何产品树、任何 git 状态；修复版**未**在历史位执行（本 pass 不重跑两脚本）。
- 登记行：**B5 harness 可重定位性缺陷 = 修复版副本入册**——`B5-fix-g1a-g3/a20260922-01/harness_relocatability_erratum.md` + `scripts_fixed/`（输出 argv[1]/env `B5FIX_OUT_DIR` 可重定位；原脚本不动、before/after sha 自证）；**重跑规则=用修复版且输出指向新 attempt**；AUDIT-DESIGN §0 事故根因面收口。
