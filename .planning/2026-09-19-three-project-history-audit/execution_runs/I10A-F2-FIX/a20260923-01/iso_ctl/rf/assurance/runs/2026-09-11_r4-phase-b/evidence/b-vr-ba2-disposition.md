# `B.VR-ba2` 复审发现处置表（2026-09-19 BAR 增量：wiki `f39bd5a` / revenue `2c5384b`）

复审记录：[reviews/B.VR-ba2.json](../reviews/B.VR-ba2.json) — **`approve_with_findings`**，
**0×P0 / 0×P1 / 0×P2 / 3×P3**。复审身份：独立只读会话
（`df04021d-b515-4526-a3b5-13dd772b27c9`），临时工作物全在 `%TEMP%\vf_r4\`，**两仓零改动**，
生产 catalog 只 `os.stat`（`49,677,344,768 B @ mtime_ns 1789799495406919100`，与其自身观测前后一致）。

**C1–C8 全部由复审独立重跑复现**（不是读我的记录）：只回退第二处守卫 ⇒ 2 failed / 5 passed 且红的正是两条新回填用例；
只回退记录事务守卫 ⇒ 1 failed 且异常在 `normalizer.py:1933` 逃逸；`retry_limit=2` 阶梯实测
（t0 可重试 → t0+899 未被重选 → t0+900 重选并终态）；树内 harness 全量重跑 **17/17 KILLED** 且与已提交 JSON
**逐字段差异为空**；`_self_check()` 三类注入 3/3 被拒；`coverage_anchor.py --expect` 退出 0；
两仓 7,225 + 4,045 个 blob 里**找不到**旧的 `8cf4a793…` 锚。

| # | 严重度 | 复审发现 | 处置 |
|---|---|---|---|
| **F-IR-10** | P3 | `evidence/barfix-product-fixes.md` §7 的变异计数是**陈旧数字**（`2 failed, 4 passed` / `6 passed`），而 JSON 与用例都是 **7 条**（baseline `7 passed`、mutated `2 failed, 5 passed`）——同节后文又写 `7 passed`，自相矛盾 | **接受并已改**：改为"副本内基线 **7 passed** ⇒ 回退后 **2 failed, 5 passed**"，数字取自 `barfix-mutations.json` 的 `baseline`/`mutated`，并在原处注明旧数字来自"第三条用例尚未加入"的版本 |
| **F-IR-11** | P3 | reviewed commit 里的 `checkpoint.json` 仍是**增量前快照**（`reviewed_commit 9e0271f`、不含本批任何 sha/数字）**且仍把已作废的 `8cf4a793…` 当有效锚**；该文件按设计被排除在自身 manifest 之外，完整性检查抓不到 | **接受并已改**：本批内**重建** `checkpoint.json`（`--reviewed-commit` = 本处置提交）；并**登记流程缺陷**——checkpoint 不校验"自己的 reviewed_commit 是否等于最新提交"，所以"陈旧 checkpoint"不会被任何门抓到，只能靠人/复审（见下方"处置中登记") |
| **F-IR-12** | P3 | 同一个 flake 用例有**两个登记号**且互不引用：`F-ZR409-1`（旧，机理=`OSError`→`b"inaccessible"`，自述**未被证明**）与 `F-ZR409-01`（新，**实测** `st_size 4096→0` 且 `mtime_ns` 不动） | **接受并已改**：在 `F-ZR409-1` 末尾加**交叉引用**，并写明**现行口径以 `F-ZR409-01` 为准**（实测 > 候选）；两条指同一用例、修法建议相同 |

## 对复审 `not_verified` 的逐条回应

1. **远端 CI run `35430114632` 无法核对（复审禁网）** —— 由作者会话用 GitHub API 核对并在记录里落盘：
   run **`35430114632`** = **success**，6/6 job 全绿，且 `test (3.13)` 的第 10 步
   `Branch coverage ratchet (FC-1204-a, fresh measurement)` = success；revenue run **`35430434111`** = success
   （`real-roots` + `verify`）。**限制照写**：这是作者会话的核对，**不是**复审的独立核对。
2. **"一次性审计脚本已删"删前不可证** —— 承认：该删除**无法由录内证据证明**（脚本只在 `%TEMP%` 与本会话命令里出现过，
   不在任何提交里）。可核的是**结果**：`_mutant_anchor_audit.py`/`_mutant_audit.py` 两个名字在仓内**零命中**，
   而它们原先检查的三件事已**并入** `barfix_mutations.py` 的 `_self_check()`（复审已独立验证三类拒绝都会触发）。
3. **全量 `2870 passed` / contract `1939` / unit `799` 未重跑** —— 承认：复审只核对了证据文件汇总行。
   这三条由作者会话的证据文件承载（`barfix6-coverage-run.txt`、`barfix6-ci-step1-unit.txt`、`barfix6-ci-step2-contract.txt`），
   且**远端 CI 在同一天、同一修订上独立跑过 unit + contract + 覆盖率棘轮**（见上）。
4. **覆盖率"跨运行可复算"只证明了留存文件自洽** —— **已补做，结论是否定的**：同一棵树、CI 同一命令**再测一次**
   （留存 `barfix6-coverage-repro.json` / `-repro-anchor.txt` / `-repro-numbers.txt` / `-repro-ratchet.txt` /
   `-repro-run.txt`）：内容锚 `63fadcf7…` **≠** `e223dab3…`，`percent_covered 83.083 vs 83.111`。
   **按预先写下的规则，"跨运行可复算"口径已作废并改写**（findings.md `F-COV-01` 第二次更正）：内容锚是
   **留存测量内容的内容标识**（不含时间戳、可对留存文件复算），不是跨运行保证——两次全量跑**失败集合不同**
   （第二次 9 failed，见新登记的 **`F-LOAD-01`**：新增 8 个失败全部为时序/进程类用例，当时本机被其它代理工作流
   并发占用；同一修订的远端 CI contract 步含这些用例全绿）。复测覆盖率+复杂度棘轮仍 **4 passed**。
5. **`F-PROD-01` 的反事实部分不可核** —— 接受并**已在记录里降级措辞**：`files_seen 46600/0` 与快照内容来自
   生产 catalog 的 `scan_runs` 表与 `runtime_policy.json`（**实测**）；"09-18 之前那次会整轮中止"是**反事实**，
   `findings.md` 与 LEDGER 里都写为**代码阅读所得**（`scanner.py:1916-1918` 的 `except Exception` 之前没有逐根捕获），
   **不**作为已复现结论。

## 处置中登记（本次新登记的流程缺陷）

- **`F-CHK-01`（流程，本批发现）**：`checkpoint.json` **不校验自己的 `reviewed_commit` 是否仍是最新提交**，
  而它又被 `excluded_by_design` 排除在自身 manifest 之外 ⇒ **一份陈旧 checkpoint 不会被任何门抓到**
  （本次就是靠复审读出来才发现的）。**修法未做**（属生成器的工作包）：生成时断言
  `reviewed_commit == git rev-parse HEAD`（或 `HEAD~1`，若 checkpoint 与记录同批提交），否则拒绝写入。
- **本批我自己的两处操作缺陷（登记）**：① 本批证据文件**误用**了上一批已占用的 `barfix4-` 前缀，覆盖了
  `barfix4-coverage-ratchet.txt`（**已从 git 恢复**，本批全部改名 `barfix6-`）；② 我在改名后**先改写了脚本输出文本**
  再发现该做法等于伪造工具输出（`coverage_anchor.py` 的 `path` 字段），于是**重跑脚本**生成该文件。
