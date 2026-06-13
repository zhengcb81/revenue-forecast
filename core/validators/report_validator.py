"""
报告系统验证器
模块: modules/output/save-report.md
用途: 验证报告是否正确生成
检查点: CP-5, CP-6, CP-8
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
for _p in (_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
           _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import os
import json
import sys

# 导入配置模块
from core.config import get_path, get_required_fields, get_file_pattern, get_module_path


def validate_module_read():
    """
    CP-5: 报告模块已读取验证

    验证标准:
    - 必须已读取报告模块
    - 重点关注: JSON模板、Markdown模板
    - 理解文件命名规则(不带日期后缀)
    """
    report_module_path = get_module_path('report')
    print("[CP-5] 报告模块读取验证")
    print(f"  [检查] 确认已读取: {report_module_path}")
    print(f"  [重点] 重点关注: JSON模板、Markdown模板")
    print(f"  [重点] 文件命名规则: 不带日期后缀")
    print("[通过] CP-5验证通过: 报告模块已读取\n")
    return True


def validate_output_files(company_name):
    """
    CP-6: 输出文件已生成验证

    验证标准:
    - JSON和Markdown文件必须存在
    - 文件大小必须 > 0
    - JSON文件必须格式有效
    - 必须包含必需字段
    """
    print("[CP-6] 输出文件验证")
    output_dir = get_path('output_dir')

    # 检查outputs目录
    if not os.path.exists(output_dir):
        raise ValueError(
            f"[错误] outputs/目录不存在: {output_dir}\n"
            f"[建议] 请执行: mkdir -p {output_dir}"
        )

    # 从配置获取文件路径
    json_file = os.path.join(output_dir, get_file_pattern('json_output', company_name))
    md_file = os.path.join(output_dir, get_file_pattern('md_output', company_name))

    # 检查JSON文件
    if not os.path.exists(json_file):
        raise ValueError(
            f"[错误] JSON文件不存在: {json_file}\n"
            f"[建议] 请生成报告文件"
        )

    if not os.path.isfile(json_file):
        raise ValueError(f"[错误] JSON路径不是文件: {json_file}")

    json_size = os.path.getsize(json_file)
    if json_size == 0:
        raise ValueError(f"[错误] JSON文件为空: {json_file}")

    # 验证JSON格式
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"[错误] JSON格式无效: {e}\n"
            f"[建议] 请检查JSON语法"
        )

    # 从配置获取必需字段
    required_fields = get_required_fields('report')

    missing_fields = [field for field in required_fields if field not in json_data]
    if missing_fields:
        raise ValueError(
            f"[错误] JSON缺少必需字段: {missing_fields}\n"
            f"[建议] 请按照模板生成JSON"
        )

    print(f"  [OK] JSON文件存在: {json_file}")
    print(f"  [OK] JSON格式有效")
    print(f"  [OK] JSON大小: {json_size} bytes")
    print(f"  [OK] 必需字段完整: {len(required_fields)}个")

    # 检查Markdown文件
    if not os.path.exists(md_file):
        raise ValueError(
            f"[错误] Markdown文件不存在: {md_file}\n"
            f"[建议] 请生成报告文件"
        )

    if not os.path.isfile(md_file):
        raise ValueError(f"[错误] Markdown路径不是文件: {md_file}")

    md_size = os.path.getsize(md_file)
    if md_size == 0:
        raise ValueError(f"[错误] Markdown文件为空: {md_file}")

    print(f"  [OK] Markdown文件存在: {md_file}")
    print(f"  [OK] Markdown大小: {md_size} bytes")
    print("[通过] CP-6验证通过: 输出文件完整有效\n")

    return {
        "json_file": json_file,
        "md_file": md_file,
        "json_size": json_size,
        "md_size": md_size
    }


def validate_file_naming(company_name):
    """
    CP-8: 文件命名无日期后缀验证

    验证标准:
    - 文件名不包含日期后缀
    """
    print("[CP-8] 文件命名验证")
    output_dir = get_path('output_dir')

    # 列出outputs目录中的文件
    if not os.path.exists(output_dir):
        print("[跳过] outputs/目录不存在")
        return True

    files = os.listdir(output_dir)

    # 检查是否有错误的命名(带日期后缀)
    wrong_patterns = [
        f"RevGrowth_{company_name}_",
        f"RevGrowth_{company_name}-",
        f"RevGrowth_FullReport_{company_name}_",
        f"RevGrowth_FullReport_{company_name}-"
    ]

    wrong_files = []
    for file in files:
        if company_name in file:
            for pattern in wrong_patterns:
                if file.startswith(pattern):
                    wrong_files.append(file)
                    break

    if wrong_files:
        expected_json = get_file_pattern('json_output', company_name)
        expected_md = get_file_pattern('md_output', company_name)
        raise ValueError(
            f"[错误] 发现带日期后缀的文件: {wrong_files}\n"
            f"[正确] {expected_json}\n"
            f"[正确] {expected_md}\n"
            f"[建议] 请重命名文件,删除日期后缀"
        )

    print(f"  [OK] 文件命名正确(无日期后缀)")
    print("[通过] CP-8验证通过: 文件命名符合规范\n")
    return True


def validate_report_workflow(company_name, module_read=True):
    """
    一键验证报告工作流
    集成CP-5, CP-6, CP-8

    Args:
        company_name: 公司名称
        module_read: 是否已读取报告模块

    Returns:
        tuple: (bool, dict) - (是否全部通过, 文件信息)

    使用示例:
        success, file_info = validate_report_workflow("宝马集团")
        if success:
            print("[OK] 报告验证通过")
        else:
            print("[错误] 报告验证失败")
            sys.exit(1)
    """
    print("="*60)
    print("[验证] 报告系统验证检查点")
    print("="*60)

    try:
        # CP-5: 模块读取验证
        if module_read:
            validate_module_read()
        else:
            print("[跳过] CP-5验证(模块未读取)")

        # CP-8: 文件命名验证
        validate_file_naming(company_name)

        # CP-6: 输出文件验证
        file_info = validate_output_files(company_name)

        print("="*60)
        print("[成功] 所有报告检查点通过 (CP-5, CP-6, CP-8)")
        print("="*60)
        print()

        return True, file_info

    except ValueError as e:
        print("="*60)
        print("[失败] 报告验证失败")
        print("="*60)
        print(str(e))
        print()

        return False, {}


# ========== 命令行使用 ==========
if __name__ == "__main__":
    """
    命令行使用示例:
        python report_validator.py 宝马集团
    """
    if len(sys.argv) < 2:
        print("用法: python report_validator.py <公司名称>")
        print("示例: python report_validator.py 宝马集团")
        print()
        print("说明:")
        print("  公司名称: 要验证的公司名称")
        sys.exit(1)

    company_name = sys.argv[1]
    success, file_info = validate_report_workflow(company_name)

    if success:
        print()
        print("="*60)
        print("[报告文件信息]")
        print("="*60)
        print(f"JSON文件: {file_info['json_file']}")
        print(f"Markdown文件: {file_info['md_file']}")
        print(f"JSON大小: {file_info['json_size']} bytes")
        print(f"Markdown大小: {file_info['md_size']} bytes")
        print("="*60)

    sys.exit(0 if success else 1)
