#!/usr/bin/env python3
"""Quick demo script to showcase the Geological Interpretation Agent."""

import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def print_header(title):
    """Print a formatted header."""
    console.print(Panel(title, style="bold cyan", border_style="cyan"))


def demo_plotting():
    """Demonstrate plotting capabilities."""
    print_header("Demo 1: Geological Plotting")

    from visualization.plotter import GeologicalPlotter

    plotter = GeologicalPlotter(output_dir="./output/demo")

    # Create velocity profile
    console.print("\n[bold]Creating velocity profile plot...[/bold]")
    depths = np.linspace(0, 50, 100)
    velocities = 5.0 + 0.1 * depths + np.random.randn(100) * 0.2

    plot_path = plotter.plot_velocity_profile(
        depths=depths,
        velocities=velocities,
        title="Demo Velocity Profile",
        save_path="./output/demo/velocity_profile.png"
    )
    console.print(f"[green]✓[/green] Saved to: {plot_path}\n")

    # Create velocity section
    console.print("[bold]Creating velocity section plot...[/bold]")
    x = np.linspace(0, 100, 50)
    z = np.linspace(0, 30, 40)
    X, Z = np.meshgrid(x, z)
    V = 5.0 + 0.05 * Z + 0.02 * X + np.random.randn(*Z.shape) * 0.1

    section_path = plotter.plot_velocity_section(
        x=x,
        depths=z,
        velocities=V,
        title="Demo Velocity Section",
        save_path="./output/demo/velocity_section.png"
    )
    console.print(f"[green]✓[/green] Saved to: {section_path}\n")


def demo_inversion():
    """Demonstrate inversion capabilities."""
    print_header("Demo 2: Linear Inversion")

    from inversion.base import LinearInversion

    console.print("\n[bold]Setting up test problem...[/bold]")

    # Create synthetic problem
    np.random.seed(42)
    n_data, n_model = 50, 30

    # True model (exponential decay)
    true_model = np.exp(-np.linspace(0, 5, n_model))

    # Forward operator (Gaussian smoothing)
    G = np.zeros((n_data, n_model))
    for i in range(n_data):
        for j in range(n_model):
            G[i, j] = np.exp(-0.5 * ((i - j * n_data / n_model) / 5) ** 2)

    # Generate data with noise
    data = G @ true_model + 0.01 * np.random.randn(n_data)

    console.print(f"  Data points: {n_data}")
    console.print(f"  Model parameters: {n_model}")
    console.print(f"  Noise level: 1%\n")

    # Run inversion
    console.print("[bold]Running linear inversion...[/bold]")
    inv = LinearInversion(regularization_weight=0.01)
    inv.set_forward_operator(G)
    inverted_model = inv.invert(data)

    # Display results
    console.print(f"\n[green]✓[/green] Inversion completed")
    console.print(f"  RMS misfit: {inv.result['misfit']:.6f}")
    console.print(f"  True model range: [{true_model.min():.4f}, {true_model.max():.4f}]")
    console.print(f"  Inverted model range: [{inverted_model.min():.4f}, {inverted_model.max():.4f}]")

    # Calculate model error
    model_error = np.sqrt(np.mean((inverted_model - true_model) ** 2))
    console.print(f"  Model error: {model_error:.6f}\n")


def demo_document_parsing():
    """Demonstrate document parsing."""
    print_header("Demo 3: Algorithm Document Parsing")

    from utils.document_parser import AlgorithmDocumentParser

    doc_path = Path("docs/algorithms/linear_inversion.md")

    if not doc_path.exists():
        console.print(f"[yellow]⚠[/yellow] Document not found: {doc_path}\n")
        return

    console.print(f"\n[bold]Parsing: {doc_path}[/bold]\n")

    parser = AlgorithmDocumentParser()
    parsed = parser.parse_markdown(doc_path)

    console.print(f"[green]✓[/green] Document parsed successfully\n")
    console.print(f"  Title: {parsed['title']}")
    console.print(f"  Sections: {len(parsed['sections'])}")
    console.print(f"  Algorithms: {len(parsed['algorithms'])}")
    console.print(f"  Parameters: {len(parsed['parameters'])}")
    console.print(f"  Equations: {len(parsed['equations'])}")
    console.print(f"  Code examples: {len(parsed['code_examples'])}\n")

    console.print("[bold]Extracted sections:[/bold]")
    for i, section in enumerate(parsed['sections'], 1):
        console.print(f"  {i}. {section['title']}")

    console.print("\n[bold]Extracted parameters:[/bold]")
    for param in parsed['parameters']:
        desc = param.get('description', '')[:60]
        console.print(f"  • {param['name']}: {desc}")

    console.print()


def demo_agents():
    """Demonstrate agent initialization."""
    print_header("Demo 4: Agent System")

    console.print("\n[bold]Initializing agents...[/bold]\n")

    from agents.geological_interpreter import GeologicalInterpreterAgent
    from agents.programming_agent import ProgrammingAgent
    from core.ollama_client import OllamaClient

    # Initialize Ollama client
    console.print("1. Creating Ollama client...")
    client = OllamaClient()
    console.print(f"   Model: {client.model}")
    console.print(f"   URL: {client.base_url}\n")

    # Initialize geological interpreter
    console.print("2. Creating Geological Interpreter Agent...")
    interpreter = GeologicalInterpreterAgent(client)
    console.print("   [green]✓[/green] Ready\n")

    # Initialize programming agent
    console.print("3. Creating Programming Agent...")
    prog_agent = ProgrammingAgent(client)
    console.print(f"   Working directory: {prog_agent.working_dir}")
    console.print("   [green]✓[/green] Ready\n")

    console.print("[bold green]All agents initialized successfully![/bold green]\n")


def main():
    """Run all demos."""
    console.print("\n")
    console.print(Panel.fit(
        "🌍 Geological Interpretation Agent - Demo",
        style="bold white on blue"
    ))
    console.print()

    try:
        # Run demos
        demo_plotting()
        console.print()

        demo_inversion()
        console.print()

        demo_document_parsing()
        console.print()

        demo_agents()
        console.print()

        # Final message
        console.print(Panel(
            "[bold green]Demo completed successfully![/bold green]\n\n"
            "Next steps:\n"
            "• Start web interface: [cyan]python main.py web[/cyan]\n"
            "• Try CLI commands: [cyan]python main.py --help[/cyan]\n"
            "• Run full examples: [cyan]python examples/basic_usage.py[/cyan]",
            style="green",
            border_style="green"
        ))
        console.print()

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
