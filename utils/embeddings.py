"""Embedding models for vector database."""

from typing import List, Union
import numpy as np
from loguru import logger


class EmbeddingModel:
    """Base class for embedding models."""

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode texts to embeddings.

        Args:
            texts: Single text or list of texts

        Returns:
            Embedding array(s)
        """
        raise NotImplementedError


class BGEM3Embedding(EmbeddingModel):
    """BGE-M3 embedding model using sentence-transformers."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str = None,
    ):
        """Initialize BGE-M3 model.

        Args:
            model_name: Model name or path
            device: Device to run model (cpu/cuda/mps)
        """
        try:
            from sentence_transformers import SentenceTransformer

            self.model_name = model_name
            logger.info(f"Loading BGE-M3 via sentence-transformers: {model_name}")

            # Determine device
            if device is None:
                import torch
                if torch.backends.mps.is_available():
                    device = "mps"
                elif torch.cuda.is_available():
                    device = "cuda"
                else:
                    device = "cpu"

            self.model = SentenceTransformer(
                model_name,
                device=device,
                trust_remote_code=True
            )

            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"BGE-M3 loaded on {device}, dimension: {self.dimension}")

        except Exception as e:
            logger.error(f"Failed to load BGE-M3 model: {e}")
            raise

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 12,
        max_length: int = 8192,
        **kwargs,
    ) -> np.ndarray:
        """Encode texts to dense embeddings.

        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            max_length: Maximum sequence length

        Returns:
            Embedding array(s)
        """
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False

        try:
            # Use sentence-transformers encode method
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                **kwargs
            )

            # Convert to numpy
            if hasattr(embeddings, 'cpu'):
                embeddings = embeddings.cpu().numpy()

            return embeddings

        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class OllamaEmbedding(EmbeddingModel):
    """Ollama-based embedding model (fallback)."""

    def __init__(self, ollama_client=None, model: str = None):
        """Initialize Ollama embedding.

        Args:
            ollama_client: Ollama client instance
            model: Embedding model name
        """
        from core.ollama_client import OllamaClient

        self.client = ollama_client or OllamaClient()
        self.model = model or self.client.model
        logger.info(f"Using Ollama embedding with model: {self.model}")

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode texts using Ollama.

        Args:
            texts: Single text or list of texts

        Returns:
            Embedding array(s)
        """
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False

        embeddings = []
        for text in texts:
            try:
                emb = self.client.embed(text)
                embeddings.append(emb)
            except Exception as e:
                logger.error(f"Failed to encode text: {e}")
                raise

        embeddings = np.array(embeddings)

        if single_text:
            return embeddings[0]
        else:
            return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension (varies by model)."""
        # BGE-M3: 1024, Qwen: varies
        return 1024  # Approximate


def create_embedding_model(
    model_type: str = "bge-m3",
    **kwargs,
) -> EmbeddingModel:
    """Factory function to create embedding model.

    Args:
        model_type: Type of model ('bge-m3' or 'ollama')
        **kwargs: Additional arguments

    Returns:
        EmbeddingModel instance
    """
    if model_type.lower() == "bge-m3":
        return BGEM3Embedding(**kwargs)
    elif model_type.lower() == "ollama":
        return OllamaEmbedding(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
