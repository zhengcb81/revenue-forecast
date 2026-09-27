# decision.md — M-T-REVIEW 合并裁定矩阵（card × clause-spots × verdict）

**卡**：M-T-REVIEW · **attempt**：`execution_runs/M-T-REVIEW/a20260923-01` · **角色**：独立审查员（sampled-verification
review agency，永不充任实现者）。**协议**：`oracle.md`（先于首检冻结，sha256 `ef68aaaf3e161dc0a88e35ef0503fc54336cd0bf1b4de650f090c3d16c851da9`）。

## 0. 合并矩阵（全 53 裁定 + 6 登记行）

子句列语义（M 卡）：① 期望输出三方一致（spec 期望输出 == oracle.expected_float == handoff.positive_expected）
② 负例全拒 `ModelRegistryError` ③ A–C 九件证据齐 ④ qualification 只动 formula（其余两栏未授予）⑤ 无产品重写。
T1 卡的子句列 = 裁定原文 3–5 子句 vs decision.md 命题表（全 = ✅，余项在 carried 列）。
pin = 固定抽样 hash 复现（raw/CRLF 形态如实记）。逐卡详证 `reviews/M01.md…M20.md`、`reviews/M21-M31_sampled.md`、
`reviews/T1_rulings.md`；逐项机器证据 `evidence/*.json`。

| 卡 | ① | ② | ③ | ④ | ⑤ | pin | VERDICT | carried / 关键备注 |
|---|---|---|---|---|---|---|---|---|
| M01 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03；首冻 hash 永久缺口 |
| M02 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03；F-M02-01 已裁（T1-16）待追加注记 |
| M03 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03；冻结体改动轮次不可复算 |
| M04 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03；PROPAGATE 批采信 |
| M05 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03/04/05（r2 态由本裁定验收） |
| M06 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 同 M05 |
| M07 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 同 M05 |
| M08 | ✅ | ✅ | ✅ | ✅ | ✅ | 2/2+repack 账本 | accepted_with_conditions | T1-15 闭环；transcription 字段对齐；D 域不裁定 |
| M09 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | F-MT-02/03/04（卡内裁决区补录） |
| M10 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | F-MT-02/03/04；mtime 腿记录态为凭 |
| M11 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 同 M10 |
| M12 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 同 M10 |
| M13 | ✅ | ✅ | ✅ | ✅ | ✅ | 2/2+repack 账本 | accepted_with_conditions | handoff cases pin 陈旧（追加注记） |
| M14 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | F-MT-02/03 |
| M15 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 同 M14 |
| M16 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 同 M14 |
| M17 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | F-MT-01/02/03/04/05（r2 态由本裁定验收） |
| M18 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 同 M17 |
| M19 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 同 M17 |
| M20 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 同 M17；D/E/F 域明示未验 |
| M21 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 深验：round-3 终裁 `aee6d601…` |
| M22 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 点名 `05f5fe10…` |
| M23 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 点名 `bd76f105…` |
| M24 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 点名 `5ff44927…`；round-2→3 自认 |
| M25 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 深验：r2 块 + 生产回滚窗登记 |
| M26 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 点名 r2 块 |
| M27 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 点名 r2 块 |
| M28 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 LF | accepted_with_conditions | 点名 r2 块 |
| M29 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 点名 `58e614d5…`；缺 positive_expected 键 |
| M30 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 点名 `dfb854b4…` |
| M31 | ✅ | ✅ | ✅ | ✅ | ✅ | 3/3 CRLF | accepted_with_conditions | 深验：`c57d5006…`/`f41b2fc7…`；T1-23/25 链 |
| T1-1 | ✅ | — | ✅ | — | ✅ | 10 pins | accepted_with_conditions | 七命题；UNRATIFIED 界线完好 |
| T1-2 | ✅ | — | ✅ | — | ✅ | 同上 | accepted_with_conditions | OPEN-4/5/6 属 TIER-2 |
| T1-5 | ✅ | — | ⚠️ | — | ✅ | 4 pins | accepted_with_conditions | 交付面薄；green 主张未复跑 |
| T1-6 | ✅ | ✅ | ✅ | — | ✅ | 38 pins | accepted_with_conditions | 选(c) 落地 7/7；预存漂移登记未修 |
| T1-7 | ✅ | — | ✅ | — | ✅ | 12 pins | accepted_with_conditions | 立卡登记表；四卡待开工 |
| T1-8 | ✅ | ✅ | ✅ | — | ✅ | 16/24/34 pins | accepted_with_conditions | 3 attempts 合一；START_HERE 勘误待追加 |
| T1-10 | ✅ | ✅ | ⚠️ | — | ✅ | 89 pins | **`changes_required`** | ②+provenance 接受；① 枚举校验未闭合 |
| T1-13 | ✅ | — | ✅ | — | ✅ | 13 pins | accepted_scoped | 出处列修复+前像 hash |
| T1-14 | ✅ | — | ✅ | — | ✅ | 13 pins | accepted_scoped | pdftotext 仅交叉核对；未升级 Git |
| T1-15 | ✅ | ✅ | ✅ | — | ✅ | 21 pins | accepted_with_conditions | F-T1-15-01 P3 + 字节数观察 |
| T1-16 | ✅ | ✅ | ✅ | — | ✅ | 3 pins | accepted_scoped | 选 A 前提实证；门仍 owner 保留 |
| T1-17 | ✅ | — | ✅ | — | ✅ | 9 pins | accepted_scoped | 门腿 9/9 |
| T1-18 | ✅ | — | ✅ | — | ✅ | 6 pins | accepted_scoped | 两半同验；blocked 完好 |
| T1-19 | ✅ | — | ✅ | — | ✅ | 8 pins | accepted_scoped | rc 表四值齐；历史 rc 未动 |
| T1-20 | ✅ | — | ✅ | — | ✅ | 25 pins | accepted_with_conditions | 一处自记限度 |
| T1-21 | ✅ | — | ✅ | — | ✅ | 3 pins | accepted_scoped | 追加式在场/回改不在场 |
| T1-22 | ✅ | ✅ | ✅ | — | ✅ | 10 pins | accepted_with_conditions | 两修卡待开工 |
| T1-23 | ✅ | — | ✅ | — | ✅ | 8 pins | accepted_scoped | 勘误闭合、数值未动 |
| T1-24 | ✅ | — | ✅ | — | ✅ | 8 pins | accepted_scoped | 三腿成立（mtime 腿记录态为凭） |
| T1-25 | ✅ | — | ✅ | — | ✅ | 同 T1-23 | accepted_scoped | R-1/R-2 清除实证 |
| T1-26 | ✅ | — | ✅ | — | ✅ | 10 pins | accepted_scoped | 半授权两腿齐 |
| T1-27 | ✅ | — | ✅ | — | ✅ | 11 pins | accepted_scoped | 缓解三分半全核 |
| T1-3/4/9/11/12/28 | — | — | — | — | — | — | not_applicable_with_reason | owner 裁决号登记行（无 attempt） |

**计数**：accepted_scoped **12** / accepted_with_conditions **40** / changes_required **1**（T1-10）/
insufficient_evidence **0** / 登记行 6。**资格边界（全部 M 卡）**：仅 `formula`，锚 `9ec65295…`，
`disclosure_adaptation=unmapped`、`accuracy=unproven`，无外推。

## 1. 审查机关与主要实证

- 固定抽样（协议 §2b，先冻结）：每 attempt 重算 input/oracle/cases（T1 抽主验证 JSON/handoff/decision）+ iso 副本对
  binding pin 与当前生产。**全队 pin 为 CRLF 形态、盘上 LF**（F-MT-01）；CRLF 重序列化下 100% 复现，唯二例外
  （M08/M13 cases.json）均为账本在案的注释性 repack。
- 2026-09-20 ~14:52 UTC 全树批量重写使原始 mtime 冻结序灭失（F-MT-02）——T1-24 第三腿以记录态 manifest 为凭。
- 生产锚漂移（`model_registry.py` `9ec65295…`→`62f864b9…`，F-MT-03）：各卡资格维持锚内有效；复跑须重新锚定。
- M21–M31 终裁存在性自 grep 实证 11/11（支持父方普查更正）；M05–M07/M17–M20 的 r2 态独立验收由本裁定补足（F-MT-04/05）。

## 2. 边界与未做

- 未执行任何卡片 harness / 未写入任何旧 attempt / 未触碰三仓（RF 仅只读哈希）。
- 本裁定**不授予**任何 D/E/F、真实公司适配、准确性或外推；抽验为 sampled-verification，非逐字节全量复算。
- 两个落槽以 `landing_package/` 载体交付父 landing 批次安装（本审查不代装）。

— 独立审查员 M-T-REVIEW / N=1，2026-09-23

---

## F-RV erratum (landing)

落卡时追加（append-only，不改上文任何既有字节）。依据 = 本卡 own review 的独立复审报告
`reviewer_report.md`（27477 B，sha256 `6aedddcc029922f348fdf36a0c67eeb11872fe9a687fe97940094e4fd7e10467`，
与 `reviewer_report.sha256` sidecar 一致；verdict=accepted_with_conditions，交付/记账级 carried，矩阵结论不动）§8：

- **F-RV-01（P3 记账）**：中间机检层与终稿自述不一致 —— `evidence/clause_compare.json` 对 M01/M09/M17 等记
  `exp_ok:false`（`oracle_expected_float` 提取器路径错；本落卡复核：全文件 `exp_ok:false`=31/31 行、
  `hash_missing_pin:true`=27 处）、`evidence/per_card_checks.json` 记 `pin_present:false`=81 处、`qual:""`；
  而终稿 review 所据 `evidence/pin_resolution.json` 与复审人独立重算均为真（引值与实测逐项相符；
  `all_pins_reproduced:false` 恰 2 卡 = M08/M13，皆为账本在案的注释性 repack）。
  ⇒ **处置：`clause_compare` / `per_card_checks` 的 exp/hash/pin/qual 字段不得被后续引用为裁决依据**；
  各卡 review 的引用面固定为 `pin_resolution.json` + 复审人独立重算（`reviewer_report.md` §2/§6）。
- **F-RV-02（P3 交付）**：`landing_package/README.md` 称「块内引 sha256」，实际 20 块仅在文件顶总则指向
  `../evidence/self_manifest.json`，块内无逐块 sha ⇒ **安装时逐块内联该块载体 sha（`reviews/<卡>.md` +
  `acceptance_rulings.md`，取自 self_manifest 并经 45/45 复核）+ 追加块体自身 sha256 = 由本安装批执行（done by this install pass）**，
  逐块记录入 `<本 attempt>\install_log.jsonl`。
- **F-RV-03（P3 形式）**：翻转块 `status_authority` 缺显式 `verdict_is_transcribed_not_authored` 键
  （现以 `implementer_signed:false` + 前缀哈希证明承担同一语义）⇒ **每个安装块内补记
  `verdict_is_transcribed_not_authored: true` = 本落卡已做（done here）**。
- **F-RV-04（P2 他卡记录）**：M17 卡自身 `handoff.acceptance.carrier.byte_equality_proof_sha256=
  6096771aa0dd906b…`，现盘 `evidence/M17/transcription_proof_r3.json` 实测 = `9d21f8557d2762cf…` —— **不符**；
  但其裁定块本体字节范围 `review.md [32643,42998)`（10355 B）本落卡切片重哈希 =
  `e383f5e89bd6737fe520bdb3b0f4bd01fc517cfd17a326564db06ea60b39c248`，与声明完全吻合 ⇒ 属证明件自身被重写/重记的
  记录漂移，非裁决字节问题 ⇒ **为 M17 登记 follow-up 行（parent records，交 M17 系/落定批次核销；不在本卡欠账内）——
  此处仅注记，不动 M17 任何字节**。
- **F-RV-05（P3 他卡记录）**：M01 `first_run_forensics.json` 的 `mtimes_supporting_the_sequence` 把
  `01:18:24` 归给 `evidence/M01/stderr.txt (re-run, now 0 bytes)`（本落卡实读确认），`review.md` 与 F-MT-02 引文
  归给 `oracle.json`（同秒双归属）—— 注记于此；F-MT-02 实质（原始冻结序现盘不可复验）不受影响。

— 落卡（carrier landing 批次转录本卡 own review 的 F-RV 发现；裁决文字出自独立复审代理，本节非自签），2026-09-23
