"""
Revenue Forecast - 行业数据模块 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 行业CAGR数据管理
2. 公司历史数据缓存
3. 同业公司数据
4. 数据更新和同步
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class IndustryMetrics:
    """行业指标数据"""
    name: str
    cagr_avg: float
    cagr_high: float
    cagr_low: float
    market_size: Optional[float] = None
    growth_drivers: List[str] = None
    risks: List[str] = None
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CompanyMetrics:
    """公司指标数据"""
    name: str
    industry: str
    historical_cagr: Optional[float] = None
    revenue_base: Optional[float] = None
    market_share: Optional[float] = None
    peers: List[str] = None
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IndustryData:
    """
    行业数据管理器
    
    管理行业和公司的历史数据，为CAGR验证提供基准
    """
    
    # 内置行业数据（简化版）
    BUILTIN_INDUSTRIES = {
        "technology": IndustryMetrics(
            name="Technology",
            cagr_avg=12.0,
            cagr_high=25.0,
            cagr_low=3.0,
            market_size=5000,
            growth_drivers=["数字化转型", "AI应用", "云计算"],
            risks=["技术迭代快", "竞争加剧"],
            last_updated="2026-01-01"
        ),
        "software": IndustryMetrics(
            name="Software",
            cagr_avg=15.0,
            cagr_high=30.0,
            cagr_low=5.0,
            market_size=3000,
            growth_drivers=["SaaS普及", "AI赋能", "企业数字化"],
            risks=["开源替代", "价格战"],
            last_updated="2026-01-01"
        ),
        "hardware": IndustryMetrics(
            name="Hardware",
            cagr_avg=8.0,
            cagr_high=15.0,
            cagr_low=2.0,
            market_size=8000,
            growth_drivers=["5G换机", "IoT设备", "新能源汽车电子"],
            risks=["供应链波动", "技术路线不确定"],
            last_updated="2026-01-01"
        ),
        "semiconductor": IndustryMetrics(
            name="Semiconductor",
            cagr_avg=10.0,
            cagr_high=20.0,
            cagr_low=3.0,
            market_size=6000,
            growth_drivers=["国产替代", "AI芯片", "汽车芯片"],
            risks=["地缘政治", "周期波动", "高投入"],
            last_updated="2026-01-01"
        ),
        "consumer_electronics": IndustryMetrics(
            name="Consumer Electronics",
            cagr_avg=6.0,
            cagr_high=12.0,
            cagr_low=1.0,
            market_size=4000,
            growth_drivers=["产品创新", "出海扩张", "生态协同"],
            risks=["市场饱和", "竞争加剧", "汇率波动"],
            last_updated="2026-01-01"
        ),
        "automotive": IndustryMetrics(
            name="Automotive",
            cagr_avg=5.0,
            cagr_high=10.0,
            cagr_low=0.0,
            market_size=10000,
            growth_drivers=["新能源转型", "智能化", "出海"],
            risks=["产能过剩", "价格战", "政策变化"],
            last_updated="2026-01-01"
        ),
        "new_energy": IndustryMetrics(
            name="New Energy",
            cagr_avg=20.0,
            cagr_high=35.0,
            cagr_low=8.0,
            market_size=2000,
            growth_drivers=[["政策支持", "技术进步", "成本下降"]],
            risks=[["产能过剩", "技术路线", "补贴退坡"]],
            last_updated="2026-01-01"
        ),
        "pharmaceutical": IndustryMetrics(
            name="Pharmaceutical",
            cagr_avg=8.0,
            cagr_high=15.0,
            cagr_low=3.0,
            market_size=2500,
            growth_drivers=["老龄化", "创新药", "出海"],
            risks=["集采", "研发失败", "监管变化"],
            last_updated="2026-01-01"
        ),
        "healthcare": IndustryMetrics(
            name="Healthcare",
            cagr_avg=10.0,
            cagr_high=18.0,
            cagr_low=5.0,
            market_size=3000,
            growth_drivers=["老龄化", "医疗升级", "数字化"],
            risks=["政策监管", "人才短缺"],
            last_updated="2026-01-01"
        ),
        "financial": IndustryMetrics(
            name="Financial Services",
            cagr_avg=6.0,
            cagr_high=12.0,
            cagr_low=2.0,
            market_size=8000,
            growth_drivers=["财富管理", "金融科技", "国际化"],
            risks=["利率波动", "监管加强", "坏账风险"],
            last_updated="2026-01-01"
        ),
        "e_commerce": IndustryMetrics(
            name="E-commerce",
            cagr_avg=15.0,
            cagr_high=25.0,
            cagr_low=8.0,
            market_size=3500,
            growth_drivers=["渗透率提升", "直播电商", "下沉市场"],
            risks=["流量成本上升", "竞争加剧", "监管"],
            last_updated="2026-01-01"
        ),
        "manufacturing": IndustryMetrics(
            name="Manufacturing",
            cagr_avg=4.0,
            cagr_high=8.0,
            cagr_low=1.0,
            market_size=15000,
            growth_drivers=["自动化", "出海", "产业升级"],
            risks=[["成本上升", "订单波动", "贸易壁垒"]],
            last_updated="2026-01-01"
        ),
        "utilities": IndustryMetrics(
            name="Utilities",
            cagr_avg=2.0,
            cagr_high=5.0,
            cagr_low=0.0,
            market_size=5000,
            growth_drivers=["电价改革", "新能源接入", "智能化"],
            risks=["价格管制", "环保要求"],
            last_updated="2026-01-01"
        ),
        "real_estate": IndustryMetrics(
            name="Real Estate",
            cagr_avg=2.0,
            cagr_high=6.0,
            cagr_low=-3.0,
            market_size=8000,
            growth_drivers=["存量运营", "REITs", "物流地产"],
            risks=["政策调控", "去杠杆", "人口结构"],
            last_updated="2026-01-01"
        )
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化行业数据管理器
        
        Args:
            data_dir: 数据目录路径，默认使用 skill 目录下的 data/
        """
        if data_dir is None:
            skill_dir = Path(__file__).parent.parent
            data_dir = skill_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.industries_file = self.data_dir / "industries.json"
        self.companies_file = self.data_dir / "companies.json"
        
        # 加载数据
        self._industries: Dict[str, IndustryMetrics] = {}
        self._companies: Dict[str, CompanyMetrics] = {}
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        # 加载行业数据
        if self.industries_file.exists():
            try:
                with open(self.industries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, metrics in data.items():
                        self._industries[name] = IndustryMetrics(**metrics)
            except Exception as e:
                print(f"[IndustryData] 加载行业数据失败: {e}")
                self._industries = self.BUILTIN_INDUSTRIES.copy()
        else:
            self._industries = self.BUILTIN_INDUSTRIES.copy()
            self._save_industries()
        
        # 加载公司数据
        if self.companies_file.exists():
            try:
                with open(self.companies_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, metrics in data.items():
                        self._companies[name] = CompanyMetrics(**metrics)
            except Exception as e:
                print(f"[IndustryData] 加载公司数据失败: {e}")
    
    def _save_industries(self):
        """保存行业数据"""
        try:
            with open(self.industries_file, 'w', encoding='utf-8') as f:
                data = {name: metrics.to_dict() for name, metrics in self._industries.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[IndustryData] 保存行业数据失败: {e}")
    
    def _save_companies(self):
        """保存公司数据"""
        try:
            with open(self.companies_file, 'w', encoding='utf-8') as f:
                data = {name: metrics.to_dict() for name, metrics in self._companies.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[IndustryData] 保存公司数据失败: {e}")
    
    def get_industry_cagr(self, industry: str, metric: str = "avg") -> Optional[float]:
        """
        获取行业CAGR
        
        Args:
            industry: 行业名称
            metric: 指标类型 (avg/high/low)
            
        Returns:
            float: CAGR值，找不到返回None
        """
        # 标准化行业名称
        industry_key = self._normalize_name(industry)
        
        if industry_key not in self._industries:
            return None
        
        ind = self._industries[industry_key]
        
        if metric == "avg":
            return ind.cagr_avg
        elif metric == "high":
            return ind.cagr_high
        elif metric == "low":
            return ind.cagr_low
        else:
            return None
    
    def get_industry_metrics(self, industry: str) -> Optional[IndustryMetrics]:
        """获取行业完整指标"""
        industry_key = self._normalize_name(industry)
        return self._industries.get(industry_key)
    
    def get_company_metrics(self, company: str) -> Optional[CompanyMetrics]:
        """获取公司完整指标"""
        company_key = self._normalize_name(company)
        return self._companies.get(company_key)
    
    def get_company_historical_cagr(self, company: str) -> Optional[float]:
        """获取公司历史CAGR"""
        metrics = self.get_company_metrics(company)
        if metrics:
            return metrics.historical_cagr
        return None
    
    def get_company_peers(self, company: str) -> List[str]:
        """获取公司同业列表"""
        metrics = self.get_company_metrics(company)
        if metrics and metrics.peers:
            return metrics.peers
        return []
    
    def update_company_cagr(self, company: str, cagr: float, year: int = 2026):
        """
        更新公司历史CAGR
        
        用于记录实际结果，改进未来预测
        """
        company_key = self._normalize_name(company)
        
        if company_key not in self._companies:
            # 创建新公司记录
            self._companies[company_key] = CompanyMetrics(
                name=company,
                industry="unknown",
                historical_cagr=cagr,
                last_updated=f"{year}-01-01"
            )
        else:
            # 更新现有记录
            self._companies[company_key].historical_cagr = cagr
            self._companies[company_key].last_updated = f"{year}-01-01"
        
        self._save_companies()
    
    def add_company(self, company: str, industry: str, peers: List[str] = None):
        """添加公司记录"""
        company_key = self._normalize_name(company)
        
        self._companies[company_key] = CompanyMetrics(
            name=company,
            industry=industry,
            peers=peers or [],
            last_updated="2026-01-01"
        )
        
        self._save_companies()
    
    def list_industries(self) -> List[str]:
        """列出所有行业"""
        return list(self._industries.keys())
    
    def list_companies(self) -> List[str]:
        """列出所有公司"""
        return list(self._companies.keys())
    
    def search_industry_by_keyword(self, keyword: str) -> List[str]:
        """通过关键词搜索行业"""
        keyword = keyword.lower()
        results = []
        
        for name, metrics in self._industries.items():
            if keyword in name.lower():
                results.append(name)
            elif metrics.growth_drivers:
                for driver in metrics.growth_drivers:
                    if keyword in driver.lower():
                        results.append(name)
                        break
        
        return results
    
    def _normalize_name(self, name: str) -> str:
        """标准化名称"""
        return name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")


# 便捷函数
def get_industry_cagr(industry: str, metric: str = "avg") -> Optional[float]:
    """便捷函数：获取行业CAGR"""
    data = IndustryData()
    return data.get_industry_cagr(industry, metric)


def get_company_historical_cagr(company: str) -> Optional[float]:
    """便捷函数：获取公司历史CAGR"""
    data = IndustryData()
    return data.get_company_historical_cagr(company)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("IndustryData 测试")
    print("=" * 60)
    
    data = IndustryData()
    
    print("\n行业列表:")
    industries = data.list_industries()
    for ind in industries[:5]:
        cagr = data.get_industry_cagr(ind)
        print(f"  {ind}: {cagr}%")
    print(f"  ... 共{len(industries)}个行业")
    
    print("\n获取特定行业数据 (technology):")
    metrics = data.get_industry_metrics("technology")
    if metrics:
        print(f"  平均CAGR: {metrics.cagr_avg}%")
        print(f"  增长驱动: {metrics.growth_drivers}")
    
    print("\n更新公司CAGR:")
    data.update_company_cagr("小米集团", 22.5, 2026)
    cagr = data.get_company_historical_cagr("小米集团")
    print(f"  小米集团历史CAGR: {cagr}%")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
