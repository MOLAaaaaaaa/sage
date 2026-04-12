"""Test script for BGE-M3 embedding."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_bge_m3_embedding():
    """Test BGE-M3 embedding model."""
    console.print(Panel("Test: BGE-M3 Embedding Model", style="cyan"))

    try:
        from utils.embeddings import BGEM3Embedding

        # Initialize model
        console.print("[bold]Loading BGE-M3 model...[/bold]")
        model = BGEM3Embedding()

        console.print(f"[green]✓[/green] Model loaded successfully")
        console.print(f"  Dimension: {model.get_dimension()}")

        # Test encoding
        console.print("\n[bold]Testing encoding...[/bold]")
        texts = [
            "塔里木盆地位于中国西北部",
            "四川盆地是重要的油气产区",
            "What is earthquake location uncertainty?",
        ]

        embeddings = model.encode(texts, batch_size=4)

        console.print(f"[green]✓[/green] Encoding successful")
        console.print(f"  Input texts: {len(texts)}")
        console.print(f"  Output shape: {embeddings.shape}")
        console.print(f"  Vector dimension: {len(embeddings[0])}")

        # Test similarity
        console.print("\n[bold]Testing similarity...[/bold]")
        import numpy as np

        # Calculate cosine similarity
        vec1 = embeddings[0]
        vec2 = embeddings[1]
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        console.print(f"  Similarity between text 1 and 2: {similarity:.4f}")
        console.print("  (Higher means more similar)\n")

        return True

    except Exception as e:
        console.print(f"[red]✗[/red] BGE-M3 test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_vector_db_with_bge():
    """Test vector database with BGE-M3."""
    console.print(Panel("Test: Vector Database with BGE-M3", style="cyan"))

    try:
        from utils.vector_db import VectorDatabase
        import tempfile
        import shutil

        # Create temporary DB
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_db"

        console.print("[bold]Initializing vector database with BGE-M3...[/bold]")
        db = VectorDatabase(
            db_path=db_path,
            embedding_type="bge-m3"
        )

        console.print(f"[green]✓[/green] Database initialized")

        # Test adding document
        console.print("\n[bold]Testing document addition...[/bold]")
        test_content = """
        塔里木盆地是中国最大的内陆盆地，位于新疆南部。
        盆地面积约56万平方公里，周围被天山、昆仑山等山脉环绕。
        该地区富含油气资源，是中国重要的能源基地。
        """

        num_chunks = db.add_document(
            doc_id="test_doc",
            content=test_content,
            metadata={"title": "Test Document", "doc_id": "test_doc"}
        )

        console.print(f"[green]✓[/green] Added {num_chunks} chunks")

        # Test search
        console.print("\n[bold]Testing search...[/bold]")
        results = db.search("塔里木盆地 位置", n_results=3)

        console.print(f"[green]✓[/green] Search returned {len(results)} results")
        if results:
            console.print(f"  Best match distance: {results[0]['distance']:.4f}")
            console.print(f"  Content preview: {results[0]['content'][:100]}...")

        # Cleanup
        shutil.rmtree(temp_dir)
        console.print("\n[green]✓[/green] All tests passed\n")

        return True

    except Exception as e:
        console.print(f"[red]✗[/red] Vector DB test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_rag_with_bge():
    """Test RAG with BGE-M3."""
    console.print(Panel("Test: RAG with BGE-M3", style="cyan"))

    try:
        from utils.rag_retriever import RAGRetriever
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "rag_db"

        console.print("[bold]Initializing RAG with BGE-M3...[/bold]")
        rag = RAGRetriever(
            db_path=db_path,
            embedding_type="bge-m3"
        )

        console.print(f"[green]✓[/green] RAG initialized")

        # Get stats
        stats = rag.get_database_stats()
        console.print(f"  Documents: {stats['unique_documents']}")
        console.print(f"  Chunks: {stats['total_chunks']}\n")

        # Cleanup
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        console.print(f"[red]✗[/red] RAG test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    console.print("\n")
    console.print(Panel.fit(
        "🧠 BGE-M3 Embedding Test Suite",
        style="bold white on blue"
    ))
    console.print()

    results = []

    # Run tests
    results.append(("BGE-M3 Embedding", test_bge_m3_embedding()))
    results.append(("Vector DB with BGE-M3", test_vector_db_with_bge()))
    results.append(("RAG with BGE-M3", test_rag_with_bge()))

    # Summary
    console.print(Panel("Test Summary", style="bold cyan"))

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{name:35s} {status}")

    console.print(f"\nTotal: {passed}/{total} tests passed\n")

    if passed == total:
        console.print("[bold green]🎉 All BGE-M3 tests passed![/bold green]\n")
        return 0
    else:
        console.print(f"[bold red]⚠️  {total - passed} test(s) failed[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
