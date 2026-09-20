# 独立买方审计验收清单

审计日：2026-09-18。审计对象为真实 A 股、港股、美股公司的 revenue-forecast 执行、filing-fetch 分支和 company-wiki 跨目录来源契约。独立审计者不制作生产预测、不修改产品代码、配置或来源数据。测试脚本、审计证据和报告仅在本审计目录保存。

## 判定方法

- **通过**：原始证据、可重复执行记录及结果共同支持；生产者口述、测试名称和 schema 通过不能单独构成证据。
- **部分通过**：实测子路径成立，仍有明确未测路径或投资用途限制。
- **失败**：可重复观察到与合同、会计口径、经营事实或用户需求冲突。
- **未证实**：缺少实测证据；不从单元测试推断生产有效。
- P0：可能静默产生重大的错误公司/时点/收入事实；P1：阻断交付或显著扭曲预测/可追溯性；P2：重要覆盖或操作风险；P3：文档/可用性问题。

## 经济和投资者需求

| 门槛 | 独立检查方法 | 不可接受的替代 |
|---|---|---|
| 公司身份与信息集 | 市场、主 ticker、财年、币种、单位、截止日与原文一致；所有来源发布日期不得晚于截止日 | 用下载日当发布日期；跨市场同名匹配 |
| 历史与基年 | 原始财务报表核对至少两年；优先 3–5 年及近期季度；分部外部收入加调整严格勾稽 | 仅能跑通的两个数字；重分类和并购不桥接 |
| 收入确认 | 商品控制权、服务履约、总额/净额、对外收入与内部交易、当期/递延分别核对 | 把订单、储量、ARR、GMV、产能直接称收入 |
| 经营驱动 | 每个重大业务通过客户/量/净价/留存/供给与期间权重重构；不足则明确低置信回退 | 全部直接 CAGR，或仅拆出没有依据的复杂参数 |
| 行业与生命周期 | 各业务分别判断成熟、周期、扩张或商业化；容量、市场和库存约束显式化 | 一家公司套单一行业标签 |
| 三情景 | 联动机制和可观测触发支持 low/base/high；离散风险覆盖，非固定±百分比 | 同时调好所有参数；将范围宣称统计置信区间 |
| 独立参考 | 行业/竞争对手/历史执行、失败样本、市场隐含份额与历史单位收入交叉检查 | 将管理目标直接设为基准；仅引用公司材料 |
| 定性传导 | 主要判断对应参数、年度、机制、替代解释及反证阈值；来源独立性人工判断 | 九行覆盖表代替研究；泛称品牌/AI/政策推动 |
| 重要缺口 | 按可能改变收入量级排序、注明影响方向与补证需求 | 用数量很多的小缺口掩盖重大未知 |
| 敏感性 | 对关键终期驱动和离散冲击重算，保留约束与存量流量依赖 | 无终期影响的早期水平冲击；敏感性简单相加 |
| 准确性 | 同一冻结信息集与基准进行真实样本外比较；没有历史冻结结果即未证实 | 模型验证通过就称预测更准确 |
| 投资可用性 | 数字可复核、主驱动量级/下行风险/监控指标清晰、条件和信任边界醒目 | schema正式状态或置信分数等同投资胜率 |

## 数据获取与跨目录验收

1. **已有文档分支**：保存请求、原目录/文件 hash、完整退出码及 stdout/stderr；核查 verified-active 身份、exact/latest 标记、源日期、零下载/零解析/零 LLM、原件没有复制或改写、handle 路径属于配置准入根。
2. **缺文档且无下载授权**：同样请求必须返回结构化 not_found；不得隐式下载或写 canonical；与“有原件但不能复用”分别说明。
3. **缺文档且获授权**：A 股走 StockInfo/cninfo、港/美股走 dayu；工作器原始暂停状态保存；超时/失败可恢复；新文件先 staging、hash 去重、写 canonical+provenance，索引后可 resolve；第二次请求应复用且原件 hash 稳定。
4. **跨根数据湖**：用实际 company_raw、dayu、Dropbox 存在的样本核验；原件与派生 normalized/summary 分开；复用派生物必须 source hash 和 producer binding 都匹配。某根没有符合条件样本即未证实，不用夹具代替。
5. **证据链闭合**：catalog document/location → 文件字节 hash → handle → source bundle/选中 artifact → revenue capture → claim locator/excerpt → parameter → forecast output；逐跳可复核。
6. **可重现发布**：input/output/result/receipt hash、一致的 engine version、输出重算、不可覆盖的 snapshot、publication registry、TRUST_BOUNDARY 与正式状态一致。

## 三公司专门审查重点

- 紫金矿业：矿产量与冶炼/贸易量分开，权益法项目产量不直接入并表收入；吨金属/克金/人民币单位，销量与产量、金属价格与净实现价、外售与内部抵销、并购及投产时点。
- 小米：手机出货与收入 ASP，IoT 品类/季节性与渠道库存，互联网用户/ARPU，汽车交付×净收入和单独爬坡/产能/质量风险；汽车与其他创新业务口径不得混淆。
- 微软：6 月财年及分部重述，Azure 增长率与云收入基数不可混用，订阅存量/净留存/用量、RPO 转收入和 AI 算力供给，gross/net，硬件和游戏成熟/收购口径。

## 只读基线发现（待实测确认）

| ID | 等级 | 预期与实际 | 证据 | 建议 |
|---|---|---|---|---|
| DOC-01 | P2 | filing-fetch Step 6/Hard gates 声称 handle 必须位于 companies 子树；同文 Notes 与生产配置允许 dayu_portfolio、directory 跨根复用。文档内部合同矛盾。 | ../filing-fetch/SKILL.md Step 6、Hard failure gates、Notes；company-wiki/config/source_catalog.yaml reusable_root_kinds | 将新下载 canonical 路径与注册根 read-only reuse 的边界分别写清；由真实跨根测试决定运行状态。 |
| DOC-02 | P3 | 主 SKILL 当前正式 schema 为 3.7；compliance-contract 首段称 schema 3.6 formal route 且 3.5 及更早支持，与下文 legacy 状态容易误读。 | revenue-forecast/SKILL.md Versioning；references/compliance-contract.md 开头 | 统一可生产和只读 legacy 矩阵表述。 |
| OBS-01 | 未证实 | source_preparation 声称支持不可用 exit 1，但 main 将所有 RuntimeError 统一为 upstream/exit 3；需实测 not_found 后判断是否吞掉语义。 | scripts/source_preparation.py 文件头和 main | 记录真实缺文件分支，避免预先判定。 |

此文件只是验收标准和文档基线，不表示任何公司预测或跨根路径已通过。
