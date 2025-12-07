"""
Embedding module for RAG Pipeline.
Handles text vectorization using OpenAI embeddings.
"""

import os
import time
import numpy as np
from typing import List, Union, Optional
from openai import OpenAI, AsyncOpenAI
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
        self.timeout = OPENAI_CONFIG.get("timeout", 30.0)
        self.max_retries = OPENAI_CONFIG.get("max_retries", 3)
        self.retry_delay = OPENAI_CONFIG.get("retry_delay", 1.0)
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=0  # We handle retries manually
        )
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.embedding_dim = OPENAI_CONFIG["embedding_dim"]
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Check if an error is retryable.
        
        Args:
            error: Exception to check
            
        Returns:
            True if error is retryable, False otherwise
        """
        error_msg = str(error).lower()
        error_type = str(type(error))
        
        # Non-retryable errors
        non_retryable_indicators = [
            "429",  # Rate limit exceeded (quota)
            "quota",
            "insufficient_quota",
            "401",  # Authentication error
            "403",  # Forbidden
            "invalid_request",
            "invalid_api_key"
        ]
        
        for indicator in non_retryable_indicators:
            if indicator in error_msg or indicator in error_type:
                return False
        
        # Retryable errors (timeout, network, server errors)
        retryable_indicators = [
            "timeout",
            "connection",
            "network",
            "500",
            "502",
            "503",
            "504",
            "rate_limit"  # Rate limit (not quota) can be retried
        ]
        
        for indicator in retryable_indicators:
            if indicator in error_msg or indicator in error_type:
                return True
        
        # Default: retry on unknown errors
        return True
    
    def generate_embedding(self, text: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Generate embedding(s) for text(s) with timeout, retry, and error handling.
        
        Args:
            text: Single text string or list of texts
            normalize: Whether to L2 normalize the embedding
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        last_exception = None
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Call OpenAI API
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                
                elapsed_time = time.time() - start_time
                
                # Warn if approaching timeout
                if elapsed_time > self.timeout * 0.8:
                    print(f"⚠️  Embedding API call took {elapsed_time:.2f}s (approaching timeout of {self.timeout}s)")
                
                embeddings = []
                for item in response.data:
                    vec = np.array(item.embedding, dtype=np.float32)
                    
                    # L2 normalization
                    if normalize:
                        vec = vec / (np.linalg.norm(vec) + 1e-12)
                    
                    embeddings.append(vec.tolist())
                
                return embeddings[0] if is_single else embeddings
            
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Check if error is retryable
                if not self._is_retryable_error(e):
                    print(f"❌ Non-retryable error: {error_msg}")
                    raise
                
                # Retry with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  Embedding API call failed (attempt {attempt + 1}/{self.max_retries}): {error_msg[:100]}")
                    print(f"   Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Embedding API call failed after {self.max_retries} attempts: {error_msg}")
                    raise
        
        # Should not reach here, but handle just in case
        if last_exception:
            raise last_exception
    
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
    
    async def generate_embedding_async(self, text: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Generate embedding(s) for text(s) asynchronously.
        
        Args:
            text: Single text string or list of texts
            normalize: Whether to L2 normalize the embedding
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        # Call OpenAI API asynchronously
        response = await self.async_client.embeddings.create(
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

