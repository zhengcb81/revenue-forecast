# after/ ：本卡的"修改后"证据说明

I-11-A 不改变任何产品行为，因此"修改后"证据 = 本 attempt 生成的证据产物本身 +
两套校验的原始输出。全部内容都在 `../evidence/I-11-A/`，本目录不复制副本（避免出现两份可能不同步的字节）。

| 需要的"修改后"证据 | 实际路径 |
|---|---|
| 命题与来源映射 | `../evidence/I-11-A/hypotheses.json`、`../evidence/I-11-A/source_map.json` |
| 机制链审查包（交行业 reviewer） | `../evidence/I-11-A/mechanism_review.md` |
| 校验原始输出（正例 + 14 个反例） | `../evidence/I-11-A/validation_report.json`、`../evidence/I-11-A/validation_report.ascii.txt` |
| 算术 oracle 复算 | `../evidence/I-11-A/extract/arithmetic_oracle.json` |
| 全部命令的 argv/退出码/输出 sha256 | `../commands.json`、`../evidence/I-11-A/extract/commands_raw.json` |
| 完整流水线日志（ASCII） | `../evidence/I-11-A/pipeline_final.ascii.txt` |
| 生产状态未变的证明 | `../evidence/I-11-A/state_before.json` 与 `state_after.json`（内容一致） |
| 交付清单 | `../evidence/I-11-A/attempt_hashes.json` |
| 完整性自检 | `../evidence/I-11-A/final_selfcheck.json` |

**注意**：`final_selfcheck.json` 是流水线最后一跑的结果。它对本目录与 `../review.md`、
`../handoff.json` 的存在性检查要求这些文件已写好，因此其 `verdict` 只有在最后一跑之后才有效；
`commands.json` 中 `I11A-17-final-selfcheck` 的 `observed_returncode` 与
`attempt_hashes.json` 的清单是判定依据。
