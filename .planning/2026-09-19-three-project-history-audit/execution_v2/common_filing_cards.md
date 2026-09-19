# I-03 / I-04 / I-08 / I-09 逐卡执行说明

**状态：全部 planned，实施未执行。Markdown 为执行权威正文；JSON 供 dispatch/校验。**

仅 I-03/I-04/I-08/I-09 的未来执行卡。本次未实施、未运行产品/测试、未下载、未写生产DB/worker/registry；仅此JSON与同名Markdown新增。

先CodeGraph定位定义/调用，再读已定位源文件并用Python AST只读核准精确行号/hash。CodeGraph部分行号落后，以下锚点以现行字节为准。

## 共用前置与边界

- 每卡先读取I-00-A/B/C及自己的依赖验收收据；planned不是可执行授权或完成。高级决策卡仅写设计收据，未签署不得实施。跨分区parent依赖由主审dispatch映射到实际卡，不由弱模型猜字母。
- 使用I-00冻结的隔离checkout/解释器/依赖；不覆盖用户dirty文件，不reset/stash主树；所有新增输入、日志、临时catalog、keys、registry、worker模拟文件放在新的new_run_root内。先检查绝对路径前缀，禁止生产公司根/正式registry/旧审计reviews路径。
- 逐个比较本卡源锚点sha256与当前待实施版本；不同即读差异和后继修复，让reviewer确认新基线，不能按旧漏洞重复修已修代码。这里只冻结规划时版本，不要求长期字节不变。
- 卡内“先重现修前失败”“确认修前错标”等动作，仅在当前冻结版本仍存在该缺陷时适用。若后继修复已关闭缺陷，则走无代码变更的原反例复验，记录修复版本与证据；禁止回退有效修复、改坏输入/实现、放宽或篡改断言来人为制造 RED。复验已通过且范围完整时可按无代码变更关闭该实现步骤，未覆盖范围仍保留待验。
- 执行命令模板前由I-00-B把占位解释器、cwd、argv、环境、输入hash与测试节点绑定到新run；复制原probe前先移除其固定旧证据写路径，不执行原脚本覆盖历史。
- 测试分级明确：pure fixture、真实代码本地跨进程、生产配置副本、真实只读数据、真实provider、生产写入。此分区最多前三类且本卡说明更窄；真实provider/安装态用户旅程归I-07/I-16。
- 凡跨项目公共schema、canonical writer、registry或worker API，只有指定owner写；发现scope外必要改动先记录阻断并交owner补卡，不能为绿灯建立平行框架。

### 每卡共同证据

- 新run唯一目录；卡ID、依赖收据hash、原义务及历史反例链接、源码/配置/解释器/实际导入路径hash、dirty清单。
- 输入实际字节/来源、手工独立expected和推导、完整stdout/stderr、raw_returncode、expected_returncode、判定分别记录；测试tier、collected/selected/passed/failed/skipped/deselected分别记录。
- 按本卡要求保存事件/调用/读写/elapsed/状态前后证据；断言不可仅为fileexists、计数或receipt.status=pass。
- 实现者与独立reviewer分别署名；未验和scope外项单列；失败保存原始输入和输出，不能换fixture/公司/口径以保持PASS。

### 禁止事项

- 本轮不执行卡、不改产品代码、不访问真实provider、不改变worker暂停状态、不迁移或清理公司数据湖。
- 未来实现卡不能把测试私钥、fake provider、模拟时钟、模拟PID或fixture-only PASS写成生产/真实市场验收。
- 不修改reviews/下任何历史产物；不运行会固定写入旧scratch/log的pure_probes.py、probe_publication.py或current_recheck.py。只读原脚本和结果。
- 保留已修F01/F02、capture_ready拒绝、有效Ed25519验签、单文件atomic replace等窄正确性；不重开已退役旧研究writer。

## 命令模板（本轮未执行）

占位符必须由 I-00-B 解析为审核过的绝对路径与 argv；不能把模板当现成新 CLI。每个模板的 expected_returncode=0，只对应测试框架成功退出；新增案例仍须逐项验收。不要为了通过而直接运行原历史探针，它们会写回自己的旧 scratch/log。

### T-GAP

已存在wiki contract测试的最小回归入口；不包括未来尚未创建用例的命令

cwd: `<isolated_company_wiki_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/contract/test_source_catalog_gap_plan.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "--basetemp=<new_run_root>/gap-pytest"
]
```

- 已读该版本conftest/测试，确认fake adapter/temp catalog且无生产默认根
- new_run_root是新建绝对路径，不等于旧审计目录
- 新增测试node由I-00-B在创建后绑定；本模板通过不等于新增反例已覆盖

### T-FILING

已存在filing测试文件中排除实际生产wiki依赖的用例

cwd: `<isolated_filing_fetch_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/test_fetch_filing.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "-k",
  "not test_cli_stdin_accepts_utf8_chinese_query",
  "--basetemp=<new_run_root>/filing-pytest"
]
```

- 源tests/test_fetch_filing.py:1438的中文stdin用例直接连接PRODUCTION_WIKI且无显式config，必须排除（历史继承会收集两次）；不能依赖它自动skip
- 逐版检查其余测试与conftest无新增live路径；实际deselected数量记录不硬套旧数
- 未来本地CLI模拟harness需先独立审路径隔离，禁止拿此live用例改公司名运行

### T-PUB

已存在revenue发布/签名/registry/单文件事务测试

cwd: `<isolated_revenue_forecast_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/test_publication_pipeline.py",
  "tests/test_publication_registry.py",
  "tests/test_attestation.py",
  "tests/test_zr710_publication_txn.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "--basetemp=<new_run_root>/publication-pytest"
]
```

环境约束：

```json
{
  "REVENUE_PUBLICATION_REGISTRY": "<new_run_root>/registry",
  "REVENUE_ATTESTATION_PROVIDER": "只在已批准fixture中设置；不得继承真实provider",
  "REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS": "<new_run_root>/测试公钥名单（若该用例需要）"
}
```

- 已读tests/conftest.py，会把registry重定向到tmp_path_factory；必须记录实际最终路径，不能只看外层env
- 原test_attestation.py:71把sys.executable当provider；真正调用协议前必须改为已批准有界fake provider，避免裸解释器挂起
- 旧ZR710仅证明单文件写/registry先失败，不可用其数量宣称整体提交已完成
- 所有测试新增hook/kill限已登记测试进程，不能操作真实worker


本文仅共用前提；领取具体卡见[调度表](dispatch.md)。
