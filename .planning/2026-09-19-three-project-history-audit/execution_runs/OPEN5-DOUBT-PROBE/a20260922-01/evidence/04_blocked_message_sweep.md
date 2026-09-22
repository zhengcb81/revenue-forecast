# 04 — Blocked-message text sweep（存疑 2 / 裁定 C8 现状盘点）

日期：2026-09-22 · OPEN5-DOUBT-PROBE/a20260922-01 · 全部检索只读执行
检索范围（全部实跑）：
- PRODUCT = `C:\Users\郑曾波\Projects\revenue-forecast`：`scripts\`、`tests\`（另全仓 `*.py` 一次，含 tools/e2e）
- CW = `C:\Users\郑曾波\Projects\company-wiki`：`src\`、`tests\`、`scripts\`
- 裁定文本本体：`execution_runs\T2-SIM-OPEN5-RF\a20260922-01\ruling.md`
- 候选（被钉对象的 UNRATIFIED 副本）：`execution_runs\I-06-A\a20260919-01\iso\candidate\`、`scripts\`

## 结论表（message → 定义处 → 断言处 → 状态）

| # | 消息/文案 | 定义处（实读） | 断言处（实 grep） | 状态 |
|---|---|---|---|---|
| 1 | `not_reviewed` 状态令牌 | CW `resolver.py:918`（默认）/`:1078`（无回执⇒not_reviewed）/`:1088`（取回执 status）；CW `prompt_injection.py:11`（docstring 契约）；RF `scripts\source_preparation.py:152-153`（N-1 防御默认+闸门） | CW `tests\contract\test_fc905_receipt_envelope.py:167,178,248`（`== "not_reviewed"` 等值）；CW `tests\unit\test_prompt_injection_guard.py:203,216,243,255,270,288`；CW `tests\unit\test_source_lifecycle.py:261-275`；RF `tests\test_fc905b_trusted_receipt.py:75-85`（经正则间接） | **PINNED**（令牌级，双仓一致；CW 多处等值断言） |
| 2 | 完整阻断句 `prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)` | RF `scripts\source_preparation.py:154-156`（唯一产品定义）；同文另存 2 份副本：候选 `w06a_candidate_patch.py:139-142`（`block_message` base，status 动态）、`w06a_apply_candidate.py:51-52`（REPLACED 锚文本，须与产品逐字节一致否则 patch 失败） | RF `tests\test_fc905b_trusted_receipt.py:76,85`：`pytest.raises(RuntimeError, match="not reviewed\|blocked")` —— **宽松正则**，不是全文断言；两仓零全文断言 | **UNPINNED**（改写文案不会红任何测试；3 份手抄副本=漂移风险，目前三份一致无漂移） |
| 3 | `cases_json_declared_expectation_missing` | **零命中**：PRODUCT `scripts\`+`tests\`+全仓 `*.py`；CW `src\`+`tests\`+`scripts\` | 零命中 | **ABSENT**（两仓无此串；连 `ruling.md` 本体也 grep 不到该串——任务描述所称"OPEN-5 ruling calls out"在裁定文本中无对应字面，裁定 C8 只统称"阻断文案"） |
| 4 | `demand_store_error=` 附加子句 / `demand_queued demand_id=…` | 仅候选 `I-06-A ...\iso\candidate\w06a_candidate_patch.py:157`（store_error 分支）/`:161-163`（正常分支）——UNRATIFIED，attempt 树内 | 产品两仓 0 定义 0 断言；仅 attempt 内行为断言：`I-06-A\scripts\w06a_cases.py` C7_r2（contains_store_error / NOT contains_demand_queued）+ `after\cli-logs\c7-store-unwritable\stderr.txt`、`c1-first-run\stderr.txt`（实发原文样本） | **UNPINNED**（产品/测试完全没有；候选内也只查子串有无，不钉全文） |
| 5 | demand/claim 拒绝文案：`no demand {id!r}` / `demand {id!r} is not claimable` / `demand {id!r} is in backoff` / `no ready demand to claim` / `lease owned by {owner!r}` / `lease expired` | RF `scripts\processing_demand.py:89,100,102,112,132,134`；CW `src\...\processing_demand.py:103,118,120,130,150,152`（两仓逐字相同） | CW `tests\contract\test_zr507_processing_demand.py:65,83,107,122,128`、RF `tests\test_zr701_f1_draft_formal.py:149` —— 全部只 `pytest.raises(<type>)`，**无一处 match=/全文断言** | **UNPINNED**（类型钉住、文案无钉；双仓当前无漂移） |
| 6 | resume 拒绝文案（C5：lease 过期 resume ⇒ REJECT） | **无实现**（候选 `DurableDemandStore` 无 resume/complete 方法，见 evidence/03；产品两仓无 resume 入口，与 `original-request-resume.json:39-42` 一致） | 无 | **ABSENT-implement-first**（文案不存在，无从钉；实施时须与 #2/#4 同一错误契约） |
| 7（附） | `unknown ruleset hash {hash!r} (fail closed)` | CW `prompt_injection_guard.py:98` | CW `tests\unit\test_prompt_injection_guard.py:122` `match="unknown ruleset hash"` | **PINNED** |
| 8（附） | `{field} must be a lowercase SHA-256`（含 `evidence_sha256 must be a lowercase SHA-256`） | CW `prompt_injection.py:37`；同族 `prompt_injection_guard.py:95,192,194`、`resolver.py:1041` | CW tests **零命中**（grep `lowercase\|evidence_sha256 must be` 仅命中 test_zr404 无关行）；仅 I-06-B attempt harness 钉过该全文（N3） | **UNPINNED**（产品测试面） |
| 9（附） | `parser/llm counts absent from the resolution envelope — fail closed instead of fabricating 0` | RF `scripts\source_preparation.py:159-162` | RF `tests\test_fc905b_trusted_receipt.py:111,113` `match="parser\|llm\|counts"` 宽松正则 | **UNPINNED** |

## 跨仓一致性（drift 检查）

- `not_reviewed` 令牌：RF 闸门消费（`source_preparation.py:153`）与 CW 生产（resolver）**一致**，无漂移。
- demand 拒绝文案：RF `processing_demand.py`（sha256=`fcdfcad8ebd1fc20febf3c157dcd20ad92708fd69d00373ef9a943e5a820afc1`）与 CW 同名模块（`90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b`）六个拒绝串**逐字相同**，无漂移（二者是独立实现、合同测试同型，类型级断言维持了这个巧合的一致——但无文本级保险）。
- 阻断全文 3 份副本（产品 :154-156 / 候选 patch :139-142 / apply 锚 :51-52）当前**一致**（apply 锚不一致会直接 patch 失败，属自检），但**无任何测试钉住** ⇒ 漂移敞口存在。
- `demand_store_error=` / `demand_queued`：产品两仓**零定义零断言** ⇒ 谈不上漂移，但完全未契约化（C8 目标物之一）。

## 对存疑 2 的回答

「阻断文案跨仓文本断言未排查」这一**排查缺口本身已闭合**（本表即排查记录，C8 要求的"断言清单 + 排查记录"中的排查记录已交付）。
但排查**结果**是：9 条文案里仅 2 条 PINNED（`not_reviewed` 令牌、`unknown ruleset hash`），5 条 UNPINNED、2 条 ABSENT
⇒ 裁定 C8 的"钉住"要求**仍未满足**：现状 = 大面积 unpinned，其中 #2 完整阻断句与 #4 `demand_store_error=` 子句正是 C8 点名要钉的两条，均未钉。

**判定：存疑 2 = RESOLVED-YES（"未排查"缺口已补，本表为证）＋ 附属敞口 REMAINS-OPEN（C8 钉住工作未做，现状 unpinned 清单已量化解析）。**
