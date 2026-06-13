#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import datetime
from pathlib import Path

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.encoding import setup_utf8_console
setup_utf8_console()


def sanitize_company_name(name):
    """清理公司名称，生成文件系统安全的目录名"""
    safe_name = re.sub(r'[\\/:*?"<>|]', "", name)
    safe_name = re.sub(r"[\s\-]+", "_", safe_name)
    safe_name = safe_name[:50].strip("_")
    return safe_name


def init_company_cache(company_name):
    """初始化公司缓存目录"""
    base_dir = "revenue-forecast-cache"
    safe_name = sanitize_company_name(company_name)
    full_path = os.path.join(base_dir, safe_name)

    # 创建目录
    os.makedirs(full_path, exist_ok=True)
    os.makedirs(os.path.join(full_path, "search-results"), exist_ok=True)

    # 创建metadata.json
    metadata = {
        "company_name": company_name,
        "sanitized_name": safe_name,
        "first_analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "last_analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_count": 0,
        "cache_version": "v2.5.0",
        "dimension_cache_status": {},
        "search_keywords_history": {},
    }

    metadata_path = os.path.join(full_path, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[OK] Cache directory created: {full_path}")
    print(f"[OK] Metadata file created: {metadata_path}")
    return full_path


if __name__ == "__main__":
    import sys

    company_name = sys.argv[1] if len(sys.argv) > 1 else "Synthomer"
    init_company_cache(company_name)
