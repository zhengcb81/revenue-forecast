# I-11-A recovery / re-run rules

本卡是**设计/契约卡**：没有产品代码修改，没有需要回滚的状态变更，也没有跨进程或崩溃恢复语义。
因此本目录不提供"异常后恢复"演练（按 `review_and_handoff.md` 允许"纯函数可说明 NA"），
只提供**证据再生与版本修订**的确定步骤。

## 1. 为什么不需要"故障恢复"证据

- 本卡的全部命令都是只读输入 + 只写 attempt 目录的确定性脚本；
- 不接触数据库、不启动 worker、不调用 provider、不写生产 catalog；
- 唯一的"状态"是本 attempt 内生成的文件，可随时由脚本重新生成。

`oracle.md` §8 的 S1–S5 停止条件已覆盖真正会中断的情形（hash 漂移、锚文本定位失败、
需要 approved 才能继续、上游冲突、同一命令两次相同失败）。

## 2. 若要重新生成证据（例如脚本修 bug 后）

在 attempt 根目录按顺序执行（全部使用 attempt 自己的隔离解释器）：

```
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\run_extraction.py <attempt> <attempt>\evidence\I-11-A\extract\commands_raw.json <attempt>\evidence\I-11-A\extract\commands_raw.ascii.txt
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\build_hypotheses.py <attempt>
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\validate_hypotheses.py <attempt> <attempt>\evidence\I-11-A\validation_report.json <attempt>\evidence\I-11-A\validation_report.ascii.txt
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\capture_state.py <attempt> before
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\capture_state.py <attempt> after
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\build_commands.py <attempt>
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\make_changes_diff.py <attempt>
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\hash_attempt.py <attempt>
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\final_selfcheck.py <attempt>
```

顺序约束（有实际原因，不是形式要求）：

1. `run_extraction.py` 必须最先跑：`build_hypotheses.py` 会把提取输出的 sha256 写进
   `source_map.json`，`validate_hypotheses.py` 会打开这些文件；顺序颠倒会让校验读到旧字节。
2. `capture_state.py after` 必须在所有写入之后、`hash_attempt.py` 之前跑。
3. `hash_attempt.py` 要在 `review.md` / `handoff.json` 之前跑一次、之后**再跑一次**
   （`I11A-14` 与 `I11A-16` 两个 command id），这样这两份交付物本身也被清单覆盖；
   最后一次运行时它会覆盖 `attempt_hashes.json`，属预期行为（记录在 commands.json 的 purpose 里）。
4. `final_selfcheck.py` 必须最后跑，它重跑两个内容校验器并比对 before/after 生产状态。

## 3. 若 reviewer 要求修改（`changes_required`）

1. **不覆盖**本 attempt 的任何已交付证据。
2. `oracle.md` 只能以 **R2 附录**追加修订（例如 OPEN-8 的 O-6 措辞修订），
   不改写 §0–§9 的正文；修订必须写明"哪一条期望错了、错在哪、修订后如何判定"。
3. 命题层面的修订 → 新建 `execution_runs/I-11-A/<new-attempt-id>/`，
   从本 attempt 复制 `tools/`（工具可复用），但**证据全部重新生成**，
   并在新 attempt 的 `handoff.json` 里引用本 attempt 的 id 与被修订的条目。
4. 若 reviewer 发现我引用的某个原始数值在原文中不存在 → 按 oracle S2 处理：
   该命题立即判 `STOP_EVIDENCE`，不得换页码或换数字让它通过。

## 4. 生产仓库的回滚

无需回滚：`state_before.json` / `state_after.json` 显示三仓 HEAD 与 porcelain 条目
在两个时点完全一致，关键文件（`revenue-forecast/SKILL.md`、`CHANGELOG.md`、
`company-wiki/config/source_catalog.yaml`、`filing-fetch/scripts/fetch_filing.py`）的 sha256 也一致。
本 attempt **没有**执行 `git add` / `commit` / `restore` / `stash`。

## 5. 已知的环境约束（影响复现）

- 只能使用 PowerShell 5.1（无 `pwsh`），控制台为 GBK：所有命令输出以 ASCII 摘要落盘，
  中文内容一律写进 UTF-8 文件而不依赖控制台；
- 单命令 600 s 上限；本卡最慢命令为 352 页 PDF 扫描（约数十秒），未触发上限；
- 禁网：`pip install` 不可用，故 venv 内的 `pytest` 是从 I-08-A attempt 的 venv
  复制包目录得到的（未走网络安装）；
- `pdftotext.exe` 来自 Git for Windows（仓库外工具，已登记 sha256 与 argv，见 OPEN-1）。
