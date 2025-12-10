"""
Configuration module for RAG Pipeline.
Centralized configuration management for all components.
"""

import os
from typing import Dict, Any


def _get_device() -> str:
    """
    Automatically detect and return the best available device.
    Returns "cuda" if GPU is available, otherwise "cpu".
    
    Returns:
        Device string ("cuda" or "cpu")
    """
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"

# Elasticsearch Configuration
ES_CONFIG: Dict[str, Any] = {
    "host": "https://localhost:9200",
    #"api_key": ("<your elasticsearch api key>", "<your elasticsearch api key secret>"),
    #"ca_certs": " path to your elasticsearch certificate",
    "index_name": "sports_kb"
}

# PostgreSQL Configuration
PG_CONFIG: Dict[str, Any] = {
    "dbname": "sports_injury_rag",
    "user": "", # Set your PostgreSQL username
    "password": "", # Set your PostgreSQL password
    "host": "localhost",
    "port": 5432
}

# OpenAI Configuration (for embeddings)
OPENAI_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),# Set your Openai API key
    "model": "text-embedding-3-small",
    "embedding_dim": 1536,
    "timeout": 30.0,  # Timeout in seconds
    "max_retries": 3,  # Maximum retry attempts
    "retry_delay": 1.0  # Initial delay between retries in seconds (exponential backoff)
}

# Gemini Configuration
GEMINI_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("GEMINI_API_KEY", ""),  # Set your Gemini API key
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "max_output_tokens": 1000,
    "top_p": 0.8,
    "top_k": 40,
    "timeout": 20.0,  # Timeout in seconds (longer for generation)
    "max_retries": 3,  # Maximum retry attempts
    "retry_delay": 1.0,  # Initial delay between retries in seconds (exponential backoff)
    "use_multiprocessing": False  
}

# Retrieval Configuration
RETRIEVAL_CONFIG: Dict[str, Any] = {
    "top_k": 60,
    "num_candidates": 1000,
    "use_hybrid": True,  # Use hybrid search (vector + BM25)
    "category_filter": False  # Enable category-based filtering
}

# Reranking Configuration
RERANKING_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "rerank_top_k": 10,  # Number of documents to return after reranking
    "model_name": "BAAI/bge-reranker-base",  # Cross-encoder model
    "device": _get_device(),  # Automatically detect: "cuda" if GPU available, else "cpu"
    "use_domain_filter": False,  # Enable sports-aware domain filtering
    "alpha": 1.0,  # Score fusion weight (1.0 = pure CE, 0.7 = 70% CE + 30% original)
    "batch_size": 32  # Batch size for cross-encoder predictions
}

# Prompt Template Configuration
# PROMPT_CONFIG: Dict[str, Any] = {
#     "system_instruction": """
# You are an expert assistant in sports injury science (sports medicine, biomechanics, prevention, rehabilitation).

# You will always receive:
# 1) A user question.
# 2) A small number of retrieved context passages.

# Your goals:
# - Answer accurately based *only on the provided context* when possible.
# - Extract the maximum useful information from *very few chunks*.
# - Do not invent data, study names, or precise protocols that are not supported.
# - When information is insufficient, clearly say what the context supports and what it does not.

# ==================== CORE RULES ====================

# USE CONTEXT FIRST:
# - Treat all provided text as primary evidence.
# - Scan all passages and extract high-yield points: mechanisms, diagnosis clues, risk factors, prevention, rehab, return-to-play principles.
# - Prefer generalizable principles found in the documents over narrow case details.

# WHEN CONTEXT IS LIMITED:
# - If the answer is partially supported, state which parts are supported vs. not supported.
# - You may generalize cautiously (use “may”, “likely”, “suggests”), but only from content inside the context.
# - Never fabricate numbers, timeline protocols, or tests not mentioned.

# SAFETY & LANGUAGE:
# - You are not a doctor; avoid direct prescriptions (e.g., “Do this”). Prefer “People are usually advised to...” or “The document indicates...”.
# - Encourage professional evaluation in case of red-flag symptoms or unclear severity.
# - Use clear, accessible language; explain medical terms briefly if needed.

# ==================== ANSWER FORMAT ====================

# 1) **Short direct answer**
#    - 2–4 sentences answering the question using context evidence.

# 2) **Structured key points**
#    - Example bullets: Mechanism, Symptoms/Recognition, Risk Factors, Prevention, Rehabilitation, Return-to-Sport.
#    - Each point should synthesize across chunks, not summarize each passage separately.

# 3) **Limitations / Safety Notice**
#    - If context doesn’t cover part of the question, say so explicitly.
#    - Suggest consultation when serious symptoms or clinical decisions are involved.

# 4) **Sources**
#    - Cite provided passages simply (e.g., “(Source: Doc 1)” or “(Sources: Doc 1–2)”).
#    - Do not create new source names or numbers.

# ==================== CITING STYLE ====================
# - Cite at least one document for each major claim.
# - If multiple documents support the same point, group citations.
# - Do not cite facts not present in the text.

# =================================
# Follow these instructions before answering any question.
# """,
#     "max_context_length": 8000,
#     "include_sources": True
# }


PROMPT_CONFIG: Dict[str, Any] = {
    "system_instruction": """
You are a helpful assistant specialized in sports injury knowledge. 
Answer questions based on the provided context documents. 
If the context doesn't contain enough information, say so clearly. 
Always cite relevant information from the context when possible.
""",
    "max_context_length": 8000,  # Maximum characters from retrieved documents
    "include_sources": True      # Include source information in the response
}


# Data Processing Configuration
DATA_CONFIG: Dict[str, Any] = {
    "batch_size": 1000,  # Batch size for bulk operations
    "embedding_normalize": True  # L2 normalize embeddings
}
