本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-03-B — 按冻结期间和修订规则修复纯 GapPlan 选择

父项：I-03。状态：planned；实施结果：未执行。角色：company-wiki 来源负责人（filing 为消费者 reviewer）。

依赖：I-03-A、I-00-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [src/company_wiki/source_catalog/gap_plan.py:32](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/gap_plan.py:32) — `GapPlan`；SHA-256 `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。
- [src/company_wiki/source_catalog/gap_plan.py:95](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/gap_plan.py:95) — `build_gap_plan`；SHA-256 `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。

### 允许改动

- 隔离 wiki checkout 的 gap_plan.py；确需的既有 candidate/handle 字段映射须按 I-03-A 决策逐文件批准；tests/contract/test_source_catalog_gap_plan.py 及同目录新增隔离用例

### 输入与独立预期

- I-03-A 已签署 oracle；历史四反例中的前三例。
- 基本样本本地 L=z-old/FY2025/2026-03-01；远端 R=a-new/FY2025/2026-04-01；capture_ready=True；其他身份/期间相同。测试包装映射必须在输入工件中可见。

### 按序动作

1. 先添加独立断言并在修前隔离运行，保存失败；断言写固定 ID/类别，不从被测 planner 的排序函数计算 expected。
2. 只改 canonical planner 的分期与修订选择，删除 accession 字典序作为新旧依据；调用者继续消费该唯一输出。
3. 处理缺期、缺日期、同日冲突和未来披露，明确返回未知/冲突而非静默忽略；不得以增加默认日期修 fixture。
4. 测试远端输入顺序逆序与本地多根同 bytes 复用；允许的重排不改变语义输出；保留 capture_ready=False 不可复用。
5. 用 CN 年报/半年报、HK 年报、美股非日历年三个手工 metadata 样本执行同一冻结规则，保存字段来源模拟声明。
6. 运行 T-GAP 及新增用例；原正确复用/零下载行为保持。命中 I-03-A 未定义情况先补高级裁决，不扩范围自行推断。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| G-B1 | L=z-old，remote=[a-new]，日期同上述 | newer_revision 精确为 [a-new]；不把 z-old 当已最新 |
| G-B2 | L=a-new/2026-04-01，remote=[z-old/2026-03-01] | newer_revision=[]；本地可复用且不降级；最新性置信按决策表 |
| G-B3 | local=[]，remote=[z-old,a-new]，同一受信期间 | missing 仅一个 a-new；顺序反转结果相同 |
| G-B4 | a-new filing=2026-08-01；as_of=2026-07-31 | 不进入可下载/可复用当期候选；future 集或等价明确状态包含该候选 |
| G-B5 | capture_ready=False 的本地 + provider_error；两个根同 hash 的合格本地；不同期间相同 FY | 不合格本地不可复用；合格多根零重复下载；不同期间分别处理，不靠 fixture 公司名 |

### 本卡追加证据

- 每个输入 JSON/语义映射、固定 expected 与实际完整 GapPlan；修前失败和修后结果；调用图差异；T-GAP stdout/stderr/exit/选择与跳过数

命令： T-GAP；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 为得到绿灯而删除 unknown/conflict；需要改 provider/network/raw writer；新 schema 未获 I-03-A 批准

### 恢复边界

- 恢复本卡隔离代码变更；保留原反例与失败输出；不得修改生产 raw/catalog 或旧 gap 授权

### 关闭标准

- G-B1—B5 与冻结未知矩阵均满足；四类市场期间模板不外推为真实 provider 验收；由非实施者验收
