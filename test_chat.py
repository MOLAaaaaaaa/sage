"""Test natural language chat functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from core.chat_agent import ChatAgent

console = Console()


def test_chat_commands():
    """Test various chat commands."""
    console.print("\n")
    console.print(Panel.fit("💬 Natural Language Chat Test", style="bold cyan"))
    console.print()

    # Initialize chat agent
    console.print("[bold]Initializing Chat Agent...[/bold]")
    agent = ChatAgent(enable_rag=False)  # Disable RAG for faster testing
    console.print("[green]✓[/green] Chat agent ready\n")

    # Test commands
    test_commands = [
        "列出当前目录的文件",
        "列出docs目录下的markdown文件",
        "查看output目录有哪些文件",
    ]

    for cmd in test_commands:
        console.print(Panel(f"📝 命令: {cmd}", style="blue"))
        result = agent.process_command(cmd)

        if result['success']:
            console.print(f"[green]✓[/green] {result['response'][:500]}")
        else:
            console.print(f"[red]✗[/red] {result['response']}")

        console.print()


if __name__ == "__main__":
    test_chat_commands()
