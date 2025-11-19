"""
Reranking module for RAG Pipeline.
Re-ranks retrieved documents using cross-encoder models.
"""

from typing import List, Dict, Any, Optional, Tuple
from ..config import RERANKING_CONFIG


class Reranker:
    """
    Re-rank search results using cross-encoder models.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        """
        Initialize reranker.
        
        Args:
            model_name: Name of the reranking model
            device: Device to use ("cpu" or "cuda")
            enabled: Whether reranking is enabled
        """
        self.enabled = enabled if enabled is not None else RERANKING_CONFIG["enabled"]
        self.model_name = model_name or RERANKING_CONFIG["model_name"]
        self.device = device or RERANKING_CONFIG["device"]
        self.rerank_top_k = RERANKING_CONFIG["rerank_top_k"]
        
        self.model = None
        self.tokenizer = None
        
        if self.enabled:
            self._load_model()
    
    def _load_model(self):
        """
        Load reranking model and tokenizer.
        """
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name, device=self.device)
            print(f"✅ Reranker model loaded: {self.model_name}")
        except ImportError:
            print("⚠️  sentence-transformers not installed. Reranking disabled.")
            print("   Install with: pip install sentence-transformers")
            self.enabled = False
        except Exception as e:
            print(f"⚠️  Failed to load reranker model: {e}")
            print("   Reranking disabled.")
            self.enabled = False
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on query relevance.
        
        Args:
            query: Query text
            documents: List of document dictionaries with 'content' key
            top_k: Number of top documents to return after reranking
            
        Returns:
            Re-ranked list of documents
        """
        if not self.enabled or not self.model:
            # Return original order if reranking is disabled
            return documents[:top_k] if top_k else documents
        
        top_k = top_k or self.rerank_top_k
        
        # Prepare pairs for cross-encoder
        pairs = []
        for doc in documents:
            content = doc.get("content", "")
            pairs.append([query, content])
        
        # Get relevance scores
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}. Returning original order.")
            return documents[:top_k]
        
        # Combine documents with scores
        doc_scores = list(zip(documents, scores))
        
        # Sort by score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update scores and return top_k
        reranked = []
        for doc, score in doc_scores[:top_k]:
            doc["rerank_score"] = float(score)
            reranked.append(doc)
        
        return reranked
    
    def rerank_with_scores(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Re-rank documents and return both documents and scores.
        
        Args:
            query: Query text
            documents: List of document dictionaries
            top_k: Number of top documents to return
            
        Returns:
            Tuple of (reranked documents, scores)
        """
        reranked = self.rerank(query, documents, top_k)
        scores = [doc.get("rerank_score", 0.0) for doc in reranked]
        return reranked, scores

