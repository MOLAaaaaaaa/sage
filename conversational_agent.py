#!/usr/bin/env python3
"""
SeismicX Conversational Agent

An intelligent dialogue system that allows users to control seismic analysis
skills through natural language conversation. Supports multi-turn interactions,
context awareness, and automatic skill routing.

Usage:
    python conversational_agent.py  # Interactive mode
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Optional imports for waveform visualization
try:
    import obspy
    HAS_OBSPY = True
except ImportError:
    HAS_OBSPY = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ConversationContext:
    """Maintains context across multiple conversation turns"""

    def __init__(self):
        self.current_task: Optional[str] = None  # Current ongoing task
        self.task_state: Dict = {}  # Task-specific state
        self.last_results: Dict = {}  # Results from last operation
        self.user_preferences: Dict = {}  # User's preferred settings
        self.conversation_history: List[Dict] = []  # Full conversation log

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def get_recent_context(self, n_turns: int = 5) -> str:
        """Get recent conversation context for LLM"""
        messages = self.conversation_history[-n_turns * 2:]  # Last n turns
        context = ""
        for msg in messages:
            role_label = "User" if msg['role'] == 'user' else "Assistant"
            context += f"{role_label}: {msg['content']}\n"
        return context


class IntentClassifier:
    """Classifies user intent from natural language input"""

    def __init__(self):
        # Intent patterns with keywords
        self.intent_patterns = {
            'phase_picking': {
                'keywords': ['拾取', 'pick', '相位', '震相', 'phase'],
                'patterns': [
                    r'拾取.*震相',
                    r'detect.*phase',
                    r'pick.*phase',
                    r'检测.*震相',
                    r'检测.*Pg',
                    r'检测.*Sg',
                    r'检测.*相位',
                ]
            },
            'phase_association': {
                'keywords': ['关联', 'association', 'associate', '定位', 'locate', 'event'],
                'patterns': [
                    r'关联.*震相',
                    r'associate.*phase',
                    r'定位.*地震',
                    r'locate.*event',
                ]
            },
            'polarity_analysis': {
                'keywords': ['极性', 'polarity', '初动', 'first motion', 'focal'],
                'patterns': [
                    r'分析.*极性',
                    r'analyze.*polarity',
                    r'初动.*方向',
                ]
            },
            'status_check': {
                'keywords': ['状态', 'status', '进度', 'progress', '完成', 'done'],
                'patterns': [
                    r'处理.*完成',
                    r'is.*ready',
                    r'状态.*如何',
                ]
            },
            'help': {
                'keywords': ['帮助', 'help', '怎么用', 'how to', '可以做什么'],
                'patterns': [
                    r'怎么.*拾取',
                    r'how.*pick',
                    r'能.*什么',
                ]
            },
            'configure': {
                'keywords': ['配置', 'config', '设置', 'set', 'change', '修改'],
                'patterns': [
                    r'设置.*模型',
                    r'configure.*model',
                    r'修改.*参数',
                ]
            },
            'data_browsing': {
                'keywords': ['查看', '浏览', 'list', 'browse', 'find', '查找', '目录', '文件夹', '看下', '看看', '显示', '有哪些'],
                'patterns': [
                    r'查看.*目录',
                    r'browse.*directory',
                    r'list.*files',
                    r'有哪些.*文件',
                    r'目录下.*什么',
                    r'看下.*文件夹',
                    r'看看.*目录',
                    r'显示.*数据',
                ]
            },
            'waveform_plotting': {
                'keywords': ['绘制', 'plot', 'draw', '显示波形', 'waveform', '波形图', '画', '可视化'],
                'patterns': [
                    r'绘制.*波形',
                    r'plot.*waveform',
                    r'显示.*mseed',
                    r'画.*图',
                    r'可视化.*数据',
                    r'画一下.*文件',
                ]
            }
        }

    def classify(self, user_input: str) -> Dict:
        """
        Classify user intent
        Returns: {intent: str, confidence: float, entities: dict}
        """
        user_input_lower = user_input.lower()
        scores = {}

        for intent, config in self.intent_patterns.items():
            score = 0

            # Keyword matching
            for keyword in config['keywords']:
                if keyword.lower() in user_input_lower:
                    score += 1

            # Pattern matching
            for pattern in config['patterns']:
                if re.search(pattern, user_input_lower):
                    score += 2

            scores[intent] = score

        # Get best intent
        if not scores or max(scores.values()) == 0:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {}
            }

        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 5.0, 1.0)  # Normalize to 0-1

        # Extract entities
        entities = self._extract_entities(user_input)

        return {
            'intent': best_intent,
            'confidence': confidence,
            'entities': entities
        }

    def _extract_entities(self, text: str) -> Dict:
        """Extract entities like file paths, model names, etc."""
        entities = {}

        # Extract file paths
        path_pattern = r'(/[^\s]+|\.\/[^\s]+)'
        paths = re.findall(path_pattern, text)
        if paths:
            entities['file_paths'] = paths

        # Extract model names
        model_patterns = [
            r'(pnsn\.v[\d.]+)',
            r'(phasenet)',
            r'(eqtransformer)',
            r'(llama[\d.]+)',
            r'(gpt-[\d.]+)',
        ]
        for pattern in model_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['model'] = match.group(1)
                break

        # Extract numbers (thresholds, counts, etc.)
        numbers = re.findall(r'(\d+\.?\d*)', text)
        if numbers:
            entities['numbers'] = [float(n) for n in numbers]

        return entities


class SkillExecutor:
    """Executes seismic analysis skills based on intent"""

    def __init__(self):
        self.available_skills = {
            'phase_picking': {
                'name': 'seismic-phase-picker',
                'description': 'Detect seismic phases from waveform data',
                'parameters': ['input_dir', 'output', 'model', 'device']
            },
            'phase_association': {
                'name': 'seismic-phase-associator',
                'description': 'Associate phase picks into earthquake events',
                'parameters': ['input_file', 'station_file', 'output', 'method']
            },
            'polarity_analysis': {
                'name': 'seismic-polarity-analyzer',
                'description': 'Analyze first-motion polarity of P-waves',
                'parameters': ['input_file', 'waveform_dir', 'output']
            },
            'data_browsing': {
                'name': 'waveform-visualizer',
                'description': 'Browse directories for seismic data files',
                'parameters': ['directory', 'file_type']
            },
            'waveform_plotting': {
                'name': 'waveform-visualizer',
                'description': 'Plot seismic waveform data',
                'parameters': ['file_path', 'output', 'filter', 'time_window']
            }
        }

    def execute(self, intent: str, entities: Dict, context: ConversationContext) -> Dict:
        """
        Execute the appropriate skill
        Returns: {success: bool, message: str, results: dict}
        """
        if intent == 'phase_picking':
            return self._execute_phase_picking(entities, context)
        elif intent == 'phase_association':
            return self._execute_phase_association(entities, context)
        elif intent == 'polarity_analysis':
            return self._execute_polarity_analysis(entities, context)
        elif intent == 'data_browsing':
            return self._execute_data_browsing(entities, context)
        elif intent == 'waveform_plotting':
            return self._execute_waveform_plotting(entities, context)
        else:
            return {
                'success': False,
                'message': f'Unknown intent: {intent}',
                'results': {}
            }

    def _execute_phase_picking(self, entities: Dict, context: ConversationContext) -> Dict:
        """Execute phase picking skill"""
        # Check if we have required parameters
        if 'file_paths' not in entities:
            return {
                'success': False,
                'message': '我需要知道波形文件的路径。请提供包含波形文件的目录路径。',
                'needs_info': ['input_directory'],
                'results': {}
            }

        input_dir = entities['file_paths'][0]
        output = entities.get('output', f'results/picks_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        model = entities.get('model', 'pnsn/pickers/pnsn.v3.jit')

        # Build command
        cmd = f"python pnsn/picker.py -i {input_dir} -o {output} -m {model}"

        # Store in context for follow-up questions
        context.current_task = 'phase_picking'
        context.task_state = {
            'input_dir': input_dir,
            'output': output,
            'model': model,
            'command': cmd
        }

        return {
            'success': True,
            'message': f'开始震相检测...\n输入目录: {input_dir}\n模型: {model}\n输出: {output}.txt',
            'action': 'execute_command',
            'command': cmd,
            'results': {'output_file': f'{output}.txt'}
        }

    def _execute_phase_association(self, entities: Dict, context: ConversationContext) -> Dict:
        """Execute phase association skill"""
        # Try to use previous pick results if available
        if 'input_file' not in entities:
            if context.last_results.get('picks_file'):
                input_file = context.last_results['picks_file']
            else:
                return {
                    'success': False,
                    'message': '我需要震相拾取文件的路径。您刚完成了拾取吗？或者请提供拾取文件路径。',
                    'needs_info': ['input_file', 'station_file'],
                    'results': {}
                }
        else:
            input_file = entities['input_file']

        if 'station_file' not in entities:
            return {
                'success': False,
                'message': '我需要台站文件的路径。请提供包含台站信息的文件路径。',
                'needs_info': ['station_file'],
                'results': {}
            }

        station_file = entities['station_file']
        output = entities.get('output', f'results/events_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        method = entities.get('method', 'fastlink')

        cmd = f"python pnsn/{method}er.py -i {input_file} -o {output} -s {station_file}"

        context.current_task = 'phase_association'
        context.task_state = {
            'input_file': input_file,
            'station_file': station_file,
            'output': output,
            'method': method,
            'command': cmd
        }

        return {
            'success': True,
            'message': f'开始震相关联...\n拾取文件: {input_file}\n台站文件: {station_file}\n方法: {method}',
            'action': 'execute_command',
            'command': cmd,
            'results': {'output_file': output}
        }

    def _execute_polarity_analysis(self, entities: Dict, context: ConversationContext) -> Dict:
        """Execute polarity analysis skill"""
        if 'input_file' not in entities:
            if context.last_results.get('picks_file'):
                input_file = context.last_results['picks_file']
            else:
                return {
                    'success': False,
                    'message': '我需要震相拾取文件路径。',
                    'needs_info': ['input_file', 'waveform_dir'],
                    'results': {}
                }
        else:
            input_file = entities['input_file']

        if 'waveform_dir' not in entities and 'file_paths' in entities:
            waveform_dir = entities['file_paths'][0]
        elif 'waveform_dir' not in entities:
            return {
                'success': False,
                'message': '我需要波形文件目录路径。',
                'needs_info': ['waveform_dir'],
                'results': {}
            }
        else:
            waveform_dir = entities['waveform_dir']

        output = f'results/polarity_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

        cmd = f"python seismic_cli.py polarity -i {input_file} -w {waveform_dir} -o {output}"

        return {
            'success': True,
            'message': f'开始初动极性分析...\n拾取文件: {input_file}\n波形目录: {waveform_dir}',
            'action': 'execute_command',
            'command': cmd,
            'results': {'output_file': output}
        }

    def _execute_data_browsing(self, entities: Dict, context: ConversationContext) -> Dict:
        """Execute data browsing - scan directory for seismic data files"""
        if 'file_paths' not in entities:
            return {
                'success': False,
                'message': '请提供要浏览的目录路径。例如："查看 /path/to/data 目录下的文件"',
                'needs_info': ['directory'],
                'results': {}
            }

        directory = entities['file_paths'][0]

        # Check if directory exists
        if not os.path.exists(directory):
            return {
                'success': False,
                'message': f'目录不存在: {directory}\n请检查路径是否正确。',
                'results': {}
            }

        if not os.path.isdir(directory):
            return {
                'success': False,
                'message': f'路径不是目录: {directory}\n请提供目录路径而不是文件路径。',
                'results': {}
            }

        # Scan for seismic data files
        supported_extensions = ['.mseed', '.sac', '.seed', '.miniseed']
        data_files = []

        try:
            for ext in supported_extensions:
                for file_path in Path(directory).rglob(f'*{ext}'):
                    data_files.append(file_path)

            # Also check uppercase extensions
            for ext in ['.MSEED', '.SAC', '.SEED']:
                for file_path in Path(directory).rglob(f'*{ext}'):
                    data_files.append(file_path)

            data_files = sorted(set(data_files))  # Remove duplicates and sort

        except Exception as e:
            return {
                'success': False,
                'message': f'扫描目录时出错: {e}',
                'results': {}
            }

        if not data_files:
            return {
                'success': True,
                'message': f'在目录 {directory} 中未找到地震数据文件。\n支持的格式: {", ".join(supported_extensions)}',
                'results': {'files': [], 'count': 0}
            }

        # Format file list for display
        file_list = []
        for i, file_path in enumerate(data_files[:20], 1):  # Limit to first 20 files
            size_mb = file_path.stat().st_size / (1024 * 1024)
            file_list.append(f"{i}. {file_path.name} ({size_mb:.1f} MB)")

        if len(data_files) > 20:
            file_list.append(f"... 还有 {len(data_files) - 20} 个文件")

        message = f"在目录 {directory} 中找到 {len(data_files)} 个地震数据文件:\n\n"
        message += "\n".join(file_list)
        message += f"\n\n您可以对我说 '绘制第1个文件' 或 '绘制 {data_files[0].name}' 来查看波形。"

        # Store results in context for follow-up
        context.last_results['browse_directory'] = directory
        context.last_results['browse_files'] = [str(f) for f in data_files]

        return {
            'success': True,
            'message': message,
            'action': 'display_files',
            'results': {
                'files': [str(f) for f in data_files],
                'count': len(data_files),
                'directory': directory
            }
        }

    def _execute_waveform_plotting(self, entities: Dict, context: ConversationContext) -> Dict:
        """Execute waveform plotting using ObsPy and matplotlib"""
        if not HAS_OBSPY:
            return {
                'success': False,
                'message': '未安装 ObsPy 库。请运行 "pip install obspy" 来安装。',
                'results': {}
            }

        if not HAS_MATPLOTLIB:
            return {
                'success': False,
                'message': '未安装 matplotlib 库。请运行 "pip install matplotlib" 来安装。',
                'results': {}
            }

        # Determine which file to plot
        file_path = None

        # Check if user specified a file index from previous browse
        if 'numbers' in entities and context.last_results.get('browse_files'):
            idx = int(entities['numbers'][0]) - 1
            browse_files = context.last_results['browse_files']
            if 0 <= idx < len(browse_files):
                file_path = browse_files[idx]

        # Check if file path is directly provided
        if not file_path and 'file_paths' in entities:
            file_path = entities['file_paths'][0]

        # Use last browsed file if available
        if not file_path and context.last_results.get('last_plotted_file'):
            file_path = context.last_results['last_plotted_file']

        if not file_path:
            return {
                'success': False,
                'message': '请指定要绘制的文件。例如：\n- "绘制 /path/to/file.mseed"\n- 或者先使用 "查看 /path/to/data" 浏览文件',
                'needs_info': ['file_path'],
                'results': {}
            }

        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': f'文件不存在: {file_path}',
                'results': {}
            }

        # Generate output path
        output_dir = entities.get('output', 'results/waveforms')
        os.makedirs(output_dir, exist_ok=True)

        file_name = Path(file_path).stem
        output_image = f"{output_dir}/{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        # Plot the waveform
        try:
            image_path = self._plot_waveform_internal(file_path, output_image, entities)

            return {
                'success': True,
                'message': f'✓ 波形图已生成!\n\n文件: {Path(file_path).name}\n输出: {image_path}\n\n图片已保存到 {output_dir} 目录。',
                'action': 'display_plot',
                'results': {
                    'image_path': image_path,
                    'source_file': file_path
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'绘制波形时出错: {e}\n\n请确保文件格式正确且可读。',
                'results': {}
            }

    def _plot_waveform_internal(self, file_path: str, output_image: str, entities: Dict) -> str:
        """Internal method to plot waveform using ObsPy and matplotlib"""
        # Read the data
        st = obspy.read(file_path)

        if len(st) == 0:
            raise ValueError("文件中没有数据道")

        # Create figure
        n_traces = len(st)
        fig_height = max(3, n_traces * 2.5)
        fig, axes = plt.subplots(n_traces, 1, figsize=(12, fig_height), sharex=True)

        if n_traces == 1:
            axes = [axes]

        # Normalize traces for better visualization
        for i, tr in enumerate(st):
            data = tr.data
            if len(data) > 0:
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val  # Normalize to [-1, 1]

            # Plot
            times = np.arange(len(tr.data)) / tr.stats.sampling_rate
            axes[i].plot(times, data, 'b-', linewidth=0.8)
            axes[i].set_ylabel(f'{tr.stats.network}.{tr.stats.station}\n{tr.stats.channel}',
                              fontsize=9)
            axes[i].grid(True, alpha=0.3)
            axes[i].axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)

        # Set x-axis label
        axes[-1].set_xlabel('Time (seconds)', fontsize=10)

        # Title
        start_time = st[0].stats.starttime
        fig.suptitle(f'Seismic Waveform\n{Path(file_path).name}\nStart: {start_time.strftime("%Y-%m-%d %H:%M:%S")}',
                    fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_image, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return output_image



class ResponseGenerator:
    """Generates natural language responses"""

    def __init__(self):
        self.templates = {
            'greeting': [
                "您好！我是SeismicX智能助手。我可以帮助您进行地震数据分析，包括震相检测、震相关联、初动极性分析和波形可视化。请问有什么可以帮您的？",
                "欢迎使用SeismicX！我可以帮您处理地震数据。您可以告诉我想要做什么，比如'查看目录'、'绘制波形'、'拾取震相'或'关联地震事件'。",
            ],
            'help': [
                "我可以帮您完成以下任务：\n\n1. **数据浏览** - 查看目录中的地震数据文件\n   例如：'帮我查看 /data/waveforms 目录下有哪些mseed文件'\n\n2. **波形绘制** - 绘制地震波形图\n   例如：'绘制 /path/to/file.mseed 的波形'\n\n3. **震相检测** - 从波形文件中检测Pg/Sg/Pn/Sn震相\n   例如：'帮我拾取/data/waveforms目录下的震相'\n\n4. **震相关联** - 将震相拾取关联为地震事件\n   例如：'关联刚才的拾取结果'\n\n5. **初动极性分析** - 分析P波初动方向\n   例如：'分析极性'\n\n请告诉我您想做什么？",
            ],
            'confirmation': [
                "好的，我将执行：{action}\n\n参数：\n{params}\n\n是否继续？(是/否)",
            ],
            'missing_info': [
                "我需要更多信息：\n{missing}\n\n请提供这些信息。",
            ],
            'success': [
                "✓ 完成！{result}\n\n接下来您想做什么？",
            ],
            'error': [
                "✗ 出错了：{error}\n\n请检查参数后重试，或者告诉我详细信息以便我帮助您。",
            ]
        }

    def generate(self, response_type: str, **kwargs) -> str:
        """Generate response based on type"""
        templates = self.templates.get(response_type, [""])
        template = templates[0]  # Could randomize later

        try:
            return template.format(**kwargs)
        except KeyError:
            return template


class ConversationalAgent:
    """Main conversational agent that orchestrates the dialogue"""

    def __init__(self):
        self.context = ConversationContext()
        self.intent_classifier = IntentClassifier()
        self.skill_executor = SkillExecutor()
        self.response_generator = ResponseGenerator()
        self.config_manager = None

        # Try to import config manager
        try:
            from config_manager import get_config_manager
            self.config_manager = get_config_manager()
        except ImportError:
            pass

    def process_message(self, user_message: str) -> Dict:
        """
        Process a user message and generate response
        Returns: {response: str, action: str, data: dict}
        """
        # Add to conversation history
        self.context.add_message('user', user_message)

        # Classify intent
        intent_result = self.intent_classifier.classify(user_message)

        # Handle based on intent
        if intent_result['intent'] == 'help':
            response = self.response_generator.generate('help')
            return {
                'response': response,
                'action': 'none',
                'data': {}
            }

        elif intent_result['intent'] == 'unknown':
            response = "抱歉，我没有理解您的意思。您可以问我'能做什么'来获取帮助，或者直接描述您想完成的任务。"
            return {
                'response': response,
                'action': 'none',
                'data': {}
            }

        # Execute skill
        execution_result = self.skill_executor.execute(
            intent_result['intent'],
            intent_result['entities'],
            self.context
        )

        # Generate response
        if not execution_result['success']:
            if 'needs_info' in execution_result:
                missing = '\n'.join([f"- {info}" for info in execution_result['needs_info']])
                response = self.response_generator.generate('missing_info', missing=missing)
                return {
                    'response': response,
                    'action': 'request_info',
                    'data': execution_result
                }
            else:
                response = self.response_generator.generate('error', error=execution_result['message'])
                return {
                    'response': response,
                    'action': 'error',
                    'data': execution_result
                }

        # Success - store results
        if 'results' in execution_result:
            self.context.last_results.update(execution_result['results'])

        response = execution_result['message']
        self.context.add_message('assistant', response)

        return {
            'response': response,
            'action': execution_result.get('action', 'none'),
            'data': execution_result
        }

    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.context.conversation_history

    def reset_conversation(self):
        """Reset conversation context"""
        self.context = ConversationContext()


# Singleton instance
_agent_instance = None


def get_agent() -> ConversationalAgent:
    """Get or create agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ConversationalAgent()
    return _agent_instance


if __name__ == '__main__':
    # Interactive mode
    print("=" * 80)
    print("SeismicX Conversational Agent")
    print("=" * 80)
    print()

    agent = get_agent()

    # Greeting
    greeting = agent.response_generator.generate('greeting')
    print(f"Assistant: {greeting}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出', 'bye']:
                print("\nAssistant: 再见！祝您工作顺利！👋\n")
                break

            if not user_input:
                continue

            result = agent.process_message(user_input)
            print(f"\nAssistant: {result['response']}\n")

            # If there's an action to execute
            if result['action'] == 'execute_command' and 'command' in result['data']:
                confirm = input("执行命令？(y/n): ").strip().lower()
                if confirm == 'y':
                    import subprocess
                    cmd = result['data']['command']
                    print(f"\nExecuting: {cmd}\n")
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if proc.returncode == 0:
                        print("✓ 命令执行成功！")
                    else:
                        print(f"✗ 命令执行失败:\n{proc.stderr}")
                    print()

        except KeyboardInterrupt:
            print("\n\nAssistant: 再见！👋\n")
            break
        except Exception as e:
            print(f"\nAssistant: 发生错误: {e}\n请重试。\n")
