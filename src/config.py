"""
Configuration module for RAG Pipeline.
Centralized configuration management for all components.
"""

import os
from typing import Dict, Any

# Elasticsearch Configuration
ES_CONFIG: Dict[str, Any] = {
    "host": "https://localhost:9200",
    "api_key": ("QnbREpoBx8vU1yItlmkz", "T4TzIbNwwlp_LsgNptb53g"),
    "ca_certs": "C:/Users/12055/OneDrive/Desktop/25Fall/291A Agent/elasticsearch-9.2.0-windows-x86_64/elasticsearch-9.2.0/config/certs/http_ca.crt",
    "index_name": "sports_kb"
}

# PostgreSQL Configuration
PG_CONFIG: Dict[str, Any] = {
    "dbname": "sports_injury_rag",
    "user": "postgres",
    "password": "170328",
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
    "api_key": os.getenv("GEMINI_API_KEY", ""),  # Set your Gemini API key
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
    "use_domain_filter": False,  # Enable sports-aware domain filtering
    "alpha": 1.0,  # Score fusion weight (1.0 = pure CE, 0.7 = 70% CE + 30% original)
    "batch_size": 32  # Batch size for cross-encoder predictions
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

