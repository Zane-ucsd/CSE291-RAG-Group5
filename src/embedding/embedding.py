"""
Embedding module for RAG Pipeline.
Handles text vectorization using OpenAI embeddings.
"""

import os
import numpy as np
from typing import List, Union, Optional
from openai import OpenAI
from ..config import OPENAI_CONFIG


class EmbeddingGenerator:
    """
    Generate embeddings for text using OpenAI API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize embedding generator.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Embedding model name (defaults to config)
        """
        self.api_key = api_key or OPENAI_CONFIG["api_key"]
        self.model = model or OPENAI_CONFIG["model"]
        self.client = OpenAI(api_key=self.api_key)
        self.embedding_dim = OPENAI_CONFIG["embedding_dim"]
    
    def generate_embedding(self, text: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Generate embedding(s) for text(s).
        
        Args:
            text: Single text string or list of texts
            normalize: Whether to L2 normalize the embedding
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        # Call OpenAI API
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        
        embeddings = []
        for item in response.data:
            vec = np.array(item.embedding, dtype=np.float32)
            
            # L2 normalization
            if normalize:
                vec = vec / (np.linalg.norm(vec) + 1e-12)
            
            embeddings.append(vec.tolist())
        
        return embeddings[0] if is_single else embeddings
    
    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        L2 normalize an embedding vector.
        
        Args:
            embedding: Embedding vector
            
        Returns:
            Normalized embedding vector
        """
        v = np.array(embedding, dtype=np.float32)
        v = v / (np.linalg.norm(v) + 1e-12)
        return v.tolist()
    
    def batch_generate(self, texts: List[str], batch_size: int = 100, normalize: bool = True) -> List[List[float]]:
        """
        Generate embeddings for a large batch of texts.
        
        Args:
            texts: List of texts
            batch_size: Number of texts to process per batch
            normalize: Whether to normalize embeddings
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.generate_embedding(batch, normalize=normalize)
            all_embeddings.extend(embeddings)
        
        return all_embeddings

