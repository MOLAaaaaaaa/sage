"""Ollama client for LLM integration."""

import os
import json
import base64
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import ollama
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize Ollama client.

        Args:
            base_url: Ollama server URL (default: from env or http://localhost:11434)
            model: Default model to use (default: from env or qwen3-vl:30b)
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3-vl:30b")
        self.client = ollama.Client(host=self.base_url)
        logger.info(f"Initialized Ollama client with model: {self.model}")

    def check_connection(self) -> bool:
        """Check if Ollama server is running and model is available.

        Returns:
            True if connection is successful
        """
        try:
            # List available models
            models = self.client.list()
            model_names = [m.model for m in models.models]

            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                return False

            logger.info(f"Successfully connected to Ollama. Model {self.model} is available.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> str:
        """Send chat messages to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat(
                model=model or self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                stream=stream,
            )

            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.message and chunk.message.content:
                        full_response += chunk.message.content
                return full_response
            else:
                return response.message.content

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise

    def chat_with_image(
        self,
        prompt: str,
        image_path: Optional[Union[str, Path]] = None,
        image_data: Optional[bytes] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Send chat message with image to vision-capable model.

        Args:
            prompt: Text prompt
            image_path: Path to image file
            image_data: Raw image bytes (alternative to image_path)
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated text response
        """
        try:
            # Prepare image data
            if image_path:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            elif image_data:
                image_bytes = image_data
            else:
                raise ValueError("Either image_path or image_data must be provided")

            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            messages = [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64],
                }
            ]

            response = self.client.chat(
                model=model or self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            return response.message.content

        except Exception as e:
            logger.error(f"Error in vision chat: {e}")
            raise

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text using completion API.

        Args:
            prompt: Input prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        try:
            response = self.client.generate(
                model=model or self.model,
                prompt=prompt,
                system=system_prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            return response.response

        except Exception as e:
            logger.error(f"Error in generation: {e}")
            raise

    def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate embeddings for text.

        Args:
            text: Input text
            model: Embedding model to use

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings(
                model=model or self.model,
                prompt=text,
            )
            return response.embedding

        except Exception as e:
            logger.error(f"Error in embedding: {e}")
            raise
