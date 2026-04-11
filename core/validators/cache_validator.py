"""
缓存系统验证器
模块: modules/cache/memory-cache.md
用途: 验证缓存系统初始化是否正确执行
检查点: CP-1, CP-2, CP-3
"""

import os
import json
import sys

# 导入配置模块
from core.config import get_path, get_required_fields


def validate_cache_path(company_name):
    """
    CP-1: 缓存路径正确性验证

    验证标准:
    - 缓存根目录必须与配置一致
    - 公司缓存目录必须正确
    """
    print("\n[CP-1] 缓存路径验证")
    cache_base_dir = get_path('cache_base_dir')

    # 检查根目录
    if not os.path.exists(cache_base_dir):
        raise ValueError(
            f"[错误] 缓存根目录不存在: {cache_base_dir}\n"
            f"[建议] 请执行: init_cache_system()"
        )

    # 检查公司目录
    expected_company_path = os.path.join(cache_base_dir, company_name)
    if not os.path.exists(expected_company_path):
        raise ValueError(
            f"[错误] 公司缓存目录不存在: {expected_company_path}\n"
            f"[建议] 请执行: init_company_cache('{company_name}')"
        )

    print(f"  [OK] 根目录: {os.path.abspath(cache_base_dir)}")
    print(f"  [OK] 公司目录: {os.path.abspath(expected_company_path)}")
    print("[通过] CP-1验证通过: 缓存路径正确\n")
    return True


def validate_metadata(company_name):
    """
    CP-2: metadata.json存在性验证

    验证标准:
    - metadata.json必须存在于公司缓存目录
    - 必须包含配置中定义的必需字段
    - 格式必须是有效的JSON
    """
    print("[CP-2] metadata.json验证")
    cache_base_dir = get_path('cache_base_dir')
    metadata_path = os.path.join(cache_base_dir, company_name, "metadata.json")

    # 检查文件存在
    if not os.path.exists(metadata_path):
        raise ValueError(
            f"[错误] metadata.json不存在: {metadata_path}\n"
            f"[建议] 请执行: init_company_cache('{company_name}')"
        )

    # 检查JSON格式
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"[错误] metadata.json格式错误: {e}\n"
            f"[建议] 请检查JSON语法"
        )

    # 从配置获取必需字段
    required_fields = get_required_fields('metadata')

    missing_fields = [field for field in required_fields if field not in metadata]
    if missing_fields:
        raise ValueError(
            f"[错误] metadata.json缺少必需字段: {missing_fields}\n"
            f"[建议] 请重新创建metadata.json"
        )

    print(f"  [OK] 文件存在: {metadata_path}")
    print(f"  [OK] JSON格式有效")
    print(f"  [OK] 必需字段完整: {len(required_fields)}个")
    print("[通过] CP-2验证通过: metadata.json完整有效\n")
    return metadata


def validate_search_results_dir(company_name):
    """
    CP-3: search-results/目录验证

    验证标准:
    - search-results/子目录必须存在
    """
    print("[CP-3] search-results/目录验证")
    cache_base_dir = get_path('cache_base_dir')
    search_results_dir = os.path.join(cache_base_dir, company_name, "search-results")

    if not os.path.exists(search_results_dir):
        raise ValueError(
            f"[错误] search-results/目录不存在: {search_results_dir}\n"
            f"[建议] 请执行: mkdir -p {search_results_dir}"
        )

    if not os.path.isdir(search_results_dir):
        raise ValueError(f"[错误] search-results/不是目录: {search_results_dir}")

    print(f"  [OK] 目录存在: {search_results_dir}")
    print("[通过] CP-3验证通过: search-results/目录存在\n")
    return search_results_dir


def validate_cache_setup(company_name, verbose=True):
    """
    一键验证所有缓存检查点
    集成CP-1, CP-2, CP-3

    使用示例:
        success, data = validate_cache_setup("宝马集团")
        if success:
            print("[OK] 可以继续下一步")
        else:
            print("[错误] 请修正错误后重试")
            sys.exit(1)
    """
    if verbose:
        print("="*60)
        print("[验证] 缓存系统验证检查点")
        print("="*60)

    try:
        # CP-1: 路径验证
        validate_cache_path(company_name)

        # CP-2: metadata.json验证
        metadata = validate_metadata(company_name)

        # CP-3: search-results/目录验证
        search_results_dir = validate_search_results_dir(company_name)

        if verbose:
            print("="*60)
            print("[成功] 所有缓存检查点通过 (CP-1, CP-2, CP-3)")
            print("="*60)
            print()

        return True, {
            "metadata": metadata,
            "search_results_dir": search_results_dir
        }

    except ValueError as e:
        if verbose:
            print("="*60)
            print("[失败] 缓存验证失败")
            print("="*60)
            print(str(e))
            print()
            print("[建议] 请检查上述错误并修正后重新验证")

        return False, {}


# ========== 命令行使用 ==========
if __name__ == "__main__":
    """
    命令行使用示例:
        python cache_validator.py 宝马集团
    """
    if len(sys.argv) < 2:
        print("用法: python cache_validator.py <公司名称>")
        print("示例: python cache_validator.py 宝马集团")
        sys.exit(1)

    company_name = sys.argv[1]
    success, _ = validate_cache_setup(company_name)

    sys.exit(0 if success else 1)
