# W03-A RF 最终交接

状态：**READY_FOR_ROOT_FINAL_TYPED_CURRENT_RECHECK**。最终产品 `2de4b9d3ad3c032c89a1987a3b2141610ac91233`；基线92b69682，经正常merge9eb包含ROOT main a8工程接线。旧b76/26P独审只签历史版本；当前补正待ROOT非作者最终签收。

## 公共合同与最终语义

只有 `scripts/company_wiki_narrative_contracts.py` runtime和 `tests/test_r1_narrative_availability.py`。Raw receipt/1仅optional availability_evidence，省略/null旧shape兼容，完整proof只保留context.read_receipt；manifest pub仍null。Project /3 exact不变，不用A证明放行B或整projection；正文、artifact/generation/缓存身份/默认均不改。

显式historical asof复用common qualification，known未来/invalid pub优先拒绝；unknown需同SHA、截止日前owner proof。Current/asof=None不虚构historical cutoff：有proof先common验形/SHA，以InformationEligibility(proof basis/available_by,published_date=None)只核actual read/retrieval；pub等原metadata不改，不因typed pub晚于read或retrieved早于pub增加限制。无proof/null保留旧current路径。Read早于proof或retrieved晚于read仍按common actual-event拒绝。

ROOT同一公共mypy由11模块补到实际12，提前拦下9项旧类型债；本包在4处既有guard后加type-only cast（Match、parent、pointer/record、locator），没有新条件、ignore或第二gate。ROOT的CI/hooks两工程文件只由本line正常合并继承，未自行编辑。

## 最终验证与历史边界

- 现有validator初轮22FAIL/20PASS；ROOT actual-event补正3RED；ROOT current合法元数据补正2RED；公共12模块mypy9ERROR RED，全保留。
- 最终同12份相关合同/reader/clock/0.8与0.9golden/projected/helper：**298PASS /1既有POSIX SKIP，7.30s**；49新例全通过。公共mypy12、全ruff、正常commit hooks全绿。所有golden SHA不变。
- 原26/b76独审重放组合323P/1skip/1旧current原因码assert过期；不改原独审源，原记录保留，**不称该组全绿或它已签新代码**。当前精确码是actual-event source_clock_conflict，不能为了旧fixture恢复虚构asof。ROOT负责新typed/current非作者补审与实际producer组合。

## 安装、清理与下一步

只需runtime单文件选择安装。ROOT已装b76，下一安装expectedOld是 **0af725599bda25c883a040605a20e1bc2d3204de0a032ce1116f8c2b0e248ac6**（3逻辑/2物理目标），原94b观察留历史而不作新门槛。本line没有写安装、main、生产配置、预算或默认。

精确独占TEMP初始/最终不存在，三轮累计632文件/30640307B清理；只保留小证据，0下载/0API/0费用/0原件改删。JSON含源码/实际及LF SHA、每轮命令exit/日志XML、历史/当前安装映射和清理。

**唯一下一步：ROOT最终非作者补审2de → 必要公开CLI组合 → ff main、正常push与consumer选择安装 → CWP producer发布。** 仍未代签W03-B 0.9/v5生产语义、W07真实摘要/普通paid缓存恢复或研究/PWF全完成。
