"""Geological interpretation agent for analyzing velocity structures and regional data."""

from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import json
from loguru import logger

from core.ollama_client import OllamaClient
from utils.rag_retriever import RAGRetriever


class GeologicalInterpreterAgent:
    """Agent for interpreting geological data including velocity structures."""

    SYSTEM_PROMPT = """你是一位专业的地球物理学家和地质解释专家。你的任务是分析给定的地质数据、速度结构图、区域信息等,并提供专业的地质解释。

你需要关注以下方面:
1. 速度结构分析:识别不同深度的速度层,解释其地质意义
2. 构造特征:识别断层、褶皱、不整合面等构造特征
3. 岩性推断:根据速度值推断可能的岩性组合
4. 地质演化:基于结构特征推测区域的地质演化历史
5. 资源潜力:评估该区域的油气、矿产等资源潜力

请提供详细、专业的分析结果,使用地质学专业术语,并给出合理的解释和建议。"""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        enable_rag: bool = True,
        embedding_type: str = "bge-m3",
    ):
        """Initialize the geological interpreter agent.

        Args:
            ollama_client: Ollama client instance (creates new one if not provided)
            enable_rag: Whether to enable RAG for literature-based analysis
            embedding_type: Type of embedding model ('bge-m3' or 'ollama')
        """
        self.client = ollama_client or OllamaClient()
        self.conversation_history: List[Dict[str, Any]] = []
        self.embedding_type = embedding_type

        # Initialize RAG if enabled
        self.rag_enabled = enable_rag
        if enable_rag:
            try:
                self.rag = RAGRetriever(
                    ollama_client=self.client,
                    embedding_type=embedding_type
                )
                logger.info(f"RAG module enabled (embedding: {embedding_type})")
            except Exception as e:
                logger.warning(f"Failed to initialize RAG: {e}. Running without RAG.")
                self.rag_enabled = False
                self.rag = None

    def analyze_region(
        self,
        region_name: str,
        description: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        use_rag: bool = True,
    ) -> str:
        """Analyze geological information for a given region.

        Args:
            region_name: Name of the region to analyze
            description: Additional description or context
            additional_data: Additional geological data
            use_rag: Whether to use RAG for literature-based analysis

        Returns:
            Analysis result text
        """
        # Use RAG if available and enabled
        if self.rag_enabled and use_rag and self.rag:
            try:
                logger.info(f"Using RAG for region analysis: {region_name}")
                response = self.rag.analyze_region_with_rag(
                    region_name=region_name,
                    description=description,
                )

                self.conversation_history.append({
                    "role": "user",
                    "content": f"Analyze region with RAG: {region_name}"
                })
                self.conversation_history.append({"role": "assistant", "content": response})

                return response
            except Exception as e:
                logger.warning(f"RAG analysis failed: {e}. Falling back to standard analysis.")

        # Fallback to standard analysis
        prompt = f"请对以下地区进行地质解释分析:\n\n地区名称: {region_name}"

        if description:
            prompt += f"\n\n描述信息:\n{description}"

        if additional_data:
            prompt += "\n\n附加数据:\n"
            for key, value in additional_data.items():
                prompt += f"- {key}: {value}\n"

        prompt += "\n\n请提供详细的地质解释,包括构造特征、地层划分、岩性推断等内容。"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        logger.info(f"Analyzing region: {region_name}")
        response = self.client.chat(messages)

        self.conversation_history.extend(messages)
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def analyze_velocity_structure(
        self,
        structure_description: str,
        image_path: Optional[Union[str, Path]] = None,
        depth_range: Optional[tuple] = None,
        velocity_data: Optional[List[Dict[str, float]]] = None,
    ) -> str:
        """Analyze velocity structure data.

        Args:
            structure_description: Text description of the velocity structure
            image_path: Path to velocity structure image
            depth_range: Depth range tuple (min_depth, max_depth) in km
            velocity_data: Velocity data points with depth

        Returns:
            Analysis result text
        """
        # Build comprehensive prompt
        prompt = "请分析以下速度结构数据:\n\n"

        if structure_description:
            prompt += f"结构描述:\n{structure_description}\n\n"

        if depth_range:
            prompt += f"深度范围: {depth_range[0]} - {depth_range[1]} km\n\n"

        if velocity_data:
            prompt += "速度数据点:\n"
            for point in velocity_data[:20]:  # Limit to first 20 points
                prompt += f"  深度: {point.get('depth', 'N/A')} km, 速度: {point.get('velocity', 'N/A')} km/s\n"
            if len(velocity_data) > 20:
                prompt += f"  ... (共 {len(velocity_data)} 个数据点)\n"
            prompt += "\n"

        prompt += """请从以下方面进行分析:
1. 速度分层特征及各层的地质意义
2. 可能的岩性组合
3. 构造背景分析
4. 与典型地质模型的对比
5. 对该区域地质演化的指示意义"""

        # If image is provided, use vision capability
        if image_path:
            logger.info(f"Analyzing velocity structure with image: {image_path}")
            try:
                response = self.client.chat_with_image(
                    prompt=prompt,
                    image_path=image_path,
                )
            except Exception as e:
                logger.warning(f"Vision analysis failed: {e}. Falling back to text-only analysis.")
                response = self._text_analysis(prompt)
        else:
            response = self._text_analysis(prompt)

        return response

    def _text_analysis(self, prompt: str) -> str:
        """Perform text-only analysis.

        Args:
            prompt: Analysis prompt

        Returns:
            Analysis result
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        return self.client.chat(messages)

    def interpret_seismic_section(
        self,
        section_image: Union[str, Path],
        location_info: Optional[str] = None,
        processing_info: Optional[str] = None,
    ) -> str:
        """Interpret a seismic section image.

        Args:
            section_image: Path to seismic section image
            location_info: Location information
            processing_info: Seismic processing information

        Returns:
            Interpretation result
        """
        prompt = f"""请解释以下地震剖面图像:

位置信息: {location_info or '未提供'}
处理信息: {processing_info or '未提供'}

请识别并解释:
1. 主要反射层及其地质含义
2. 断层系统和构造样式
3. 沉积相和地层单元
4. 不整合面和关键层位
5. 潜在的储层和盖层组合"""

        logger.info(f"Interpreting seismic section: {section_image}")
        try:
            response = self.client.chat_with_image(
                prompt=prompt,
                image_path=section_image,
            )
        except Exception as e:
            logger.error(f"Seismic interpretation failed: {e}")
            raise

        return response

    def compare_regions(
        self,
        regions: List[Dict[str, Any]],
    ) -> str:
        """Compare geological characteristics of multiple regions.

        Args:
            regions: List of region data dicts with 'name' and 'description'

        Returns:
            Comparative analysis
        """
        prompt = "请对比分析以下地区的地质特征:\n\n"

        for i, region in enumerate(regions, 1):
            prompt += f"地区 {i}: {region['name']}\n"
            if 'description' in region:
                prompt += f"{region['description']}\n"
            prompt += "\n"

        prompt += """请从以下方面进行对比:
1. 构造背景和大地构造位置
2. 地层发育特征
3. 速度结构差异
4. 资源潜力对比
5. 勘探开发建议"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        return self.client.chat(messages)

    def generate_report(
        self,
        title: str,
        analyses: List[Dict[str, str]],
    ) -> str:
        """Generate a comprehensive geological interpretation report.

        Args:
            title: Report title
            analyses: List of analysis results with 'type' and 'content'

        Returns:
            Formatted report
        """
        report = f"# {title}\n\n"
        report += f"生成时间: {self._get_timestamp()}\n\n"
        report += "---\n\n"

        for analysis in analyses:
            report += f"## {analysis['type']}\n\n"
            report += f"{analysis['content']}\n\n"

        report += "---\n\n"
        report += "**注**: 本报告由AI地质解释助手生成,仅供参考。实际地质工作需结合实地调查和专业判断。"

        return report

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    # RAG Management Methods
    def upload_pdf_to_rag(self, pdf_path: Union[str, Path], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload PDF to RAG knowledge base.

        Args:
            pdf_path: Path to PDF file
            doc_id: Custom document ID

        Returns:
            Upload result
        """
        if not self.rag_enabled or not self.rag:
            raise RuntimeError("RAG is not enabled")

        pdf_path = Path(pdf_path)
        return self.rag.upload_pdf(pdf_path, doc_id)

    def search_literature(
        self,
        query: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search geological literature.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            List of relevant passages
        """
        if not self.rag_enabled or not self.rag:
            raise RuntimeError("RAG is not enabled")

        return self.rag.search_literature(query, n_results)

    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG database statistics.

        Returns:
            Statistics dict
        """
        if not self.rag_enabled or not self.rag:
            raise RuntimeError("RAG is not enabled")

        return self.rag.get_database_stats()

    def list_rag_documents(self) -> List[Dict[str, Any]]:
        """List all documents in RAG database.

        Returns:
            List of document info
        """
        if not self.rag_enabled or not self.rag:
            raise RuntimeError("RAG is not enabled")

        return self.rag.list_documents()

    def delete_rag_document(self, doc_id: str) -> bool:
        """Delete a document from RAG database.

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        if not self.rag_enabled or not self.rag:
            raise RuntimeError("RAG is not enabled")

        return self.rag.delete_document(doc_id)
