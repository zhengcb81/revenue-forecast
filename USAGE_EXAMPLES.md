# Revenue Forecast Skill - 使用示例

**版本**: v2.5.0
**更新日期**: 2026-03-01
**适用场景**: 验证脚本、检查清单、完整流程使用示例

---

## 1. 验证脚本使用示例

### 1.1 基本验证命令

```bash
# 验证阿里巴巴报告
python validate_report.py 阿里巴巴 "C:\Users\郑曾波\Projects\Research\outputs"

# 验证药明康德报告
python validate_report.py 药明康德 "C:\Users\郑曾波\Projects\Research\outputs"

# 验证小米集团报告
python validate_report.py 小米集团 "C:\Users\郑曾波\Projects\Research\outputs"
```

### 1.2 验证输出示例

**成功验证示例**:
```
✅ ================================
✅ 报告验证结果: 阿里巴巴
✅ ================================
✅ 1. 文件完整性检查: 通过
✅   - JSON文件存在: RevGrowth_阿里巴巴.json (15.2KB > 2KB要求)
✅   - Markdown文件存在: RevGrowth_FullReport_阿里巴巴.md (28.5KB > 10KB要求)
✅ 2. 语言检测: 通过
✅   - 中文比例: 94.4% (>70%要求)
✅   - 英文比例: 5.6% (<30%要求)
✅ 3. JSON格式验证: 通过
✅   - 必需字段完整: company_name, analysis_date, score, key_metrics等
✅   - 参数溯源字段存在: parameter_tracing
✅ 4. Markdown章节验证: 通过
✅   - 执行摘要: ✓
✅   - 关键财务指标: ✓
✅   - 双曲线业务分析: ✓
✅   - 情景分析: ✓
✅   - 投资建议: ✓
✅   - 参数溯源: ✓
✅ ================================
✅ 所有检查通过! 报告符合v2.5.0框架要求
✅ ================================
```

**验证失败示例**:
```
❌ ================================
❌ 报告验证结果: 测试公司
❌ ================================
❌ 1. 文件完整性检查: 失败
❌   - JSON文件存在: RevGrowth_测试公司.json (1.5KB < 2KB要求)
❌   - Markdown文件不存在: RevGrowth_FullReport_测试公司.md
❌ 2. 语言检测: 失败
❌   - 中文比例: 45.2% (<70%要求)
❌   - 英文比例: 54.8% (>30%要求)
❌ 3. JSON格式验证: 失败
❌   - 缺少必需字段: parameter_tracing
❌ 4. Markdown章节验证: 不适用(文件不存在)
❌ ================================
❌ 验证失败! 禁止进入第九步
❌ 必须修正以下问题:
❌   1. 重新生成Markdown完整报告
❌   2. 确保报告语言为中文(英文比例<30%)
❌   3. 添加parameter_tracing字段到JSON
❌ ================================
```

### 1.3 验证脚本参数

```bash
# 完整参数格式
python validate_report.py [公司名称] [输出目录路径] [可选:详细模式]

# 详细模式
python validate_report.py 阿里巴巴 "C:\Users\郑曾波\Projects\Research\outputs" --verbose

# 指定JSON文件路径
python validate_report.py --json "C:\path\to\RevGrowth_阿里巴巴.json" --markdown "C:\path\to\RevGrowth_FullReport_阿里巴巴.md"
```

---

## 2. 检查清单使用示例

### 2.1 检查清单文件位置

```
.claude/skills/revenue-forecast/checklist.md
```

### 2.2 检查清单使用流程

**Step 0: 加载配置**
```markdown
### Step 0: 配置加载 ✅
- [x] config.yaml文件存在且可读取
- [x] 缓存目录路径正确: revenue-forecast-cache/
- [x] 输出目录路径正确: outputs/
- [x] 当前年份自动计算: 2026
```

**Step 8: 生成并保存报告**
```markdown
### Step 8: 报告生成 ✅
- [x] JSON文件已生成: RevGrowth_[公司名].json
- [x] Markdown完整报告已生成: RevGrowth_FullReport_[公司名].md
- [x] 报告语言为中文(英文比例<30%)
- [x] 报告包含所有必需章节
```

**Step 8.5: 报告验证 (v2.3.1新增，当前v2.5.0)**
```markdown
### Step 8.5: 报告验证 ✅
- [x] 执行validate_report.py验证脚本
- [x] 语言检测通过(英文比例<30%)
- [x] 文件完整性检查通过(JSON + Markdown)
- [x] JSON格式验证通过(包含必需字段)
- [x] Markdown章节验证通过(所有必需章节存在)
- [x] 文件大小检查通过(JSON>2KB, Markdown>10KB)
```

### 2.3 问题记录表示例

| 步骤 | 问题描述 | 解决方案 | 解决状态 |
|------|----------|----------|----------|
| Step 2 | 公司类型检测置信度低(0.45) | 手动指定公司类型为"产品驱动型" | ✅ 已解决 |
| Step 8 | Markdown报告只有420 bytes | 重新生成完整报告，确保包含所有章节 | ✅ 已解决 |
| Step 8.5 | JSON缺少parameter_tracing字段 | 在JSON生成代码中添加参数溯源字段 | ✅ 已解决 |

---

## 3. 完整流程示例

### 3.1 新公司分析完整流程

```bash
# 1. 启动Claude Code
# 2. 执行revenue-forecast技能
使用revenue-forecast skill分析阿里巴巴

# 3. 自动执行10步流程:
#   Step 0: 加载配置
#   Step 1: 初始化缓存系统
#   Step 2: 判断公司类型(产品驱动型)
#   Step 3: 判断语言策略(中英双语)
#   Step 4: 执行9维度研究
#   Step 5: 执行产品驱动型专项分析
#   Step 6: 情景预测与加权计算
#   Step 7: 综合评分(基于CAGR查表)
#   Step 8: 生成并保存报告
#   Step 8.5: 报告验证(强制执行)
#   Step 9: 更新缓存

# 4. 输出文件:
#   outputs/RevGrowth_阿里巴巴.json
#   outputs/RevGrowth_FullReport_阿里巴巴.md
#   revenue-forecast-cache/阿里巴巴/metadata.json
```

### 3.2 验证失败处理流程

```bash
# 1. 执行分析
使用revenue-forecast skill分析测试公司

# 2. Step 8.5验证失败
❌ 验证失败! 禁止进入第九步

# 3. 查看验证错误
python validate_report.py 测试公司 "C:\Users\郑曾波\Projects\Research\outputs"

# 4. 修正问题
#   - 确保报告语言为中文
#   - 确保生成完整Markdown报告
#   - 添加parameter_tracing字段

# 5. 重新验证
python validate_report.py 测试公司 "C:\Users\郑曾波\Projects\Research\outputs"

# 6. 验证通过后继续
✅ 所有检查通过! 报告符合v2.5.0框架要求
```

---

## 4. 常见问题与解决方案

### Q1: 验证脚本报告"文件不存在"错误
**A**: 检查输出目录路径是否正确:
```bash
# 错误路径
python validate_report.py 阿里巴巴 "outputs"  # 相对路径可能不对

# 正确路径(使用绝对路径)
python validate_report.py 阿里巴巴 "C:\Users\郑曾波\Projects\Research\outputs"
```

### Q2: 检查清单中的某个步骤总是失败
**A**: 查看问题记录表，记录具体问题:
1. 在checklist.md的问题记录表中添加问题描述
2. 分析根本原因
3. 实施解决方案
4. 更新解决状态

### Q3: 报告语言检测失败，但报告确实是中文
**A**: 可能包含大量英文术语或代码片段:
1. 减少英文术语使用
2. 将代码片段移至附录
3. 确保正文部分中文比例>70%

### Q4: 如何跳过验证(不推荐)
**A**: v2.5.0框架禁止跳过验证，但紧急情况下:
```bash
# 不推荐! 仅用于调试
python validate_report.py 公司名 路径 --force-continue
```

---

## 5. 最佳实践

### 5.1 报告生成最佳实践
- ✅ **语言**: 使用中文撰写报告，英文术语比例<30%
- ✅ **完整性**: 确保生成JSON和Markdown两个文件
- ✅ **章节**: 包含所有6个必需章节
- ✅ **参数溯源**: JSON中必须包含parameter_tracing字段
- ✅ **文件大小**: JSON>2KB, Markdown>10KB

### 5.2 检查清单使用最佳实践
- ✅ **逐步检查**: 每个步骤完成后立即检查对应项
- ✅ **问题记录**: 发现问题时立即记录到问题记录表
- ✅ **版本对应**: 使用与框架版本对应的检查清单版本
- ✅ **强制使用**: 严格执行检查清单，不得跳过任何检查项

### 5.3 验证脚本最佳实践
- ✅ **预验证**: 生成报告后立即运行验证脚本
- ✅ **详细模式**: 使用--verbose参数查看详细验证信息
- ✅ **错误处理**: 根据验证错误信息精确修正问题
- ✅ **强制阻断**: 尊重验证失败阻断机制，不强行绕过

---

**文档版本**: v1.1
**最后更新**: 2026-03-01
**对应框架版本**: v2.5.0
**维护者**: Revenue Forecast System