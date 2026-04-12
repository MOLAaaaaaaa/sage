"""Parser for algorithm documentation in Markdown format."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from loguru import logger


class AlgorithmDocumentParser:
    """Parse and extract information from algorithm documentation."""

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse_markdown(self, doc_path: Path) -> Dict[str, Any]:
        """Parse a markdown algorithm document.

        Args:
            doc_path: Path to markdown file

        Returns:
            Parsed document structure
        """
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = {
            'title': self._extract_title(content),
            'sections': self._extract_sections(content),
            'algorithms': self._extract_algorithms(content),
            'parameters': self._extract_parameters(content),
            'equations': self._extract_equations(content),
            'code_examples': self._extract_code_examples(content),
            'references': self._extract_references(content),
            'raw_content': content,
        }

        logger.info(f"Parsed algorithm document: {doc_path.name}")
        return result

    def _extract_title(self, content: str) -> str:
        """Extract document title (first level-1 heading).

        Args:
            content: Markdown content

        Returns:
            Title string
        """
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled"

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract all sections from markdown.

        Args:
            content: Markdown content

        Returns:
            List of section dicts with 'title' and 'content'
        """
        sections = []
        # Match level 2 headings and their content
        pattern = r'^##\s+(.+?)$\n(.*?)(?=^##\s+|$)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            sections.append({
                'title': match.group(1).strip(),
                'content': match.group(2).strip()
            })

        return sections

    def _extract_algorithms(self, content: str) -> List[Dict[str, Any]]:
        """Extract algorithm descriptions.

        Args:
            content: Markdown content

        Returns:
            List of algorithm descriptions
        """
        algorithms = []

        # Look for algorithm sections or code blocks with algorithm tag
        algo_pattern = r'###\s+(?:Algorithm|算法)\s*:?\s*(.+?)$\n(.*?)(?=^###|$)'
        matches = re.finditer(algo_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)

        for match in matches:
            algorithms.append({
                'name': match.group(1).strip(),
                'description': match.group(2).strip()
            })

        # If no explicit algorithm sections, look for numbered lists describing steps
        if not algorithms:
            step_pattern = r'(?:步骤|Step)\s*\d+[.:]\s*(.+?)(?=(?:步骤|Step)\s*\d+[.:]|$)'
            step_matches = re.finditer(step_pattern, content, re.DOTALL | re.IGNORECASE)
            steps = [m.group(1).strip() for m in step_matches]

            if steps:
                algorithms.append({
                    'name': 'Main Algorithm',
                    'description': '\n\n'.join(steps),
                    'steps': steps
                })

        return algorithms

    def _extract_parameters(self, content: str) -> List[Dict[str, str]]:
        """Extract parameter definitions.

        Args:
            content: Markdown content

        Returns:
            List of parameter dicts
        """
        parameters = []

        # Look for parameter tables or lists
        table_pattern = r'\|(.+)\|\n\|[-\s|]+\|\n((?:\|.+\|\n)*)'
        table_match = re.search(table_pattern, content)

        if table_match:
            headers = [h.strip() for h in table_match.group(1).split('|')]
            rows = table_match.group(2).strip().split('\n')

            for row in rows:
                cells = [c.strip() for c in row.split('|')[1:-1]]
                if len(cells) >= 2:
                    param = {'name': cells[0]}
                    for i, header in enumerate(headers[1:], 1):
                        if i < len(cells):
                            param[header.lower()] = cells[i]
                    parameters.append(param)
        else:
            # Look for parameter lists
            param_pattern = r'-?\s*\*\*(.+?)\*\*[:：]\s*(.+?)(?=\n-?\s*\*\*|\n\n|$)'
            matches = re.finditer(param_pattern, content)

            for match in matches:
                parameters.append({
                    'name': match.group(1).strip(),
                    'description': match.group(2).strip()
                })

        return parameters

    def _extract_equations(self, content: str) -> List[str]:
        """Extract mathematical equations.

        Args:
            content: Markdown content

        Returns:
            List of equation strings
        """
        equations = []

        # LaTeX display math
        display_pattern = r'\$\$(.+?)\$\$'
        equations.extend(re.findall(display_pattern, content, re.DOTALL))

        # Inline math (if not already captured)
        inline_pattern = r'(?<!\$)\$([^$]+?)\$(?!\$)'
        equations.extend(re.findall(inline_pattern, content))

        return equations

    def _extract_code_examples(self, content: str) -> List[Dict[str, str]]:
        """Extract code examples from markdown.

        Args:
            content: Markdown content

        Returns:
            List of code example dicts
        """
        examples = []

        # Match code blocks with language specification
        code_pattern = r'```(\w+)\s*\n(.*?)\n```'
        matches = re.finditer(code_pattern, content, re.DOTALL)

        for match in matches:
            examples.append({
                'language': match.group(1),
                'code': match.group(2)
            })

        return examples

    def _extract_references(self, content: str) -> List[str]:
        """Extract references/bibliography.

        Args:
            content: Markdown content

        Returns:
            List of reference strings
        """
        references = []

        # Look for References section
        ref_section = re.search(
            r'#+\s*(?:References|参考文献)\s*\n(.*?)(?=^#|$)',
            content, re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        if ref_section:
            ref_text = ref_section.group(1).strip()
            # Split by numbered items or bullet points
            refs = re.split(r'\n\s*(?:\d+\.|-|\*)\s*', ref_text)
            references = [r.strip() for r in refs if r.strip()]

        return references

    def generate_prompt_from_doc(self, doc_path: Path) -> str:
        """Generate a prompt for code generation from algorithm documentation.

        Args:
            doc_path: Path to markdown file

        Returns:
            Formatted prompt for LLM
        """
        parsed = self.parse_markdown(doc_path)

        prompt = f"# 算法实现任务\n\n"
        prompt += f"## 算法名称: {parsed['title']}\n\n"

        if parsed['algorithms']:
            prompt += "## 算法描述\n\n"
            for algo in parsed['algorithms']:
                prompt += f"### {algo['name']}\n{algo['description']}\n\n"

        if parsed['parameters']:
            prompt += "## 参数说明\n\n"
            for param in parsed['parameters']:
                prompt += f"- **{param['name']}**: {param.get('description', '')}\n"
            prompt += "\n"

        if parsed['equations']:
            prompt += "## 数学公式\n\n"
            for i, eq in enumerate(parsed['equations'], 1):
                prompt += f"{i}. ${eq}$\n"
            prompt += "\n"

        if parsed['code_examples']:
            prompt += "## 参考代码示例\n\n"
            for example in parsed['code_examples']:
                prompt += f"```{example['language']}\n{example['code']}\n```\n\n"

        prompt += "请根据以上算法文档,生成完整的Python实现代码。"

        return prompt
