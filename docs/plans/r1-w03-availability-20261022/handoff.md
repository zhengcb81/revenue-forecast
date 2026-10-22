# W03-A RF 可用时间证据交接

状态：**REVIEWED_ENGINEERING_CONSUMER_GREEN_PENDING_ROOT_COMPOSITION**。最终产品 `b76fb96f9b410abceefc6b264120c5101654492b`（含初版6efbebc3），分支 `codex/r1-narrative-availability`，基线 `92b69682`。未合主线、未推送、未安装。此文件和JSON取代初版交接中的产品/测试计数。

## 产品与责任边界

只改 `scripts/company_wiki_narrative_contracts.py`，新回归 `tests/test_r1_narrative_availability.py`。raw `narrative-read-receipt/1` 只增加可省略/为null的 `availability_evidence`；完全复用 `contracts.source_clock` 的现有proof形状、SHA、资格和actual-event规则，没有第二种证明、身份或权限链。

manifest/ref既有同SHA、身份、期间和请求绑定先执行，随后判断时间。未知pub仍null，合法同SHAprior/archive/current-open proof可判断截止日；known future/invalid publication仍优先拒绝；known past不因更晚capture退化。既有拒绝码 `source_after_as_of`、`source_publication_unknown`、`invalid_as_of_date`保留。

有历史asof或实际提供proof时，保留qualifier返回的eligibility，调用原 `validate_source_events` 核实际read_at/retrieved_at；不自写日期比较。**asof=None且省略/null proof保留既有当前读取语义**，pub仍typed而不授历史资格。有proof的当前模式用真实receipt.read_at UTC日交common qualifier，再核actual events，不能靠省略asof绕过晚证明。known pub早于read时，不因更晚proof日期拒绝。

完整proof只保留在 `context.read_receipt`，不增context字段，不进immutable bundle、generation、缓存身份或模型输入；receipt仍16KiB。projected `/3` exact字段集合不改，A/B任一parent的root single proof（含null）都不能放行projection。

## TDD与集中节点

- 未改旧validator首轮 **22 FAIL /20 PASS，1.92s**；实现后同42例全PASS。
- ROOT集中检查指出actual-event边未接，先得 **3 FAIL /2 PASS（42未选），0.72s**，确认为缺失既有时钟规则。复用common事件规则后，原current/no-proof兼容测试曾1FAIL；保留旧current语义，**未改该既有测试或golden来适配实现**，失败日志也保留。
- 最终12份新旧reader/source-clock/0.8和0.9存档golden/引用/parent合同：**296 PASS /1既有SKIP，4.49s**，其中本包47新例全部PASS。唯一skip是Windows不跑POSIX executable-provider CLI。
- 全scope ruff、公共mypy11源码、host guard通过；两次产品正常commit的ruff/mypy/host guard全绿，无跳hook。
- 冻结fixture所有SHA保持不变，旧omitted receipt消费结果字节不变。完整命令/exit/XML/source SHA与LF映射见JSON/evidence。

受控RF reader child确实跑原有进程适配并保留完整proof，但它是本地wire夹具。RF不重新打开原件；本线0 raw original open/0下载/0外部API。**没有代签真实CWP producer、其原件单次打开或正式摘要质量**，这些由CWP线和ROOT实际组合节点验证。

## 安装与保留

ROOT仅定点同步 `scripts/company_wiki_narrative_contracts.py`；source_clock是W02已存在依赖，本包没改。三份安装旧SHA与物理别名见JSON，最终只读复核未变；先consumer独审/发布/安装，再producer。本新回归需ROOT集中接既有CI显式SMOKE_TESTS，本lane没改CI/hooks。

原件、生产配置、预算/账本、FF/ET/CWP、0.8默认与研究状态均未动。精确独占TEMP `C:\Users\郑曾波\Projects\revenue-forecast-r1-boundary\.planning\w3` 初始/最终不存在；两轮累计清理424文件/20367027 bytes，逐轮收据保留。只留小日志/收据，不复制raw，不声称未测的峰值通过。

## 下一步与未覆盖

ROOT按最终产品SHA做非作者独审 → 新CWP真实PDF/native JSON公开CLI→FF/RF组合/single-open/scope/golden → consumer优先并线、选择安装与发布。W03-B 0.9/v5实际生产选择/正式summary/context、W07配置内真实摘要/普通paid恢复/cache/四审仍OPEN；本切面不等于共享引擎生产全完成。

## 非作者独审完成

`/root/r1_w04_summary_runtime` 独立26例 **26 PASS /0 FAIL /0 SKIP，0.47s**，绑定最终b76产品真实runtime SHA、前后不变；正式 `r1-w03-rf-independent-20261022.md/json`，状态 `PASS_ENGINEERING_CONSUMER_ONLY`。JSON SHA `41cb7b2e8ac7f4a9d3f26e6f20986aac523928b59382d4956683421f08068c53`。仅消费者工程签收，未替ROOT代签真实producer组合或live。下一步ROOT真实producer→consumer组合和顺序发布/安装。
