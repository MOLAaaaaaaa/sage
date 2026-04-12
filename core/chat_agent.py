"""Unified chat agent for natural language interaction."""

from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from core.chat_router import ChatRouter
from utils.file_tools import FileSystemTool
from utils.nl_plotter import NaturalLanguagePlotter
from agents.geological_interpreter import GeologicalInterpreterAgent
from mineral.exploration_agent import MineralExplorationAgent


class ChatAgent:
    """Unified chat agent that routes commands to appropriate handlers."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        enable_rag: bool = True,
        embedding_type: str = "bge-m3",
    ):
        """Initialize chat agent.

        Args:
            base_dir: Base directory for file operations
            enable_rag: Enable RAG for geological analysis
            embedding_type: Embedding model type
        """
        self.base_dir = base_dir or Path.cwd()
        self.router = ChatRouter()
        self.file_tool = FileSystemTool(base_dir=self.base_dir)
        self.nl_plotter = NaturalLanguagePlotter(output_dir=self.base_dir / "output" / "plots")

        # Initialize geological agents
        try:
            from core.ollama_client import OllamaClient
            ollama_client = OllamaClient()

            self.geo_agent = GeologicalInterpreterAgent(
                ollama_client=ollama_client,
                enable_rag=enable_rag,
                embedding_type=embedding_type
            )

            self.mineral_agent = MineralExplorationAgent(
                ollama_client=ollama_client,
                enable_rag=enable_rag,
                embedding_type=embedding_type
            )

            self.agents_available = True
        except Exception as e:
            logger.warning(f"Geological agents not available: {e}")
            self.agents_available = False
            self.geo_agent = None
            self.mineral_agent = None

        logger.info("Chat agent initialized")

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process natural language command.

        Args:
            user_input: User's natural language input

        Returns:
            Response dict with result
        """
        try:
            # Detect intent
            intent = self.router.detect_intent(user_input)
            logger.info(f"Processing command: {user_input[:50]}... (intent: {intent})")

            # Extract parameters
            params = self.router.extract_parameters(user_input, intent)

            # Route to appropriate handler
            if intent == 'list_files':
                return self._handle_list_files(params)
            elif intent == 'plot_data':
                return self._handle_plot_data(user_input, params)
            elif intent == 'analyze_region':
                return self._handle_region_analysis(user_input, params)
            elif intent == 'search_literature':
                return self._handle_literature_search(user_input, params)
            elif intent == 'identify_deposit':
                return self._handle_deposit_identification(user_input, params)
            else:
                return self._handle_general_chat(user_input)

        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f'处理失败: {e}'
            }

    def _handle_list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file listing command.

        Args:
            params: Extracted parameters

        Returns:
            Response
        """
        directory = params.get('directory', '.')
        pattern = params.get('pattern', '*')

        result = self.file_tool.list_files(
            directory=directory,
            pattern=pattern
        )

        if result['success']:
            # Format response
            response = f"📁 目录 {result['directory']} 下的文件:\n\n"

            if result['total_files'] == 0:
                response += "  (空目录)"
            else:
                for i, file_info in enumerate(result['files'], 1):
                    response += f"{i}. 📄 {file_info['name']}\n"
                    response += f"   大小: {file_info['size']} | 修改: {file_info['modified']}\n"

                if result['truncated']:
                    response += f"\n... (仅显示前{len(result['files'])}个文件)"

            response += f"\n\n总计: {result['total_files']} 个文件"

            return {
                'success': True,
                'intent': 'list_files',
                'data': result,
                'response': response
            }
        else:
            return {
                'success': False,
                'intent': 'list_files',
                'error': result['error'],
                'response': f"❌ 错误: {result['error']}"
            }

    def _handle_plot_data(
        self,
        user_input: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle plotting command.

        Args:
            user_input: Original user input
            params: Extracted parameters

        Returns:
            Response
        """
        data_file = params.get('data_file')

        result = self.nl_plotter.plot_from_command(
            command=user_input,
            data_file=data_file
        )

        if result['success']:
            return {
                'success': True,
                'intent': 'plot_data',
                'data': result,
                'response': f"✅ {result['message']}"
            }
        else:
            return {
                'success': False,
                'intent': 'plot_data',
                'error': result['error'],
                'response': f"❌ 绘图失败: {result['error']}"
            }

    def _handle_region_analysis(
        self,
        user_input: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle region analysis command.

        Args:
            user_input: User input
            params: Parameters

        Returns:
            Response
        """
        if not self.agents_available or not self.geo_agent:
            return {
                'success': False,
                'intent': 'analyze_region',
                'error': 'Geological agent not available',
                'response': '❌ 地质分析功能不可用,请检查Ollama连接'
            }

        # Extract region name from input
        import re
        match = re.search(r'分析\s*([^\s,，]+)', user_input)
        region_name = match.group(1) if match else "未知地区"

        try:
            result = self.geo_agent.analyze_region(
                region_name=region_name,
                use_rag=True
            )

            return {
                'success': True,
                'intent': 'analyze_region',
                'data': {'analysis': result},
                'response': result
            }
        except Exception as e:
            return {
                'success': False,
                'intent': 'analyze_region',
                'error': str(e),
                'response': f'❌ 分析失败: {e}'
            }

    def _handle_literature_search(
        self,
        user_input: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle literature search.

        Args:
            user_input: User input
            params: Parameters

        Returns:
            Response
        """
        if not self.agents_available or not self.geo_agent or not self.geo_agent.rag_enabled:
            return {
                'success': False,
                'intent': 'search_literature',
                'error': 'RAG not available',
                'response': '❌ 文献检索功能不可用'
            }

        # Extract search query
        import re
        match = re.search(r'搜索\s*(.+?)(?:\s*$)', user_input)
        query = match.group(1) if match else user_input

        try:
            results = self.geo_agent.search_literature(query, n_results=5)

            if not results:
                response = "未找到相关文献"
            else:
                response = f"📚 找到 {len(results)} 条相关文献:\n\n"
                for i, result in enumerate(results, 1):
                    meta = result['metadata']
                    response += f"{i}. **{meta.get('title', '未知')}**\n"
                    response += f"   作者: {meta.get('author', '未知')}\n"
                    response += f"   内容: {result['content'][:200]}...\n\n"

            return {
                'success': True,
                'intent': 'search_literature',
                'data': {'results': results},
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'intent': 'search_literature',
                'error': str(e),
                'response': f'❌ 检索失败: {e}'
            }

    def _handle_deposit_identification(
        self,
        user_input: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle deposit type identification.

        Args:
            user_input: User input
            params: Parameters

        Returns:
            Response
        """
        if not self.agents_available or not self.mineral_agent:
            return {
                'success': False,
                'intent': 'identify_deposit',
                'error': 'Mineral agent not available',
                'response': '❌ 矿床识别功能不可用'
            }

        try:
            # This is a simplified version - in practice would extract features
            response = self.mineral_agent.analyze_mineralization_elements(
                region_description=user_input
            )

            return {
                'success': True,
                'intent': 'identify_deposit',
                'data': {'analysis': response},
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'intent': 'identify_deposit',
                'error': str(e),
                'response': f'❌ 识别失败: {e}'
            }

    def _handle_general_chat(self, user_input: str) -> Dict[str, Any]:
        """Handle general chat message.

        Args:
            user_input: User input

        Returns:
            Response
        """
        if not self.agents_available or not self.geo_agent:
            return {
                'success': False,
                'intent': 'general_chat',
                'error': 'LLM not available',
                'response': '❌ AI对话功能不可用,请检查Ollama连接'
            }

        try:
            messages = [
                {"role": "system", "content": "你是地质解释Agent助手,可以帮助用户进行地质数据分析、文件管理和绘图等操作。"},
                {"role": "user", "content": user_input}
            ]

            response = self.geo_agent.client.chat(messages)

            return {
                'success': True,
                'intent': 'general_chat',
                'data': {'response': response},
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'intent': 'general_chat',
                'error': str(e),
                'response': f'❌ 对话失败: {e}'
            }
