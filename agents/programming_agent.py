"""Programming agent for automatic code generation and execution of inversion/forward modeling."""

import os
import sys
import tempfile
import subprocess
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import traceback
from loguru import logger

from core.ollama_client import OllamaClient


class ProgrammingAgent:
    """Agent for generating and executing geological computation code."""

    CODE_GENERATION_PROMPT = """你是一位专业的地球物理计算程序员。根据给定的算法说明和需求,编写高质量的Python代码来实现地质反演、正演或其他计算任务。

代码要求:
1. 使用numpy、scipy等科学计算库
2. 包含完整的错误处理和输入验证
3. 添加详细的注释和文档字符串
4. 提供清晰的函数接口
5. 考虑计算效率和内存使用
6. 如果需要绘图,使用matplotlib或plotly

请只返回Python代码,不要包含其他解释文字。代码应该是完整可运行的。"""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        working_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize programming agent.

        Args:
            ollama_client: Ollama client instance
            working_dir: Working directory for generated code
        """
        self.client = ollama_client or OllamaClient()
        self.working_dir = Path(working_dir) if working_dir else Path("./output/generated_code")
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.generated_files: List[Path] = []

    def generate_code_from_markdown(
        self,
        markdown_path: Union[str, Path],
        task_description: Optional[str] = None,
    ) -> str:
        """Generate code from algorithm documentation in Markdown format.

        Args:
            markdown_path: Path to markdown documentation file
            task_description: Additional task description

        Returns:
            Generated Python code
        """
        # Read markdown file
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        prompt = f"""请根据以下算法文档生成Python实现代码:

算法文档:
{markdown_content}

"""
        if task_description:
            prompt += f"\n具体任务要求:\n{task_description}\n"

        prompt += "\n请生成完整的Python代码实现该算法。"

        messages = [
            {"role": "system", "content": self.CODE_GENERATION_PROMPT},
            {"role": "user", "content": prompt},
        ]

        logger.info(f"Generating code from: {markdown_path}")
        code = self.client.chat(messages, temperature=0.3, max_tokens=8192)

        # Extract code blocks if present
        code = self._extract_code_blocks(code)

        # Save generated code
        code_file = self._save_code(code, markdown_path)
        logger.info(f"Generated code saved to: {code_file}")

        return code

    def generate_code_from_description(
        self,
        description: str,
        algorithm_type: str = "inversion",
    ) -> str:
        """Generate code from natural language description.

        Args:
            description: Description of the algorithm/task
            algorithm_type: Type of algorithm (inversion, forward_modeling, etc.)

        Returns:
            Generated Python code
        """
        prompt = f"""请编写一个{algorithm_type}的Python程序。

任务描述:
{description}

请确保代码:
1. 有清晰的函数接口
2. 包含必要的参数验证
3. 有详细的注释说明
4. 可以独立运行测试"""

        messages = [
            {"role": "system", "content": self.CODE_GENERATION_PROMPT},
            {"role": "user", "content": prompt},
        ]

        logger.info(f"Generating code for: {algorithm_type}")
        code = self.client.chat(messages, temperature=0.3, max_tokens=8192)

        code = self._extract_code_blocks(code)
        code_file = self._save_code(code, f"{algorithm_type}_task")
        logger.info(f"Generated code saved to: {code_file}")

        return code

    def execute_code(
        self,
        code: Optional[str] = None,
        code_file: Optional[Union[str, Path]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """Execute generated code safely.

        Args:
            code: Python code string to execute
            code_file: Path to code file (alternative to code)
            input_data: Input data to pass to the code
            timeout: Execution timeout in seconds

        Returns:
            Execution result dict with 'success', 'output', 'error', 'result_file'
        """
        if code is None and code_file is None:
            raise ValueError("Either code or code_file must be provided")

        # Create temporary file if code is provided as string
        if code:
            temp_file = self._save_code(code, "temp_execution")
            code_file = temp_file

        logger.info(f"Executing code: {code_file}")

        # Prepare execution environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent) + ":" + env.get("PYTHONPATH", "")

        try:
            # Execute code
            result = subprocess.run(
                [sys.executable, str(code_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=str(self.working_dir),
            )

            success = result.returncode == 0
            output = result.stdout
            error = result.stderr if not success else None

            logger.info(f"Execution {'succeeded' if success else 'failed'}")

            return {
                "success": success,
                "output": output,
                "error": error,
                "result_file": None,  # Code should save its own results
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Code execution timed out after {timeout}s")
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds",
                "result_file": None,
            }
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "result_file": None,
            }

    def run_inversion(
        self,
        algorithm_doc: Union[str, Path],
        input_data_file: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run inversion based on algorithm documentation.

        Args:
            algorithm_doc: Path to algorithm documentation
            input_data_file: Path to input data file
            parameters: Additional parameters

        Returns:
            Inversion results
        """
        # Generate inversion code
        task_desc = f"""
实现一个反演程序,要求:
- 读取输入数据文件: {input_data_file}
- 使用算法文档中描述的方法进行反演
- 保存反演结果到输出文件
- 生成可视化结果图
"""
        if parameters:
            task_desc += f"\n- 使用以下参数: {parameters}"

        code = self.generate_code_from_markdown(algorithm_doc, task_desc)

        # Execute the code
        result = self.execute_code(code)

        return result

    def run_forward_modeling(
        self,
        model_parameters: Dict[str, Any],
        algorithm_doc: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Run forward modeling simulation.

        Args:
            model_parameters: Model parameters for forward modeling
            algorithm_doc: Optional algorithm documentation

        Returns:
            Forward modeling results
        """
        if algorithm_doc:
            code = self.generate_code_from_markdown(
                algorithm_doc,
                f"实现正演模拟,使用参数: {model_parameters}"
            )
        else:
            code = self.generate_code_from_description(
                f"实现地球物理正演模拟,参数: {model_parameters}",
                "forward_modeling"
            )

        result = self.execute_code(code)
        return result

    def _extract_code_blocks(self, text: str) -> str:
        """Extract Python code blocks from markdown-formatted text.

        Args:
            text: Text containing code blocks

        Returns:
            Extracted code
        """
        # Look for ```python ... ``` blocks
        import re
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            # Return the longest match (most likely the complete code)
            return max(matches, key=len)

        # If no code blocks found, return text as-is (might be plain code)
        return text.strip()

    def _save_code(self, code: str, base_name: str) -> Path:
        """Save generated code to file.

        Args:
            code: Python code
            base_name: Base name for the file

        Returns:
            Path to saved file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.py"
        filepath = self.working_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        self.generated_files.append(filepath)
        return filepath

    def cleanup_generated_files(self):
        """Remove all generated code files."""
        for filepath in self.generated_files:
            try:
                filepath.unlink()
                logger.debug(f"Removed: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to remove {filepath}: {e}")

        self.generated_files.clear()
        logger.info("Cleaned up generated files")
