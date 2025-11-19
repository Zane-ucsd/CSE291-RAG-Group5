"""
Utility functions for RAG Pipeline.
Text classification, preprocessing, and helper functions.
"""

from typing import Optional, List
import re


def classify_sport_category(text: str) -> str:
    """
    Classify text into sport categories based on keywords.
    
    Args:
        text: Input text to classify
        
    Returns:
        Category name: "Badminton", "Cycling", "Running", "Soccer", "Swimming", or "General"
    """
    lower_text = text.lower()
    
    if "badminton" in lower_text:
        return "Badminton"
    elif any(keyword in lower_text for keyword in ["cyclist", "cycling", "saddle", "bike", "bicycle"]):
        return "Cycling"
    elif any(keyword in lower_text for keyword in ["runner", "running", "jogging"]):
        return "Running"
    elif any(keyword in lower_text for keyword in ["football", "soccer", "footballer"]):
        return "Soccer"
    elif any(keyword in lower_text for keyword in ["swimmer", "swimming", "breaststroke", "freestyle", "backstroke"]):
        return "Swimming"
    else:
        return "General"


def normalize_category(category: Optional[str]) -> Optional[str]:
    """
    Normalize category string to lowercase.
    
    Args:
        category: Category string
        
    Returns:
        Lowercase category or None
    """
    if category:
        return category.lower().strip()
    return None


def preprocess_text(text: str) -> str:
    """
    Basic text preprocessing.
    
    Args:
        text: Raw text
        
    Returns:
        Preprocessed text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_context_documents(documents: List[dict], max_length: int = 3000, truncate_per_doc: bool = False) -> str:
    """
    Format retrieved documents into context string for prompt.
    
    Args:
        documents: List of document dictionaries with 'content' and optionally 'source' keys
        max_length: Maximum total length of context
        truncate_per_doc: If True, truncate each document individually to fit more documents
    
    Returns:
        Formatted context string
    """
    context_parts = []
    current_length = 0
    
    # If truncate_per_doc is True, calculate max length per document
    if truncate_per_doc and len(documents) > 0:
        # Reserve space for formatting (approximately 50 chars per doc)
        avg_formatting = 50
        # Ensure each document gets at least 300 chars, but try to fit all documents
        max_per_doc = max(300, (max_length - avg_formatting * len(documents)) // len(documents))
    else:
        max_per_doc = None
    
    for i, doc in enumerate(documents, 1):
        content = doc.get("content", "")
        source = doc.get("source", "Unknown")
        
        # Truncate individual document if needed
        if max_per_doc and len(content) > max_per_doc:
            content = content[:max_per_doc - 3] + "..."
        
        # Format: [Document 1] (Source: xxx)\nContent...
        doc_text = f"[Document {i}] (Source: {source})\n{content}\n\n"
        
        if current_length + len(doc_text) > max_length:
            # If we're truncating per doc, try to fit at least part of this document
            if truncate_per_doc:
                remaining = max_length - current_length - len(f"[Document {i}] (Source: {source})\n\n")
                if remaining > 100:  # Only add if we have meaningful space
                    truncated_content = content[:remaining - 3] + "..."
                    doc_text = f"[Document {i}] (Source: {source})\n{truncated_content}\n\n"
                    context_parts.append(doc_text)
            break
            
        context_parts.append(doc_text)
        current_length += len(doc_text)
    
    return "".join(context_parts)

