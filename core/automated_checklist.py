"""
Revenue Forecast - 自动化检查清单 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 解析 checklist.md
2. 自动执行可验证的检查项
3. 生成检查报告
4. 集成到强制执行系统
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
import os
import sys
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checkpoint_registry import CheckpointRegistry, CheckpointConfig, CheckpointType, CheckpointResult, ValidationContext


@dataclass
class CheckItem:
    """检查项"""
    id: str
    description: str
    step_id: str
    check_type: str  # file_exists, content_contains, field_not_empty, etc.
    params: Dict[str, Any] = field(default_factory=dict)
    is_manual: bool = False  # 是否需要人工检查
    auto_executable: bool = True  # 是否可以自动执行


@dataclass
class CheckResult:
    """检查结果"""
    item_id: str
    description: str
    passed: bool
    message: str = ""
    details: Dict = field(default_factory=dict)


class AutomatedChecklist:
    """
    自动化检查清单
    
    从 checklist.md 解析检查项并自动执行
    """
    
    def __init__(self, skill_dir: Optional[str] = None):
        """
        初始化自动化检查清单
        
        Args:
            skill_dir: skill目录路径
        """
        if skill_dir is None:
            self.skill_dir = Path(__file__).parent.parent
        else:
            self.skill_dir = Path(skill_dir)
        
        self.checklist_file = self.skill_dir / "checklist.md"
        self.check_items: List[CheckItem] = []
        self._auto_check_functions: Dict[str, Callable] = {}
        
        # 注册自动检查函数
        self._register_auto_checks()
        
        # 加载检查项
        self._load_checklist()
    
    def _register_auto_checks(self):
        """注册自动检查函数"""
        self._auto_check_functions = {
            "file_exists": self._check_file_exists,
            "content_contains": self._check_content_contains,
            "field_not_empty": self._check_field_not_empty,
            "json_field_exists": self._check_json_field_exists,
            "md_section_exists": self._check_md_section_exists,
            "token_usage": self._check_token_usage,
            "tool_calls": self._check_tool_calls,
            "dimension_files": self._check_dimension_files
        }
    
    def _load_checklist(self):
        """从 checklist.md 加载检查项"""
        if not self.checklist_file.exists():
            print(f"[AutomatedChecklist] 警告: checklist.md 不存在")
            return
        
        try:
            with open(self.checklist_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_checklist(content)
            print(f"[AutomatedChecklist] 加载了 {len(self.check_items)} 个检查项")
            
        except Exception as e:
            print(f"[AutomatedChecklist] 加载失败: {e}")
    
    def _parse_checklist(self, content: str):
        """解析检查清单内容"""
        # 解析步骤章节
        step_pattern = r'## 第(\d+)步[：:](.+?)\n'
        steps = re.findall(step_pattern, content)
        
        for step_num, step_name in steps:
            step_id = f"step{step_num}"
            
            # 提取该步骤的检查项（简化解析）
            # 查找该步骤下的复选框
            step_section = self._extract_section(content, f"## 第{step_num}步")
            if step_section:
                # 查找检查项（以- [ ]或- [x]开头）
                items = re.findall(r'- \[([ x])\] \*\*(.+?)\*\*[：:]?\s*(.+?)(?=\n|$)', step_section)
                
                for checked, item_id, item_desc in items:
                    check_item = CheckItem(
                        id=f"{step_id}_{item_id}",
                        description=item_desc.strip(),
                        step_id=step_id,
                        check_type=self._infer_check_type(item_desc),
                        is_manual=False
                    )
                    self.check_items.append(check_item)
    
    def _extract_section(self, content: str, section_header: str) -> str:
        """提取章节内容"""
        pattern = re.escape(section_header) + r'(.+?)(?=## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        return ""
    
    def _infer_check_type(self, description: str) -> str:
        """推断检查类型"""
        desc_lower = description.lower()
        
        if "文件" in desc_lower or "file" in desc_lower:
            return "file_exists"
        elif "token" in desc_lower or "消耗" in desc_lower:
            return "token_usage"
        elif "工具" in desc_lower or "调用" in desc_lower:
            return "tool_calls"
        elif "维度" in desc_lower or "dimension" in desc_lower:
            return "dimension_files"
        elif "json" in desc_lower:
            return "json_field_exists"
        elif "markdown" in desc_lower or "章节" in desc_lower:
            return "md_section_exists"
        elif "字段" in desc_lower or "field" in desc_lower:
            return "field_not_empty"
        elif "内容" in desc_lower or "content" in desc_lower:
            return "content_contains"
        else:
            return "manual"  # 默认为手动检查
    
    def execute_checks_for_step(self, step_id: str, context: ValidationContext) -> CheckpointResult:
        """
        执行指定步骤的所有自动检查
        
        Args:
            step_id: 步骤ID
            context: 验证上下文
            
        Returns:
            CheckpointResult: 检查结果
        """
        # 获取该步骤的检查项
        step_items = [item for item in self.check_items if item.step_id == step_id and item.auto_executable]
        
        if not step_items:
            return CheckpointResult(
                checkpoint_id=f"{step_id}_checklist",
                passed=True,
                message=f"步骤 {step_id} 没有可自动执行的检查项"
            )
        
        results = []
        all_passed = True
        
        for item in step_items:
            check_func = self._auto_check_functions.get(item.check_type)
            
            if check_func:
                try:
                    check_result = check_func(item, context)
                    results.append(check_result)
                    if not check_result.passed:
                        all_passed = False
                except Exception as e:
                    results.append(CheckResult(
                        item_id=item.id,
                        description=item.description,
                        passed=False,
                        message=f"检查执行异常: {str(e)}"
                    ))
                    all_passed = False
            else:
                # 无法自动执行的标记为手动
                results.append(CheckResult(
                    item_id=item.id,
                    description=item.description,
                    passed=True,
                    message="需要手动检查"
                ))
        
        # 生成结果
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        
        errors = [r.message for r in results if not r.passed and r.message]
        
        return CheckpointResult(
            checkpoint_id=f"{step_id}_checklist",
            passed=all_passed,
            score=(passed_count / total_count * 100) if total_count > 0 else 100,
            message=f"检查清单: {passed_count}/{total_count}项通过",
            details={
                "step_id": step_id,
                "total_checks": total_count,
                "passed_checks": passed_count,
                "results": [
                    {
                        "id": r.item_id,
                        "description": r.description,
                        "passed": r.passed,
                        "message": r.message
                    }
                    for r in results
                ]
            },
            errors=errors
        )
    
    def register_to_checkpoint_registry(self, registry: CheckpointRegistry):
        """将检查清单注册到检查点注册中心"""
        for item in self.check_items:
            if not item.auto_executable:
                continue
            
            config = CheckpointConfig(
                id=item.id,
                name=item.description,
                type=CheckpointType.BLOCKING if not item.is_manual else CheckpointType.WARNING,
                enabled=True
            )
            registry.register(config)
    
    # ========== 自动检查函数 ==========
    
    def _check_file_exists(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查文件是否存在"""
        file_path = item.params.get("path", "")
        if not file_path:
            # 从描述中提取文件名
            match = re.search(r'(\S+\.\w+)', item.description)
            if match:
                file_path = match.group(1)
        
        # 构建完整路径
        if not os.path.isabs(file_path):
            company_cache = os.path.join(
                context.metadata.get("cache_dir", ""),
                context.company_name
            )
            full_path = os.path.join(company_cache, file_path)
        else:
            full_path = file_path
        
        exists = os.path.exists(full_path)
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=exists,
            message=f"文件存在: {file_path}" if exists else f"文件不存在: {file_path}"
        )
    
    def _check_content_contains(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查内容是否包含特定文本"""
        content = context.content
        keyword = item.params.get("keyword", "")
        
        if not keyword:
            # 从描述中提取关键词
            match = re.search(r'["\'](.+?)["\']', item.description)
            if match:
                keyword = match.group(1)
        
        contains = keyword in content if keyword else False
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=contains,
            message=f"包含'{keyword}'" if contains else f"不包含'{keyword}'"
        )
    
    def _check_field_not_empty(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查字段不为空"""
        field_name = item.params.get("field", "")
        value = context.metadata.get(field_name)
        
        is_not_empty = value is not None and str(value).strip() != ""
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=is_not_empty,
            message=f"字段 {field_name} 有值" if is_not_empty else f"字段 {field_name} 为空"
        )
    
    def _check_json_field_exists(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查JSON字段存在"""
        # 需要从上下文中获取JSON数据
        json_data = context.metadata.get("json_data", {})
        field_path = item.params.get("field", "")
        
        # 支持嵌套路径如 "scenario_analysis.base.cagr"
        value = json_data
        for key in field_path.split("."):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                value = None
                break
        
        exists = value is not None
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=exists,
            message=f"JSON字段 {field_path} 存在" if exists else f"JSON字段 {field_path} 不存在"
        )
    
    def _check_md_section_exists(self, item: CheckItem, context: CheckResult) -> CheckResult:
        """检查Markdown章节存在"""
        content = context.content
        section = item.params.get("section", "")
        
        if not section:
            # 从描述中提取章节名
            match = re.search(r'["\'](.+?)["\']', item.description)
            if match:
                section = match.group(1)
        
        # 检查是否作为标题存在
        pattern = rf'^#+\s*{re.escape(section)}'
        exists = bool(re.search(pattern, content, re.MULTILINE))
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=exists,
            message=f"章节 '{section}' 存在" if exists else f"章节 '{section}' 不存在"
        )
    
    def _check_token_usage(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查Token使用"""
        token_usage = context.token_usage
        min_tokens = item.params.get("min", 8000)
        
        passed = token_usage >= min_tokens
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=passed,
            message=f"Token使用: {token_usage} (要求: >= {min_tokens})"
        )
    
    def _check_tool_calls(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查工具调用"""
        tool_calls = context.tool_calls
        min_calls = item.params.get("min", 18)
        
        passed = len(tool_calls) >= min_calls
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=passed,
            message=f"工具调用: {len(tool_calls)}次 (要求: >= {min_calls})"
        )
    
    def _check_dimension_files(self, item: CheckItem, context: ValidationContext) -> CheckResult:
        """检查维度文件"""
        cache_dir = context.metadata.get("cache_dir", "")
        company_name = context.company_name
        
        import glob
        company_cache = os.path.join(cache_dir, company_name)
        dim_files = glob.glob(os.path.join(company_cache, "dimension-*.md"))
        
        min_files = item.params.get("min", 9)
        passed = len(dim_files) >= min_files
        
        return CheckResult(
            item_id=item.id,
            description=item.description,
            passed=passed,
            message=f"维度文件: {len(dim_files)}个 (要求: >= {min_files})"
        )
    
    def generate_report(self) -> str:
        """生成检查清单自动化报告"""
        total = len(self.check_items)
        auto_executable = sum(1 for item in self.check_items if item.auto_executable)
        manual = total - auto_executable
        
        report = f"""# 检查清单自动化报告

## 统计

- 总检查项: {total}
- 可自动执行: {auto_executable} ({auto_executable/total*100:.1f}%)
- 需人工检查: {manual} ({manual/total*100:.1f}%)

## 检查项列表

"""
        
        for item in self.check_items:
            status = "自动" if item.auto_executable else "手动"
            report += f"- [{status}] {item.id}: {item.description}\n"
        
        return report


# 便捷函数
def create_automated_checklist(skill_dir: Optional[str] = None) -> AutomatedChecklist:
    """创建自动化检查清单实例"""
    return AutomatedChecklist(skill_dir)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("AutomatedChecklist 测试")
    print("=" * 60)
    
    checklist = AutomatedChecklist()
    
    print(f"\n加载了 {len(checklist.check_items)} 个检查项")
    
    # 显示前5个
    print("\n前5个检查项:")
    for item in checklist.check_items[:5]:
        auto = "自动" if item.auto_executable else "手动"
        print(f"  [{auto}] {item.id}: {item.description[:50]}...")
    
    # 生成报告
    print("\n生成统计报告...")
    report = checklist.generate_report()
    print(f"  报告长度: {len(report)} 字符")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
