"""Intelligent chat router for natural language commands."""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger


class ChatRouter:
    """Route natural language commands to appropriate functions."""

    def __init__(self):
        """Initialize chat router."""
        self.command_patterns = {
            'list_files': [
                r'列出.*文件',
                r'查看.*目录',
                r'显示.*文件',
                r'有哪些文件',
                r'目录下.*什么',
                r'list.*files',
                r'show.*files',
                r'what.*files',
            ],
            'plot_data': [
                r'绘制',
                r'画图',
                r'作图',
                r'plot',
                r'graph',
                r'chart',
                r'可视化',
            ],
            'analyze_region': [
                r'分析.*地区',
                r'地质解释',
                r'区域分析',
                r'analyze.*region',
            ],
            'search_literature': [
                r'搜索.*文献',
                r'查找.*资料',
                r'search.*literature',
            ],
            'identify_deposit': [
                r'识别.*矿床',
                r'矿床类型',
                r'deposit.*type',
            ],
        }

    def detect_intent(self, user_input: str) -> str:
        """Detect user intent from input.

        Args:
            user_input: User's natural language input

        Returns:
            Detected intent (command type)
        """
        user_input_lower = user_input.lower()

        for intent, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    logger.info(f"Detected intent: {intent}")
                    return intent

        # Default to general chat
        return 'general_chat'

    def extract_parameters(self, user_input: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from user input based on intent.

        Args:
            user_input: User's input
            intent: Detected intent

        Returns:
            Extracted parameters
        """
        params = {}

        if intent == 'list_files':
            # Extract directory path - improved pattern
            dir_patterns = [
                r'(?:在|从)\s*([^\s]+?)\s*(?:目录|文件夹)',  # 在XX目录
                r'(?:查看|列出)\s*([^\s]+?)\s*(?:目录|文件夹)',  # 列出XX目录
                r'([a-zA-Z0-9_./-]+)\s*(?:dir|folder)',  # English patterns
            ]

            params['directory'] = '.'
            for pattern in dir_patterns:
                dir_match = re.search(pattern, user_input)
                if dir_match:
                    params['directory'] = dir_match.group(1).strip()
                    break

            # Check for "当前目录" or "current directory"
            if '当前' in user_input or 'current' in user_input.lower():
                params['directory'] = '.'

            # Check for file pattern
            ext_match = re.search(r'(\.\w+)\s*文件', user_input)
            if ext_match:
                params['pattern'] = f'*{ext_match.group(1)}'
            elif 'markdown' in user_input.lower() or 'md' in user_input.lower():
                params['pattern'] = '*.md'
            elif 'pdf' in user_input.lower():
                params['pattern'] = '*.pdf'
            elif 'python' in user_input.lower() or 'py' in user_input.lower():
                params['pattern'] = '*.py'
            else:
                params['pattern'] = '*'

        elif intent == 'plot_data':
            # Extract file name
            file_match = re.search(r'([^\s]+\.(?:csv|txt|dat|npy|npz))', user_input)
            if file_match:
                params['data_file'] = file_match.group(1)

            # Extract plot type
            if '速度' in user_input or 'velocity' in user_input.lower():
                params['plot_type'] = 'velocity'
            elif '重力' in user_input or 'gravity' in user_input.lower():
                params['plot_type'] = 'gravity'
            elif '磁' in user_input or 'magnetic' in user_input.lower():
                params['plot_type'] = 'magnetic'
            else:
                params['plot_type'] = 'auto'

        return params
