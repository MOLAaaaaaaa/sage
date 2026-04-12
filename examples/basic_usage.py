"""Example usage of the Geological Interpretation Agent."""

import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ollama_client import OllamaClient
from agents.geological_interpreter import GeologicalInterpreterAgent
from agents.programming_agent import ProgrammingAgent
from visualization.plotter import GeologicalPlotter
from utils.document_parser import AlgorithmDocumentParser


def example_1_region_analysis():
    """Example 1: Regional geological analysis."""
    print("=" * 80)
    print("Example 1: Regional Geological Analysis")
    print("=" * 80)

    interpreter = GeologicalInterpreterAgent()

    # Analyze a region
    result = interpreter.analyze_region(
        region_name="塔里木盆地",
        description="中国西部大型含油气盆地,面积约56万平方公里"
    )

    print("\n分析结果:\n")
    print(result)
    print("\n")


def example_2_velocity_analysis():
    """Example 2: Velocity structure analysis."""
    print("=" * 80)
    print("Example 2: Velocity Structure Analysis")
    print("=" * 80)

    interpreter = GeologicalInterpreterAgent()

    # Create sample velocity data
    depths = np.linspace(0, 50, 20)
    velocities = 5.0 + 0.08 * depths + np.random.randn(20) * 0.15

    velocity_data = [
        {"depth": float(d), "velocity": float(v)}
        for d, v in zip(depths, velocities)
    ]

    result = interpreter.analyze_velocity_structure(
        structure_description="某地区一维速度结构,速度随深度增加",
        depth_range=(0, 50),
        velocity_data=velocity_data
    )

    print("\n速度结构分析结果:\n")
    print(result)
    print("\n")


def example_3_code_generation():
    """Example 3: Generate code from algorithm documentation."""
    print("=" * 80)
    print("Example 3: Code Generation from Algorithm Documentation")
    print("=" * 80)

    prog_agent = ProgrammingAgent()

    # Generate code from markdown documentation
    doc_path = Path(__file__).parent.parent / "docs" / "algorithms" / "linear_inversion.md"

    if doc_path.exists():
        code = prog_agent.generate_code_from_markdown(
            markdown_path=doc_path,
            task_description="实现线性反演算法,包含测试用例"
        )

        print("\n生成的代码预览 (前500字符):\n")
        print(code[:500])
        print("...\n")

        # Save the code
        output_path = Path("./output/examples/generated_inversion.py")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"完整代码已保存到: {output_path}\n")
    else:
        print(f"算法文档不存在: {doc_path}")
        print("请先创建算法文档\n")


def example_4_plotting():
    """Example 4: Create geological plots."""
    print("=" * 80)
    print("Example 4: Creating Geological Plots")
    print("=" * 80)

    plotter = GeologicalPlotter(output_dir="./output/examples")

    # Create velocity profile
    depths = np.linspace(0, 50, 100)
    velocities = 5.0 + 0.1 * depths + np.random.randn(100) * 0.2

    plot_path = plotter.plot_velocity_profile(
        depths=depths,
        velocities=velocities,
        title="Example Velocity Profile",
        save_path="./output/examples/velocity_profile.png"
    )

    print(f"\n速度剖面图已保存: {plot_path}\n")

    # Create velocity section
    x = np.linspace(0, 100, 50)
    z = np.linspace(0, 30, 40)
    X, Z = np.meshgrid(x, z)
    V = 5.0 + 0.05 * Z + 0.02 * X + np.random.randn(*Z.shape) * 0.1

    section_path = plotter.plot_velocity_section(
        x=x,
        depths=z,
        velocities=V,
        title="Example Velocity Section",
        save_path="./output/examples/velocity_section.png"
    )

    print(f"速度断面图已保存: {section_path}\n")


def example_5_document_parsing():
    """Example 5: Parse algorithm documentation."""
    print("=" * 80)
    print("Example 5: Algorithm Document Parsing")
    print("=" * 80)

    parser = AlgorithmDocumentParser()
    doc_path = Path(__file__).parent.parent / "docs" / "algorithms" / "linear_inversion.md"

    if doc_path.exists():
        parsed = parser.parse_markdown(doc_path)

        print(f"\n文档标题: {parsed['title']}")
        print(f"章节数量: {len(parsed['sections'])}")
        print(f"算法数量: {len(parsed['algorithms'])}")
        print(f"参数数量: {len(parsed['parameters'])}")
        print(f"公式数量: {len(parsed['equations'])}")
        print(f"代码示例数量: {len(parsed['code_examples'])}")

        print("\n提取的章节:")
        for section in parsed['sections']:
            print(f"  - {section['title']}")

        print("\n提取的参数:")
        for param in parsed['parameters']:
            print(f"  - {param['name']}: {param.get('description', '')[:50]}")

        print("\n")
    else:
        print(f"文档不存在: {doc_path}\n")


def example_6_inversion():
    """Example 6: Run a simple inversion."""
    print("=" * 80)
    print("Example 6: Running Linear Inversion")
    print("=" * 80)

    from inversion.base import LinearInversion

    # Create synthetic data
    np.random.seed(42)
    n_data = 50
    n_model = 30

    # True model
    true_model = np.exp(-np.linspace(0, 5, n_model))

    # Forward operator (simple smoothing matrix)
    G = np.zeros((n_data, n_model))
    for i in range(n_data):
        for j in range(n_model):
            G[i, j] = np.exp(-0.5 * ((i - j * n_data / n_model) / 5) ** 2)

    # Generate observed data
    data = G @ true_model + 0.01 * np.random.randn(n_data)

    # Run inversion
    inv = LinearInversion(regularization_weight=0.01)
    inv.set_forward_operator(G)

    inverted_model = inv.invert(data)

    print(f"\n真实模型范围: [{true_model.min():.4f}, {true_model.max():.4f}]")
    print(f"反演模型范围: [{inverted_model.min():.4f}, {inverted_model.max():.4f}]")
    print(f"数据拟合残差: {inv.result['misfit']:.6f}")
    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "地质解释Agent系统 - 示例演示" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Check Ollama connection first
    print("检查Ollama连接...")
    client = OllamaClient()
    if not client.check_connection():
        print("\n警告: Ollama服务未连接或模型不可用")
        print("请运行: ollama pull qwen3-vl:30b")
        print("部分功能可能无法使用\n")
        response = input("是否继续运行示例? (y/n): ")
        if response.lower() != 'y':
            return

    # Run examples
    try:
        example_5_document_parsing()
    except Exception as e:
        print(f"Example 5 failed: {e}\n")

    try:
        example_4_plotting()
    except Exception as e:
        print(f"Example 4 failed: {e}\n")

    try:
        example_6_inversion()
    except Exception as e:
        print(f"Example 6 failed: {e}\n")

    # Examples requiring Ollama
    print("\n以下示例需要Ollama连接:\n")

    try:
        example_1_region_analysis()
    except Exception as e:
        print(f"Example 1 failed (可能需要Ollama): {e}\n")

    try:
        example_2_velocity_analysis()
    except Exception as e:
        print(f"Example 2 failed (可能需要Ollama): {e}\n")

    try:
        example_3_code_generation()
    except Exception as e:
        print(f"Example 3 failed (可能需要Ollama): {e}\n")

    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
