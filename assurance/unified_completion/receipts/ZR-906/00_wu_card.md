# ZR-906 工作单元卡（preflight）— H：最终六类 ratchet（hardcode/dead path/complexity/type/coverage/encoding）

- 领取时间：2026-08-23T00:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-906`（ZR-905 closure → ZR-906）；锁 ZR-906（owner=zr906-implementer，nonce 14adaefb…）。
- 依赖：ZR-104（质量基线，accepted ✅）、"全部实现"（A~H 前置卡全闭）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H 第五卡——最终六类质量 ratchet（卡描述："root 特判 0、关键 legacy caller 0、critical coverage 阈值、Windows 错误 0；required check"）。现状缺口（RED）：六类 gate 分散（complexity ratchet 有、coverage gate 有但跑全量 pytest 未排除 fc1103 挂起 → 超时不可用、hardcode/legacy/encoding 无自动化扫描器、mypy 无零增长门）；无聚合器。
2. **production entrypoint 是什么？** 新 `tools/final_ratchet.py`（聚合六类 gate：hardcode 代码级特判扫描（docstring/注释防线语义标签白名单——ZR-603/611 模式）/ legacy caller 扫描 / complexity（test_complexity_ratchet）/ type（mypy 冻结基线 2）/ coverage（run_coverage_gates）/ encoding（BOM 扫描））+ 修 `tools/run_coverage_gates.py`（排除 fc1103 挂起 + timeout）。
3. **RED？** grep final_ratchet → 零命中；run_coverage_gates 实测超时（全量 pytest 含 fc1103 挂起）；无 hardcode/legacy/encoding 自动化扫描；mypy 无零增长门。
4. **允许改哪些文件？** revenue：新 `tools/final_ratchet.py`、新 `tests/test_zr906_final_ratchet.py`、修 `tools/run_coverage_gates.py`（tools/ 非产品路径）；receipts/ZR-906/**、locks、state.json、README 镜像、planning docs。禁止：scripts/ 产品代码改动、真实 catalog/root 写、下载、LLM。
5. **下一单元解锁？** ZR-907（contract/doc/sample drift patrol，依赖 ZR-906）或 ZR-901（PR 门）。本卡不做：CI required-check 集成（ZR-901）、filing/wiki 仓的深度扫描（本卡聚合器以 revenue 产品代码为扫描域，filing/wiki 由 ZR-901/907 覆盖）。

## Acceptance criteria

- **C1 扫描器非空洞（杀 G1）**：注入代码级硬编码名 / legacy 引用 / BOM 文件 → 对应 gate 红；注释/docstring 防线语义标签 → 绿（白名单语义）。
- **C2 聚合器可执行**：`final_ratchet.py` 输出六类 gate（hardcode/legacy/encoding/complexity/type/coverage）ok/RED；exit code 反映最差 gate；`--scanners-only` 快速模式（CI 用，跳过慢 gate）。
- **C3 零增长强制（杀 G2/G3）**：真实 scripts/ 产品代码 hardcode 代码级命中 0、legacy caller 0、BOM 0；coverage gate 排除 fc1103 后可运行（不再超时）。
- **C4 质量门**：全量回归零回退（基线 862 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：注入探针用 tmp 文件；真实 scripts/ 只读扫描。
- mypy 基线冻结 2（既有错误零增长门）；coverage gate 全量运行约 3 分钟（测试用 scanners-only 验证聚合器）。
