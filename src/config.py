"""
Configuration module for RAG Pipeline.
Centralized configuration management for all components.
"""

import os
from typing import Dict, Any

# Elasticsearch Configuration
ES_CONFIG: Dict[str, Any] = {
    "host": "http://localhost:9200",  # ES 8.11.0 via Docker (security disabled for dev)
    "index_name": "sports_kb"
    # No api_key or ca_certs needed - security disabled in Docker container
}

# PostgreSQL Configuration
PG_CONFIG: Dict[str, Any] = {
    "dbname": "sports_injury_rag",
    "user": "apple",  # Your Mac username
    "password": "",  # Homebrew PostgreSQL doesn't require password for local connections
    "host": "localhost",
    "port": 5432
}

# OpenAI Configuration (for embeddings)
OPENAI_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),# Set your Openai API key
    "model": "text-embedding-3-small",
    "embedding_dim": 1536
}

# Gemini Configuration
GEMINI_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("GEMINI_API_KEY", ""),  # Replace with your actual key
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "max_output_tokens": 1000,
    "top_p": 0.8,
    "top_k": 40
}

# Retrieval Configuration
RETRIEVAL_CONFIG: Dict[str, Any] = {
    "top_k": 10,
    "num_candidates": 60,
    "use_hybrid": True,  # Use hybrid search (vector + BM25)
    "category_filter": True  # Enable category-based filtering
}

# Reranking Configuration
RERANKING_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "rerank_top_k": 10,  # Number of documents to return after reranking
    "model_name": "BAAI/bge-reranker-base",  # Cross-encoder model
    "device": "cpu",  # "cpu" or "cuda"
    "use_domain_filter": True,  # Enable sports-aware boosting
    "alpha": 0.7  # Score fusion: 0.7 = 70% CE + 30% original (1.0 = pure CE)
}

# Prompt Template Configuration
PROMPT_CONFIG: Dict[str, Any] = {
    "system_instruction": """You are a helpful assistant specialized in sports injury knowledge. 
Answer questions based on the provided context documents. If the context doesn't contain enough information, 
say so clearly. Always cite relevant information from the context when possible.""",
    "max_context_length": 8000,  # Maximum characters from retrieved documents
    "include_sources": True  # Include source information in the response
}

# Data Processing Configuration
DATA_CONFIG: Dict[str, Any] = {
    "batch_size": 1000,  # Batch size for bulk operations
    "embedding_normalize": True  # L2 normalize embeddings
}

