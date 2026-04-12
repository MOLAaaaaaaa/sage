"""Test script for RAG functionality."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_rag_initialization():
    """Test RAG module initialization."""
    console.print(Panel("Test 1: RAG Initialization", style="cyan"))

    try:
        from utils.rag_retriever import RAGRetriever
        from core.ollama_client import OllamaClient

        client = OllamaClient()
        rag = RAGRetriever(ollama_client=client)

        console.print("[green]✓[/green] RAG initialized successfully")
        console.print(f"  PDF directory: {rag.pdf_dir}")
        console.print(f"  Vector DB path: {rag.vector_db.db_path}\n")

        return True
    except Exception as e:
        console.print(f"[red]✗[/red] RAG initialization failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_parser():
    """Test PDF parser (without actual PDF)."""
    console.print(Panel("Test 2: PDF Parser", style="cyan"))

    try:
        from utils.pdf_parser import PDFParser

        parser = PDFParser()
        console.print("[green]✓[/green] PDF parser initialized")
        console.print("  Note: Upload a PDF to test actual parsing\n")

        return True
    except Exception as e:
        console.print(f"[red]✗[/red] PDF parser failed: {e}\n")
        return False


def test_vector_db():
    """Test vector database operations."""
    console.print(Panel("Test 3: Vector Database", style="cyan"))

    try:
        from utils.vector_db import VectorDatabase
        from core.ollama_client import OllamaClient

        client = OllamaClient()
        db = VectorDatabase(ollama_client=client)

        # Get stats
        stats = db.get_stats()
        console.print("[green]✓[/green] Vector database operational")
        console.print(f"  Total chunks: {stats['total_chunks']}")
        console.print(f"  Unique documents: {stats['unique_documents']}\n")

        return True
    except Exception as e:
        console.print(f"[red]✗[/red] Vector database failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_agent_integration():
    """Test Agent integration with RAG."""
    console.print(Panel("Test 4: Agent Integration", style="cyan"))

    try:
        from agents.geological_interpreter import GeologicalInterpreterAgent

        agent = GeologicalInterpreterAgent(enable_rag=True)

        if agent.rag_enabled:
            console.print("[green]✓[/green] RAG enabled in agent")

            # Get stats
            stats = agent.get_rag_stats()
            console.print(f"  Documents in KB: {stats['unique_documents']}")
            console.print(f"  Total chunks: {stats['total_chunks']}\n")
        else:
            console.print("[yellow]⚠[/yellow] RAG disabled in agent\n")

        return True
    except Exception as e:
        console.print(f"[red]✗[/red] Agent integration failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def demo_usage():
    """Show usage examples."""
    console.print(Panel("Usage Examples", style="bold green"))

    examples = """
1. Upload PDF via Web Interface:
   - Go to http://localhost:8000
   - Click "文献库" tab
   - Upload your geological PDFs

2. Upload PDF via Python:
   ```python
   from agents.geological_interpreter import GeologicalInterpreterAgent

   agent = GeologicalInterpreterAgent()
   result = agent.upload_pdf_to_rag("path/to/paper.pdf")
   print(result)
   ```

3. Search Literature:
   ```python
   results = agent.search_literature("塔里木盆地 构造", n_results=5)
   for r in results:
       print(r['content'][:200])
   ```

4. Analyze Region with RAG:
   ```python
   analysis = agent.analyze_region(
       region_name="塔里木盆地",
       use_rag=True  # Enable RAG
   )
   ```

5. Via CLI:
   ```bash
   # Start web interface
   python main.py web

   # Then upload PDFs through the UI
   ```
"""
    console.print(examples)


def main():
    """Run all tests."""
    console.print("\n")
    console.print(Panel.fit(
        "📚 RAG System Test Suite",
        style="bold white on blue"
    ))
    console.print()

    results = []

    # Run tests
    results.append(("RAG Initialization", test_rag_initialization()))
    results.append(("PDF Parser", test_pdf_parser()))
    results.append(("Vector Database", test_vector_db()))
    results.append(("Agent Integration", test_agent_integration()))

    # Summary
    console.print(Panel("Test Summary", style="bold cyan"))

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{name:30s} {status}")

    console.print(f"\nTotal: {passed}/{total} tests passed\n")

    if passed == total:
        console.print("[bold green]🎉 All tests passed! RAG system is ready.[/bold green]\n")
        demo_usage()
        return 0
    else:
        console.print(f"[bold red]⚠️  {total - passed} test(s) failed[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
