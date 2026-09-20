# Owner 裁定单（2026-09-20 汇总；供一次性拍板）

本文件把 PLAN 里**所有需要 owner（你）签字才能继续**的门集中成一张可勾选的清单。
每条给出：**问题 → 选项与后果 → 复核者/实现者的建议（若有）→ 解锁什么 → 签在哪里**。
未签之前，相关卡一律保持 `blocked`/`review_pending`，实现者不得自决（这一条已被多轮复核确认执行到位）。

勾选方式示例：在「裁定」栏写 `选 A` / `选 B` / `照建议` 即可；涉及数值的直接写数值。

---

## 一、解锁面最大的一片：D-W05 与 D-W06（≈20 张卡）

这两项签字后，**I-05-B/C、I-06-B、I-07-B…E、I-12-A…E、I-13-A…C、I-16-A/B、I-17-A/B** 整条链才可开工。

### D-W05（I-05-A）
- **W05-1（OPEN-1）版本死锁**：`section_extractor` 对"已有 `completed` 行"的文档**永不重算**，只按 `sec.status='completed'` 取用、**无版本比较**；因此历史 sections 工件将永久停留在"仅源窗口校验、无 per-slice 哈希纵深"的状态，正常管道无法自愈。
  - 选项 A：**接受现状**，把"历史工件只享受源窗口绑定"写进契约，并在 D 阶段把"无哈希工件"标为低置信（成本 0，风险：历史工件若被同源改写只能靠源窗口抓出）。
  - 选项 B：**允许一次性回填/重算**（需定义"哪些版本算本卡产物"、重算是否改 `content_sha256`、如何记账）。
  - 选项 C：**新增版本比较**（把 `generator_version` 纳入取用判据）⇒ 会改变"已完成行"的取用语义，需新 oracle。
  - 复核者未给单一建议；实现者明说"交 D-W05，不自决"。
- **W05-2（OPEN-7）`as_of_date`**：本卡取 `""`，而 `service.query_source_bundle` 用 `published_date`。需定：两者是否等价、空值是否合法。
  - 选项 A：显式规定 `as_of_date` 为必填且等于 `published_date`；选项 B：保留空值并规定"空=未指定，不参与筛选"。

### D-W06（I-06-A）
- **W06-1（OPEN-2，决定性）幂等键不含请求身份**：实测同一 `demand_id` 会携带**首个请求**的 `request_sha256`，而两个仅 `as_of_date` 不同的请求得到 `d8afcf31…dd62` 与 `4bddf9e6…0b84` 两个不同请求摘要 ⇒ 重放/去重语义错位。
  - 选项 A：**幂等键 = hash(请求身份)**（含 `as_of_date`/目标/载荷摘要），同一请求重复提交才复用；选项 B：保留现键但**拒绝**键同而载荷异（fail-closed）。
  - 建议（复核者）：**必须先裁此项**，否则 I-06-B 无法写出可失败用例。
- **W06-2…6（OPEN-1/3/4/5/6）**：见 `execution_runs/I-06-A/a20260919-01/handoff.json` 的 `open_questions`（候选处于 UNRATIFIED 状态，不得落地）。

---

## 二、产品实施与晋升

### D-W15（I-15-A，生产 prune）
五项（W15-1…5）均未签；复核者已确认：证据/诊断层 `accepted_scoped`（五类反例可复现、`6 failed/5 passed`），**但产品实施仍 blocked，不得开工、不得执行任何生产 prune**（现有实现"空目录也删/同日覆写/时钟取目录名/TOCTOU/崩溃后不可恢复"）。
- 裁定：签/不签；若签，是否允许按 `decision.md` 的 proposed 方案改写 `prune_retired_evidence.py` 与 `archive_retired_evidence.py`（注意 `archive_retired_evidence.py:65` 仍以 `"wt"` 截断写快照）。

### I-14-A D1/D2/D3（晋升 `iso/slo_probe_patched.py` 进 `RF/tools/` 的前置）
- D1 → 由**非本探针作者**的运维 reviewer 签（50 ms 间隔是否足够、live `rss` 峰值 vs `peak_wset` 可比性、误差规则）；
- D2 → 生产 SLO / 探针 owner 确认（含 `catalog_dir` 标量解析器限制）；
- D3 → I-16 确认（bundle 未被测量时**恒 exit 2** 这一契约变更）。
- 未签前**禁止**把补丁拷进 `RF/tools/`；I-16 实测前必须先提供 bundle 测量文件。

### I-14-C C12（产品侧硬前置）
F-07（redactor 阻塞）用例在无 timeout 包装时**挂起 >90 s**（不是失败）。产品测试必须加 `pytest-timeout` 或把调用放进**带硬超时的子进程**，并实测"阻塞 ⇒ FAIL"后才可关闭 C12。C13（裸值贪婪语义吞掉后续诊断，112 字符→34 字符）已冻结，不改代码，但**描述已按事实更正**。

---

## 三、签字信任域（I-08-A / I-08-B / I-09-A）
- **OPEN-D7（优先）**：`W`/`T`/`L` 三个数值（provider 超时、stdout 上限、签名窗口等）。裁决前任何人不得把具体秒数/字节数写成规范值。
- **OPEN-D1/D2/D3 同批**：issuer 命名、轮换与撤销语义（分批会使 I-08-B 返工）。
- **OPEN-D6**：3.8 的消费者旁路缺口（实测仍在，`invest_contracts.py:1116`、`:1131-1132`）须开**跨仓卡**落地 R-LEGACY-1 与 E29。
- **OPEN-D4/D5**：D4 可由 revenue publication owner 自决（决定写入 decision 修订）；D5 需跨仓双方签字。
- **I-08-B CONFLICT-1/2**：复核者已判**接受**（豁免集 + 两条 AST 断言已加固；golden 刷新有新旧两树各 1 passed 的补证）⇒ 只需你**追认**。
- **I-09-A OPEN-I09A-1…6**：① `package_target` 语义（逻辑名 vs 路径）+ 与 D4 耦合；② 同请求两目标算一个还是两个发布（**由 ① 导出**）；③ 成员角色名清单 + attestation 锚**一次**行 schema 升版（锚**不得**进入 `identity_payload`）；④ registry env 指向目录的 fail-open 已写入 I-09-B allowlist（fail-closed + 负例）；⑤ 依赖验收冲突（已由 I-00-A errata 确认与 I-08-A 裁决部分消解）；⑥ **I-08-A §7 次序修正**（"注册→写 output"改为"成员落盘→唯一 append"，须由 I-08-A owner 写入上游文本，附**孤儿成员五条规则 + E31 四段式重述**）。

---

## 四、单卡级
- **M08 三步**：① 裁定读法 **C 权威**；② owner 更正索引（**更正目标按实测**：`card_M08.md:42`、`model_cards.md:552`、`model_cards.json:1930`、`dispatch.json:5755` 印的都是 `手算：100+40−5−10−15−60=50；−15重估必须剔除。`；读法 C 的带符号呈现应为 `100+40−5+−10+−15−60`，**期望 `[50]` 不变**）；③ 更正后 reviewer 用同一 `code_root 9ec65295…` 复跑留档。
- **M02-01**：被忽略字段是否仍受域约束（实测 `base=-5` 仍被拒）⇒ 选 A 保持 fail-closed / 选 B 忽略未用字段。
- **I-11-A OPEN-1…10**：① 是否允许 `pdftotext.exe` 作第二独立取文路径（sha256 `252d2b34…`）；② 紫金铜当量系数（结论每 +1 吨/千克移动 ≈10,670.9 元/吨铜当量）；③ 微软 FY2027 是否仍 PBP/IC/MPC；④ 页码口径是否升为 schema 规范值；⑤ 港股原文可读性归谁解决；⑥ 四条专业阈值是否采用；⑦ 命题 1/6 的分部集合；⑧ `oracle` O-6 页号措辞（实测 offset=+1）；⑨ I-11 模板是否升级为超集；⑩ `reviews` mtime 口径。**OPEN-2/3/5/6 阻塞 I-11-B/I-07-E。**
- **I-14-B D-1…D-6**：① reviewer 在 `oracle.md §6.1` 填 `frozen_tolerance_seconds`（实现者提议 5 s；实测扫描 tol ≤86 s 全拒、87 s 起通过）后才能开真实窗口；② 是否用 PATH 上的 ffmpeg/playwright 建捕获路径并授权启动 worker/UI 窗口；③ 由 I-17-A reviewer 签定保留哪些自然窗口；④ 本卡产物不进生产树。真实 30/60/120 检查现为 **blocked**。
- **I-04-C C2（OPEN-3）**：`lock_budget_for(x)=min(x,60)` 的命名/边界验收 + `worker-pause` 是否留在锁内（现维持锁内）；**不阻塞签收**。

---

## 五、复核者建议"新立卡"的产品级缺陷（进入 D 阶段前必须处理）
1. **`model_registry.py:335` 静默补 0**：无显式 default 的 optional driver 被补 `0.0`（**31 个槽位 / 24 个模型**）⇒ 把"不存在"与"没找到"编码成同一输入，D 阶段会直接产出错误映射。建议：省缺即抛 `ModelRegistryError`（把隐式 0 变显式 0 仍无法区分"没找到"）。
2. **`_SIGNED_DRIVERS` 按名字定符号**：`other_revenue` signed 而 `usage_revenue` 非 signed；`franchise_system_sales`/`supply_revenue`/`recognized_performance_fees` 同属"可冲回已确认金额"却在 `[0,inf)`。建议与第 1 项同卡改为**基于语义角色**的规则。
3. **rc 码表跨批不统一**：M05–M08 用 `2=harness`，M09–M16 等用 `1=harness / 2=no-verdict / 3=negative`；同一个 `rc=2` 语义不同，跨批聚合会误判。建议**冻结一个码表**写入 `START_HERE.md`，各批带自描述 `exit_code_legend`，**不回改历史 rc**。
4. **I-00-B 绑定范围追认**：其 `binding.json` 只绑"隔离方案 + 两阶段规则"、未物化 checkout，而卡片 L49 明写"从 I-00-B 读取 isolated checkout"。建议书面追认"物化由各 attempt 完成并记录来源 hash"（各批实测快照与生产逐字节相同）。

---

## 六、待你知悉的治理事件（无需签字，但需裁定口径）
- **`oracle.md` 事后编辑**（I-08-B N2）：`8d6dc81b… → bd67211f…`，binding 已重新登记。复核者明确"**治理裁定我无权作出**"。建议口径：允许追加式 provenance 登记（写明何时、为何、新 hash），**禁止**回改为"从未编辑"。
- **M03 冻结正文被改动过一次**（印刷笔误 `123,751.5203…`→`123,751.503987`）：已按 PERMANENT provenance event 永久登记，**不回改**。
- **M21–M24 的 `oracle.md` 0–11 节未能逐字节不变**：因复核要求的改动本身落在冻结正文（负例表/计数）与新增第 12 节；处置为**白名单校验的定点编辑**（每处改动行必须含复核明确的 token，否则拒绝写入并回滚；改动行 8/6/8/17、白名单外 0 行），diff 与前像留档。**复核者已裁决：可接受，但仅此一次、自此冻结**；第三轮若再编辑正文即判 `blocked`。另登记其机制弱点：白名单 token 是**子串匹配** ⇒ “白名单外 0 行”属弱保证（真正保证来自复核者的独立复算）。

---

## 七、第三轮复核后新增 / 变动（2026-09-20 04:1x）

1. **【已由 reviewer 落定，无需你签】I-14-B D-1**：`frozen_tolerance_seconds = 5`、`capture_latency_tolerance_seconds = 5`。依据为两处独立实测夹出的合法带 **[1, 86] s**（L1 `tol=0.9 拒 / 1.0 通过`；L2 `≤86 拒 / 87 起通过`）。改动仅 `oracle.md` L128–131，`093899bc…→f8082205…`，填前副本留档。**签字 ≠ 可开真实窗口**：真实 30/60/120 仍 `blocked`。
2. **【需你定】跨批 runner 修复是否推广**：M17–M20 已把 F-01 修好（`5307d2cc…`，逐例 `expected` 按异常**精确类型名**比较 + `declared_expectation_mismatch` + 变异臂 F）。**不推广的代价**：M05–M16 / M21–M31 各批的“逐例拒绝语义”仍无自动门（改 `expected` 后仍 rc=0，四批 reviewer 各自独立命中）。建议：只改**各批自己**的副本、`before/` 留旧版、**不回改历史 rc、不动冻结证据**，并在每批补“改 expected ⇒ rc=3”变异臂。
3. **【需你定】I-14-B D-2**：是否授权新建 UI/进程捕获路径。事实：PATH 上确有 `ffmpeg.exe`/`playwright.exe`，但 `playwright` 在隔离解释器内**不可导入**、4002 个候选文件中 **0 个**预布置记录器。reviewer 维持 `blocked`、**不授权**，并认为这属你的专业决定 + 新卡。
4. **【需你定，建议立卡】`natural_window.py` 两个产品级缺陷**（reviewer 自造用例实测被 accept）：①`claim.basis` **无枚举校验** ⇒ `basis=''`/缺失/`None`/`'wall_clock'` 全部被接受，J1/J2/J3/J11 可被一个字段名绕过；②`union_of_windows`/`sum_of_windows` 把 **quick_check 计入自然观察时长** ⇒ 2220 被接受而诚实的 1740 被拒。注意②**已烧进冻结期望**（W1 `union_seconds=2220`），修复必须同时以追加式 provenance 更正期望 ⇒ 属产品 + 计划双侧动作。
5. **【已撤回，无需裁定】M31“卡片必填清单不含 `net_revenue_per_unit`”**：不成立 —— `card_M31.md:9` 与 `model_cards.md:2818` 均列该驱动（7 项），`binding.json`/`oracle.md §12`/`handoff.json` OQ-04 标题为误读。改为**勘误**（纯文字，不改数值结论）；**勘误完成前 M31 不得关闭**。
6. **【口径确认】`oracle.md` 文本不得作为“事前冻结证据”**（OQ-05，M29–M31）：formula 资格由**可逐字节重生成的 `oracle.json`** + **生成器代码运行前已 hash 到盘上文件**（`scripts/oracle_<CARD>.py`，`3177247f…`）+ `oracle.json` mtime 早于产品 stdout 承载。若你需要“文本事前冻结”这一更强主张，须按最小范围**重跑**（每卡全新 attempt、单趟不中断、清理 pass-1 残留、不复用旧 evidence、由 reviewer 在独立 session 先取 hash 再放行）。
7. **【口径确认】冻结正文定点编辑**：M21–M24 的裁决是“仅此一次、自此冻结”；第三方若再改 0–12 节正文即 `blocked`。今后同类需求一律**追加节**（写明“第 X 行已过时，以本节为准”）。
8. **【待你知悉，已更正】记账审计两处错误**：I-02-A 的 `:5` 本就是 `pending` 占位文本（审计把 `:5`/`:70` 说反了）；**“全 PLAN 树不存在 `oracle.json`”是错的** —— `evidence/<CARD>/oracle.json` 与 `recovery/selfcheck/evidence/<CARD>/oracle.json` 均实际存在，相关更正只断言“`copy/`、`copy_r2/` 快照目录缺失”。
