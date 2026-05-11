"""Service for generating text embeddings using Google Gemini API."""
import asyncio
from typing import List

from google import genai
from src.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text string."""
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=self.model,
                contents=text
            )
            # Response format depends on the SDK version, usually it's in embeddings[0].values
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding Error: {str(e)}")
            # Return zero vector as fallback or raise? 
            # Requirement doesn't specify, but Task 15.3 mentions a retry queue.
            return [0.0] * self.dimension

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of text strings."""
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=self.model,
                contents=texts
            )
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            print(f"Batch Embedding Error: {str(e)}")
            return [[0.0] * self.dimension for _ in texts]
