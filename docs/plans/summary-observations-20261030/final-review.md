# RF assessed narrative consumer：独立工程终审

**四路径工程范围 PASS，0 OPEN。** 独立冻结20项纯wire合成测试与永久消费者21项合计最新 **41P/1.49秒**。四文件raw/LF SHA和RF预存assurance三项状态绑定 `permanent-seal.json`（先前工程seal保留为`final-seal.json`）。审查只写ROOT本目录，无产品改写、hook、commit、下载、模型或真实PDF解析。

范围：`scripts/narrative_summary_observations.py`、`scripts/company_wiki_narrative_contracts.py`、`scripts/source_narrative_context.py`、`tests/test_assessed_narrative_consumer.py`。结论仅对seal中的字节成立；后续产品/测试字节更新须刷新seal。

## 发现与修复

初次15项10FAIL/5PASS：consumer对excluded task仅检查list、对validator dependencies仅检查非空hash字典、对diagnostic仅检查claim和rule字符串，均弱于CWP公开 `summary-assessment/1` wire shape/algebra。最后加入所请求的quality/skip公开不变量反例后，20项12FAIL/8PASS：draft需要review但没有program diagnostics时可错误投影成verified；skip summary.model=None仍可携带phantom versions.model。

ROOT修复后：

- 固定当前validator版本公开7个依赖键，implementation SHA绑定声明的dependencies canonical hash，不读取当前CWP源码hash，不将历史软件配方变成升级许可。
- excluded row有精确字段/status/reason格式；任务key唯一、与admitted互斥；duplicate代表必须在admitted中。仅验证已声明结果自洽，不重新决定哪个任务应该排除。
- diagnostic合法rule枚举和scope shape，普通diagnostic引用requested task与bundle中已验证span；unmatched/ambiguous范围保持task/span为null。不运行prose诊断、不复算来源task分类或风险结论。
- draft状态与bundle quality保持公开映射；diagnostic/missing-requested仍保留needs_review，风险claim仍需needs_review。new skip保留summary.model=None、versions.model=None、assessment=None，不制造模型或评估对象。

独立最终20项全部PASS（`recheck-tests.log`、`recheck-junit.xml`）；先前失败保留 `initial-tests.log`、`shape-tests.log`与初始review，未改写历史成全绿。

## 责任边界与兼容判断

新模块只依赖stdlib和RF自有canonical hash helper，没有CWP import、网络/目录查找、provider、模型或源材料解析。仅显式接受raw2.1/projected3.1 + prompt `reading-source-scoped/4.2.0` / producer1.1.0的assessment；旧raw2.0/projected3.0继续原语义且不凭空增加assessment字段。schema或prompt单边降级无法吞掉新assessment。

已存在context仍为`revenue-narrative-context/1`与`/3`，consumption receipt仍为既有`/1`与`/3`，assessment只作为可选源观察字段保留；legacy没有字段，new skip保留显式null。context.to_dict及receipt均隔离副本，修改消费receipt不污染验证context。

原始claims canonical hash绑定与artifact/ref/receipt/原件hash/locator校验链未被旁路。summary_assessment的semantic_status与subfact_coverage_status只能为not_evaluated；“没有已知程序诊断”不变成语义通过。budget-deferred与missing-requested分开，完整requested但尚有budget-deferred仍诚实保留admitted_emission_complete=False及deferred任务。

assessment不会改变`narrative_read_receipt`的初始not_consumed；后续真正的claim→used parameter→formula采用仍走既有精确parent/capture/span绑定。此工程审查没有将读到assessment、producer verified或20项合成全绿冒充实际预测采用。

## 验证方法与保护状态

独立命令使用ROOT `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --noconftest -c 本目录/pytest.ini 本目录/test_wire_independent.py`。只使用RF既有合成golden与公开wire对象，合成deps hash明确不声称生产来源plan证明。

永久单文件结果见 `permanent-tests.log` / `permanent-junit.xml`；该次9P是消费者新增测试，不是全仓测试。独立scope维持冻结20项，未扩展到真实loopback、模型/摘要执行或全仓审计。ROOT的真实loopback与实际采用收据应单独绑定其运行环境和真实来源。

预存assurance三项仅只读hash核对，当前均与baseline一致（seal为准）。本审查未运行hook，未stage或恢复这些WIP。

## 永久回归固化后的seal刷新

ROOT将12个关键wire反例固化到 `test_assessed_narrative_consumer.py` 并格式化：依赖键/自洽hash、excluded status/互斥/reason/代表、diagnostic rule/task/span/null scope、draft quality laundering和skip phantom model。反例在引用/claims hash重签后验证合同拒绝，未靠无关陈旧hash使测试假绿；未增加来源policy或语义规则重算。

独立复核确认生产三路径raw/LF与上一seal完全不变，仅永久测试变更。当前永久21项与原冻结独立20项合跑 **41 passed / 1.49秒**；日志 `permanent-final-tests.log`、`permanent-final-junit.xml`。最新 `permanent-seal.json` 绑定四文件；RF预存assurance三项raw hash仍与baseline一致。工程结论仍0 OPEN，不签真实预测采用。
