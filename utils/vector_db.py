"""Vector database for RAG using ChromaDB."""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import chromadb
from chromadb.config import Settings
from loguru import logger

from utils.embeddings import EmbeddingModel, create_embedding_model
from core.ollama_client import OllamaClient


class VectorDatabase:
    """ChromaDB-based vector database for geological literature."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        embedding_type: str = "bge-m3",
        collection_name: str = "geological_literature",
        ollama_client: Optional[OllamaClient] = None,
    ):
        """Initialize vector database.

        Args:
            db_path: Path to persist database (default: ./data/vector_db)
            embedding_model: Custom embedding model instance
            embedding_type: Type of embedding ('bge-m3' or 'ollama')
            collection_name: Name of the collection
            ollama_client: Ollama client (for ollama embedding type)
        """
        self.db_path = db_path or Path("./data/vector_db")
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Geological literature knowledge base"}
        )

        # Initialize embedding model
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            if embedding_type.lower() == "ollama":
                self.embedding_model = create_embedding_model(
                    "ollama",
                    ollama_client=ollama_client
                )
            else:
                self.embedding_model = create_embedding_model(embedding_type)

        logger.info(f"Initialized vector database at {self.db_path}")
        logger.info(f"Embedding model: {type(self.embedding_model).__name__}")
        logger.info(f"Collection: {collection_name} ({self.collection.count()} documents)")

    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> int:
        """Add document to vector database with chunking.

        Args:
            doc_id: Unique document ID
            content: Document text content
            metadata: Document metadata
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            Number of chunks added
        """
        # Split content into chunks
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        if not chunks:
            logger.warning(f"No chunks created for document: {doc_id}")
            return 0

        # Generate embeddings for each chunk
        embeddings = []
        texts_to_encode = [chunk["text"] for chunk in chunks]

        try:
            # Batch encode all chunks
            encoded_embeddings = self.embedding_model.encode(texts_to_encode)

            # Handle both single and batch results
            if len(encoded_embeddings.shape) == 1:
                # Single embedding returned
                embeddings.append(encoded_embeddings)
            else:
                # Multiple embeddings returned
                for emb in encoded_embeddings:
                    embeddings.append(emb)

            logger.debug(f"Generated {len(embeddings)} embeddings")

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return 0

        if not embeddings:
            logger.error(f"Failed to generate any embeddings for: {doc_id}")
            return 0

        # Prepare data for insertion
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "page_number": chunk.get("page_number", 0),
            }
            for i, chunk in enumerate(chunks)
        ]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Added {len(chunks)} chunks for document: {doc_id}")
        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents.

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Metadata filters

        Returns:
            List of relevant document chunks
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query)

            # Ensure it's a list format for ChromaDB
            if len(query_embedding.shape) == 1:
                query_embedding = [query_embedding.tolist()]
            else:
                query_embedding = query_embedding.tolist()

            # Search
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=filter_metadata,
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })

            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_document(self, doc_id: str) -> int:
        """Delete a document and all its chunks.

        Args:
            doc_id: Document ID to delete

        Returns:
            Number of chunks deleted
        """
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={"doc_id": doc_id},
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                count = len(results["ids"])
                logger.info(f"Deleted {count} chunks for document: {doc_id}")
                return count
            else:
                logger.warning(f"Document not found: {doc_id}")
                return 0

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dict
        """
        count = self.collection.count()

        # Get unique document IDs
        all_docs = self.collection.get()
        unique_docs = set()
        if all_docs["metadatas"]:
            for meta in all_docs["metadatas"]:
                if "doc_id" in meta:
                    unique_docs.add(meta["doc_id"])

        return {
            "total_chunks": count,
            "unique_documents": len(unique_docs),
            "collection_name": self.collection_name,
            "db_path": str(self.db_path),
        }

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the database.

        Returns:
            List of document info
        """
        all_docs = self.collection.get()

        documents = {}
        if all_docs["metadatas"]:
            for i, meta in enumerate(all_docs["metadatas"]):
                doc_id = meta.get("doc_id", "unknown")
                if doc_id not in documents:
                    documents[doc_id] = {
                        "doc_id": doc_id,
                        "title": meta.get("title", "Unknown"),
                        "author": meta.get("author", "Unknown"),
                        "filename": meta.get("filename", ""),
                        "chunks": 0,
                        "pages": meta.get("pages", 0),
                    }
                documents[doc_id]["chunks"] += 1

        return list(documents.values())

    @staticmethod
    def _chunk_text(
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks.

        Args:
            text: Text to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of chunks with text and metadata
        """
        chunks = []

        # Split by pages first if available
        pages = text.split("--- Page")

        if len(pages) > 1:
            # Process page by page
            for page_text in pages:
                if not page_text.strip():
                    continue

                # Extract page number
                page_num = 0
                if "--- Page" in page_text:
                    try:
                        page_num = int(page_text.split("---")[1].strip().split()[0])
                        page_text = "---".join(page_text.split("---")[2:])
                    except:
                        pass

                # Chunk within page
                page_chunks = VectorDatabase._chunk_single_text(
                    page_text, chunk_size, chunk_overlap
                )
                for chunk in page_chunks:
                    chunk["page_number"] = page_num
                    chunks.append(chunk)
        else:
            # Single chunk without page info
            chunks = VectorDatabase._chunk_single_text(text, chunk_size, chunk_overlap)

        return chunks

    @staticmethod
    def _chunk_single_text(
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[Dict[str, Any]]:
        """Split a single text into chunks.

        Args:
            text: Text to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of chunk dicts
        """
        if not text.strip():
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # Try to break at sentence boundary
            if end < text_len:
                # Look for sentence boundary
                for sep in ['. ', '\n', '。', '；']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({"text": chunk_text})

            start = end - chunk_overlap
            if start <= 0:
                break

        return chunks
