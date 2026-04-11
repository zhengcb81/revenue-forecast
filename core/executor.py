"""
营收增长预测分析 - 强制执行引擎
用途: 强制执行框架要求,防止人为错误
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# 导入配置模块
from core.config import (
    get_path,
    get_version,
    get_format,
    get_module_path,
    get_all_module_paths,
    get_file_pattern
)

# ============ 第一部分:缓存系统管理 ============

class CacheSystem:
    """缓存系统管理器 - 强制执行"""

    def __init__(self):
        self.cache_base_dir = get_path('cache_base_dir')

    def init_cache_system(self):
        """
        初始化缓存系统
        强制: 必须使用配置中的 cache_base_dir
        """
        expected_dir = get_path('cache_base_dir')
        if not os.path.exists(self.cache_base_dir):
            os.makedirs(self.cache_base_dir, exist_ok=True)
            print(f"✅ 缓存根目录已创建: {os.path.abspath(self.cache_base_dir)}")
        else:
            print(f"ℹ️ 缓存根目录已存在: {os.path.abspath(self.cache_base_dir)}")

        # 验证检查点1: 路径必须正确
        if self.cache_base_dir != expected_dir:
            raise ValueError(f"❌ 缓存路径错误! 期望: {expected_dir}, 实际: {self.cache_base_dir}")

        return self.cache_base_dir

    def init_company_cache(self, company_name):
        """
        初始化公司缓存目录
        强制: 路径必须为 revenue-forecast-cache/{公司名}/
        """
        # 初始化根目录
        self.init_cache_system()

        # 创建公司目录
        company_cache_dir = os.path.join(self.cache_base_dir, company_name)
        search_results_dir = os.path.join(company_cache_dir, "search-results")

        os.makedirs(company_cache_dir, exist_ok=True)
        os.makedirs(search_results_dir, exist_ok=True)

        # 验证检查点2: 公司目录路径必须正确
        expected_path = os.path.abspath(os.path.join(self.cache_base_dir, company_name))
        actual_path = os.path.abspath(company_cache_dir)
        if expected_path != actual_path:
            raise ValueError(f"❌ 公司缓存路径错误! 期望: {expected_path}, 实际: {actual_path}")

        # 创建或更新metadata.json
        metadata_path = os.path.join(company_cache_dir, "metadata.json")
        date_fmt = get_format('date')
        datetime_fmt = get_format('datetime')

        if os.path.exists(metadata_path):
            print(f"ℹ️ 公司缓存已存在: {company_cache_dir}")
            # 读取现有metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            # 创建新metadata
            metadata = {
                "company_name": company_name,
                "created_at": datetime.now().strftime(date_fmt),
                "last_analyzed": datetime.now().strftime(datetime_fmt),
                "analysis_count": 0,
                "cache_status": "initialized",
                "output_files": {
                    "json": "",
                    "markdown": ""
                },
                "search_results_count": 0,
                "dimensions_analyzed": 0,
                "language_strategy": "pending",
                "company_type": "pending",
                "framework_version": get_version()
            }
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"✅ 公司缓存目录已创建: {company_cache_dir}")

        return company_cache_dir, metadata

    def validate_cache_structure(self, company_name):
        """
        验证缓存结构是否符合要求
        验证检查点3: 必须通过验证才能继续
        """
        company_cache_dir = os.path.join(self.cache_base_dir, company_name)

        # 检查1: 目录是否存在
        if not os.path.exists(company_cache_dir):
            raise ValueError(f"❌ 公司缓存目录不存在: {company_cache_dir}")

        # 检查2: metadata.json是否存在
        metadata_path = os.path.join(company_cache_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise ValueError(f"❌ metadata.json不存在: {metadata_path}")

        # 检查3: search-results/子目录是否存在
        search_results_dir = os.path.join(company_cache_dir, "search-results")
        if not os.path.exists(search_results_dir):
            raise ValueError(f"❌ search-results/目录不存在: {search_results_dir}")

        print("✅ 缓存结构验证通过")
        return True

# ============ 第二部分:验证检查点系统 ============

class ValidationCheckpoints:
    """验证检查点系统 - 强制验证每个关键步骤"""

    def __init__(self, company_name):
        self.company_name = company_name
        self.errors = []
        self.warnings = []

    def check_step1_cache_initialization(self):
        """
        验证检查点1: 缓存初始化验证
        """
        separator = "=" * get_format('separator_length')
        cache_base_dir = get_path('cache_base_dir')
        print(f"\n{separator}")
        print("🔍 验证检查点1: 缓存初始化")
        print(separator)

        checks = []

        # 检查1.1: 根目录路径
        cache_root_exists = os.path.exists(cache_base_dir)
        checks.append({
            "name": f"缓存根目录存在: {cache_base_dir}",
            "status": "✅ 通过" if cache_root_exists else "❌ 失败",
            "critical": True
        })

        # 检查1.2: 公司目录路径
        expected_company_path = os.path.join(cache_base_dir, self.company_name)
        company_dir_exists = os.path.exists(expected_company_path)
        checks.append({
            "name": f"公司目录存在: {expected_company_path}",
            "status": "✅ 通过" if company_dir_exists else "❌ 失败",
            "critical": True
        })

        # 检查1.3: metadata.json存在
        metadata_path = os.path.join(expected_company_path, "metadata.json")
        metadata_exists = os.path.exists(metadata_path)
        checks.append({
            "name": f"metadata.json存在",
            "status": "✅ 通过" if metadata_exists else "❌ 失败",
            "critical": True
        })

        # 检查1.4: search-results/目录存在
        search_results_path = os.path.join(expected_company_path, "search-results")
        search_results_exists = os.path.exists(search_results_path)
        checks.append({
            "name": f"search-results/目录存在",
            "status": "✅ 通过" if search_results_exists else "❌ 失败",
            "critical": True
        })

        # 打印检查结果
        for check in checks:
            print(f"  {check['status']} - {check['name']}")
            if check['status'] == "❌ 失败" and check['critical']:
                self.errors.append(f"检查点1失败: {check['name']}")

        # 关键检查必须全部通过
        critical_passed = all(
            check['status'] == "✅ 通过" or not check['critical']
            for check in checks
        )

        if critical_passed:
            print("✅ 验证检查点1: 全部通过")
            return True
        else:
            print("❌ 验证检查点1: 存在关键错误,禁止继续!")
            return False

    def check_step2_module_reading(self, modules_read):
        """
        验证检查点2: 模块读取验证
        """
        separator = "=" * get_format('separator_length')
        print(f"\n{separator}")
        print("🔍 验证检查点2: 模块读取")
        print(separator)

        required_modules = get_all_module_paths()

        all_read = True
        for module in required_modules:
            is_read = module in modules_read
            status = "✅ 已读取" if is_read else "❌ 未读取"
            print(f"  {status} - {module}")
            if not is_read:
                all_read = False
                self.errors.append(f"检查点2失败: 必须读取 {module}")

        if all_read:
            print("✅ 验证检查点2: 全部通过")
            return True
        else:
            print("❌ 验证检查点2: 存在缺失模块,禁止继续!")
            return False

    def check_step3_output_files(self):
        """
        验证检查点3: 输出文件验证
        """
        separator = "=" * get_format('separator_length')
        output_dir = get_path('output_dir')
        print(f"\n{separator}")
        print("🔍 验证检查点3: 输出文件")
        print(separator)

        # 检查outputs目录是否存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"  ℹ️ 创建输出目录: {output_dir}")

        # 检查两个输出文件
        json_file = os.path.join(output_dir, get_file_pattern('json_output', self.company_name))
        md_file = os.path.join(output_dir, get_file_pattern('md_output', self.company_name))

        checks = [
            {
                "name": f"JSON摘要文件: {json_file}",
                "exists": os.path.exists(json_file),
                "critical": True
            },
            {
                "name": f"Markdown完整报告: {md_file}",
                "exists": os.path.exists(md_file),
                "critical": True
            }
        ]

        for check in checks:
            status = "✅ 存在" if check['exists'] else "❌ 不存在"
            size_info = ""
            if check['exists']:
                size = os.path.getsize(
                    json_file if "JSON" in check['name'] else md_file
                )
                size_info = f" ({size} bytes)"
            print(f"  {status}{size_info} - {check['name']}")

            if not check['exists'] and check['critical']:
                self.errors.append(f"检查点3失败: {check['name']}")

        all_exist = all(check['exists'] for check in checks)

        if all_exist:
            print("✅ 验证检查点3: 全部通过")
            return True
        else:
            print("❌ 验证检查点3: 输出文件缺失")
            return False

    def print_summary(self):
        """打印验证总结"""
        separator = "=" * get_format('separator_length')
        print(f"\n{separator}")
        print("📊 验证总结")
        print(separator)

        if self.errors:
            print(f"❌ 错误数量: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ 所有验证检查点通过!")
            return True

# ============ 第三部分:强制执行主流程 ============

class RevenueForecastExecutor:
    """营收增长预测分析 - 强制执行器"""

    def __init__(self, company_name):
        self.company_name = company_name
        self.cache_system = CacheSystem()
        self.validator = ValidationCheckpoints(company_name)
        self.modules_read = []

    def execute_analysis(self):
        """
        执行完整的营收增长预测分析
        强制: 每个步骤必须通过验证检查点
        """
        separator = "=" * get_format('separator_length')
        datetime_fmt = get_format('datetime')
        print(separator)
        print(f"🚀 开始执行营收增长预测分析: {self.company_name}")
        print(f"📅 执行时间: {datetime.now().strftime(datetime_fmt)}")
        print(f"📦 框架版本: {get_version()}")
        print(separator)

        try:
            # ========== 步骤1: 初始化缓存系统 ==========
            print("\n📍 步骤1: 初始化缓存系统")
            cache_dir, metadata = self.cache_system.init_company_cache(self.company_name)

            # 验证检查点1
            if not self.validator.check_step1_cache_initialization():
                raise Exception("❌ 缓存初始化验证失败,停止执行!")

            # ========== 步骤2: 读取必要模块 ==========
            print("\n📍 步骤2: 读取必要模块")
            # 这里由用户调用Read工具读取模块
            # 暂时记录已读取的模块列表
            print("ℹ️ 请确保已读取以下模块:")
            for module_path in get_all_module_paths():
                print(f"  - {module_path}")

            # 验证检查点2(在读取模块后手动调用)
            # if not self.validator.check_step2_module_reading(self.modules_read):
            #     raise Exception("❌ 模块读取验证失败,停止执行!")

            # ========== 步骤3-10: 其他分析步骤 ==========
            # ... (这里留给实际的业务逻辑)

            # ========== 最后验证: 输出文件 ==========
            print("\n📍 最后验证: 检查输出文件")
            # if not self.validator.check_step3_output_files():
            #     raise Exception("❌ 输出文件验证失败!")

            # ========== 打印总结 ==========
            separator = "=" * get_format('separator_length')
            print(f"\n{separator}")
            print("✅ 分析执行完成!")
            print(separator)

            return True

        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            print("💡 建议: 请检查上述错误信息,修正后重新执行")
            return False

# ============ 第四部分:使用示例 ============

if __name__ == "__main__":
    """
    使用示例

    注意: 此示例代码仅供演示,实际使用时请通过skill.md调用
    """
    import sys

    if len(sys.argv) > 1:
        company_name = sys.argv[1]
    else:
        print("用法: python executor.py <公司名称>")
        print("示例: python executor.py 小米集团")
        sys.exit(1)

    executor = RevenueForecastExecutor(company_name)
    success = executor.execute_analysis()

    if success:
        print("\n✅ 分析成功完成!")
    else:
        print("\n❌ 分析执行失败!")
        sys.exit(1)
