# recovery.md — TTL-30D-POLICY / a20260922-01

生产零写、零 git；本卡成果全部在 attempt 内待复审。以下为父方（复审通过后）落地与回滚程序。

## 0. 状态锚点

| 对象 | sha256 |
|---|---|
| 生产 guard（当前=before，未动） | `F900A13D7C22FE3BD742485C6B603DE11B92A56D2414A2A046216CCD3B0B9C08` |
| iso after（修复版，待晋升） | `142AE84838960D500528F2BD3BEE1742758152E0518E061A67ED3997CA6DD7DD` |
| changes.diff（6 hunks / 112 行） | `8271158BF034E6FEC60B65D48BEC173F5EE1A98AD1538D29A8DAEBCBD29FDBD3` |

## 1. 落地（复审通过后，由父执行——既定模式「父保留各仓提交权」）

1. 独立复审读齐：`oracle.md`（含 §5 勘误与冻结哈希）+ `oracle_freeze.json` + `binding.json` + `commands.json` + `decision.md` + `changes.diff` + `evidence/*` 原始件。
2. 应用（二选一，均无需 git）：
   - **整文件**：把 `iso/prompt_injection_guard.py` 覆盖到
     `C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\prompt_injection_guard.py`；
   - **diff**：按 `changes.diff`（6 hunks，difflib unified，LF 行尾）手工套用到生产文件。
3. 验收锚：
   - 落地后 `Get-FileHash` == `142AE848…7DD`；
   - `python -m pytest tests/unit/test_prompt_injection_guard.py tests/unit/test_readiness_graph.py -q` ⇒ **26 passed**（零测试编辑）；
   - `python <attempt>/scripts/ttl30d_probe.py <cw>/src <临时out.json>` ⇒ `gating_failed=[]`（16/16）。
4. 之后由父分仓提交（卡面：production commit by parent）。提交范围 = **恰好 1 个文件**（prompt_injection_guard.py）；勿 `git add -A`。

## 2. 回滚

- 落地后回滚：恢复字节至 sha `F900A13D…C08`——该字节即生产 HEAD 当前内容（本卡未改生产，`git checkout -- src/company_wiki/source_catalog/prompt_injection_guard.py` 即得；若已提交则 revert 该单文件提交）。
- 校验回滚成功：`Get-FileHash` == `F900A13D…C08`。
- 恢复后行为回到 before 基线：超帽不拒、past-now 复活（=decision.md DEF-1/2/3 重现），产品测试仍 26 passed（这正是需要 oracle 探针的原因——product tests 对帽变异不敏感，见 decision.md 逐案表 R 行）。

## 3. 环境/工具复现

- **%TEMP% 镜像**：`%TEMP%\ttl30d-a20260922-01`（src+2 测试+conftests 拷贝，guard=iso 版已还原）。复审者可直接复跑；清理：`Remove-Item -Recurse -Force $env:TEMP\ttl30d-a20260922-01`（纯临时件）。
- **探针复跑**：`python scripts/ttl30d_probe.py <mirror或cw的src目录> <out.json>`（期望值字面量取自 oracle，不从实现反推）。
- **变异重建**：`python scripts/make_mutants.py iso/prompt_injection_guard.py mutants/`（m1=移除帽+finite 校验块；m2=移除 past-now 分支；各断言块恰好匹配一次，且 `compile()` 语法校验）。
- **diff 重建**：`python scripts/make_diff.py <prod> <iso> changes.diff`（difflib，无 git；勿走 stdout 管道——GBK 会截断，见 commands C11a 披露）。

## 4. 证据只读锚

`evidence/final_deliverable_hashes.json` 收录全部交付件 sha256；`evidence/red_before.json`/`green_after.json`/`mutation_m1_*.json`/`mutation_m2_*.json`/`green_confirm.json` 内嵌各自运行时实际加载的 `guard_sha256`，可据以判定每份结果对应哪版代码（f900a13d…=before、142ae848…=after、61cdab69…=m1、f75eed61…=m2）。
