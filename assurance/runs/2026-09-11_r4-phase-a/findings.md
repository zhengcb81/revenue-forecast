# R4 Phase A 发现（findings）

## F-A01-1：A 阶段的设计准入本身需要"精确 DEV/数据读取许可"，当前授权只够只读映射

- 证据：执行计划 §2 表格——「A 合同与真实基线 | 设计准入 = 文档完成后，**未来精确DEV/数据读取许可**」；handbook §2.5「首次实施前用户须批准 DEV 精确工作包及文件范围」。
- 影响：A01（读代码/配置）可在只读范围内先做；**A05/A06（真实语料、基线 trace）必须等精确数据读取许可**，A02–A04 的合同设计可在 A01 收口后提交 A.DR。
- 处置：本 run 只做只读映射，不越门。

## F-A01-2：跨仓主链是"子进程级联"，不是进程内调用

- 证据：filing `scripts/fetch_filing.py:199-213` `_run_company_wiki_json` 用 `subprocess.run` 调 wiki CLI（Windows `CREATE_NO_WINDOW`）；revenue `scripts/source_preparation.py:3-4` 自述"真实跨仓链：filing-fetch (resolve/ensure) → company-wiki catalog"，`:18` 导入 `subprocess`；revenue `scripts/company_wiki_source.py:12/261` 经 `filing_fetch_client.resolve_filing`。
- 影响：A03 的"副作用表"必须**按子进程边界**给（解释器路径/cwd/argv/env/读写集合/网络/预算/timeout），不能只按函数调用描述；VR 的隔离测试也要在子进程层观测。

## F-A01-3：wiki CLI 面很大（47 个子命令），其中既有只读也有写

- 证据：`cli.py` 解析器实测 47 个子命令，含 `identify/resolve/query/preview/documents/export`（只读面）与 `ensure/scan/normalize/summarize/apply/prune-retired-evidence/duplicate-recycle/import-portfolio/install-startup/...`（写/外部面）。
- 影响：A03 必须为每个对外接口标注"纯读 / 可能写 / 可能外发"；`ensure` 已有 `--allow-download` + worker paused 审计（`_append_paused_acquisition_audit`）两道闸，属既有安全面，A 阶段**只记录不改**。
- 未做：逐条副作用矩阵（需跑 `--help`/`--dry-run`，等 command-manifest）。

## F-A01-4：迁移期分支仍在链上，但不属 A 阶段动作

- 证据：`resolver.py` 中 `legacy_bridge_allowed` 出现 **10 处**；R9 执行包把 bridge/flags 列为批 3 删除对象（revenue `assurance/fc/Phase-14/01_r9_packet.md` §1）。
- 影响：A 阶段记录其存在与位置即可；删除归 R9（技术门 FC-705 + owner 政策门 + 独立 receipt/reviewer）。

## F-A01-5：9/7 诊断行号不可当坐标

- 证据：handbook §2.3「9/7诊断行号只是定位线索」；本步实测 `scanner.py` 与包内行号已漂移（facade 在 `1375-1407`，包写 `1357-1360`）。
- 处置：本映射一律按**符号 + 实测行号**双写，执行时以符号为准。

## F-A01-6：CLI 表面积已由真实解析器确认；"47"是源码 grep 的错，真值 51（41 顶层 + 10 嵌套）

- 证据：owner 2026-09-11 批准的 `--help`-only command-manifest 执行 **52 次探针**，全部 rc=0；输出见 [evidence/cli-help-matrix.json](evidence/cli-help-matrix.json)。真实命令树：41 顶层 + `documents{retire,restore}` / `identity-enrichment{preview,verify,reject}` / `activation{preview,apply,rollback}` / `runtime-policy{show,apply}`。
- **零副作用已证明而非声称**：前后快照比对 `catalog.sqlite3`、`config/source_catalog.yaml`、`__pycache__` 目录集合、git dirty 行数 —— 四项全部 **true（未变）**。
- 处置：A01 §4 以探针结果为准并保留更正说明；A03 §2 的分类依据从"源码 grep（暂定）"升级为"真实 help 文本"。

## F-A01-7：`--help` 探针证明"解析期无副作用"，但不等于"行为层无副作用"

- 证据：`cli.py:860-868` —— `main()` 先 `parse_args`（`--help` 在此 exit），之后才 `config.resolve(strict=True)` + `load_catalog_config`；且模块级只有 `if __name__ == "__main__":` 与 `__all__`（无导入期副作用）。
- 影响：这解释了零副作用，但**不能**推出"任何 `--dry-run` 也安全"——dry-run 会走到 config/DB 层。
- 处置：行为探针（`--dry-run`、只读查询）必须在**隔离副本**上做，且属 A06/VR 范围。
