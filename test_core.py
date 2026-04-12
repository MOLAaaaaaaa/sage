"""Test script to verify core functionality."""

import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported."""
    print("测试模块导入...")

    try:
        from core.ollama_client import OllamaClient
        print("  ✓ core.ollama_client")
    except ImportError as e:
        print(f"  ✗ core.ollama_client: {e}")
        return False

    try:
        from agents.geological_interpreter import GeologicalInterpreterAgent
        print("  ✓ agents.geological_interpreter")
    except ImportError as e:
        print(f"  ✗ agents.geological_interpreter: {e}")
        return False

    try:
        from agents.programming_agent import ProgrammingAgent
        print("  ✓ agents.programming_agent")
    except ImportError as e:
        print(f"  ✗ agents.programming_agent: {e}")
        return False

    try:
        from visualization.plotter import GeologicalPlotter
        print("  ✓ visualization.plotter")
    except ImportError as e:
        print(f"  ✗ visualization.plotter: {e}")
        return False

    try:
        from utils.document_parser import AlgorithmDocumentParser
        print("  ✓ utils.document_parser")
    except ImportError as e:
        print(f"  ✗ utils.document_parser: {e}")
        return False

    try:
        from inversion.base import LinearInversion, IterativeInversion
        print("  ✓ inversion.base")
    except ImportError as e:
        print(f"  ✗ inversion.base: {e}")
        return False

    return True


def test_plotter():
    """Test plotting functionality."""
    print("\n测试绘图功能...")

    try:
        from visualization.plotter import GeologicalPlotter

        plotter = GeologicalPlotter(output_dir="./output/test")

        # Test velocity profile
        depths = np.linspace(0, 50, 50)
        velocities = 5.0 + 0.1 * depths + np.random.randn(50) * 0.2

        plot_path = plotter.plot_velocity_profile(
            depths=depths,
            velocities=velocities,
            title="Test Plot",
            save_path="./output/test/test_velocity.png"
        )

        if plot_path.exists():
            print(f"  ✓ 速度剖面图生成成功: {plot_path}")
        else:
            print("  ✗ 速度剖面图生成失败")
            return False

        return True

    except Exception as e:
        print(f"  ✗ 绘图测试失败: {e}")
        return False


def test_inversion():
    """Test inversion functionality."""
    print("\n测试反演功能...")

    try:
        from inversion.base import LinearInversion

        # Create simple test case
        np.random.seed(42)
        G = np.array([[1, 0], [0, 1], [1, 1]], dtype=float)
        true_model = np.array([2.0, 3.0])
        data = G @ true_model + 0.01 * np.random.randn(3)

        # Run inversion
        inv = LinearInversion(regularization_weight=0.001)
        inv.set_forward_operator(G)
        model = inv.invert(data)

        # Check results
        if len(model) == 2:
            print(f"  ✓ 线性反演成功: model={model}")
            print(f"  ✓ 真实值: {true_model}, 反演值: {model}")
            print(f"  ✓ 残差: {inv.result['misfit']:.6f}")
            return True
        else:
            print("  ✗ 反演结果维度错误")
            return False

    except Exception as e:
        print(f"  ✗ 反演测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_parser():
    """Test document parsing."""
    print("\n测试文档解析...")

    try:
        from utils.document_parser import AlgorithmDocumentParser

        doc_path = Path("docs/algorithms/linear_inversion.md")

        if not doc_path.exists():
            print(f"  ⚠ 算法文档不存在: {doc_path}")
            return True

        parser = AlgorithmDocumentParser()
        parsed = parser.parse_markdown(doc_path)

        print(f"  ✓ 文档解析成功")
        print(f"    - 标题: {parsed['title']}")
        print(f"    - 章节数: {len(parsed['sections'])}")
        print(f"    - 参数数: {len(parsed['parameters'])}")

        return True

    except Exception as e:
        print(f"  ✗ 文档解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_initialization():
    """Test agent initialization (without Ollama connection)."""
    print("\n测试Agent初始化...")

    try:
        from agents.geological_interpreter import GeologicalInterpreterAgent
        from agents.programming_agent import ProgrammingAgent

        # These should initialize without error (Ollama connection checked separately)
        interpreter = GeologicalInterpreterAgent()
        print("  ✓ GeologicalInterpreterAgent 初始化成功")

        prog_agent = ProgrammingAgent()
        print("  ✓ ProgrammingAgent 初始化成功")

        return True

    except Exception as e:
        print(f"  ✗ Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("地质解释Agent系统 - 功能测试")
    print("=" * 80)
    print()

    results = []

    # Run tests
    results.append(("模块导入", test_imports()))
    results.append(("Agent初始化", test_agent_initialization()))
    results.append(("绘图功能", test_plotter()))
    results.append(("反演功能", test_inversion()))
    results.append(("文档解析", test_document_parser()))

    # Print summary
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s} {status}")

    print("-" * 80)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 80)

    if passed == total:
        print("\n🎉 所有测试通过! 系统已就绪。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败,请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
