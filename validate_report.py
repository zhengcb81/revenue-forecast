#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revenue-forecast 报告验证脚本

用途：验证生成的分析报告是否符合框架要求
版本：v2.0 (v2.6.0)
创建日期：2026-01-15
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

    def _detect_origin_type(self):
        """从 metadata.json 读取公司地域类型（v2.6.1）

        复用第3步语言策略判定的结果，未找到则默认 'foreign'（保守判定）。

        Returns:
            str: 'chinese' / 'foreign' / 'mixed'
        """
        import os as _os
        # 缓存目录可能在多个位置：相对 output_dir 的上级、或 revenue-forecast-cache/
        candidates = []
        # 路径1: {output_dir}/../revenue-forecast-cache/{company}/metadata.json
        parent = _os.path.dirname(self.output_dir.rstrip("/\\"))
        candidates.append(_os.path.join(parent, "revenue-forecast-cache", self.company_name, "metadata.json"))
        # 路径2: {output_dir}/../../revenue-forecast-cache/{company}/metadata.json
        grand = _os.path.dirname(parent)
        candidates.append(_os.path.join(grand, "revenue-forecast-cache", self.company_name, "metadata.json"))

        for path in candidates:
            if _os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    ot = meta.get("origin_type")
                    if ot in ("chinese", "foreign", "mixed"):
                        return ot
                except Exception:
                    pass
        return "foreign"  # 默认对外国公司保守判定

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

    def strip_non_prose(self, content):
        """剥离脚注区、引用区、URL、代码块等非正文内容

        v2.6.1 新增：语言检查只针对"正文叙述"，不针对溯源脚注。
        外国公司的脚注原文天然是英文（SEC 文件、英文新闻稿），
        将其计入语言比例会严重高估英文占比，导致误判。

        Args:
            content: Markdown 完整内容

        Returns:
            str: 仅保留正文叙述的内容
        """
        import re as _re
        lines = content.split("\n")
        prose_lines = []
        in_code_block = False
        in_footnote_section = False

        for line in lines:
            # 跟踪代码块状态
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # 检测脚注区起始（## 参数溯源 / ## 脚注 / ## 引用 / ## References 等章节）
            if _re.match(r"^#{1,6}\s*(参数溯源|脚注|引用|参考资料|References|Footnotes|附录|Appendix)", line):
                in_footnote_section = True
                continue
            # 遇到下一个一级/二级章节，退出脚注区
            if in_footnote_section and _re.match(r"^#{1,2}\s+", line):
                in_footnote_section = False

            if in_footnote_section:
                continue

            # 跳过脚注行（[^xx]:）和纯 URL 行
            if _re.match(r"^\s*\[\^[^\]]+\]:", line):
                continue
            if _re.match(r"^\s*(URL|链接|来源链接)\s*:", line, _re.IGNORECASE):
                continue
            # 跳过表格分隔线、空行
            if not stripped or _re.match(r"^[\|\-\s:]+$", stripped):
                continue

            # 行内剥离 URL 和 [^xx] 引用标记
            cleaned = _re.sub(r"https?://[^\s)]+", "", line)
            cleaned = _re.sub(r"\[\^[^\]]+\]", "", cleaned)
            prose_lines.append(cleaned)

        return "\n".join(prose_lines)

    def detect_long_english_runs(self, content, min_length=80):
        """检测正文中连续的长英文段落（v2.6.1 软指标）

        抓"真正的问题"：正文中出现未翻译的大段英文。
        与 english_ratio 不同，本指标不受专有名词稀释影响。

        Args:
            content: 已剥离脚注/引用的正文
            min_length: 视为"长英文段落"的最小连续英文单词数（默认 80）

        Returns:
            list: 每个长英文段落的 (行号, 字符数) 元组列表
        """
        import re as _re
        runs = []
        # 按"非英文边界"切分（中文、标点等），找连续英文段
        # 连续英文段定义为：连续的 ASCII 字母+空格+常见标点（.,;:()-"）
        pattern = _re.compile(r"[A-Za-z][A-Za-z\s.,;:()\-\u2014\u2013\"'/%$]+")
        for match in pattern.finditer(content):
            seg = match.group()
            # 统计英文单词数（数字不算）
            words = [w for w in seg.split() if any(c.isalpha() and ord(c) < 128 for c in w)]
            if len(words) >= min_length:
                runs.append((match.start(), len(words)))
        return runs


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

        # 检查4: 语言检测（v2.6.1 改进：仅检查正文，不检查脚注/引用/URL）
        prose = self.strip_non_prose(content)

        # 4a: 整体英文比例（含脚注）—— 仅作展示
        overall_ratio = self.detect_english_ratio(content)
        # 4b: 正文英文比例（剥离脚注/引用/URL 后）—— 真正的判定依据
        prose_ratio = self.detect_english_ratio(prose)
        print(f"📊 英文比例（整体）: {overall_ratio * 100:.1f}%")
        print(f"📊 英文比例（正文，剥离脚注/URL）: {prose_ratio * 100:.1f}%")

        # 4c: 长英文段落检测（软指标）
        long_runs = self.detect_long_english_runs(prose, min_length=80)

        # 按公司地域分级判定（v2.6.1）
        origin_type = self._detect_origin_type()
        thresholds = {
            "chinese":  {"prose_ratio": 0.20, "long_runs": 1,  "label": "中国公司"},
            "foreign":  {"prose_ratio": 0.55, "long_runs": 3,  "label": "外国公司"},
            "mixed":    {"prose_ratio": 0.40, "long_runs": 2,  "label": "混合公司"},
        }
        cfg = thresholds.get(origin_type, thresholds["foreign"])

        failed = False
        if prose_ratio > cfg["prose_ratio"]:
            self.errors.append(
                f"❌ 正文语言违规: 正文英文比例 {prose_ratio * 100:.1f}% > {cfg['prose_ratio']*100:.0f}% "
                f"（{cfg['label']}阈值；脚注/URL 已排除）"
            )
            failed = True
        if len(long_runs) > cfg["long_runs"]:
            self.errors.append(
                f"❌ 正文出现 {len(long_runs)} 处连续英文长段（≥80 词），"
                f"超过 {cfg['label']}阈值 {cfg['long_runs']} 处。请检查是否有未翻译的英文段落。"
            )
            failed = True
        if failed:
            return False

        print(f"✅ 正文语言符合要求（{cfg['label']}策略，英文比例 {prose_ratio*100:.1f}%，长英文段 {len(long_runs)} 处）")

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

    # ============ v2.6.0 新增三项强制验证 ============

    def validate_calculation_trace(self):
        """验证计算过程完整性（四段落结构、加权公式、插值计算）

        对应 modules/output/save-report.md 第 5.9 节。
        """
        print(f"\n检查计算过程完整性（v2.6.0）")

        if not os.path.exists(self.md_file):
            self.errors.append(f"❌ 无法验证计算过程: Markdown文件不存在")
            return False

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查1: 情景预测章节的四段落结构
        four_section_keywords = ["假设依据", "计算过程", "验证检查", "结论"]
        missing_in_scenario = [kw for kw in four_section_keywords if kw not in content]
        if missing_in_scenario:
            self.errors.append(
                f"❌ 情景预测章节缺少四段落结构: 缺失 {', '.join(missing_in_scenario)}"
            )
        else:
            print(f"✅ 情景预测章节包含四段落结构（假设依据/计算过程/验证检查/结论）")

        # 检查2: 综合CAGR章节是否包含加权计算
        weighted_indicators = ["加权", "概率"]
        has_weighted = all(ind in content for ind in weighted_indicators)
        if not has_weighted:
            self.errors.append(f"❌ 综合CAGR章节缺少加权计算过程（关键词: 加权/概率）")
        else:
            print(f"✅ 综合CAGR章节包含加权计算过程")

        # 检查3: 评分章节是否包含线性插值计算
        interpolation_indicators = ["插值", "评分"]
        has_interpolation = all(ind in content for ind in interpolation_indicators)
        if not has_interpolation:
            self.warnings.append(
                f"⚠️ 评分章节未检测到线性插值计算关键词（插值/评分）"
            )
        else:
            print(f"✅ 评分章节包含线性插值计算")

        # 检查4: JSON 是否包含 calculation_trace 字段
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    jdata = json.load(f)
                if "calculation_trace" not in jdata:
                    self.errors.append(
                        f"❌ JSON 缺少 calculation_trace 字段（计算过程记录）"
                    )
                else:
                    print(f"✅ JSON 包含 calculation_trace 字段")
            except json.JSONDecodeError:
                self.warnings.append(f"⚠️ JSON 格式错误，无法检查 calculation_trace")

        return not any(
            "计算过程" in e or "calculation_trace" in e or "加权" in e
            for e in self.errors
        )

    def validate_evidence_chain(self):
        """验证证据链完整性（全链路溯源 Level 3）

        对应 modules/parameter-tracing/evidence-chain-spec.md。
        """
        print(f"\n检查证据链完整性（v2.6.0 Level 3）")

        # ---- JSON 侧检查 ----
        if not os.path.exists(self.json_file):
            self.errors.append(f"❌ 无法验证证据链: JSON文件不存在")
            return False

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                jdata = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ JSON 格式错误，无法验证证据链: {e}")
            return False

        ec = jdata.get("evidence_chain")
        if not ec or not isinstance(ec, dict):
            self.errors.append(
                f"❌ JSON 缺少 evidence_chain 字段（v2.6.0 强制 Level 3 全链路溯源）"
            )
            return False

        # 检查1: 溯源参数数量 ≥ 10
        params = ec.get("params", [])
        if len(params) < 10:
            self.errors.append(
                f"❌ evidence_chain.params 数量不足: {len(params)} < 10"
            )
        else:
            print(f"✅ 溯源参数数量: {len(params)} (≥ 10)")

        # 检查2: 每条证据必须有 9 个必填字段且 URL/quote 合法
        required_evidence_fields = [
            "search_query", "source_url", "source_title", "source_date",
            "source_type", "quote", "extracted_value", "reliability", "timestamp",
        ]
        bad_entries = 0
        for i, p in enumerate(params):
            ev = p.get("evidence")
            if not ev or not isinstance(ev, dict):
                self.errors.append(
                    f"❌ evidence_chain.params[{i}] 缺少 evidence 子对象"
                )
                bad_entries += 1
                continue
            missing = [k for k in required_evidence_fields if k not in ev]
            if missing:
                self.errors.append(
                    f"❌ evidence_chain.params[{i}].evidence 缺失字段: {', '.join(missing)}"
                )
                bad_entries += 1
                continue
            url = ev.get("source_url", "")
            if not (url.startswith("http://") or url.startswith("https://")):
                self.errors.append(
                    f"❌ evidence_chain.params[{i}].source_url 非 http(s) 开头: {url[:50]}"
                )
                bad_entries += 1
                continue
            quote = ev.get("quote", "")
            if not (10 <= len(quote) <= 500):
                self.errors.append(
                    f"❌ evidence_chain.params[{i}].quote 长度 {len(quote)} 不在 10-500 区间"
                )
                bad_entries += 1

        if bad_entries == 0 and len(params) >= 10:
            print(f"✅ 所有证据条目字段完整、URL/quote 合法")

        # 检查3: 必溯清单覆盖率 100%
        critical_param_names = {
            "current_revenue", "revenue_growth_yoy", "operating_margin",
            "net_margin", "market_share", "segment_revenue",
            "composite_cagr",
        }
        traced_names = {p.get("param_name", "") for p in params}
        # 宽松匹配：只要 param_name 包含关键词即视为已溯
        covered = set()
        for cn in critical_param_names:
            if any(cn in (pn or "") for pn in traced_names):
                covered.add(cn)
        uncovered = critical_param_names - covered
        if uncovered:
            self.errors.append(
                f"❌ 必溯参数未覆盖: {', '.join(sorted(uncovered))}（必溯清单要求 100% 覆盖）"
            )
        else:
            print(f"✅ 必溯参数清单 100% 覆盖")

        # 检查4: coverage_pct ≥ 85
        coverage = ec.get("coverage_pct", 0)
        try:
            coverage = float(coverage)
        except (TypeError, ValueError):
            coverage = 0.0
        if coverage < 85.0:
            self.errors.append(
                f"❌ 证据链覆盖率 {coverage}% < 85%（最低要求）"
            )
        else:
            print(f"✅ 证据链覆盖率: {coverage}%")

        # 检查5: untraced_critical_params 必须为空
        untraced = ec.get("untraced_critical_params", [])
        if untraced:
            self.errors.append(
                f"❌ untraced_critical_params 非空: {untraced}"
            )
        else:
            print(f"✅ 无未溯源的关键参数")

        # ---- Markdown 侧检查：脚注数 ≥ 10 ----
        if os.path.exists(self.md_file):
            with open(self.md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            footnote_pattern = re.compile(r"\[\^[\w\-]+\]")
            footnotes = set(footnote_pattern.findall(md_content))
            if len(footnotes) < 10:
                self.errors.append(
                    f"❌ Markdown 脚注数量不足: {len(footnotes)} < 10"
                )
            else:
                print(f"✅ Markdown 脚注数量: {len(footnotes)} (≥ 10)")

        return not any("evidence_chain" in e or "脚注" in e or "必溯" in e
                       or "覆盖率" in e or "未溯源" in e or "未覆盖" in e
                       for e in self.errors)

    def validate_calculation_consistency(self):
        """验证计算一致性：重新计算 weighted CAGR，与报告值对比

        防止数字造假。对应 modules/parameter-tracing/evidence-chain-spec.md 第九节。
        """
        print(f"\n检查计算一致性（v2.6.0）")

        if not os.path.exists(self.json_file):
            self.warnings.append(f"⚠️ JSON 不存在，跳过计算一致性检查")
            return True

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                jdata = json.load(f)
        except json.JSONDecodeError:
            self.warnings.append(f"⚠️ JSON 格式错误，跳过计算一致性检查")
            return True

        trace = jdata.get("calculation_trace")
        if not trace:
            self.warnings.append(
                f"⚠️ JSON 无 calculation_trace 字段，跳过计算一致性检查"
            )
            return True

        # 检查: weighted_average 段的 calculation_steps 是否加和一致
        weighted = trace.get("weighted_average") or trace.get("composite_cagr") or {}
        steps = weighted.get("calculation_steps")
        # 期望 calculation_steps 是字符串列表，形如 "870.8×25%=217.7"
        if steps and isinstance(steps, list):
            try:
                # 提取每步的等号右侧数字，加和（跳过"合计/总计/Total"行，避免双重计算）
                extracted = []
                for s in steps:
                    if "=" in s and not re.search(r"合计|总计|Total|sum", s, re.IGNORECASE):
                        right = s.split("=", 1)[1]
                        # 提取最后一个数字（可能是加权值）
                        nums = re.findall(r"-?\d+\.?\d*", right)
                        if nums:
                            extracted.append(float(nums[-1]))
                if extracted:
                    total = sum(extracted)
                    # 与合计行对比（寻找 "合计" 或最终 result 字段）
                    final = weighted.get("result") or weighted.get("total")
                    if final is not None:
                        try:
                            final = float(final)
                            if abs(total - final) > 0.5:
                                self.errors.append(
                                    f"❌ 计算一致性失败: 加权步骤合计 {total:.1f} ≠ 报告值 {final:.1f}"
                                )
                            else:
                                print(f"✅ 加权计算一致性通过: {total:.1f} ≈ {final:.1f}")
                        except (TypeError, ValueError):
                            pass
            except Exception as e:
                self.warnings.append(
                    f"⚠️ 加权计算一致性检查异常: {e}"
                )

        # 检查: CAGR 公式 (revenue_final/revenue_base)^(1/n)-1 与报告 CAGR 一致
        scenario = trace.get("scenario_analysis", {})
        base_rev = jdata.get("key_metrics", {}).get("current_revenue")
        if base_rev and scenario:
            try:
                base_rev = float(base_rev)
                # 找基准情景 annual_revenue 末年值
                base_scenario = scenario.get("base", {})
                ann = (base_scenario.get("annual_revenue")
                       or base_scenario.get("annual_revenue_forecast") or {})
                if isinstance(ann, dict) and ann:
                    last_year = sorted(ann.keys())[-1]
                    final_rev = float(ann[last_year])
                    years = len(ann)
                    if years > 0 and base_rev > 0:
                        cagr_calc = (final_rev / base_rev) ** (1.0 / years) - 1
                        cagr_reported = (base_scenario.get("cagr_5y")
                                         or base_scenario.get("cagr"))
                        if cagr_reported is not None:
                            try:
                                cagr_reported = float(cagr_reported)
                                diff = abs(cagr_calc * 100 - cagr_reported)
                                if diff > 1.0:
                                    self.errors.append(
                                        f"❌ CAGR 一致性失败: 重算 {cagr_calc*100:.1f}% vs 报告 {cagr_reported:.1f}%"
                                    )
                                else:
                                    print(
                                        f"✅ CAGR 一致性通过: {cagr_calc*100:.1f}% ≈ {cagr_reported:.1f}%"
                                    )
                            except (TypeError, ValueError):
                                pass
            except Exception as e:
                self.warnings.append(f"⚠️ CAGR 一致性检查异常: {e}")

        return not any("一致性失败" in e for e in self.errors)

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

        # v2.6.0 新增三项强制验证
        calc_trace_ok = self.validate_calculation_trace()
        evidence_ok = self.validate_evidence_chain()
        consistency_ok = self.validate_calculation_consistency()

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
            print(f"\n✅ 报告符合revenue-forecast v2.6.0框架要求")
            print(f"✅ 证据链: Level 3 全链路溯源 通过")
            print(f"✅ 计算过程: 四段落结构 + 一致性验证 通过")
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
