"""
Checklist验证器 - 解析和验证checklist.md文件
版本: v1.0
创建日期: 2026-01-17

功能:
1. 解析checklist.md文件，提取每个步骤的检查项
2. 验证检查项是否标记为完成（- [x] 或 - [X]）
3. 为每个步骤生成验证结果
4. 与EnforcementController集成
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .enforcement_controller import StepValidationResult

class ChecklistItem:
    """检查清单项"""
    def __init__(self, text: str, is_checked: bool = False, indent_level: int = 0):
        self.text = text.strip()
        self.is_checked = is_checked
        self.indent_level = indent_level
        self.children: List['ChecklistItem'] = []

    def add_child(self, child: 'ChecklistItem'):
        self.children.append(child)

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "is_checked": self.is_checked,
            "indent_level": self.indent_level,
            "children": [child.to_dict() for child in self.children]
        }

class ChecklistStep:
    """检查清单步骤"""
    def __init__(self, step_id: str, name: str):
        self.step_id = step_id
        self.name = name
        self.items: List[ChecklistItem] = []

    def add_item(self, item: ChecklistItem):
        self.items.append(item)

    def get_completion_rate(self) -> Tuple[int, int]:
        """获取完成率（完成数/总数）"""
        total = 0
        completed = 0

        def count_items(item: ChecklistItem):
            nonlocal total, completed
            total += 1
            if item.is_checked:
                completed += 1
            for child in item.children:
                count_items(child)

        for item in self.items:
            count_items(item)

        return completed, total

    def validate(self) -> StepValidationResult:
        """验证步骤检查项"""
        completed, total = self.get_completion_rate()
        result = StepValidationResult(True)

        if total == 0:
            result.add_warning(f"步骤 {self.step_id} 没有检查项")
            return result

        completion_rate = completed / total * 100

        if completion_rate < 100:
            result.add_error(f"步骤 {self.step_id} 检查项未完全完成: {completed}/{total} ({completion_rate:.1f}%)")

        # 检查是否有未完成的关键项（顶级项）
        for item in self.items:
            if not item.is_checked and item.indent_level == 0:
                result.add_warning(f"未完成关键检查项: {item.text}")

        return result

    def to_dict(self) -> Dict:
        completed, total = self.get_completion_rate()
        return {
            "step_id": self.step_id,
            "name": self.name,
            "item_count": total,
            "completed_count": completed,
            "completion_rate": completed / total * 100 if total > 0 else 0,
            "items": [item.to_dict() for item in self.items]
        }

class ChecklistValidator:
    """检查清单验证器"""

    # 步骤ID映射（checklist标题到步骤ID）
    STEP_MAPPING = {
        "第0步: 加载配置": "step0",
        "第1步: 初始化缓存系统": "step1",
        "第2步: 判断公司类型": "step2",
        "第3步: 语言策略判断": "step3",
        "第4步: 执行9维度研究": "step4",
        "第4.5步: 品牌矩阵分析": "step4_5",
        "第5步: 执行公司类型专项分析": "step5",
        "第6步: 情景预测与加权计算": "step6",
        "第7步: 综合CAGR计算": "step7",
        "第8步: 综合评分": "step8",
        "第9步: 生成并保存报告": "step9",
        "第9.5步: 报告验证": "step9_5",
        "第10步: 更新缓存": "step10"
    }

    def __init__(self, checklist_path: str):
        self.checklist_path = Path(checklist_path)
        self.steps: Dict[str, ChecklistStep] = {}
        self._parse_checklist()

    def _parse_checklist(self):
        """解析checklist.md文件"""
        if not self.checklist_path.exists():
            raise FileNotFoundError(f"检查清单文件不存在: {self.checklist_path}")

        with open(self.checklist_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_step: Optional[ChecklistStep] = None
        current_items_stack: List[ChecklistItem] = []

        for line in lines:
            line = line.rstrip()

            # 检查是否为步骤标题 (如 "## 第0步: 加载配置")
            step_match = re.match(r'^##\s+(第[\d.]+步:.*)$', line)
            if step_match:
                step_title = step_match.group(1)
                step_id = self.STEP_MAPPING.get(step_title)
                if step_id:
                    current_step = ChecklistStep(step_id, step_title)
                    self.steps[step_id] = current_step
                    current_items_stack = []
                else:
                    current_step = None
                continue

            # 检查是否为检查项 (如 "- [ ] 配置模块读取" 或 "- [x] 配置模块读取")
            item_match = re.match(r'^(\s*)[-*]\s+\[(.)\]\s+(.+)$', line)
            if item_match and current_step:
                indent = len(item_match.group(1))
                check_mark = item_match.group(2).lower()
                item_text = item_match.group(3)

                is_checked = check_mark == 'x'
                indent_level = indent // 2  # 假设2空格缩进

                item = ChecklistItem(item_text, is_checked, indent_level)

                # 处理嵌套层次
                while current_items_stack and current_items_stack[-1].indent_level >= indent_level:
                    current_items_stack.pop()

                if current_items_stack:
                    current_items_stack[-1].add_child(item)
                else:
                    current_step.add_item(item)

                current_items_stack.append(item)
                continue

            # 检查是否为子项描述（不以复选框开头）
            if line.strip() and current_step and current_items_stack:
                # 可能是检查项的描述文本
                last_item = current_items_stack[-1]
                if not line.strip().startswith('-') and not line.strip().startswith('*'):
                    last_item.text += " " + line.strip()

    def validate_step(self, step_id: str) -> StepValidationResult:
        """验证特定步骤"""
        if step_id not in self.steps:
            return StepValidationResult(False, errors=[f"步骤 {step_id} 在检查清单中未找到"])

        step = self.steps[step_id]
        return step.validate()

    def validate_all_steps(self) -> Dict[str, StepValidationResult]:
        """验证所有步骤"""
        results = {}
        for step_id, step in self.steps.items():
            results[step_id] = step.validate()
        return results

    def get_step_completion_rate(self, step_id: str) -> Tuple[int, int, float]:
        """获取步骤完成率"""
        if step_id not in self.steps:
            return 0, 0, 0.0

        step = self.steps[step_id]
        completed, total = step.get_completion_rate()
        rate = completed / total * 100 if total > 0 else 0.0
        return completed, total, rate

    def print_summary(self):
        """打印检查清单摘要"""
        print("=" * 70)
        print("检查清单验证摘要")
        print("=" * 70)

        if not self.steps:
            print("❌ 未找到任何步骤")
            return

        total_items = 0
        total_completed = 0

        for step_id, step in self.steps.items():
            completed, total = step.get_completion_rate()
            rate = completed / total * 100 if total > 0 else 0.0
            total_items += total
            total_completed += completed

            status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
            print(f"{status} {step.name}: {completed}/{total} ({rate:.1f}%)")

        overall_rate = total_completed / total_items * 100 if total_items > 0 else 0.0
        print("-" * 70)
        print(f"总计: {total_completed}/{total_items} ({overall_rate:.1f}%)")
        print("=" * 70)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "checklist_path": str(self.checklist_path),
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()}
        }


# ============ 与EnforcementController集成 ============

def create_checklist_validator_for_step(checklist_path: str, step_id: str) -> callable:
    """为特定步骤创建验证函数"""
    def validator() -> StepValidationResult:
        try:
            validator = ChecklistValidator(checklist_path)
            return validator.validate_step(step_id)
        except Exception as e:
            return StepValidationResult(False, errors=[f"检查清单验证失败: {str(e)}"])

    return validator


# ============ 使用示例 ============

if __name__ == "__main__":
    """使用示例"""
    # 假设checklist.md在技能根目录
    checklist_path = Path(__file__).parent.parent / "checklist.md"

    if not checklist_path.exists():
        print(f"测试: 创建示例checklist.md")
        # 创建示例checklist用于测试
        sample_checklist = """# Revenue-Forecast Skill 执行检查清单 v1.0

## 第0步: 加载配置

- [x] 配置模块读取
  - [x] 已读取 `core/config.yaml`
  - [x] 已读取 `core/config.py`
- [x] 配置验证函数调用
- [x] 配置摘要验证

## 第1步: 初始化缓存系统

- [x] 缓存目录创建
- [ ] metadata.json 创建/更新
- [x] search-results 子目录
"""
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(sample_checklist)

    try:
        validator = ChecklistValidator(str(checklist_path))
        validator.print_summary()

        # 测试特定步骤
        print("\n详细验证结果:")
        for step_id in ["step0", "step1"]:
            result = validator.validate_step(step_id)
            print(f"{step_id}: {'通过' if result else '失败'}")
            if result.errors:
                print(f"  错误: {result.errors}")
            if result.warnings:
                print(f"  警告: {result.warnings}")

    finally:
        # 清理测试文件
        if "sample_checklist" in locals():
            checklist_path.unlink()