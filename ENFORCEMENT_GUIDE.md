# 强制执行控制器使用指南

版本: v1.0
创建日期: 2026-01-17

## 概述

强制执行控制器是revenue-forecast技能的核心保障机制，确保所有分析步骤必须完整执行，防止因任何原因（如省token、简化操作）而跳过流程。

## 核心功能

### 1. 步骤状态跟踪
- 每个步骤有明确状态：`pending`、`in_progress`、`completed`、`failed`
- 自动记录步骤开始和完成时间
- 持久化保存到`enforcement_state.json`

### 2. 步骤依赖验证
- 前一步未完成不能进入下一步
- 自动检查步骤依赖关系
- 阻止不符合依赖的步骤启动

### 3. 多维度防跳过机制（v2.5.0增强）

**设计理念**: 不依赖单一时间指标，而是从多个维度综合评估实际工作量

**验证维度**:
1. **Token消耗**: 衡量思考深度（如step4至少8000 tokens）
2. **内容产出**: 衡量输出质量（如step4至少5000字符）
3. **工具调用**: 衡量行动次数（如step4至少18次搜索）
4. **文件生成**: 衡量工作成果（如step4至少9个维度文件）

**通过逻辑**: 内容和文件是硬性要求，Token和工具调用可互补，至少满足两项才可通过

**优势**:
- ✅ 不受模型速度影响（速度快也能通过）
- ✅ 不受缓存影响（命中缓存也能通过）
- ✅ 更关注实际产出而非耗时
- ✅ 防止"快速生成垃圾内容"式偷懒

### 4. 完整性验证
- 验证所有步骤是否完成
- 验证是否有步骤被跳过
- 生成综合执行报告

## 基本使用

### 方法1: 直接使用控制器

```python
from core.enforcement_controller import EnforcementController

# 创建控制器
controller = EnforcementController("公司名称")

# 执行步骤
try:
    # 步骤0: 加载配置
    controller.start_step("step0")
    # ... 执行步骤逻辑 ...
    controller.complete_step("step0")

    # 步骤1: 初始化缓存
    controller.start_step("step1")
    # ... 执行步骤逻辑 ...
    controller.complete_step("step1")

    # 继续其他步骤...

except ValueError as e:
    print(f"步骤执行失败: {e}")

# 最终验证
validation = controller.enforce_complete_execution()
if validation:
    print("✅ 分析完整执行")
else:
    print(f"❌ 分析不完整: {validation.errors}")

# 打印状态报告
controller.print_status_report()
```

### 方法2: 使用集成器（推荐）

```python
from core.enforcement_integrator import EnforcementIntegrator

# 创建集成器
integrator = EnforcementIntegrator("公司名称")

# 设置检查清单验证
integrator.setup_checklist_validation()

# 执行分析（同上）

# 打印综合报告
integrator.print_comprehensive_report()

# 获取改进建议
recommendations = integrator.get_recommendations()
for rec in recommendations:
    print(f"- {rec}")
```

## 标准步骤列表

| 步骤ID | 名称 | 依赖 |
|--------|------|------|
| step0 | 加载配置 | - |
| step1 | 初始化缓存系统 | step0 |
| step2 | 判断公司类型 | step1 |
| step3 | 语言策略判断 | step2 |
| step4 | 执行9维度研究 | step3 |
| step4_5 | 品牌矩阵分析 | step4 |
| step5 | 执行公司类型专项分析 | step4 |
| step6 | 情景预测与加权计算 | step5 |
| step7 | 综合CAGR计算 | step6 |
| step8 | 综合评分 | step7 |
| step9 | 生成并保存报告 | step8 |
| step9_5 | 报告验证 | step9 |
| step10 | 更新缓存 | step9_5 |

## 多维度防跳过验证（v2.5.0新特性）

### 基本用法

使用 `complete_step_with_validation` 方法替代 `complete_step`，启用多维度验证：

```python
from core.enforcement_controller import EnforcementController

controller = EnforcementController("公司名称")

# 执行步骤
controller.start_step("step4")

# ... 执行分析逻辑 ...
# - 执行搜索（被记录）
# - 生成维度文件
# - 写入分析内容

# 完成步骤并进行多维度验证
controller.complete_step_with_validation(
    step_id="step4",
    token_usage=8500,        # 实际消耗的Token数
    content=all_dimensions_content,  # 生成的内容总长度
    tool_calls=20,           # 工具调用次数（如搜索次数）
    tool_types=["web_search", "read", "write"]  # 使用的工具类型
)
```

### 验证维度和阈值

| 步骤 | Token要求 | 内容长度 | 工具调用 | 文件要求 |
|-----|----------|---------|---------|---------|
| step4 | 8000+ | 5000+字符 | 18+ | 9个维度文件 |
| step5 | 5000+ | 3000+字符 | 8+ | 分析文件 |
| step9 | 3000+ | 3000+字符 | 4+ | JSON+Markdown |

### 通过逻辑

```
✅ 通过：满足以下任意两项
   - Token消耗达标 + 内容深度达标
   - 内容深度达标 + 文件生成完整
   - 工具调用达标 + Token消耗达标

❌ 失败：仅满足一项或都不满足
```

这样即使模型速度很快，只要实际产出（内容、文件、工具调用）达标，也能通过验证。

### 示例：速度快的场景

```python
# 场景：模型速度很快，step4只用了30秒，但产出充足
controller.complete_step_with_validation(
    step_id="step4",
    token_usage=12000,       # ✅ 超过8000要求
    content=dim_content,     # ✅ 6000字符，超过5000要求
    tool_calls=22,           # ✅ 超过18次要求
    tool_types=["web_search", "read", "write"]
)
# 结果：通过（虽然时间很短，但产出充足）
```

### 示例：偷懒被检测

```python
# 场景：想偷懒，跳过搜索直接生成内容
controller.complete_step_with_validation(
    step_id="step4",
    token_usage=2000,        # ❌ 远低于8000要求
    content=short_content,   # ❌ 只有1000字符
    tool_calls=2,            # ❌ 远低于18次要求
    tool_types=["write"]     # ❌ 缺少搜索和读取
)
# 结果：失败，抛出异常，阻止完成
```

## 传统防跳过示例（依赖验证）

### 尝试跳过步骤（被阻止）

```python
controller = EnforcementController("测试公司")

# 执行step0
controller.start_step("step0")
controller.complete_step("step0")

# 尝试直接跳到step2（跳过step1）
try:
    controller.start_step("step2")  # 会抛出异常
except ValueError as e:
    # 输出: 无法开始步骤 step2: 依赖步骤 step1 未完成 (状态: pending)
    print(f"正确阻止: {e}")
```

### 检测跳过行为

```python
# 即使手动绕过，也能检测
controller.start_step("step1")
controller.complete_step("step1")

# 跳过step2，直接执行step3
controller.start_step("step3")
controller.complete_step("step3")

# 检测跳过
summary = controller.get_execution_summary()
if summary["has_skipped_steps"]:
    print(f"检测到跳过: {summary['skipped_steps']}")
    # 输出: 检测到跳过: ['step2']
```

## 验证和报告

### 1. 步骤执行状态

```python
controller.print_status_report()
```

输出示例：
```
======================================================================
强制执行控制器状态报告
======================================================================
公司: 测试公司
总步骤数: 13
完成: 5 | 进行中: 0 | 待处理: 8 | 失败: 0
完成度: 38.5%

步骤状态详情:
----------------------------------------------------------------------
✅ 加载配置 (step0)
✅ 初始化缓存系统 (step1) ← [step0]
✅ 判断公司类型 (step2) ← [step1]
✅ 语言策略判断 (step3) ← [step2]
✅ 执行9维度研究 (step4) ← [step3]
⏳ 品牌矩阵分析 (step4_5) ← [step4]
...
```

### 2. 完整性验证

```python
validation = controller.enforce_complete_execution()

if not validation:
    print("验证失败:")
    for error in validation.errors:
        print(f"  - {error}")
```

### 3. 综合报告（集成器）

```python
integrator.print_comprehensive_report()
```

输出包含：
1. 步骤执行状态
2. 检查清单验证结果
3. 报告验证结果
4. 总体结论

## 集成到skill.md

在skill.md的执行指令中添加：

```markdown
## 强制执行要求 ⚠️

**必须使用强制执行控制器**:

1. 在分析开始时创建控制器
2. 每个步骤必须调用`start_step()`和`complete_step()`
3. 分析结束前必须通过`enforce_complete_execution()`验证
4. 任何跳过步骤的行为都将被阻止

**示例**:
```python
from core.enforcement_controller import EnforcementController

controller = EnforcementController(company_name)

# 执行每个步骤
for step_id in ["step0", "step1", ..., "step10"]:
    controller.start_step(step_id)
    # ... 执行步骤逻辑 ...
    controller.complete_step(step_id)

# 最终验证
validation = controller.enforce_complete_execution()
if not validation:
    raise Exception(f"分析不完整: {validation.errors}")
```
```

## 错误处理

### 常见错误

**1. 依赖步骤未完成**
```
ValueError: 无法开始步骤 step2: 依赖步骤 step1 未完成 (状态: pending)
```
**解决**: 按顺序执行，先完成step1

**2. 步骤状态错误**
```
ValueError: 步骤 step1 状态为 completed，无法开始
```
**解决**: 不要重复开始已完成的步骤

**3. 验证失败**
```
StepValidationError: 步骤被跳过: 语言策略判断 (step3)
```
**解决**: 补充执行被跳过的步骤

## 测试

运行测试套件：

```bash
cd .claude/skills/revenue-forecast
python tests/test_enforcement.py
```

测试覆盖：
- ✅ 正常流程执行
- ✅ 尝试跳过步骤的阻止
- ✅ 步骤依赖验证
- ✅ 状态持久化
- ✅ 集成器功能

## 文件结构

```
revenue-forecast/
├── core/
│   ├── enforcement_controller.py    # 强制执行控制器核心
│   ├── enforcement_integrator.py    # 集成器
│   └── checklist_validator.py       # 检查清单验证器
├── tests/
│   └── test_enforcement.py          # 测试套件
└── ENFORCEMENT_GUIDE.md             # 本文档
```

## 版本兼容性

- ✅ 完全兼容现有skill.md v2.3.1
- ✅ 兼容checklist.md v1.0
- ✅ 兼容validate_report.py v1.0
- ✅ 不破坏现有工作流

## 常见问题

**Q: 是否必须使用控制器？**
A: 是的。从v2.4.0开始，所有分析必须通过控制器执行。

**Q: 控制器会影响性能吗？**
A: 不会。状态跟踪轻量化，仅在步骤边界进行检查。

**Q: 如何恢复被中断的分析？**
A: 使用`load_state()`方法从保存的状态文件恢复。

**Q: 可以自定义步骤吗？**
A: 可以。使用`register_step()`方法注册自定义步骤。

## 技术支持

如有问题，请查看：
1. 测试用例：`tests/test_enforcement.py`
2. 代码注释：各模块的docstring
3. IMPLEMENTATION_PLAN.md：设计文档

---

*文档版本: v1.0*
*最后更新: 2026-01-17*
