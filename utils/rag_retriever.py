"""RAG (Retrieval-Augmented Generation) module for geological literature."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from utils.pdf_parser import PDFParser
from utils.vector_db import VectorDatabase
from core.ollama_client import OllamaClient


class RAGRetriever:
    """RAG system for geological literature retrieval and analysis."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        ollama_client: Optional[OllamaClient] = None,
        pdf_dir: Optional[Path] = None,
        embedding_type: str = "bge-m3",
    ):
        """Initialize RAG retriever.

        Args:
            db_path: Path to vector database
            ollama_client: Ollama client
            pdf_dir: Directory for PDF uploads
            embedding_type: Type of embedding model ('bge-m3' or 'ollama')
        """
        self.ollama_client = ollama_client or OllamaClient()
        self.vector_db = VectorDatabase(
            db_path=db_path,
            embedding_type=embedding_type,
            ollama_client=self.ollama_client if embedding_type == "ollama" else None
        )
        self.pdf_parser = PDFParser()
        self.pdf_dir = pdf_dir or Path("./data/uploads/pdfs")
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"RAG Retriever initialized (embedding: {embedding_type})")

    def upload_pdf(self, pdf_path: Path, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload and index a PDF document.

        Args:
            pdf_path: Path to PDF file
            doc_id: Custom document ID (default: filename stem)

        Returns:
            Upload result with stats
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Parse PDF
        logger.info(f"Parsing PDF: {pdf_path.name}")
        parsed = self.pdf_parser.parse_pdf_with_metadata(pdf_path)

        # Generate doc_id if not provided
        if doc_id is None:
            doc_id = pdf_path.stem

        # Add metadata
        metadata = {
            **parsed["metadata"],
            "doc_id": doc_id,
        }

        # Add to vector database
        logger.info(f"Indexing document: {doc_id}")
        num_chunks = self.vector_db.add_document(
            doc_id=doc_id,
            content=parsed["full_text"],
            metadata=metadata,
        )

        result = {
            "success": True,
            "doc_id": doc_id,
            "filename": pdf_path.name,
            "title": metadata["title"],
            "author": metadata["author"],
            "pages": metadata["pages"],
            "chunks_indexed": num_chunks,
        }

        logger.info(f"Successfully indexed: {doc_id} ({num_chunks} chunks)")
        return result

    def batch_upload_pdfs(self, directory: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Upload and index all PDFs in a directory.

        Args:
            directory: Directory containing PDFs (default: pdf_dir)

        Returns:
            List of upload results
        """
        dir_path = directory or self.pdf_dir
        pdf_files = list(dir_path.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {dir_path}")
            return []

        results = []
        for pdf_file in pdf_files:
            try:
                result = self.upload_pdf(pdf_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to upload {pdf_file.name}: {e}")
                results.append({
                    "success": False,
                    "filename": pdf_file.name,
                    "error": str(e),
                })

        logger.info(f"Batch upload completed: {len(results)} files")
        return results

    def search_literature(
        self,
        query: str,
        n_results: int = 5,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search geological literature.

        Args:
            query: Search query
            n_results: Number of results
            filter_by: Metadata filters

        Returns:
            List of relevant passages
        """
        results = self.vector_db.search(
            query=query,
            n_results=n_results,
            filter_metadata=filter_by,
        )

        return results

    def get_context_for_query(
        self,
        query: str,
        region: Optional[str] = None,
        n_results: int = 10,
    ) -> str:
        """Get relevant context from literature for a query.

        Args:
            query: User query
            region: Optional region filter
            n_results: Number of passages to retrieve

        Returns:
            Formatted context string
        """
        # Build filter
        filter_by = None
        if region:
            filter_by = {"region": region}

        # Search
        results = self.search_literature(
            query=query,
            n_results=n_results,
            filter_by=filter_by,
        )

        if not results:
            return "未找到相关文献资料。"

        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            passage = (
                f"[文献 {i}] {metadata.get('title', 'Unknown')}\n"
                f"作者: {metadata.get('author', 'Unknown')}\n"
                f"页码: {metadata.get('page_number', 'N/A')}\n"
                f"相关内容: {result['content']}\n"
            )
            context_parts.append(passage)

        context = "\n".join(context_parts)
        logger.info(f"Retrieved {len(results)} passages for query")

        return context

    def analyze_region_with_rag(
        self,
        region_name: str,
        description: Optional[str] = None,
        n_references: int = 10,
    ) -> str:
        """Analyze a region using RAG with literature context.

        Args:
            region_name: Region name
            description: Additional description
            n_references: Number of references to retrieve

        Returns:
            Analysis with literature references
        """
        # Build search query
        search_query = f"{region_name} 地质 构造 地层"
        if description:
            search_query += f" {description}"

        # Get relevant literature
        logger.info(f"Searching literature for: {region_name}")
        context = self.get_context_for_query(
            query=search_query,
            region=region_name,
            n_results=n_references,
        )

        # Build prompt with context
        prompt = f"""请基于以下参考文献和专业知识，对{region_name}进行地质解释分析。

## 相关参考文献

{context}

## 分析要求

请结合上述文献资料，从以下方面进行分析：
1. 区域构造背景和大地构造位置
2. 地层发育特征和时代划分
3. 主要构造样式和变形特征
4. 沉积相和岩相古地理
5. 资源潜力和勘探前景
6. 与文献中类似区域的对比

"""
        if description:
            prompt += f"补充信息:\n{description}\n\n"

        prompt += "请提供详细、专业的地质解释，并适当引用参考文献。"

        # Generate analysis using LLM
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的地球物理学家和地质解释专家，擅长结合文献资料进行地质分析。"
            },
            {"role": "user", "content": prompt},
        ]

        response = self.ollama_client.chat(messages)
        return response

    def get_database_stats(self) -> Dict[str, Any]:
        """Get vector database statistics.

        Returns:
            Statistics dict
        """
        return self.vector_db.get_stats()

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the database.

        Returns:
            List of document info
        """
        return self.vector_db.list_documents()

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the database.

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        count = self.vector_db.delete_document(doc_id)
        return count > 0
