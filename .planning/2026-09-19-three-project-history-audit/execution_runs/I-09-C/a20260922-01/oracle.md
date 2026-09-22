# oracle.md — I-09-C（逐边界故障注入、并发与重启恢复独立验收）

- card: I-09-C（父项 I-09）；attempt: `a20260922-01`
- 角色：revenue 发布负责人（独立签名/事务 reviewer）
- 冻结时点：**运行前**（本文件写成时，本卡尚未执行任何产品/测试命令；见 `preflight_anchors.md` §5）
- 本文件是**独立预期**，不是验收结论；实现者不自签 accepted。
- 骨架内容 = card 正文逐字转录 + I-09-A 冻结 oracle 逐字转录；**本卡不新增、不改写、不“补选”任何期望**。

## A. card 的正反例表（`card_I-09-C.md` L39–47，逐字转录）

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| P-C1 | prepare前后、JSON完成、Markdown完成、registry持久化前后、commit前后、返回前逐点kill | 按冻结表仅P0或完整P1可消费；无混包；未commit的P1资格为false |
| P-C2 | P1已commit后响应丢失，再重试同幂等请求 | 逻辑P1=1；返回/恢复可定位同发布；允许历史行数不误报重复bug |
| P-C3 | 两进程同时从同链尾提交；另一个reader连续读 | 链无分叉/断裂；无丢失提交；reader不会接受半行/未commit为正式包；允许短暂忙/重试按契约 |
| P-C4 | 恢复中再次kill；损坏prepare或成员hash；完整P0存在 | 再次恢复幂等；损坏项fail closed且保留诊断；P0不被删除或改写 |
| P-C5 | stdout pipe失败、直接API、validate-only、snapshot历史 | 各按冻结兼容矩阵；validate-only无发布写；stdout失败不伪称跨终端事务回滚 |

### 输入与独立预期（card L24–27，逐字转录）

- 每个故障点独立新目录与同一P0/P1输入；I-09-A冻结故障点与返回码oracle；两真实本地进程与只读consumer进程。
- 测试必须包括真正进程中止，Python finally不会运行；patch OSError仅证明异常路径，不代替崩溃持久性。

### 失败停止条件（card L55–57，逐字转录）

- 测试kill涉及未登记PID；底层持久性不满足已宣称平台保证；需要删历史行；只测异常不测真正退出

### 恢复边界（card L59–61，逐字转录）

- 只停止测试进程并保留scratch证据；恢复上一个完整测试包；真实registry/用户包绝不触碰；失败退回I-09-B并保留反例

### 关闭标准（card L63–65，逐字转录）

- 故障表逐行签收无缺格；两进程并发与全新reader/recovery成立；旧功能兼容与签名链通过；生产I-16/I-17仍单列待验

## B. I-09-A 冻结「故障点 & 返回码 oracle」（F1–F12，逐字转录）

来源：`execution_runs/I-09-A/a20260919-01/decision.md` §7（文件 sha256 `94a27b8ae31cb7467bf9910714e90777a1cec7790e3d6bca364c9e4062db8a57`）。

转录口径说明（原文 L410）：`rc` 一栏 = **producer 进程退出码**；「可见版本」= 读者进程判定。**A** = I-09-A 冻结预期（提案）；**E** = 该卡实测。`n/a` = 该卡未实测（I-09-C 范围），**不得**当作通过。

| # | 故障点 | 冻结预期（A） | rc（A） | 恢复动作（A） | 本卡实测（E） |
|---|---|---|---|---|---|
| F1 | prepare 前（输入强验证失败） | provider 调用 0、registry 新增 0、无成员 | 2 | 无（fail closed） | 未构造（I-08-A A-D4 已覆盖同类） |
| F2 | prepare 中（载荷/身份计算失败） | 同上 | 2 | 无 | n/a |
| F3 | JSON 落盘失败（P5-a） | 无成员可见、无 committed 行 | 2 | 重试写成员 | ✅ c02（rc=2；但**现状**仍留 1 行 → 见 F9） |
| F4 | Markdown 落盘失败（P5-b） | 同上（成员不齐 ⇒ 不可提交） | 2 | 重试写 Markdown | ✅ c03（rc=2；**现状**读者仍见 commit_qualified=1） |
| F5 | registry 锁获取失败 | 无 committed 行 | 2 | 超时后重试 | n/a（锁未实现） |
| F6 | registry append 前崩溃 | 无 committed 行；成员成为**孤儿**（不可消费） | — (kill) | 孤儿清理或重写 | n/a（I-09-C） |
| F7 | append 写了一半（torn line） | 链校验失败 ⇒ 整个 registry 不可读（fail closed） | 2 | 人工介入/从备份修复 | n/a（现状 `_read_entries` 会报错） |
| F8 | append + fsync 完成、回报前崩溃 | **已 committed**；重试必须得到**同一**逻辑 commit | — (kill) | 幂等重试 | 部分：N-8 显示现状无身份 ⇒ 重试不可判定 |
| F9 | 成员已落盘、registry append 失败 | 无 committed 行（成员不可见） | 2 | 重试 append | ✅ c04b（rc=2、无输出、0 行） |
| F10 | commit 可见后、返回前崩溃 | 已 committed；读者可见；调用者未知 | n/a | 幂等重试（同 `publication_id`） | n/a（I-09-C） |
| F11 | 恢复过程再崩溃 | 补偿行半写 ⇒ 链断 ⇒ registry 不可读 | — | 重入恢复（先查是否已补偿） | n/a（I-09-C） |
| F12 | stdout 输送失败（管道关闭/终端退出） | **无保证**（不可达保证，D-3 C-12 明列） | 0 或 2 | 无 | 未构造（不可承诺） |

配套 pin（同批只读文件）：I-09-A `oracle.md` = `D7F6B102ECC99A564FF6977B69A7B5E8FE6AF9EDCC4AE356C041426891E6DC8D`；`oracle_addendum.md` = `DE7FA1F335E4C4054E6CCCDB7D8C25160518BEE0EFC50BC1091DE9392715BCB5`（其中 §2/§4 记录 c04 冻结期望不成立、c02/c03 措辞更正——本卡消费 F 表时必须连同 addendum 一起读）。

## C. rc 语义（两套，分列不混读）

1. **producer/CLI raw rc**（F 表 `rc（A）` 列、P-C 各点的“原始 returncode”）：`0` = CLI 正常结束；`2` = CLI 按其契约失败退出；`— (kill)` = 进程被**真实**终止（Python `finally` 不运行）。
2. **harness rc**（`execution_v2/START_HERE.md` L90–115 冻结码表，本卡 runner 必须自带 `exit_code_legend`）：

| rc | 含义 | 判据 |
|---|---|---|
| `0` | 通过 | 命令正常结束，且业务判定为通过（外层 runner 退出 0 不能覆盖子命令失败） |
| `1` | harness 失败 | 测试/运行器自身出错：导入失败、夹具错误、期望文件缺失、路径未绑定 |
| `2` | 无裁决 / 预期拒绝 | 用例是负例且业务上被正确拒绝；或该命令不产生裁决（如只读查询） |
| `3` | 未达预期 | 正例未通过，或负例未被拒绝 |

> 每份 case 证据必须分列：`raw_returncode`（被 kill/被测进程）、`expected_raw_returncode`（F 表 rc(A)）、`harness_rc`（本卡 runner）、业务判定。`skipped`/`timeout`/未采集 ≠ 通过。

## D. 每点必须采集的证据（card L51 逐字 + 执行细化，均为“记录什么”，不改变期望）

- 每故障点独立run_id/输入/代码hash、hook位置与触发轨迹、PID证据、原始returncode及expected分离、reader观测、两次恢复结果、registry链全检与提交计数
- hook 只进测试构建代码、只在测试中启用；hook 位置需交独立 reviewer 核对“正常提交顺序未改变”。
- kill 只允许作用于 `new_run` manifest 登记的测试 PID；每点由**全新 reader 进程**记录可见包成员/hash/commit 资格（不看写者返回值、不只看无 tmp 文件）。

## E. 本 oracle 当前未覆盖 / 被阻断的项

- **未冻结到运行级**：每个 fault point 的独立目录名、注入 hook 的具体行号、PID manifest 格式 —— 这些依赖 iso 树与 harness 实现（九步第 2/6 步），在 STOP 解除前不创建。
- **未运行任何命令**（`commands.json` 全部 `binding_status=unbound`、`raw_exit_codes={}`）。
- **产品问题不修**：发现产品缺陷退回 I-09-B；本卡 allowlist = 隔离 publication transaction 测试 + 本次故障 harness。
- **锚点 STOP**：见 `preflight_anchors.md` §4——`scripts/revenue_forecast.py:55` 锚点既 ≠ card 也 ≠ 已登记漂移值，按 parent 指令停止在运行之前。
- 生产 I-16/I-17 仍单列待验（card 关闭标准原文）；`disclosure_adaptation=unmapped`、`accuracy=unproven`。
