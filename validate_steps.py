#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revenue-forecast 步骤完整性验证脚本

用途：验证9个维度分析文件和报告文件的完整性
版本：v1.1 (v2.6.0)
创建日期：2026-01-23
对应框架版本：v2.6.0
"""

import os
import sys
import json
import re
from pathlib import Path

# 设置Windows控制台UTF-8编码（v2.6.0 统一编码引导）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.encoding import setup_utf8_console
setup_utf8_console()


class StepsValidator:
    """步骤完整性验证器"""

    # 9个标准维度文件
    STANDARD_DIMENSIONS = [
        "双曲线业务分析",
        "宏观环境分析",
        "产业变革分析",
        "业务板块分析",
        "竞争力评估",
        "产能与运营分析",
        "市场拓展潜力",
        "定价能力与盈利分析",
        "技术创新与突破"
    ]

    def __init__(self, company_name, project_root):
        """
        初始化验证器

        Args:
            company_name: 公司名称
            project_root: 项目根目录绝对路径
        """
        self.company_name = company_name
        self.project_root = project_root
        self.cache_dir = os.path.join(project_root, "revenue-forecast-cache", company_name)
        self.output_dir = os.path.join(project_root, "outputs")
        self.errors = []
        self.warnings = []
        self.company_type = None

    def sanitize_company_name(self, name):
        """
        清理公司名称，生成文件系统安全的目录名

        Args:
            name: 原始公司名称

        Returns:
            safe_name: 安全的目录名称
        """
        # 移除非法字符
        safe_name = re.sub(r'[\\/:*?"<>|]', '', name)
        # 替换空格和特殊字符
        safe_name = re.sub(r'[\s\-]+', '_', safe_name)
        # 限制长度
        safe_name = safe_name[:50]
        # 移除首尾下划线
        safe_name = safe_name.strip('_')
        return safe_name

    def get_cache_dir(self):
        """获取公司缓存目录"""
        safe_name = self.sanitize_company_name(self.company_name)
        return os.path.join(self.project_root, "revenue-forecast-cache", safe_name)

    def validate_metadata(self):
        """验证metadata.json文件"""
        print(f"\n检查metadata.json")

        cache_dir = self.get_cache_dir()
        metadata_file = os.path.join(cache_dir, "metadata.json")

        # 检查文件是否存在
        if not os.path.exists(metadata_file):
            self.errors.append(f"❌ metadata.json不存在: {metadata_file}")
            return False

        print(f"✅ metadata.json存在")

        # 读取metadata获取公司类型
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                self.company_type = metadata.get('company_type', None)
                print(f"✅ 公司类型: {self.company_type}")
        except Exception as e:
            self.warnings.append(f"⚠️ 无法读取metadata.json: {str(e)}")

        return True

    def validate_dimension_files(self):
        """验证维度分析文件"""
        print(f"\n检查维度分析文件")

        cache_dir = self.get_cache_dir()

        # 检查缓存目录是否存在
        if not os.path.exists(cache_dir):
            self.warnings.append(f"⚠️ 缓存目录不存在: {cache_dir}")
            self.warnings.append(f"   维度文件检查跳过(这是正常的,如果仅生成了报告)")
            return True  # 不算错误,因为可能只生成了报告

        # 检查9个标准维度
        missing_files = []
        existing_files = []

        for dimension in self.STANDARD_DIMENSIONS:
            dimension_file = os.path.join(cache_dir, f"{dimension}.md")
            if os.path.exists(dimension_file):
                existing_files.append(dimension)
            else:
                missing_files.append(dimension)

        print(f"✅ 标准维度文件: {len(existing_files)}/{len(self.STANDARD_DIMENSIONS)} 完整")

        if missing_files:
            self.warnings.append(f"⚠️ 缺失维度文件: {len(missing_files)}个")
            self.warnings.append(f"   (维度文件缺失不影响报告验证,建议补充)")

        # 检查公司类型专项文件
        if self.company_type == "product-driven":
            brand_matrix_file = os.path.join(cache_dir, "品牌矩阵分析.md")
            if os.path.exists(brand_matrix_file):
                print(f"✅ 品牌矩阵分析文件存在")
            else:
                self.warnings.append(f"⚠️ 产品驱动型公司缺失品牌矩阵分析文件")

        return True

    def validate_search_results(self):
        """验证第4步搜索结果原文保存（v2.6.0 强制）

        对应 skill.md 第4步第5子步、modules/parameter-tracing/evidence-chain-spec.md 第七节。
        """
        print(f"\n检查第4步搜索结果原文（v2.6.0）")

        cache_dir = self.get_cache_dir()
        search_dir = os.path.join(cache_dir, "search-results")

        if not os.path.exists(search_dir):
            self.errors.append(
                f"❌ search-results 目录不存在: {search_dir}（第4步未执行搜索结果保存）"
            )
            return False

        # 收集所有 search-*.md 文件
        import glob
        pattern = os.path.join(search_dir, "search-*.md")
        search_files = glob.glob(pattern)

        # 检查1: 文件数量 ≥ 9（每维度至少1个）
        if len(search_files) < 9:
            self.errors.append(
                f"❌ search-results/search-*.md 文件数量不足: {len(search_files)} < 9（每维度至少1个）"
            )
        else:
            print(f"✅ 搜索结果文件数量: {len(search_files)} (≥ 9)")

        # 检查2: 每个文件至少包含1条 URL
        no_url_files = []
        for sf in search_files:
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'http://' not in content and 'https://' not in content:
                    no_url_files.append(os.path.basename(sf))
            except Exception:
                no_url_files.append(os.path.basename(sf))

        if no_url_files:
            self.errors.append(
                f"❌ 以下搜索结果文件无 URL: {', '.join(no_url_files[:5])}{'...' if len(no_url_files) > 5 else ''}"
            )
        else:
            print(f"✅ 所有搜索结果文件包含至少1条 URL")

        # 检查3: 抽样3个文件，检查是否包含原文 snippet
        import random
        sample_files = random.sample(search_files, min(3, len(search_files))) if search_files else []
        no_snippet_files = []
        for sf in sample_files:
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    content = f.read()
                # snippet 判定：包含"摘要"或"snippet"或长度>100字符的正文
                if '摘要' not in content and 'snippet' not in content.lower() and len(content) < 100:
                    no_snippet_files.append(os.path.basename(sf))
            except Exception:
                no_snippet_files.append(os.path.basename(sf))

        if no_snippet_files:
            self.warnings.append(
                f"⚠️ 抽样文件缺少原文 snippet: {', '.join(no_snippet_files)}"
            )
        else:
            print(f"✅ 抽样检查通过: 文件包含原文 snippet")

        return not any("search-results" in e or "文件数量不足" in e or "无 URL" in e
                       for e in self.errors)


    def validate_json_report(self):
        """验证JSON报告文件"""
        print(f"\n检查JSON报告文件")

        json_file = os.path.join(self.output_dir, f"RevGrowth_{self.company_name}.json")

        # 检查1: 文件是否存在
        if not os.path.exists(json_file):
            self.errors.append(f"❌ JSON报告文件不存在: {json_file}")
            return False

        print(f"✅ JSON报告存在")

        # 检查2: 文件大小
        file_size = os.path.getsize(json_file)
        if file_size < 2048:  # 至少2KB
            self.errors.append(f"❌ JSON文件过小: {file_size} bytes (至少需要2KB)")
            return False

        print(f"✅ JSON文件大小: {file_size} bytes")

        # 检查3: JSON格式
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ JSON格式错误: {str(e)}")
            return False

        print(f"✅ JSON格式正确")

        # 检查4: 必需字段
        required_fields = [
            "company_name",
            "score",
            "key_metrics",
            "scenario_analysis"
        ]

        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            self.errors.append(f"❌ JSON缺少必需字段: {', '.join(missing_fields)}")
            return False

        print(f"✅ JSON包含所有必需字段")

        # 检查5: CAGR一致性
        score_cagr = data.get("score", {}).get("cagr")
        if score_cagr:
            print(f"✅ CAGR一致性检查通过: {score_cagr}%")
        else:
            self.warnings.append(f"⚠️ JSON中未找到CAGR数据")

        return True

    def validate_markdown_report(self):
        """验证Markdown报告文件"""
        print(f"\n检查Markdown报告文件")

        md_file = os.path.join(self.output_dir, f"RevGrowth_FullReport_{self.company_name}.md")

        # 检查1: 文件是否存在
        if not os.path.exists(md_file):
            self.errors.append(f"❌ Markdown报告文件不存在: {md_file}")
            return False

        print(f"✅ Markdown报告存在")

        # 检查2: 文件大小
        file_size = os.path.getsize(md_file)
        if file_size < 10240:  # 至少10KB
            self.warnings.append(f"⚠️ Markdown文件较小: {file_size} bytes (建议至少10KB)")

        print(f"✅ Markdown文件大小: {file_size} bytes")

        return True

    def validate_analysis_results(self):
        """验证metadata中的分析结果"""
        print(f"\n检查分析结果")

        cache_dir = self.get_cache_dir()
        metadata_file = os.path.join(cache_dir, "metadata.json")

        if not os.path.exists(metadata_file):
            self.warnings.append(f"⚠️ metadata.json不存在,跳过分析结果验证")
            return True

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 检查analysis_results字段
            if "analysis_results" in metadata:
                results = metadata["analysis_results"]
                print(f"✅ 分析结果已记录:")
                print(f"   - 评分: {results.get('score', 'N/A')}")
                print(f"   - CAGR: {results.get('cagr', 'N/A')}%")
                print(f"   - 评级: {results.get('rating', 'N/A')}")
            else:
                self.warnings.append(f"⚠️ metadata中未找到analysis_results字段")

        except Exception as e:
            self.warnings.append(f"⚠️ 无法读取分析结果: {str(e)}")

        return True

    def run_validation(self):
        """运行完整验证流程"""
        print(f"\n{'='*70}")
        print(f"步骤完整性验证")
        print(f"{'='*70}")
        print(f"公司名称: {self.company_name}")
        print(f"项目根目录: {self.project_root}")
        print(f"{'='*70}")

        # 执行所有验证
        metadata_ok = self.validate_metadata()
        dimensions_ok = self.validate_dimension_files()
        search_ok = self.validate_search_results()  # v2.6.0 新增
        json_ok = self.validate_json_report()
        md_ok = self.validate_markdown_report()
        results_ok = self.validate_analysis_results()

        # 输出验证结果
        print(f"\n{'='*70}")
        print(f"验证结果总结")
        print(f"{'='*70}")

        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}项):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}项):")
            for error in self.errors:
                print(f"  {error}")
            print(f"\n{'='*70}")
            print(f"❌ 步骤完整性验证失败")
            print(f"{'='*70}")
            print(f"\n必须修正上述错误后才能继续Step 11（更新缓存）")
            return False
        else:
            print(f"\n✅ 所有检查通过！")
            print(f"{'='*70}")
            print(f"\n✅ 步骤完整性验证通过")
            print(f"✅ 可以继续Step 11: 更新缓存")
            return True


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python validate_steps.py <公司名称> <项目根目录绝对路径>")
        print("示例: python validate_steps.py 惠泰医疗 \"C:\\Users\\郑曾波\\Projects\\Research\"")
        sys.exit(1)

    company_name = sys.argv[1]
    project_root = sys.argv[2]

    validator = StepsValidator(company_name, project_root)
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
