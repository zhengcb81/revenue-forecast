# sampled_and_namecheck_M21-M31.md — M21–M31 终裁有效性抽验/点名表（落槽 2 · 供父登记归档）

**性质**：M21–M31 已有有效终裁（其普查更正经本审查员自 grep 实证 11/11）。本表 = 终裁有效性的
抽验记录（3 深验 + 8 点名），供父 landing 批次登记入 REMEDIATION_REGISTER / findings（D9 收口附件）。
**不**修改 M21–M31 旧 attempt —— 其终裁本已落定，无需翻转。
出具：**独立审查员 M-T-REVIEW / N=1**，2026-09-23。详证 `../reviews/M21-M31_sampled.md`。

## 表一 · 终裁存在性（本审查员实证，非转述普查）

| 卡 | verdict 文本落点 | 逐字节转录证明（sha 前 16） | 确认追加证明 | status |
|---|---|---|---|---|
| M21 | review.md round2 120–130 / round3 131–140 | `aee6d601c2c44e59…` | — | accepted_scoped |
| M22 | review.md（round3 全批） | `05f5fe10d42b12ec…` | — | accepted_scoped |
| M23 | review.md（round3 全批） | `bd76f1053438da80…` | — | accepted_scoped |
| M24 | review.md（round3 维持偏差） | `5ff449274be8f840…` | — | accepted_scoped |
| M25–M28 | review.md 83–131（r2 append-only 块；artifact_sha256 族） | （块内 append-only 形态） | — | accepted_scoped |
| M29 | review.md 42–109 + 111–129 | `58e614d533e6be73…` | `4ff7a53b7a999974…` | accepted_scoped |
| M30 | review.md 42–90 + 92–110 | `dfb854b4cc085b76…` | `a0992cfea58efad5…` | accepted_scoped |
| M31 | review.md 43–98 + 100–118 | `c57d50061510e548…` | `f41b2fc71f8b7605…` | accepted_scoped |

## 表二 · 深验 3 张（pin + 签名行 + 落定形态）

| 卡 | pin 抽验 | 签名行/落定形态 | 抽验裁定 |
|---|---|---|---|
| M21 | 3/3 复现（CRLF）；iso==binding==锚 | round-3 终裁逐字转录 + 逐字节证明；「implementer never writes accepted」 | **accepted_with_conditions**（F-MT-01/02/03） |
| M25 | 3/3 复现（LF 直配）；iso==binding==锚 | r2 块 append-only；生产回滚窗 + owner 恢复已登记未抹去 | **accepted_with_conditions**（F-MT-02/03） |
| M31 | 3/3 复现（CRLF）；iso==binding==锚 | status_authority 块齐（implementer_signed=false / qualification_scope=formula@锚）；T1-23 勘误 + T1-25 R-1/R-2 清除链闭合 | **accepted_with_conditions**（F-MT-02/03；handoff 缺 positive_expected 键） |

## 表三 · 点名 8 张（终裁在案 · 引 sha · 抽点五子句全过）

| 卡 | 终裁 sha（前 16） | 抽点摘要 | 抽验裁定 |
|---|---|---|---|
| M22 | `05f5fe10d42b12ec…` | `[55]` 三方一致 / 11/11 / 九件 / 三栏 / 无产品改动；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03） |
| M23 | `bd76f1053438da80…` | `[110]` / 全过；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03） |
| M24 | `5ff449274be8f840…` | `[215]` / 全过；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03；round-2→3 reviewer 自认记录采信） |
| M26 | r2 块（M25 族） | `[205]` / 全过；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M27 | r2 块 | `[264000]` / 全过；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M28 | r2 块 | `[11.5]` / 全过；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M29 | `58e614d533e6be73…` | `[300]` / 全过；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03；缺 positive_expected 键） |
| M30 | `dfb854b4cc085b76…` | `[600]` / 全过；pin 3/3 CRLF | **accepted_with_conditions**（同上） |

**汇**：11/11 终裁有效、无一按缺验收处理；全数仅 `formula` 资格（锚 `9ec65295…`）。

— 独立审查员 M-T-REVIEW / N=1，2026-09-23
