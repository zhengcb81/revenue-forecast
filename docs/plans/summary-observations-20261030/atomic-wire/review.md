# RF atomic wire consumer：实施与自审交接

**READY FOR ROOT INDEPENDENT REVIEW；当前自审0个未解决产品发现。** 本worker实施后自审，不将自己的测试称作另一名独立审查员验收；ROOT独审/正式发布仍待完成。

仅修改RF两路径：`scripts/narrative_summary_observations.py`与`tests/test_assessed_narrative_consumer.py`。`scripts/company_wiki_narrative_contracts.py`无需修改，作为公开边界一并seal。`final-seal.json`包含三路径raw/LF SHA。无commit/push/deploy、无hook/模型/下载/真实PDF解析。

## 改变与责任边界

原consumer将bundle2.1/3.1绑定到单prompt4.2。现在以frozen dataclass和只读MappingProxyType登记两个明确公开wire配对：

| prompt | assessor | dependency键集 | diagnostic规则 |
|---|---|---|---|
| reading-source-scoped/4.2.0 | source-summary-assessment/1.0.0 | matching/task_plan/admission/scoped_view/encoding/claim_roles/assessment共7键 | 原5个规则原样 |
| reading-source-scoped/4.3.0 | source-summary-assessment/1.1.0 | 原7键＋assertion_frames共8键 | 原5个＋possible_current_action_as_future、possible_project_capacity_basis_loss |

两者仍要求cap40、producer1.1.0、assessment schema1/22字段、bundle raw2.1/projected3.1、claims hash及dependency canonical hash、现有scope/algebra/quality/skip不变量。新归属诊断仍沿`possible_attribution_loss`。4.2不能接受新assessor/依赖/规则，4.3不能接受旧assessor/依赖形状；未知assessed tuple拒绝。历史`PROMPT`保留alias但不再决定所有评估分派。

未导入CWP或assertion_frames实现，未重算source frames、task admission、locator、语义或阅读范围。新规则只是有限程序possible观察，`semantic_status/subfact_coverage_status`仍只能not_evaluated；context/consumption schema不变，skip显式null model/assessment，receipt仍not_consumed。RF不验证bundle中根本不存在的projection7/request8/decoder7字段；这些upstream请求身份归CWP recipe owner，本consumer只核可见公开wire tuple。

## TDD与验证

- 原永久21项保留，新增36项公开合同用例；先红 **13 failed /44 passed /2.87s**（red-tests.log、red-junit.xml），再 **57 passed /0.52s**（green-tests.log、green-junit.xml）。13失败均为合法4.3 raw/projected/skip/诊断原先被单prompt代码拒绝。
- 正反例包含：两prompt raw/projected、合法skip、receipt副本隔离/not_consumed、old/new assessor和依赖错配、缺/额外键、未知prompt、draft quality laundering、每个旧/新rule与版本归属、新projected诊断保留needs_review/not_evaluated。
- 六个短相关模块 **262 passed /3.97s**，见related-tests.log/junit：assessed consumer、public reader、w04 public consumer、DU11 citation context/consumption、shared reading contract。使用`--noconftest -p no:cacheprovider`，没有运行跨仓真实loopback或完整公司loop。
- Ruff check消费者/公开边界/测试PASS，两个改动路径format-check PASS，见ruff.log；git diff --check PASS。
- 仓库既有precommit/CI精确类型命令 **15 source files PASS**，见ci-mypy.log：

```text
python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py scripts/company_wiki_narrative_contracts.py scripts/narrative_summary_observations.py --cache-dir <ROOT-owned-ci-mypy-cache>
```

### 保留的探索性类型结果

在ROOT给出精确CI命令前，本worker手选15个narrative/capture编排源做了一次探索性检查，出现3个既有错误：source_narrative_context.py:146的Any|None传_claim；source_preparation.py:205的kind Any|None、:432的**reader_options与bool参数。两个文件`git diff --name-only`为空，不在本轮写权限内，未修改。原失败记录保留mypy.log；只对consumer/contract的聚焦2源也PASS（mypy-focused.log）。这不替代固定CI gate，也没有另选15源把原命令涂绿。

## 自审与保护

有限catalog只有显式4.2/4.3，不是动态插件/策略引擎；原字段检查、scalar类型、subset/algebra、diagnostic source_span在已验证bundle内、unknown/duplicate互斥、risk claim needs_review、claims/deps哈希和quality投影仍在同一函数执行。新增规则走同一已定义普通scope shape，不增加语义NLI承诺。

授权两路径差异与三项原有assurance WIP清晰分开；config/source_catalog、RF output、其他源无本worker改动。before-domain.json与final-seal.json比较：三项assurance raw hash与baseline相同，output147文件的路径/size/mtime元数据摘要均为`f5e660f542004c39a8208e1b37dfc12c85b3a6a72d8dcb4e0c7f870ab08e6ce9`，没有输出写入。

该交接不签source framing正确性、新CWP请求实际生成、付费摘要改善、真实RF研究/参数/公式采用。下一步仅ROOT独立审查这两个改动路径及本收据，再由ROOT按正常流程决定发布。
