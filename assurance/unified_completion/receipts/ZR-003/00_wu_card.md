# ZR-003 工作单元卡（preflight）— 紫金 golden corpus 脱敏注册

- 领取时间：2026-08-14T03:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-003`；units.ZR-001.status=accepted + closure.next=ZR-003。
- 依赖：ZR-001（accepted ✅）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** A0 基线：把紫金年报、七份研报、错误 strategy HTML 与预测 input/result 注册为脱敏 golden corpus（source/content hashes + 预期实体/角色/期间 + 只读 + 无内容泄漏），为 ZR-102/505/510 的 T2 真实样本验收与 ZR-503 多实体错归测试提供冻结 oracle。
2. **production entrypoint 是什么？** 真实样本文件本身（companies canonical PDF、Dropbox 七份研报 PDF、audit 封存 sources/outputs）。注册表/校验器是 assurance 工具链，不触碰任何生产写入口。
3. **哪个 current-triplet 行为是 RED？** 尚无 golden corpus 注册表（still_missing）；篡改样本字节必须被 verify 拒绝；样本字节不得出现在仓库提交物中（无内容泄漏）；样本缺失才允许 blocked。
4. **允许改哪些文件？** `assurance/unified_completion/corpus/**`（注册表+校验模块）、`uc/cli.py`（corpus-verify 子命令）、`tests/test_zr003_corpus.py`、`receipts/ZR-003/**`。禁止：产品代码/配置/CI、真实 catalog/roots 写入、把样本内容复制进仓库。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-102（hermetic T1 runner 依赖 ZR-002+ZR-003）、ZR-505/510（研报 golden 验收）。本卡不处理研报预处理/表格保真，那些归 ZR-504~506。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-001 accepted（机器状态 2026-08-14T03:19:24Z；closure.next=ZR-003）。
- [x] triplet 冻结：revenue=`7716b876f503e980932d8873cdaec393ced3274b`（ZR-001 closure 提交，领取时重读）；filing `83c638e…`；wiki `ef125ed…`。
- [x] 样本可用性（领取前已核）：年报×2（companies，hash 与 08-12 封存一致）；研报×7（Dropbox，本轮已算 sha）；strategy HTML（audit sources/，b2d215df…）；input/result（audit outputs/）。样本缺失=blocked 条件不触发。
- [x] 脱敏纪律：注册表只存 anchor+相对路径+hash+元数据，不存绝对用户路径、不存内容字节。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（assurance owner）；样本文件只读。
- **Current-state drift verdict**：`still_missing`——无 golden corpus 注册表。
- **Acceptance criteria**：`golden_corpus.json` 存在且 12 样本全部 hash/实体/角色/期间齐备；`corpus-verify` 对真实样本 rc=0 且零写指纹；篡改样本被拒；仓库内无样本字节泄漏；样本缺失时输出 blocked 语义。
- **Stop conditions / handoff**：生产 catalog/roots 写入、样本内容进入提交物 → 立即停止并 blocked。
