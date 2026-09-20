## M08 · project_backlog — 独立 reviewer 裁决（owner 三步第③步，2026-09-20）

**verdict：accepted_scoped，范围＝仅 formula 资格。** `disclosure_adaptation = unmapped`、`accuracy = unproven` 维持不变；本裁决**不**授予披露适配或准确性，也**不**裁决其它任何卡。

**依据（全部本 reviewer 自行执行）：**
1. **索引更正＝读法 C 的带符号呈现，且只改了那一处。** 对四份 index 的前像与本 reviewer 实测现文件做**字节级 diff**（`m08a_diff.py`，前像取自 `execution_runs/M08/a20260919-01/recovery/owner_ruling_20260920_index_correction/pre_image__*`）：
   - 唯一变更区间（common prefix / common suffix 之外）在四份中**均为** 旧 `b'\xe2\x88\x9210'` → 新 `b'+\xe2\x88\x9210+'`，即 `−10` → `+−10`（3B → 5B，U+2212 未变）。文件字节各 +2：6243→6245、166010→166012、440393→440395、660318→660320。
   - **重建校验**：`now_prefix + pre_region + now_suffix == pre` 四份**全部 True** ⇒ 除该 2 字节处外**无任何其它字节变化**。
   - 现文件行：`card_M08.md:42` = `手算：100+40−5+−10+−15−60=50；−15重估必须剔除。 **期望输出：`[50]`。**`；`model_cards.md:552` 同句；`model_cards.json:1930` 与 `dispatch.json:5755` = `"independent_hand_work": "100+40−5+−10+−15−60=50；−15重估必须剔除。"`。
   - 唯一性：旧片段在 pre 中各命中**恰 1 次**，新片段在 now 中各命中**恰 1 次**。本 reviewer另核 `100+40−20=120`（另一模型的算式）**未被触碰**（无 `'100+40-5+10+-15-60=50'` 连字符变体、无第三方片段位移）。
   - 现 hash 四个**全部等于**更正后值：`card_M08.md 352585e94146fd10…`、`model_cards.md 63bca6bada3b4bf0…`、`model_cards.json a9f569f2bea8b6ce…`、`dispatch.json 0126acb61a8ef2e7…`；两个 JSON `json.load` 均 OK（dict）。
   - 该修正确实是读法 C：`−5`（取消）`+−10`（合同变更，带符号相加）`+−15`（重估，带符号相加）`−60`（期末），与 `scripts/model_registry.py:228` formula 串及 `_project_backlog`（fsum 中 `+drivers["contract_changes"]`、`+drivers["backlog_remeasurements"]`）一致；`[50]` 未变。
2. **同一 `code_root` 复跑通过。** `m08b_rerun.py`，在 %TEMP% 复本上以 `--code-root <scratch>/iso/checkout_scripts` 运行同一 `scripts/run_card.py`：
   - `iso/checkout_scripts/model_registry.py` sha256 = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`（＝绑定值）；`model_extensions.py` = `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`；runner = `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`。
   - **raw rc = 0**；`positive actual [50.0]` vs frozen `[50.0]`，`tolerances_ok True`；continuity ok；`defaults ok: True actual [65.0] expected [65.0]`；负例 **11/11 PASS_rejected**；观测 `OBS-SIGN-B=85.0`、`OBS-SIGN-NEG=55.0`、`OBS-REMEASURE-USED=65.0`（与 defaults 不同）——与 r1/r2/r3 行为完全一致。
   - 冻结运行件**逐字节未变**：`input.json 5f1ab943…`、`oracle.json 2264f673…`、`cases.json 57459a8f…`、`run_result.json 83015b9d…`、`negative_results.json 9bebe733…`、`qualification.json 42abe40d…`、`decision.md 42124934…`、`binding.json f376b719…`、`handoff.json 2ea09d4f…`、`commands.json 92875088…`（复跑前后对照，全部 unchanged=True）。
   - 留档（**新文件名，未覆盖任何既有记录**）：`execution_runs/M08/a20260919-01/recovery/rerun_after_owner_correction_20260920/` — `rerun_run_result.json`(24176B)、`rerun_stdout.txt`(2690B)、`rerun_summary.json`(4185B)。
3. **owner 裁定链完整。** `OWNER_DECISIONS.md` sha256 `380c1d96…`：§四 L60 三步条 + §十 L116 **原话逐字**「…M08 三步照办；…」 + §十裁定表「**M08 三步 ｜ 照办** … ③reviewer 用**同一 `code_root 9ec65295…`** 复跑留档 ｜ **M08 解除 blocked（待复跑通过）**」。PERMANENT provenance event 见 `recovery/owner_ruling_20260920_index_correction/{PROVENANCE.md, provenance.json}`（含前后 sha256/行号/字节数与四份前像），且已随提交 `b07d9b95` 入库（`git show --stat`：11 files，4 个 index 各 `2 +-`，其余为新增）。
4. **追加式治理保持。** 四份 `oracle.md` 的 v1 冻结体前缀仍逐字节相同（`sha256(raw[:8774/7482/7645/12557])` ＝ `ae1986f6…/d335f5ec…/1eeb6806…/47481cab…`，四份 MATCH=True）；`## 修订 r2` 计数仍为 1；r3 内容被 **re-render** 为更精确的版本并落在 `recovery/docfix-r3/oracle_merged_M0x.md`（现与在盘 `oracle.md` 逐字节相同）。新 r3 正文已**采纳本 reviewer 的 F-R3-01**：明写"本节由修订 r3 **插入**"，并给出正确字节账 `19745 − 3585 + 4156 = 20316` 与重建等式 `live = pre[:16160] + 本节`。**冻结期望零变化**：M05 `[620]/[550,880]/[600]`、M06 `[23]/[23,44]/[20]`、M07 `[122]/[122,165]/[120]`、M08 `[50]/[50,0]/[65]` 与预注册（`2a6398ed…`）逐一相等，负例四卡仍 11/11。

**重新绑定（供后续卡对账）——更正后的四个 index sha256：**
| 文件 | 行 | sha256（新，权威） |
|---|---|---|
| `execution_v2/card_M08.md` | 42 | `352585e94146fd1019df3c2bd8e2923c5d152f1fa10d7c0f2077801a044786e4` |
| `execution_v2/model_cards.md` | 552 | `63bca6bada3b4bf0202370b189462bd4bcd3050dfe0f217c066679afe9001710` |
| `execution_v2/model_cards.json` | 1930 | `a9f569f2bea8b6ce316b745d49bd08ca72c9acc30249750ee71d58be553b4179` |
| `execution_v2/dispatch.json` | 5755 | `0126acb61a8ef2e7d3a01185a900a67ddc5f9bea7bd91da856a465d1e8a82069` |

**本裁决不覆盖：** M05/M06/M07 的三资格维持先前结论。**本 reviewer 不自行改写 `qualification.json` 的 formula 状态**（避免自签）；由实现者在转录本裁决后按常规落 `formula = accepted_scoped`（仅 formula）并保留另两栏。`handoff.status` 由 `blocked` 转正常态同此。

**发现（不阻断）：**
- **F-M08-R1（P2）**：`execution_v2/validation.json` 旧 hash 快照 4 个键全部过期（index 更正导致），建议重跑刷新。
- **F-M08-R2（P3）**：历史载体旧 hash 应保持原样；`card_conflict.json` 记的是更正前值，勿当权威。
- **F-M08-R3（P3）**：四份 `oracle.md` 已被 r3 re-render（hash 已变），请以新 hash 作为当前值。

**未验证：** r3 re-render 脚本本身；`OWNER_DECISIONS.md §十` 其它裁定项的落地；`validation.json` 重跑后是否新增其它 errors；73/73、61/61 计数；`M05-M08` 批目录与 HEAD 逐文件比对。
