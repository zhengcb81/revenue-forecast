#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revenue-forecast 报告验证脚本

用途：验证生成的分析报告是否符合框架要求
版本：v1.0
创建日期：2026-01-15
"""

import os
import sys
import json
import re
from pathlib import Path

# 设置Windows控制台UTF-8编码
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class ReportValidator:
    """报告验证器"""

    def __init__(self, company_name, output_dir="outputs"):
        self.company_name = company_name
        self.output_dir = output_dir
        self.json_file = os.path.join(output_dir, f"RevGrowth_{company_name}.json")
        self.md_file = os.path.join(
            output_dir, f"RevGrowth_FullReport_{company_name}.md"
        )
        self.errors = []
        self.warnings = []

    def detect_english_ratio(self, text):
        """检测文本中英文比例

        Args:
            text: 待检测文本

        Returns:
            float: 英文字符占所有字母字符的比例 (0-1)
        """
        if not text:
            return 0.0

        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total_chars = sum(1 for c in text if c.isalpha())

        if total_chars == 0:
            return 0.0

        return english_chars / total_chars

    def validate_json_file(self):
        """验证JSON文件"""
        print(f"\n检查JSON文件: {self.json_file}")

        # 检查1: 文件是否存在
        if not os.path.exists(self.json_file):
            self.errors.append(f"❌ JSON报告文件不存在: {self.json_file}")
            return False

        print(f"✅ JSON文件存在")

        # 检查2: 文件大小
        file_size = os.path.getsize(self.json_file)
        if file_size < 2048:  # 至少2KB
            self.errors.append(f"❌ JSON文件过小: {file_size} bytes (至少需要2KB)")
            return False

        print(f"✅ JSON文件大小: {file_size} bytes")

        # 检查3: JSON格式
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ JSON格式错误: {str(e)}")
            return False

        print(f"✅ JSON格式正确")

        # 检查4: 必需字段
        required_fields = ["company_name", "score", "key_metrics", "scenario_analysis"]

        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            self.errors.append(f"❌ JSON缺少必需字段: {', '.join(missing_fields)}")
            return False

        print(f"✅ JSON包含所有必需字段")

        # 检查5: 参数溯源信息 (v2.3.0新增)
        if "parameter_tracing" in data or "data_source" in str(data):
            print(f"✅ JSON包含参数溯源信息")
        else:
            self.warnings.append(f"⚠️ JSON未包含parameter_tracing字段")

        return True

    def validate_markdown_file(self):
        """验证Markdown文件"""
        print(f"\n检查Markdown文件: {self.md_file}")

        # 检查1: 文件是否存在
        if not os.path.exists(self.md_file):
            self.errors.append(f"❌ Markdown报告文件不存在: {self.md_file}")
            return False

        print(f"✅ Markdown文件存在")

        # 检查2: 文件大小
        file_size = os.path.getsize(self.md_file)
        if file_size < 10240:  # 至少10KB
            self.warnings.append(
                f"⚠️ Markdown文件较小: {file_size} bytes (建议至少10KB)"
            )

        print(f"✅ Markdown文件大小: {file_size} bytes")

        # 检查3: 读取内容
        try:
            with open(self.md_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"❌ 无法读取Markdown文件: {str(e)}")
            return False

        # 检查4: 语言检测（核心要求！）
        english_ratio = self.detect_english_ratio(content)
        print(f"📊 英文比例: {english_ratio * 100:.1f}%")

        if english_ratio > 0.3:  # 超过30%英文视为违规
            self.errors.append(
                f"❌ 报告语言违规: 英文比例 {english_ratio * 100:.1f}% > 30% (框架强制要求中文)"
            )
            return False

        print(f"✅ 报告语言符合要求（中文为主）")

        # 检查5: 必需章节
        required_sections = [
            "执行摘要",
            "关键财务指标",
            "双曲线业务分析",
            "情景分析",
            "投资建议",
            "参数溯源",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            self.errors.append(
                f"❌ Markdown缺少必需章节: {', '.join(missing_sections)}"
            )
            return False

        print(f"✅ Markdown包含所有必需章节")

        # 检查6: 核心关键词（中文）
        chinese_keywords = ["亿元", "公司类型", "CAGR", "营收"]
        found_keywords = [kw for kw in chinese_keywords if kw in content]
        print(f"✅ 发现核心关键词: {', '.join(found_keywords)}")

        return True

    def run_validation(self):
        """运行完整验证"""
        print(f"\n{'=' * 70}")
        print(f"revenue-forecast 报告验证")
        print(f"{'=' * 70}")
        print(f"公司名称: {self.company_name}")
        print(f"输出目录: {self.output_dir}")
        print(f"{'=' * 70}")

        # 验证JSON
        json_ok = self.validate_json_file()

        # 验证Markdown
        md_ok = self.validate_markdown_file()

        # 输出结果
        print(f"\n{'=' * 70}")
        print(f"验证结果总结")
        print(f"{'=' * 70}")

        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}项):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}项):")
            for error in self.errors:
                print(f"  {error}")
            print(f"\n{'=' * 70}")
            print(f"❌ 验证失败！")
            print(f"{'=' * 70}")
            print(f"\n必须修正上述错误后才能继续Step 10（更新缓存）")
            return False
        else:
            print(f"\n✅ 所有检查通过！")
            print(f"{'=' * 70}")
            print(f"\n✅ 报告符合revenue-forecast v2.5.0框架要求")
            print(f"✅ 可以继续Step 10: 更新缓存")
            return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_report.py <公司名称> [输出目录]")
        print("示例: python validate_report.py 阿里巴巴")
        sys.exit(1)

    company_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs"

    validator = ReportValidator(company_name, output_dir)
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
