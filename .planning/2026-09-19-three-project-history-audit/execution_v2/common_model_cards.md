# I-10：31个收入模型执行卡

全部状态为 planned。这里只制定执行文件，未运行新卡、未修改产品。JSON是字段完整的执行清单，与本文同次生成。

## 调度资格与证据位置

M卡调度accepted仅指A–C公式/负例资格通过。D–E是实际采用模型的企业披露适配资格，由先行I-10-A完成，供I-11-B及I-07-E消费；I-10-A不依赖I-11或I-07-E。F归I-12独立后续。D–F不阻断M卡的公式阶段完成，M accepted绝不等于披露或准确性通过。

所有evidence/<card_id>/路径相对于本轮新attempt_root；attempt_root由I-00-B绑定，不是本次历史审计目录或产品目录。每次尝试独立，禁止覆盖旧证据。

runtime负例沿用现行计算契约，不声称经济上永不可能。真实银行等业务可有负营业收入；若披露落在契约外，停适配并由专业reviewer审定扩展，禁止裁零或改会计口径造通过。

只读源码参考根为 `C:/Users/郑曾波/Projects/revenue-forecast`；实际执行cwd必须从I-00-B取得隔离checkout，不是该生产参考根。

## 共同规则

1. 合成公式验证、企业披露适配、准确性证明是三种独立资格。
2. 每个数字均为合成手算，不是真实公司披露；U是统一货币单位，实际使用必须填写币种/尺度/年度。
3. 从I-00-B绑定的隔离checkout根目录把 `scripts` 加入 Python 路径，只调用 `calculate_registered_model(**input)`。真实映射另经 `scripts/forecast/segments.py:61 calculate_model_path`。
4. 数值容差 `1e-9×max(1,|expected|)`；先核路径长度，禁止先四舍五入。保存命令、stdout/stderr、退出码和源码hash。
5. 已修的-100%增长、时间分数、负利率、重估/修订和非有限值拒绝保持。历史97测试/216子测试不代表实际预测准确性。
6. 可选默认值不是缺披露时填零/一的授权；缺失必须显式处理。专业判断未决，停在对应资格，不能改成整体PASS。

公共负例：

- N01：对首个必填driver首值分别替换True、float('nan')、float('inf')、float('-inf')，四个独立case → ModelRegistryError，不能用JSON解析器拒绝替代模型拒绝
- N02：首个必填driver数组替换为[]，其余不变 → ModelRegistryError/路径长度
- N03：删除首个必填driver → ModelRegistryError/缺字段
- N04：添加unknown_driver=[1]*len(years) → ModelRegistryError/未知字段
- N05：years替换为[]；另案仅将首个year替换True → ModelRegistryError/年度

所有披露字段需填：`entity_id/market/segment`、`source_doc_id/version/sha256/page/table/span`、`published_at/available_at/retrieved_at`、`as_of/fiscal_period_start/fiscal_period_end`、`currency/scale/physical_unit`、`raw_label/raw_value/raw_unit`、`normalized_value/conversion_formula`、`gross_net/tax/ownership/consolidation_scope`、`reported_derived_assumed/assumption_reason`、`restatement_mapping/reviewer`。


本文仅共用前提；领取具体卡见[调度表](dispatch.md)。
