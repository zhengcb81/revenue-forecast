# REGISTRY-CLOSURE recovery — a20260923-01

## 如何续做/复核本卡

1. **清单与判据**：`oracle.md`（冻结，sha 见 `oracle.sha256`/`binding.json`）。复核=逐项对照 `decision.md` 表行与其证据指针。
2. **行为恒等复算**（J1）：`python evidence\rem05_verify.py`（只读；产出 AST 三树判定 + 20 形态 redact_text 恒等 + 编译）。输出已存 `evidence\rem05_behavior_identity.txt`。
3. **补丁重建复算**（J1/J2）：`python evidence\rem05_build_patch.py`、`python evidence\r503_build_patch.py`（difflib 只读重建补丁与 diff；输出 opcode 表证明纯插入/双行改）。**注意**：脚本只写本 attempt 目录，不触任何目标文件。
4. **changes.diff 应用**（未来落用）：4 hunk 均注释级；对两目标（I-14-D r6 树 `observability.py`、生产 CW `observability.py`）先重算锚行在位再 `git apply`/手插；应用后跑 redaction 测试族 + rule/oracle harness 确认 verdict 不漂。

## 已知风险/断点（如实）

- **并发写风险**：登记册由父侧并行追加（本卡期间 §76→§78 出现）。本卡汇总节以**文件末尾单节**追加；若与父写入交错，以追加后重读为准（追加命令=单次 AppendAllText）。
- **EOL 教训沿用**：补丁构建全部字节级（difflib + bytes replace），插入注释按宿主行尾（CRLF）构造——规避本计划已立的 BOM/EOL 自伤族（register §52 第 9 例）。
- **不重跑历史 harness**：I-14-D 的 `harness\run_*.py` 等脚本可能内嵌输出路径（AUDIT-DESIGN 事故同族），本卡**一律不执行**历史 attempt 内脚本；行为验证只用本 attempt 自带探针（import-only）。
- r503 首版锚句（整句单行）不中（源文件两行折行）→ 改双行锚（3-strike 内解决；两次尝试均记 commands.md）。

## 恢复点

- 若中断：从 `decision.md` 表格续（每行独立自含）；登记册汇总节若未追加，按 decision「汇总节预览」原样补（单节、append-only）。
