"""Command-line interface for geological interpretation agent."""

import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from core.ollama_client import OllamaClient
from agents.geological_interpreter import GeologicalInterpreterAgent
from agents.programming_agent import ProgrammingAgent
from visualization.plotter import GeologicalPlotter
from utils.document_parser import AlgorithmDocumentParser

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Geological Interpretation Agent - CLI Tool.

    A powerful tool for geological data analysis, velocity structure interpretation,
    and automated inversion/forward modeling using AI.
    """
    pass


@cli.command()
def check():
    """Check system status and connections."""
    console.print(Panel("System Status Check", style="bold blue"))

    # Check Ollama connection
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Checking Ollama connection...", total=None)
        client = OllamaClient()
        connected = client.check_connection()
        progress.update(task, completed=True)

    if connected:
        console.print("[green]✓[/green] Ollama server is running")
        console.print(f"[green]✓[/green] Model available: {client.model}")
    else:
        console.print("[red]✗[/red] Ollama server is not running or model not available")
        console.print("[yellow]![/yellow] Please start Ollama and pull the required model:")
        console.print("    ollama pull qwen3-vl:30b")


@cli.command()
@click.option("--region", "-r", required=True, help="Region name to analyze")
@click.option("--description", "-d", help="Additional description of the region")
@click.option("--output", "-o", help="Output file path for the report")
def analyze_region(region, description, output):
    """Analyze geological information for a specific region."""
    console.print(Panel(f"Analyzing Region: {region}", style="bold cyan"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Performing geological analysis...", total=None)

        interpreter = GeologicalInterpreterAgent()
        result = interpreter.analyze_region(
            region_name=region,
            description=description
        )
        progress.update(task, completed=True)

    # Display result
    console.print("\n")
    console.print(Markdown(result))

    # Save to file if requested
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] Report saved to: {output_path}")


@cli.command()
@click.option("--image", "-i", help="Path to velocity structure image")
@click.option("--description", "-d", help="Description of the velocity structure")
@click.option("--depth-min", type=float, help="Minimum depth (km)")
@click.option("--depth-max", type=float, help="Maximum depth (km)")
@click.option("--output", "-o", help="Output file path")
def analyze_velocity(image, description, depth_min, depth_max, output):
    """Analyze velocity structure data."""
    console.print(Panel("Velocity Structure Analysis", style="bold cyan"))

    depth_range = None
    if depth_min is not None and depth_max is not None:
        depth_range = (depth_min, depth_max)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing velocity structure...", total=None)

        interpreter = GeologicalInterpreterAgent()
        result = interpreter.analyze_velocity_structure(
            structure_description=description or "",
            image_path=image,
            depth_range=depth_range
        )
        progress.update(task, completed=True)

    console.print("\n")
    console.print(Markdown(result))

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] Analysis saved to: {output_path}")


@cli.command()
@click.option("--doc", "-d", required=True, help="Path to algorithm documentation (Markdown)")
@click.option("--task", "-t", help="Specific task description")
@click.option("--output", "-o", help="Output file path for generated code")
def generate_code(doc, task, output):
    """Generate Python code from algorithm documentation."""
    console.print(Panel("Code Generation from Algorithm Documentation", style="bold cyan"))

    doc_path = Path(doc)
    if not doc_path.exists():
        console.print(f"[red]Error:[/red] Documentation file not found: {doc}")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task_progress = progress.add_task("Generating code...", total=None)

        programming_agent = ProgrammingAgent()
        code = programming_agent.generate_code_from_markdown(
            markdown_path=doc_path,
            task_description=task
        )
        progress.update(task_progress, completed=True)

    # Display code preview
    console.print("\n[bold]Generated Code Preview:[/bold]\n")
    lines = code.split('\n')
    preview_lines = min(50, len(lines))
    for line in lines[:preview_lines]:
        console.print(f"  {line}")
    if len(lines) > preview_lines:
        console.print(f"  ... ({len(lines) - preview_lines} more lines)")

    # Save code
    if output:
        output_path = Path(output)
    else:
        output_path = Path("./output/generated_code") / f"{doc_path.stem}_generated.py"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)

    console.print(f"\n[green]✓[/green] Code saved to: {output_path}")


@cli.command()
@click.option("--code", "-c", help="Path to Python code file to execute")
@click.option("--timeout", type=int, default=300, help="Execution timeout in seconds")
def execute_code(code, timeout):
    """Execute generated Python code."""
    console.print(Panel("Code Execution", style="bold cyan"))

    code_path = Path(code)
    if not code_path.exists():
        console.print(f"[red]Error:[/red] Code file not found: {code}")
        sys.exit(1)

    with open(code_path, 'r', encoding='utf-8') as f:
        code_content = f.read()

    console.print(f"[blue]Executing:[/blue] {code_path}\n")

    programming_agent = ProgrammingAgent()
    result = programming_agent.execute_code(
        code=code_content,
        timeout=timeout
    )

    if result['success']:
        console.print("[green]✓[/green] Execution successful\n")
        if result['output']:
            console.print("[bold]Output:[/bold]")
            console.print(result['output'])
    else:
        console.print("[red]✗[/red] Execution failed\n")
        if result['error']:
            console.print("[bold red]Error:[/bold red]")
            console.print(result['error'])


@cli.command()
@click.option("--algorithm", "-a", required=True, help="Algorithm documentation file")
@click.option("--data", "-d", required=True, help="Input data file")
@click.option("--params", "-p", help="Parameters as JSON string")
def run_inversion(algorithm, data, params):
    """Run inversion based on algorithm documentation."""
    console.print(Panel("Running Inversion", style="bold cyan"))

    algo_path = Path(algorithm)
    data_path = Path(data)

    if not algo_path.exists():
        console.print(f"[red]Error:[/red] Algorithm doc not found: {algorithm}")
        sys.exit(1)

    if not data_path.exists():
        console.print(f"[red]Error:[/red] Data file not found: {data}")
        sys.exit(1)

    parameters = None
    if params:
        import json
        try:
            parameters = json.loads(params)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON parameters")
            sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task_progress = progress.add_task("Running inversion...", total=None)

        programming_agent = ProgrammingAgent()
        result = programming_agent.run_inversion(
            algorithm_doc=algo_path,
            input_data_file=data_path,
            parameters=parameters
        )
        progress.update(task_progress, completed=True)

    if result['success']:
        console.print("[green]✓[/green] Inversion completed successfully\n")
        if result['output']:
            console.print("[bold]Output:[/bold]")
            console.print(result['output'])
    else:
        console.print("[red]✗[/red] Inversion failed\n")
        if result['error']:
            console.print("[bold red]Error:[/bold red]")
            console.print(result['error'])


@cli.command()
@click.option("--type", "plot_type", required=True,
              type=click.Choice(['velocity-profile', 'velocity-section', 'inversion-result']),
              help="Type of plot to generate")
@click.option("--output", "-o", help="Output image path")
def create_plot(plot_type, output):
    """Create example geological plots."""
    console.print(Panel(f"Creating Plot: {plot_type}", style="bold cyan"))

    import numpy as np

    plotter = GeologicalPlotter()

    if plot_type == 'velocity-profile':
        depths = np.linspace(0, 50, 100)
        velocities = 5.0 + 0.1 * depths + np.random.randn(100) * 0.2

        save_path = output or "./output/plots/velocity_profile.png"
        plotter.plot_velocity_profile(depths, velocities, save_path=save_path)

    elif plot_type == 'velocity-section':
        x = np.linspace(0, 100, 50)
        depths = np.linspace(0, 30, 40)
        X, Z = np.meshgrid(x, depths)
        velocities = 5.0 + 0.05 * Z + 0.02 * X + np.random.randn(*Z.shape) * 0.1

        save_path = output or "./output/plots/velocity_section.png"
        plotter.plot_velocity_section(x, depths, velocities, save_path=save_path)

    elif plot_type == 'inversion-result':
        observed = np.sin(np.linspace(0, 10, 100)) + np.random.randn(100) * 0.1
        predicted = np.sin(np.linspace(0, 10, 100))
        model = np.linspace(0, 5, 50)

        save_path = output or "./output/plots/inversion_result.png"
        plotter.plot_inversion_result(observed, predicted, model, save_path=save_path)

    console.print(f"[green]✓[/green] Plot saved to: {save_path}")


@cli.command()
def web():
    """Start the web interface."""
    console.print(Panel("Starting Web Interface", style="bold green"))
    console.print("Opening browser at: http://localhost:8000\n")

    import uvicorn
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from web.app import app
    uvicorn.run(app, host="0.0.0.0", port=8000)


@cli.command()
@click.argument('message', nargs=-1, required=True)
def chat(message):
    """Process natural language command.

    Example:
        python main.py chat "列出当前目录的文件"
        python main.py chat "绘制速度剖面图 data.npy"
    """
    user_input = ' '.join(message)
    console.print(Panel(f"处理命令: {user_input}", style="cyan"))

    from core.chat_agent import ChatAgent
    agent = ChatAgent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("处理中...", total=None)
        result = agent.process_command(user_input)
        progress.update(task, completed=True)

    if result['success']:
        console.print(f"\n[green]✓[/green] {result['response']}")
    else:
        console.print(f"\n[red]✗[/red] {result['response']}")


if __name__ == "__main__":
    cli()
