"""
Reranking module for RAG Pipeline.
Re-ranks retrieved documents using cross-encoder models with optional domain filtering.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from ..config import RERANKING_CONFIG
from .domain_filter import DomainFilter


class Reranker:
    """
    Re-rank search results using cross-encoder models.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        enabled: Optional[bool] = None,
        use_domain_filter: bool = False,
        alpha: float = 1.0
    ):
        """
        Initialize reranker with optional domain filtering and score fusion.
        
        Args:
            model_name: Name of the reranking model
            device: Device to use ("cpu" or "cuda")
            enabled: Whether reranking is enabled
            use_domain_filter: Whether to use domain-specific filtering/boosting
            alpha: Score fusion weight (1.0 = pure CE, 0.7 = 70% CE + 30% original)
        """
        self.enabled = enabled if enabled is not None else RERANKING_CONFIG["enabled"]
        self.model_name = model_name or RERANKING_CONFIG["model_name"]
        self.device = device or RERANKING_CONFIG["device"]
        self.rerank_top_k = RERANKING_CONFIG["rerank_top_k"]
        self.use_domain_filter = use_domain_filter
        self.alpha = alpha
        
        self.model = None
        self.tokenizer = None
        self.domain_filter = None
        
        # Initialize domain filter if enabled
        if self.use_domain_filter:
            self.domain_filter = DomainFilter()
            print("✅ Domain filter enabled (sports-aware boosting)")
        
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
        Re-rank documents with optional domain filtering and score fusion.
        
        Two-stage approach:
        1. Domain filter (if enabled): Fast rule-based boosting
        2. Cross-encoder: Deep semantic reranking with optional score fusion
        
        Args:
            query: Query text
            documents: List of document dictionaries with 'content' key
            top_k: Number of top documents to return after reranking
            
        Returns:
            Re-ranked list of documents
        """
        if not documents:
            return []
        
        if not self.enabled or not self.model:
            # Return original order if reranking is disabled
            return documents[:top_k] if top_k else documents
        
        top_k = top_k or self.rerank_top_k
        
        # Stage 1: Domain filtering (if enabled)
        if self.domain_filter:
            documents = self.domain_filter.boost_documents(query, documents)
        
        # Store original scores for fusion
        original_scores = [doc.get("score", 0.0) for doc in documents]
        
        # Stage 2: Cross-encoder reranking
        # Prepare pairs for cross-encoder
        pairs = []
        for doc in documents:
            content = doc.get("content", "")
            pairs.append([query, content])
        
        # Get cross-encoder scores
        try:
            ce_scores = self.model.predict(pairs)
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}. Returning original order.")
            return documents[:top_k]
        
        # Normalize CE scores to [0, 1] range for fusion
        ce_scores_normalized = self._normalize_scores(ce_scores)
        
        # Apply score fusion (if alpha < 1.0)
        if self.alpha < 1.0:
            # Normalize original scores for fair fusion
            orig_scores_normalized = self._normalize_scores(np.array(original_scores))
            
            # Fusion: alpha * CE + (1-alpha) * original
            final_scores = (
                self.alpha * ce_scores_normalized + 
                (1 - self.alpha) * orig_scores_normalized
            )
        else:
            # Pure cross-encoder scores (backward compatible)
            final_scores = ce_scores_normalized
        
        # Combine documents with final scores
        doc_scores = list(zip(documents, final_scores, ce_scores))
        
        # Sort by final score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update scores and return top_k
        reranked = []
        for doc, final_score, ce_score in doc_scores[:top_k]:
            doc["rerank_score"] = float(ce_score)  # Store raw CE score
            doc["score"] = float(final_score)  # Update with fused score
            if self.alpha < 1.0:
                doc["fusion_alpha"] = self.alpha
            reranked.append(doc)
        
        return reranked
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to [0, 1] range."""
        scores = np.array(scores)
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score - min_score > 1e-6:
            return (scores - min_score) / (max_score - min_score)
        return scores
    
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

