"""
Embedding service using OpenAI's embedding models.
"""

from openai import OpenAI
from typing import List, Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Embedding model to use (defaults to config)
        """
        settings = get_settings()
        
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Embedding dimensions for different models
        self.dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # OpenAI supports batching up to 2048 inputs
            batch_size = 100  # Be conservative
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                # Sort by index to maintain order
                sorted_data = sorted(response.data, key=lambda x: x.index)
                batch_embeddings = [item.embedding for item in sorted_data]
                
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(
                    f"Generated embeddings for batch {i//batch_size + 1}, "
                    f"{len(batch)} texts"
                )
            
            logger.info(f"Generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings for the current model."""
        return self.dimensions.get(self.model, 1536)
