"""Mineral exploration agent for ore deposit analysis using multi-source geophysical data."""

from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import numpy as np
from loguru import logger

from core.ollama_client import OllamaClient
from utils.rag_retriever import RAGRetriever


class MineralExplorationAgent:
    """Agent for mineral exploration and ore deposit analysis.

    Integrates gravity, magnetic, electromagnetic, and well log data
    for ore deposit identification and characterization.
    """

    SYSTEM_PROMPT = """你是一位专业的矿床地质学家和勘探地球物理学家。你的任务是综合分析重磁电、测井等多源数据,进行找矿预测和矿床评价。

你需要关注以下方面:
1. 矿床类型识别:根据地质特征和地球物理异常识别矿床类型
2. 成矿要素分析:分析控矿构造、岩性、地层等成矿要素
3. 地球物理解释:解释重力、磁法、电磁异常及其地质意义
4. 多源数据融合:综合重磁电测井数据进行综合评价
5. 找矿预测:基于已有信息预测找矿靶区和资源潜力

请提供专业、详细的矿床分析报告,包括矿床类型、成矿模式、资源潜力评估等。"""

    # 常见矿床类型及其特征
    DEPOSIT_TYPES = {
        "斑岩型铜矿": {
            "gravity": "低密度蚀变带,可能显示负异常",
            "magnetic": "强磁化晕,环带状磁性结构",
            "electromagnetic": "硫化矿体显示低阻高极化",
            "geology": "中酸性侵入岩,钾化-绢云母化-青磐岩化分带",
            "examples": ["德兴铜矿", "玉龙铜矿", "多宝山铜矿"]
        },
        "矽卡岩型铁矿": {
            "gravity": "高密度矿体,正异常明显",
            "magnetic": "强磁性,高磁异常",
            "electromagnetic": "导电性好,低阻异常",
            "geology": "中酸性岩体与碳酸盐岩接触带,石榴子石-透辉石矽卡岩",
            "examples": ["大冶铁矿", "邯邢式铁矿", "莱芜铁矿"]
        },
        "VMS块状硫化物": {
            "gravity": "中等密度差异",
            "magnetic": "弱磁或无磁",
            "electromagnetic": "极强导电性,明显低阻高极化",
            "geology": "火山岩系,海底喷流沉积成因",
            "examples": ["白银厂", "红透山", "小西南岔"]
        },
        "造山型金矿": {
            "gravity": "密度差异不明显",
            "magnetic": "磁性较弱,断裂带显示低磁",
            "electromagnetic": "含硫化物时显示极化异常",
            "geology": "韧性剪切带,绿片岩相变质岩",
            "examples": ["焦家金矿", "玲珑金矿", "夹皮沟金矿"]
        },
        "卡林型金矿": {
            "gravity": "低密度含矿层",
            "magnetic": "弱磁性",
            "electromagnetic": "含砷黄铁矿时显示极化",
            "geology": "微细浸染型,碳酸盐岩或碎屑岩容矿",
            "examples": ["烂泥沟金矿", "水银洞金矿"]
        },
        "岩浆铜镍硫化物": {
            "gravity": "高密度矿体",
            "magnetic": "强磁性(含磁黄铁矿)",
            "electromagnetic": "强导电性强极化",
            "geology": "基性-超基性岩体,深部熔离成因",
            "examples": ["金川铜镍矿", "黄山铜镍矿", "喀拉通克"]
        }
    }

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        enable_rag: bool = True,
        embedding_type: str = "bge-m3",
    ):
        """Initialize mineral exploration agent.

        Args:
            ollama_client: Ollama client instance
            enable_rag: Enable RAG for literature-based analysis
            embedding_type: Type of embedding model
        """
        self.client = ollama_client or OllamaClient()
        self.conversation_history: List[Dict[str, Any]] = []

        # Initialize RAG if enabled
        self.rag_enabled = enable_rag
        if enable_rag:
            try:
                self.rag = RAGRetriever(
                    ollama_client=self.client,
                    embedding_type=embedding_type
                )
                logger.info(f"RAG module enabled for mineral exploration (embedding: {embedding_type})")
            except Exception as e:
                logger.warning(f"Failed to initialize RAG: {e}. Running without RAG.")
                self.rag_enabled = False
                self.rag = None

        # Data storage
        self.gravity_data: Optional[Dict[str, Any]] = None
        self.magnetic_data: Optional[Dict[str, Any]] = None
        self.em_data: Optional[Dict[str, Any]] = None
        self.well_log_data: Optional[Dict[str, Any]] = None
        self.geological_data: Optional[Dict[str, Any]] = None

    def load_gravity_data(self, data: Dict[str, Any]):
        """Load gravity survey data.

        Args:
            data: Gravity data dict with 'x', 'y', 'z', 'gravity_values', 'station_info'
        """
        self.gravity_data = data
        logger.info(f"Loaded gravity data: {len(data.get('gravity_values', []))} stations")

    def load_magnetic_data(self, data: Dict[str, Any]):
        """Load magnetic survey data.

        Args:
            data: Magnetic data dict with 'x', 'y', 'z', 'magnetic_values', 'survey_info'
        """
        self.magnetic_data = data
        logger.info(f"Loaded magnetic data: {len(data.get('magnetic_values', []))} stations")

    def load_em_data(self, data: Dict[str, Any]):
        """Load electromagnetic survey data.

        Args:
            data: EM data dict with 'x', 'y', 'resistivity', 'chargeability', 'frequency'
        """
        self.em_data = data
        logger.info(f"Loaded EM data: {len(data.get('resistivity', []))} soundings")

    def load_well_log_data(self, data: Dict[str, Any]):
        """Load well log data.

        Args:
            data: Well log data with 'depth', 'gr', 'sp', 'resistivity', 'density', 'neutron'
        """
        self.well_log_data = data
        logger.info(f"Loaded well log data: {len(data.get('depth', []))} depth points")

    def load_geological_data(self, data: Dict[str, Any]):
        """Load geological information.

        Args:
            data: Geological data with 'lithology', 'structure', 'alteration', 'mineralization'
        """
        self.geological_data = data
        logger.info("Loaded geological data")

    def identify_deposit_type(
        self,
        gravity_anomaly: Optional[str] = None,
        magnetic_anomaly: Optional[str] = None,
        em_response: Optional[str] = None,
        geological_features: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Identify ore deposit type based on multi-source data.

        Args:
            gravity_anomaly: Description of gravity anomaly
            magnetic_anomaly: Description of magnetic anomaly
            em_response: Description of EM response
            geological_features: Geological features description

        Returns:
            Deposit type identification result
        """
        # Build feature vector
        features = []

        if gravity_anomaly:
            features.append(f"重力异常: {gravity_anomaly}")
        if magnetic_anomaly:
            features.append(f"磁异常: {magnetic_anomaly}")
        if em_response:
            features.append(f"电磁响应: {em_response}")
        if geological_features:
            features.append(f"地质特征: {geological_features}")

        if not features:
            raise ValueError("At least one data source must be provided")

        # Use LLM for classification
        prompt = f"""根据以下地球物理和地质特征,识别可能的矿床类型:

{'; '.join(features)}

请参考以下常见矿床类型的地球物理特征:
"""
        for deposit_type, characteristics in self.DEPOSIT_TYPES.items():
            prompt += f"\n- {deposit_type}: 重力={characteristics['gravity']}, 磁力={characteristics['magnetic']}, 电磁={characteristics['electromagnetic']}"

        prompt += "\n\n请给出:\n1. 最可能的矿床类型\n2. 判断依据\n3. 典型实例对比\n4. 进一步工作建议"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat(messages)

        result = {
            "input_features": features,
            "analysis": response,
            "matched_types": self._match_deposit_types(gravity_anomaly, magnetic_anomaly, em_response)
        }

        return result

    def analyze_mineralization_elements(
        self,
        region_description: str,
        available_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Analyze metallogenic elements for ore formation.

        Args:
            region_description: Description of the study area
            available_data: Available data summary

        Returns:
            Metallogenic elements analysis
        """
        prompt = f"""请对以下地区进行成矿要素分析:

区域描述:
{region_description}

"""
        if available_data:
            prompt += "\n可用数据:\n"
            for key, value in available_data.items():
                prompt += f"- {key}: {value}\n"

        prompt += """
请从以下成矿要素进行分析:

1. **构造控矿要素**
   - 大地构造背景
   - 控矿构造类型(断裂、褶皱、接触带等)
   - 构造演化历史

2. **岩性岩相要素**
   - 容矿岩石类型
   - 岩相古地理
   - 有利岩性组合

3. **岩浆活动要素**
   - 成矿相关岩体
   - 岩浆演化序列
   - 侵位机制

4. **地层要素**
   - 赋矿层位
   - 地层时代
   - 岩性组合

5. **蚀变矿化要素**
   - 蚀变类型及分带
   - 矿化特征
   - 矿石矿物组合

6. **地球化学要素**
   - 元素异常特征
   - 指示元素组合
   - 原生晕分带

7. **地球物理要素**
   - 重磁电异常特征
   - 深部结构信息
   - 隐伏岩体定位

请提供详细的成矿要素分析报告。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        return self.client.chat(messages)

    def comprehensive_analysis(
        self,
        project_name: str,
        location: str,
        use_rag: bool = True,
    ) -> str:
        """Perform comprehensive mineral deposit analysis.

        Args:
            project_name: Project name
            location: Location description
            use_rag: Whether to use RAG for literature context

        Returns:
            Comprehensive analysis report
        """
        # Gather available data summary
        data_summary = {}
        if self.gravity_data:
            data_summary['重力数据'] = f"{len(self.gravity_data.get('gravity_values', []))}个测点"
        if self.magnetic_data:
            data_summary['磁法数据'] = f"{len(self.magnetic_data.get('magnetic_values', []))}个测点"
        if self.em_data:
            data_summary['电磁数据'] = f"{len(self.em_data.get('resistivity', []))}个测深点"
        if self.well_log_data:
            data_summary['测井数据'] = f"{len(self.well_log_data.get('depth', []))}个深度点"
        if self.geological_data:
            data_summary['地质资料'] = "已有"

        # Use RAG if available
        if self.rag_enabled and use_rag and self.rag:
            try:
                context = self.rag.get_context_for_query(
                    query=f"{project_name} {location} 矿床 成矿",
                    n_results=5
                )
            except Exception:
                context = "未检索到相关文献"
        else:
            context = "未使用文献检索"

        prompt = f"""# {project_name} 矿床综合分析报告

## 项目位置
{location}

## 可用数据
{chr(10).join([f'- {k}: {v}' for k, v in data_summary.items()])}

## 相关文献背景
{context}

## 分析要求

请基于上述数据和信息,生成一份完整的矿床分析报告,包括:

1. **区域地质背景**
   - 大地构造位置
   - 区域地层
   - 区域构造
   - 区域岩浆岩

2. **矿区地质特征**
   - 矿区地层
   - 矿区构造
   - 矿区岩浆岩
   - 围岩蚀变

3. **地球物理场特征**
   - 重力异常特征及解释
   - 磁异常特征及解释
   - 电磁异常特征及解释
   - 综合地球物理模型

4. **矿床地质特征**
   - 矿体形态产状
   - 矿石物质组成
   - 矿石结构构造
   - 矿化阶段划分

5. **矿床类型及成矿模式**
   - 矿床类型确定
   - 成矿时代
   - 成矿物质来源
   - 成矿流体特征
   - 成矿模式

6. **找矿标志**
   - 地质找矿标志
   - 地球物理找矿标志
   - 地球化学找矿标志
   - 遥感找矿标志

7. **资源潜力评价**
   - 已知资源量
   - 深部及外围预测
   - 找矿前景分析

8. **下一步工作建议**
   - 补充工作内容
   - 勘探工程布置
   - 技术方法选择

请提供专业、详细的分析报告。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        report = self.client.chat(messages, max_tokens=8192)

        self.conversation_history.extend(messages)
        self.conversation_history.append({"role": "assistant", "content": report})

        return report

    def _match_deposit_types(
        self,
        gravity: Optional[str],
        magnetic: Optional[str],
        em: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Match observed features with known deposit types.

        Args:
            gravity: Gravity anomaly description
            magnetic: Magnetic anomaly description
            em: EM response description

        Returns:
            List of matched deposit types with scores
        """
        matches = []

        for deposit_type, chars in self.DEPOSIT_TYPES.items():
            score = 0
            reasons = []

            # Simple keyword matching (can be enhanced with ML)
            if gravity:
                if any(kw in gravity for kw in ['高密度', '正异常']):
                    if '正异常' in chars['gravity'] or '高密度' in chars['gravity']:
                        score += 1
                        reasons.append("重力特征匹配")

            if magnetic:
                if any(kw in magnetic for kw in ['强磁', '高磁']):
                    if '强磁' in chars['magnetic'] or '高磁' in chars['magnetic']:
                        score += 1
                        reasons.append("磁法特征匹配")

            if em:
                if any(kw in em for kw in ['低阻', '高极化']):
                    if '低阻' in chars['electromagnetic'] or '高极化' in chars['electromagnetic']:
                        score += 1
                        reasons.append("电磁特征匹配")

            if score > 0:
                matches.append({
                    "deposit_type": deposit_type,
                    "score": score,
                    "reasons": reasons,
                    "examples": chars['examples']
                })

        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches

    def generate_exploration_report(
        self,
        title: str,
        analyses: List[Dict[str, str]],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Generate comprehensive exploration report.

        Args:
            title: Report title
            analyses: List of analysis sections
            output_path: Optional path to save report

        Returns:
            Report text
        """
        report = f"# {title}\n\n"
        report += f"**生成时间**: {self._get_timestamp()}\n\n"
        report += "---\n\n"

        for section in analyses:
            report += f"## {section['title']}\n\n"
            report += f"{section['content']}\n\n"

        report += "---\n\n"
        report += "**免责声明**: 本报告由AI辅助生成,仅供参考。实际勘探决策需结合实地调查和专业判断。\n"

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")

        return report

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
