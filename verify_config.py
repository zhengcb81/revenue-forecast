#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""配置验证脚本"""
import os
import sys

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.encoding import setup_utf8_console
setup_utf8_console()

from core.config import (
    validate_config,
    print_config_validation,
    get_cache_base_dir,
    get_output_dir,
    get_search_results_subdir,
    get_dimension_files,
    get_company_types
)

def main():
    print("=" * 60)
    print("配置验证检查点 - 第0步")
    print("=" * 60)
    print()

    # 1. 验证配置完整性
    is_valid, errors = validate_config()
    print(f"[OK] 配置验证: {'通过' if is_valid else '失败'}")
    if errors:
        print("错误信息:")
        for error in errors:
            print(f"   [X] {error}")
    print()

    # 2. 打印配置摘要
    print(print_config_validation())
    print()

    # 3. 详细配置信息
    print("详细配置信息:")
    print(f"[OK] 缓存根目录: {get_cache_base_dir()}")
    print(f"[OK] 输出目录: {get_output_dir()}")
    print(f"[OK] 搜索结果子目录: {get_search_results_subdir()}")
    print(f"[OK] 默认维度文件数: {len(get_dimension_files('default'))}个")
    print(f"[OK] 产品驱动型维度文件数: {len(get_dimension_files('product-driven'))}个")
    print(f"[OK] 公司类型配置: {list(get_company_types().keys())}")
    print()

    print("=" * 60)
    print("[OK] 第0步配置加载完成！可以继续下一步")
    print("=" * 60)

if __name__ == "__main__":
    main()
